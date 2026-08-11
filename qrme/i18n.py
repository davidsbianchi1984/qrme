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
    'a hashtag names a topic, not an account — give the account\'s handle or paste its link': {
        'es': 'un hashtag nombra un tema, no una cuenta: da el identificador de la cuenta o pega su enlace.',
        'fr': "un hashtag désigne un sujet, pas un compte — donnez l'identifiant du compte ou collez son lien.",
        'de': 'ein Hashtag benennt ein Thema, kein Konto — gib den Handle des Kontos an oder füge seinen Link ein.',
        'pt': 'uma hashtag nomeia um tema, não uma conta — dê o identificador da conta ou cole o seu link.',
        'it': 'un hashtag nomina un argomento, non un account — indica l\'handle dell\'account o incolla il suo link.',
        'ja': 'ハッシュタグはトピックの名前であり、アカウントではありません。アカウントのハンドルを入力するか、リンクを貼り付けてください。',
        'zh': '话题标签指的是话题，不是账号——请提供账号的用户名或粘贴其链接。',
        'hi': 'हैशटैग किसी विषय का नाम है, खाते का नहीं — खाते का हैंडल दें या उसका लिंक चिपकाएँ।',
        'ar': 'الوسم يسمي موضوعًا لا حسابًا — أعطِ معرّف الحساب أو الصق رابطه.',
    },
    'that link\'s site is not a platform this deployment recognises — pick the platform and type the handle instead': {
        'es': 'el sitio de ese enlace no es una plataforma que este despliegue reconozca: elige la plataforma y escribe el identificador en su lugar.',
        'fr': "le site de ce lien n'est pas une plateforme reconnue par ce déploiement — choisissez la plateforme et saisissez l'identifiant à la place.",
        'de': 'die Website dieses Links ist keine Plattform, die diese Installation kennt — wähle die Plattform und gib stattdessen den Handle ein.',
        'pt': 'o site desse link não é uma plataforma que esta instalação reconheça — escolha a plataforma e escreva o identificador em vez disso.',
        'it': 'il sito di quel link non è una piattaforma riconosciuta da questa installazione — scegli la piattaforma e digita l\'handle al suo posto.',
        'ja': 'そのリンクのサイトは、この環境が認識するプラットフォームではありません。代わりにプラットフォームを選んでハンドルを入力してください。',
        'zh': '该链接的网站不是此部署可识别的平台——请改为选择平台并输入账号名。',
        'hi': 'उस लिंक की साइट ऐसी प्लेटफ़ॉर्म नहीं है जिसे यह परिनियोजन पहचानता हो — इसके बजाय प्लेटफ़ॉर्म चुनें और हैंडल लिखें।',
        'ar': 'موقع هذا الرابط ليس منصة يتعرف عليها هذا النشر — اختر المنصة واكتب المعرّف بدلًا من ذلك.',
    },
    'that link has no account in it — paste the profile\'s own page, not the platform\'s front door': {
        'es': 'ese enlace no contiene ninguna cuenta: pega la página propia del perfil, no la portada de la plataforma.',
        'fr': "ce lien ne contient aucun compte — collez la page du profil lui-même, pas la porte d'entrée de la plateforme.",
        'de': 'dieser Link enthält kein Konto — füge die eigene Seite des Profils ein, nicht die Startseite der Plattform.',
        'pt': 'esse link não contém nenhuma conta — cole a página do próprio perfil, não a porta de entrada da plataforma.',
        'it': 'quel link non contiene alcun account — incolla la pagina del profilo stesso, non l\'ingresso della piattaforma.',
        'ja': 'そのリンクにはアカウントが含まれていません。プラットフォームの入口ではなく、プロフィール自身のページを貼り付けてください。',
        'zh': '该链接里没有账号——请粘贴档案自己的页面，而不是平台的首页。',
        'hi': 'उस लिंक में कोई खाता नहीं है — प्लेटफ़ॉर्म का मुख्य द्वार नहीं, प्रोफ़ाइल का अपना पेज चिपकाएँ।',
        'ar': 'هذا الرابط لا يحتوي على حساب — الصق صفحة الملف نفسه، لا الباب الأمامي للمنصة.',
    },
    'this deployment is offline — nothing leaves this machine, so the page cannot be fetched. Paste the content into collect instead.': {
        'es': 'este despliegue está sin conexión: nada sale de esta máquina, así que la página no puede traerse. Pega el contenido en recopilar en su lugar.',
        'fr': "ce déploiement est hors ligne — rien ne quitte cette machine, la page ne peut donc pas être récupérée. Collez plutôt le contenu dans la collecte.",
        'de': 'diese Installation ist offline — nichts verlässt diesen Rechner, also kann die Seite nicht geholt werden. Füge den Inhalt stattdessen ins Sammeln ein.',
        'pt': 'esta instalação está offline — nada sai desta máquina, então a página não pode ser buscada. Cole o conteúdo em recolher em vez disso.',
        'it': 'questa installazione è offline — nulla esce da questa macchina, quindi la pagina non può essere recuperata. Incolla invece il contenuto nella raccolta.',
        'ja': 'この環境はオフラインです — このマシンから何も出ないため、ページを取得できません。代わりに内容を収集に貼り付けてください。',
        'zh': '此部署处于离线状态 — 任何内容都不会离开这台机器，因此无法抓取页面。请改为将内容粘贴到采集中。',
        'hi': 'यह परिनियोजन ऑफ़लाइन है — इस मशीन से कुछ बाहर नहीं जाता, इसलिए पेज नहीं लाया जा सकता। इसके बजाय सामग्री को संग्रह में चिपकाएँ।',
        'ar': 'هذا النشر دون اتصال — لا شيء يغادر هذا الجهاز، لذا لا يمكن جلب الصفحة. الصق المحتوى في الجمع بدلًا من ذلك.',
    },
    'this connection has no public address to visit — reconnect with the account\'s handle, or paste content into collect': {
        'es': 'esta conexión no tiene dirección pública que visitar: reconecta con el identificador de la cuenta o pega contenido en recopilar',
        'fr': "cette connexion n'a pas d'adresse publique à visiter — reconnectez avec l'identifiant du compte, ou collez le contenu dans la collecte",
        'de': 'diese Verbindung hat keine öffentliche Adresse zum Besuchen — verbinde neu mit der Kennung des Kontos oder füge Inhalt ins Sammeln ein',
        'pt': 'esta ligação não tem endereço público para visitar — volte a ligar com o identificador da conta, ou cole conteúdo em recolher',
        'it': "questa connessione non ha un indirizzo pubblico da visitare — ricollega con l'handle dell'account, o incolla il contenuto nella raccolta",
        'ja': 'この接続には訪問できる公開アドレスがありません — アカウントのハンドルで接続し直すか、内容を収集に貼り付けてください',
        'zh': '此连接没有可访问的公开地址 — 请用账户的用户名重新连接，或将内容粘贴到采集中',
        'hi': 'इस कनेक्शन के पास जाने योग्य कोई सार्वजनिक पता नहीं है — खाते के हैंडल से फिर से जोड़ें, या सामग्री को संग्रह में चिपकाएँ',
        'ar': 'لا يملك هذا الاتصال عنوانًا علنيًا لزيارته — أعد الربط بمعرّف الحساب، أو الصق المحتوى في الجمع',
    },
    'say what you were trying to do and what stood in the way': {
        'es': 'di qué intentabas hacer y qué se interpuso',
        'fr': "dites ce que vous essayiez de faire et ce qui s'y est opposé",
        'de': 'sag, was du versucht hast und was im Weg stand',
        'pt': 'diga o que você estava tentando fazer e o que ficou no caminho',
        'it': 'di\' cosa stavi cercando di fare e cosa ti ha ostacolato',
        'ja': '何をしようとして、何が妨げになったかを書いてください',
        'zh': '请写出你想做什么，以及是什么挡住了你',
        'hi': 'बताइए कि आप क्या करने की कोशिश कर रहे थे और क्या आड़े आया',
        'ar': 'اذكر ما كنت تحاول فعله وما الذي وقف في طريقك',
    },
    'no referral was issued': {
        'es': 'no se emitió ninguna derivación',
        'fr': "aucune orientation n'a été émise",
        'de': 'es wurde keine Weiterleitung ausgestellt',
        'pt': 'não foi emitido qualquer encaminhamento',
        'it': 'non è stato emesso alcun rinvio',
        'ja': '引き継ぎは発行されていません',
        'zh': '没有签发任何转介',
        'hi': 'कोई रेफ़रल जारी नहीं किया गया',
        'ar': 'لم تُصدر أي إحالة',
    },
    'this homepage is not public': {
        'es': 'esta página personal no es pública',
        'fr': "cette page personnelle n'est pas publique",
        'de': 'diese Startseite ist nicht öffentlich',
        'pt': 'esta página pessoal não é pública',
        'it': 'questa pagina personale non è pubblica',
        'ja': 'このホームページは公開されていません',
        'zh': '此主页未公开', 'hi': 'यह होमपेज सार्वजनिक नहीं है',
        'ar': 'هذه الصفحة الشخصية ليست عامة'},
    'no such shop': {
        'es': 'no existe esa tienda', 'fr': "cette boutique n'existe pas",
        'de': 'kein solcher Laden', 'pt': 'essa loja não existe',
        'it': 'nessun negozio con questo nome', 'ja': 'そのショップは存在しません',
        'zh': '没有这家店铺', 'hi': 'ऐसी कोई दुकान नहीं है', 'ar': 'لا يوجد متجر بهذا الاسم'},
    'no such order': {
        'es': 'no existe ese pedido', 'fr': "cette commande n'existe pas",
        'de': 'keine solche Bestellung', 'pt': 'esse pedido não existe',
        'it': 'nessun ordine con questo numero', 'ja': 'その注文は存在しません',
        'zh': '没有这个订单', 'hi': 'ऐसा कोई ऑर्डर नहीं है', 'ar': 'لا يوجد طلب بهذا الرقم'},
    'party is seller or buyer': {
        'es': 'la parte es el vendedor o el comprador',
        'fr': "la partie est le vendeur ou l'acheteur",
        'de': 'die Partei ist Verkäufer oder Käufer',
        'pt': 'a parte é o vendedor ou o comprador',
        'it': "la parte è il venditore o l'acquirente",
        'ja': '当事者は販売者か購入者です', 'zh': '当事方是卖家或买家',
        'hi': 'पक्ष विक्रेता या खरीदार है', 'ar': 'الطرف هو البائع أو المشتري'},
    'this profile is restricted pending an objection review; it is not publishing new work while the objection is open': {
        'es': 'este perfil está restringido a la espera de la revisión de una objeción; no publica trabajo nuevo mientras la objeción esté abierta',
        'fr': "ce profil est restreint dans l'attente de l'examen d'une objection ; il ne publie pas de nouveau travail tant que l'objection est ouverte",
        'de': 'dieses Profil ist bis zur Einspruchsprüfung eingeschränkt; es veröffentlicht keine neuen Arbeiten, solange der Einspruch offen ist',
        'pt': 'este perfil está restrito enquanto aguarda a revisão de uma objeção; não publica trabalho novo enquanto a objeção estiver aberta',
        'it': "questo profilo è limitato in attesa della revisione di un'obiezione; non pubblica nuovi lavori finché l'obiezione resta aperta",
        'ja': 'このプロフィールは異議の審査を待って制限中です。異議が open のあいだ、新しい作品は公開しません',
        'zh': '此资料因异议待审而受限；在异议未结之前不会发布新作品',
        'hi': 'यह प्रोफ़ाइल आपत्ति समीक्षा तक प्रतिबंधित है; जब तक आपत्ति खुली है, यह नया कार्य प्रकाशित नहीं करती',
        'ar': 'هذا الملف مقيَّد بانتظار مراجعة اعتراض؛ ولا ينشر أعمالًا جديدة ما دام الاعتراض قائمًا',
    },
    # --- 0.40.2: the 142 recorded in tests/refusals_untranslated.txt -------
    #
    # Every one of these was a sentence the product said when it said no, in
    # English, to an owner who had chosen otherwise. 0.24.0 translated the
    # eleven any route can raise and wrote the rest down; the record is the
    # reason they could be finished rather than rediscovered.
    #
    #     asked     is the refusal translated
    #     mattered  is every refusal translated
    #
    # Field names, enum values and env vars stay as they are: `base_age`,
    # `robot_id`, `QRME_PDI_URL`, `approve`/`reject`. They are the API's own
    # names, identical in every language, and declining them into a sentence
    # is the half-in-one-language failure this table exists to refuse.
    '18+ only — present an interactor token whose verified birthdate shows 18 or older': {
        'es': 'solo mayores de 18 — presente un token de interactor cuya fecha de nacimiento verificada muestre 18 años o más',
        'fr': 'réservé aux 18 ans et plus — présentez un jeton d\'interacteur dont la date de naissance vérifiée indique 18 ans ou plus',
        'de': 'nur ab 18 — legen Sie ein Interaktor-Token vor, dessen geprüftes Geburtsdatum 18 Jahre oder älter ausweist',
        'pt': 'apenas maiores de 18 — apresente um token de interator cuja data de nascimento verificada mostre 18 anos ou mais',
        'it': 'solo 18+ — presenta un token di interattore la cui data di nascita verificata indichi 18 anni o più',
        'ja': '18歳以上限定 — 確認済みの生年月日が18歳以上であるインタラクター・トークンを提示してください',
        'zh': '仅限18岁以上 — 请出示已验证出生日期显示满18岁的互动者令牌',
        'hi': 'केवल 18+ — ऐसा इंटरैक्टर टोकन प्रस्तुत करें जिसकी सत्यापित जन्मतिथि 18 वर्ष या अधिक दर्शाती हो',
        'ar': 'للبالغين 18 عامًا فأكثر — قدِّم رمز متفاعل يُظهر تاريخ ميلاده المُوثَّق أنه 18 عامًا أو أكثر',
    },
    'a buyer acts with an interactor token': {
        'es': 'un comprador actúa con un token de interactor',
        'fr': 'un acheteur agit avec un jeton d\'interacteur',
        'de': 'eine Käuferin oder ein Käufer handelt mit einem Interaktor-Token',
        'pt': 'um comprador atua com um token de interator',
        'it': 'un acquirente agisce con un token di interattore',
        'ja': '購入者はインタラクター・トークンで操作します',
        'zh': '买家须使用互动者令牌进行操作',
        'hi': 'खरीदार इंटरैक्टर टोकन के साथ कार्य करता है',
        'ar': 'يتصرّف المشتري باستخدام رمز متفاعل',
    },
    'a ceremony needs the challenge to sign over': {
        'es': 'una ceremonia necesita el desafío que se va a firmar',
        'fr': 'une cérémonie a besoin du défi à signer',
        'de': 'eine Zeremonie benötigt die zu signierende Challenge',
        'pt': 'uma cerimónia precisa do desafio a assinar',
        'it': 'una cerimonia richiede la sfida da firmare',
        'ja': '署名の儀式には対象となるチャレンジが必要です',
        'zh': '签名仪式需要待签署的质询串',
        'hi': 'समारोह को हस्ताक्षर हेतु चैलेंज चाहिए',
        'ar': 'تحتاج المراسم إلى التحدّي المراد التوقيع عليه',
    },
    'a connection is between two people, so this needs the token of one of them rather than a profile\'s owner token': {
        'es': 'una conexión es entre dos personas, así que esto necesita el token de una de ellas y no el token de propietario de un perfil',
        'fr': 'une connexion se fait entre deux personnes : il faut donc le jeton de l\'une d\'elles, et non le jeton propriétaire d\'un profil',
        'de': 'eine Verbindung besteht zwischen zwei Personen; dafür wird das Token einer von ihnen benötigt, nicht das Eigentümer-Token eines Profils',
        'pt': 'uma ligação é entre duas pessoas, por isso é necessário o token de uma delas e não o token de proprietário de um perfil',
        'it': 'una connessione è tra due persone, quindi serve il token di una di loro e non il token del titolare di un profilo',
        'ja': 'つながりは二人の人間のあいだのものです。プロフィールの所有者トークンではなく、どちらかご本人のトークンが必要です',
        'zh': '连接存在于两个人之间，因此需要其中一方的令牌，而非某个资料的所有者令牌',
        'hi': 'संबंध दो व्यक्तियों के बीच होता है, इसलिए किसी प्रोफ़ाइल के स्वामी टोकन के बजाय उनमें से एक का टोकन चाहिए',
        'ar': 'الاتصال يكون بين شخصين، لذا يلزم رمز أحدهما لا رمز مالك الملف',
    },
    'a handoff requires the user\'s explicit consent': {
        'es': 'un traspaso requiere el consentimiento explícito del usuario',
        'fr': 'un transfert requiert le consentement explicite de l\'utilisateur',
        'de': 'eine Übergabe erfordert die ausdrückliche Einwilligung der Nutzerin oder des Nutzers',
        'pt': 'uma transferência requer o consentimento explícito do utilizador',
        'it': 'un passaggio di consegne richiede il consenso esplicito dell\'utente',
        'ja': '引き継ぎにはご本人の明示的な同意が必要です',
        'zh': '移交需要用户的明确同意',
        'hi': 'हस्तांतरण के लिए उपयोगकर्ता की स्पष्ट सहमति आवश्यक है',
        'ar': 'تتطلّب الإحالة موافقة صريحة من المستخدم',
    },
    'a licence that permits deriving an agent requires a verified-18+ buyer — the same bar deriving one does, applied before the fee rather than after': {
        'es': 'una licencia que permite derivar un agente requiere un comprador verificado de 18+ — el mismo listón que derivar uno, aplicado antes de la tarifa en lugar de después',
        'fr': 'une licence autorisant à dériver un agent exige un acheteur vérifié de 18 ans ou plus — la même exigence que pour en dériver un, appliquée avant les frais plutôt qu\'après',
        'de': 'eine Lizenz, die das Ableiten eines Agenten erlaubt, erfordert eine geprüft volljährige Käuferin oder einen geprüft volljährigen Käufer — dieselbe Schwelle wie beim Ableiten, nur vor der Gebühr statt danach',
        'pt': 'uma licença que permite derivar um agente exige um comprador verificado com 18+ — a mesma exigência de derivar um, aplicada antes da taxa e não depois',
        'it': 'una licenza che consente di derivare un agente richiede un acquirente verificato 18+ — lo stesso requisito della derivazione, applicato prima del pagamento anziché dopo',
        'ja': 'エージェントの派生を許すライセンスには、18歳以上と確認された購入者が必要です — 派生そのものと同じ基準を、料金の後ではなく前に適用します',
        'zh': '允许派生代理的许可需要经过验证的18岁以上买家 — 与派生本身相同的门槛，只是在收费之前而非之后适用',
        'hi': 'एजेंट व्युत्पन्न करने की अनुमति देने वाले लाइसेंस हेतु सत्यापित 18+ खरीदार आवश्यक है — वही मानक जो व्युत्पन्न करने पर लागू होता है, शुल्क के बाद नहीं बल्कि पहले',
        'ar': 'الترخيص الذي يسمح باشتقاق وكيل يتطلّب مشتريًا مُوثَّقًا بعمر 18 عامًا فأكثر — وهو المعيار نفسه المطلوب للاشتقاق، لكن قبل الرسوم لا بعدها',
    },
    'a message is required': {
        'es': 'se requiere un mensaje',
        'fr': 'un message est requis',
        'de': 'eine Nachricht ist erforderlich',
        'pt': 'é necessária uma mensagem',
        'it': 'è richiesto un messaggio',
        'ja': 'メッセージが必要です',
        'zh': '需要填写消息内容',
        'hi': 'संदेश आवश्यक है',
        'ar': 'الرسالة مطلوبة',
    },
    'a pack needs at least one knowledge item': {
        'es': 'un paquete necesita al menos un elemento de conocimiento',
        'fr': 'un pack a besoin d\'au moins un élément de connaissance',
        'de': 'ein Paket benötigt mindestens einen Wissensbaustein',
        'pt': 'um pacote precisa de pelo menos um item de conhecimento',
        'it': 'un pacchetto richiede almeno un elemento di conoscenza',
        'ja': 'パックには知識項目が少なくとも一つ必要です',
        'zh': '知识包至少需要一个知识条目',
        'hi': 'पैक में कम से कम एक ज्ञान आइटम होना चाहिए',
        'ar': 'تحتاج الحزمة إلى عنصر معرفي واحد على الأقل',
    },
    'a rated profile is placed one-to-one. A shared room behind an adult code in a public place is a different product with different moderation questions, not a flag on this one': {
        'es': 'un perfil con clasificación se coloca uno a uno. Una sala compartida tras un código para adultos en un lugar público es otro producto con otras preguntas de moderación, no una casilla en este',
        'fr': 'un profil classé est placé en tête-à-tête. Une salle partagée derrière un code adulte dans un lieu public est un autre produit, avec d\'autres questions de modération — pas une option de celui-ci',
        'de': 'ein eingestuftes Profil wird eins zu eins platziert. Ein geteilter Raum hinter einem Erwachsenen-Code an einem öffentlichen Ort ist ein anderes Produkt mit anderen Moderationsfragen, kein Schalter an diesem',
        'pt': 'um perfil classificado é colocado um para um. Uma sala partilhada atrás de um código para adultos num local público é outro produto, com outras questões de moderação, e não uma opção deste',
        'it': 'un profilo classificato viene collocato uno a uno. Una stanza condivisa dietro un codice per adulti in un luogo pubblico è un altro prodotto, con altre domande di moderazione, non un\'opzione di questo',
        'ja': 'レーティング付きプロフィールは一対一で配置します。公共の場でアダルトコードの先にある共有ルームは、別のモデレーション課題をもつ別の製品であり、本製品の設定項目ではありません',
        'zh': '分级资料按一对一方式投放。公共场所中以成人验证码进入的共享房间属于另一种产品，有另一套审核问题，而不是本产品的一个开关',
        'hi': 'रेटेड प्रोफ़ाइल एक-से-एक रखी जाती है। सार्वजनिक स्थान पर वयस्क कोड के पीछे साझा कक्ष एक अलग उत्पाद है जिसके मॉडरेशन प्रश्न अलग हैं, इस उत्पाद का विकल्प नहीं',
        'ar': 'يوضع الملف المصنَّف واحدًا لواحد. الغرفة المشتركة خلف رمز للبالغين في مكان عام منتَج آخر بأسئلة إشراف مختلفة، وليست خيارًا في هذا المنتج',
    },
    'a room turn is spoken by a person, so this needs the token of a user participant rather than a profile\'s owner token': {
        'es': 'un turno en una sala lo habla una persona, así que esto necesita el token de un participante y no el token de propietario de un perfil',
        'fr': 'un tour de parole dans une salle est pris par une personne : il faut donc le jeton d\'un participant, et non le jeton propriétaire d\'un profil',
        'de': 'ein Redebeitrag in einem Raum kommt von einer Person; dafür wird das Token einer teilnehmenden Person benötigt, nicht das Eigentümer-Token eines Profils',
        'pt': 'um turno numa sala é falado por uma pessoa, por isso é necessário o token de um participante e não o token de proprietário de um perfil',
        'it': 'un turno in una stanza è parlato da una persona, quindi serve il token di un partecipante e non il token del titolare di un profilo',
        'ja': 'ルームでの発言は人が行うものです。プロフィールの所有者トークンではなく、参加者ご本人のトークンが必要です',
        'zh': '房间中的发言由真人做出，因此需要参与者本人的令牌，而非某个资料的所有者令牌',
        'hi': 'कक्ष में बात एक व्यक्ति करता है, इसलिए किसी प्रोफ़ाइल के स्वामी टोकन के बजाय किसी प्रतिभागी का टोकन चाहिए',
        'ar': 'الحديث في الغرفة يصدر عن شخص، لذا يلزم رمز أحد المشاركين لا رمز مالك الملف',
    },
    'acceptance of the Terms of Service is required to create a profile (GET /terms)': {
        'es': 'es necesario aceptar los Términos del Servicio para crear un perfil (GET /terms)',
        'fr': 'l\'acceptation des conditions d\'utilisation est requise pour créer un profil (GET /terms)',
        'de': 'für das Anlegen eines Profils ist die Zustimmung zu den Nutzungsbedingungen erforderlich (GET /terms)',
        'pt': 'é necessária a aceitação dos Termos de Serviço para criar um perfil (GET /terms)',
        'it': 'per creare un profilo è necessario accettare i Termini di servizio (GET /terms)',
        'ja': 'プロフィールの作成には利用規約への同意が必要です (GET /terms)',
        'zh': '创建资料需先接受服务条款 (GET /terms)',
        'hi': 'प्रोफ़ाइल बनाने के लिए सेवा शर्तों की स्वीकृति आवश्यक है (GET /terms)',
        'ar': 'إنشاء ملف يتطلّب قبول شروط الخدمة (GET /terms)',
    },
    'acquiring a license on a rated profile requires a verified-18+ buyer': {
        'es': 'adquirir una licencia sobre un perfil con clasificación requiere un comprador verificado de 18+',
        'fr': 'acquérir une licence sur un profil classé exige un acheteur vérifié de 18 ans ou plus',
        'de': 'der Erwerb einer Lizenz an einem eingestuften Profil erfordert eine geprüft volljährige Käuferin oder einen geprüft volljährigen Käufer',
        'pt': 'adquirir uma licença sobre um perfil classificado exige um comprador verificado com 18+',
        'it': 'acquisire una licenza su un profilo classificato richiede un acquirente verificato 18+',
        'ja': 'レーティング付きプロフィールのライセンス取得には、18歳以上と確認された購入者が必要です',
        'zh': '获取分级资料的许可需要经过验证的18岁以上买家',
        'hi': 'रेटेड प्रोफ़ाइल पर लाइसेंस लेने हेतु सत्यापित 18+ खरीदार आवश्यक है',
        'ar': 'الحصول على ترخيص لملف مصنَّف يتطلّب مشتريًا مُوثَّقًا بعمر 18 عامًا فأكثر',
    },
    'adult mode is never available for a profile of another real person': {
        'es': 'el modo adulto nunca está disponible para el perfil de otra persona real',
        'fr': 'le mode adulte n\'est jamais disponible pour le profil d\'une autre personne réelle',
        'de': 'der Erwachsenenmodus steht für das Profil einer anderen realen Person nie zur Verfügung',
        'pt': 'o modo adulto nunca está disponível para o perfil de outra pessoa real',
        'it': 'la modalità per adulti non è mai disponibile per il profilo di un\'altra persona reale',
        'ja': 'アダルトモードは、実在する他人のプロフィールでは決して利用できません',
        'zh': '成人模式绝不适用于他人的真实人物资料',
        'hi': 'किसी अन्य वास्तविक व्यक्ति की प्रोफ़ाइल के लिए वयस्क मोड कभी उपलब्ध नहीं है',
        'ar': 'وضع البالغين غير متاح إطلاقًا لملف شخص حقيقي آخر',
    },
    'adult mode requires a verified adult owner': {
        'es': 'el modo adulto requiere un propietario adulto verificado',
        'fr': 'le mode adulte exige un propriétaire adulte vérifié',
        'de': 'der Erwachsenenmodus erfordert eine geprüft volljährige Inhaberin oder einen geprüft volljährigen Inhaber',
        'pt': 'o modo adulto exige um proprietário adulto verificado',
        'it': 'la modalità per adulti richiede un titolare adulto verificato',
        'ja': 'アダルトモードには、成人であると確認された所有者が必要です',
        'zh': '成人模式需要经过验证的成年所有者',
        'hi': 'वयस्क मोड के लिए सत्यापित वयस्क स्वामी आवश्यक है',
        'ar': 'يتطلّب وضع البالغين مالكًا بالغًا مُوثَّقًا',
    },
    'an agent has already been derived here': {
        'es': 'ya se ha derivado un agente aquí',
        'fr': 'un agent a déjà été dérivé ici',
        'de': 'hier wurde bereits ein Agent abgeleitet',
        'pt': 'já foi derivado um agente aqui',
        'it': 'qui è già stato derivato un agente',
        'ja': 'ここでは既にエージェントが派生済みです',
        'zh': '此处已派生过一个代理',
        'hi': 'यहाँ पहले ही एक एजेंट व्युत्पन्न किया जा चुका है',
        'ar': 'سبق أن اشتُقّ وكيل هنا',
    },
    'an owner token is required': {
        'es': 'se requiere un token de propietario',
        'fr': 'un jeton propriétaire est requis',
        'de': 'ein Eigentümer-Token ist erforderlich',
        'pt': 'é necessário um token de proprietário',
        'it': 'è richiesto un token del titolare',
        'ja': '所有者トークンが必要です',
        'zh': '需要所有者令牌',
        'hi': 'स्वामी टोकन आवश्यक है',
        'ar': 'رمز المالك مطلوب',
    },
    'app connector not found': {
        'es': 'conector de aplicación no encontrado',
        'fr': 'connecteur d\'application introuvable',
        'de': 'App-Connector nicht gefunden',
        'pt': 'conector de aplicação não encontrado',
        'it': 'connettore dell\'app non trovato',
        'ja': 'アプリコネクタが見つかりません',
        'zh': '未找到应用连接器',
        'hi': 'ऐप कनेक्टर नहीं मिला',
        'ar': 'لم يُعثر على موصّل التطبيق',
    },
    'approval actions: approve, reject': {
        'es': 'acciones de aprobación: approve, reject',
        'fr': 'actions d\'approbation : approve, reject',
        'de': 'Freigabeaktionen: approve, reject',
        'pt': 'ações de aprovação: approve, reject',
        'it': 'azioni di approvazione: approve, reject',
        'ja': '承認の操作: approve, reject',
        'zh': '审批操作：approve、reject',
        'hi': 'अनुमोदन क्रियाएँ: approve, reject',
        'ar': 'إجراءات الموافقة: approve, reject',
    },
    'assist needs input — what the paused phase asked for': {
        'es': 'la asistencia necesita una entrada — lo que pidió la fase en pausa',
        'fr': 'l\'assistance a besoin d\'une saisie — ce que la phase en pause a demandé',
        'de': 'die Unterstützung benötigt eine Eingabe — das, wonach die pausierte Phase gefragt hat',
        'pt': 'a assistência precisa de uma entrada — aquilo que a fase em pausa pediu',
        'it': 'l\'assistenza richiede un input — ciò che la fase in pausa ha chiesto',
        'ja': 'アシストには入力が必要です — 一時停止中のフェーズが求めた内容です',
        'zh': '协助需要输入 — 即暂停阶段所请求的内容',
        'hi': 'सहायता को इनपुट चाहिए — वही जो रुके हुए चरण ने माँगा था',
        'ar': 'تحتاج المساعدة إلى مُدخل — وهو ما طلبته المرحلة المتوقفة',
    },
    'authentication required — this is for the people who are here': {
        'es': 'se requiere autenticación — esto es para las personas que están aquí',
        'fr': 'authentification requise — ceci est réservé aux personnes présentes',
        'de': 'Authentifizierung erforderlich — das hier ist für die Anwesenden',
        'pt': 'autenticação necessária — isto é para as pessoas que estão aqui',
        'it': 'autenticazione richiesta — questo è per le persone che sono qui',
        'ja': '認証が必要です — これはここにいる方のためのものです',
        'zh': '需要身份验证 — 此处面向在场的人',
        'hi': 'प्रमाणीकरण आवश्यक है — यह यहाँ मौजूद लोगों के लिए है',
        'ar': 'المصادقة مطلوبة — هذا مخصّص لمن هم هنا',
    },
    'authentication required — this room\'s disclosure is for the people in it': {
        'es': 'se requiere autenticación — la divulgación de esta sala es para quienes están en ella',
        'fr': 'authentification requise — la divulgation de cette salle est réservée à ceux qui s\'y trouvent',
        'de': 'Authentifizierung erforderlich — die Offenlegung dieses Raums ist für die Personen darin bestimmt',
        'pt': 'autenticação necessária — a divulgação desta sala é para quem está nela',
        'it': 'autenticazione richiesta — la divulgazione di questa stanza è per chi vi si trova',
        'ja': '認証が必要です — このルームの開示は、その場にいる方のためのものです',
        'zh': '需要身份验证 — 此房间的披露信息面向房间内的人',
        'hi': 'प्रमाणीकरण आवश्यक है — इस कक्ष का प्रकटीकरण उसमें मौजूद लोगों के लिए है',
        'ar': 'المصادقة مطلوبة — إفصاح هذه الغرفة مخصّص لمن فيها',
    },
    'base_age cannot be negative': {
        'es': 'base_age no puede ser negativo',
        'fr': 'base_age ne peut pas être négatif',
        'de': 'base_age darf nicht negativ sein',
        'pt': 'base_age não pode ser negativo',
        'it': 'base_age non può essere negativo',
        'ja': 'base_age を負の値にはできません',
        'zh': 'base_age 不能为负数',
        'hi': 'base_age ऋणात्मक नहीं हो सकता',
        'ar': 'لا يمكن أن تكون قيمة base_age سالبة',
    },
    'beacon not found': {
        'es': 'baliza no encontrada',
        'fr': 'balise introuvable',
        'de': 'Beacon nicht gefunden',
        'pt': 'baliza não encontrada',
        'it': 'beacon non trovato',
        'ja': 'ビーコンが見つかりません',
        'zh': '未找到信标',
        'hi': 'बीकन नहीं मिला',
        'ar': 'لم يُعثر على المنارة',
    },
    'beacons are for publish connections': {
        'es': 'las balizas son para conexiones de publicación',
        'fr': 'les balises servent aux connexions de publication',
        'de': 'Beacons sind für Veröffentlichungsverbindungen',
        'pt': 'as balizas são para ligações de publicação',
        'it': 'i beacon sono per le connessioni di pubblicazione',
        'ja': 'ビーコンは公開用の接続に使うものです',
        'zh': '信标用于发布类连接',
        'hi': 'बीकन प्रकाशन कनेक्शनों के लिए हैं',
        'ar': 'المنارات مخصّصة لاتصالات النشر',
    },
    'campaign not found': {
        'es': 'campaña no encontrada',
        'fr': 'campagne introuvable',
        'de': 'Kampagne nicht gefunden',
        'pt': 'campanha não encontrada',
        'it': 'campagna non trovata',
        'ja': 'キャンペーンが見つかりません',
        'zh': '未找到活动',
        'hi': 'अभियान नहीं मिला',
        'ar': 'لم يُعثر على الحملة',
    },
    'coming up on stream needs an account — the host is deciding about a person, not an anonymous request': {
        'es': 'aparecer en la emisión requiere una cuenta — el anfitrión está decidiendo sobre una persona, no sobre una petición anónima',
        'fr': 'passer à l\'antenne nécessite un compte — l\'hôte se prononce sur une personne, pas sur une requête anonyme',
        'de': 'in der Übertragung aufzutreten erfordert ein Konto — die gastgebende Person entscheidet über einen Menschen, nicht über eine anonyme Anfrage',
        'pt': 'aparecer na transmissão exige uma conta — o anfitrião está a decidir sobre uma pessoa e não sobre um pedido anónimo',
        'it': 'comparire in diretta richiede un account — chi ospita sta decidendo su una persona, non su una richiesta anonima',
        'ja': '配信に登場するにはアカウントが必要です — ホストは匿名のリクエストではなく、一人の人について判断します',
        'zh': '上镜需要账户 — 主持人是在对一个人做决定，而不是对一个匿名请求',
        'hi': 'स्ट्रीम पर आने के लिए खाता आवश्यक है — मेज़बान किसी गुमनाम अनुरोध पर नहीं, बल्कि एक व्यक्ति पर निर्णय ले रहा है',
        'ar': 'الظهور في البث يتطلّب حسابًا — فالمضيف يقرّر بشأن شخص، لا بشأن طلب مجهول',
    },
    'connection has been revoked': {
        'es': 'la conexión ha sido revocada',
        'fr': 'la connexion a été révoquée',
        'de': 'die Verbindung wurde widerrufen',
        'pt': 'a ligação foi revogada',
        'it': 'la connessione è stata revocata',
        'ja': 'この接続は取り消されました',
        'zh': '该连接已被撤销',
        'hi': 'कनेक्शन रद्द कर दिया गया है',
        'ar': 'تم إلغاء الاتصال',
    },
    'connection not found': {
        'es': 'conexión no encontrada',
        'fr': 'connexion introuvable',
        'de': 'Verbindung nicht gefunden',
        'pt': 'ligação não encontrada',
        'it': 'connessione non trovata',
        'ja': '接続が見つかりません',
        'zh': '未找到连接',
        'hi': 'कनेक्शन नहीं मिला',
        'ar': 'لم يُعثر على الاتصال',
    },
    'connector has been revoked': {
        'es': 'el conector ha sido revocado',
        'fr': 'le connecteur a été révoqué',
        'de': 'der Connector wurde widerrufen',
        'pt': 'o conector foi revogado',
        'it': 'il connettore è stato revocato',
        'ja': 'このコネクタは取り消されました',
        'zh': '该连接器已被撤销',
        'hi': 'कनेक्टर रद्द कर दिया गया है',
        'ar': 'تم إلغاء الموصّل',
    },
    'deriving an agent requires a verified-adult buyer': {
        'es': 'derivar un agente requiere un comprador adulto verificado',
        'fr': 'dériver un agent exige un acheteur adulte vérifié',
        'de': 'das Ableiten eines Agenten erfordert eine geprüft volljährige Käuferin oder einen geprüft volljährigen Käufer',
        'pt': 'derivar um agente exige um comprador adulto verificado',
        'it': 'derivare un agente richiede un acquirente adulto verificato',
        'ja': 'エージェントの派生には、成人であると確認された購入者が必要です',
        'zh': '派生代理需要经过验证的成年买家',
        'hi': 'एजेंट व्युत्पन्न करने हेतु सत्यापित वयस्क खरीदार आवश्यक है',
        'ar': 'اشتقاق وكيل يتطلّب مشتريًا بالغًا مُوثَّقًا',
    },
    'every item in a robot pack needs a task (the command verb)': {
        'es': 'cada elemento de un paquete de robot necesita una tarea (el verbo del comando)',
        'fr': 'chaque élément d\'un pack robot a besoin d\'une tâche (le verbe de la commande)',
        'de': 'jeder Baustein eines Roboterpakets benötigt eine Aufgabe (das Befehlsverb)',
        'pt': 'cada item de um pacote de robô precisa de uma tarefa (o verbo do comando)',
        'it': 'ogni elemento di un pacchetto per robot richiede un compito (il verbo del comando)',
        'ja': 'ロボットパックの各項目にはタスク（コマンドの動詞）が必要です',
        'zh': '机器人包中的每个条目都需要一个任务（命令动词）',
        'hi': 'रोबोट पैक के प्रत्येक आइटम को एक कार्य चाहिए (कमांड क्रिया)',
        'ar': 'كل عنصر في حزمة الروبوت يحتاج إلى مهمة (فعل الأمر)',
    },
    'excursion not found': {
        'es': 'excursión no encontrada',
        'fr': 'excursion introuvable',
        'de': 'Exkursion nicht gefunden',
        'pt': 'excursão não encontrada',
        'it': 'escursione non trovata',
        'ja': 'エクスカーションが見つかりません',
        'zh': '未找到外出探索',
        'hi': 'भ्रमण नहीं मिला',
        'ar': 'لم يُعثر على الرحلة',
    },
    'game session not found': {
        'es': 'sesión de juego no encontrada',
        'fr': 'session de jeu introuvable',
        'de': 'Spielsitzung nicht gefunden',
        'pt': 'sessão de jogo não encontrada',
        'it': 'sessione di gioco non trovata',
        'ja': 'ゲームセッションが見つかりません',
        'zh': '未找到游戏会话',
        'hi': 'गेम सत्र नहीं मिला',
        'ar': 'لم يُعثر على جلسة اللعب',
    },
    'gifting is 18+': {
        'es': 'los regalos son solo para mayores de 18',
        'fr': 'les cadeaux sont réservés aux 18 ans et plus',
        'de': 'Schenken ist ab 18',
        'pt': 'as ofertas são apenas para maiores de 18',
        'it': 'i regali sono solo 18+',
        'ja': 'ギフトは18歳以上限定です',
        'zh': '赠礼仅限18岁以上',
        'hi': 'उपहार देना केवल 18+ के लिए है',
        'ar': 'الإهداء للبالغين 18 عامًا فأكثر',
    },
    'gifting requires a verified birthdate on your account — an unverified age is not evidence of an adult': {
        'es': 'regalar requiere una fecha de nacimiento verificada en su cuenta — una edad sin verificar no es prueba de ser adulto',
        'fr': 'offrir un cadeau exige une date de naissance vérifiée sur votre compte — un âge non vérifié ne prouve pas la majorité',
        'de': 'Schenken erfordert ein geprüftes Geburtsdatum in Ihrem Konto — ein ungeprüftes Alter ist kein Nachweis der Volljährigkeit',
        'pt': 'oferecer exige uma data de nascimento verificada na sua conta — uma idade não verificada não é prova de que é adulto',
        'it': 'fare un regalo richiede una data di nascita verificata sul tuo account — un\'età non verificata non è prova di maggiore età',
        'ja': 'ギフトにはアカウント上で確認済みの生年月日が必要です — 未確認の年齢は成人であることの証明になりません',
        'zh': '赠礼需要您账户中已验证的出生日期 — 未经验证的年龄不能证明您已成年',
        'hi': 'उपहार देने हेतु आपके खाते में सत्यापित जन्मतिथि आवश्यक है — असत्यापित आयु वयस्क होने का प्रमाण नहीं है',
        'ar': 'يتطلّب الإهداء تاريخ ميلاد مُوثَّقًا في حسابك — والعمر غير المُوثَّق ليس دليلًا على البلوغ',
    },
    'gifts come from a person, so this needs an interactor token': {
        'es': 'los regalos vienen de una persona, así que esto necesita un token de interactor',
        'fr': 'un cadeau vient d\'une personne : il faut donc un jeton d\'interacteur',
        'de': 'Geschenke kommen von einer Person; dafür wird ein Interaktor-Token benötigt',
        'pt': 'as ofertas vêm de uma pessoa, por isso é necessário um token de interator',
        'it': 'i regali vengono da una persona, quindi serve un token di interattore',
        'ja': 'ギフトは人から贈られるものなので、インタラクター・トークンが必要です',
        'zh': '赠礼来自某个人，因此需要互动者令牌',
        'hi': 'उपहार किसी व्यक्ति से आते हैं, इसलिए इंटरैक्टर टोकन चाहिए',
        'ar': 'الهدايا تأتي من شخص، لذا يلزم رمز متفاعل',
    },
    'grant not found': {
        'es': 'concesión no encontrada',
        'fr': 'autorisation introuvable',
        'de': 'Freigabe nicht gefunden',
        'pt': 'concessão não encontrada',
        'it': 'concessione non trovata',
        'ja': '許可が見つかりません',
        'zh': '未找到授权',
        'hi': 'अनुदान नहीं मिला',
        'ar': 'لم يُعثر على التفويض',
    },
    'grant revoked or unknown': {
        'es': 'concesión revocada o desconocida',
        'fr': 'autorisation révoquée ou inconnue',
        'de': 'Freigabe widerrufen oder unbekannt',
        'pt': 'concessão revogada ou desconhecida',
        'it': 'concessione revocata o sconosciuta',
        'ja': '許可が取り消されたか、不明です',
        'zh': '授权已撤销或未知',
        'hi': 'अनुदान रद्द या अज्ञात',
        'ar': 'التفويض مُلغى أو غير معروف',
    },
    'handoff not found': {
        'es': 'traspaso no encontrado',
        'fr': 'transfert introuvable',
        'de': 'Übergabe nicht gefunden',
        'pt': 'transferência não encontrada',
        'it': 'passaggio di consegne non trovato',
        'ja': '引き継ぎが見つかりません',
        'zh': '未找到移交记录',
        'hi': 'हस्तांतरण नहीं मिला',
        'ar': 'لم يُعثر على الإحالة',
    },
    'hybrid profiles are created via POST /profiles/composite, from at least two source profiles': {
        'es': 'los perfiles híbridos se crean con POST /profiles/composite, a partir de al menos dos perfiles de origen',
        'fr': 'les profils hybrides se créent via POST /profiles/composite, à partir d\'au moins deux profils sources',
        'de': 'Hybridprofile werden über POST /profiles/composite aus mindestens zwei Quellprofilen erstellt',
        'pt': 'os perfis híbridos são criados via POST /profiles/composite, a partir de pelo menos dois perfis de origem',
        'it': 'i profili ibridi si creano tramite POST /profiles/composite, da almeno due profili di origine',
        'ja': 'ハイブリッドのプロフィールは、二つ以上の元プロフィールから POST /profiles/composite で作成します',
        'zh': '混合资料通过 POST /profiles/composite 创建，需至少两个来源资料',
        'hi': 'हाइब्रिड प्रोफ़ाइलें कम से कम दो स्रोत प्रोफ़ाइलों से POST /profiles/composite द्वारा बनाई जाती हैं',
        'ar': 'تُنشأ الملفات الهجينة عبر POST /profiles/composite من ملفَّين مصدرَين على الأقل',
    },
    'kind must be consult, finetune, or clone': {
        'es': 'kind debe ser consult, finetune o clone',
        'fr': 'kind doit être consult, finetune ou clone',
        'de': 'kind muss consult, finetune oder clone sein',
        'pt': 'kind deve ser consult, finetune ou clone',
        'it': 'kind deve essere consult, finetune o clone',
        'ja': 'kind は consult、finetune、clone のいずれかである必要があります',
        'zh': 'kind 必须为 consult、finetune 或 clone',
        'hi': 'kind का मान consult, finetune या clone होना चाहिए',
        'ar': 'يجب أن تكون قيمة kind إحدى: consult أو finetune أو clone',
    },
    'license not found': {
        'es': 'licencia no encontrada',
        'fr': 'licence introuvable',
        'de': 'Lizenz nicht gefunden',
        'pt': 'licença não encontrada',
        'it': 'licenza non trovata',
        'ja': 'ライセンスが見つかりません',
        'zh': '未找到许可',
        'hi': 'लाइसेंस नहीं मिला',
        'ar': 'لم يُعثر على الترخيص',
    },
    'listing not found': {
        'es': 'anuncio no encontrado',
        'fr': 'annonce introuvable',
        'de': 'Angebot nicht gefunden',
        'pt': 'anúncio não encontrado',
        'it': 'annuncio non trovato',
        'ja': '出品が見つかりません',
        'zh': '未找到该刊登',
        'hi': 'लिस्टिंग नहीं मिली',
        'ar': 'لم يُعثر على الإعلان',
    },
    'message not found': {
        'es': 'mensaje no encontrado',
        'fr': 'message introuvable',
        'de': 'Nachricht nicht gefunden',
        'pt': 'mensagem não encontrada',
        'it': 'messaggio non trovato',
        'ja': 'メッセージが見つかりません',
        'zh': '未找到消息',
        'hi': 'संदेश नहीं मिला',
        'ar': 'لم يُعثر على الرسالة',
    },
    'mode must be \'sign\' or \'enroll\'': {
        'es': 'mode debe ser \'sign\' o \'enroll\'',
        'fr': 'mode doit être \'sign\' ou \'enroll\'',
        'de': 'mode muss \'sign\' oder \'enroll\' sein',
        'pt': 'mode deve ser \'sign\' ou \'enroll\'',
        'it': 'mode deve essere \'sign\' o \'enroll\'',
        'ja': 'mode は \'sign\' か \'enroll\' である必要があります',
        'zh': 'mode 必须为 \'sign\' 或 \'enroll\'',
        'hi': 'mode का मान \'sign\' या \'enroll\' होना चाहिए',
        'ar': 'يجب أن تكون قيمة mode إما \'sign\' أو \'enroll\'',
    },
    'no PDI vault configured (set QRME_PDI_URL / QRME_PDI_TOKEN)': {
        'es': 'no hay bóveda PDI configurada (defina QRME_PDI_URL / QRME_PDI_TOKEN)',
        'fr': 'aucun coffre PDI configuré (définissez QRME_PDI_URL / QRME_PDI_TOKEN)',
        'de': 'kein PDI-Tresor konfiguriert (QRME_PDI_URL / QRME_PDI_TOKEN setzen)',
        'pt': 'não há cofre PDI configurado (defina QRME_PDI_URL / QRME_PDI_TOKEN)',
        'it': 'nessuna cassaforte PDI configurata (imposta QRME_PDI_URL / QRME_PDI_TOKEN)',
        'ja': 'PDI 保管庫が設定されていません（QRME_PDI_URL / QRME_PDI_TOKEN を設定してください）',
        'zh': '未配置 PDI 保险库（请设置 QRME_PDI_URL / QRME_PDI_TOKEN）',
        'hi': 'कोई PDI वॉल्ट कॉन्फ़िगर नहीं है (QRME_PDI_URL / QRME_PDI_TOKEN सेट करें)',
        'ar': 'لا توجد خزنة PDI مُهيّأة (اضبط QRME_PDI_URL / QRME_PDI_TOKEN)',
    },
    'no delegated workflow with that id': {
        'es': 'no hay ningún flujo de trabajo delegado con ese id',
        'fr': 'aucun flux de travail délégué avec cet identifiant',
        'de': 'kein delegierter Arbeitsablauf mit dieser Kennung',
        'pt': 'não há nenhum fluxo de trabalho delegado com esse id',
        'it': 'nessun flusso di lavoro delegato con quell\'id',
        'ja': 'その id の委任ワークフローはありません',
        'zh': '不存在具有该 id 的委托工作流',
        'hi': 'उस आईडी वाला कोई प्रत्यायोजित वर्कफ़्लो नहीं है',
        'ar': 'لا يوجد سير عمل مُفوَّض بهذا المعرّف',
    },
    'no embedding yet — interact first': {
        'es': 'todavía no hay incrustación — interactúe primero',
        'fr': 'pas encore d\'embedding — interagissez d\'abord',
        'de': 'noch kein Embedding — treten Sie zuerst in Kontakt',
        'pt': 'ainda não há embedding — interaja primeiro',
        'it': 'nessun embedding ancora — interagisci prima',
        'ja': '埋め込みはまだありません — まずやり取りしてください',
        'zh': '尚无嵌入向量 — 请先进行互动',
        'hi': 'अभी कोई एम्बेडिंग नहीं — पहले बातचीत करें',
        'ar': 'لا يوجد تضمين بعد — تفاعل أولًا',
    },
    'no engagement recorded': {
        'es': 'no hay interacción registrada',
        'fr': 'aucune interaction enregistrée',
        'de': 'kein Kontakt verzeichnet',
        'pt': 'não há interação registada',
        'it': 'nessuna interazione registrata',
        'ja': '記録されたやり取りがありません',
        'zh': '没有已记录的互动',
        'hi': 'कोई सहभागिता दर्ज नहीं है',
        'ar': 'لا يوجد تفاعل مسجَّل',
    },
    'no lesson covers that screen': {
        'es': 'ninguna lección cubre esa pantalla',
        'fr': 'aucune leçon ne couvre cet écran',
        'de': 'keine Lektion behandelt diesen Bildschirm',
        'pt': 'nenhuma lição cobre esse ecrã',
        'it': 'nessuna lezione copre quella schermata',
        'ja': 'その画面を扱うレッスンはありません',
        'zh': '没有课程涵盖该屏幕',
        'hi': 'उस स्क्रीन को कोई पाठ नहीं समेटता',
        'ar': 'لا يغطّي أي درس تلك الشاشة',
    },
    'no mail server is configured — save one first': {
        'es': 'no hay ningún servidor de correo configurado — guarde uno primero',
        'fr': 'aucun serveur de messagerie n\'est configuré — enregistrez-en un d\'abord',
        'de': 'es ist kein Mailserver konfiguriert — legen Sie zuerst einen an',
        'pt': 'não há nenhum servidor de e-mail configurado — guarde um primeiro',
        'it': 'nessun server di posta configurato — salvane prima uno',
        'ja': 'メールサーバーが設定されていません — まず登録してください',
        'zh': '未配置邮件服务器 — 请先保存一个',
        'hi': 'कोई मेल सर्वर कॉन्फ़िगर नहीं है — पहले एक सहेजें',
        'ar': 'لا يوجد خادم بريد مُهيّأ — احفظ واحدًا أولًا',
    },
    'no such agent': {
        'es': 'no existe ese agente',
        'fr': 'aucun agent de ce nom',
        'de': 'kein solcher Agent',
        'pt': 'não existe esse agente',
        'it': 'nessun agente di questo tipo',
        'ja': 'そのようなエージェントはありません',
        'zh': '没有该代理',
        'hi': 'ऐसा कोई एजेंट नहीं',
        'ar': 'لا يوجد وكيل بهذا الوصف',
    },
    'no such credential': {
        'es': 'no existe esa credencial',
        'fr': 'aucun identifiant de ce nom',
        'de': 'kein solcher Berechtigungsnachweis',
        'pt': 'não existe essa credencial',
        'it': 'nessuna credenziale di questo tipo',
        'ja': 'そのような資格情報はありません',
        'zh': '没有该凭据',
        'hi': 'ऐसा कोई क्रेडेंशियल नहीं',
        'ar': 'لا توجد بيانات اعتماد بهذا الوصف',
    },
    'no such session': {
        'es': 'no existe esa sesión',
        'fr': 'aucune session de ce nom',
        'de': 'keine solche Sitzung',
        'pt': 'não existe essa sessão',
        'it': 'nessuna sessione di questo tipo',
        'ja': 'そのようなセッションはありません',
        'zh': '没有该会话',
        'hi': 'ऐसा कोई सत्र नहीं',
        'ar': 'لا توجد جلسة بهذا الوصف',
    },
    'not a party to this session': {
        'es': 'no eres parte de esta sesión',
        'fr': 'vous n’êtes pas partie à cette session',
        'de': 'keine Partei dieser Sitzung',
        'pt': 'não é parte desta sessão',
        'it': 'non sei parte di questa sessione',
        'ja': 'このセッションの当事者ではありません',
        'zh': '不是该会话的当事方',
        'hi': 'आप इस सत्र के पक्षकार नहीं हैं',
        'ar': 'لست طرفًا في هذه الجلسة',
    },
    'only the desk offers a connection — the caller answers it': {
        'es': 'solo el escritorio ofrece una conexión: quien llama la responde',
        'fr': 'seul le bureau propose une connexion — l’appelant y répond',
        'de': 'nur der Desk bietet eine Verbindung an — der Anrufer antwortet darauf',
        'pt': 'só a banca oferece uma ligação — quem chama é que responde',
        'it': 'solo la postazione offre una connessione — chi chiama risponde',
        'ja': '接続を提案できるのはデスクだけです — 応答するのは呼び出した側です',
        'zh': '只有展台可以发出连接邀请——由来访者作答',
        'hi': 'कनेक्शन की पेशकश केवल डेस्क करता है — उत्तर कॉल करने वाला देता है',
        'ar': 'المكتب وحده يعرض الاتصال — والمتصل هو من يجيب عليه',
    },
    'only the caller answers an offer — it is their machine the connection opens': {
        'es': 'solo quien llama responde a una oferta: es su máquina la que abre la conexión',
        'fr': 'seul l’appelant répond à une offre — c’est sa machine que la connexion ouvre',
        'de': 'nur der Anrufer antwortet auf ein Angebot — es ist seine Maschine, die die Verbindung öffnet',
        'pt': 'só quem chama responde a uma oferta — é a máquina dessa pessoa que a ligação abre',
        'it': 'solo chi chiama risponde a un’offerta — è la sua macchina che la connessione apre',
        'ja': '提案に答えられるのは呼び出した側だけです — 接続が開くのはその人のマシンだからです',
        'zh': '只有来访者能回应邀请——因为连接打开的是他们的设备',
        'hi': 'पेशकश का उत्तर केवल कॉल करने वाला देता है — कनेक्शन उसी की मशीन खोलता है',
        'ar': 'المتصل وحده يجيب على العرض — فالاتصال يفتح جهازه هو',
    },
    'no such feed item': {
        'es': 'no existe ese elemento del feed',
        'fr': 'aucun élément de ce fil',
        'de': 'kein solches Element im Feed',
        'pt': 'não existe esse item do feed',
        'it': 'nessun elemento di questo tipo nel feed',
        'ja': 'そのフィード項目はありません',
        'zh': '没有该信息流条目',
        'hi': 'ऐसा कोई फ़ीड आइटम नहीं',
        'ar': 'لا يوجد عنصر بهذا الوصف في التدفق',
    },
    'no such desk': {
        'es': 'no existe ese escritorio',
        'fr': 'aucun bureau de ce nom',
        'de': 'kein solcher Desk',
        'pt': 'não existe essa banca',
        'it': 'nessuna postazione di questo tipo',
        'ja': 'そのようなデスクはありません',
        'zh': '没有该展台',
        'hi': 'ऐसा कोई डेस्क नहीं',
        'ar': 'لا يوجد مكتب بهذا الوصف',
    },
    'no such desk beacon': {
        'es': 'no existe esa baliza de escritorio',
        'fr': 'aucune balise de bureau de ce nom',
        'de': 'kein solcher Desk-Beacon',
        'pt': 'não existe essa baliza de banca',
        'it': 'nessun beacon di postazione di questo tipo',
        'ja': 'そのようなデスク・ビーコンはありません',
        'zh': '没有该展台信标',
        'hi': 'ऐसा कोई डेस्क बीकन नहीं',
        'ar': 'لا توجد منارة مكتب بهذا الوصف',
    },
    'no such listing': {
        'es': 'no existe ese anuncio',
        'fr': 'aucune annonce de ce nom',
        'de': 'kein solches Angebot',
        'pt': 'não existe esse anúncio',
        'it': 'nessun annuncio di questo tipo',
        'ja': 'そのような出品はありません',
        'zh': '没有该刊登',
        'hi': 'ऐसी कोई लिस्टिंग नहीं',
        'ar': 'لا يوجد إعلان بهذا الوصف',
    },
    'no such place': {
        'es': 'no existe ese lugar',
        'fr': 'aucun lieu de ce nom',
        'de': 'kein solcher Ort',
        'pt': 'não existe esse local',
        'it': 'nessun luogo di questo tipo',
        'ja': 'そのような場所はありません',
        'zh': '没有该地点',
        'hi': 'ऐसा कोई स्थान नहीं',
        'ar': 'لا يوجد مكان بهذا الوصف',
    },
    'no such profile': {
        'es': 'no existe ese perfil',
        'fr': 'aucun profil de ce nom',
        'de': 'kein solches Profil',
        'pt': 'não existe esse perfil',
        'it': 'nessun profilo di questo tipo',
        'ja': 'そのようなプロフィールはありません',
        'zh': '没有该资料',
        'hi': 'ऐसी कोई प्रोफ़ाइल नहीं',
        'ar': 'لا يوجد ملف بهذا الوصف',
    },
    'no such referral': {
        'es': 'no existe esa derivación',
        'fr': 'aucune orientation de ce nom',
        'de': 'keine solche Überweisung',
        'pt': 'não existe esse encaminhamento',
        'it': 'nessun invio di questo tipo',
        'ja': 'そのような紹介はありません',
        'zh': '没有该转介',
        'hi': 'ऐसा कोई रेफ़रल नहीं',
        'ar': 'لا توجد إحالة بهذا الوصف',
    },
    'no such ring': {
        'es': 'no existe ese timbre',
        'fr': 'aucune sonnerie de ce nom',
        'de': 'kein solches Klingeln',
        'pt': 'não existe esse toque',
        'it': 'nessuna chiamata di questo tipo',
        'ja': 'そのような呼び出しはありません',
        'zh': '没有该呼叫',
        'hi': 'ऐसी कोई घंटी नहीं',
        'ar': 'لا يوجد رنين بهذا الوصف',
    },
    'no such signature': {
        'es': 'no existe esa firma',
        'fr': 'aucune signature de ce nom',
        'de': 'keine solche Signatur',
        'pt': 'não existe essa assinatura',
        'it': 'nessuna firma di questo tipo',
        'ja': 'そのような署名はありません',
        'zh': '没有该签名',
        'hi': 'ऐसा कोई हस्ताक्षर नहीं',
        'ar': 'لا يوجد توقيع بهذا الوصف',
    },
    'no such watermark — this content was not credentialed by this QRME deployment': {
        'es': 'no existe esa marca de agua — este contenido no fue acreditado por esta instalación de QRME',
        'fr': 'aucun filigrane de ce nom — ce contenu n\'a pas été accrédité par ce déploiement QRME',
        'de': 'kein solches Wasserzeichen — dieser Inhalt wurde von dieser QRME-Installation nicht beglaubigt',
        'pt': 'não existe essa marca de água — este conteúdo não foi credenciado por esta instalação QRME',
        'it': 'nessuna filigrana di questo tipo — questo contenuto non è stato accreditato da questa installazione QRME',
        'ja': 'そのような透かしはありません — このコンテンツは、この QRME 環境が発行したものではありません',
        'zh': '没有该水印 — 此内容并非由本 QRME 部署签发凭证',
        'hi': 'ऐसा कोई वॉटरमार्क नहीं — यह सामग्री इस QRME परिनियोजन द्वारा प्रमाणित नहीं की गई',
        'ar': 'لا توجد علامة مائية بهذا الوصف — لم يعتمد هذا المحتوى من نشر QRME هذا',
    },
    'no synthetic profiles in this room': {
        'es': 'no hay perfiles sintéticos en esta sala',
        'fr': 'aucun profil synthétique dans cette salle',
        'de': 'keine synthetischen Profile in diesem Raum',
        'pt': 'não há perfis sintéticos nesta sala',
        'it': 'nessun profilo sintetico in questa stanza',
        'ja': 'このルームに合成プロフィールはありません',
        'zh': '此房间内没有合成资料',
        'hi': 'इस कक्ष में कोई सिंथेटिक प्रोफ़ाइल नहीं',
        'ar': 'لا توجد ملفات اصطناعية في هذه الغرفة',
    },
    'no view available for this desk': {
        'es': 'no hay vista disponible para este escritorio',
        'fr': 'aucune vue disponible pour ce bureau',
        'de': 'für diesen Desk ist keine Ansicht verfügbar',
        'pt': 'não há vista disponível para esta banca',
        'it': 'nessuna vista disponibile per questa postazione',
        'ja': 'このデスクに表示できるビューはありません',
        'zh': '此展台没有可用的视图',
        'hi': 'इस डेस्क के लिए कोई दृश्य उपलब्ध नहीं',
        'ar': 'لا يوجد عرض متاح لهذا المكتب',
    },
    'not a participant in this connection': {
        'es': 'no participa en esta conexión',
        'fr': 'vous ne participez pas à cette connexion',
        'de': 'Sie sind an dieser Verbindung nicht beteiligt',
        'pt': 'não participa nesta ligação',
        'it': 'non partecipi a questa connessione',
        'ja': 'この接続の参加者ではありません',
        'zh': '您不是此连接的参与者',
        'hi': 'आप इस कनेक्शन में सहभागी नहीं हैं',
        'ar': 'لست طرفًا في هذا الاتصال',
    },
    'not authorized for this account': {
        'es': 'sin autorización para esta cuenta',
        'fr': 'non autorisé pour ce compte',
        'de': 'keine Berechtigung für dieses Konto',
        'pt': 'sem autorização para esta conta',
        'it': 'non autorizzato per questo account',
        'ja': 'このアカウントへの権限がありません',
        'zh': '无权访问此账户',
        'hi': 'इस खाते के लिए अधिकार नहीं',
        'ar': 'غير مخوَّل لهذا الحساب',
    },
    'not in conversation with this profile; delegated work is for somebody already talking to it': {
        'es': 'no está en conversación con este perfil; el trabajo delegado es para quien ya habla con él',
        'fr': 'vous n\'êtes pas en conversation avec ce profil ; le travail délégué s\'adresse à quelqu\'un qui lui parle déjà',
        'de': 'Sie stehen mit diesem Profil nicht im Gespräch; delegierte Arbeit ist für jemanden, der bereits mit ihm spricht',
        'pt': 'não está em conversa com este perfil; o trabalho delegado é para quem já fala com ele',
        'it': 'non sei in conversazione con questo profilo; il lavoro delegato è per chi ci sta già parlando',
        'ja': 'このプロフィールとの会話がありません。委任された作業は、すでに会話している方のためのものです',
        'zh': '您尚未与此资料建立对话；委托工作面向已在与它交谈的人',
        'hi': 'आप इस प्रोफ़ाइल से बातचीत में नहीं हैं; प्रत्यायोजित कार्य उनके लिए है जो पहले से इससे बात कर रहे हैं',
        'ar': 'لست في محادثة مع هذا الملف؛ العمل المُفوَّض مخصّص لمن يتحدّث إليه بالفعل',
    },
    'not this organization\'s owner': {
        'es': 'no es el propietario de esta organización',
        'fr': 'vous n\'êtes pas le propriétaire de cette organisation',
        'de': 'nicht die Inhaberin oder der Inhaber dieser Organisation',
        'pt': 'não é o proprietário desta organização',
        'it': 'non sei il titolare di questa organizzazione',
        'ja': 'この組織の所有者ではありません',
        'zh': '您不是该组织的所有者',
        'hi': 'आप इस संगठन के स्वामी नहीं हैं',
        'ar': 'لست مالك هذه المؤسسة',
    },
    'not your credential': {
        'es': 'no es su credencial',
        'fr': 'ce n\'est pas votre identifiant',
        'de': 'nicht Ihr Berechtigungsnachweis',
        'pt': 'não é a sua credencial',
        'it': 'non è la tua credenziale',
        'ja': 'あなたの資格情報ではありません',
        'zh': '这不是您的凭据',
        'hi': 'यह आपका क्रेडेंशियल नहीं है',
        'ar': 'ليست بيانات اعتمادك',
    },
    'not your envelope': {
        'es': 'no es su sobre',
        'fr': 'ce n\'est pas votre enveloppe',
        'de': 'nicht Ihr Umschlag',
        'pt': 'não é o seu envelope',
        'it': 'non è la tua busta',
        'ja': 'あなたの封筒ではありません',
        'zh': '这不是您的信封',
        'hi': 'यह आपका लिफ़ाफ़ा नहीं है',
        'ar': 'ليس مظروفك',
    },
    'not your listing': {
        'es': 'no es su anuncio',
        'fr': 'ce n\'est pas votre annonce',
        'de': 'nicht Ihr Angebot',
        'pt': 'não é o seu anúncio',
        'it': 'non è il tuo annuncio',
        'ja': 'あなたの出品ではありません',
        'zh': '这不是您的刊登',
        'hi': 'यह आपकी लिस्टिंग नहीं है',
        'ar': 'ليس إعلانك',
    },
    'not yours to remove': {
        'es': 'no es suyo para quitarlo',
        'fr': 'ce n\'est pas à vous de le retirer',
        'de': 'nicht Ihres, um es zu entfernen',
        'pt': 'não é seu para remover',
        'it': 'non spetta a te rimuoverlo',
        'ja': 'これを取り除く権限はあなたにはありません',
        'zh': '这不是您可以移除的',
        'hi': 'इसे हटाना आपका अधिकार नहीं है',
        'ar': 'ليس لك أن تزيله',
    },
    'nothing accrued — the balance is zero': {
        'es': 'no hay nada acumulado — el saldo es cero',
        'fr': 'rien d\'accumulé — le solde est nul',
        'de': 'nichts aufgelaufen — der Saldo ist null',
        'pt': 'não há nada acumulado — o saldo é zero',
        'it': 'nulla di maturato — il saldo è zero',
        'ja': '積み上がった残高はありません — 残高はゼロです',
        'zh': '没有累计金额 — 余额为零',
        'hi': 'कुछ भी संचित नहीं — शेष शून्य है',
        'ar': 'لا شيء متراكم — الرصيد صفر',
    },
    'nothing answers to that code': {
        'es': 'nada responde a ese código',
        'fr': 'rien ne répond à ce code',
        'de': 'auf diesen Code antwortet nichts',
        'pt': 'nada responde a esse código',
        'it': 'nulla risponde a quel codice',
        'ja': 'そのコードに応じるものはありません',
        'zh': '没有任何内容对应该代码',
        'hi': 'उस कोड का कुछ भी उत्तर नहीं देता',
        'ar': 'لا شيء يستجيب لهذا الرمز',
    },
    'nothing answers to that reference': {
        'es': 'nada responde a esa referencia',
        'fr': 'rien ne répond à cette référence',
        'de': 'auf diese Referenz antwortet nichts',
        'pt': 'nada responde a essa referência',
        'it': 'nulla risponde a quel riferimento',
        'ja': 'その参照に応じるものはありません',
        'zh': '没有任何内容对应该引用',
        'hi': 'उस संदर्भ का कुछ भी उत्तर नहीं देता',
        'ar': 'لا شيء يستجيب لهذا المرجع',
    },
    'objection not found for this profile': {
        'es': 'objeción no encontrada para este perfil',
        'fr': 'objection introuvable pour ce profil',
        'de': 'Einspruch für dieses Profil nicht gefunden',
        'pt': 'objeção não encontrada para este perfil',
        'it': 'obiezione non trovata per questo profilo',
        'ja': 'このプロフィールに対する異議は見つかりません',
        'zh': '未找到针对此资料的异议',
        'hi': 'इस प्रोफ़ाइल के लिए आपत्ति नहीं मिली',
        'ar': 'لم يُعثر على اعتراض لهذا الملف',
    },
    'only a profile\'s owner can bring it into a room': {
        'es': 'solo el propietario de un perfil puede llevarlo a una sala',
        'fr': 'seul le propriétaire d\'un profil peut l\'amener dans une salle',
        'de': 'nur die Inhaberin oder der Inhaber eines Profils kann es in einen Raum bringen',
        'pt': 'apenas o proprietário de um perfil o pode trazer para uma sala',
        'it': 'solo il titolare di un profilo può portarlo in una stanza',
        'ja': 'プロフィールをルームに連れて来られるのは、その所有者だけです',
        'zh': '只有资料的所有者才能将其带入房间',
        'hi': 'किसी प्रोफ़ाइल को कक्ष में केवल उसका स्वामी ला सकता है',
        'ar': 'لا يمكن إحضار الملف إلى غرفة إلا مالكه',
    },
    'only adult-mode profiles are placed at adult venues': {
        'es': 'solo los perfiles en modo adulto se colocan en locales para adultos',
        'fr': 'seuls les profils en mode adulte sont placés dans des lieux pour adultes',
        'de': 'nur Profile im Erwachsenenmodus werden an Erwachsenen-Locations platziert',
        'pt': 'apenas perfis em modo adulto são colocados em locais para adultos',
        'it': 'solo i profili in modalità per adulti vengono collocati in locali per adulti',
        'ja': 'アダルト会場に配置できるのは、アダルトモードのプロフィールだけです',
        'zh': '只有成人模式的资料才会投放到成人场所',
        'hi': 'वयस्क स्थलों पर केवल वयस्क-मोड प्रोफ़ाइलें रखी जाती हैं',
        'ar': 'لا تُوضع في أماكن البالغين إلا الملفات في وضع البالغين',
    },
    'organization not found': {
        'es': 'organización no encontrada',
        'fr': 'organisation introuvable',
        'de': 'Organisation nicht gefunden',
        'pt': 'organização não encontrada',
        'it': 'organizzazione non trovata',
        'ja': '組織が見つかりません',
        'zh': '未找到组织',
        'hi': 'संगठन नहीं मिला',
        'ar': 'لم يُعثر على المؤسسة',
    },
    'outcome must be \'uphold\' or \'dismiss\'': {
        'es': 'outcome debe ser \'uphold\' o \'dismiss\'',
        'fr': 'outcome doit être \'uphold\' ou \'dismiss\'',
        'de': 'outcome muss \'uphold\' oder \'dismiss\' sein',
        'pt': 'outcome deve ser \'uphold\' ou \'dismiss\'',
        'it': 'outcome deve essere \'uphold\' o \'dismiss\'',
        'ja': 'outcome は \'uphold\' か \'dismiss\' である必要があります',
        'zh': 'outcome 必须为 \'uphold\' 或 \'dismiss\'',
        'hi': 'outcome का मान \'uphold\' या \'dismiss\' होना चाहिए',
        'ar': 'يجب أن تكون قيمة outcome إما \'uphold\' أو \'dismiss\'',
    },
    'owners under 18 require parent/guardian consent': {
        'es': 'los propietarios menores de 18 requieren el consentimiento de su padre, madre o tutor',
        'fr': 'les propriétaires de moins de 18 ans doivent avoir le consentement d\'un parent ou tuteur',
        'de': 'Inhaberinnen und Inhaber unter 18 benötigen die Einwilligung der Eltern oder Erziehungsberechtigten',
        'pt': 'proprietários com menos de 18 anos requerem consentimento parental ou do tutor',
        'it': 'i titolari di età inferiore a 18 anni richiedono il consenso di un genitore o tutore',
        'ja': '18歳未満の所有者には、保護者の同意が必要です',
        'zh': '未满18岁的所有者需要父母或监护人同意',
        'hi': '18 वर्ष से कम आयु के स्वामियों हेतु माता-पिता/अभिभावक की सहमति आवश्यक है',
        'ar': 'يحتاج المالكون دون سن 18 إلى موافقة أحد الوالدين أو الوصي',
    },
    'pack already installed on this profile': {
        'es': 'el paquete ya está instalado en este perfil',
        'fr': 'le pack est déjà installé sur ce profil',
        'de': 'das Paket ist auf diesem Profil bereits installiert',
        'pt': 'o pacote já está instalado neste perfil',
        'it': 'il pacchetto è già installato su questo profilo',
        'ja': 'このプロフィールには、このパックが既にインストール済みです',
        'zh': '该知识包已安装在此资料上',
        'hi': 'यह पैक इस प्रोफ़ाइल पर पहले से स्थापित है',
        'ar': 'الحزمة مثبَّتة بالفعل على هذا الملف',
    },
    'pack already installed on this robot': {
        'es': 'el paquete ya está instalado en este robot',
        'fr': 'le pack est déjà installé sur ce robot',
        'de': 'das Paket ist auf diesem Roboter bereits installiert',
        'pt': 'o pacote já está instalado neste robô',
        'it': 'il pacchetto è già installato su questo robot',
        'ja': 'このロボットには、このパックが既にインストール済みです',
        'zh': '该知识包已安装在此机器人上',
        'hi': 'यह पैक इस रोबोट पर पहले से स्थापित है',
        'ar': 'الحزمة مثبَّتة بالفعل على هذا الروبوت',
    },
    'pack not found': {
        'es': 'paquete no encontrado',
        'fr': 'pack introuvable',
        'de': 'Paket nicht gefunden',
        'pt': 'pacote não encontrado',
        'it': 'pacchetto non trovato',
        'ja': 'パックが見つかりません',
        'zh': '未找到知识包',
        'hi': 'पैक नहीं मिला',
        'ar': 'لم يُعثر على الحزمة',
    },
    'pack not installed on this profile': {
        'es': 'el paquete no está instalado en este perfil',
        'fr': 'le pack n\'est pas installé sur ce profil',
        'de': 'das Paket ist auf diesem Profil nicht installiert',
        'pt': 'o pacote não está instalado neste perfil',
        'it': 'il pacchetto non è installato su questo profilo',
        'ja': 'このプロフィールには、このパックはインストールされていません',
        'zh': '该知识包未安装在此资料上',
        'hi': 'यह पैक इस प्रोफ़ाइल पर स्थापित नहीं है',
        'ar': 'الحزمة غير مثبَّتة على هذا الملف',
    },
    'pack not installed on this robot': {
        'es': 'el paquete no está instalado en este robot',
        'fr': 'le pack n\'est pas installé sur ce robot',
        'de': 'das Paket ist auf diesem Roboter nicht installiert',
        'pt': 'o pacote não está instalado neste robô',
        'it': 'il pacchetto non è installato su questo robot',
        'ja': 'このロボットには、このパックはインストールされていません',
        'zh': '该知识包未安装在此机器人上',
        'hi': 'यह पैक इस रोबोट पर स्थापित नहीं है',
        'ar': 'الحزمة غير مثبَّتة على هذا الروبوت',
    },
    'placement not found': {
        'es': 'colocación no encontrada',
        'fr': 'placement introuvable',
        'de': 'Platzierung nicht gefunden',
        'pt': 'colocação não encontrada',
        'it': 'collocazione non trovata',
        'ja': '配置が見つかりません',
        'zh': '未找到投放记录',
        'hi': 'प्लेसमेंट नहीं मिला',
        'ar': 'لم يُعثر على التوظيف',
    },
    'price cannot be negative': {
        'es': 'el precio no puede ser negativo',
        'fr': 'le prix ne peut pas être négatif',
        'de': 'der Preis darf nicht negativ sein',
        'pt': 'o preço não pode ser negativo',
        'it': 'il prezzo non può essere negativo',
        'ja': '価格を負の値にはできません',
        'zh': '价格不能为负数',
        'hi': 'मूल्य ऋणात्मक नहीं हो सकता',
        'ar': 'لا يمكن أن يكون السعر سالبًا',
    },
    'profile has already departed': {
        'es': 'el perfil ya se ha marchado',
        'fr': 'le profil est déjà parti',
        'de': 'das Profil ist bereits verabschiedet',
        'pt': 'o perfil já partiu',
        'it': 'il profilo se n\'è già andato',
        'ja': 'このプロフィールは既に去っています',
        'zh': '该资料已离去',
        'hi': 'प्रोफ़ाइल पहले ही विदा ले चुकी है',
        'ar': 'سبق أن رحل هذا الملف',
    },
    'profile has an open objection; resolve it before succession': {
        'es': 'el perfil tiene una objeción abierta; resuélvala antes de la sucesión',
        'fr': 'le profil fait l\'objet d\'une objection en cours ; résolvez-la avant la succession',
        'de': 'für das Profil liegt ein offener Einspruch vor; klären Sie ihn vor der Nachfolge',
        'pt': 'o perfil tem uma objeção em aberto; resolva-a antes da sucessão',
        'it': 'il profilo ha un\'obiezione aperta; risolvila prima della successione',
        'ja': 'このプロフィールには未解決の異議があります。承継の前に解決してください',
        'zh': '该资料存在未决异议；请在继承前先行处理',
        'hi': 'प्रोफ़ाइल पर एक खुली आपत्ति है; उत्तराधिकार से पहले उसे निपटाएँ',
        'ar': 'على هذا الملف اعتراض مفتوح؛ احسمه قبل الخلافة',
    },
    'profile is not listed': {
        'es': 'el perfil no está anunciado',
        'fr': 'le profil n\'est pas mis en vente',
        'de': 'das Profil ist nicht gelistet',
        'pt': 'o perfil não está anunciado',
        'it': 'il profilo non è in vendita',
        'ja': 'このプロフィールは出品されていません',
        'zh': '该资料未被刊登',
        'hi': 'प्रोफ़ाइल सूचीबद्ध नहीं है',
        'ar': 'الملف غير معروض',
    },
    'profile knowledge packs install onto the profile — omit robot_id': {
        'es': 'los paquetes de conocimiento de perfil se instalan en el perfil — omita robot_id',
        'fr': 'les packs de connaissances de profil s\'installent sur le profil — omettez robot_id',
        'de': 'Wissenspakete für Profile werden auf dem Profil installiert — robot_id weglassen',
        'pt': 'os pacotes de conhecimento de perfil instalam-se no perfil — omita robot_id',
        'it': 'i pacchetti di conoscenza di profilo si installano sul profilo — ometti robot_id',
        'ja': 'プロフィール用の知識パックはプロフィールにインストールします — robot_id は指定しないでください',
        'zh': '资料知识包安装到资料上 — 请省略 robot_id',
        'hi': 'प्रोफ़ाइल ज्ञान पैक प्रोफ़ाइल पर स्थापित होते हैं — robot_id न भेजें',
        'ar': 'تُثبَّت حزم معرفة الملف على الملف — احذف robot_id',
    },
    'profile listings require profile_id': {
        'es': 'los anuncios de perfil requieren profile_id',
        'fr': 'les annonces de profil requièrent profile_id',
        'de': 'Profilangebote erfordern profile_id',
        'pt': 'os anúncios de perfil requerem profile_id',
        'it': 'gli annunci di profilo richiedono profile_id',
        'ja': 'プロフィールの出品には profile_id が必要です',
        'zh': '资料刊登需要 profile_id',
        'hi': 'प्रोफ़ाइल लिस्टिंग हेतु profile_id आवश्यक है',
        'ar': 'إعلانات الملفات تتطلّب profile_id',
    },
    'profiles of another real person require a consent/rights record': {
        'es': 'los perfiles de otra persona real requieren un registro de consentimiento o de derechos',
        'fr': 'les profils d\'une autre personne réelle exigent un enregistrement de consentement ou de droits',
        'de': 'Profile einer anderen realen Person erfordern einen Einwilligungs- oder Rechtenachweis',
        'pt': 'os perfis de outra pessoa real exigem um registo de consentimento ou de direitos',
        'it': 'i profili di un\'altra persona reale richiedono un registro di consenso o di diritti',
        'ja': '実在する他人のプロフィールには、同意または権利の記録が必要です',
        'zh': '他人的真实人物资料需要同意或权利记录',
        'hi': 'किसी अन्य वास्तविक व्यक्ति की प्रोफ़ाइल हेतु सहमति/अधिकार अभिलेख आवश्यक है',
        'ar': 'تتطلّب ملفات شخص حقيقي آخر سجلّ موافقة أو حقوق',
    },
    'provider not found': {
        'es': 'proveedor no encontrado',
        'fr': 'fournisseur introuvable',
        'de': 'Anbieter nicht gefunden',
        'pt': 'fornecedor não encontrado',
        'it': 'fornitore non trovato',
        'ja': 'プロバイダーが見つかりません',
        'zh': '未找到提供方',
        'hi': 'प्रदाता नहीं मिला',
        'ar': 'لم يُعثر على المزوّد',
    },
    'publishing needs an owner token': {
        'es': 'publicar necesita un token de propietario',
        'fr': 'la publication nécessite un jeton propriétaire',
        'de': 'das Veröffentlichen erfordert ein Eigentümer-Token',
        'pt': 'publicar exige um token de proprietário',
        'it': 'la pubblicazione richiede un token del titolare',
        'ja': '公開には所有者トークンが必要です',
        'zh': '发布需要所有者令牌',
        'hi': 'प्रकाशन हेतु स्वामी टोकन आवश्यक है',
        'ar': 'النشر يتطلّب رمز المالك',
    },
    'rated packs install only onto adult-mode profiles': {
        'es': 'los paquetes con clasificación se instalan solo en perfiles en modo adulto',
        'fr': 'les packs classés ne s\'installent que sur des profils en mode adulte',
        'de': 'eingestufte Pakete lassen sich nur auf Profilen im Erwachsenenmodus installieren',
        'pt': 'os pacotes classificados instalam-se apenas em perfis em modo adulto',
        'it': 'i pacchetti classificati si installano solo su profili in modalità per adulti',
        'ja': 'レーティング付きパックは、アダルトモードのプロフィールにのみインストールできます',
        'zh': '分级知识包只能安装到成人模式的资料上',
        'hi': 'रेटेड पैक केवल वयस्क-मोड प्रोफ़ाइलों पर स्थापित होते हैं',
        'ar': 'لا تُثبَّت الحزم المصنَّفة إلا على الملفات في وضع البالغين',
    },
    'rating must be 1–5': {
        'es': 'la valoración debe estar entre 1 y 5',
        'fr': 'la note doit être comprise entre 1 et 5',
        'de': 'die Bewertung muss zwischen 1 und 5 liegen',
        'pt': 'a avaliação deve estar entre 1 e 5',
        'it': 'la valutazione deve essere compresa tra 1 e 5',
        'ja': '評価は1〜5の範囲で指定してください',
        'zh': '评分必须为 1–5',
        'hi': 'रेटिंग 1–5 के बीच होनी चाहिए',
        'ar': 'يجب أن يكون التقييم بين 1 و5',
    },
    'renewing charges a period, so it needs the beneficiary the money accrues to': {
        'es': 'renovar cobra un periodo, así que necesita el beneficiario al que se acumula el dinero',
        'fr': 'le renouvellement facture une période : il faut donc le bénéficiaire à qui l\'argent revient',
        'de': 'eine Verlängerung berechnet einen Zeitraum; dafür wird die begünstigte Person benötigt, der das Geld zufließt',
        'pt': 'renovar cobra um período, por isso é necessário o beneficiário a quem o dinheiro se acumula',
        'it': 'il rinnovo addebita un periodo, quindi serve il beneficiario a cui il denaro matura',
        'ja': '更新は一定期間分を課金するため、その収入が帰属する受取人が必要です',
        'zh': '续订会按周期收费，因此需要指明款项归属的受益人',
        'hi': 'नवीनीकरण एक अवधि का शुल्क लेता है, इसलिए वह लाभार्थी चाहिए जिसे राशि जमा होती है',
        'ar': 'التجديد يفرض رسوم فترة، لذا يلزم المستفيد الذي يُستحق له المال',
    },
    'robot not found': {
        'es': 'robot no encontrado',
        'fr': 'robot introuvable',
        'de': 'Roboter nicht gefunden',
        'pt': 'robô não encontrado',
        'it': 'robot non trovato',
        'ja': 'ロボットが見つかりません',
        'zh': '未找到机器人',
        'hi': 'रोबोट नहीं मिला',
        'ar': 'لم يُعثر على الروبوت',
    },
    'robot not found on this profile': {
        'es': 'robot no encontrado en este perfil',
        'fr': 'robot introuvable sur ce profil',
        'de': 'Roboter auf diesem Profil nicht gefunden',
        'pt': 'robô não encontrado neste perfil',
        'it': 'robot non trovato su questo profilo',
        'ja': 'このプロフィールにそのロボットは見つかりません',
        'zh': '此资料下未找到该机器人',
        'hi': 'इस प्रोफ़ाइल पर रोबोट नहीं मिला',
        'ar': 'لم يُعثر على الروبوت في هذا الملف',
    },
    'robot packs install onto a bound robot — pass robot_id': {
        'es': 'los paquetes de robot se instalan en un robot vinculado — pase robot_id',
        'fr': 'les packs robot s\'installent sur un robot lié — passez robot_id',
        'de': 'Roboterpakete werden auf einem gebundenen Roboter installiert — robot_id angeben',
        'pt': 'os pacotes de robô instalam-se num robô associado — passe robot_id',
        'it': 'i pacchetti per robot si installano su un robot associato — passa robot_id',
        'ja': 'ロボットパックは紐づけ済みのロボットにインストールします — robot_id を指定してください',
        'zh': '机器人知识包安装到已绑定的机器人上 — 请传入 robot_id',
        'hi': 'रोबोट पैक किसी बंधे रोबोट पर स्थापित होते हैं — robot_id भेजें',
        'ar': 'تُثبَّت حزم الروبوت على روبوت مرتبط — مرِّر robot_id',
    },
    'room not found': {
        'es': 'sala no encontrada',
        'fr': 'salle introuvable',
        'de': 'Raum nicht gefunden',
        'pt': 'sala não encontrada',
        'it': 'stanza non trovata',
        'ja': 'ルームが見つかりません',
        'zh': '未找到房间',
        'hi': 'कक्ष नहीं मिला',
        'ar': 'لم يُعثر على الغرفة',
    },
    'say requires an arg (what to speak about)': {
        'es': 'say requiere un arg (sobre qué hablar)',
        'fr': 'say nécessite un arg (le sujet à énoncer)',
        'de': 'say benötigt ein arg (worüber gesprochen werden soll)',
        'pt': 'say requer um arg (aquilo sobre o que falar)',
        'it': 'say richiede un arg (di cosa parlare)',
        'ja': 'say には arg（何を話すか）が必要です',
        'zh': 'say 需要一个 arg（要说的内容）',
        'hi': 'say को एक arg चाहिए (किस बारे में बोलना है)',
        'ar': 'يتطلّب say وسيطًا arg (ما الذي يُقال)',
    },
    'social connection not found': {
        'es': 'conexión social no encontrada',
        'fr': 'connexion sociale introuvable',
        'de': 'soziale Verbindung nicht gefunden',
        'pt': 'ligação social não encontrada',
        'it': 'connessione social non trovata',
        'ja': 'ソーシャル接続が見つかりません',
        'zh': '未找到社交连接',
        'hi': 'सोशल कनेक्शन नहीं मिला',
        'ar': 'لم يُعثر على الاتصال الاجتماعي',
    },
    'that is not yours to remove': {
        'es': 'eso no es suyo para quitarlo',
        'fr': 'ce n\'est pas à vous de le retirer',
        'de': 'das ist nicht Ihres, um es zu entfernen',
        'pt': 'isso não é seu para remover',
        'it': 'non spetta a te rimuoverlo',
        'ja': 'それを取り除く権限はあなたにはありません',
        'zh': '这不是您可以移除的',
        'hi': 'उसे हटाना आपका अधिकार नहीं है',
        'ar': 'ليس لك أن تزيل ذلك',
    },
    'that is not yours to say': {
        'es': 'eso no es suyo para decirlo',
        'fr': 'ce n\'est pas à vous de le dire',
        'de': 'das ist nicht Ihres, um es zu sagen',
        'pt': 'isso não é seu para dizer',
        'it': 'non spetta a te dirlo',
        'ja': 'それを述べる権限はあなたにはありません',
        'zh': '这不是您可以发表的',
        'hi': 'उसे कहना आपका अधिकार नहीं है',
        'ar': 'ليس لك أن تقول ذلك',
    },
    'that profile is not yours. Bringing somebody else\'s into your session is a two-party agreement — see the skill-grant routes, which already ask both sides': {
        'es': 'ese perfil no es suyo. Traer el de otra persona a su sesión es un acuerdo entre dos partes — consulte las rutas de concesión de habilidades, que ya preguntan a ambos lados',
        'fr': 'ce profil n\'est pas le vôtre. Amener celui de quelqu\'un d\'autre dans votre session est un accord entre deux parties — voyez les routes de concession de compétences, qui interrogent déjà les deux côtés',
        'de': 'dieses Profil gehört Ihnen nicht. Das Profil einer anderen Person in Ihre Sitzung zu holen ist eine Vereinbarung zwischen zwei Parteien — siehe die Skill-Grant-Routen, die bereits beide Seiten fragen',
        'pt': 'esse perfil não é seu. Trazer o de outra pessoa para a sua sessão é um acordo entre duas partes — consulte as rotas de concessão de competências, que já perguntam a ambos os lados',
        'it': 'quel profilo non è tuo. Portare quello di qualcun altro nella tua sessione è un accordo tra due parti — vedi le rotte di concessione delle competenze, che già interpellano entrambe le parti',
        'ja': 'そのプロフィールはあなたのものではありません。他人のものを自分のセッションに連れて来ることは二者間の合意です — 既に双方に確認するスキル付与のルートをご覧ください',
        'zh': '该资料不属于您。把别人的资料带入您的会话是一项双方协议 — 请参阅技能授权路由，它已经会征询双方意见',
        'hi': 'वह प्रोफ़ाइल आपकी नहीं है। किसी और की प्रोफ़ाइल को अपने सत्र में लाना दो-पक्षीय सहमति है — स्किल-ग्रांट रूट देखें, जो पहले से दोनों पक्षों से पूछते हैं',
        'ar': 'ذلك الملف ليس لك. إحضار ملف شخص آخر إلى جلستك اتفاق بين طرفين — راجع مسارات منح المهارات، فهي تسأل الطرفين أصلًا',
    },
    'the rated tier requires verified 18+ participants': {
        'es': 'el nivel con clasificación requiere participantes verificados de 18+',
        'fr': 'le palier classé exige des participants vérifiés de 18 ans ou plus',
        'de': 'die eingestufte Stufe erfordert geprüft volljährige Teilnehmende',
        'pt': 'o nível classificado exige participantes verificados com 18+',
        'it': 'il livello classificato richiede partecipanti verificati 18+',
        'ja': 'レーティング付きの階層には、18歳以上と確認された参加者が必要です',
        'zh': '分级层级需要经过验证的18岁以上参与者',
        'hi': 'रेटेड श्रेणी हेतु सत्यापित 18+ प्रतिभागी आवश्यक हैं',
        'ar': 'تتطلّب الفئة المصنَّفة مشاركين مُوثَّقين بعمر 18 عامًا فأكثر',
    },
    'this beacon has been picked up': {
        'es': 'esta baliza ya ha sido recogida',
        'fr': 'cette balise a déjà été récupérée',
        'de': 'dieser Beacon wurde bereits abgeholt',
        'pt': 'esta baliza já foi recolhida',
        'it': 'questo beacon è già stato ritirato',
        'ja': 'このビーコンは既に引き取られています',
        'zh': '此信标已被领取',
        'hi': 'यह बीकन उठाया जा चुका है',
        'ar': 'سبق أن التُقطت هذه المنارة',
    },
    'this connection has ended': {
        'es': 'esta conexión ha terminado',
        'fr': 'cette connexion est terminée',
        'de': 'diese Verbindung ist beendet',
        'pt': 'esta ligação terminou',
        'it': 'questa connessione è terminata',
        'ja': 'この接続は終了しました',
        'zh': '此连接已结束',
        'hi': 'यह कनेक्शन समाप्त हो चुका है',
        'ar': 'انتهى هذا الاتصال',
    },
    'this connection is for collecting, not publishing': {
        'es': 'esta conexión es para recopilar, no para publicar',
        'fr': 'cette connexion sert à collecter, pas à publier',
        'de': 'diese Verbindung dient dem Sammeln, nicht dem Veröffentlichen',
        'pt': 'esta ligação é para recolher e não para publicar',
        'it': 'questa connessione serve a raccogliere, non a pubblicare',
        'ja': 'この接続は収集用であり、公開用ではありません',
        'zh': '此连接用于收集，而非发布',
        'hi': 'यह कनेक्शन एकत्र करने के लिए है, प्रकाशन के लिए नहीं',
        'ar': 'هذا الاتصال للجمع لا للنشر',
    },
    'this connection is for publishing, not collecting': {
        'es': 'esta conexión es para publicar, no para recopilar',
        'fr': 'cette connexion sert à publier, pas à collecter',
        'de': 'diese Verbindung dient dem Veröffentlichen, nicht dem Sammeln',
        'pt': 'esta ligação é para publicar e não para recolher',
        'it': 'questa connessione serve a pubblicare, non a raccogliere',
        'ja': 'この接続は公開用であり、収集用ではありません',
        'zh': '此连接用于发布，而非收集',
        'hi': 'यह कनेक्शन प्रकाशन के लिए है, एकत्र करने के लिए नहीं',
        'ar': 'هذا الاتصال للنشر لا للجمع',
    },
    'this excursion has no findings to learn': {
        'es': 'esta excursión no tiene hallazgos que aprender',
        'fr': 'cette excursion n\'a aucun résultat à apprendre',
        'de': 'diese Exkursion hat keine Erkenntnisse zum Lernen',
        'pt': 'esta excursão não tem descobertas para aprender',
        'it': 'questa escursione non ha risultati da apprendere',
        'ja': 'このエクスカーションには、学べる知見がありません',
        'zh': '此次外出探索没有可供学习的发现',
        'hi': 'इस भ्रमण में सीखने योग्य कोई निष्कर्ष नहीं',
        'ar': 'لا توجد نتائج قابلة للتعلّم في هذه الرحلة',
    },
    'this game session has ended': {
        'es': 'esta sesión de juego ha terminado',
        'fr': 'cette session de jeu est terminée',
        'de': 'diese Spielsitzung ist beendet',
        'pt': 'esta sessão de jogo terminou',
        'it': 'questa sessione di gioco è terminata',
        'ja': 'このゲームセッションは終了しました',
        'zh': '此游戏会话已结束',
        'hi': 'यह गेम सत्र समाप्त हो चुका है',
        'ar': 'انتهت جلسة اللعب هذه',
    },
    'this license belongs to another buyer': {
        'es': 'esta licencia pertenece a otro comprador',
        'fr': 'cette licence appartient à un autre acheteur',
        'de': 'diese Lizenz gehört einer anderen Käuferin oder einem anderen Käufer',
        'pt': 'esta licença pertence a outro comprador',
        'it': 'questa licenza appartiene a un altro acquirente',
        'ja': 'このライセンスは別の購入者のものです',
        'zh': '此许可属于其他买家',
        'hi': 'यह लाइसेंस किसी अन्य खरीदार का है',
        'ar': 'هذا الترخيص يخصّ مشتريًا آخر',
    },
    'this license does not permit deriving an agent (consult only)': {
        'es': 'esta licencia no permite derivar un agente (solo consulta)',
        'fr': 'cette licence ne permet pas de dériver un agent (consultation uniquement)',
        'de': 'diese Lizenz erlaubt kein Ableiten eines Agenten (nur Beratung)',
        'pt': 'esta licença não permite derivar um agente (apenas consulta)',
        'it': 'questa licenza non consente di derivare un agente (solo consultazione)',
        'ja': 'このライセンスではエージェントを派生できません（相談のみ）',
        'zh': '此许可不允许派生代理（仅限咨询）',
        'hi': 'यह लाइसेंस एजेंट व्युत्पन्न करने की अनुमति नहीं देता (केवल परामर्श)',
        'ar': 'لا يسمح هذا الترخيص باشتقاق وكيل (استشارة فقط)',
    },
    'this license has been revoked': {
        'es': 'esta licencia ha sido revocada',
        'fr': 'cette licence a été révoquée',
        'de': 'diese Lizenz wurde widerrufen',
        'pt': 'esta licença foi revogada',
        'it': 'questa licenza è stata revocata',
        'ja': 'このライセンスは取り消されました',
        'zh': '此许可已被撤销',
        'hi': 'यह लाइसेंस रद्द कर दिया गया है',
        'ar': 'تم إلغاء هذا الترخيص',
    },
    'this listing is not for sale': {
        'es': 'este anuncio no está en venta',
        'fr': 'cette annonce n\'est pas à vendre',
        'de': 'dieses Angebot steht nicht zum Verkauf',
        'pt': 'este anúncio não está à venda',
        'it': 'questo annuncio non è in vendita',
        'ja': 'この出品は販売対象ではありません',
        'zh': '此刊登不出售',
        'hi': 'यह लिस्टिंग बिक्री हेतु नहीं है',
        'ar': 'هذا الإعلان ليس للبيع',
    },
    'this pack is age-restricted (18+); present a verified-18+ interactor token or an adult-mode owner token': {
        'es': 'este paquete tiene restricción de edad (18+); presente un token de interactor verificado de 18+ o un token de propietario en modo adulto',
        'fr': 'ce pack est réservé aux adultes (18+) ; présentez un jeton d\'interacteur vérifié 18+ ou un jeton propriétaire en mode adulte',
        'de': 'dieses Paket ist altersbeschränkt (ab 18); legen Sie ein geprüftes 18+-Interaktor-Token oder ein Eigentümer-Token im Erwachsenenmodus vor',
        'pt': 'este pacote tem restrição de idade (18+); apresente um token de interator verificado com 18+ ou um token de proprietário em modo adulto',
        'it': 'questo pacchetto è vietato ai minori (18+); presenta un token di interattore verificato 18+ o un token del titolare in modalità per adulti',
        'ja': 'このパックは年齢制限付き（18歳以上）です。18歳以上と確認されたインタラクター・トークン、またはアダルトモードの所有者トークンを提示してください',
        'zh': '此知识包有年龄限制（18+）；请出示已验证的18岁以上互动者令牌或成人模式的所有者令牌',
        'hi': 'यह पैक आयु-प्रतिबंधित है (18+); सत्यापित 18+ इंटरैक्टर टोकन या वयस्क-मोड स्वामी टोकन प्रस्तुत करें',
        'ar': 'هذه الحزمة مقيَّدة بالعمر (18+)؛ قدِّم رمز متفاعل مُوثَّقًا بعمر 18+ أو رمز مالك في وضع البالغين',
    },
    'this profile has been terminated': {
        'es': 'este perfil ha sido eliminado',
        'fr': 'ce profil a été supprimé',
        'de': 'dieses Profil wurde beendet',
        'pt': 'este perfil foi eliminado',
        'it': 'questo profilo è stato eliminato',
        'ja': 'このプロフィールは終了しました',
        'zh': '此资料已被终止',
        'hi': 'यह प्रोफ़ाइल समाप्त कर दी गई है',
        'ar': 'أُنهي هذا الملف',
    },
    'this profile has departed': {
        'es': 'este perfil se ha marchado',
        'fr': 'ce profil est parti',
        'de': 'dieses Profil hat sich verabschiedet',
        'pt': 'este perfil partiu',
        'it': 'questo profilo se n\'è andato',
        'ja': 'このプロフィールは去りました',
        'zh': '此资料已离去',
        'hi': 'यह प्रोफ़ाइल विदा ले चुकी है',
        'ar': 'رحل هذا الملف',
    },
    'this profile has departed; its memory remains viewable': {
        'es': 'este perfil se ha marchado; su memoria sigue siendo visible',
        'fr': 'ce profil est parti ; sa mémoire reste consultable',
        'de': 'dieses Profil hat sich verabschiedet; seine Erinnerung bleibt einsehbar',
        'pt': 'este perfil partiu; a sua memória permanece visível',
        'it': 'questo profilo se n\'è andato; la sua memoria resta consultabile',
        'ja': 'このプロフィールは去りました。その記憶は引き続き閲覧できます',
        'zh': '此资料已离去；其记忆仍可查看',
        'hi': 'यह प्रोफ़ाइल विदा ले चुकी है; इसकी स्मृति देखी जा सकती है',
        'ar': 'رحل هذا الملف؛ ولا تزال ذاكرته قابلة للاطّلاع',
    },
    'this profile is age-gated; verified 18+ required': {
        'es': 'este perfil tiene restricción de edad; se requiere verificación de 18+',
        'fr': 'ce profil est réservé aux adultes ; vérification 18+ requise',
        'de': 'dieses Profil ist altersbeschränkt; geprüfte Volljährigkeit erforderlich',
        'pt': 'este perfil tem restrição de idade; é necessária verificação de 18+',
        'it': 'questo profilo è vietato ai minori; è richiesta la verifica 18+',
        'ja': 'このプロフィールは年齢制限付きです。18歳以上の確認が必要です',
        'zh': '此资料有年龄限制；需要18岁以上验证',
        'hi': 'यह प्रोफ़ाइल आयु-प्रतिबंधित है; सत्यापित 18+ आवश्यक',
        'ar': 'هذا الملف مقيَّد بالعمر؛ يلزم توثيق 18 عامًا فأكثر',
    },
    'this profile is not a hybrid': {
        'es': 'este perfil no es híbrido',
        'fr': 'ce profil n\'est pas hybride',
        'de': 'dieses Profil ist kein Hybrid',
        'pt': 'este perfil não é híbrido',
        'it': 'questo profilo non è ibrido',
        'ja': 'このプロフィールはハイブリッドではありません',
        'zh': '此资料不是混合资料',
        'hi': 'यह प्रोफ़ाइल हाइब्रिड नहीं है',
        'ar': 'هذا الملف ليس هجينًا',
    },
    'this profile is not offered for license': {
        'es': 'este perfil no se ofrece bajo licencia',
        'fr': 'ce profil n\'est pas proposé sous licence',
        'de': 'dieses Profil wird nicht zur Lizenzierung angeboten',
        'pt': 'este perfil não é oferecido para licenciamento',
        'it': 'questo profilo non è offerto in licenza',
        'ja': 'このプロフィールはライセンス提供されていません',
        'zh': '此资料未提供许可',
        'hi': 'यह प्रोफ़ाइल लाइसेंस हेतु प्रस्तुत नहीं है',
        'ar': 'هذا الملف غير معروض للترخيص',
    },
    'this profile is reactive-only; its owner has not enabled proactive outreach': {
        'es': 'este perfil es solo reactivo; su propietario no ha habilitado el contacto proactivo',
        'fr': 'ce profil est uniquement réactif ; son propriétaire n\'a pas activé les prises de contact spontanées',
        'de': 'dieses Profil ist rein reaktiv; die Inhaberin oder der Inhaber hat proaktive Ansprache nicht aktiviert',
        'pt': 'este perfil é apenas reativo; o seu proprietário não ativou o contacto proativo',
        'it': 'questo profilo è solo reattivo; il titolare non ha abilitato i contatti proattivi',
        'ja': 'このプロフィールは受動的な応答のみです。所有者は能動的な働きかけを有効にしていません',
        'zh': '此资料仅被动响应；其所有者未启用主动联系',
        'hi': 'यह प्रोफ़ाइल केवल प्रतिक्रियात्मक है; इसके स्वामी ने सक्रिय संपर्क सक्षम नहीं किया',
        'ar': 'هذا الملف تفاعلي فقط؛ لم يُفعّل مالكه التواصل المبادِر',
    },
    'this profile is restricted pending an objection review; it is not accepting new interactors': {
        'es': 'este perfil está restringido a la espera de la revisión de una objeción; no está aceptando nuevos interactores',
        'fr': 'ce profil est restreint dans l\'attente de l\'examen d\'une objection ; il n\'accepte pas de nouveaux interacteurs',
        'de': 'dieses Profil ist bis zur Einspruchsprüfung eingeschränkt; es nimmt keine neuen Interaktoren auf',
        'pt': 'este perfil está restrito enquanto aguarda a revisão de uma objeção; não está a aceitar novos interatores',
        'it': 'questo profilo è limitato in attesa della revisione di un\'obiezione; non accetta nuovi interattori',
        'ja': 'このプロフィールは異議の審査を待って制限中です。新しいインタラクターは受け付けていません',
        'zh': '此资料因异议待审而受限；暂不接受新的互动者',
        'hi': 'यह प्रोफ़ाइल आपत्ति समीक्षा तक प्रतिबंधित है; नए इंटरैक्टर स्वीकार नहीं कर रही',
        'ar': 'هذا الملف مقيَّد بانتظار مراجعة اعتراض؛ ولا يقبل متفاعلين جددًا',
    },
    'this profile no longer answers': {
        'es': 'este perfil ya no responde',
        'fr': 'ce profil ne répond plus',
        'de': 'dieses Profil antwortet nicht mehr',
        'pt': 'este perfil já não responde',
        'it': 'questo profilo non risponde più',
        'ja': 'このプロフィールはもう応答しません',
        'zh': '此资料不再作出回应',
        'hi': 'यह प्रोफ़ाइल अब उत्तर नहीं देती',
        'ar': 'لم يعد هذا الملف يستجيب',
    },
    'this profile\'s license is age-restricted (18+); present a verified-18+ interactor token': {
        'es': 'la licencia de este perfil tiene restricción de edad (18+); presente un token de interactor verificado de 18+',
        'fr': 'la licence de ce profil est réservée aux adultes (18+) ; présentez un jeton d\'interacteur vérifié 18+',
        'de': 'die Lizenz dieses Profils ist altersbeschränkt (ab 18); legen Sie ein geprüftes 18+-Interaktor-Token vor',
        'pt': 'a licença deste perfil tem restrição de idade (18+); apresente um token de interator verificado com 18+',
        'it': 'la licenza di questo profilo è vietata ai minori (18+); presenta un token di interattore verificato 18+',
        'ja': 'このプロフィールのライセンスは年齢制限付き（18歳以上）です。18歳以上と確認されたインタラクター・トークンを提示してください',
        'zh': '此资料的许可有年龄限制（18+）；请出示已验证的18岁以上互动者令牌',
        'hi': 'इस प्रोफ़ाइल का लाइसेंस आयु-प्रतिबंधित है (18+); सत्यापित 18+ इंटरैक्टर टोकन प्रस्तुत करें',
        'ar': 'ترخيص هذا الملف مقيَّد بالعمر (18+)؛ قدِّم رمز متفاعل مُوثَّقًا بعمر 18+',
    },
    'this token names no profile': {
        'es': 'este token no nombra ningún perfil',
        'fr': 'ce jeton ne désigne aucun profil',
        'de': 'dieses Token benennt kein Profil',
        'pt': 'este token não nomeia nenhum perfil',
        'it': 'questo token non indica alcun profilo',
        'ja': 'このトークンはどのプロフィールも指していません',
        'zh': '此令牌未指向任何资料',
        'hi': 'यह टोकन किसी प्रोफ़ाइल को नहीं दर्शाता',
        'ar': 'لا يشير هذا الرمز إلى أي ملف',
    },
    'token does not resolve to a profile': {
        'es': 'el token no resuelve a un perfil',
        'fr': 'le jeton ne correspond à aucun profil',
        'de': 'das Token lässt sich keinem Profil zuordnen',
        'pt': 'o token não corresponde a um perfil',
        'it': 'il token non corrisponde ad alcun profilo',
        'ja': 'トークンをプロフィールに解決できません',
        'zh': '令牌无法解析到任何资料',
        'hi': 'टोकन किसी प्रोफ़ाइल पर हल नहीं होता',
        'ar': 'لا يُحَلّ الرمز إلى ملف',
    },
    'token invalid or revoked': {
        'es': 'token no válido o revocado',
        'fr': 'jeton invalide ou révoqué',
        'de': 'Token ungültig oder widerrufen',
        'pt': 'token inválido ou revogado',
        'it': 'token non valido o revocato',
        'ja': 'トークンが無効か、取り消されています',
        'zh': '令牌无效或已撤销',
        'hi': 'टोकन अमान्य या रद्द',
        'ar': 'الرمز غير صالح أو مُلغى',
    },
    'unknown registry': {
        'es': 'registro desconocido',
        'fr': 'registre inconnu',
        'de': 'unbekanntes Verzeichnis',
        'pt': 'registo desconhecido',
        'it': 'registro sconosciuto',
        'ja': '不明なレジストリです',
        'zh': '未知的注册表',
        'hi': 'अज्ञात रजिस्ट्री',
        'ar': 'سجلّ غير معروف',
    },
    'unknown venue': {
        'es': 'local desconocido',
        'fr': 'lieu inconnu',
        'de': 'unbekannte Location',
        'pt': 'local desconhecido',
        'it': 'locale sconosciuto',
        'ja': '不明な会場です',
        'zh': '未知的场所',
        'hi': 'अज्ञात स्थल',
        'ar': 'مكان غير معروف',
    },
    'workflow actions: advance, assist, cancel': {
        'es': 'acciones del flujo de trabajo: advance, assist, cancel',
        'fr': 'actions du flux de travail : advance, assist, cancel',
        'de': 'Aktionen des Arbeitsablaufs: advance, assist, cancel',
        'pt': 'ações do fluxo de trabalho: advance, assist, cancel',
        'it': 'azioni del flusso di lavoro: advance, assist, cancel',
        'ja': 'ワークフローの操作: advance, assist, cancel',
        'zh': '工作流操作：advance、assist、cancel',
        'hi': 'वर्कफ़्लो क्रियाएँ: advance, assist, cancel',
        'ar': 'إجراءات سير العمل: advance, assist, cancel',
    },
    'workflow not found': {
        'es': 'flujo de trabajo no encontrado',
        'fr': 'flux de travail introuvable',
        'de': 'Arbeitsablauf nicht gefunden',
        'pt': 'fluxo de trabalho não encontrado',
        'it': 'flusso di lavoro non trovato',
        'ja': 'ワークフローが見つかりません',
        'zh': '未找到工作流',
        'hi': 'वर्कफ़्लो नहीं मिला',
        'ar': 'لم يُعثر على سير العمل',
    },
    'you are not here': {
        'es': 'usted no está aquí',
        'fr': 'vous n\'êtes pas ici',
        'de': 'Sie sind nicht hier',
        'pt': 'não está aqui',
        'it': 'non sei qui',
        'ja': 'あなたはここにいません',
        'zh': '您不在这里',
        'hi': 'आप यहाँ नहीं हैं',
        'ar': 'لست هنا',
    },
    'you are not in this lobby': {
        'es': 'usted no está en este vestíbulo',
        'fr': 'vous n\'êtes pas dans ce hall',
        'de': 'Sie sind nicht in dieser Lobby',
        'pt': 'não está neste átrio',
        'it': 'non sei in questa lobby',
        'ja': 'あなたはこのロビーにいません',
        'zh': '您不在此大厅中',
        'hi': 'आप इस लॉबी में नहीं हैं',
        'ar': 'لست في هذه الردهة',
    },
    'you are not in this room': {
        'es': 'usted no está en esta sala',
        'fr': 'vous n\'êtes pas dans cette salle',
        'de': 'Sie sind nicht in diesem Raum',
        'pt': 'não está nesta sala',
        'it': 'non sei in questa stanza',
        'ja': 'あなたはこのルームにいません',
        'zh': '您不在此房间中',
        'hi': 'आप इस कक्ष में नहीं हैं',
        'ar': 'لست في هذه الغرفة',
    },
    'you are not in this watch party': {
        'es': 'usted no está en esta fiesta de visionado',
        'fr': 'vous n\'êtes pas dans cette soirée de visionnage',
        'de': 'Sie sind nicht in dieser Watch-Party',
        'pt': 'não está nesta festa de visualização',
        'it': 'non sei in questa festa di visione',
        'ja': 'あなたはこのウォッチパーティーにいません',
        'zh': '您不在此观影派对中',
        'hi': 'आप इस वॉच पार्टी में नहीं हैं',
        'ar': 'لست في حفل المشاهدة هذا',
    },
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


#: The label the form shows, for the fields a person types into one.
#:
#: `validation_message` used to render pydantic's own field name — a 422 on the
#: sign-up form said `display_name — Field required` while the form beside it
#: said **Profile name**, and had said it in ten languages since the console
#: was localized.
#:
#:     asked     is the refusal a sentence in the reader's language
#:     mattered  does it name the field the reader can see
#:
#: Server-side, where the sentence is composed, for the reason that sentence is
#: composed here at all: nine clients rendering it is nine chances to render it
#: differently, and six of those are in languages with no test runner in this
#: repository.
#:
#: Wording ported from the console's own labels where one exists —
#: `onb.profile.name`, `onb.persona`, `onb.email`, `onb.password` — so the
#: sentence and the form agree by construction rather than by somebody keeping
#: them in step. There is no mechanical mapping to port the rest: the console's
#: rows are keyed by screen, and a name-match against them returns `title` →
#: *"A profile depicts me"*, which is a heading. Guessing is what
#: `validation_message`'s docstring declined to do, and this table does not.
#:
#: A field with no row keeps its identifier, exactly as before, and is recorded
#: in `tests/field_labels_unmapped.txt`.
_FIELD_LABELS: dict[str, dict[str, str]] = {
    # The accessibility report's three questions, worded as the form asks
    # them — a refusal that names one of these should read like the form.
    'doing': {'en': 'What were you trying to do?', 'es': '¿Qué intentabas hacer?', 'fr': 'Qu’essayiez-vous de faire ?', 'de': 'Was hast du versucht zu tun?', 'pt': 'O que você estava tentando fazer?', 'it': 'Cosa stavi cercando di fare?', 'ja': '何をしようとしていましたか？', 'zh': '你当时想做什么？', 'hi': 'आप क्या करने की कोशिश कर रहे थे?', 'ar': 'ما الذي كنت تحاول فعله؟'},
    'wall': {'en': 'What stood in the way?', 'es': '¿Qué se interpuso?', 'fr': 'Qu’est-ce qui a fait obstacle ?', 'de': 'Was stand im Weg?', 'pt': 'O que ficou no caminho?', 'it': 'Cosa ti ha ostacolato?', 'ja': '何が妨げになりましたか？', 'zh': '是什么挡住了你？', 'hi': 'क्या आड़े आया?', 'ar': 'ما الذي وقف في الطريق؟'},
    'help': {'en': 'What would help?', 'es': '¿Qué ayudaría?', 'fr': 'Qu’est-ce qui aiderait ?', 'de': 'Was würde helfen?', 'pt': 'O que ajudaria?', 'it': 'Cosa aiuterebbe?', 'ja': '何があれば助かりますか？', 'zh': '什么会有帮助？', 'hi': 'क्या मदद करेगा?', 'ar': 'ما الذي قد يساعد؟'},
    'lang': {'en': 'Language', 'es': 'Idioma', 'fr': 'Langue', 'de': 'Sprache', 'pt': 'Idioma', 'it': 'Lingua', 'ja': '言語', 'zh': '语言', 'hi': 'भाषा', 'ar': 'اللغة'},
    'beneficiary': {'en': 'Beneficiary', 'es': 'Beneficiario', 'fr': 'Bénéficiaire', 'de': 'Begünstigter', 'pt': 'Beneficiário', 'it': 'Beneficiario', 'ja': '受取人', 'zh': '受益人', 'hi': 'लाभार्थी', 'ar': 'المستفيد'},
    'designees': {'en': 'Designees', 'es': 'Designados', 'fr': 'Désignataires', 'de': 'Benannte', 'pt': 'Designados', 'it': 'Designati', 'ja': '指定先', 'zh': '指定人', 'hi': 'नामित', 'ar': 'المعيَّنون'},
    'comfort': {'en': 'How they comfort', 'es': 'Cómo consuelan', 'fr': 'Comment ils réconfortent', 'de': 'Wie sie trösten', 'pt': 'Como confortam', 'it': 'Come consolano', 'ja': '慰め方', 'zh': '如何安慰', 'hi': 'कैसे सांत्वना देते हैं', 'ar': 'كيف يواسون'},
    'humor': {'en': 'Humor', 'es': 'Humor', 'fr': 'Humour', 'de': 'Humor', 'pt': 'Humor', 'it': 'Umorismo', 'ja': 'ユーモア', 'zh': '幽默', 'hi': 'हास्य', 'ar': 'روح الدعابة'},
    'social_style': {'en': 'Social style', 'es': 'Estilo social', 'fr': 'Style social', 'de': 'Sozialer Stil', 'pt': 'Estilo social', 'it': 'Stile sociale', 'ja': '社交スタイル', 'zh': '社交风格', 'hi': 'सामाजिक शैली', 'ar': 'الأسلوب الاجتماعي'},
    'what_matters': {'en': 'What matters', 'es': 'Lo que importa', 'fr': 'Ce qui compte', 'de': 'Was zählt', 'pt': 'O que importa', 'it': 'Ciò che conta', 'ja': '大切なこと', 'zh': '在乎的事', 'hi': 'क्या मायने रखता है', 'ar': 'ما يهم'},
    'sources': {'en': 'Source profiles, comma-separated', 'es': 'Perfiles fuente, separados por comas', 'fr': 'Profils sources, séparés par des virgules', 'de': 'Quellprofile, kommagetrennt', 'pt': 'Perfis de origem, separados por vírgulas', 'it': 'Profili di origine, separati da virgole', 'ja': '元プロフィール（カンマ区切り）', 'zh': '来源资料，逗号分隔', 'hi': 'स्रोत प्रोफ़ाइल, अल्पविराम से', 'ar': 'الملفات المصدر مفصولة بفواصل'},
    'weight': {'en': 'Share of the blend', 'es': 'Parte de la mezcla', 'fr': 'Part du mélange', 'de': 'Anteil an der Mischung', 'pt': 'Parte da mistura', 'it': 'Quota della miscela', 'ja': 'ブレンドの割合', 'zh': '混合中的份额', 'hi': 'मिश्रण में हिस्सा', 'ar': 'الحصة في المزيج'},
    'aspect': {'en': 'Their aspect', 'es': 'Su rasgo', 'fr': 'Leur aspect', 'de': 'Ihr Aspekt', 'pt': 'O seu aspeto', 'it': 'Il loro aspetto', 'ja': 'その人の要素', 'zh': '他们的特质', 'hi': 'उनका पहलू', 'ar': 'ما يخصّه من سمات'},
    'minutes': {'en': 'Minutes', 'es': 'Minutos', 'fr': 'Minutes', 'de': 'Minuten', 'pt': 'Minutos', 'it': 'Minuti', 'ja': '分', 'zh': '分钟', 'hi': 'मिनट', 'ar': 'الدقائق'},
    'lesson': {'en': 'Step', 'es': 'Paso', 'fr': 'Étape', 'de': 'Schritt', 'pt': 'Passo', 'it': 'Passo', 'ja': 'ステップ', 'zh': '步骤', 'hi': 'चरण', 'ar': 'الخطوة'},
    'position_s': {'en': 'Position, in seconds', 'es': 'Posición, en segundos', 'fr': 'Position, en secondes', 'de': 'Position, in Sekunden', 'pt': 'Posição, em segundos', 'it': 'Posizione, in secondi', 'ja': '位置（秒）', 'zh': '位置（秒）', 'hi': 'स्थिति, सेकंड में', 'ar': 'الموضع بالثواني'},
    'verification_ref': {'en': 'Verification reference', 'es': 'Referencia de verificación', 'fr': 'Référence de vérification', 'de': 'Verifizierungsnachweis', 'pt': 'Referência de verificação', 'it': 'Riferimento di verifica', 'ja': '確認書類の参照', 'zh': '核验凭证', 'hi': 'सत्यापन संदर्भ', 'ar': 'مرجع التحقق'},
    'interactor_id': {'en': 'Visitor', 'es': 'Visitante', 'fr': 'Visiteur', 'de': 'Besucher', 'pt': 'Visitante', 'it': 'Visitatore', 'ja': '訪問者', 'zh': '访客', 'hi': 'आगंतुक', 'ar': 'الزائر'},
    'phases': {'en': 'Phases', 'es': 'Fases', 'fr': 'Phases', 'de': 'Phasen', 'pt': 'Fases', 'it': 'Fasi', 'ja': 'フェーズ', 'zh': '阶段', 'hi': 'चरण', 'ar': 'المراحل'},
    'items': {'en': 'Items', 'es': 'Elementos', 'fr': 'Éléments', 'de': 'Einträge', 'pt': 'Itens', 'it': 'Voci', 'ja': '項目', 'zh': '条目', 'hi': 'आइटम', 'ar': 'العناصر'},
    'text': {'en': 'Text', 'es': 'Texto', 'fr': 'Texte', 'de': 'Text', 'pt': 'Texto', 'it': 'Testo', 'ja': 'テキスト', 'zh': '文本', 'hi': 'पाठ', 'ar': 'النص'},
    'specialist_profile_id': {'en': 'Specialist profile', 'es': 'Perfil especialista', 'fr': 'Profil spécialiste', 'de': 'Spezialistenprofil', 'pt': 'Perfil especialista', 'it': 'Profilo specialista', 'ja': '専門家プロフィール', 'zh': '专家档案', 'hi': 'विशेषज्ञ प्रोफ़ाइल', 'ar': 'ملف المتخصص'},
    'faces': {'en': 'Faces', 'es': 'Caras', 'fr': 'Faces', 'de': 'Ansichten', 'pt': 'Faces', 'it': 'Facce', 'ja': '表示面', 'zh': '显示面', 'hi': 'फ़ेस', 'ar': 'الأوجه'},
    'asset': {'en': 'Portrait asset', 'es': 'Recurso del retrato', 'fr': 'Fichier du portrait', 'de': 'Porträt-Datei', 'pt': 'Ficheiro do retrato', 'it': 'File del ritratto', 'ja': 'ポートレート素材', 'zh': '肖像素材', 'hi': 'चित्र फ़ाइल', 'ar': 'ملف الصورة'},
    'torso': {'en': 'Upper-torso image', 'es': 'Imagen de medio cuerpo', 'fr': 'Image en buste', 'de': 'Oberkörper-Bild', 'pt': 'Imagem de meio corpo', 'it': 'Immagine a mezzo busto', 'ja': '上半身の画像', 'zh': '上半身图像', 'hi': 'ऊपरी धड़ की छवि', 'ar': 'صورة الجذع العلوي'},
    'extra': {'en': 'Extra capture frames', 'es': 'Fotogramas adicionales de la captura', 'fr': 'Images supplémentaires de la capture', 'de': 'Zusätzliche Aufnahmebilder', 'pt': 'Quadros adicionais da captura', 'it': 'Fotogrammi aggiuntivi della cattura', 'ja': '追加のキャプチャ画像', 'zh': '额外的拍摄帧', 'hi': 'अतिरिक्त कैप्चर फ़्रेम', 'ar': 'إطارات التقاط إضافية'},
    'emblem': {'en': 'Field emblem', 'es': 'Emblema de campo', 'fr': 'Emblème de domaine', 'de': 'Fach-Emblem', 'pt': 'Emblema de área', 'it': 'Emblema di settore', 'ja': '分野のエンブレム', 'zh': '领域徽记', 'hi': 'क्षेत्र प्रतीक', 'ar': 'شعار المجال'},
    'surfaces': {'en': 'Surfaces', 'es': 'Superficies', 'fr': 'Surfaces', 'de': 'Oberflächen', 'pt': 'Superfícies', 'it': 'Superfici', 'ja': 'サーフェス', 'zh': '呈现面', 'hi': 'सतहें', 'ar': 'الأسطح'},
    'feature': {'en': 'Feature', 'es': 'Función', 'fr': 'Fonction', 'de': 'Funktion', 'pt': 'Função', 'it': 'Funzione', 'ja': '機能', 'zh': '功能', 'hi': 'सुविधा', 'ar': 'الميزة'},
    'headline': {'en': 'Headline', 'es': 'Titular', 'fr': 'Accroche', 'de': 'Überschrift', 'pt': 'Título', 'it': 'Titolo', 'ja': '見出し', 'zh': '标题', 'hi': 'शीर्षक', 'ar': 'العنوان'},
    'availability': {'en': 'Availability', 'es': 'Disponibilidad', 'fr': 'Disponibilité', 'de': 'Verfügbarkeit', 'pt': 'Disponibilidade', 'it': 'Disponibilità', 'ja': '在庫状況', 'zh': '供货情况', 'hi': 'उपलब्धता', 'ar': 'التوفر'},
    'buyer_id': {'en': 'Buyer', 'es': 'Comprador', 'fr': 'Acheteur', 'de': 'Käufer', 'pt': 'Comprador', 'it': 'Acquirente', 'ja': '購入者', 'zh': '买家', 'hi': 'खरीदार', 'ar': 'المشتري'},
    'offering_id': {'en': 'Offering', 'es': 'Artículo', 'fr': 'Article', 'de': 'Angebot', 'pt': 'Artigo', 'it': 'Articolo', 'ja': '商品', 'zh': '商品', 'hi': 'पेशकश', 'ar': 'المعروض'},
    'party': {'en': 'Party', 'es': 'Parte', 'fr': 'Partie', 'de': 'Partei', 'pt': 'Parte', 'it': 'Parte', 'ja': '当事者', 'zh': '当事方', 'hi': 'पक्ष', 'ar': 'الطرف'},
    'quantity': {'en': 'Quantity', 'es': 'Cantidad', 'fr': 'Quantité', 'de': 'Menge', 'pt': 'Quantidade', 'it': 'Quantità', 'ja': '数量', 'zh': '数量', 'hi': 'मात्रा', 'ar': 'الكمية'},
    'tag': {'en': 'Tag', 'es': 'Etiqueta', 'fr': 'Étiquette', 'de': 'Schlagwort', 'pt': 'Etiqueta', 'it': 'Etichetta', 'ja': 'タグ', 'zh': '标签', 'hi': 'टैग', 'ar': 'الوسم'},
    'accept': {'en': 'Accept', 'es': 'Aceptar', 'fr': 'Accepter', 'de': 'Annehmen', 'pt': 'Aceitar', 'it': 'Accetta', 'ja': '承諾', 'zh': '接受', 'hi': 'स्वीकार करें', 'ar': 'قبول'},
    'ring_id': {'en': 'Bell ring', 'es': 'Toque de timbre', 'fr': 'Coup de sonnette', 'de': 'Klingelzeichen', 'pt': 'Toque de campainha', 'it': 'Squillo del campanello', 'ja': 'ベルの呼び出し', 'zh': '门铃记录', 'hi': 'घंटी की सूचना', 'ar': 'رنّة الجرس'},
    'display_name': {'en': 'Profile name', 'es': 'Nombre del perfil', 'fr': 'Nom du profil', 'de': 'Profilname', 'pt': 'Nome do perfil', 'it': 'Nome del profilo', 'ja': 'プロフィール名', 'zh': '资料名称', 'hi': 'प्रोफ़ाइल नाम', 'ar': 'اسم الملف'},
    'persona': {'en': 'Persona', 'es': 'Persona', 'fr': 'Persona', 'de': 'Persona', 'pt': 'Persona', 'it': 'Persona', 'ja': 'ペルソナ', 'zh': '人设', 'hi': 'व्यक्तित्व', 'ar': 'الشخصية'},
    'email': {'en': 'Email', 'es': 'Correo electrónico', 'fr': 'E-mail', 'de': 'E-Mail', 'pt': 'E-mail', 'it': 'E-mail', 'ja': 'メールアドレス', 'zh': '电子邮箱', 'hi': 'ईमेल', 'ar': 'البريد الإلكتروني'},
    'password': {'en': 'Password', 'es': 'Contraseña', 'fr': 'Mot de passe', 'de': 'Passwort', 'pt': 'Palavra-passe', 'it': 'Password', 'ja': 'パスワード', 'zh': '密码', 'hi': 'पासवर्ड', 'ar': 'كلمة المرور'},
    'birthdate': {'en': 'Date of birth', 'es': 'Fecha de nacimiento', 'fr': 'Date de naissance', 'de': 'Geburtsdatum', 'pt': 'Data de nascimento', 'it': 'Data di nascita', 'ja': '生年月日', 'zh': '出生日期', 'hi': 'जन्म तिथि', 'ar': 'تاريخ الميلاد'},
    'reason': {'en': 'Reason', 'es': 'Motivo', 'fr': 'Motif', 'de': 'Grund', 'pt': 'Motivo', 'it': 'Motivo', 'ja': '理由', 'zh': '原因', 'hi': 'कारण', 'ar': 'السبب'},
    'topic': {'en': 'Topic', 'es': 'Tema', 'fr': 'Sujet', 'de': 'Thema', 'pt': 'Tema', 'it': 'Argomento', 'ja': 'トピック', 'zh': '主题', 'hi': 'विषय', 'ar': 'الموضوع'},
    'content': {'en': 'Content', 'es': 'Contenido', 'fr': 'Contenu', 'de': 'Inhalt', 'pt': 'Conteúdo', 'it': 'Contenuto', 'ja': '内容', 'zh': '内容', 'hi': 'सामग्री', 'ar': 'المحتوى'},
    'message': {'en': 'Message', 'es': 'Mensaje', 'fr': 'Message', 'de': 'Nachricht', 'pt': 'Mensagem', 'it': 'Messaggio', 'ja': 'メッセージ', 'zh': '消息', 'hi': 'संदेश', 'ar': 'الرسالة'},
    'title': {'en': 'Title', 'es': 'Título', 'fr': 'Titre', 'de': 'Titel', 'pt': 'Título', 'it': 'Titolo', 'ja': 'タイトル', 'zh': '标题', 'hi': 'शीर्षक', 'ar': 'العنوان'},
    'purpose': {'en': 'Purpose', 'es': 'Propósito', 'fr': 'Objectif', 'de': 'Zweck', 'pt': 'Finalidade', 'it': 'Scopo', 'ja': '目的', 'zh': '用途', 'hi': 'उद्देश्य', 'ar': 'الغرض'},
    'plan': {'en': 'Plan', 'es': 'Plan', 'fr': 'Formule', 'de': 'Tarif', 'pt': 'Plano', 'it': 'Piano', 'ja': 'プラン', 'zh': '方案', 'hi': 'योजना', 'ar': 'الخطة'},
    'note': {'en': 'Note', 'es': 'Nota', 'fr': 'Note', 'de': 'Notiz', 'pt': 'Nota', 'it': 'Nota', 'ja': 'メモ', 'zh': '备注', 'hi': 'टिप्पणी', 'ar': 'ملاحظة'},
    'objector_ref': {'en': 'Proof reference', 'es': 'Referencia de prueba', 'fr': 'Référence de preuve', 'de': 'Nachweisreferenz', 'pt': 'Referência de prova', 'it': 'Riferimento di prova', 'ja': '証明の参照番号', 'zh': '证明参考号', 'hi': 'प्रमाण संदर्भ', 'ar': 'مرجع الإثبات'},
    'profile_id': {'en': 'Profile id', 'es': 'Id del perfil', 'fr': 'Identifiant du profil', 'de': 'Profil-ID', 'pt': 'Id do perfil', 'it': 'Id del profilo', 'ja': 'プロフィールID', 'zh': '资料 id', 'hi': 'प्रोफ़ाइल आईडी', 'ar': 'معرّف الملف'},
    'price': {'en': 'Price', 'es': 'Precio', 'fr': 'Prix', 'de': 'Preis', 'pt': 'Preço', 'it': 'Prezzo', 'ja': '価格', 'zh': '价格', 'hi': 'मूल्य', 'ar': 'السعر'},
    'currency': {'en': 'Currency', 'es': 'Moneda', 'fr': 'Devise', 'de': 'Währung', 'pt': 'Moeda', 'it': 'Valuta', 'ja': '通貨', 'zh': '货币', 'hi': 'मुद्रा', 'ar': 'العملة'},
    'terms': {'en': 'Terms', 'es': 'Términos', 'fr': 'Conditions', 'de': 'Bedingungen', 'pt': 'Termos', 'it': 'Termini', 'ja': '条件', 'zh': '条款', 'hi': 'शर्तें', 'ar': 'الشروط'},
    'scenario': {'en': 'Scenario', 'es': 'Escenario', 'fr': 'Scénario', 'de': 'Szenario', 'pt': 'Cenário', 'it': 'Scenario', 'ja': 'シナリオ', 'zh': '情景', 'hi': 'परिदृश्य', 'ar': 'السيناريو'},
    'horizon': {'en': 'Time horizon', 'es': 'Horizonte temporal', 'fr': 'Horizon temporel', 'de': 'Zeithorizont', 'pt': 'Horizonte temporal', 'it': 'Orizzonte temporale', 'ja': '期間', 'zh': '时间范围', 'hi': 'समय-सीमा', 'ar': 'الأفق الزمني'},
    'handle': {'en': 'Handle', 'es': 'Identificador', 'fr': 'Identifiant', 'de': 'Kürzel', 'pt': 'Identificador', 'it': 'Handle', 'ja': 'ハンドル名', 'zh': '账号名', 'hi': 'हैंडल', 'ar': 'المعرّف'},
    'goal': {'en': 'Goal', 'es': 'Objetivo', 'fr': 'Objectif', 'de': 'Ziel', 'pt': 'Objetivo', 'it': 'Obiettivo', 'ja': '目標', 'zh': '目标', 'hi': 'लक्ष्य', 'ar': 'الهدف'},
    'name': {'en': 'Name', 'es': 'Nombre', 'fr': 'Nom', 'de': 'Name', 'pt': 'Nome', 'it': 'Nome', 'ja': '名前', 'zh': '名称', 'hi': 'नाम', 'ar': 'الاسم'},
    'about': {'en': 'About', 'es': 'Acerca de', 'fr': 'À propos', 'de': 'Über', 'pt': 'Sobre', 'it': 'Info', 'ja': '自己紹介', 'zh': '关于', 'hi': 'परिचय', 'ar': 'نبذة'},
    'accent': {'en': 'Accent', 'es': 'Acento', 'fr': 'Accent', 'de': 'Akzent', 'pt': 'Realce', 'it': 'Accento', 'ja': 'アクセント', 'zh': '强调色', 'hi': 'उभार रंग', 'ar': 'اللون المميز'},
    'accept_price': {'en': 'Asking price', 'es': 'Precio solicitado', 'fr': 'Prix demandé', 'de': 'Geforderter Preis', 'pt': 'Preço pedido', 'it': 'Prezzo richiesto', 'ja': '希望価格', 'zh': '要价', 'hi': 'मांगी गई कीमत', 'ar': 'السعر المطلوب'},
    'action': {'en': 'Action', 'es': 'Acción', 'fr': 'Action', 'de': 'Aktion', 'pt': 'Ação', 'it': 'Azione', 'ja': 'アクション', 'zh': '操作', 'hi': 'कार्रवाई', 'ar': 'الإجراء'},
    'alias': {'en': 'Alias', 'es': 'Alias', 'fr': 'Alias', 'de': 'Alias', 'pt': 'Alias', 'it': 'Alias', 'ja': 'エイリアス', 'zh': '别名', 'hi': 'उपनाम', 'ar': 'الاسم المستعار'},
    'amount': {'en': 'Amount', 'es': 'Importe', 'fr': 'Montant', 'de': 'Betrag', 'pt': 'Montante', 'it': 'Importo', 'ja': '金額', 'zh': '金额', 'hi': 'राशि', 'ar': 'المبلغ'},
    'answers': {'en': 'Answers', 'es': 'Respuestas', 'fr': 'Réponses', 'de': 'Antworten', 'pt': 'Respostas', 'it': 'Risposte', 'ja': '回答', 'zh': '回答', 'hi': 'उत्तर', 'ar': 'الإجابات'},
    'area': {'en': 'Area', 'es': 'Área', 'fr': 'Domaine', 'de': 'Bereich', 'pt': 'Área', 'it': 'Area', 'ja': '分野', 'zh': '领域', 'hi': 'क्षेत्र', 'ar': 'المجال'},
    'attestor': {'en': 'Attestor', 'es': 'Certificador', 'fr': 'Attestataire', 'de': 'Bestätiger', 'pt': 'Atestador', 'it': 'Attestatore', 'ja': '証明者', 'zh': '证明人', 'hi': 'प्रमाणक', 'ar': 'المُصدِّق'},
    'basis': {'en': 'Basis', 'es': 'Base', 'fr': 'Base', 'de': 'Grundlage', 'pt': 'Base', 'it': 'Base', 'ja': '根拠', 'zh': '依据', 'hi': 'आधार', 'ar': 'الأساس'},
    'blurb': {'en': 'Blurb', 'es': 'Descripción breve', 'fr': 'Description courte', 'de': 'Kurzbeschreibung', 'pt': 'Descrição breve', 'it': 'Descrizione breve', 'ja': '紹介文', 'zh': '简介', 'hi': 'संक्षिप्त विवरण', 'ar': 'وصف موجز'},
    'body': {'en': 'Message', 'es': 'Mensaje', 'fr': 'Message', 'de': 'Nachricht', 'pt': 'Mensagem', 'it': 'Messaggio', 'ja': 'メッセージ', 'zh': '消息', 'hi': 'संदेश', 'ar': 'الرسالة'},
    'borrower_id': {'en': 'Borrower id', 'es': 'Id del prestatario', 'fr': 'Id de l’emprunteur', 'de': 'Ausleiher-ID', 'pt': 'Id do mutuário', 'it': 'Id del mutuatario', 'ja': '借り手ID', 'zh': '借用者 id', 'hi': 'उधारकर्ता आईडी', 'ar': 'معرّف المستعير'},
    'caller_id': {'en': 'Caller id', 'es': 'Id del llamante', 'fr': 'Id de l’appelant', 'de': 'Anrufer-ID', 'pt': 'Id de quem chama', 'it': 'Id del chiamante', 'ja': '発信者ID', 'zh': '来电者 id', 'hi': 'कॉलर आईडी', 'ar': 'معرّف المتصل'},
    'callsign': {'en': 'Callsign', 'es': 'Indicativo', 'fr': 'Indicatif', 'de': 'Rufzeichen', 'pt': 'Indicativo', 'it': 'Nominativo', 'ja': 'コールサイン', 'zh': '呼号', 'hi': 'कॉलसाइन', 'ar': 'رمز النداء'},
    'category': {'en': 'Category', 'es': 'Categoría', 'fr': 'Catégorie', 'de': 'Kategorie', 'pt': 'Categoria', 'it': 'Categoria', 'ja': 'カテゴリー', 'zh': '类别', 'hi': 'श्रेणी', 'ar': 'الفئة'},
    'cause': {'en': 'Cause', 'es': 'Causa', 'fr': 'Cause', 'de': 'Anliegen', 'pt': 'Causa', 'it': 'Causa', 'ja': '目的', 'zh': '事由', 'hi': 'उद्देश्य', 'ar': 'القضية'},
    'channel': {'en': 'Channel', 'es': 'Canal', 'fr': 'Canal', 'de': 'Kanal', 'pt': 'Canal', 'it': 'Canale', 'ja': 'チャンネル', 'zh': '频道', 'hi': 'चैनल', 'ar': 'القناة'},
    'code': {'en': 'Code', 'es': 'Código', 'fr': 'Code', 'de': 'Code', 'pt': 'Código', 'it': 'Codice', 'ja': 'コード', 'zh': '验证码', 'hi': 'कोड', 'ar': 'الرمز'},
    'consent': {'en': 'Consent', 'es': 'Consentimiento', 'fr': 'Consentement', 'de': 'Einwilligung', 'pt': 'Consentimento', 'it': 'Consenso', 'ja': '同意', 'zh': '同意', 'hi': 'सहमति', 'ar': 'الموافقة'},
    'contact': {'en': 'Contact', 'es': 'Contacto', 'fr': 'Contact', 'de': 'Kontakt', 'pt': 'Contacto', 'it': 'Contatto', 'ja': '連絡先', 'zh': '联系方式', 'hi': 'संपर्क', 'ar': 'جهة الاتصال'},
    'criteria': {'en': 'Criteria', 'es': 'Criterios', 'fr': 'Critères', 'de': 'Kriterien', 'pt': 'Critérios', 'it': 'Criteri', 'ja': '条件', 'zh': '条件', 'hi': 'मानदंड', 'ar': 'المعايير'},
    'desk_id': {'en': 'Desk id', 'es': 'Id del mostrador', 'fr': 'Id du comptoir', 'de': 'Schalter-ID', 'pt': 'Id do balcão', 'it': 'Id dello sportello', 'ja': 'デスクID', 'zh': '服务台 id', 'hi': 'डेस्क आईडी', 'ar': 'معرّف المكتب'},
    'direction': {'en': 'Direction', 'es': 'Sentido', 'fr': 'Sens', 'de': 'Richtung', 'pt': 'Direção', 'it': 'Direzione', 'ja': '方向', 'zh': '方向', 'hi': 'दिशा', 'ar': 'الاتجاه'},
    'display_text': {'en': 'Displayed text', 'es': 'Texto mostrado', 'fr': 'Texte affiché', 'de': 'Angezeigter Text', 'pt': 'Texto exibido', 'it': 'Testo mostrato', 'ja': '表示テキスト', 'zh': '显示文本', 'hi': 'दिखाया गया पाठ', 'ar': 'النص المعروض'},
    'document': {'en': 'Document', 'es': 'Documento', 'fr': 'Document', 'de': 'Dokument', 'pt': 'Documento', 'it': 'Documento', 'ja': '文書', 'zh': '文件', 'hi': 'दस्तावेज़', 'ar': 'المستند'},
    'domain': {'en': 'Domain', 'es': 'Dominio', 'fr': 'Domaine', 'de': 'Domäne', 'pt': 'Domínio', 'it': 'Dominio', 'ja': '領域', 'zh': '领域', 'hi': 'डोमेन', 'ar': 'المجال'},
    'fee': {'en': 'Fee', 'es': 'Tarifa', 'fr': 'Frais', 'de': 'Gebühr', 'pt': 'Taxa', 'it': 'Tariffa', 'ja': '手数料', 'zh': '费用', 'hi': 'शुल्क', 'ar': 'الرسوم'},
    'finish': {'en': 'Finish', 'es': 'Acabado', 'fr': 'Finition', 'de': 'Oberfläche', 'pt': 'Acabamento', 'it': 'Finitura', 'ja': '仕上げ', 'zh': '外观', 'hi': 'फ़िनिश', 'ar': 'اللمسة النهائية'},
    'from_department': {'en': 'From department', 'es': 'Desde el departamento', 'fr': 'Depuis le service', 'de': 'Von der Abteilung', 'pt': 'Do departamento', 'it': 'Dal reparto', 'ja': '送り元の部門', 'zh': '来自部门', 'hi': 'किस विभाग से', 'ar': 'من القسم'},
    'game': {'en': 'Game', 'es': 'Juego', 'fr': 'Jeu', 'de': 'Spiel', 'pt': 'Jogo', 'it': 'Gioco', 'ja': 'ゲーム', 'zh': '游戏', 'hi': 'खेल', 'ar': 'اللعبة'},
    'guest_id': {'en': 'Guest id', 'es': 'Id del invitado', 'fr': 'Id de l’invité', 'de': 'Gast-ID', 'pt': 'Id do convidado', 'it': 'Id dell’ospite', 'ja': 'ゲストID', 'zh': '访客 id', 'hi': 'अतिथि आईडी', 'ar': 'معرّف الضيف'},
    'has_llm': {'en': 'Has an LLM', 'es': 'Tiene LLM', 'fr': 'Avec LLM', 'de': 'Mit LLM', 'pt': 'Tem LLM', 'it': 'Con LLM', 'ja': 'LLMあり', 'zh': '带 LLM', 'hi': 'LLM सहित', 'ar': 'مع LLM'},
    'host': {'en': 'Host', 'es': 'Servidor', 'fr': 'Hôte', 'de': 'Host', 'pt': 'Servidor', 'it': 'Host', 'ja': 'ホスト', 'zh': '主机', 'hi': 'होस्ट', 'ar': 'المضيف'},
    'html': {'en': 'HTML', 'es': 'HTML', 'fr': 'HTML', 'de': 'HTML', 'pt': 'HTML', 'it': 'HTML', 'ja': 'HTML', 'zh': 'HTML', 'hi': 'HTML', 'ar': 'HTML'},
    'id': {'en': 'Id', 'es': 'Id', 'fr': 'Id', 'de': 'ID', 'pt': 'Id', 'it': 'Id', 'ja': 'ID', 'zh': 'ID', 'hi': 'आईडी', 'ar': 'المعرّف'},
    'include_remote': {'en': 'Include remote', 'es': 'Incluir remotos', 'fr': 'Inclure à distance', 'de': 'Remote einbeziehen', 'pt': 'Incluir remotos', 'it': 'Includi remoti', 'ja': 'リモートを含む', 'zh': '包含远程', 'hi': 'रिमोट शामिल करें', 'ar': 'تضمين البعيد'},
    'industry': {'en': 'Industry', 'es': 'Sector', 'fr': 'Secteur', 'de': 'Branche', 'pt': 'Setor', 'it': 'Settore', 'ja': '業界', 'zh': '行业', 'hi': 'उद्योग', 'ar': 'القطاع'},
    'input': {'en': 'Input', 'es': 'Entrada', 'fr': 'Entrée', 'de': 'Eingabe', 'pt': 'Entrada', 'it': 'Input', 'ja': '入力', 'zh': '输入', 'hi': 'इनपुट', 'ar': 'الإدخال'},
    'keep': {'en': 'Keep', 'es': 'Conservar', 'fr': 'Conserver', 'de': 'Behalten', 'pt': 'Manter', 'it': 'Mantieni', 'ja': '保持', 'zh': '保留', 'hi': 'रखें', 'ar': 'الاحتفاظ'},
    'kind': {'en': 'Kind', 'es': 'Tipo', 'fr': 'Type', 'de': 'Art', 'pt': 'Tipo', 'it': 'Tipo', 'ja': '種類', 'zh': '类型', 'hi': 'प्रकार', 'ar': 'النوع'},
    'label': {'en': 'Label', 'es': 'Etiqueta', 'fr': 'Libellé', 'de': 'Bezeichnung', 'pt': 'Etiqueta', 'it': 'Etichetta', 'ja': 'ラベル', 'zh': '标签', 'hi': 'लेबल', 'ar': 'التسمية'},
    'language': {'en': 'Language', 'es': 'Idioma', 'fr': 'Langue', 'de': 'Sprache', 'pt': 'Idioma', 'it': 'Lingua', 'ja': '言語', 'zh': '语言', 'hi': 'भाषा', 'ar': 'اللغة'},
    'layout': {'en': 'Layout', 'es': 'Diseño', 'fr': 'Mise en page', 'de': 'Layout', 'pt': 'Esquema', 'it': 'Layout', 'ja': 'レイアウト', 'zh': '布局', 'hi': 'लेआउट', 'ar': 'التخطيط'},
    'level': {'en': 'Level', 'es': 'Nivel', 'fr': 'Niveau', 'de': 'Stufe', 'pt': 'Nível', 'it': 'Livello', 'ja': 'レベル', 'zh': '级别', 'hi': 'स्तर', 'ar': 'المستوى'},
    'links': {'en': 'Links', 'es': 'Enlaces', 'fr': 'Liens', 'de': 'Links', 'pt': 'Ligações', 'it': 'Collegamenti', 'ja': 'リンク', 'zh': '链接', 'hi': 'लिंक', 'ar': 'الروابط'},
    'locality': {'en': 'Locality', 'es': 'Localidad', 'fr': 'Localité', 'de': 'Ort', 'pt': 'Localidade', 'it': 'Località', 'ja': '地域', 'zh': '地区', 'hi': 'इलाक़ा', 'ar': 'المنطقة'},
    'location': {'en': 'Location', 'es': 'Ubicación', 'fr': 'Lieu', 'de': 'Standort', 'pt': 'Localização', 'it': 'Posizione', 'ja': '場所', 'zh': '位置', 'hi': 'स्थान', 'ar': 'الموقع'},
    'mark': {'en': 'Mark', 'es': 'Marca', 'fr': 'Marque', 'de': 'Zeichen', 'pt': 'Marca', 'it': 'Marchio', 'ja': 'マーク', 'zh': '标记', 'hi': 'चिह्न', 'ar': 'العلامة'},
    'meaning': {'en': 'Meaning', 'es': 'Significado', 'fr': 'Signification', 'de': 'Bedeutung', 'pt': 'Significado', 'it': 'Significato', 'ja': '意味', 'zh': '含义', 'hi': 'अर्थ', 'ar': 'المعنى'},
    'member_id': {'en': 'Member id', 'es': 'Id del miembro', 'fr': 'Id du membre', 'de': 'Mitglieds-ID', 'pt': 'Id do membro', 'it': 'Id del membro', 'ja': 'メンバーID', 'zh': '成员 id', 'hi': 'सदस्य आईडी', 'ar': 'معرّف العضو'},
    'member_kind': {'en': 'Member kind', 'es': 'Tipo de miembro', 'fr': 'Type de membre', 'de': 'Mitgliedsart', 'pt': 'Tipo de membro', 'it': 'Tipo di membro', 'ja': 'メンバー種別', 'zh': '成员类型', 'hi': 'सदस्य प्रकार', 'ar': 'نوع العضو'},
    'method': {'en': 'Method', 'es': 'Método', 'fr': 'Méthode', 'de': 'Methode', 'pt': 'Método', 'it': 'Metodo', 'ja': '方法', 'zh': '方式', 'hi': 'तरीका', 'ar': 'الطريقة'},
    'mode': {'en': 'Mode', 'es': 'Modo', 'fr': 'Mode', 'de': 'Modus', 'pt': 'Modo', 'it': 'Modalità', 'ja': 'モード', 'zh': '模式', 'hi': 'मोड', 'ar': 'الوضع'},
    'model': {'en': 'Model', 'es': 'Modelo', 'fr': 'Modèle', 'de': 'Modell', 'pt': 'Modelo', 'it': 'Modello', 'ja': 'モデル', 'zh': '模型', 'hi': 'मॉडल', 'ar': 'النموذج'},
    'moment': {'en': 'Moment', 'es': 'Momento', 'fr': 'Moment', 'de': 'Moment', 'pt': 'Momento', 'it': 'Momento', 'ja': '瞬間', 'zh': '时刻', 'hi': 'क्षण', 'ar': 'اللحظة'},
    'new_password': {'en': 'New password', 'es': 'Nueva contraseña', 'fr': 'Nouveau mot de passe', 'de': 'Neues Passwort', 'pt': 'Nova palavra-passe', 'it': 'Nuova password', 'ja': '新しいパスワード', 'zh': '新密码', 'hi': 'नया पासवर्ड', 'ar': 'كلمة المرور الجديدة'},
    'objects': {'en': 'Objects', 'es': 'Objetos', 'fr': 'Objets', 'de': 'Objekte', 'pt': 'Objetos', 'it': 'Oggetti', 'ja': 'オブジェクト', 'zh': '对象', 'hi': 'वस्तुएँ', 'ar': 'الكائنات'},
    'org': {'en': 'Organization', 'es': 'Organización', 'fr': 'Organisation', 'de': 'Organisation', 'pt': 'Organização', 'it': 'Organizzazione', 'ja': '組織', 'zh': '组织', 'hi': 'संगठन', 'ar': 'المنظمة'},
    'owner_id': {'en': 'Owner id', 'es': 'Id del propietario', 'fr': 'Id du propriétaire', 'de': 'Inhaber-ID', 'pt': 'Id do proprietário', 'it': 'Id del proprietario', 'ja': 'オーナーID', 'zh': '所有者 id', 'hi': 'स्वामी आईडी', 'ar': 'معرّف المالك'},
    'period': {'en': 'Period', 'es': 'Periodo', 'fr': 'Période', 'de': 'Zeitraum', 'pt': 'Período', 'it': 'Periodo', 'ja': '期間', 'zh': '周期', 'hi': 'अवधि', 'ar': 'الفترة'},
    'platform': {'en': 'Platform', 'es': 'Plataforma', 'fr': 'Plateforme', 'de': 'Plattform', 'pt': 'Plataforma', 'it': 'Piattaforma', 'ja': 'プラットフォーム', 'zh': '平台', 'hi': 'प्लेटफ़ॉर्म', 'ar': 'المنصة'},
    'port': {'en': 'Port', 'es': 'Puerto', 'fr': 'Port', 'de': 'Port', 'pt': 'Porta', 'it': 'Porta', 'ja': 'ポート', 'zh': '端口', 'hi': 'पोर्ट', 'ar': 'المنفذ'},
    'post_id': {'en': 'Post id', 'es': 'Id de la publicación', 'fr': 'Id de la publication', 'de': 'Beitrags-ID', 'pt': 'Id da publicação', 'it': 'Id del post', 'ja': '投稿ID', 'zh': '帖子 id', 'hi': 'पोस्ट आईडी', 'ar': 'معرّف المنشور'},
    'proofing_attestor': {'en': 'Proofing attestor', 'es': 'Certificador de la verificación', 'fr': 'Attestataire de la vérification', 'de': 'Bestätiger der Prüfung', 'pt': 'Atestador da verificação', 'it': 'Attestatore della verifica', 'ja': '検証の証明者', 'zh': '核验证明人', 'hi': 'सत्यापन प्रमाणक', 'ar': 'مُصدِّق التحقق'},
    'proofing_level': {'en': 'Proofing level', 'es': 'Nivel de verificación', 'fr': 'Niveau de vérification', 'de': 'Prüfstufe', 'pt': 'Nível de verificação', 'it': 'Livello di verifica', 'ja': '検証レベル', 'zh': '核验级别', 'hi': 'सत्यापन स्तर', 'ar': 'مستوى التحقق'},
    'provider_id': {'en': 'Provider id', 'es': 'Id del proveedor', 'fr': 'Id du fournisseur', 'de': 'Anbieter-ID', 'pt': 'Id do fornecedor', 'it': 'Id del fornitore', 'ja': 'プロバイダーID', 'zh': '提供方 id', 'hi': 'प्रदाता आईडी', 'ar': 'معرّف المزوّد'},
    'provider_name': {'en': 'Provider name', 'es': 'Nombre del proveedor', 'fr': 'Nom du fournisseur', 'de': 'Anbietername', 'pt': 'Nome do fornecedor', 'it': 'Nome del fornitore', 'ja': 'プロバイダー名', 'zh': '提供方名称', 'hi': 'प्रदाता का नाम', 'ar': 'اسم المزوّد'},
    'public_url': {'en': 'Public URL', 'es': 'URL pública', 'fr': 'URL publique', 'de': 'Öffentliche URL', 'pt': 'URL pública', 'it': 'URL pubblico', 'ja': '公開URL', 'zh': '公开 URL', 'hi': 'सार्वजनिक URL', 'ar': 'عنوان URL العام'},
    'question': {'en': 'Question', 'es': 'Pregunta', 'fr': 'Question', 'de': 'Frage', 'pt': 'Pergunta', 'it': 'Domanda', 'ja': '質問', 'zh': '问题', 'hi': 'प्रश्न', 'ar': 'السؤال'},
    'quiet_end': {'en': 'Quiet hours end', 'es': 'Fin de las horas de silencio', 'fr': 'Fin des heures calmes', 'de': 'Ende der Ruhezeit', 'pt': 'Fim das horas de silêncio', 'it': 'Fine delle ore di silenzio', 'ja': '静かな時間の終了', 'zh': '免打扰结束', 'hi': 'शांत समय की समाप्ति', 'ar': 'نهاية ساعات الهدوء'},
    'quiet_start': {'en': 'Quiet hours start', 'es': 'Inicio de las horas de silencio', 'fr': 'Début des heures calmes', 'de': 'Beginn der Ruhezeit', 'pt': 'Início das horas de silêncio', 'it': 'Inizio delle ore di silenzio', 'ja': '静かな時間の開始', 'zh': '免打扰开始', 'hi': 'शांत समय की शुरुआत', 'ar': 'بداية ساعات الهدوء'},
    'rating': {'en': 'Rating', 'es': 'Valoración', 'fr': 'Note', 'de': 'Bewertung', 'pt': 'Avaliação', 'it': 'Valutazione', 'ja': '評価', 'zh': '评分', 'hi': 'रेटिंग', 'ar': 'التقييم'},
    'ref': {'en': 'Reference', 'es': 'Referencia', 'fr': 'Référence', 'de': 'Referenz', 'pt': 'Referência', 'it': 'Riferimento', 'ja': '参照', 'zh': '引用', 'hi': 'संदर्भ', 'ar': 'المرجع'},
    'region': {'en': 'Region', 'es': 'Región', 'fr': 'Région', 'de': 'Region', 'pt': 'Região', 'it': 'Regione', 'ja': '地方', 'zh': '区域', 'hi': 'क्षेत्र', 'ar': 'الإقليم'},
    'relationship_type': {'en': 'Relationship type', 'es': 'Tipo de relación', 'fr': 'Type de relation', 'de': 'Beziehungsart', 'pt': 'Tipo de relação', 'it': 'Tipo di relazione', 'ja': '関係の種類', 'zh': '关系类型', 'hi': 'रिश्ते का प्रकार', 'ar': 'نوع العلاقة'},
    'remote': {'en': 'Remote', 'es': 'Remoto', 'fr': 'À distance', 'de': 'Remote', 'pt': 'Remoto', 'it': 'Da remoto', 'ja': 'リモート', 'zh': '远程', 'hi': 'रिमोट', 'ar': 'عن بُعد'},
    'role': {'en': 'Role', 'es': 'Rol', 'fr': 'Rôle', 'de': 'Rolle', 'pt': 'Função', 'it': 'Ruolo', 'ja': '役割', 'zh': '角色', 'hi': 'भूमिका', 'ar': 'الدور'},
    'scope': {'en': 'Scope', 'es': 'Alcance', 'fr': 'Périmètre', 'de': 'Umfang', 'pt': 'Âmbito', 'it': 'Ambito', 'ja': '範囲', 'zh': '范围', 'hi': 'दायरा', 'ar': 'النطاق'},
    'seconds': {'en': 'Seconds', 'es': 'Segundos', 'fr': 'Secondes', 'de': 'Sekunden', 'pt': 'Segundos', 'it': 'Secondi', 'ja': '秒', 'zh': '秒', 'hi': 'सेकंड', 'ar': 'الثواني'},
    'sender': {'en': 'Sender', 'es': 'Remitente', 'fr': 'Expéditeur', 'de': 'Absender', 'pt': 'Remetente', 'it': 'Mittente', 'ja': '送信者', 'zh': '发件人', 'hi': 'प्रेषक', 'ar': 'المرسِل'},
    'share': {'en': 'Share', 'es': 'Parte', 'fr': 'Part', 'de': 'Anteil', 'pt': 'Parte', 'it': 'Quota', 'ja': '割合', 'zh': '份额', 'hi': 'हिस्सा', 'ar': 'الحصة'},
    'size': {'en': 'Size', 'es': 'Tamaño', 'fr': 'Taille', 'de': 'Größe', 'pt': 'Tamanho', 'it': 'Dimensione', 'ja': 'サイズ', 'zh': '大小', 'hi': 'आकार', 'ar': 'الحجم'},
    'skill_kind': {'en': 'Skill kind', 'es': 'Tipo de habilidad', 'fr': 'Type de compétence', 'de': 'Art der Fähigkeit', 'pt': 'Tipo de competência', 'it': 'Tipo di abilità', 'ja': 'スキル種別', 'zh': '技能类型', 'hi': 'कौशल प्रकार', 'ar': 'نوع المهارة'},
    'skill_ref': {'en': 'Skill reference', 'es': 'Referencia de la habilidad', 'fr': 'Référence de la compétence', 'de': 'Fähigkeits-Referenz', 'pt': 'Referência da competência', 'it': 'Riferimento dell’abilità', 'ja': 'スキル参照', 'zh': '技能引用', 'hi': 'कौशल संदर्भ', 'ar': 'مرجع المهارة'},
    'source': {'en': 'Source', 'es': 'Fuente', 'fr': 'Source', 'de': 'Quelle', 'pt': 'Fonte', 'it': 'Fonte', 'ja': 'ソース', 'zh': '来源', 'hi': 'स्रोत', 'ar': 'المصدر'},
    'stock': {'en': 'Stock', 'es': 'Existencias', 'fr': 'Stock', 'de': 'Bestand', 'pt': 'Stock', 'it': 'Scorte', 'ja': '在庫', 'zh': '库存', 'hi': 'स्टॉक', 'ar': 'المخزون'},
    'subject': {'en': 'Subject', 'es': 'Asunto', 'fr': 'Sujet', 'de': 'Betreff', 'pt': 'Assunto', 'it': 'Oggetto', 'ja': '件名', 'zh': '主题', 'hi': 'विषय', 'ar': 'الموضوع'},
    'surface': {'en': 'Surface', 'es': 'Superficie', 'fr': 'Surface', 'de': 'Fläche', 'pt': 'Superfície', 'it': 'Superficie', 'ja': 'サーフェス', 'zh': '表面', 'hi': 'सतह', 'ar': 'السطح'},
    'surface_id': {'en': 'Surface id', 'es': 'Id de la superficie', 'fr': 'Id de la surface', 'de': 'Flächen-ID', 'pt': 'Id da superfície', 'it': 'Id della superficie', 'ja': 'サーフェスID', 'zh': '表面 id', 'hi': 'सतह आईडी', 'ar': 'معرّف السطح'},
    'tagline': {'en': 'Tagline', 'es': 'Lema', 'fr': 'Slogan', 'de': 'Slogan', 'pt': 'Slogan', 'it': 'Slogan', 'ja': 'キャッチフレーズ', 'zh': '标语', 'hi': 'टैगलाइन', 'ar': 'الشعار'},
    'tags': {'en': 'Tags', 'es': 'Etiquetas', 'fr': 'Mots-clés', 'de': 'Schlagwörter', 'pt': 'Etiquetas', 'it': 'Tag', 'ja': 'タグ', 'zh': '标签', 'hi': 'टैग', 'ar': 'الوسوم'},
    'target': {'en': 'Target', 'es': 'Objetivo', 'fr': 'Cible', 'de': 'Ziel', 'pt': 'Alvo', 'it': 'Obiettivo', 'ja': 'ターゲット', 'zh': '目标', 'hi': 'लक्ष्य', 'ar': 'الهدف'},
    'theme': {'en': 'Theme', 'es': 'Tema', 'fr': 'Thème', 'de': 'Design', 'pt': 'Tema', 'it': 'Tema', 'ja': 'テーマ', 'zh': '主题', 'hi': 'थीम', 'ar': 'السمة'},
    'tier': {'en': 'Tier', 'es': 'Nivel', 'fr': 'Palier', 'de': 'Stufe', 'pt': 'Escalão', 'it': 'Livello', 'ja': 'ティア', 'zh': '层级', 'hi': 'टियर', 'ar': 'المستوى'},
    'to': {'en': 'To', 'es': 'Para', 'fr': 'À', 'de': 'An', 'pt': 'Para', 'it': 'A', 'ja': '宛先', 'zh': '发给', 'hi': 'किसे', 'ar': 'إلى'},
    'tone': {'en': 'Tone', 'es': 'Tono', 'fr': 'Ton', 'de': 'Ton', 'pt': 'Tom', 'it': 'Tono', 'ja': 'トーン', 'zh': '语气', 'hi': 'लहजा', 'ar': 'النبرة'},
    'top_friends': {'en': 'Top friends', 'es': 'Mejores amigos', 'fr': 'Meilleurs amis', 'de': 'Beste Freunde', 'pt': 'Melhores amigos', 'it': 'Migliori amici', 'ja': 'トップフレンド', 'zh': '挚友', 'hi': 'खास दोस्त', 'ar': 'أفضل الأصدقاء'},
    'trade': {'en': 'Trade', 'es': 'Oficio', 'fr': 'Métier', 'de': 'Gewerk', 'pt': 'Ofício', 'it': 'Mestiere', 'ja': '職種', 'zh': '手艺', 'hi': 'पेशा', 'ar': 'الحرفة'},
    'username': {'en': 'Username', 'es': 'Nombre de usuario', 'fr': 'Nom d’utilisateur', 'de': 'Benutzername', 'pt': 'Nome de utilizador', 'it': 'Nome utente', 'ja': 'ユーザー名', 'zh': '用户名', 'hi': 'उपयोगकर्ता नाम', 'ar': 'اسم المستخدم'},
    'venue': {'en': 'Venue', 'es': 'Lugar', 'fr': 'Lieu', 'de': 'Veranstaltungsort', 'pt': 'Local', 'it': 'Luogo', 'ja': '会場', 'zh': '场地', 'hi': 'स्थल', 'ar': 'المكان'},
    'video_title': {'en': 'Video title', 'es': 'Título del vídeo', 'fr': 'Titre de la vidéo', 'de': 'Videotitel', 'pt': 'Título do vídeo', 'it': 'Titolo del video', 'ja': '動画タイトル', 'zh': '视频标题', 'hi': 'वीडियो शीर्षक', 'ar': 'عنوان الفيديو'},
    'video_url': {'en': 'Video URL', 'es': 'URL del vídeo', 'fr': 'URL de la vidéo', 'de': 'Video-URL', 'pt': 'URL do vídeo', 'it': 'URL del video', 'ja': '動画URL', 'zh': '视频 URL', 'hi': 'वीडियो URL', 'ar': 'عنوان URL للفيديو'},
    'viewer_id': {'en': 'Viewer id', 'es': 'Id del espectador', 'fr': 'Id du spectateur', 'de': 'Zuschauer-ID', 'pt': 'Id do espectador', 'it': 'Id dello spettatore', 'ja': '視聴者ID', 'zh': '观看者 id', 'hi': 'दर्शक आईडी', 'ar': 'معرّف المشاهد'},
    'viewer_kind': {'en': 'Viewer kind', 'es': 'Tipo de espectador', 'fr': 'Type de spectateur', 'de': 'Zuschauerart', 'pt': 'Tipo de espectador', 'it': 'Tipo di spettatore', 'ja': '視聴者種別', 'zh': '观看者类型', 'hi': 'दर्शक प्रकार', 'ar': 'نوع المشاهد'},
    'what': {'en': 'What', 'es': 'Qué', 'fr': 'Quoi', 'de': 'Was', 'pt': 'O quê', 'it': 'Cosa', 'ja': '内容', 'zh': '内容', 'hi': 'क्या', 'ar': 'ماذا'},
    'work': {'en': 'Work', 'es': 'Trabajo', 'fr': 'Travail', 'de': 'Arbeit', 'pt': 'Trabalho', 'it': 'Lavoro', 'ja': '作業', 'zh': '工作', 'hi': 'काम', 'ar': 'العمل'},    'signature_id': {'en': 'Signature id', 'es': 'Id de firma', 'fr': 'Id de signature', 'de': 'Signatur-Id', 'pt': 'Id de assinatura', 'it': 'Id di firma', 'ja': '署名ID', 'zh': '签名ID', 'hi': 'हस्ताक्षर आईडी', 'ar': 'معرّف التوقيع'},

}


def field_label(name: str, language: str) -> str:
    """The label a person sees beside this field, or its identifier.

    Falls back to the identifier rather than to English: an unmapped field is
    a name the reader was already being shown, and inventing a word for it
    would be worse than the identifier they can at least match to the form.
    """
    row = _FIELD_LABELS.get(name)
    if not row:
        return name
    return row.get(language) or row.get(DEFAULT) or name


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

    **Since 0.40.8 the fields a person types into a form carry the label the
    form shows** — `_FIELD_LABELS` above, ported from the console's own labels
    where one exists so the sentence and the form agree by construction. A
    field with no row keeps its identifier, which is what the paragraph above
    describes and is still the right answer for it: an identifier the reader
    can match to the form beats a word invented for them. The unmapped ones are
    recorded in `tests/field_labels_unmapped.txt` and that record only
    shrinks.

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
                        else field_label(p, language) for p in where)
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
