"""Per-profile language: the persona speaks it everywhere.

A synthetic profile has one voice across every surface — chat, composed
posts, room turns, robot speech. Setting a language makes that voice speak
it natively: the directive rides on the persona system prompt, so every
generation site inherits it without per-endpoint plumbing. Owner-set,
like the model preference.
"""

from __future__ import annotations

import re

SUPPORTED: dict[str, str] = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "it": "Italiano",
    "ja": "日本語",
    "zh": "中文",
    "hi": "हिन्दी",
    "ar": "العربية",
}

DEFAULT = "en"

# "pre": the persona speaks the language natively everywhere (default).
# "on_demand": the persona keeps its original voice; the owner translates
# selectively via POST /profiles/{id}/translate.
MODES = ("pre", "on_demand")


def get_pref(profile_id: str) -> tuple[str, str]:
    from . import db
    row = db.connect().execute(
        "SELECT language, mode FROM language_prefs WHERE profile_id=?",
        (profile_id,)).fetchone()
    return (row["language"], row["mode"]) if row else (DEFAULT, "pre")


def get_language(profile_id: str) -> str:
    return get_pref(profile_id)[0]


def effective_language(profile_id: str) -> str:
    language, mode = get_pref(profile_id)
    return language if mode == "pre" else DEFAULT


def set_language(profile_id: str, language: str, mode: str = "pre") -> str:
    if language not in SUPPORTED:
        raise ValueError(f"unknown language {language!r}")
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    from . import db
    conn = db.connect()
    conn.execute(
        "INSERT INTO language_prefs (profile_id, language, mode, updated_at)"
        " VALUES (?,?,?,?)"
        " ON CONFLICT(profile_id) DO UPDATE SET language=excluded.language,"
        " mode=excluded.mode, updated_at=excluded.updated_at",
        (profile_id, language, mode, db.utcnow()))
    conn.commit()
    return language


def translate(profile_id: str, text: str, to: str | None = None,
              cloud=None) -> dict:
    """Translate anything the owner runs across — an interactor's message,
    a room turn, a listing — using the profile's own model. The offline stub
    cannot translate free text, and says so instead of pretending."""
    from . import llm
    target = to or get_language(profile_id)
    if target not in SUPPORTED:
        raise ValueError(f"unknown language {target!r}")
    if target == DEFAULT:
        return {"text": text, "translation": text, "language": target,
                "engine": "none", "note": "target language is English"}
    effective = llm.resolve_choice(llm.get_choice(profile_id))
    if effective == "stub":
        return {"text": text, "translation": text, "language": target,
                "engine": "stub",
                "note": "the offline stub cannot translate free text — "
                        "configure a model provider for live translation"}
    system = (f"You are a precise translator. Translate the user's text into "
              f"{SUPPORTED[target]} ({target}). Preserve meaning, tone, and "
              "formatting. Output only the translation.")
    translation = llm.provider_for_profile(profile_id, cloud=cloud).generate(
        system, [{"role": "user", "content": text}])
    return {"text": text, "translation": translation, "language": target,
            "engine": effective}


def directive(language: str) -> str:
    if language == DEFAULT:
        return ""
    return (f"\nSpeak entirely in {SUPPORTED[language]} ({language}) — every "
            "reply, post, and spoken line, while staying fully in character.")


# --------------------------------------------------------------------------- #
# The visitor's language
# --------------------------------------------------------------------------- #
#
# Everything above this line takes a `profile_id`. That is right for the
# console, whose readers all have one, and it has nothing to say about the one
# surface built for people who do not: `screens/Public.tsx`, where somebody
# contests a synthetic profile of themselves, asks whether what they were sent
# was written by a person, or checks they met the same profile twice.
#
# A previous round read `navigator.languages` there and put that screen's
# frame into ten languages. Its *answers* stayed in one. Every sentence the
# server contributes to that page — the recovery result, the restriction
# notice, the consistency guarantee, the synthetic-media disclosure, the
# refusals — is authored in English here and rendered verbatim. So a visitor
# in Osaka got a Japanese page, typed in a piece of text, pressed a Japanese
# button, and was answered in English at the exact moment they were being told
# the thing they came to find out.
#
# The audit's recurring shape, one layer in from the last round on this
# screen: the question asked was *is the surface localized*; the one that
# matters is *is the answer*.
#
# Hand-translated and looked up, never machine-translated — the rule
# `jim.i18n` and `pdi.i18n` already follow. A statement about whether a person
# wrote something, or that a profile has been restricted, is not text to hand
# to a model: an approximate translation of "we cannot name an author" is a
# different sentence with different weight. Unknown text falls through as
# English, which is a visible gap rather than a confident error.


def negotiate(header: str | None) -> str:
    """Pick a supported language from an ``Accept-Language`` header.

    Quality values honoured, region dropped (``es-419`` and ``es-ES`` are both
    ``es``), the header's own order as the tie-break, and anything
    unrecognised falls back to English rather than guessing.

    The visitor's language, which on these routes is the only one there is:
    `open_objection` says its caller "need not own an account", so there is no
    stored preference to read and no profile to read it from.
    """
    if not header:
        return DEFAULT
    ranked: list[tuple[float, int, str]] = []
    for index, part in enumerate(header.split(",")):
        piece = part.strip()
        if not piece:
            continue
        tag, _, params = piece.partition(";")
        quality = 1.0
        for param in params.split(";"):
            key, _, value = param.partition("=")
            if key.strip() == "q":
                try:
                    quality = float(value)
                except ValueError:
                    quality = 0.0
        base = tag.strip().split("-")[0].lower()
        if base in SUPPORTED and quality > 0:
            ranked.append((-quality, index, base))
    return min(ranked)[2] if ranked else DEFAULT


#: **State words are deliberately absent.** `status`, `profile_status` and
#: `prior_status` are the API's vocabulary, not prose: `Contest.tsx` branches
#: on `status.status === "open"`. Translating them server-side was the first
#: version of this round and driving it caught the consequence — the console's
#: "End it now" card would have vanished for every non-English browser, on the
#: one screen where a standing party ends a case immediately. What a person
#: reads is translated; what a client compares is not. The same rule PDI's
#: gate page follows for its `<option value>`s. `Public.tsx` translates the
#: state for display through `pub.state.*` in `l10n.ts`, which is where a
#: display decision belongs.
#:
#: Keyed on the English source, the way JIM's and PDI's tables are, so editing
#: the English invalidates its translations loudly — the page falls back to the
#: new English — rather than quietly serving the old sentence in nine
#: languages.
_PUBLIC: dict[str, dict[str, str]] = {
    "this is the record of your own case: what happened, who did it, and when. The reasons and other free text are not repeated here — you wrote yours, and nobody else's is yours to read": {
        'es': 'este es el registro de su propio caso: qué ocurrió, quién lo hizo y cuándo. Los motivos y demás texto libre no se repiten aquí: el suyo lo escribió usted, y el de los demás no le corresponde leerlo',
        'fr': "voici le registre de votre propre dossier : ce qui s'est passé, qui l'a fait et quand. Les motifs et autres textes libres ne sont pas repris ici — le vôtre, vous l'avez écrit, et celui des autres ne vous revient pas",
        'de': 'dies ist die Akte Ihres eigenen Falls: was geschah, wer es tat und wann. Begründungen und anderer Freitext werden hier nicht wiederholt — Ihre haben Sie selbst geschrieben, und die anderer steht Ihnen nicht zu',
        'pt': 'este é o registo do seu próprio caso: o que aconteceu, quem o fez e quando. Os motivos e outro texto livre não são repetidos aqui — o seu escreveu-o você, e o dos outros não lhe cabe ler',
        'it': "questo è il registro del tuo caso: cosa è successo, chi lo ha fatto e quando. Le motivazioni e gli altri testi liberi non sono ripetuti qui — la tua l'hai scritta tu, e quella altrui non spetta a te leggerla",
        'ja': 'これはあなた自身の案件の記録です。何が、誰によって、いつ行われたか。理由などの自由記述はここには載せません。あなたの理由はあなたが書いたものであり、他人のものはあなたが読むべきものではないからです。',
        'zh': '这是你自己案件的记录：发生了什么、由谁执行、在何时。理由和其他自由文本不在此重复 — 你的理由是你自己写的，而别人的不该由你来读。',
        'hi': 'यह आपके अपने मामले का रिकॉर्ड है: क्या हुआ, किसने किया, और कब। कारण और अन्य मुक्त पाठ यहाँ दोहराए नहीं जाते — अपना आपने लिखा था, और दूसरों का पढ़ना आपका काम नहीं।',
        'ar': 'هذا سجل قضيتك أنت: ما الذي حدث، ومن فعله، ومتى. أما الأسباب وسائر النص الحر فلا تتكرر هنا — سببك كتبته أنت، وسبب غيرك ليس لك أن تقرأه',
    },
    'consent withdrawn; the profile is terminated and its content erased': {
        'es': 'consentimiento retirado; el perfil queda terminado y su contenido borrado',
        'fr': 'consentement retiré ; le profil est supprimé et son contenu effacé',
        'de': 'Einwilligung zurückgezogen; das Profil ist beendet und sein Inhalt gelöscht',
        'pt': 'consentimento retirado; o perfil é terminado e o seu conteúdo apagado',
        'it': 'consenso ritirato; il profilo è terminato e i suoi contenuti cancellati',
        'ja': '同意が撤回されました。プロフィールは終了し、その内容は消去されます。',
        'zh': '同意已撤回；该资料已终止，其内容已被抹除。',
        'hi': 'सहमति वापस ली गई; प्रोफ़ाइल समाप्त कर दी गई और उसकी सामग्री मिटा दी गई।',
        'ar': 'سُحبت الموافقة؛ أُنهي الملف ومُحي محتواه',
    },
    'authorization revoked; the profile is terminated and its content erased': {
        'es': 'autorización revocada; el perfil queda terminado y su contenido borrado',
        'fr': 'autorisation révoquée ; le profil est supprimé et son contenu effacé',
        'de': 'Autorisierung widerrufen; das Profil ist beendet und sein Inhalt gelöscht',
        'pt': 'autorização revogada; o perfil é terminado e o seu conteúdo apagado',
        'it': 'autorizzazione revocata; il profilo è terminato e i suoi contenuti cancellati',
        'ja': '承認が取り消されました。プロフィールは終了し、その内容は消去されます。',
        'zh': '授权已撤销；该资料已终止，其内容已被抹除。',
        'hi': 'प्राधिकरण रद्द किया गया; प्रोफ़ाइल समाप्त कर दी गई और उसकी सामग्री मिटा दी गई।',
        'ar': 'أُلغي التفويض؛ أُنهي الملف ومُحي محتواه',
    },
    'no text to examine': {
        'es': 'no hay texto que examinar',
        'fr': 'aucun texte à examiner',
        'de': 'kein Text zum Prüfen',
        'pt': 'não há texto para examinar',
        'it': 'nessun testo da esaminare',
        'ja': '調べる文章がありません',
        'zh': '没有可供检查的文本',
        'hi': 'जाँचने के लिए कोई पाठ नहीं',
        'ar': 'لا يوجد نص لفحصه',
    },
    'no stamped work shares any wording with this text': {
        'es': 'ningún trabajo sellado comparte redacción con este texto',
        'fr': 'aucun contenu estampillé ne partage de formulation avec ce texte',
        'de': 'keine gestempelte Arbeit teilt Wortlaut mit diesem Text',
        'pt': 'nenhum trabalho carimbado partilha redação com este texto',
        'it': 'nessun lavoro timbrato condivide formulazioni con questo testo',
        'ja': 'この文章と語句を共有する、印の付いた作品はありません',
        'zh': '没有任何加标记的作品与此文本用词相同',
        'hi': 'किसी मुहरबंद काम की शब्दावली इस पाठ से मेल नहीं खाती',
        'ar': 'لا يشترك أي عمل مختوم في صياغة هذا النص',
    },
    'some wording overlaps stamped work, but not enough to name an author — ordinary phrases are shared by unrelated texts': {
        'es': 'parte de la redacción coincide con trabajo sellado, pero no lo suficiente para nombrar a un autor: las frases corrientes las comparten textos sin relación',
        'fr': 'une partie de la formulation recoupe du contenu estampillé, mais pas assez pour nommer un auteur — les tournures ordinaires sont partagées par des textes sans lien',
        'de': 'ein Teil des Wortlauts überschneidet sich mit gestempelter Arbeit, aber nicht genug, um einen Urheber zu nennen — gewöhnliche Wendungen teilen sich unverwandte Texte',
        'pt': 'parte da redação coincide com trabalho carimbado, mas não o suficiente para nomear um autor — frases comuns são partilhadas por textos sem relação',
        'it': 'una parte della formulazione si sovrappone a lavoro timbrato, ma non abbastanza per nominare un autore — le frasi comuni sono condivise da testi non correlati',
        'ja': '一部の語句は印の付いた作品と重なりますが、著者を特定するには足りません。ありふれた言い回しは無関係な文章どうしでも共有されます。',
        'zh': '部分用词与加标记的作品重合，但不足以指认作者 — 常见措辞在毫无关联的文本之间也会共享。',
        'hi': 'कुछ शब्दावली मुहरबंद काम से मेल खाती है, पर किसी लेखक का नाम लेने के लिए पर्याप्त नहीं — सामान्य वाक्यांश असंबंधित पाठों में भी साझा होते हैं।',
        'ar': 'بعض الصياغة تتقاطع مع عمل مختوم، لكن ليس بما يكفي لتسمية مؤلف — فالعبارات المألوفة تتشاركها نصوص لا صلة بينها.',
    },
    'AI-generated synthetic media — produced by a QRME synthetic profile, not a real person': {
        'es': 'medio sintético generado por IA: producido por un perfil sintético de QRME, no por una persona real',
        'fr': 'média synthétique généré par IA — produit par un profil synthétique QRME, pas par une personne réelle',
        'de': 'KI-erzeugte synthetische Medien — von einem synthetischen QRME-Profil erzeugt, nicht von einer echten Person',
        'pt': 'média sintética gerada por IA — produzida por um perfil sintético do QRME, não por uma pessoa real',
        'it': "media sintetico generato dall'IA — prodotto da un profilo sintetico QRME, non da una persona reale",
        'ja': 'AI が生成した合成メディア — 実在の人物ではなく、QRME の合成プロフィールによる生成物です',
        'zh': 'AI 生成的合成媒体 — 由 QRME 合成资料生成，而非真人所作',
        'hi': 'AI द्वारा निर्मित सिंथेटिक मीडिया — किसी वास्तविक व्यक्ति ने नहीं, QRME की सिंथेटिक प्रोफ़ाइल ने बनाया',
        'ar': 'وسائط اصطناعية من إنتاج الذكاء الاصطناعي — أنتجها ملف اصطناعي في QRME، لا شخص حقيقي',
    },
    "keyed five-word windows, HMAC'd with this deployment's watermark key and compared by overlap — arithmetic, not a learned detector, so the score can be checked by hand": {
        'es': 'ventanas de cinco palabras con clave, firmadas con HMAC usando la clave de marca de agua de esta instalación y comparadas por solapamiento: aritmética, no un detector entrenado, de modo que la puntuación puede comprobarse a mano',
        'fr': "fenêtres de cinq mots à clé, signées en HMAC avec la clé de filigrane de ce déploiement et comparées par recouvrement — de l'arithmétique, pas un détecteur appris, si bien que le score peut être vérifié à la main",
        'de': 'verschlüsselte Fünf-Wort-Fenster, mit dem Wasserzeichenschlüssel dieser Installation HMAC-signiert und über Überschneidung verglichen — Arithmetik, kein gelernter Detektor, die Bewertung ist also von Hand nachrechenbar',
        'pt': 'janelas de cinco palavras com chave, assinadas por HMAC com a chave de marca de água desta instalação e comparadas por sobreposição — aritmética, não um detetor treinado, pelo que a pontuação pode ser verificada à mão',
        'it': 'finestre di cinque parole con chiave, firmate in HMAC con la chiave di filigrana di questa installazione e confrontate per sovrapposizione — aritmetica, non un rilevatore addestrato, quindi il punteggio è verificabile a mano',
        'ja': '鍵付きの 5 語ウィンドウを、この環境の透かし鍵で HMAC 化し、重なりで比較しています。学習した検出器ではなく算術なので、スコアは手作業で検算できます。',
        'zh': '使用本部署的水印密钥对五词窗口做 HMAC，并按重叠度比较 — 这是算术，不是训练出来的检测器，因此分数可以手工核验。',
        'hi': 'इस परिनियोजन की वॉटरमार्क कुंजी से HMAC किए गए पाँच-शब्द विंडो, जिनकी तुलना ओवरलैप से होती है — यह अंकगणित है, कोई प्रशिक्षित डिटेक्टर नहीं, इसलिए स्कोर हाथ से जाँचा जा सकता है।',
        'ar': 'نوافذ من خمس كلمات مُفتاحية، مُوقَّعة بـ HMAC بمفتاح العلامة المائية لهذا التنصيب ومقارَنة بالتداخل — حسابٌ لا كاشف مُدرَّب، فالنتيجة قابلة للتحقق يدويًا.',
    },
    'unaltered': {
        'es': 'sin alterar',
        'fr': 'non modifié',
        'de': 'unverändert',
        'pt': 'não alterado',
        'it': 'non alterato',
        'ja': '改変なし',
        'zh': '未经改动',
        'hi': 'अपरिवर्तित',
        'ar': 'غير مُعدَّل',
    },
    'altered but traceable': {
        'es': 'alterado pero rastreable',
        'fr': 'modifié mais traçable',
        'de': 'verändert, aber nachverfolgbar',
        'pt': 'alterado mas rastreável',
        'it': 'alterato ma tracciabile',
        'ja': '改変されているが追跡可能',
        'zh': '已改动但仍可追溯',
        'hi': 'बदला गया पर पता लगाने योग्य',
        'ar': 'مُعدَّل لكن قابل للتتبع',
    },
    'profile restricted pending review; the owner must re-attest their rights basis': {
        'es': 'perfil restringido a la espera de revisión; el titular debe volver a acreditar su base de derechos',
        'fr': "profil restreint en attente d'examen ; le propriétaire doit réattester sa base de droits",
        'de': 'Profil bis zur Prüfung beschränkt; die Inhaberin oder der Inhaber muss die Rechtsgrundlage erneut bestätigen',
        'pt': 'perfil restringido a aguardar revisão; o titular tem de voltar a atestar a sua base de direitos',
        'it': 'profilo limitato in attesa di revisione; il titolare deve riattestare la propria base di diritti',
        'ja': '審査が終わるまでプロフィールを制限しました。所有者は権利の根拠を改めて証明する必要があります。',
        'zh': '该资料在审核期间受到限制；所有者必须重新证明其权利依据。',
        'hi': 'समीक्षा होने तक प्रोफ़ाइल सीमित; स्वामी को अपना अधिकार-आधार फिर से प्रमाणित करना होगा',
        'ar': 'قُيّد الملف بانتظار المراجعة؛ وعلى المالك أن يُثبت أساس حقه من جديد',
    },
    'identity, memory, and voice stay constant across every embodiment and modality; only the form of expression changes': {
        'es': 'la identidad, la memoria y la voz permanecen constantes en cada encarnación y modalidad; solo cambia la forma de expresión',
        'fr': "l'identité, la mémoire et la voix restent constantes dans chaque incarnation et modalité ; seule la forme d'expression change",
        'de': 'Identität, Gedächtnis und Stimme bleiben über jede Verkörperung und Modalität hinweg gleich; nur die Ausdrucksform ändert sich',
        'pt': 'a identidade, a memória e a voz mantêm-se constantes em cada encarnação e modalidade; só muda a forma de expressão',
        'it': "identità, memoria e voce restano costanti in ogni incarnazione e modalità; cambia solo la forma dell'espressione",
        'ja': '身元・記憶・声は、どの形態・様式でも一定です。変わるのは表現の形だけです。',
        'zh': '身份、记忆与声音在每一种化身和形态中保持不变；改变的只是表达形式。',
        'hi': 'पहचान, स्मृति और आवाज़ हर रूप और माध्यम में अपरिवर्तित रहती हैं; केवल अभिव्यक्ति का रूप बदलता है।',
        'ar': 'تبقى الهوية والذاكرة والصوت ثابتة عبر كل تجسيد وكل وسيط؛ ولا يتغير إلا شكل التعبير.',
    },
    'text, voice, feed, AR/VR, a speaker, a hologram, or a robot': {
        'es': 'texto, voz, feed, RA/RV, un altavoz, un holograma o un robot',
        'fr': 'texte, voix, flux, RA/RV, une enceinte, un hologramme ou un robot',
        'de': 'Text, Stimme, Feed, AR/VR, ein Lautsprecher, ein Hologramm oder ein Roboter',
        'pt': 'texto, voz, feed, RA/RV, uma coluna, um holograma ou um robô',
        'it': 'testo, voce, feed, AR/VR, un altoparlante, un ologramma o un robot',
        'ja': 'テキスト、音声、フィード、AR/VR、スピーカー、ホログラム、ロボット',
        'zh': '文本、语音、信息流、AR/VR、音箱、全息影像或机器人',
        'hi': 'पाठ, आवाज़, फ़ीड, AR/VR, स्पीकर, होलोग्राम या रोबोट',
        'ar': 'نص، صوت، تدفق، الواقع المعزز/الافتراضي، مكبر صوت، صورة مجسّمة، أو روبوت',
    },
    'profile not found': {
        'es': 'no se encontró el perfil',
        'fr': 'profil introuvable',
        'de': 'Profil nicht gefunden',
        'pt': 'perfil não encontrado',
        'it': 'profilo non trovato',
        'ja': 'プロフィールが見つかりません',
        'zh': '未找到该资料',
        'hi': 'प्रोफ़ाइल नहीं मिली',
        'ar': 'لم يُعثر على الملف',
    },
    'objection not found': {
        'es': 'no se encontró la objeción',
        'fr': 'contestation introuvable',
        'de': 'Widerspruch nicht gefunden',
        'pt': 'contestação não encontrada',
        'it': 'contestazione non trovata',
        'ja': '異議が見つかりません',
        'zh': '未找到该异议',
        'hi': 'आपत्ति नहीं मिली',
        'ar': 'لم يُعثر على الاعتراض',
    },
    'profile is terminated; there is nothing left to object to': {
        'es': 'el perfil está terminado; no queda nada a lo que objetar',
        'fr': 'le profil est supprimé ; il ne reste rien à contester',
        'de': 'das Profil ist beendet; es bleibt nichts, dem zu widersprechen wäre',
        'pt': 'o perfil está terminado; não resta nada a contestar',
        'it': 'il profilo è terminato; non resta nulla da contestare',
        'ja': 'このプロフィールは終了しています。異議を申し立てる対象は残っていません。',
        'zh': '该资料已终止，已无可提出异议的对象。',
        'hi': 'प्रोफ़ाइल समाप्त हो चुकी है; अब आपत्ति करने को कुछ शेष नहीं।',
        'ar': 'أُنهي هذا الملف؛ لم يبقَ ما يُعترض عليه.',
    },
}


def tr_public(text: str, language: str) -> str:
    """Translate one of the sentences the accountless surface shows."""
    if language == DEFAULT:
        return text
    return _PUBLIC.get(text, {}).get(language, text)


def localize_public(obj, language: str):
    """Walk a response, replacing exactly the sentences we have.

    Anything not in the table passes through untouched, and that is the point:
    a person's display name, a signature, an id and a number are not ours to
    translate. Only sentences this product wrote are.
    """
    if language == DEFAULT:
        return obj
    if isinstance(obj, dict):
        return {key: localize_public(value, language)
                for key, value in obj.items()}
    if isinstance(obj, list):
        return [localize_public(value, language) for value in obj]
    if isinstance(obj, str):
        return tr_public(obj, language)
    return obj


# --------------------------------------------------------------------------- #
# The product's own refusals
# --------------------------------------------------------------------------- #
#
# The first line of this module says the persona speaks the owner's language
# everywhere. It does — `directive` rides on the system prompt, so every
# generation site inherits it. The *platform* spoke English: every 4xx an owner
# received, on an account where they had chosen Portuguese, where the model
# answered them in Portuguese, and where the console's sidebar was in
# Portuguese too.
#
# `common.refusals_in` was added for the four accountless routes and its
# docstring said why the owner routes were left out:
#
#     `profile_or_404` and its siblings are shared with every owner route and
#     say "profile not found" in English, which is right there — the owner
#     picked that language
#
# The owner did not pick that language. They picked one, it is in
# `language_prefs`, and English is what they get when they picked English. The
# justification for the scope was the defect.
#
#     asked     did the caller state a language
#     mattered  did the profile
#
# ## Whose language
#
# Not the profile named in the path. `GET /profiles/{id}/consistency` is a
# public route: the reader is a stranger asking about somebody else's profile,
# and answering them in *that owner's* language would be a new wrong answer
# dressed as a fix. Not `Accept-Language` either — a console owner's browser
# sends `en-US` whatever they set in the app, which would have made the whole
# thing a no-op that passed its own tests.
#
#     asked     whose language is stored here
#     mattered  who is reading this sentence
#
# The credential names the reader. An owner token means the profile's own
# setting; anything else — an interactor, a reviewer, no token at all — means
# the header, which is all such a reader carries.
#
# ## Which of the two stored values
#
# `get_language`, not `effective_language`. The latter returns English whenever
# the mode is `on_demand`, and that mode is a statement about the *persona's*
# voice — "keep speaking as you were, I will translate what I choose". It says
# nothing about what the owner reads. Reusing it here would have looked right,
# passed a test written with a `pre`-mode profile, and served English refusals
# to every owner who had asked their persona to stay in character.


#: What a slot may hold and still be dropped into a translated frame.
#:
#: The rule is whitespace. A token — `en`, `openai`, `prf_9f2`, `@ada`,
#: `/profiles`, `12.00` — has none. English prose has spaces in it, and so does
#: every other language's. The one allowed exception is a comma-separated list
#: of tokens, because half the refusals this exists for are "must be one of".
#:
#: Deliberately conservative in one direction only: it refuses some slots that
#: would have been safe (a product name like `Unitree G1`) and never accepts
#: one that is not. A refused slot costs an English sentence, which is the
#: state everything was already in. An accepted prose slot costs a sentence
#: half in one language and half in another, in front of somebody who is
#: already being told no.
#:
#: Whitespace, not an allowlist of characters. The first version of this listed
#: the characters a token may contain, which quietly meant *ASCII*: Devanagari
#: writes its vowels as combining marks, which are not `\w`, so every Hindi
#: word in the vocabulary below failed a rule written to catch English
#: sentences. Caught by `test_no_vocabulary_word_is_itself_prose`, which was
#: asking the question the docstring already claimed this asked.
_SLOT_TOKEN = re.compile(r"^\S*$")


def _is_token(value) -> bool:
    return all(_SLOT_TOKEN.match(part.strip())
               for part in str(value).split(","))


class Templated(str):
    """A refusal whose English text is not a constant, carried so it can be.

    `f"language must be one of {', '.join(SUPPORTED)}"` cannot be keyed on its
    English source, because at the moment it is raised there is no English
    source — only a result. `tests/refusals_untranslated.txt` named 49 of these
    and counted none of them, and the same held in the sibling products.

        asked     is the refusal a constant we can translate
        mattered  is every part of it something we can translate

    This is a `str`, and its value is the finished English sentence. Everything
    that already treats a detail as text keeps working unchanged — the default
    path, JSON encoding, every driven test asserting on a message. What it adds
    is a memory of how it was built, so `localize_detail` can look up the
    *template* and refill it in the reader's language.

    ## The slot is the whole problem

    A translated frame around an English slot is worse than an English
    sentence: it reads as a mistake, and it is the failure this repository
    already refuses to ship for the plan gate, whose message interpolates a
    capability description and a plan title. So a slot that does not look like
    a token (see `_SLOT_TOKEN`) sets `translatable = False` and the whole
    sentence stays English — the state it was in before, chosen rather than
    stumbled into. Nothing raises: a refusal path is the last place to add a
    way to fail.

    For a closed set of product words — an objection's `status`, say — pass the
    slot through `term()` first, and the slot arrives already translated.
    """

    template: str
    slots: dict
    translatable: bool

    def __new__(cls, template: str, **slots):
        # `Opening` applies here too, not only at translation. This value *is*
        # the English sentence — the one an English reader gets and the one
        # every driven test reads — so a capitalisation that only happened on
        # the translated path would leave English the odd one out.
        english = {k: _open(v) if isinstance(v, Opening) else v
                   for k, v in slots.items()}
        text = template.format(**english)
        self = super().__new__(cls, text)
        self.template = template
        self.slots = slots
        # A `Term` is exempt from the whitespace rule, and that is the point of
        # it. The rule exists to catch prose *this product did not author* — a
        # library's exception, a hardware availability string — which cannot be
        # translated because nobody wrote a translation for it. A `Term` is
        # drawn from a closed set this product does author, so its whitespace
        # is not a warning sign: `create and run your own synthetic profiles`
        # is a phrase with a translation, and refusing it for having spaces
        # would keep the plan gate English for exactly the wrong reason.
        #
        #     asked     does this slot contain whitespace
        #     mattered  is this slot something we have a translation for
        #
        # Safe by construction either way: an unmapped `Term` keeps the whole
        # refusal English in `localize_detail`, the same as a prose slot.
        self.translatable = all(isinstance(v, Term) or _is_token(v)
                                for v in slots.values())
        return self


def fill(template: str, **slots) -> Templated:
    """`raise HTTPException(422, i18n.fill(TEMPLATE, choices=...))`.

    A function rather than the class directly, so a raise site reads as a
    sentence being built and not as an object being constructed.
    """
    return Templated(template, **slots)


class Term(str):
    """A slot drawn from the product's own closed vocabulary.

    `f"objection is already {obj['status']}"` has a slot holding `open`,
    `upheld` or `dismissed` — the API's words, which a client branches on. They
    stay those words on the wire. But inside a sentence a person reads, an
    English key in a Portuguese frame is the mixed sentence this whole
    mechanism exists to prevent, and `_SLOT_TOKEN` cannot catch it: `upheld` is
    one word with no whitespace, indistinguishable from an identifier.

    So the author marks it, and the marking is what makes it translatable:

        i18n.fill(i18n.OBJECTION_ALREADY, status=i18n.Term(obj["status"]))

    Translated at render, not at raise: the reader's language is not known at
    the raise site, which is the reason the handler does this work at all.
    """


class Opening(Term):
    """A `Term` that begins its sentence, and so is capitalised.

    After translation, never before. The vocabulary holds one form of each
    phrase — `create and run your own synthetic profiles` — and each language
    raises its own first letter from that; a capitalised table would need a
    second copy of every entry, free to drift from the first.

    `str.capitalize()` is wrong here: it lower-cases everything after the first
    character, which would turn German's `im Marktplatz einstellen` into
    something with its nouns flattened. Only the first character moves.
    """


def _open(text: str) -> str:
    return text[:1].upper() + text[1:]


def term(word: str, language: str) -> str:
    """One vocabulary word in the reader's language.

    Unknown words come back unchanged, which is a visible gap rather than a
    confident error — and `test_every_state_a_refusal_can_name_has_a_word`
    fails on any this product can actually reach.
    """
    if language == DEFAULT:
        return word
    return _VOCABULARY.get(word, {}).get(language, word)


def tr_refusal(text: str, language: str) -> str:
    """Translate one of the sentences this product refuses with.

    `_PUBLIC` is consulted too, and deliberately: "profile not found" is
    raised by `profile_or_404`, which the accountless routes and every owner
    route share. Two tables would be two translations of one sentence, free to
    drift, with nothing to say which reader got which.
    """
    if language == DEFAULT:
        return text
    return (_REFUSALS.get(text) or _TEMPLATES.get(text)
            or _VALIDATION.get(text)
            or _PUBLIC.get(text, {})).get(language, text)


def sentence_of(detail) -> str | None:
    """The part of a refusal a person is meant to read, whatever shape it has.

    `detail` is a string for most refusals, a dict for the plan gate, and a
    list of rows for a 422. Three shapes, and every client had to know which
    one it was looking at — which is why the plan gate reached three of the
    four as `HTTP 402`.

        asked     does the sentence ride beside the structure
        mattered  does every structured refusal put it in the same place

    Returns `None` when there is nothing readable rather than inventing
    something: a bare status is more honest than a sentence this module made
    up. `api.py` answers exactly as it used to in that case.

    The 422's list is deliberately not handled here. Its sentence needs the
    reader's language and the field-name rules, which is `validation_message`'s
    job, and its handler passes the result in directly.
    """
    if isinstance(detail, str):
        return detail or None
    if isinstance(detail, dict):
        said = detail.get("message")
        return said if isinstance(said, str) and said else None
    return None


def localize_detail(detail, language: str):
    """An HTTPException detail, translated in whichever shape it arrives.

    Details are usually a sentence. `tiers.gate` raises a **dict** — reason,
    capability, price, and a `message` a person reads — because a client has
    to tell an upgrade apart from a purchase without matching on prose. A
    handler that translated only `str` would have left the plan gate in
    English: the one refusal in this product that stands between somebody and
    a decision to pay, untouched, while everything around it changed language.

    Only `message` is translated. `reason`, `capability`, `needs` and `have`
    are the API's vocabulary — the console branches on them — and the same
    rule holds here as for `_PUBLIC`: what a person reads is translated, what
    a client compares is not.
    """
    if language == DEFAULT:
        return detail
    # Before the plain-string branch: a Templated *is* a str, and its value is
    # the finished English sentence, which is not a key in any table. Looking
    # it up would find nothing and return the English — silently, and
    # indistinguishably from a sentence nobody has translated yet.
    if isinstance(detail, Templated):
        if not detail.translatable:
            return str(detail)
        # A vocabulary word with no translation would land in the frame as an
        # English key — the mixed sentence `Term` exists to prevent, arriving
        # through the mechanism built to prevent it. Structural rather than
        # enumerated: a status added to a table three modules away cannot be
        # relied upon to reach a list here, so an unknown word keeps the whole
        # refusal English instead of being caught by a test that has to be
        # remembered.
        vocabulary = [v for v in detail.slots.values() if isinstance(v, Term)]
        if any(str(v) not in _VOCABULARY for v in vocabulary):
            return str(detail)
        frame = tr_refusal(detail.template, language)
        filling = {}
        for key, value in detail.slots.items():
            if isinstance(value, Opening):
                filling[key] = _open(term(value, language))
            elif isinstance(value, Term):
                filling[key] = term(value, language)
            else:
                filling[key] = value
        try:
            return frame.format(**filling)
        except (KeyError, IndexError, ValueError):
            # A translation whose braces do not match the template's. The
            # English sentence is correct and complete; a half-formatted one
            # in the reader's language is not.
            return str(detail)
    if isinstance(detail, str):
        return tr_refusal(detail, language)
    if isinstance(detail, dict) and isinstance(detail.get("message"), str):
        # `localize_detail` and not `tr_refusal`: a `Templated` *is* a `str`,
        # so `tr_refusal` would look up the finished English sentence, find
        # nothing, and hand back the English — losing the template it is
        # carrying. The plan gate's message is exactly that shape.
        return {**detail,
                "message": localize_detail(detail["message"], language)}
    return detail


def refusal_language(request) -> str:
    """The language the person receiving this refusal reads.

    Never raises and never touches the response path's own error handling: a
    diagnostic that can fail is worse than one that is in the wrong language.
    """
    from . import auth
    try:
        who = auth.principal(request)
        if who and who.get("role") == "owner":
            return get_language(who["subject_id"])
    except Exception:
        pass
    return negotiate(request.headers.get("accept-language"))


#: Sentences the product refuses with, keyed on the English source the way
#: `_PUBLIC` is — so editing the English falls back loudly to the new English
#: rather than quietly serving the old sentence in nine languages.
#:
#: What is here is what every route can raise: the shared owner and interactor
#: checks in `common.py`, and the credential checks in `auth.py`. What is not
#: here is recorded in `tests/refusals_untranslated.txt` and ratcheted.
# --- templates: the refusals whose English is not a constant ----------------
#
# Named constants rather than literals at the raise site, so this file is the
# whole list of them and `test_a_refusal_template_is_translated_or_written_down`
# can enumerate it. A raise site reads:
#
#     raise HTTPException(422, i18n.fill(
#         i18n.MUST_BE_ONE_OF, field="language",
#         choices=", ".join(i18n.SUPPORTED)))
#
# Every slot in every template below holds a token — a field name, a joined
# list of machine values, a status word that has already been through `term`.
# See `Templated` for why that is the whole design constraint.

#: Six routes said this about six different fields. One sentence, one
#: translation, `field` as a slot: the field name is the API's own and is the
#: same string in every language.
MUST_BE_ONE_OF = "{field} must be one of {choices}"

#: `identity` and `overlays` both name a surface that does not exist.
UNKNOWN_SURFACE = "unknown surface {surface} — one of {choices}"

#: The four governance routes, plus the two elsewhere. Separate templates
#: rather than one with a `{subject}` slot, and deliberately: "objection",
#: "message" and "profile" are single English words, and a single English word
#: is exactly what `_SLOT_TOKEN` cannot tell apart from an identifier. Naming
#: the subject inside the template puts it where it can be translated.
OBJECTION_ALREADY = "objection is already {status}"
MESSAGE_ALREADY = "message is already {status}"
PROFILE_ALREADY = "profile is already {status}"
NOT_A_MEMORIAL = "this profile is {status}, not a memorial"

#: The refusal `refusals_untranslated.txt` named for four releases as the one
#: thing it would not half-do. Its slots are prose — a capability description
#: and a billing period — so translating the frame alone would have produced a
#: sentence half in each language at the one moment in this product that stands
#: between somebody and a decision to pay. Both slots are `Term`s now, drawn
#: from the vocabulary below, so the whole sentence arrives in one language or
#: none of it does.
#:
#: The plan titles are deliberately *not* slots to translate. `Basic` and `Pro`
#: are what the product is called on the pricing page, in the console's tabs
#: and on a receipt; a person comparing a refusal against a price list needs
#: the same word in both places. They ride in as tokens.
PLAN_GATE = ("{capability} needs {needs} (${price}/{period}). "
             "This account is on {have}. Billing here is simulated — "
             "subscribing records a row and moves no real funds.")

#: Every template this module offers. Derived from the table below rather than
#: repeated, so a template with no translations is impossible by construction.
TEMPLATES = (MUST_BE_ONE_OF, UNKNOWN_SURFACE, OBJECTION_ALREADY,
             MESSAGE_ALREADY, PROFILE_ALREADY, NOT_A_MEMORIAL, PLAN_GATE)

_TEMPLATES: dict[str, dict[str, str]] = {
    PLAN_GATE: {
        'es': '{capability} requiere {needs} (${price}/{period}). Esta cuenta '
              'está en {have}. La facturación aquí es simulada: suscribirse '
              'registra una fila y no mueve fondos reales.',
        'fr': '{capability} nécessite {needs} ({price} $/{period}). Ce compte '
              'est en {have}. La facturation est simulée ici : souscrire '
              'enregistre une ligne et ne déplace aucun fonds réel.',
        'de': '{capability} erfordert {needs} ({price} $/{period}). Dieses '
              'Konto ist auf {have}. Die Abrechnung ist hier simuliert — ein '
              'Abo legt eine Zeile an und bewegt kein echtes Geld.',
        'pt': '{capability} requer {needs} (${price}/{period}). Esta conta '
              'está no {have}. A cobrança aqui é simulada: assinar registra '
              'uma linha e não movimenta fundos reais.',
        'it': '{capability} richiede {needs} ({price} $/{period}). Questo '
              'account è su {have}. La fatturazione qui è simulata: '
              'abbonarsi registra una riga e non muove fondi reali.',
        'ja': '{capability}には{needs}が必要です（${price}／{period}）。'
              'このアカウントは{have}です。ここでの課金はシミュレーションです — '
              '購読しても記録が残るだけで、実際の資金は動きません。',
        'zh': '{capability}需要 {needs}（${price}/{period}）。'
              '此账户当前为 {have}。此处的计费为模拟 — 订阅只会记录一行，'
              '不会转移真实资金。',
        'hi': '{capability} के लिए {needs} चाहिए (${price}/{period})। '
              'यह खाता {have} पर है। यहाँ बिलिंग नकली है — सदस्यता लेने पर '
              'केवल एक पंक्ति दर्ज होती है, असली पैसा नहीं जाता।',
        'ar': '{capability} يتطلب {needs} (${price}/{period}). هذا الحساب على '
              '{have}. الفوترة هنا محاكاة — الاشتراك يسجل صفًا ولا ينقل '
              'أموالًا حقيقية.',
    },
    MUST_BE_ONE_OF: {
        'es': '{field} debe ser uno de {choices}',
        'fr': '{field} doit être l\'un de {choices}',
        'de': '{field} muss eines von {choices} sein',
        'pt': '{field} deve ser um de {choices}',
        'it': '{field} deve essere uno tra {choices}',
        'ja': '{field} は次のいずれかにしてください: {choices}',
        'zh': '{field} 必须是以下之一：{choices}',
        'hi': '{field} इनमें से एक होना चाहिए: {choices}',
        'ar': '{field} يجب أن يكون أحد التالي: {choices}',
    },
    UNKNOWN_SURFACE: {
        'es': 'superficie desconocida {surface} — una de {choices}',
        'fr': 'surface inconnue {surface} — l\'une de {choices}',
        'de': 'unbekannte Oberfläche {surface} — eine von {choices}',
        'pt': 'superfície desconhecida {surface} — uma de {choices}',
        'it': 'superficie sconosciuta {surface} — una tra {choices}',
        'ja': '不明なサーフェス {surface} — 次のいずれかです: {choices}',
        'zh': '未知的呈现面 {surface} — 应为以下之一：{choices}',
        'hi': 'अज्ञात सतह {surface} — इनमें से एक: {choices}',
        'ar': 'سطح غير معروف {surface} — أحد التالي: {choices}',
    },
    OBJECTION_ALREADY: {
        'es': 'la objeción ya está {status}',
        'fr': 'l\'objection est déjà {status}',
        'de': 'der Einspruch ist bereits {status}',
        'pt': 'a objeção já está {status}',
        'it': 'l\'obiezione è già {status}',
        'ja': 'この異議はすでに{status}です',
        'zh': '该异议已经{status}',
        'hi': 'यह आपत्ति पहले ही {status} है',
        'ar': 'هذا الاعتراض {status} بالفعل',
    },
    MESSAGE_ALREADY: {
        'es': 'el mensaje ya está {status}',
        'fr': 'le message est déjà {status}',
        'de': 'die Nachricht ist bereits {status}',
        'pt': 'a mensagem já está {status}',
        'it': 'il messaggio è già {status}',
        'ja': 'このメッセージはすでに{status}です',
        'zh': '该消息已经{status}',
        'hi': 'यह संदेश पहले ही {status} है',
        'ar': 'هذه الرسالة {status} بالفعل',
    },
    PROFILE_ALREADY: {
        'es': 'el perfil ya está {status}',
        'fr': 'le profil est déjà {status}',
        'de': 'das Profil ist bereits {status}',
        'pt': 'o perfil já está {status}',
        'it': 'il profilo è già {status}',
        'ja': 'このプロフィールはすでに{status}です',
        'zh': '该档案已经{status}',
        'hi': 'यह प्रोफ़ाइल पहले ही {status} है',
        'ar': 'هذا الملف {status} بالفعل',
    },
    NOT_A_MEMORIAL: {
        'es': 'este perfil está {status}, no es un memorial',
        'fr': 'ce profil est {status}, ce n\'est pas un mémorial',
        'de': 'dieses Profil ist {status} und kein Gedenkprofil',
        'pt': 'este perfil está {status}, não é um memorial',
        'it': 'questo profilo è {status}, non è un memoriale',
        'ja': 'このプロフィールは{status}であり、追悼プロフィールではありません',
        'zh': '该档案为{status}，不是纪念档案',
        'hi': 'यह प्रोफ़ाइल {status} है, स्मारक नहीं',
        'ar': 'هذا الملف {status}، وليس ملفًا تذكاريًا',
    },
}

#: The product's own closed-set words, for the moment one lands inside a
#: sentence a person reads. They stay keys on the wire — the console branches
#: on `status` — so this is only ever applied by `term()` at the last step.
_VOCABULARY: dict[str, dict[str, str]] = {
    # The billing period, and the eight capability descriptions the plan gate
    # names. Longer than the state words above, and belonging here for the same
    # reason: they are a closed set this product authors, so there is a
    # translation for each and no guessing involved. `_SLOT_TOKEN` would refuse
    # them for having spaces, which is why `Term` is exempt from it.
    'month': {'es': 'mes', 'fr': 'mois', 'de': 'Monat', 'pt': 'mês',
              'it': 'mese', 'ja': '月', 'zh': '月', 'hi': 'माह',
              'ar': 'شهر'},
    'create and run your own synthetic profiles': {
        'es': 'crear y ejecutar tus propios perfiles sintéticos',
        'fr': 'créer et faire tourner vos propres profils synthétiques',
        'de': 'eigene synthetische Profile erstellen und betreiben',
        'pt': 'criar e executar os seus próprios perfis sintéticos',
        'it': 'creare e gestire i tuoi profili sintetici',
        'ja': '自分の合成プロフィールを作成して動かすこと',
        'zh': '创建并运行你自己的合成档案',
        'hi': 'अपनी स्वयं की सिंथेटिक प्रोफ़ाइल बनाना और चलाना',
        'ar': 'إنشاء ملفاتك الاصطناعية وتشغيلها'},
    'your own personal agent': {
        'es': 'tu propio agente personal',
        'fr': 'votre propre agent personnel',
        'de': 'Ihr eigener persönlicher Agent',
        'pt': 'o seu próprio agente pessoal',
        'it': 'il tuo agente personale',
        'ja': '自分専用のエージェント',
        'zh': '你自己的个人代理',
        'hi': 'आपका अपना निजी एजेंट',
        'ar': 'وكيلك الشخصي الخاص'},
    'every modifier and builder for your agent — steering, adaptation, '
    'governance and delegation': {
        'es': 'todos los modificadores y constructores de tu agente: '
              'dirección, adaptación, gobernanza y delegación',
        'fr': 'tous les modificateurs et constructeurs de votre agent : '
              'pilotage, adaptation, gouvernance et délégation',
        'de': 'alle Modifikatoren und Baukästen für Ihren Agenten — Steuerung, '
              'Anpassung, Governance und Delegation',
        'pt': 'todos os modificadores e construtores do seu agente: direção, '
              'adaptação, governança e delegação',
        'it': 'tutti i modificatori e i costruttori del tuo agente: '
              'orientamento, adattamento, governance e delega',
        'ja': 'エージェントのすべての調整項目とビルダー — ステアリング、適応、'
              'ガバナンス、委任',
        'zh': '代理的全部调节项与构建器 — 引导、适应、治理与委派',
        'hi': 'आपके एजेंट के सभी संशोधक और बिल्डर — स्टीयरिंग, अनुकूलन, '
              'शासन और प्रत्यायोजन',
        'ar': 'كل أدوات التعديل والبناء لوكيلك — التوجيه والتكيّف والحوكمة '
              'والتفويض'},
    'list, sell, license, place and buy on the marketplace': {
        'es': 'publicar, vender, licenciar, colocar y comprar en el mercado',
        'fr': 'lister, vendre, licencier, placer et acheter sur la place '
              'de marché',
        'de': 'im Marktplatz einstellen, verkaufen, lizenzieren, platzieren '
              'und kaufen',
        'pt': 'listar, vender, licenciar, colocar e comprar no mercado',
        'it': 'pubblicare, vendere, concedere in licenza, collocare e '
              'acquistare sul marketplace',
        'ja': 'マーケットプレイスでの出品・販売・ライセンス・配置・購入',
        'zh': '在市场中上架、出售、授权、投放与购买',
        'hi': 'मार्केटप्लेस पर सूचीबद्ध करना, बेचना, लाइसेंस देना, रखना और खरीदना',
        'ar': 'العرض والبيع والترخيص والوضع والشراء في السوق'},
    'install knowledge packs and downloads': {
        'es': 'instalar paquetes de conocimiento y descargas',
        'fr': 'installer des packs de connaissances et des téléchargements',
        'de': 'Wissenspakete und Downloads installieren',
        'pt': 'instalar pacotes de conhecimento e transferências',
        'it': 'installare pacchetti di conoscenza e download',
        'ja': 'ナレッジパックとダウンロードのインストール',
        'zh': '安装知识包与下载内容',
        'hi': 'नॉलेज पैक और डाउनलोड इंस्टॉल करना',
        'ar': 'تثبيت حزم المعرفة والتنزيلات'},
    'connect outside apps and services to a profile': {
        'es': 'conectar aplicaciones y servicios externos a un perfil',
        'fr': 'connecter des applications et services externes à un profil',
        'de': 'externe Apps und Dienste mit einem Profil verbinden',
        'pt': 'ligar aplicações e serviços externos a um perfil',
        'it': 'collegare app e servizi esterni a un profilo',
        'ja': '外部のアプリやサービスをプロフィールに接続すること',
        'zh': '将外部应用与服务连接到档案',
        'hi': 'बाहरी ऐप्स और सेवाओं को प्रोफ़ाइल से जोड़ना',
        'ar': 'ربط التطبيقات والخدمات الخارجية بملف'},
    'lend a skill to another profile, or borrow one': {
        'es': 'prestar una habilidad a otro perfil, o tomar una prestada',
        'fr': "prêter une compétence à un autre profil, ou en emprunter une",
        'de': 'eine Fähigkeit an ein anderes Profil verleihen oder eine leihen',
        'pt': 'emprestar uma competência a outro perfil, ou pedir uma '
              'emprestada',
        'it': "prestare un'abilità a un altro profilo, o prenderne una in "
              'prestito',
        'ja': '他のプロフィールにスキルを貸す、または借りること',
        'zh': '把技能借给其他档案，或借用一项',
        'hi': 'किसी अन्य प्रोफ़ाइल को कौशल उधार देना, या एक उधार लेना',
        'ar': 'إعارة مهارة لملف آخر أو استعارة واحدة'},
    'standing connections to other accounts': {
        'es': 'conexiones permanentes con otras cuentas',
        'fr': 'connexions permanentes avec d\'autres comptes',
        'de': 'dauerhafte Verbindungen zu anderen Konten',
        'pt': 'ligações permanentes a outras contas',
        'it': 'connessioni permanenti ad altri account',
        'ja': '他のアカウントとの継続的な接続',
        'zh': '与其他账户的长期连接',
        'hi': 'अन्य खातों से स्थायी संबंध',
        'ar': 'اتصالات دائمة بحسابات أخرى'},
    'open': {'es': 'abierta', 'fr': 'ouverte', 'de': 'offen', 'pt': 'aberta',
             'it': 'aperta', 'ja': '未処理', 'zh': '待处理', 'hi': 'खुली',
             'ar': 'مفتوح'},
    'upheld': {'es': 'aceptada', 'fr': 'acceptée', 'de': 'stattgegeben',
               'pt': 'aceita', 'it': 'accolta', 'ja': '認容済み',
               'zh': '支持', 'hi': 'स्वीकृत', 'ar': 'مقبول'},
    'dismissed': {'es': 'rechazada', 'fr': 'rejetée', 'de': 'abgewiesen',
                  'pt': 'rejeitada', 'it': 'respinta', 'ja': '却下済み',
                  'zh': '驳回', 'hi': 'खारिज', 'ar': 'مرفوض'},
    'withdrawn': {'es': 'retirada', 'fr': 'retirée', 'de': 'zurückgezogen',
                  'pt': 'retirada', 'it': 'ritirata', 'ja': '取り下げ済み',
                  'zh': '撤回', 'hi': 'वापस ली गई', 'ar': 'مسحوب'},
    'delivered': {'es': 'entregado', 'fr': 'livré', 'de': 'zugestellt',
                  'pt': 'entregue', 'it': 'consegnato', 'ja': '配信済み',
                  'zh': '送达', 'hi': 'वितरित', 'ar': 'تم التسليم'},
    'blocked': {'es': 'bloqueado', 'fr': 'bloqué', 'de': 'blockiert',
                'pt': 'bloqueado', 'it': 'bloccato', 'ja': 'ブロック済み',
                'zh': '拦截', 'hi': 'अवरुद्ध', 'ar': 'محظور'},
    'active': {'es': 'activo', 'fr': 'actif', 'de': 'aktiv', 'pt': 'ativo',
               'it': 'attivo', 'ja': '有効', 'zh': '启用中', 'hi': 'सक्रिय',
               'ar': 'نشط'},
    'memorial': {'es': 'memorial', 'fr': 'mémorial', 'de': 'Gedenkprofil',
                 'pt': 'memorial', 'it': 'memoriale', 'ja': '追悼',
                 'zh': '纪念', 'hi': 'स्मारक', 'ar': 'تذكاري'},
    'departed': {'es': 'retirado', 'fr': 'retiré', 'de': 'ausgeschieden',
                 'pt': 'retirado', 'it': 'ritirato', 'ja': '退出済み',
                 'zh': '离开', 'hi': 'निवृत्त', 'ar': 'منسحب'},
    'revoked': {'es': 'revocada', 'fr': 'révoquée', 'de': 'widerrufen',
                'pt': 'revogada', 'it': 'revocata', 'ja': '取消済み',
                'zh': '撤销', 'hi': 'निरस्त', 'ar': 'ملغى'},
    'restricted': {'es': 'restringido', 'fr': 'restreint',
                   'de': 'eingeschränkt', 'pt': 'restrito',
                   'it': 'limitato', 'ja': '制限中', 'zh': '受限',
                   'hi': 'प्रतिबंधित', 'ar': 'مقيد'},
    'terminated': {'es': 'cerrado', 'fr': 'clôturé', 'de': 'beendet',
                   'pt': 'encerrado', 'it': 'chiuso', 'ja': '終了済み',
                   'zh': '终止', 'hi': 'समाप्त', 'ar': 'منهى'},
    'suspended': {'es': 'suspendido', 'fr': 'suspendu', 'de': 'gesperrt',
                  'pt': 'suspenso', 'it': 'sospeso', 'ja': '停止中',
                  'zh': '暂停', 'hi': 'निलंबित', 'ar': 'موقوف'},
}


_REFUSALS: dict[str, dict[str, str]] = {
    'authentication required': {
        'es': 'se requiere autenticación',
        'fr': 'authentification requise',
        'de': 'Authentifizierung erforderlich',
        'pt': 'autenticação necessária',
        'it': 'autenticazione richiesta',
        'ja': '認証が必要です',
        'zh': '需要身份验证',
        'hi': 'प्रमाणीकरण आवश्यक है',
        'ar': 'المصادقة مطلوبة',
    },
    'not authorized for this resource': {
        'es': 'sin autorización para este recurso',
        'fr': 'non autorisé pour cette ressource',
        'de': 'keine Berechtigung für diese Ressource',
        'pt': 'sem autorização para este recurso',
        'it': 'non autorizzato per questa risorsa',
        'ja': 'このリソースへの権限がありません',
        'zh': '无权访问此资源',
        'hi': 'इस संसाधन के लिए अधिकार नहीं है',
        'ar': 'غير مخوَّل للوصول إلى هذا المورد',
    },
    "authentication required — this acts on somebody's behalf, so it has to "
    "know it is them": {
        'es': 'se requiere autenticación — esto actúa en nombre de alguien, '
              'así que tiene que saber que es esa persona',
        'fr': "authentification requise — ceci agit au nom de quelqu'un, il "
              "faut donc savoir que c'est bien cette personne",
        'de': 'Authentifizierung erforderlich — dies handelt im Namen einer '
              'Person, also muss feststehen, dass sie es ist',
        'pt': 'autenticação necessária — isto age em nome de alguém, por isso '
              'tem de saber que é essa pessoa',
        'it': 'autenticazione richiesta — questo agisce per conto di '
              'qualcuno, quindi deve sapere che è davvero lui',
        'ja': '認証が必要です — これは誰かの代理として行う操作なので、本人で'
              'あることを確かめる必要があります',
        'zh': '需要身份验证 — 此操作代表他人执行，因此必须确认是本人',
        'hi': 'प्रमाणीकरण आवश्यक है — यह किसी की ओर से किया जाने वाला कार्य है, '
              'इसलिए यह जानना ज़रूरी है कि वह वही व्यक्ति है',
        'ar': 'المصادقة مطلوبة — هذا الإجراء يتم نيابةً عن شخص، لذا يجب '
              'التأكد من أنه هو',
    },
    'that is not you — an id in a request body is a claim, and this one does '
    'not match the token presented': {
        'es': 'esa no es tu identidad — un id en el cuerpo de una petición es '
              'una afirmación, y este no coincide con el token presentado',
        'fr': "ce n'est pas vous — un identifiant dans le corps d'une requête "
              "est une affirmation, et celui-ci ne correspond pas au jeton "
              "présenté",
        'de': 'das sind nicht Sie — eine ID im Anfragetext ist eine '
              'Behauptung, und diese passt nicht zum vorgelegten Token',
        'pt': 'essa não é a sua identidade — um id no corpo de um pedido é '
              'uma afirmação, e este não corresponde ao token apresentado',
        'it': "quella non è la tua identità — un id nel corpo di una "
              "richiesta è un'affermazione, e questo non corrisponde al token "
              "presentato",
        'ja': 'それはあなたではありません — リクエスト本文の id は主張にすぎず、'
              '提示されたトークンと一致しません',
        'zh': '那不是你 — 请求体中的 id 只是一种声称，而它与所出示的令牌不符',
        'hi': 'वह आप नहीं हैं — अनुरोध के मुख्य भाग में दिया गया id एक दावा है, '
              'और यह प्रस्तुत टोकन से मेल नहीं खाता',
        'ar': 'هذا لست أنت — المعرِّف في جسم الطلب مجرد ادعاء، وهو لا يطابق '
              'الرمز المقدَّم',
    },
    'only the people involved in this can act on it': {
        'es': 'solo las personas implicadas en esto pueden actuar sobre ello',
        'fr': 'seules les personnes concernées peuvent agir ici',
        'de': 'nur die daran beteiligten Personen können hier handeln',
        'pt': 'só as pessoas envolvidas nisto podem agir sobre isto',
        'it': 'solo le persone coinvolte possono agire su questo',
        'ja': 'これに関わっている人だけが操作できます',
        'zh': '只有参与此事的人才能对其进行操作',
        'hi': 'इसमें शामिल लोग ही इस पर कार्रवाई कर सकते हैं',
        'ar': 'لا يمكن التصرف في هذا إلا للأشخاص المعنيين به',
    },
    'interactor not found': {
        'es': 'interlocutor no encontrado',
        'fr': 'interlocuteur introuvable',
        'de': 'Interaktionspartner nicht gefunden',
        'pt': 'interlocutor não encontrado',
        'it': 'interlocutore non trovato',
        'ja': '対話相手が見つかりません',
        'zh': '未找到互动者',
        'hi': 'संवादकर्ता नहीं मिला',
        'ar': 'لم يتم العثور على المتفاعل',
    },
    'reviewer token required': {
        'es': 'se requiere un token de revisor',
        'fr': "jeton d'examinateur requis",
        'de': 'Prüfer-Token erforderlich',
        'pt': 'é necessário um token de revisor',
        'it': 'è richiesto un token di revisore',
        'ja': '審査者トークンが必要です',
        'zh': '需要审核员令牌',
        'hi': 'समीक्षक टोकन आवश्यक है',
        'ar': 'رمز المراجع مطلوب',
    },
    'invalid reviewer token': {
        'es': 'token de revisor no válido',
        'fr': "jeton d'examinateur invalide",
        'de': 'ungültiges Prüfer-Token',
        'pt': 'token de revisor inválido',
        'it': 'token di revisore non valido',
        'ja': '審査者トークンが無効です',
        'zh': '审核员令牌无效',
        'hi': 'समीक्षक टोकन अमान्य है',
        'ar': 'رمز المراجع غير صالح',
    },
    'this deployment requires a signup key to create a profile — send it as '
    'the x-signup-key header': {
        'es': 'esta instalación requiere una clave de registro para crear un '
              'perfil — envíala en la cabecera x-signup-key',
        'fr': "cette installation exige une clé d'inscription pour créer un "
              "profil — envoyez-la dans l'en-tête x-signup-key",
        'de': 'diese Installation verlangt einen Registrierungsschlüssel, um '
              'ein Profil anzulegen — senden Sie ihn im Header x-signup-key',
        'pt': 'esta instalação exige uma chave de registo para criar um '
              'perfil — envie-a no cabeçalho x-signup-key',
        'it': 'questa installazione richiede una chiave di registrazione per '
              "creare un profilo — inviala nell'intestazione x-signup-key",
        'ja': 'この配備でプロフィールを作成するには登録キーが必要です — '
              'x-signup-key ヘッダーで送ってください',
        'zh': '此部署需要注册密钥才能创建档案 — 请在 x-signup-key 请求头中发送',
        'hi': 'इस परिनियोजन में प्रोफ़ाइल बनाने के लिए साइनअप कुंजी चाहिए — इसे '
              'x-signup-key हेडर में भेजें',
        'ar': 'يتطلب هذا النشر مفتاح تسجيل لإنشاء ملف تعريف — أرسله في ترويسة '
              'x-signup-key',
    },
}


# --------------------------------------------------------------------------- #
# The refusal that handed the body back
# --------------------------------------------------------------------------- #
#
# The round above put every refusal this product *writes* into the reader's
# language, through one handler no raise site opts into. It missed every
# refusal this product *returns*.
#
#     asked     is every refusal this product writes translated
#     mattered  is every refusal this product returns
#
# `RequestValidationError` is not an `HTTPException`. FastAPI raises it before
# any handler of ours runs and renders it with its own, so a 422 — the refusal
# a person meets most often, because it is what a mistyped form produces —
# went out in English past a handler written to catch everything.
#
# ## The larger half
#
# Pydantic's error rows carry an `input` key holding **the value that failed**,
# which for a missing field is the entire submitted body. So the 422 handed it
# straight back:
#
#     {"type": "missing", "loc": ["body", "text"], "msg": "Field required",
#      "input": {"entry": "chest pain since Tuesday, have not told my
#                daughter", "mood": 3}}
#
# That is JIM's. PDI's returned a record value in plaintext — on the one path
# in an encrypted vault that never touches the encryption layer. Every other
# part of this ecosystem's error design refuses to carry content: `errors.ts`
# and the nine `Problems` modules record a method, a redacted path and a
# status and have no parameter a message could arrive through; `cloudgw`
# refuses a report whole if it finds prose in it. The one place content left
# the process was the framework's default renderer, because nobody had looked
# at it as ours.
#
# ## What is returned now
#
# `type` and `loc`, which are the client's vocabulary — a console highlights
# the field that `loc` names — and `msg`. Not `input`, and not `ctx`: `ctx`
# carries a validator's own exception on `value_error`, which is a second door
# into the same room.
#
# Two narrower rules, both for text that comes from *our* code rather than
# pydantic's fixed catalogue:
#
# * `value_error` and `assertion_error` messages are replaced outright. Their
#   text is whatever a validator raised, and a validator that quotes the value
#   it rejected — `f"unknown site {site!r}"` — is the same leak wearing a
#   different key. No model here has one today. The rule is for the day one is
#   added, which is the only time this would otherwise be noticed.
# * On `extra_forbidden`, the last element of `loc` is the caller's own key
#   name rather than a field this product declares — so it is echoed only when
#   it is *shaped* like a field name. Naming the key is the point of that
#   refusal; a key with spaces in it is not a typo, it is content.


#: What is said instead of a validator's own words. Deliberately useless as a
#: hint: `loc` still names the field, and a sentence that explained more would
#: be quoting the thing this exists to stop quoting.
UNSPECIFIED_VALUE_ERROR = "that value is not acceptable here"

#: Where a caller's own key name would otherwise be echoed.
UNRECOGNISED_FIELD = "<unrecognised field>"

#: What a mistyped field name looks like. A key matching this is echoed back on
#: `extra_forbidden`, because naming it is the whole value of that refusal:
#: `test_a_write_that_answers_200_did_something` exists because two routes used
#: to accept `dials` for `values` and `years` for `period`, discard them, and
#: answer 200. A round was spent making those strict so the caller is *told*
#: which key was wrong, and the first version of this file redacted it away
#: again — caught by that guard, which is what it was written for.
#:
#:     asked     can a key carry content
#:     mattered  does this key look like content
#:
#: Anything else — a key with spaces in it, a sentence, something longer than a
#: field name has any business being — is replaced. A client that builds an
#: object keyed on what somebody typed produces exactly that shape.
_FIELD_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,39}$")

_OUR_OWN_WORDS = ("value_error", "assertion_error")


def validation_detail(errors, language: str) -> list[dict]:
    """Pydantic's error rows, with everything the caller sent taken out.

    Built by allowing three keys rather than by removing `input`. A denylist
    would have to be revisited every time pydantic adds a key; this cannot
    grow a leak by someone else's release.
    """
    rows = []
    for error in errors:
        kind = str(error.get("type", ""))
        where = list(error.get("loc", ()))
        if (kind == "extra_forbidden" and where
                and not _FIELD_NAME.match(str(where[-1]))):
            where[-1] = UNRECOGNISED_FIELD
        message = (UNSPECIFIED_VALUE_ERROR if kind in _OUR_OWN_WORDS
                   else str(error.get("msg", "")))
        rows.append({
            "type": kind,
            "loc": [p if isinstance(p, int) else str(p) for p in where],
            "msg": tr_refusal(message, language),
        })
    return rows


#: The first element of a pydantic `loc`, naming which part of the request the
#: field was in rather than naming a field. Dropped when composing the
#: sentence: a person reading "body.display_name" learns nothing from "body"
#: that the form they are looking at has not already told them.
_WHERE_MARKERS = ("body", "query", "path", "header", "cookie")


def validation_message(rows: list[dict], language: str) -> str:
    """One sentence, from rows a person was never going to read.

    `validation_detail` above puts pydantic's rows into the reader's language.
    Nine clients then rendered them: the three consoles printed the array as
    JSON, the three Android shells did the same by coercion, and the iOS and
    Windows shells asked for a string, got an array, and fell back to the
    status code. So a mistyped form said either `[{"type":"missing",...}]` or
    `HTTP 422`.

        asked     is the refusal translated
        mattered  is the refusal a sentence

    Composed here rather than in each client for the reason the refusal
    handler is one handler: nine renderings of one thing are nine chances to
    render it differently, and six of these are in languages with no test
    runner in this repository.

    ## What stays an identifier

    The field name is not translated and is not meant to read as a word. It is
    the API's name for the field — `display_name` — which is the same string in
    every language, and it is joined to the sentence with an em dash rather
    than declined into it, so nothing here is half in one language and half in
    another. That is the failure `tests/refusals_untranslated.txt` refuses to
    ship for the plan gate, and it applies here too.

    Mapping those names to the labels a form actually shows — *"Nome de
    exibição"* rather than `display_name` — is a per-client table this does not
    have, and is recorded as the remaining gap rather than guessed at.

    Carries nothing `detail` does not: the same `loc` and the same already
    redacted `msg`, which is what `test_the_sentence_says_no_more_than_the_rows`
    holds it to.
    """
    parts = []
    for row in rows:
        where = [str(p) for p in row.get("loc", ())]
        if where and where[0] in _WHERE_MARKERS:
            where = where[1:]
        name = ".".join(tr_refusal(p, language) if p == UNRECOGNISED_FIELD
                        else p for p in where)
        said = str(row.get("msg", ""))
        parts.append(f"{name} — {said}" if name else said)
    return "; ".join(p for p in parts if p)


#: Pydantic's own catalogue, for the messages this product's forms can
#: produce. Safe to pass through untranslated as well as translated: these
#: sentences interpolate limits, never the value that failed. Anything not
#: here falls through as English, which is a visible gap rather than a
#: confident error.
_VALIDATION: dict[str, dict[str, str]] = {
    # Not a message but a field name, and the one field name that is prose:
    # `validation_detail` substitutes it where a caller's own key would
    # otherwise be echoed, so it lands in the sentence `validation_message`
    # composes and has to be readable there.
    UNRECOGNISED_FIELD: {
        'es': '<campo no reconocido>',
        'fr': '<champ non reconnu>',
        'de': '<unbekanntes Feld>',
        'pt': '<campo não reconhecido>',
        'it': '<campo non riconosciuto>',
        'ja': '<認識できない項目>',
        'zh': '<无法识别的字段>',
        'hi': '<अपरिचित फ़ील्ड>',
        'ar': '<حقل غير معروف>',
    },
    UNSPECIFIED_VALUE_ERROR: {
        'es': 'ese valor no es aceptable aquí',
        'fr': "cette valeur n'est pas acceptable ici",
        'de': 'dieser Wert ist hier nicht zulässig',
        'pt': 'esse valor não é aceitável aqui',
        'it': 'questo valore non è accettabile qui',
        'ja': 'この値はここでは使えません',
        'zh': '此处不接受该值',
        'hi': 'यह मान यहाँ स्वीकार्य नहीं है',
        'ar': 'هذه القيمة غير مقبولة هنا',
    },
    'Field required': {
        'es': 'campo obligatorio',
        'fr': 'champ requis',
        'de': 'Pflichtfeld',
        'pt': 'campo obrigatório',
        'it': 'campo obbligatorio',
        'ja': '必須項目です',
        'zh': '此字段为必填项',
        'hi': 'यह फ़ील्ड आवश्यक है',
        'ar': 'حقل مطلوب',
    },
    'Extra inputs are not permitted': {
        'es': 'no se admiten campos adicionales',
        'fr': 'les champs supplémentaires ne sont pas autorisés',
        'de': 'zusätzliche Felder sind nicht zulässig',
        'pt': 'não são permitidos campos adicionais',
        'it': 'non sono ammessi campi aggiuntivi',
        'ja': '追加の項目は指定できません',
        'zh': '不允许提供额外字段',
        'hi': 'अतिरिक्त फ़ील्ड की अनुमति नहीं है',
        'ar': 'لا يُسمح بحقول إضافية',
    },
    'Input should be a valid string': {
        'es': 'debe ser una cadena de texto válida',
        'fr': 'doit être une chaîne de caractères valide',
        'de': 'muss eine gültige Zeichenkette sein',
        'pt': 'tem de ser uma cadeia de texto válida',
        'it': 'deve essere una stringa valida',
        'ja': '有効な文字列を指定してください',
        'zh': '应为有效的字符串',
        'hi': 'यह एक मान्य स्ट्रिंग होनी चाहिए',
        'ar': 'يجب أن تكون سلسلة نصية صالحة',
    },
    'Input should be a valid integer': {
        'es': 'debe ser un número entero válido',
        'fr': 'doit être un entier valide',
        'de': 'muss eine gültige ganze Zahl sein',
        'pt': 'tem de ser um número inteiro válido',
        'it': 'deve essere un numero intero valido',
        'ja': '有効な整数を指定してください',
        'zh': '应为有效的整数',
        'hi': 'यह एक मान्य पूर्णांक होना चाहिए',
        'ar': 'يجب أن يكون عددًا صحيحًا صالحًا',
    },
    'Input should be a valid number': {
        'es': 'debe ser un número válido',
        'fr': 'doit être un nombre valide',
        'de': 'muss eine gültige Zahl sein',
        'pt': 'tem de ser um número válido',
        'it': 'deve essere un numero valido',
        'ja': '有効な数値を指定してください',
        'zh': '应为有效的数字',
        'hi': 'यह एक मान्य संख्या होनी चाहिए',
        'ar': 'يجب أن يكون رقمًا صالحًا',
    },
    'Input should be a valid boolean': {
        'es': 'debe ser un valor booleano válido',
        'fr': 'doit être un booléen valide',
        'de': 'muss ein gültiger Wahrheitswert sein',
        'pt': 'tem de ser um valor booleano válido',
        'it': 'deve essere un valore booleano valido',
        'ja': '有効な真偽値を指定してください',
        'zh': '应为有效的布尔值',
        'hi': 'यह एक मान्य बूलियन मान होना चाहिए',
        'ar': 'يجب أن تكون قيمة منطقية صالحة',
    },
    'Input should be a valid list': {
        'es': 'debe ser una lista válida',
        'fr': 'doit être une liste valide',
        'de': 'muss eine gültige Liste sein',
        'pt': 'tem de ser uma lista válida',
        'it': 'deve essere un elenco valido',
        'ja': '有効なリストを指定してください',
        'zh': '应为有效的列表',
        'hi': 'यह एक मान्य सूची होनी चाहिए',
        'ar': 'يجب أن تكون قائمة صالحة',
    },
    'Input should be a valid dictionary': {
        'es': 'debe ser un objeto válido',
        'fr': 'doit être un objet valide',
        'de': 'muss ein gültiges Objekt sein',
        'pt': 'tem de ser um objeto válido',
        'it': 'deve essere un oggetto valido',
        'ja': '有効なオブジェクトを指定してください',
        'zh': '应为有效的对象',
        'hi': 'यह एक मान्य ऑब्जेक्ट होना चाहिए',
        'ar': 'يجب أن يكون كائنًا صالحًا',
    },
    'Input should be a valid date': {
        'es': 'debe ser una fecha válida',
        'fr': 'doit être une date valide',
        'de': 'muss ein gültiges Datum sein',
        'pt': 'tem de ser uma data válida',
        'it': 'deve essere una data valida',
        'ja': '有効な日付を指定してください',
        'zh': '应为有效的日期',
        'hi': 'यह एक मान्य दिनांक होनी चाहिए',
        'ar': 'يجب أن يكون تاريخًا صالحًا',
    },
}
