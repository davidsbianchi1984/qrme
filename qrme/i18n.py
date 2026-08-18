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
#: The one sentence a person can meet on any route in this product,
#: because it is the answer to a route that failed. Named here so
#: `_REFUSALS` can carry it and the middleware can look it up — a
#: refusal built inline is a refusal in English.
SERVER_ERROR = ("Something went wrong on our side. "
                "Nothing you sent was recorded.")



#: What each way a widget can fail says to the person who wrote it.
#:
#: The runner answers in keys — `widgets.timeout`, `widgets.no_netns` — so
#: that nothing builds a sentence at the point of failure. These are the
#: English, and `_REFUSALS` carries them into the other nine like every
#: other refusal this product makes.
STUDIO_REFUSALS: dict[str, str] = {
    "widgets.unnamed": "give this widget a name",
    "widgets.no_such": "no such widget",
    "widgets.too_long": "this widget is longer than the editor will store",
    "widgets.too_many": "you are holding as many widgets as one profile may",
    "widgets.threw": "your widget stopped on an error",
    "widgets.timeout": "your widget ran longer than it is allowed to",
    "widgets.killed": "your widget was stopped for using more than it is allowed",
    "widgets.no_answer": "your widget finished without returning anything",
    "widgets.no_unshare": "this deployment cannot build the box a widget runs "
                          "in, so nothing will run here",
    "widgets.no_netns": "this deployment cannot cut the network for a widget, "
                        "so nothing will run here",
    "widgets.no_node": "this deployment has no interpreter for widgets, so "
                       "nothing will run here",
    "widgets.node_too_old": "this deployment's interpreter is too old to "
                            "hold a widget in, so nothing will run here",
    "widgets.no_rlimits": "this deployment cannot cap what a widget may use, "
                          "so nothing will run here",
    # The agent that writes them. Its wrong answers are a genre of their own:
    # every one of these is the model failing, not the person, and each says
    # so rather than reading as something they did.
    "agent.said_nothing": "say what you would like changed",
    "agent.model_silent": "the model did not answer",
    "agent.unreadable_call": "the model's answer could not be read as a request",
    "agent.unknown_tool": "the model asked for something it does not have",
    "agent.missing_argument": "the model left out something the step needs",
    "agent.field_not_yours": "the model tried to change something that step "
                             "does not reach",
    "agent.not_asked": "that step runs inside a turn and was not one to "
                       "confirm",
    "agent.tool_failed": "that step did not finish",
    "agent.too_many_steps": "this went on longer than one turn allows — ask "
                            "again for something narrower",
}

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


_PUBLIC['\u2014 cut off here, not finished. Ask me to continue.'] = {
    'es': '\u2014 cortado aqu\u00ed, no terminado. P\u00eddeme que siga.',
    'fr': "\u2014 coup\u00e9 ici, pas fini. Demandez-moi de continuer.",
    'de': '\u2014 hier abgeschnitten, nicht fertig. Bitte mich weiterzumachen.',
    'pt': '\u2014 cortado aqui, n\u00e3o terminado. Pe\u00e7a-me para continuar.',
    'it': '\u2014 troncato qui, non finito. Chiedimi di continuare.',
    'ja': '\u2014 ここで切れています。終わったのではありません。続きを求めてください。',
    'zh': '\u2014 到这里被截断了，不是说完了。让我继续。',
    'hi': '\u2014 यहाँ कट गया, समाप्त नहीं हुआ। मुझसे जारी रखने को कहें।',
    'ar': '\u2014 انقطع هنا ولم ينتهِ. اطلب مني المتابعة.',
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


def raised(exc: Exception):
    """The sentence an exception was raised with, in the shape it was raised.

    `str(exc)` looks equivalent and is not. `str()` on a `str` subclass returns
    a plain `str`, so a `Templated` carried by a domain exception and passed on
    as `HTTPException(403, str(exc))` reaches the handler having forgotten its
    template — English, silently, and indistinguishable from a sentence nobody
    has translated yet.

        asked     is the refusal translated
        mattered  did it still know how it was built when it got there

    The escalation router did exactly that with `DIALER_SEALED`, which is the
    sentence a person reads while something is going wrong. A route that
    refuses with a template uses this instead.
    """
    return exc.args[0] if exc.args else ""


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
NO_SUCH_MATTER = "no such matter"
MATTER_NEEDS_WORDS = "say what is wrong, in your own words"
MATTER_NEEDS_AN_ANSWER = "say what settled it"

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


#: The two sentences a person reads when they pressed for emergency services
#: and this deployment did not place a call. They are templated because the
#: number differs per deployment — and the slot is a **phone number**, not
#: prose, so translating the frame around it is safe. The rule that keeps a
#: `Templated` honest (a translated frame around an English slot reads as a
#: bug) is about slots holding sentences; `999` is `999` in every language.
#:
#: These are the most important sentences this product can say. Somebody is
#: reading them while something is going wrong, so they are translated rather
#: than recorded — and neither of them claims a call was placed.
DIALER_SEALED = ("the dialer is sealed on this deployment and no call was "
                 "placed — dial {number} yourself, now")
DIALER_NO_CARRIER = ("the dialer is unsealed but no carrier is configured, so "
                     "no call was placed — dial {number} yourself, now")

#: Nobody gave the agent this privilege. The slot holds the thing itself — the
#: sentence the person would use for it — drawn from the closed vocabulary in
#: `qrme/privileges.py`, so it arrives translated rather than as `run_jobs` in
#: the middle of a Portuguese sentence.
PRIVILEGE_NOT_GIVEN = ("this profile's agent has not been given permission to "
                       "{doing} — turn it on under what the agent may do, "
                       "where it says what it will keep")

#: Every template this module offers. Derived from the table below rather than
#: repeated, so a template with no translations is impossible by construction.
TEMPLATES = (MUST_BE_ONE_OF, UNKNOWN_SURFACE, OBJECTION_ALREADY,
             MESSAGE_ALREADY, PROFILE_ALREADY, NOT_A_MEMORIAL, PLAN_GATE,
             DIALER_SEALED, DIALER_NO_CARRIER, PRIVILEGE_NOT_GIVEN)

_TEMPLATES: dict[str, dict[str, str]] = {
    PRIVILEGE_NOT_GIVEN: {
        'es': 'el agente de este perfil no tiene permiso para {doing}: '
              'actívalo en lo que el agente puede hacer, donde dice qué '
              'guardará',
        'fr': "l'agent de ce profil n'a pas la permission de {doing} — "
              "activez-la dans ce que l'agent peut faire, où il est dit ce "
              "qu'il conservera",
        'de': 'der Agent dieses Profils hat keine Erlaubnis, {doing} — '
              'schalte sie unter „was der Agent darf" frei, wo steht, was er '
              'behält',
        'pt': 'o agente deste perfil não tem permissão para {doing} — '
              'ative-a em o que o agente pode fazer, onde diz o que ele '
              'guardará',
        'it': "l'agente di questo profilo non ha il permesso di {doing}: "
              "attivalo in ciò che l'agente può fare, dove dice cosa "
              "conserverà",
        'ja': 'このプロフィールのエージェントには{doing}許可が与えられていません — '
              '「エージェントにできること」で有効にしてください。'
              '何を保持するかもそこに書かれています',
        'zh': '此档案的代理未获准{doing}——请在“代理可以做什么”中开启，'
              '那里写明了它会保留什么',
        'hi': 'इस प्रोफ़ाइल के एजेंट को {doing} की अनुमति नहीं दी गई है — '
              'इसे «एजेंट क्या कर सकता है» में चालू कीजिए, जहाँ लिखा है कि '
              'वह क्या रखेगा',
        'ar': 'لم يُمنح وكيل هذا الملف إذنًا لـ{doing} — فعّله في «ما يمكن '
              'للوكيل فعله»، حيث يُذكر ما سيحتفظ به',
    },
    DIALER_SEALED: {
        'es': 'el marcador está sellado en esta instalación y no se realizó ninguna llamada: marca {number} tú mismo, ahora',
        'fr': "le composeur est scellé sur ce déploiement et aucun appel n'a été passé — composez {number} vous-même, maintenant",
        'de': 'der Wählvorgang ist auf dieser Installation versiegelt und es wurde kein Anruf getätigt — wähle {number} selbst, jetzt',
        'pt': 'o marcador está selado nesta instalação e nenhuma chamada foi feita — marque {number} você mesmo, agora',
        'it': 'il combinatore è sigillato su questa installazione e non è stata effettuata alcuna chiamata: componi {number} tu stesso, adesso',
        'ja': 'この配備では発信が封じられており、通話は行われませんでした。ご自分で {number} にすぐかけてください',
        'zh': '此部署的拨号功能已封闭，没有发出任何通话——请你自己立刻拨打 {number}',
        'hi': 'इस परिनियोजन में डायलर सील है और कोई कॉल नहीं की गई — आप स्वयं अभी {number} पर कॉल कीजिए',
        'ar': 'أداة الاتصال مختومة في هذا النشر ولم تُجرَ أي مكالمة — اتصل بـ {number} بنفسك، الآن',
    },
    DIALER_NO_CARRIER: {
        'es': 'el marcador está abierto pero no hay operador configurado, así que no se realizó ninguna llamada: marca {number} tú mismo, ahora',
        'fr': "le composeur est ouvert mais aucun opérateur n'est configuré, donc aucun appel n'a été passé — composez {number} vous-même, maintenant",
        'de': 'der Wählvorgang ist offen, aber kein Anbieter ist konfiguriert, also wurde kein Anruf getätigt — wähle {number} selbst, jetzt',
        'pt': 'o marcador está aberto mas nenhum operador está configurado, por isso nenhuma chamada foi feita — marque {number} você mesmo, agora',
        'it': "il combinatore è aperto ma nessun operatore è configurato, quindi non è stata effettuata alcuna chiamata: componi {number} tu stesso, adesso",
        'ja': '発信は開いていますが通信事業者が設定されていないため、通話は行われませんでした。ご自分で {number} にすぐかけてください',
        'zh': '拨号功能已开启但未配置运营商，因此没有发出任何通话——请你自己立刻拨打 {number}',
        'hi': 'डायलर खुला है पर कोई वाहक कॉन्फ़िगर नहीं है, इसलिए कोई कॉल नहीं की गई — आप स्वयं अभी {number} पर कॉल कीजिए',
        'ar': 'أداة الاتصال مفتوحة لكن لا مشغّل مضبوط، فلم تُجرَ أي مكالمة — اتصل بـ {number} بنفسك، الآن',
    },
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


#: The privilege roster's own sentences — what each power does, and what it
#: keeps. They lead two lives: shown as a list somebody chooses from, and
#: dropped into `PRIVILEGE_NOT_GIVEN` as its slot. So they are merged into both
#: tables below rather than typed into each, because two copies of one sentence
#: are two sentences the moment somebody edits one.
#:
#: The `asks` half is phrased so it reads after "permission to" in every
#: language — an infinitive in the Romance languages, a masdar in Arabic, an
#: oblique infinitive in Hindi — and still reads as a list item on its own.
_PRIVILEGE_SENTENCES: dict[str, dict[str, str]] = {
    'go and read up on something it does not know': {
        'es': 'ir a informarse sobre algo que no conoce',
        'fr': "aller se documenter sur quelque chose qu'il ne connaît pas",
        'de': 'sich über etwas zu informieren, das er nicht kennt',
        'pt': 'ir informar-se sobre algo que não conhece',
        'it': 'andare a informarsi su qualcosa che non conosce',
        'ja': '知らないことを調べに行く',
        'zh': '去查阅它所不知道的事情',
        'hi': 'जो वह नहीं जानता उसे पढ़कर जानने',
        'ar': 'الاطّلاع على ما لا يعرفه'},
    'put a question to strangers who can answer it': {
        'es': 'plantear una pregunta a desconocidos que puedan responderla',
        'fr': "poser une question à des inconnus capables d'y répondre",
        'de': 'Fremden eine Frage zu stellen, die sie beantworten können',
        'pt': 'colocar uma pergunta a desconhecidos que possam respondê-la',
        'it': 'porre una domanda a sconosciuti che possono rispondere',
        'ja': '答えられる見知らぬ人に質問を出す',
        'zh': '向能够回答的陌生人提出问题',
        'hi': 'अजनबियों से, जो उत्तर दे सकें, प्रश्न पूछने',
        'ar': 'طرح سؤال على غرباء يمكنهم الإجابة عنه'},
    'catch a real person up on a matter before they step in': {
        'es': 'poner al día a una persona real sobre un asunto antes de que '
              'intervenga',
        'fr': "mettre une personne réelle au courant d'une affaire avant "
              "qu'elle intervienne",
        'de': 'einen echten Menschen über eine Sache ins Bild zu setzen, '
              'bevor er einsteigt',
        'pt': 'pôr uma pessoa real a par de um assunto antes de ela entrar',
        'it': 'mettere una persona reale al corrente di una questione prima '
              'che intervenga',
        'ja': '実在の担当者が入る前に、その件について引き継ぐ',
        'zh': '在真人介入之前，先把事情的来龙去脉交接给他',
        'hi': 'किसी असली व्यक्ति को, उसके आने से पहले, मामले से अवगत कराने',
        'ar': 'إطلاع شخص حقيقي على المسألة قبل أن يتدخل'},
    'reach emergency services when it cannot resolve something': {
        'es': 'contactar con los servicios de emergencia cuando no puede '
              'resolver algo',
        'fr': "joindre les services d'urgence quand il ne peut pas résoudre "
              "quelque chose",
        'de': 'den Notruf zu erreichen, wenn er etwas nicht lösen kann',
        'pt': 'contactar os serviços de emergência quando não consegue '
              'resolver algo',
        'it': "contattare i servizi di emergenza quando non riesce a "
              "risolvere qualcosa",
        'ja': '解決できないときに緊急サービスへ連絡する',
        'zh': '在无法解决问题时联系紧急服务',
        'hi': 'जब वह कुछ हल न कर सके तो आपातकालीन सेवाओं से संपर्क करने',
        'ar': 'الاتصال بخدمات الطوارئ حين يعجز عن حل أمر ما'},
    'do a multi-step job over material the owner has granted it': {
        'es': 'realizar un trabajo de varios pasos sobre material que el '
              'titular le ha concedido',
        'fr': "effectuer un travail en plusieurs étapes sur des éléments que "
              "le titulaire lui a accordés",
        'de': 'eine mehrstufige Arbeit an Material zu erledigen, das der '
              'Inhaber ihm freigegeben hat',
        'pt': 'realizar um trabalho de vários passos sobre material que o '
              'titular lhe concedeu',
        'it': "svolgere un lavoro in più passaggi su materiale che il "
              "titolare gli ha concesso",
        'ja': '所有者が許可した資料について、複数段階の作業を行う',
        'zh': '就所有者已授权的材料执行多步骤的工作',
        'hi': 'स्वामी द्वारा दी गई सामग्री पर बहु-चरणीय कार्य करने',
        'ar': 'تنفيذ عمل متعدد الخطوات على مواد منحه إياها المالك'},
    'what it learned, as a knowledge source on the profile': {
        'es': 'lo que aprendió, como fuente de conocimiento en el perfil',
        'fr': "ce qu'il a appris, comme source de connaissance sur le profil",
        'de': 'was es gelernt hat, als Wissensquelle im Profil',
        'pt': 'o que aprendeu, como fonte de conhecimento no perfil',
        'it': 'ciò che ha appreso, come fonte di conoscenza sul profilo',
        'ja': '学んだ内容を、プロフィールの知識ソースとして',
        'zh': '它学到的内容，作为该档案上的知识来源',
        'hi': 'जो उसने सीखा, प्रोफ़ाइल पर ज्ञान-स्रोत के रूप में',
        'ar': 'ما تعلّمه، كمصدر معرفة في الملف'},
    'answers the owner accepts, as a knowledge source': {
        'es': 'las respuestas que el titular acepta, como fuente de '
              'conocimiento',
        'fr': "les réponses que le titulaire accepte, comme source de "
              "connaissance",
        'de': 'die Antworten, die der Inhaber annimmt, als Wissensquelle',
        'pt': 'as respostas que o titular aceita, como fonte de conhecimento',
        'it': "le risposte che il titolare accetta, come fonte di conoscenza",
        'ja': '所有者が受け入れた回答を、知識ソースとして',
        'zh': '所有者接受的回答，作为知识来源',
        'hi': 'स्वामी द्वारा स्वीकारे गए उत्तर, ज्ञान-स्रोत के रूप में',
        'ar': 'الإجابات التي يقبلها المالك، كمصدر معرفة'},
    'nothing new — it sends what a grant already allows': {
        'es': 'nada nuevo: envía lo que una concesión ya permite',
        'fr': "rien de nouveau — il envoie ce qu'une autorisation permet déjà",
        'de': 'nichts Neues — es sendet, was eine Freigabe ohnehin erlaubt',
        'pt': 'nada de novo — envia o que uma concessão já permite',
        'it': 'niente di nuovo: invia ciò che una concessione già consente',
        'ja': '新たに保持するものはなく、許可がすでに認めた範囲を送るだけ',
        'zh': '不新增任何保留内容——它只发送授权本已允许的部分',
        'hi': 'कुछ नया नहीं — वह वही भेजता है जिसकी अनुमति पहले से है',
        'ar': 'لا شيء جديد — يرسل ما يسمح به التفويض أصلًا'},
    'the matter, and whether a call connected': {
        'es': 'el asunto, y si una llamada llegó a conectarse',
        'fr': "l'affaire, et si un appel a abouti",
        'de': 'die Sache, und ob ein Anruf zustande kam',
        'pt': 'o assunto, e se uma chamada chegou a ligar-se',
        'it': 'la questione, e se una chiamata è stata collegata',
        'ja': 'その件と、通話がつながったかどうか',
        'zh': '该事项，以及通话是否接通',
        'hi': 'मामला, और क्या कोई कॉल जुड़ी',
        'ar': 'المسألة، وما إذا كانت مكالمة قد اتصلت'},
    "the job's finished output, watermarked": {
        'es': 'el resultado terminado del trabajo, con marca de agua',
        'fr': 'le résultat fini du travail, filigrané',
        'de': 'das fertige Ergebnis der Arbeit, mit Wasserzeichen',
        'pt': 'o resultado terminado do trabalho, com marca de água',
        'it': "il risultato finito del lavoro, con filigrana",
        'ja': '作業の完成物に、透かしを付けたもの',
        'zh': '该工作的成品，带水印',
        'hi': 'कार्य का तैयार परिणाम, वॉटरमार्क सहित',
        'ar': 'ناتج العمل النهائي، موسومًا بعلامة مائية'},
}

# One sentence, two tables. `Term` reads the vocabulary when it fills the
# refusal; `localize_public` reads the public table when the roster is shown.
_VOCABULARY.update(_PRIVILEGE_SENTENCES)
_PUBLIC.update(_PRIVILEGE_SENTENCES)


_REFUSALS: dict[str, dict[str, str]] = {
    'no such matter': {
        'es': 'no existe ese asunto',
        'fr': 'aucune affaire de ce nom',
        'de': 'kein solcher Vorgang',
        'pt': 'não existe esse assunto',
        'it': 'nessuna questione di questo tipo',
        'ja': 'そのような案件はありません',
        'zh': '没有该事项',
        'hi': 'ऐसा कोई मामला नहीं',
        'ar': 'لا توجد مسألة بهذا الوصف',
    },
    'say what is wrong, in your own words': {
        'es': 'di qué va mal, con tus propias palabras',
        'fr': 'dites ce qui ne va pas, avec vos propres mots',
        'de': 'sag mit deinen eigenen Worten, was nicht stimmt',
        'pt': 'diga o que está errado, com as suas palavras',
        'it': "di' che cosa non va, con parole tue",
        'ja': '何が問題なのかを、ご自身の言葉で書いてください',
        'zh': '用你自己的话说明哪里出了问题',
        'hi': 'अपने शब्दों में बताइए कि क्या गड़बड़ है',
        'ar': 'قل ما الخطأ، بكلماتك أنت',
    },
    'say what settled it': {
        'es': 'di qué lo resolvió',
        'fr': "dites ce qui l'a réglé",
        'de': 'sag, was es geklärt hat',
        'pt': 'diga o que o resolveu',
        'it': "di' che cosa l'ha risolto",
        'ja': '何で解決したのかを書いてください',
        'zh': '说明是什么解决了它',
        'hi': 'बताइए कि इसे किसने हल किया',
        'ar': 'قل ما الذي حسم الأمر',
    },
    'no such escalation': {
        'es': 'no existe esa escalada',
        'fr': 'aucune escalade de ce nom',
        'de': 'keine solche Eskalation',
        'pt': 'não existe esse encaminhamento urgente',
        'it': 'nessuna escalation di questo tipo',
        'ja': 'そのようなエスカレーションはありません',
        'zh': '没有该升级记录',
        'hi': 'ऐसा कोई एस्केलेशन नहीं',
        'ar': 'لا يوجد تصعيد بهذا الوصف',
    },
    'say what could not be resolved, in one line': {
        'es': 'di qué no se pudo resolver, en una línea',
        'fr': "dites en une ligne ce qui n'a pas pu être résolu",
        'de': 'sag in einer Zeile, was nicht gelöst werden konnte',
        'pt': 'diga o que não foi possível resolver, numa linha',
        'it': "di' in una riga che cosa non si è potuto risolvere",
        'ja': '解決できなかったことを、一行で書いてください',
        'zh': '用一行说明什么没能解决',
        'hi': 'एक पंक्ति में बताइए कि क्या हल नहीं हो सका',
        'ar': 'قل في سطر واحد ما الذي تعذّر حلّه',
    },
    'that escalation belongs to somebody else': {
        'es': 'esa escalada es de otra persona',
        'fr': "cette escalade appartient à quelqu'un d'autre",
        'de': 'diese Eskalation gehört jemand anderem',
        'pt': 'esse encaminhamento urgente é de outra pessoa',
        'it': 'quella escalation è di qualcun altro',
        'ja': 'そのエスカレーションは他の人のものです',
        'zh': '那条升级记录属于别人',
        'hi': 'वह एस्केलेशन किसी और का है',
        'ar': 'ذلك التصعيد يخص شخصًا آخر',
    },
    'that signature is over different words — sign the waiver as it reads now': {
        'es': 'esa firma cubre otras palabras: firma la exención tal como está ahora',
        'fr': "cette signature porte sur d'autres mots — signez la décharge telle qu'elle est maintenant",
        'de': 'diese Signatur deckt andere Worte ab — unterschreibe die Verzichtserklärung so, wie sie jetzt lautet',
        'pt': 'essa assinatura cobre outras palavras — assine a declaração tal como está agora',
        'it': "quella firma copre parole diverse: firma la liberatoria com'è adesso",
        'ja': 'その署名は別の文面に対するものです。いまの免責文にあらためて署名してください',
        'zh': '该签名针对的是另一段文字——请签署现在这份免责声明',
        'hi': 'वह हस्ताक्षर किसी और पाठ पर है — अभी जो छूट-पत्र है उस पर हस्ताक्षर कीजिए',
        'ar': 'ذلك التوقيع على كلمات أخرى — وقّع الإقرار بصيغته الحالية',
    },
    'sign the emergency-services waiver before this can be pressed — it says that services rendered may be charged to you': {
        'es': 'firma la exención de servicios de emergencia antes de poder pulsarlo: dice que los servicios prestados pueden cobrarse',
        'fr': "signez la décharge relative aux services d'urgence avant de pouvoir appuyer — elle indique que les services rendus peuvent vous être facturés",
        'de': 'unterschreibe die Verzichtserklärung für Rettungsdienste, bevor dies gedrückt werden kann — sie sagt, dass erbrachte Leistungen dir berechnet werden können',
        'pt': 'assine a declaração dos serviços de emergência antes de isto poder ser premido — diz que os serviços prestados lhe podem ser cobrados',
        'it': 'firma la liberatoria per i servizi di emergenza prima di poterlo premere: dice che i servizi resi possono esserti addebitati',
        'ja': '押せるようにする前に、緊急サービスの免責文に署名してください。提供された役務の費用が請求されうると書かれています',
        'zh': '按下之前请先签署紧急服务免责声明——上面写明所提供的服务可能向你收费',
        'hi': 'इसे दबाने से पहले आपातकालीन सेवाओं का छूट-पत्र हस्ताक्षरित कीजिए — उसमें लिखा है कि दी गई सेवाओं का शुल्क आपसे लिया जा सकता है',
        'ar': 'وقّع إقرار خدمات الطوارئ قبل أن يمكن الضغط — فهو ينص على أن الخدمات المقدَّمة قد تُحتسب عليك',
    },
    'no such provider': {
        'es': 'no existe ese proveedor',
        'fr': 'aucun prestataire de ce nom',
        'de': 'kein solcher Anbieter',
        'pt': 'não existe esse prestador',
        'it': 'nessun fornitore di questo tipo',
        'ja': 'そのような提供者はいません',
        'zh': '没有该服务提供方',
        'hi': 'ऐसा कोई प्रदाता नहीं',
        'ar': 'لا يوجد مزوّد بهذا الوصف',
    },
    'that person is not one of yours': {
        'es': 'esa persona no es de las tuyas',
        'fr': 'cette personne ne fait pas partie des vôtres',
        'de': 'diese Person gehört nicht zu deinen',
        'pt': 'essa pessoa não é uma das suas',
        'it': 'quella persona non è tra le tue',
        'ja': 'その人は、あなたの人たちに入っていません',
        'zh': '那个人不在你的人选之中',
        'hi': 'वह व्यक्ति आपके लोगों में नहीं है',
        'ar': 'ذلك الشخص ليس من أهل ثقتك المسجّلين',
    },
    'say what this is about, in one line': {
        'es': 'di de qué se trata, en una línea',
        'fr': "dites de quoi il s'agit, en une ligne",
        'de': 'sag in einer Zeile, worum es geht',
        'pt': 'diga do que se trata, numa linha',
        'it': "di' di che cosa si tratta, in una riga",
        'ja': '何についてか、一行で書いてください',
        'zh': '用一行说明这是关于什么的',
        'hi': 'एक पंक्ति में बताइए कि यह किस बारे में है',
        'ar': 'قل ما موضوع هذا، في سطر واحد',
    },
    'that grant is unknown or has been revoked — nothing can be read with it': {
        'es': 'ese permiso es desconocido o ha sido revocado: no se puede leer nada con él',
        'fr': 'cette autorisation est inconnue ou a été révoquée — rien ne peut être lu avec elle',
        'de': 'diese Freigabe ist unbekannt oder wurde widerrufen — damit lässt sich nichts lesen',
        'pt': 'essa autorização é desconhecida ou foi revogada — nada pode ser lido com ela',
        'it': 'quel permesso è sconosciuto o è stato revocato: con esso non si può leggere nulla',
        'ja': 'その許可は不明か、取り消されています。これで読めるものはありません',
        'zh': '该授权未知或已被撤销——用它读不到任何内容',
        'hi': 'वह अनुमति अज्ञात है या रद्द की जा चुकी है — इससे कुछ नहीं पढ़ा जा सकता',
        'ar': 'هذا التصريح مجهول أو أُلغي — لا يمكن قراءة شيء به',
    },
    'bring somebody into your people before briefing them — a file does not travel to a professional nobody chose': {
        'es': 'añade a esa persona a las tuyas antes de informarla: un expediente no viaja a un profesional que nadie eligió',
        'fr': "ajoutez cette personne aux vôtres avant de la briefer — un dossier ne va pas à un professionnel que personne n'a choisi",
        'de': 'nimm diese Person zuerst zu deinen auf — eine Akte geht nicht an eine Fachkraft, die niemand gewählt hat',
        'pt': 'junte essa pessoa às suas antes de a informar — um processo não viaja para um profissional que ninguém escolheu',
        'it': 'aggiungi quella persona alle tue prima di informarla: un fascicolo non va a un professionista che nessuno ha scelto',
        'ja': '先にその人をあなたの人たちに加えてください。誰も選んでいない専門家に資料は渡りません',
        'zh': '先把这个人加入你的人选，再向其通报——档案不会送往没有人选择过的专业人士',
        'hi': 'उन्हें जानकारी देने से पहले अपने लोगों में जोड़िए — फ़ाइल ऐसे पेशेवर तक नहीं जाती जिसे किसी ने चुना ही नहीं',
        'ar': 'أضِف ذلك الشخص إلى أهل ثقتك قبل إحاطته — لا ينتقل ملف إلى مِهني لم يخترْه أحد',
    },
    'a campaign needs a goal above zero': {
        'es': 'una campaña necesita una meta mayor que cero',
        'fr': "une campagne a besoin d'un objectif supérieur à zéro",
        'de': 'eine Kampagne braucht ein Ziel über null',
        'pt': 'uma campanha precisa de uma meta acima de zero',
        'it': 'una campagna ha bisogno di un obiettivo sopra lo zero',
        'ja': 'キャンペーンには、ゼロより大きい目標が要ります',
        'zh': '筹款需要一个大于零的目标',
        'hi': 'अभियान के लिए शून्य से बड़ा लक्ष्य चाहिए',
        'ar': 'الحملة تحتاج هدفًا أكبر من صفر',
    },
    'a desk needs a name a visitor can read': {
        'es': 'un puesto necesita un nombre que un visitante pueda leer',
        'fr': "un guichet a besoin d'un nom qu'un visiteur puisse lire",
        'de': 'ein Schalter braucht einen Namen, den ein Besucher lesen kann',
        'pt': 'um balcão precisa de um nome que um visitante consiga ler',
        'it': 'un banco ha bisogno di un nome che un visitatore possa leggere',
        'ja': '受付には、訪れた人が読める名前が要ります',
        'zh': '服务台需要一个访客能读懂的名称',
        'hi': 'डेस्क के लिए ऐसा नाम चाहिए जो आगंतुक पढ़ सके',
        'ar': 'المكتب يحتاج اسمًا يستطيع الزائر قراءته',
    },
    'a donation needs an amount above zero': {
        'es': 'una donación necesita un importe mayor que cero',
        'fr': "un don a besoin d'un montant supérieur à zéro",
        'de': 'eine Spende braucht einen Betrag über null',
        'pt': 'um donativo precisa de um valor acima de zero',
        'it': 'una donazione ha bisogno di un importo sopra lo zero',
        'ja': '寄付には、ゼロより大きい金額が要ります',
        'zh': '捐赠需要一个大于零的金额',
        'hi': 'दान के लिए शून्य से बड़ी राशि चाहिए',
        'ar': 'التبرع يحتاج مبلغًا أكبر من صفر',
    },
    'a grant needs two people': {
        'es': 'un préstamo necesita dos personas',
        'fr': 'un prêt a besoin de deux personnes',
        'de': 'eine Leihgabe braucht zwei Personen',
        'pt': 'um empréstimo precisa de duas pessoas',
        'it': 'un prestito ha bisogno di due persone',
        'ja': '貸し出しには二人が必要です',
        'zh': '出借需要两个人',
        'hi': 'उधार देने के लिए दो लोग चाहिए',
        'ar': 'الإعارة تحتاج شخصين',
    },
    'a note needs something in it': {
        'es': 'una nota necesita algo dentro',
        'fr': 'une note doit contenir quelque chose',
        'de': 'eine Notiz braucht einen Inhalt',
        'pt': 'uma nota precisa de algo dentro',
        'it': 'una nota deve contenere qualcosa',
        'ja': 'メモには何か書いてください',
        'zh': '备注不能是空的',
        'hi': 'टिप्पणी में कुछ तो होना चाहिए',
        'ar': 'الملاحظة يجب أن تحتوي شيئًا',
    },
    'a skill lent in one place cannot be used in another — ask there': {
        'es': 'una habilidad prestada en un sitio no puede usarse en otro: pídela allí',
        'fr': 'une compétence prêtée à un endroit ne peut servir ailleurs — demandez-la là-bas',
        'de': 'eine an einem Ort verliehene Fähigkeit gilt nicht anderswo — frage dort',
        'pt': 'uma competência emprestada num sítio não pode ser usada noutro — peça lá',
        'it': "un'abilità prestata in un posto non vale altrove: chiedila lì",
        'ja': 'ある場所で借りた技能は別の場所では使えません。その場所で頼んでください',
        'zh': '在一处借来的技能不能用在另一处——请到那边申请',
        'hi': 'एक जगह उधार लिया कौशल दूसरी जगह काम नहीं आता — वहीं माँगिए',
        'ar': 'المهارة المعارة في مكان لا تُستخدم في آخر — اطلبها هناك',
    },
    'an edit needs something in it — retract instead': {
        'es': 'una edición necesita algo dentro; si no, retíralo',
        'fr': 'une modification doit contenir quelque chose — sinon, retirez-le',
        'de': 'eine Änderung braucht einen Inhalt — sonst nimm es zurück',
        'pt': 'uma edição precisa de algo dentro — caso contrário, retire-o',
        'it': 'una modifica deve contenere qualcosa: altrimenti ritiralo',
        'ja': '書き直しには何か書いてください。何も残さないなら取り消しを使います',
        'zh': '修改内容不能为空——若要清空请改用撤回',
        'hi': 'बदलाव में कुछ तो होना चाहिए — वरना वापस लीजिए',
        'ar': 'التعديل يجب أن يحتوي شيئًا — وإلا فاسحبه',
    },
    'every share must be above zero': {
        'es': 'cada parte debe ser mayor que cero',
        'fr': 'chaque part doit être supérieure à zéro',
        'de': 'jeder Anteil muss über null liegen',
        'pt': 'cada parte tem de ser acima de zero',
        'it': 'ogni quota deve essere sopra lo zero',
        'ja': 'どの取り分も、ゼロより大きくしてください',
        'zh': '每一份都必须大于零',
        'hi': 'हर हिस्सा शून्य से बड़ा होना चाहिए',
        'ar': 'كل حصة يجب أن تكون أكبر من صفر',
    },
    'name at least one loved one or organization': {
        'es': 'nombra al menos a un ser querido o una organización',
        'fr': 'nommez au moins un proche ou une organisation',
        'de': 'nenne mindestens einen Angehörigen oder eine Organisation',
        'pt': 'indique pelo menos um ente querido ou uma organização',
        'it': "indica almeno una persona cara o un'organizzazione",
        'ja': '大切な人か団体を、少なくとも一つ挙げてください',
        'zh': '至少指明一位亲友或一个机构',
        'hi': 'कम से कम एक अपने या एक संस्था का नाम दीजिए',
        'ar': 'سمِّ عزيزًا واحدًا أو منظمة واحدة على الأقل',
    },
    'no such clinician': {
        'es': 'no existe ese clínico',
        'fr': 'aucun clinicien de ce nom',
        'de': 'keine solche Ärztin, kein solcher Arzt',
        'pt': 'não existe esse clínico',
        'it': 'nessun clinico di questo tipo',
        'ja': 'そのような臨床医はいません',
        'zh': '没有该临床医生',
        'hi': 'ऐसा कोई चिकित्सक नहीं',
        'ar': 'لا يوجد طبيب بهذا الوصف',
    },
    'no such connection in this session': {
        'es': 'no existe esa conexión en esta sesión',
        'fr': 'aucune connexion de ce nom dans cette session',
        'de': 'keine solche Verbindung in dieser Sitzung',
        'pt': 'não existe essa ligação nesta sessão',
        'it': 'nessuna connessione di questo tipo in questa sessione',
        'ja': 'このセッションにそのような接続はありません',
        'zh': '本次会话中没有该连接',
        'hi': 'इस सत्र में ऐसा कोई कनेक्शन नहीं',
        'ar': 'لا يوجد اتصال بهذا الوصف في هذه الجلسة',
    },
    'no such grant': {
        'es': 'no existe ese préstamo',
        'fr': 'aucun prêt de ce nom',
        'de': 'keine solche Leihgabe',
        'pt': 'não existe esse empréstimo',
        'it': 'nessun prestito di questo tipo',
        'ja': 'そのような貸し出しはありません',
        'zh': '没有该出借记录',
        'hi': 'ऐसा कोई उधार नहीं',
        'ar': 'لا توجد إعارة بهذا الوصف',
    },
    'no such referral, or it has not been opened yet': {
        'es': 'no existe esa derivación, o todavía no se ha abierto',
        'fr': "aucun renvoi de ce nom, ou il n'a pas encore été ouvert",
        'de': 'keine solche Überweisung, oder sie wurde noch nicht geöffnet',
        'pt': 'não existe esse encaminhamento, ou ainda não foi aberto',
        'it': 'nessun invio di questo tipo, o non è ancora stato aperto',
        'ja': 'そのような紹介はないか、まだ開かれていません',
        'zh': '没有该转诊，或它尚未被打开',
        'hi': 'ऐसा कोई रेफ़रल नहीं, या वह अभी खोला नहीं गया',
        'ar': 'لا توجد إحالة بهذا الوصف، أو أنها لم تُفتح بعد',
    },
    'no such request': {
        'es': 'no existe esa solicitud',
        'fr': 'aucune demande de ce nom',
        'de': 'keine solche Anfrage',
        'pt': 'não existe esse pedido',
        'it': 'nessuna richiesta di questo tipo',
        'ja': 'そのような依頼はありません',
        'zh': '没有该请求',
        'hi': 'ऐसा कोई अनुरोध नहीं',
        'ar': 'لا يوجد طلب بهذا الوصف',
    },
    'only the person it was offered to can accept it': {
        'es': 'solo la persona a quien se ofreció puede aceptarlo',
        'fr': "seule la personne à qui il a été proposé peut l'accepter",
        'de': 'nur die Person, der es angeboten wurde, kann es annehmen',
        'pt': 'só a pessoa a quem foi oferecido o pode aceitar',
        'it': 'solo la persona a cui è stato offerto può accettarlo',
        'ja': '申し出を受けた本人だけが承諾できます',
        'zh': '只有被提供的那个人可以接受',
        'hi': 'जिसे प्रस्ताव दिया गया, केवल वही स्वीकार कर सकता है',
        'ar': 'لا يقبله إلا من عُرض عليه',
    },
    'only the person it was offered to can decline it': {
        'es': 'solo la persona a quien se ofreció puede rechazarlo',
        'fr': 'seule la personne à qui il a été proposé peut le refuser',
        'de': 'nur die Person, der es angeboten wurde, kann es ablehnen',
        'pt': 'só a pessoa a quem foi oferecido o pode recusar',
        'it': 'solo la persona a cui è stato offerto può rifiutarlo',
        'ja': '申し出を受けた本人だけが断れます',
        'zh': '只有被提供的那个人可以拒绝',
        'hi': 'जिसे प्रस्ताव दिया गया, केवल वही अस्वीकार कर सकता है',
        'ar': 'لا يرفضه إلا من عُرض عليه',
    },
    'only the two people involved can close this': {
        'es': 'solo las dos personas implicadas pueden cerrarlo',
        'fr': 'seules les deux personnes concernées peuvent y mettre fin',
        'de': 'nur die beiden Beteiligten können das schließen',
        'pt': 'só as duas pessoas envolvidas o podem encerrar',
        'it': 'solo le due persone coinvolte possono chiuderlo',
        'ja': '関わっている二人だけが終われます',
        'zh': '只有涉及的两个人可以结束它',
        'hi': 'इसमें शामिल दोनों लोग ही इसे बंद कर सकते हैं',
        'ar': 'لا يغلقه إلا الشخصان المعنيان',
    },
    'only your own turn can be retracted': {
        'es': 'solo puedes retirar tu propio turno',
        'fr': 'vous ne pouvez retirer que votre propre tour',
        'de': 'nur der eigene Beitrag kann zurückgenommen werden',
        'pt': 'só pode retirar a sua própria vez',
        'it': 'puoi ritirare solo il tuo turno',
        'ja': '取り消せるのは自分の発言だけです',
        'zh': '只能撤回你自己的那一轮',
        'hi': 'केवल अपनी ही बात वापस ली जा सकती है',
        'ar': 'لا يُسحب إلا دورك أنت',
    },
    'say what is being lent, in words the other reads': {
        'es': 'di qué se presta, en palabras que el otro lea',
        'fr': "dites ce qui est prêté, dans des mots que l'autre lit",
        'de': 'sag in Worten, die der andere liest, was verliehen wird',
        'pt': 'diga o que está a ser emprestado, em palavras que o outro leia',
        'it': "di' che cosa viene prestato, con parole che l'altro legge",
        'ja': '何を貸すのか、相手が読む言葉で書いてください',
        'zh': '用对方能读懂的话说明借出的是什么',
        'hi': 'क्या उधार दिया जा रहा है, ऐसे शब्दों में बताइए जो दूसरा पढ़े',
        'ar': 'قل ما الذي يُعار، بكلمات يقرؤها الطرف الآخر',
    },
    'that grant belongs to somebody else': {
        'es': 'ese préstamo es de otra persona',
        'fr': "ce prêt appartient à quelqu'un d'autre",
        'de': 'diese Leihgabe gehört jemand anderem',
        'pt': 'esse empréstimo é de outra pessoa',
        'it': 'quel prestito è di qualcun altro',
        'ja': 'その貸し出しは他の人のものです',
        'zh': '那笔出借属于别人',
        'hi': 'वह उधार किसी और का है',
        'ar': 'تلك الإعارة تخص شخصًا آخر',
    },
    'that grant is closed': {
        'es': 'ese préstamo está cerrado',
        'fr': 'ce prêt est clos',
        'de': 'diese Leihgabe ist geschlossen',
        'pt': 'esse empréstimo está encerrado',
        'it': 'quel prestito è chiuso',
        'ja': 'その貸し出しは終了しています',
        'zh': '那笔出借已结束',
        'hi': 'वह उधार बंद हो चुका है',
        'ar': 'تلك الإعارة مغلقة',
    },
    'that link is not valid': {
        'es': 'ese enlace no es válido',
        'fr': "ce lien n'est pas valide",
        'de': 'dieser Link ist nicht gültig',
        'pt': 'essa ligação não é válida',
        'it': 'quel link non è valido',
        'ja': 'そのリンクは有効ではありません',
        'zh': '该链接无效',
        'hi': 'वह लिंक मान्य नहीं है',
        'ar': 'هذا الرابط غير صالح',
    },
    'that message belongs to somebody else': {
        'es': 'ese mensaje es de otra persona',
        'fr': "ce message appartient à quelqu'un d'autre",
        'de': 'diese Nachricht gehört jemand anderem',
        'pt': 'essa mensagem é de outra pessoa',
        'it': 'quel messaggio è di qualcun altro',
        'ja': 'そのメッセージは他の人のものです',
        'zh': '那条消息属于别人',
        'hi': 'वह संदेश किसी और का है',
        'ar': 'تلك الرسالة تخص شخصًا آخر',
    },
    'that message was retracted': {
        'es': 'ese mensaje fue retirado',
        'fr': 'ce message a été retiré',
        'de': 'diese Nachricht wurde zurückgenommen',
        'pt': 'essa mensagem foi retirada',
        'it': 'quel messaggio è stato ritirato',
        'ja': 'そのメッセージは取り消されました',
        'zh': '那条消息已被撤回',
        'hi': 'वह संदेश वापस लिया जा चुका है',
        'ar': 'تلك الرسالة سُحبت',
    },
    'that offer was declined — a fresh one is needed': {
        'es': 'esa oferta fue rechazada: hace falta una nueva',
        'fr': 'cette proposition a été refusée — il en faut une nouvelle',
        'de': 'dieses Angebot wurde abgelehnt — es braucht ein neues',
        'pt': 'essa oferta foi recusada — é preciso uma nova',
        'it': "quell'offerta è stata rifiutata: ne serve una nuova",
        'ja': 'その申し出は断られました。新しく出し直してください',
        'zh': '那个提议已被拒绝——需要重新提出',
        'hi': 'वह प्रस्ताव अस्वीकार हो चुका — नया देना होगा',
        'ar': 'رُفض ذلك العرض — يلزم عرض جديد',
    },
    'that reply link is not valid': {
        'es': 'ese enlace de respuesta no es válido',
        'fr': "ce lien de réponse n'est pas valide",
        'de': 'dieser Antwort-Link ist nicht gültig',
        'pt': 'essa ligação de resposta não é válida',
        'it': 'quel link di risposta non è valido',
        'ja': 'その返信リンクは有効ではありません',
        'zh': '该回复链接无效',
        'hi': 'वह उत्तर-लिंक मान्य नहीं है',
        'ar': 'رابط الرد هذا غير صالح',
    },
    "that ring is not this desk's": {
        'es': 'ese timbrazo no es de este puesto',
        'fr': "cette sonnerie n'est pas celle de ce guichet",
        'de': 'dieses Klingeln gehört nicht zu diesem Schalter',
        'pt': 'esse toque não é deste balcão',
        'it': 'quello squillo non è di questo banco',
        'ja': 'その呼び出しは、この受付のものではありません',
        'zh': '那次按铃不属于这个服务台',
        'hi': 'वह घंटी इस डेस्क की नहीं है',
        'ar': 'ذلك الرنين ليس لهذا المكتب',
    },
    'that signature does not verify': {
        'es': 'esa firma no se verifica',
        'fr': 'cette signature ne se vérifie pas',
        'de': 'diese Signatur lässt sich nicht verifizieren',
        'pt': 'essa assinatura não se verifica',
        'it': 'quella firma non si verifica',
        'ja': 'その署名は検証できません',
        'zh': '该签名无法通过验证',
        'hi': 'वह हस्ताक्षर सत्यापित नहीं होता',
        'ar': 'هذا التوقيع لا يجتاز التحقق',
    },
    'the bell was just rung — give them a moment to reach the desk': {
        'es': 'acaban de llamar: dales un momento para llegar al puesto',
        'fr': 'on vient de sonner — laissez-leur un instant pour rejoindre le guichet',
        'de': 'es wurde gerade geklingelt — gib ihnen einen Moment bis zum Schalter',
        'pt': 'o toque foi agora mesmo — dê-lhes um momento para chegar ao balcão',
        'it': 'hanno appena suonato: dai loro un momento per raggiungere il banco',
        'ja': 'いま呼び出したところです。受付に着くまで少し待ってください',
        'zh': '刚刚按过铃——给他们一点时间走到服务台',
        'hi': 'अभी-अभी घंटी बजी है — उन्हें डेस्क तक आने का थोड़ा समय दीजिए',
        'ar': 'رُنّ الجرس للتو — أمهلهم لحظة للوصول إلى المكتب',
    },
    'the summary changed after it was signed; sign the new one': {
        'es': 'el resumen cambió después de firmarse; firma el nuevo',
        'fr': 'le résumé a changé après signature ; signez le nouveau',
        'de': 'die Zusammenfassung hat sich nach der Unterschrift geändert; unterschreibe die neue',
        'pt': 'o resumo mudou depois de assinado; assine o novo',
        'it': 'il riepilogo è cambiato dopo la firma; firma quello nuovo',
        'ja': '署名のあとで要約が変わりました。新しいほうに署名してください',
        'zh': '摘要在签署之后有改动；请签署新的那份',
        'hi': 'हस्ताक्षर के बाद सारांश बदल गया; नए पर हस्ताक्षर कीजिए',
        'ar': 'تغيّر الملخص بعد توقيعه؛ وقّع الملخص الجديد',
    },
    'this campaign is closed': {
        'es': 'esta campaña está cerrada',
        'fr': 'cette campagne est close',
        'de': 'diese Kampagne ist geschlossen',
        'pt': 'esta campanha está encerrada',
        'it': 'questa campagna è chiusa',
        'ja': 'このキャンペーンは終了しています',
        'zh': '这项筹款已结束',
        'hi': 'यह अभियान बंद है',
        'ar': 'هذه الحملة مغلقة',
    },
    'this desk is closed, so the bell is off — nobody would hear it': {
        'es': 'este puesto está cerrado, así que el timbre está apagado: nadie lo oiría',
        'fr': "ce guichet est fermé, la sonnette est donc coupée — personne ne l'entendrait",
        'de': 'dieser Schalter ist geschlossen, die Klingel also aus — niemand würde sie hören',
        'pt': 'este balcão está fechado, por isso a campainha está desligada — ninguém a ouviria',
        'it': 'questo banco è chiuso, quindi il campanello è spento: nessuno lo sentirebbe',
        'ja': 'この受付は閉まっているので呼び鈴も切ってあります。誰にも聞こえません',
        'zh': '此服务台已关闭，所以铃是关的——没有人会听见',
        'hi': 'यह डेस्क बंद है, इसलिए घंटी भी बंद है — कोई सुनेगा ही नहीं',
        'ar': 'هذا المكتب مغلق، فالجرس مطفأ — لن يسمعه أحد',
    },
    'this referral has already been released': {
        'es': 'esta derivación ya se ha entregado',
        'fr': 'ce renvoi a déjà été transmis',
        'de': 'diese Überweisung wurde bereits übergeben',
        'pt': 'este encaminhamento já foi entregue',
        'it': 'questo invio è già stato consegnato',
        'ja': 'この紹介はすでに引き渡されています',
        'zh': '该转诊已经发出',
        'hi': 'यह रेफ़रल पहले ही भेजा जा चुका है',
        'ar': 'سبق أن أُرسلت هذه الإحالة',
    },
    'this session is closed': {
        'es': 'esta sesión está cerrada',
        'fr': 'cette session est close',
        'de': 'diese Sitzung ist geschlossen',
        'pt': 'esta sessão está encerrada',
        'it': 'questa sessione è chiusa',
        'ja': 'このセッションは終了しています',
        'zh': '本次会话已结束',
        'hi': 'यह सत्र बंद है',
        'ar': 'هذه الجلسة مغلقة',
    },
    'this stream is closed right now': {
        'es': 'esta transmisión está cerrada ahora mismo',
        'fr': "cette diffusion est fermée pour l'instant",
        'de': 'dieser Stream ist gerade geschlossen',
        'pt': 'esta transmissão está fechada neste momento',
        'it': 'questa diretta è chiusa in questo momento',
        'ja': 'この配信はいま閉じています',
        'zh': '此直播目前已关闭',
        'hi': 'यह स्ट्रीम अभी बंद है',
        'ar': 'هذا البث مغلق الآن',
    },
    'you are not on this stream': {
        'es': 'no estás en esta transmisión',
        'fr': "vous n'êtes pas sur cette diffusion",
        'de': 'du bist nicht in diesem Stream',
        'pt': 'não está nesta transmissão',
        'it': 'non sei in questa diretta',
        'ja': 'あなたはこの配信に参加していません',
        'zh': '你不在此直播中',
        'hi': 'आप इस स्ट्रीम में नहीं हैं',
        'ar': 'لست في هذا البث',
    },
    'you have already written back on this referral': {
        'es': 'ya has respondido en esta derivación',
        'fr': 'vous avez déjà répondu sur ce renvoi',
        'de': 'du hast auf diese Überweisung bereits geantwortet',
        'pt': 'já respondeu neste encaminhamento',
        'it': 'hai già risposto su questo invio',
        'ja': 'この紹介にはすでに返信済みです',
        'zh': '你已经就该转诊回复过了',
        'hi': 'आप इस रेफ़रल पर पहले ही जवाब दे चुके हैं',
        'ar': 'سبق أن رددت على هذه الإحالة',
    },
    'campaign not found or already closed': {
        'es': 'campaña no encontrada o ya cerrada',
        'fr': 'campagne introuvable ou déjà close',
        'de': 'Kampagne nicht gefunden oder bereits geschlossen',
        'pt': 'campanha não encontrada ou já encerrada',
        'it': 'campagna non trovata o già chiusa',
        'ja': 'キャンペーンが見つからないか、すでに終了しています',
        'zh': '未找到该筹款，或它已结束',
        'hi': 'अभियान नहीं मिला, या वह बंद हो चुका है',
        'ar': 'الحملة غير موجودة أو مغلقة بالفعل',
    },
    'name the host to stop visiting': {
        'es': 'nombra el host que dejará de visitarse',
        'fr': 'nommez l\'hôte à ne plus visiter',
        'de': 'nenne den Host, der nicht mehr besucht werden soll',
        'pt': 'indique o host que deixará de ser visitado',
        'it': "indica l'host da non visitare più",
        'ja': '訪問をやめるホストを指定してください',
        'zh': '指明要停止访问的主机',
        'hi': 'बताइए किस होस्ट पर जाना बंद करना है',
        'ar': 'سمِّ المضيف الذي يجب التوقف عن زيارته',
    },
    'name the host to visit again': {
        'es': 'nombra el host que volverá a visitarse',
        'fr': 'nommez l\'hôte à visiter de nouveau',
        'de': 'nenne den Host, der wieder besucht werden soll',
        'pt': 'indique o host que voltará a ser visitado',
        'it': "indica l'host da visitare di nuovo",
        'ja': 'ふたたび訪問するホストを指定してください',
        'zh': '指明要重新访问的主机',
        'hi': 'बताइए किस होस्ट पर फिर से जाना है',
        'ar': 'سمِّ المضيف الذي ستُستأنف زيارته',
    },
    'this profile does not visit that host any more — lift the stand-down on '
    'it if this connection should start fetching again': {
        'es': 'este perfil ya no visita ese host — levanta la suspensión '
              'sobre él si esta conexión debe volver a traer contenido',
        'fr': "ce profil ne visite plus cet hôte — levez la suspension le "
              'concernant si cette connexion doit recommencer à récupérer',
        'de': 'dieses Profil besucht diesen Host nicht mehr — hebe die '
              'Aussetzung auf, wenn diese Verbindung wieder abrufen soll',
        'pt': 'este perfil já não visita esse host — levante a suspensão '
              'sobre ele se esta ligação deve voltar a buscar conteúdo',
        'it': "questo profilo non visita più quell'host — revoca la "
              'sospensione se questa connessione deve tornare a recuperare',
        'ja': 'このプロフィールはそのホストをもう訪問しません。この接続で再び取得するなら、'
              '訪問停止を解除してください',
        'zh': '此资料不再访问该主机——若这条连接应恢复抓取，请解除对它的暂停',
        'hi': 'यह प्रोफ़ाइल अब उस होस्ट पर नहीं जाती — यदि यह कनेक्शन फिर से '
              'सामग्री लाए, तो उस पर लगी रोक हटाइए',
        'ar': 'لم يعد هذا الملف يزور ذلك المضيف — ارفع الإيقاف عنه إن كان على '
              'هذا الاتصال أن يعود إلى الجلب',
    },
    'reading where this deployment has been requires the QRME_PROBLEMS_KEY '
    'bearer token': {
        'es': 'leer dónde ha estado esta instalación requiere el token '
              'portador QRME_PROBLEMS_KEY',
        'fr': 'lire où ce déploiement est allé exige le jeton porteur '
              'QRME_PROBLEMS_KEY',
        'de': 'zu lesen, wo diese Installation war, erfordert das '
              'QRME_PROBLEMS_KEY-Bearer-Token',
        'pt': 'ler onde esta instalação esteve requer o token portador '
              'QRME_PROBLEMS_KEY',
        'it': 'leggere dove è stata questa installazione richiede il token '
              'bearer QRME_PROBLEMS_KEY',
        'ja': 'この配備がどこへ行ったかの閲覧には QRME_PROBLEMS_KEY のベアラートークンが必要です',
        'zh': '读取此部署去过哪里需要 QRME_PROBLEMS_KEY 持有者令牌',
        'hi': 'यह परिनियोजन कहाँ-कहाँ गया है, पढ़ने के लिए QRME_PROBLEMS_KEY '
              'बियरर टोकन चाहिए',
        'ar': 'قراءة أين ذهب هذا النشر تتطلب رمز QRME_PROBLEMS_KEY الحامل',
    },
    'where this deployment has been is readable from this machine only until '
    'QRME_PROBLEMS_KEY is set — behind a proxy, set it': {
        'es': 'dónde ha estado esta instalación solo se puede leer desde esta '
              'máquina hasta que se fije QRME_PROBLEMS_KEY — tras un proxy, '
              'fíjala',
        'fr': "où ce déploiement est allé n'est lisible que depuis cette "
              "machine tant que QRME_PROBLEMS_KEY n'est pas définie — "
              'derrière un proxy, définissez-la',
        'de': 'wo diese Installation war, ist nur von dieser Maschine lesbar, '
              'bis QRME_PROBLEMS_KEY gesetzt ist — hinter einem Proxy: setzen',
        'pt': 'onde esta instalação esteve só pode ser lido a partir desta '
              'máquina até QRME_PROBLEMS_KEY estar definida — atrás de um '
              'proxy, defina-a',
        'it': 'dove è stata questa installazione è leggibile solo da questa '
              'macchina finché QRME_PROBLEMS_KEY non è impostata — dietro un '
              'proxy, impostala',
        'ja': 'この配備がどこへ行ったかは、QRME_PROBLEMS_KEY が設定されるまで'
              'この機械からのみ読めます。プロキシの背後では設定してください',
        'zh': '在设置 QRME_PROBLEMS_KEY 之前，此部署去过哪里只能从本机读取——'
              '若在代理之后，请设置它',
        'hi': 'QRME_PROBLEMS_KEY सेट होने तक यह परिनियोजन कहाँ-कहाँ गया है, '
              'केवल इसी मशीन से पढ़ा जा सकता है — प्रॉक्सी के पीछे हो तो इसे सेट कीजिए',
        'ar': 'أين ذهب هذا النشر يمكن قراءته من هذا الجهاز فقط إلى أن يُضبط '
              'QRME_PROBLEMS_KEY — خلف وسيط، اضبطه',
    },
    'an empty answer answers nothing': {
        'es': 'una respuesta vacía no responde nada',
        'fr': 'une réponse vide ne répond à rien',
        'de': 'eine leere Antwort beantwortet nichts',
        'pt': 'uma resposta vazia não responde nada',
        'it': 'una risposta vuota non risponde a nulla',
        'ja': '空の回答は何も答えていません',
        'zh': '空的回答什么也没回答',
        'hi': 'खाली उत्तर कुछ नहीं बताता',
        'ar': 'الإجابة الفارغة لا تجيب عن شيء',
    },
    'no such answer to this question': {
        'es': 'no existe esa respuesta a esta pregunta',
        'fr': 'aucune réponse de ce nom à cette question',
        'de': 'keine solche Antwort auf diese Frage',
        'pt': 'não existe essa resposta para esta pergunta',
        'it': 'nessuna risposta di questo tipo a questa domanda',
        'ja': 'この質問にそのような回答はありません',
        'zh': '这个问题没有该回答',
        'hi': 'इस प्रश्न का ऐसा कोई उत्तर नहीं',
        'ar': 'لا توجد إجابة بهذا الوصف على هذا السؤال',
    },
    'no such question': {
        'es': 'no existe esa pregunta',
        'fr': 'aucune question de ce nom',
        'de': 'keine solche Frage',
        'pt': 'não existe essa pergunta',
        'it': 'nessuna domanda di questo tipo',
        'ja': 'そのような質問はありません',
        'zh': '没有该问题',
        'hi': 'ऐसा कोई प्रश्न नहीं',
        'ar': 'لا يوجد سؤال بهذا الوصف',
    },
    'say what you want to know, in one question': {
        'es': 'di qué quieres saber, en una sola pregunta',
        'fr': 'dites en une seule question ce que vous voulez savoir',
        'de': 'sag in einer Frage, was du wissen willst',
        'pt': 'diga o que quer saber, numa única pergunta',
        'it': "di' che cosa vuoi sapere, in una sola domanda",
        'ja': '知りたいことを、質問一つで書いてください',
        'zh': '用一个问题说明你想知道什么',
        'hi': 'एक ही प्रश्न में बताइए कि आप क्या जानना चाहते हैं',
        'ar': 'قل ما تريد معرفته، في سؤال واحد',
    },
    'that answer is longer than this board takes': {
        'es': 'esa respuesta es más larga de lo que admite este tablón',
        'fr': 'cette réponse est plus longue que ce que ce tableau accepte',
        'de': 'diese Antwort ist länger, als dieses Brett annimmt',
        'pt': 'essa resposta é mais longa do que este quadro aceita',
        'it': 'questa risposta è più lunga di quanto questa bacheca accetti',
        'ja': 'この掲示板が受け取れる長さを超えています',
        'zh': '这条回答超过了本板块接受的长度',
        'hi': 'यह उत्तर इस बोर्ड की सीमा से लंबा है',
        'ar': 'هذه الإجابة أطول مما تقبله هذه اللوحة',
    },
    'that is a long direction to point in': {
        'es': 'esa indicación es demasiado larga',
        'fr': 'cette indication est trop longue',
        'de': 'dieser Hinweis ist zu lang',
        'pt': 'essa indicação é longa demais',
        'it': 'questa indicazione è troppo lunga',
        'ja': 'その案内は長すぎます',
        'zh': '这个指引太长了',
        'hi': 'यह संकेत बहुत लंबा है',
        'ar': 'هذا التوجيه طويل أكثر من اللازم',
    },
    'that is a long name to be called by': {
        'es': 'ese nombre es demasiado largo para llamarte así',
        'fr': "c'est un nom bien long pour vous appeler",
        'de': 'das ist ein langer Name, um so genannt zu werden',
        'pt': 'esse nome é longo demais para o chamarem assim',
        'it': 'è un nome troppo lungo per farsi chiamare così',
        'ja': '呼び名としては長すぎます',
        'zh': '这个称呼太长了',
        'hi': 'यह नाम पुकारने के लिए बहुत लंबा है',
        'ar': 'هذا اسم طويل ليُنادى به',
    },
    'this answer was blocked by the filter and cannot be folded in': {
        'es': 'el filtro bloqueó esta respuesta y no puede incorporarse',
        'fr': "le filtre a bloqué cette réponse ; elle ne peut pas être intégrée",
        'de': 'der Filter hat diese Antwort blockiert; sie kann nicht '
              'übernommen werden',
        'pt': 'o filtro bloqueou esta resposta e ela não pode ser incorporada',
        'it': 'il filtro ha bloccato questa risposta e non può essere integrata',
        'ja': 'この回答はフィルターで止められたため、取り込めません',
        'zh': '这条回答已被过滤器拦截，无法收录',
        'hi': 'इस उत्तर को फ़िल्टर ने रोका है, इसे शामिल नहीं किया जा सकता',
        'ar': 'حجب المرشِّح هذه الإجابة، فلا يمكن ضمّها',
    },
    'this question is already closed': {
        'es': 'esta pregunta ya está cerrada',
        'fr': 'cette question est déjà close',
        'de': 'diese Frage ist bereits geschlossen',
        'pt': 'esta pergunta já está encerrada',
        'it': 'questa domanda è già chiusa',
        'ja': 'この質問はすでに締め切られています',
        'zh': '这个问题已经关闭',
        'hi': 'यह प्रश्न पहले ही बंद हो चुका है',
        'ar': 'هذا السؤال مغلق بالفعل',
    },
    'this question is closed — it is not taking answers any more': {
        'es': 'esta pregunta está cerrada: ya no admite respuestas',
        'fr': "cette question est close — elle n'accepte plus de réponses",
        'de': 'diese Frage ist geschlossen — sie nimmt keine Antworten mehr an',
        'pt': 'esta pergunta está encerrada — já não aceita respostas',
        'it': 'questa domanda è chiusa — non accetta più risposte',
        'ja': 'この質問は締め切られており、これ以上回答を受け付けません',
        'zh': '这个问题已关闭，不再接受回答',
        'hi': 'यह प्रश्न बंद है — अब उत्तर स्वीकार नहीं किए जाते',
        'ar': 'هذا السؤال مغلق — لم يعد يقبل إجابات',
    },
    'a fee cannot be negative': {
        'es': 'la comisión no puede ser negativa',
        'fr': 'les frais ne peuvent pas être négatifs',
        'de': 'die Gebühr darf nicht negativ sein',
        'pt': 'a taxa não pode ser negativa',
        'it': 'la commissione non può essere negativa',
        'ja': '手数料を負の値にはできません',
        'zh': '费用不能为负数',
        'hi': 'शुल्क ऋणात्मक नहीं हो सकता',
        'ar': 'لا يمكن أن تكون الرسوم سالبة',
    },
    'a size cannot be negative': {
        'es': 'el tamaño no puede ser negativo',
        'fr': 'la taille ne peut pas être négative',
        'de': 'die Größe darf nicht negativ sein',
        'pt': 'o tamanho não pode ser negativo',
        'it': 'la dimensione non può essere negativa',
        'ja': 'サイズを負の値にはできません',
        'zh': '尺寸不能为负数',
        'hi': 'आकार ऋणात्मक नहीं हो सकता',
        'ar': 'لا يمكن أن يكون الحجم سالبًا',
    },
    'an exchange needs two parties': {
        'es': 'un intercambio necesita dos partes',
        'fr': 'un échange a besoin de deux parties',
        'de': 'ein Austausch braucht zwei Parteien',
        'pt': 'uma troca precisa de duas partes',
        'it': 'uno scambio ha bisogno di due parti',
        'ja': 'やり取りには当事者が二者必要です',
        'zh': '交换需要两方',
        'hi': 'आदान-प्रदान के लिए दो पक्ष चाहिए',
        'ar': 'التبادل يحتاج إلى طرفين',
    },
    'direction is host_to_guest or guest_to_host': {
        'es': 'la dirección es host_to_guest o guest_to_host',
        'fr': 'la direction est host_to_guest ou guest_to_host',
        'de': 'die Richtung ist host_to_guest oder guest_to_host',
        'pt': 'a direção é host_to_guest ou guest_to_host',
        'it': 'la direzione è host_to_guest o guest_to_host',
        'ja': '方向は host_to_guest か guest_to_host です',
        'zh': '方向为 host_to_guest 或 guest_to_host',
        'hi': 'दिशा host_to_guest या guest_to_host होती है',
        'ar': 'الاتجاه هو host_to_guest أو guest_to_host',
    },
    'every item needs a name the other side will read': {
        'es': 'cada elemento necesita un nombre que la otra parte pueda leer',
        'fr': "chaque élément a besoin d'un nom que l'autre partie lira",
        'de': 'jeder Posten braucht einen Namen, den die andere Seite liest',
        'pt': 'cada item precisa de um nome que o outro lado vá ler',
        'it': "ogni voce ha bisogno di un nome che l'altra parte leggerà",
        'ja': '各項目には、相手が読む名前が必要です',
        'zh': '每一项都需要一个对方能看懂的名称',
        'hi': 'हर मद को एक नाम चाहिए जिसे दूसरा पक्ष पढ़ेगा',
        'ar': 'كل بند يحتاج اسمًا يقرأه الطرف الآخر',
    },
    'no such exchange': {
        'es': 'no existe ese intercambio',
        'fr': 'aucun échange de ce nom',
        'de': 'kein solcher Austausch',
        'pt': 'não existe essa troca',
        'it': 'nessuno scambio di questo tipo',
        'ja': 'そのようなやり取りはありません',
        'zh': '没有该交换',
        'hi': 'ऐसा कोई आदान-प्रदान नहीं',
        'ar': 'لا يوجد تبادل بهذا الوصف',
    },
    'no such item on this manifest': {
        'es': 'no existe ese elemento en esta lista',
        'fr': 'aucun élément de ce nom sur cette liste',
        'de': 'kein solcher Posten auf dieser Liste',
        'pt': 'não existe esse item nesta lista',
        'it': 'nessuna voce di questo tipo in questo elenco',
        'ja': 'この目録にそのような項目はありません',
        'zh': '此清单上没有该项目',
        'hi': 'इस सूची में ऐसी कोई मद नहीं',
        'ar': 'لا يوجد بند بهذا الوصف في هذا البيان',
    },
    'nothing can be accepted until both parties have signed this manifest': {
        'es': 'no se puede aceptar nada hasta que ambas partes hayan firmado esta lista',
        'fr': "rien ne peut être accepté tant que les deux parties n'ont pas signé cette liste",
        'de': 'nichts kann angenommen werden, bevor beide Parteien diese Liste unterschrieben haben',
        'pt': 'nada pode ser aceite enquanto ambas as partes não assinarem esta lista',
        'it': 'non si può accettare nulla finché entrambe le parti non hanno firmato questo elenco',
        'ja': '双方がこの目録に署名するまで、何も受け取れません',
        'zh': '在双方都签署这份清单之前，任何东西都不能接收',
        'hi': 'जब तक दोनों पक्ष इस सूची पर हस्ताक्षर न करें, कुछ भी स्वीकार नहीं हो सकता',
        'ar': 'لا يمكن قبول أي شيء حتى يوقّع الطرفان على هذا البيان',
    },
    'only the side receiving an item can accept it — the sender cannot accept on their behalf': {
        'es': 'solo la parte que recibe un elemento puede aceptarlo: quien lo envía no puede aceptar en su nombre',
        'fr': "seule la partie qui reçoit un élément peut l'accepter — l'expéditeur ne peut pas accepter à sa place",
        'de': 'nur die empfangende Seite kann einen Posten annehmen — die sendende kann das nicht für sie tun',
        'pt': 'só o lado que recebe um item o pode aceitar — quem envia não pode aceitar por ele',
        'it': 'solo la parte che riceve una voce può accettarla: chi la invia non può accettare al suo posto',
        'ja': '項目を受け取る側だけが受領できます。送る側が代わりに受領することはできません',
        'zh': '只有接收方能确认收下——发送方不能代其确认',
        'hi': 'किसी मद को केवल पाने वाला पक्ष स्वीकार कर सकता है — भेजने वाला उसकी ओर से नहीं',
        'ar': 'لا يقبل البند إلا الطرف المستلم — لا يمكن للمرسل القبول نيابة عنه',
    },
    'only the two parties can reopen this': {
        'es': 'solo las dos partes pueden reabrir esto',
        'fr': 'seules les deux parties peuvent rouvrir ceci',
        'de': 'nur die beiden Parteien können das wieder öffnen',
        'pt': 'só as duas partes podem reabrir isto',
        'it': 'solo le due parti possono riaprirlo',
        'ja': '再開できるのは当事者二者だけです',
        'zh': '只有这两方可以重新打开',
        'hi': 'इसे केवल दोनों पक्ष फिर से खोल सकते हैं',
        'ar': 'لا يمكن إعادة فتح هذا إلا للطرفين',
    },
    'only the two parties can sign this': {
        'es': 'solo las dos partes pueden firmar esto',
        'fr': 'seules les deux parties peuvent signer ceci',
        'de': 'nur die beiden Parteien können das unterschreiben',
        'pt': 'só as duas partes podem assinar isto',
        'it': 'solo le due parti possono firmarlo',
        'ja': '署名できるのは当事者二者だけです',
        'zh': '只有这两方可以签署',
        'hi': 'इस पर केवल दोनों पक्ष हस्ताक्षर कर सकते हैं',
        'ar': 'لا يمكن توقيع هذا إلا للطرفين',
    },
    'only the two parties can withdraw this': {
        'es': 'solo las dos partes pueden retirar esto',
        'fr': 'seules les deux parties peuvent retirer ceci',
        'de': 'nur die beiden Parteien können das zurückziehen',
        'pt': 'só as duas partes podem retirar isto',
        'it': 'solo le due parti possono ritirarlo',
        'ja': '取り下げられるのは当事者二者だけです',
        'zh': '只有这两方可以撤回',
        'hi': 'इसे केवल दोनों पक्ष वापस ले सकते हैं',
        'ar': 'لا يمكن سحب هذا إلا للطرفين',
    },
    'reopen the exchange to change the manifest': {
        'es': 'reabre el intercambio para cambiar la lista',
        'fr': "rouvrez l'échange pour modifier la liste",
        'de': 'öffne den Austausch wieder, um die Liste zu ändern',
        'pt': 'reabra a troca para alterar a lista',
        'it': "riapri lo scambio per modificare l'elenco",
        'ja': '目録を変えるには、やり取りを再開してください',
        'zh': '要修改清单，请重新打开这次交换',
        'hi': 'सूची बदलने के लिए आदान-प्रदान फिर से खोलें',
        'ar': 'أعد فتح التبادل لتغيير البيان',
    },
    'say what the work is, in one sentence': {
        'es': 'di en qué consiste el trabajo, en una frase',
        'fr': 'dites en une phrase en quoi consiste le travail',
        'de': 'sag in einem Satz, worin die Arbeit besteht',
        'pt': 'diga em que consiste o trabalho, numa frase',
        'it': "di' in una frase in cosa consiste il lavoro",
        'ja': 'どんな仕事か、一文で書いてください',
        'zh': '用一句话说明这是什么工作',
        'hi': 'एक वाक्य में बताइए कि काम क्या है',
        'ar': 'قل ما هو العمل، في جملة واحدة',
    },
    'there is nothing on the manifest — an empty agreement agrees to nothing in particular, which is the state people sign by accident': {
        'es': 'la lista está vacía: un acuerdo vacío no acuerda nada en concreto, y ese es el estado que la gente firma sin darse cuenta',
        'fr': "la liste est vide — un accord vide ne convient de rien en particulier, et c'est l'état que les gens signent par accident",
        'de': 'auf der Liste steht nichts — eine leere Vereinbarung vereinbart nichts Bestimmtes, und genau das unterschreiben Leute versehentlich',
        'pt': 'não há nada na lista — um acordo vazio não acorda nada em concreto, que é o estado que as pessoas assinam sem querer',
        'it': "l'elenco è vuoto: un accordo vuoto non concorda nulla in particolare, ed è lo stato che si firma per sbaglio",
        'ja': '目録に何もありません。空の合意は何も取り決めていません。人がうっかり署名してしまうのは、この状態です',
        'zh': '清单上什么都没有——空的协议没有约定任何具体内容，而这正是人们会误签的状态',
        'hi': 'सूची में कुछ नहीं है — खाली समझौता किसी खास बात पर सहमत नहीं होता, और यही वह स्थिति है जिस पर लोग गलती से हस्ताक्षर कर देते हैं',
        'ar': 'لا شيء في البيان — الاتفاق الفارغ لا يتفق على شيء بعينه، وهذه هي الحالة التي يوقّعها الناس عن غير قصد',
    },
    'this exchange is finished': {
        'es': 'este intercambio está terminado',
        'fr': 'cet échange est terminé',
        'de': 'dieser Austausch ist abgeschlossen',
        'pt': 'esta troca está concluída',
        'it': 'questo scambio è concluso',
        'ja': 'このやり取りは終了しています',
        'zh': '这次交换已经结束',
        'hi': 'यह आदान-प्रदान समाप्त हो चुका है',
        'ar': 'انتهى هذا التبادل',
    },
    'this exchange is not editable — reopen it to change the manifest, which clears both signatures': {
        'es': 'este intercambio no se puede editar: reábrelo para cambiar la lista, lo que borra ambas firmas',
        'fr': "cet échange n'est pas modifiable — rouvrez-le pour changer la liste, ce qui efface les deux signatures",
        'de': 'dieser Austausch ist nicht bearbeitbar — öffne ihn wieder, um die Liste zu ändern; das löscht beide Unterschriften',
        'pt': 'esta troca não é editável — reabra-a para alterar a lista, o que apaga ambas as assinaturas',
        'it': "questo scambio non è modificabile: riaprilo per cambiare l'elenco, cosa che cancella entrambe le firme",
        'ja': 'このやり取りは編集できません。目録を変えるには再開してください。両方の署名が消えます',
        'zh': '这次交换不可编辑——重新打开它才能改清单，这会清除双方签名',
        'hi': 'इस आदान-प्रदान को संपादित नहीं किया जा सकता — सूची बदलने के लिए इसे फिर से खोलें, जिससे दोनों हस्ताक्षर मिट जाते हैं',
        'ar': 'هذا التبادل غير قابل للتعديل — أعد فتحه لتغيير البيان، وهذا يمسح التوقيعين',
    },
    'there is nowhere here to keep that credential sealed, so it will not be kept at all — this needs a plan with a vault behind it, on a deployment that has one': {
        'es': 'aquí no hay dónde guardar esa credencial sellada, así que no se guardará en absoluto: hace falta un plan con bóveda detrás, en una instalación que tenga una',
        'fr': "il n'y a ici nulle part où garder cette information scellée, elle ne sera donc pas gardée du tout — il faut un forfait avec un coffre derrière, sur un déploiement qui en possède un",
        'de': 'hier gibt es keinen Ort, um diese Zugangsdaten versiegelt aufzubewahren, also werden sie gar nicht aufbewahrt — dafür braucht es einen Tarif mit Tresor, auf einer Installation, die einen hat',
        'pt': 'não há aqui onde guardar essa credencial selada, por isso não será guardada de todo — isto precisa de um plano com cofre por trás, numa instalação que tenha um',
        'it': "qui non c'è nessun posto dove tenere sigillata quella credenziale, quindi non verrà tenuta affatto: serve un piano con una cassaforte dietro, su un'installazione che ne abbia una",
        'ja': 'その資格情報を封印して置いておける場所がここにはないので、まったく保管しません。金庫のあるプランと、金庫を備えた環境が必要です。',
        'zh': '这里没有地方能把那份凭据封存起来，所以根本不会保存它——这需要一个背后有保险库的套餐，且部署本身也要有保险库。',
        'hi': 'उस क्रेडेंशियल को सील करके रखने की जगह यहाँ नहीं है, इसलिए इसे रखा ही नहीं जाएगा — इसके लिए तिजोरी वाला प्लान चाहिए, और ऐसी तैनाती जिसमें तिजोरी हो।',
        'ar': 'لا يوجد هنا مكان لحفظ تلك البيانات مختومة، لذا لن تُحفظ إطلاقًا — يحتاج هذا إلى خطة وراءها خزنة، على نشر يملك واحدة.',
    },
    'a link starts with http:// or https://': {
        'es': 'un enlace empieza por http:// o https://',
        'fr': "un lien commence par http:// ou https://",
        'de': 'ein Link beginnt mit http:// oder https://',
        'pt': 'um link começa por http:// ou https://',
        'it': 'un link comincia con http:// o https://',
        'ja': 'リンクは http:// または https:// で始まります。',
        'zh': '链接以 http:// 或 https:// 开头。',
        'hi': 'लिंक http:// या https:// से शुरू होता है।',
        'ar': 'الرابط يبدأ بـ http:// أو https://',
    },
    'no such imported item in this conversation': {
        'es': 'no hay ningún elemento importado así en esta conversación',
        'fr': "aucun élément importé de ce genre dans cette conversation",
        'de': 'in diesem Gespräch gibt es kein solches importiertes Element',
        'pt': 'não há nenhum item importado assim nesta conversa',
        'it': 'in questa conversazione non c’è nessun elemento importato così',
        'ja': 'この会話にそのような取り込み済みの資料はありません。',
        'zh': '这场对话里没有这样一份已导入的材料。',
        'hi': 'इस बातचीत में ऐसा कोई आयातित आइटम नहीं है।',
        'ar': 'لا يوجد عنصر مستورد بهذا الوصف في هذه المحادثة.',
    },
    'the upload arrived empty': {
        'es': 'la subida llegó vacía',
        'fr': "l’envoi est arrivé vide",
        'de': 'der Upload kam leer an',
        'pt': 'o carregamento chegou vazio',
        'it': 'il caricamento è arrivato vuoto',
        'ja': 'アップロードは空のまま届きました。',
        'zh': '上传过来的内容是空的。',
        'hi': 'अपलोड खाली आया।',
        'ar': 'وصل الرفع فارغًا.',
    },
    'kind is one of image, video, file — or leave it off': {
        'es': 'kind es image, video o file — o déjelo sin poner',
        'fr': "kind vaut image, video ou file — ou bien laissez-le de côté",
        'de': 'kind ist image, video oder file — oder lassen Sie es weg',
        'pt': 'kind é image, video ou file — ou deixe-o de fora',
        'it': 'kind è image, video o file — oppure lascialo perdere',
        'ja': 'kind は image、video、file のいずれかです。指定しなくても構いません。',
        'zh': 'kind 只能是 image、video 或 file——不填也可以。',
        'hi': 'kind इनमें से एक है: image, video, file — या इसे छोड़ दें।',
        'ar': 'kind يكون image أو video أو file — أو اتركه دون تحديد.',
    },
    'Something went wrong on our side. Nothing you sent was recorded.': {
        'es': 'Algo falló de nuestro lado. No se registró nada de lo que envió.',
        'fr': "Quelque chose a échoué de notre côté. Rien de ce que vous avez envoyé n'a été enregistré.",
        'de': 'Auf unserer Seite ist etwas schiefgegangen. Nichts von dem, was Sie gesendet haben, wurde gespeichert.',
        'pt': 'Algo correu mal do nosso lado. Nada do que enviou ficou registado.',
        'it': 'Qualcosa è andato storto dalla nostra parte. Nulla di ciò che ha inviato è stato registrato.',
        'ja': 'こちら側で問題が発生しました。送信された内容は記録されていません。',
        'zh': '我们这边出了问题。您发送的内容没有被记录。',
        'hi': 'हमारी ओर से कुछ गड़बड़ हो गई। आपने जो भेजा, वह दर्ज नहीं हुआ।',
        'ar': 'حدث خطأ من جانبنا. لم يُسجَّل أي شيء أرسلته.',
    },
    "this deployment's interpreter is too old to hold a widget in, so nothing will run here": {
        'es': 'el intérprete de esta instalación es demasiado antiguo para contener un widget, así que aquí no se ejecutará nada',
        'fr': "l'interpréteur de cette installation est trop ancien pour contenir un widget ; rien ne s'exécutera ici",
        'de': 'der Interpreter dieser Installation ist zu alt, um ein Widget einzuschließen — hier läuft nichts',
        'pt': 'o interpretador desta instalação é demasiado antigo para conter um widget, por isso nada correrá aqui',
        'it': "l'interprete di questa installazione è troppo vecchio per contenere un widget, quindi qui non girerà nulla",
        'ja': 'この配備のインタープリターは古すぎてウィジェットを閉じ込められないため、ここでは何も実行されません。',
        'zh': '本部署的解释器太旧，无法把小工具关进箱子里，因此这里不会运行任何东西。',
        'hi': 'इस डिप्लॉयमेंट का इंटरप्रेटर इतना पुराना है कि विजेट को बॉक्स में नहीं रख सकता, इसलिए यहाँ कुछ नहीं चलेगा।',
        'ar': 'مفسّر هذا النشر أقدم من أن يحتوي أداة داخل صندوق، لذا لن يُشغَّل شيء هنا.',
    },
    'this deployment cannot cap what a widget may use, so nothing will run here': {
        'es': 'esta instalación no puede limitar lo que un widget puede consumir, así que aquí no se ejecutará nada',
        'fr': "cette installation ne peut pas plafonner ce qu'un widget consomme ; rien ne s'exécutera ici",
        'de': 'diese Installation kann nicht begrenzen, was ein Widget verbraucht — hier läuft nichts',
        'pt': 'esta instalação não consegue limitar o que um widget pode consumir, por isso nada correrá aqui',
        'it': "questa installazione non può limitare ciò che un widget consuma, quindi qui non girerà nulla",
        'ja': 'この配備はウィジェットが使える量に上限をかけられないため、ここでは何も実行されません。',
        'zh': '本部署无法限制小工具能占用多少资源，因此这里不会运行任何东西。',
        'hi': 'यह डिप्लॉयमेंट यह सीमित नहीं कर सकता कि विजेट कितना इस्तेमाल करे, इसलिए यहाँ कुछ नहीं चलेगा।',
        'ar': 'لا يستطيع هذا النشر تحديد سقف لما تستهلكه الأداة، لذا لن يُشغَّل شيء هنا.',
    },
    'say what you would like changed': {
        'es': 'diga qué le gustaría cambiar',
        'fr': "dites ce que vous souhaitez changer",
        'de': 'sagen Sie, was Sie ändern möchten',
        'pt': 'diga o que gostaria de mudar',
        'it': 'dica che cosa vorrebbe cambiare',
        'ja': '何を変えたいかを書いてください。',
        'zh': '请说明您想改动什么。',
        'hi': 'बताइए आप क्या बदलना चाहते हैं।',
        'ar': 'قل ما الذي تريد تغييره.',
    },
    'the model did not answer': {
        'es': 'el modelo no respondió',
        'fr': "le modèle n'a pas répondu",
        'de': 'das Modell hat nicht geantwortet',
        'pt': 'o modelo não respondeu',
        'it': 'il modello non ha risposto',
        'ja': 'モデルから応答がありませんでした。',
        'zh': '模型没有回应。',
        'hi': 'मॉडल ने उत्तर नहीं दिया।',
        'ar': 'لم يُجب النموذج.',
    },
    "the model's answer could not be read as a request": {
        'es': 'la respuesta del modelo no pudo leerse como una petición',
        'fr': "la réponse du modèle n'a pas pu être lue comme une demande",
        'de': 'die Antwort des Modells ließ sich nicht als Anfrage lesen',
        'pt': 'a resposta do modelo não pôde ser lida como um pedido',
        'it': 'la risposta del modello non è stata leggibile come richiesta',
        'ja': 'モデルの答えを要求として読み取れませんでした。',
        'zh': '模型的回答无法解析为一次请求。',
        'hi': 'मॉडल का उत्तर एक अनुरोध के रूप में पढ़ा नहीं जा सका।',
        'ar': 'تعذّرت قراءة إجابة النموذج كطلب.',
    },
    'the model asked for something it does not have': {
        'es': 'el modelo pidió algo que no tiene',
        'fr': "le modèle a demandé quelque chose qu'il n'a pas",
        'de': 'das Modell hat etwas verlangt, das es nicht hat',
        'pt': 'o modelo pediu algo que não tem',
        'it': 'il modello ha chiesto qualcosa che non ha',
        'ja': 'モデルは持っていないものを求めました。',
        'zh': '模型索取了它并不具备的东西。',
        'hi': 'मॉडल ने ऐसी चीज़ माँगी जो उसके पास नहीं है।',
        'ar': 'طلب النموذج شيئًا لا يملكه.',
    },
    'that step runs inside a turn and was not one to confirm': {
        'es': 'ese paso se ejecuta dentro del turno y no era de los que se confirman',
        'fr': "cette étape s'exécute dans le tour et n'était pas de celles à confirmer",
        'de': 'dieser Schritt läuft innerhalb des Zuges und war keiner zum Bestätigen',
        'pt': 'esse passo corre dentro do turno e não era dos que se confirmam',
        'it': 'quel passo viene eseguito nel turno e non era da confermare',
        'ja': 'その手順はやり取りの中で実行されるもので、確認を求める種類ではありません。',
        'zh': '该步骤在对话回合内执行，本就不需要确认。',
        'hi': 'वह चरण बातचीत के भीतर ही चलता है; वह पुष्टि माँगने वालों में नहीं था।',
        'ar': 'تلك الخطوة تُنفَّذ داخل الدور ولم تكن مما يُستأذن فيه.',
    },
    'the model tried to change something that step does not reach': {
        'es': 'el modelo intentó cambiar algo que ese paso no alcanza',
        'fr': "le modèle a tenté de modifier quelque chose que cette étape n'atteint pas",
        'de': 'das Modell wollte etwas ändern, das dieser Schritt nicht erreicht',
        'pt': 'o modelo tentou alterar algo que esse passo não alcança',
        'it': 'il modello ha tentato di cambiare qualcosa che quel passo non raggiunge',
        'ja': 'モデルは、その手順が及ばないものを変更しようとしました。',
        'zh': '模型试图更改该步骤触及不到的东西。',
        'hi': 'मॉडल ने ऐसी चीज़ बदलने की कोशिश की जहाँ वह चरण पहुँचता ही नहीं।',
        'ar': 'حاول النموذج تغيير شيء لا تبلغه تلك الخطوة.',
    },
    'the model left out something the step needs': {
        'es': 'el modelo omitió algo que el paso necesita',
        'fr': "le modèle a omis quelque chose dont l'étape a besoin",
        'de': 'das Modell hat etwas ausgelassen, das der Schritt braucht',
        'pt': 'o modelo omitiu algo de que o passo precisa',
        'it': 'il modello ha tralasciato qualcosa che il passaggio richiede',
        'ja': 'モデルはその手順に必要なものを書き落としました。',
        'zh': '模型漏掉了该步骤所需的内容。',
        'hi': 'मॉडल उस चरण के लिए ज़रूरी कुछ छोड़ गया।',
        'ar': 'أغفل النموذج شيئًا تحتاجه هذه الخطوة.',
    },
    'that step did not finish': {
        'es': 'ese paso no se completó',
        'fr': "cette étape ne s'est pas achevée",
        'de': 'dieser Schritt wurde nicht abgeschlossen',
        'pt': 'esse passo não chegou ao fim',
        'it': 'quel passaggio non si è concluso',
        'ja': 'その手順は完了しませんでした。',
        'zh': '该步骤没有完成。',
        'hi': 'वह चरण पूरा नहीं हुआ।',
        'ar': 'لم تكتمل تلك الخطوة.',
    },
    'this went on longer than one turn allows — ask again for something narrower': {
        'es': 'esto se alargó más de lo que permite un turno: pida algo más acotado',
        'fr': "cela a duré plus qu'un tour ne le permet — redemandez quelque chose de plus restreint",
        'de': 'das dauerte länger, als ein Zug erlaubt — fragen Sie nach etwas Engerem',
        'pt': 'isto prolongou-se mais do que uma vez permite — peça algo mais restrito',
        'it': "è andata avanti più di quanto un turno consenta — chieda qualcosa di più circoscritto",
        'ja': '一度のやり取りで許される長さを超えました。もっと絞った内容で頼んでください。',
        'zh': '这超出了一次交互允许的长度 — 请换个更窄的要求再问。',
        'hi': 'यह एक बार में जितना चल सकता है उससे लंबा हो गया — कुछ और सीमित माँगिए।',
        'ar': 'استغرق هذا أطول مما تسمح به جولة واحدة — اطلب شيئًا أضيق.',
    },
    'no such handoff — mint a fresh ticket': {
        'es': 'no existe esa entrega — genera un vale nuevo',
        'fr': "ce transfert n'existe pas — émettez un nouveau ticket",
        'de': 'keine solche Übergabe — stellen Sie ein frisches Ticket aus',
        'pt': 'essa entrega não existe — emita um bilhete novo',
        'it': 'nessuna consegna del genere — emetti un biglietto nuovo',
        'ja': 'その受け渡しは存在しません — 新しいチケットを発行してください',
        'zh': '没有这个交接——请重新生成一张票据',
        'hi': 'ऐसा कोई हस्तांतरण नहीं — नया टिकट बनाएँ',
        'ar': 'لا يوجد تسليم كهذا — أصدر تذكرة جديدة',
    },
    'this handoff has already been used or has expired — '
    'mint a fresh ticket': {
        'es': 'esta entrega ya se usó o ha caducado — genera un vale nuevo',
        'fr': 'ce transfert a déjà servi ou a expiré — émettez un nouveau '
              'ticket',
        'de': 'diese Übergabe wurde schon benutzt oder ist abgelaufen — '
              'stellen Sie ein frisches Ticket aus',
        'pt': 'esta entrega já foi usada ou expirou — emita um bilhete novo',
        'it': 'questa consegna è già stata usata o è scaduta — emetti un '
              'biglietto nuovo',
        'ja': 'この受け渡しは使用済みか期限切れです — 新しいチケットを発行してください',
        'zh': '这个交接已被使用或已过期——请重新生成一张票据',
        'hi': 'यह हस्तांतरण इस्तेमाल हो चुका है या समाप्त हो गया — नया टिकट बनाएँ',
        'ar': 'استُخدم هذا التسليم من قبل أو انتهت صلاحيته — أصدر تذكرة جديدة',
    },
    'reading the failure map requires the QRME_PROBLEMS_KEY bearer token': {
        'es': 'leer el mapa de fallos requiere el token portador '
              'QRME_PROBLEMS_KEY',
        'fr': 'lire la carte des échecs exige le jeton porteur '
              'QRME_PROBLEMS_KEY',
        'de': 'das Lesen der Fehlerkarte erfordert das '
              'QRME_PROBLEMS_KEY-Bearer-Token',
        'pt': 'ler o mapa de falhas requer o token portador '
              'QRME_PROBLEMS_KEY',
        'it': 'leggere la mappa dei guasti richiede il token bearer '
              'QRME_PROBLEMS_KEY',
        'ja': '障害マップの閲覧には QRME_PROBLEMS_KEY のベアラートークンが必要です',
        'zh': '读取故障图需要 QRME_PROBLEMS_KEY 持有者令牌',
        'hi': 'विफलता मानचित्र पढ़ने के लिए QRME_PROBLEMS_KEY बियरर टोकन चाहिए',
        'ar': 'قراءة خريطة الأعطال تتطلب رمز QRME_PROBLEMS_KEY الحامل',
    },
    'wrong problems key': {
        'es': 'clave de problemas incorrecta',
        'fr': 'mauvaise clé des problèmes',
        'de': 'falscher Problems-Schlüssel',
        'pt': 'chave de problemas errada',
        'it': 'chiave dei problemi sbagliata',
        'ja': 'problemsキーが違います',
        'zh': '问题密钥不正确',
        'hi': 'समस्याओं की कुंजी ग़लत है',
        'ar': 'مفتاح المشاكل خاطئ',
    },
    'the failure aggregate is readable from this machine only until '
    'QRME_PROBLEMS_KEY is set — behind a proxy, set it': {
        'es': 'el agregado de fallos solo se puede leer desde esta máquina '
              'hasta que se fije QRME_PROBLEMS_KEY — tras un proxy, fíjala',
        'fr': "l'agrégat des échecs n'est lisible que depuis cette machine "
              'tant que QRME_PROBLEMS_KEY n\'est pas définie — derrière un '
              'proxy, définissez-la',
        'de': 'das Fehleraggregat ist nur von dieser Maschine lesbar, bis '
              'QRME_PROBLEMS_KEY gesetzt ist — hinter einem Proxy: setzen',
        'pt': 'o agregado de falhas só pode ser lido a partir desta máquina '
              'até QRME_PROBLEMS_KEY estar definida — atrás de um proxy, '
              'defina-a',
        'it': "l'aggregato dei guasti è leggibile solo da questa macchina "
              'finché QRME_PROBLEMS_KEY non è impostata — dietro un proxy, '
              'impostala',
        'ja': '障害の集計は QRME_PROBLEMS_KEY を設定するまでこの機械からしか読めません — '
              'プロキシの背後では設定してください',
        'zh': '在设置 QRME_PROBLEMS_KEY 之前，故障汇总只能从本机读取——在代理之后请务必设置',
        'hi': 'जब तक QRME_PROBLEMS_KEY निर्धारित नहीं होती, विफलता समग्र केवल इसी '
              'मशीन से पढ़ा जा सकता है — प्रॉक्सी के पीछे इसे निर्धारित करें',
        'ar': 'لا يمكن قراءة مجمّع الأعطال إلا من هذا الجهاز حتى يُعيَّن '
              'QRME_PROBLEMS_KEY — خلف وكيل، عيِّنه',
    },
    'only the host decides where a party can be found': {
        'es': 'solo el anfitrión decide dónde se puede encontrar una sala',
        'fr': "seul l'hôte décide où une séance peut être trouvée",
        'de': 'nur der Gastgeber entscheidet, wo eine Party zu finden ist',
        'pt': 'só o anfitrião decide onde uma sessão pode ser encontrada',
        'it': "solo l'ospite decide dove una festa può essere trovata",
        'ja': 'パーティを公開する場所を決められるのはホストだけです',
        'zh': '只有主持人能决定放映会在哪里被找到',
        'hi': 'केवल मेज़बान तय करता है कि पार्टी कहाँ मिल सकती है',
        'ar': 'المضيف وحده يقرر أين يمكن العثور على الجلسة',
    },
    'a public party needs a title people can find it by': {
        'es': 'una sala pública necesita un título por el que la gente pueda encontrarla',
        'fr': "une séance publique a besoin d'un titre par lequel on peut la trouver",
        'de': 'eine öffentliche Party braucht einen Titel, unter dem man sie finden kann',
        'pt': 'uma sessão pública precisa de um título pelo qual as pessoas a encontrem',
        'it': 'una festa pubblica ha bisogno di un titolo con cui trovarla',
        'ja': '公開パーティには、人が見つけられるタイトルが必要です',
        'zh': '公开放映会需要一个能让人找到它的标题',
        'hi': 'सार्वजनिक पार्टी को एक शीर्षक चाहिए जिससे लोग उसे ढूँढ सकें',
        'ar': 'الجلسة العامة تحتاج إلى عنوان يجدها الناس به',
    },
    'that title cannot stand on a public surface': {
        'es': 'ese título no puede estar en una superficie pública',
        'fr': 'ce titre ne peut pas figurer sur une surface publique',
        'de': 'dieser Titel kann auf einer öffentlichen Fläche nicht stehen',
        'pt': 'esse título não pode ficar numa superfície pública',
        'it': 'quel titolo non può stare su una superficie pubblica',
        'ja': 'そのタイトルは公開の場には掲載できません',
        'zh': '这个标题不能出现在公开界面上',
        'hi': 'वह शीर्षक सार्वजनिक सतह पर नहीं रह सकता',
        'ar': 'هذا العنوان لا يمكن أن يظهر على واجهة عامة',
    },
    'nothing posted has that id — give the id of a posted video, or paste the video\'s own link': {
        'es': 'nada publicado tiene ese id — da el id de un vídeo publicado, o pega el enlace del propio vídeo',
        'fr': "rien de publié ne porte cet id — donnez l'id d'une vidéo publiée, ou collez le lien de la vidéo elle-même",
        'de': 'nichts Veröffentlichtes trägt diese ID — gib die ID eines veröffentlichten Videos an, oder füge den Link des Videos selbst ein',
        'pt': 'nada publicado tem esse id — dá o id de um vídeo publicado, ou cola o link do próprio vídeo',
        'it': "niente di pubblicato ha quell'id — dai l'id di un video pubblicato, o incolla il link del video stesso",
        'ja': 'そのIDの投稿はありません — 投稿された動画のIDを入力するか、動画自体のリンクを貼り付けてください',
        'zh': '没有帖子是这个 ID — 请提供已发布视频的帖子 ID，或直接粘贴视频链接',
        'hi': 'इस आईडी की कोई पोस्ट नहीं है — किसी पोस्ट किए गए वीडियो की आईडी दें, या वीडियो का लिंक चिपकाएँ',
        'ar': 'لا يوجد منشور بهذا المعرّف — أعط معرّف فيديو منشور، أو الصق رابط الفيديو نفسه',
    },
    'say what is being rehearsed — an empty scenario gives the counterpart nothing to play': {
        'es': 'di qué se ensaya — un escenario vacío no le da nada que interpretar a la contraparte',
        'fr': "dites ce qui se répète — un scénario vide ne donne rien à jouer à l'interlocuteur",
        'de': 'sag, was geprobt wird — ein leeres Szenario gibt dem Gegenüber nichts zu spielen',
        'pt': 'diz o que se ensaia — um cenário vazio não dá nada à contraparte para representar',
        'it': "di' cosa si prova — uno scenario vuoto non dà nulla da recitare alla controparte",
        'ja': '何を練習するのか言ってください — 空のシナリオでは相手役に演じるものがありません',
        'zh': '说明要排练什么 — 空白的情境让对手无从扮演',
        'hi': 'बताएँ क्या अभ्यास हो रहा है — खाली परिदृश्य में सामने वाले के निभाने को कुछ नहीं',
        'ar': 'قل ما الذي يُتدرَّب عليه — سيناريو فارغ لا يعطي الطرف الآخر شيئًا يؤديه',
    },
    'an empty line rehearses nothing': {
        'es': 'una línea vacía no ensaya nada',
        'fr': 'une réplique vide ne répète rien',
        'de': 'eine leere Zeile probt nichts',
        'pt': 'uma fala vazia não ensaia nada',
        'it': 'una battuta vuota non prova nulla',
        'ja': '空のセリフでは何も練習できません',
        'zh': '空白的台词排练不了任何东西',
        'hi': 'खाली पंक्ति से कोई अभ्यास नहीं होता',
        'ar': 'سطر فارغ لا يتدرب على شيء',
    },
    'no such rehearsal — the room may already be closed and wiped': {
        'es': 'no existe ese ensayo — puede que la sala ya esté cerrada y borrada',
        'fr': "cette répétition n'existe pas — la salle est peut-être déjà fermée et effacée",
        'de': 'keine solche Probe — der Raum ist womöglich schon geschlossen und gelöscht',
        'pt': 'esse ensaio não existe — a sala pode já estar fechada e apagada',
        'it': "quella prova non esiste — la stanza potrebbe essere già chiusa e cancellata",
        'ja': 'そのリハーサルはありません — 部屋はすでに閉じられ消去されたのかもしれません',
        'zh': '没有这个排练 — 房间可能已被关闭并抹除',
        'hi': 'ऐसा कोई पूर्वाभ्यास नहीं — कमरा शायद पहले ही बंद और मिटाया जा चुका है',
        'ar': 'لا بروفة كهذه — لعل الغرفة أُغلقت ومُحيت بالفعل',
    },
    'the steering is locked; these dials do not move until the owner unlocks them': {
        'es': 'la dirección está bloqueada; estos diales no se mueven hasta que el propietario los desbloquee',
        'fr': "le pilotage est verrouillé ; ces cadrans ne bougeront pas tant que le propriétaire ne les aura pas déverrouillés",
        'de': 'die Steuerung ist gesperrt; diese Regler bewegen sich nicht, bis der Eigentümer sie entsperrt',
        'pt': 'a direção está bloqueada; estes mostradores não se movem até o proprietário os desbloquear',
        'it': 'lo sterzo è bloccato; queste manopole non si muovono finché il proprietario non le sblocca',
        'ja': 'ステアリングはロックされています。所有者が解除するまで、これらのダイヤルは動きません',
        'zh': '转向已锁定；在所有者解锁之前，这些旋钮不会移动',
        'hi': 'स्टीयरिंग बंद है; जब तक स्वामी नहीं खोलते, ये डायल नहीं हिलेंगे',
        'ar': 'التوجيه مقفل؛ لا تتحرك هذه الأقراص حتى يفتحها المالك',
    },
    'say what to forget — empty words strike nothing': {
        'es': 'di qué olvidar — las palabras vacías no borran nada',
        'fr': "dites quoi oublier — des mots vides n'effacent rien",
        'de': 'sag, was vergessen werden soll — leere Worte streichen nichts',
        'pt': 'diz o que esquecer — palavras vazias não riscam nada',
        'it': 'di\' cosa dimenticare — parole vuote non cancellano nulla',
        'ja': '何を忘れるか言ってください — 空の言葉では何も消せません',
        'zh': '说明要忘记什么 — 空洞的词语抹不掉任何东西',
        'hi': 'बताएँ क्या भुलाना है — खाली शब्द कुछ नहीं मिटाते',
        'ar': 'قل ما الذي يُنسى — الكلمات الفارغة لا تمحو شيئًا',
    },
    'nothing remembered here carries those words': {
        'es': 'nada de lo recordado aquí lleva esas palabras',
        'fr': 'rien de ce qui est retenu ici ne porte ces mots',
        'de': 'nichts hier Erinnertes trägt diese Worte',
        'pt': 'nada do que aqui se lembra carrega essas palavras',
        'it': 'nulla di ciò che è ricordato qui porta quelle parole',
        'ja': 'ここで記憶されているものに、その言葉はありません',
        'zh': '这里记住的内容中没有这些词',
        'hi': 'यहाँ याद रखी किसी बात में वे शब्द नहीं हैं',
        'ar': 'لا شيء مما هو محفوظ هنا يحمل تلك الكلمات',
    },
    'select at least one turn — nothing was struck': {
        'es': 'seleccione al menos un turno — no se borró nada',
        'fr': 'sélectionnez au moins un tour — rien n\'a été effacé',
        'de': 'wählen Sie mindestens einen Beitrag — nichts wurde gestrichen',
        'pt': 'selecione pelo menos um turno — nada foi apagado',
        'it': 'seleziona almeno un turno — nulla è stato cancellato',
        'ja': '少なくとも一つの発言を選択してください — 何も削除されませんでした',
        'zh': '至少选择一条发言 — 没有删除任何内容',
        'hi': 'कम से कम एक बारी चुनें — कुछ भी नहीं हटाया गया',
        'ar': 'اختر مداخلة واحدة على الأقل — لم يُحذف شيء',
    },
    'none of those turns are in this memory': {
        'es': 'ninguno de esos turnos está en esta memoria',
        'fr': 'aucun de ces tours n\'est dans cette mémoire',
        'de': 'keiner dieser Beiträge ist in diesem Gedächtnis',
        'pt': 'nenhum desses turnos está nesta memória',
        'it': 'nessuno di quei turni è in questa memoria',
        'ja': 'それらの発言はこの記憶の中にありません',
        'zh': '这些发言都不在这段记忆中',
        'hi': 'उनमें से कोई भी बारी इस स्मृति में नहीं है',
        'ar': 'لا شيء من تلك المداخلات موجود في هذه الذاكرة',
    },
    'no remembered turn has that id': {
        'es': 'ningún turno recordado tiene ese identificador',
        'fr': 'aucun tour retenu ne porte cet identifiant',
        'de': 'kein erinnerter Beitrag trägt diese Kennung',
        'pt': 'nenhum turno lembrado tem esse identificador',
        'it': 'nessun turno ricordato ha quell\'identificativo',
        'ja': 'その ID を持つ記憶された発言はありません',
        'zh': '没有记住的发言带有该标识',
        'hi': 'किसी याद रखी बारी की वह पहचान नहीं है',
        'ar': 'لا توجد مداخلة محفوظة بهذا المعرّف',
    },
    'say what the turn should say — to remove it, strike it instead': {
        'es': 'diga qué debe decir el turno — para quitarlo, bórrelo en su lugar',
        'fr': 'dites ce que le tour doit dire — pour le retirer, effacez-le plutôt',
        'de': 'sagen Sie, was der Beitrag sagen soll — zum Entfernen streichen Sie ihn stattdessen',
        'pt': 'diga o que o turno deve dizer — para removê-lo, apague-o em vez disso',
        'it': 'di\' cosa deve dire il turno — per rimuoverlo, cancellalo invece',
        'ja': '発言の内容を書いてください — 削除したい場合は代わりに削除操作を使ってください',
        'zh': '写出这条发言应说的内容 — 要移除它，请改用删除',
        'hi': 'बताएँ कि बारी में क्या कहा जाए — हटाने के लिए इसके बजाय मिटाएँ',
        'ar': 'اكتب ما ينبغي أن تقوله المداخلة — لإزالتها احذفها بدلاً من ذلك',
    },
    'those words cannot stand in this record': {
        'es': 'esas palabras no pueden permanecer en este registro',
        'fr': 'ces mots ne peuvent pas rester dans ce registre',
        'de': 'diese Worte können in dieser Aufzeichnung nicht bestehen',
        'pt': 'essas palavras não podem permanecer neste registro',
        'it': 'quelle parole non possono restare in questo registro',
        'ja': 'その言葉はこの記録に残せません',
        'zh': '这些词不能留在这份记录中',
        'hi': 'वे शब्द इस अभिलेख में नहीं रह सकते',
        'ar': 'تلك الكلمات لا يمكن أن تبقى في هذا السجل',
    },
    'that platform shows a signed-out visitor only its login wall, so there is nothing of the account to import — copy the profile\'s text while signed in and paste it into collect instead': {
        'es': 'esa plataforma solo muestra su muro de inicio de sesión a un visitante sin sesión, así que no hay nada de la cuenta que importar: copia el texto del perfil con la sesión iniciada y pégalo en recopilar.',
        'fr': "cette plateforme ne montre à un visiteur non connecté que son mur de connexion, il n'y a donc rien du compte à importer — copiez le texte du profil en étant connecté et collez-le dans la collecte.",
        'de': 'diese Plattform zeigt einem nicht angemeldeten Besucher nur ihre Anmeldewand, es gibt also nichts vom Konto zu importieren — kopiere den Text des Profils im angemeldeten Zustand und füge ihn beim Sammeln ein.',
        'pt': 'essa plataforma mostra a um visitante sem sessão apenas o seu muro de início de sessão, por isso não há nada da conta para importar — copia o texto do perfil com sessão iniciada e cola-o na recolha.',
        'it': 'quella piattaforma mostra a un visitatore non connesso solo il proprio muro di accesso, quindi non c\'è nulla dell\'account da importare — copia il testo del profilo da connesso e incollalo nella raccolta.',
        'ja': 'そのプラットフォームは、ログインしていない訪問者にはログイン画面しか見せないため、アカウントから取り込めるものはありません。ログインした状態でプロフィールの文章をコピーし、収集に貼り付けてください。',
        'zh': '该平台对未登录的访客只显示登录墙，因此没有任何账号内容可导入——请在登录状态下复制个人主页的文字，粘贴到收集里。',
        'hi': 'वह प्लैटफ़ॉर्म बिना साइन-इन आगंतुक को केवल अपनी लॉगिन दीवार दिखाता है, इसलिए खाते से आयात करने को कुछ नहीं है — साइन इन करके प्रोफ़ाइल का पाठ कॉपी करें और उसे संग्रह में चिपकाएँ।',
        'ar': 'تلك المنصة لا تُظهر للزائر غير المسجّل سوى جدار تسجيل الدخول، فلا شيء من الحساب يمكن استيراده — انسخ نص الملف وأنت مسجّل الدخول وألصقه في التجميع.',
    },
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
    'no standing room by that name': {
        'es': 'no hay sala permanente con ese nombre.',
        'fr': 'aucune salle permanente ne porte ce nom.',
        'de': 'kein ständiger Raum trägt diesen Namen.',
        'pt': 'não há sala permanente com esse nome.',
        'it': 'nessuna stanza permanente con quel nome.',
        'ja': 'その名前の常設の部屋はありません。',
        'zh': '没有这个名字的常设房间。',
        'hi': 'उस नाम का कोई स्थायी कमरा नहीं है।',
        'ar': 'لا توجد غرفة دائمة بهذا الاسم.',
    },
    'nobody has this room open yet, and a room opens with you and a profile in it — pick a profile first': {
        'es': 'nadie tiene esta sala abierta todavía, y una sala se abre contigo y un perfil dentro: elige primero un perfil.',
        'fr': "personne n'a encore ouvert cette salle, et une salle s'ouvre avec vous et un profil à l'intérieur — choisissez d'abord un profil.",
        'de': 'niemand hat diesen Raum bisher geöffnet, und ein Raum öffnet sich mit dir und einem Profil darin — wähle zuerst ein Profil.',
        'pt': 'ninguém tem esta sala aberta ainda, e uma sala abre-se contigo e um perfil lá dentro — escolhe primeiro um perfil.',
        'it': 'nessuno ha ancora aperto questa stanza, e una stanza si apre con te e un profilo dentro — scegli prima un profilo.',
        'ja': 'この部屋はまだ誰も開いていません。部屋はあなたとプロフィールが中にいる状態で開きます。先にプロフィールを選んでください。',
        'zh': '还没有人开这个房间，而房间开启时要有你和一个档案在里面——请先选择一个档案。',
        'hi': 'अभी किसी ने यह कमरा नहीं खोला है, और कमरा आपके और एक प्रोफ़ाइल के भीतर होने से खुलता है — पहले एक प्रोफ़ाइल चुनें।',
        'ar': 'لم يفتح أحد هذه الغرفة بعد، والغرفة تُفتح وأنت وملف بداخلها — اختر ملفًا أولًا.',
    },
    'they are already in this room': {
        'es': 'ya está en esta sala.',
        'fr': 'cette personne est déjà dans cette salle.',
        'de': 'diese Person ist schon in diesem Raum.',
        'pt': 'já está nesta sala.',
        'it': 'è già in questa stanza.',
        'ja': 'その相手はすでにこの部屋にいます。',
        'zh': '对方已经在这个房间里了。',
        'hi': 'वे पहले से ही इस कमरे में हैं।',
        'ar': 'هو موجود في هذه الغرفة بالفعل.',
    },
    'this room filled up before you answered — eight seats, and every one '
    'taken': {
        'es': 'la sala se llenó antes de que respondieras: ocho asientos, y '
              'todos ocupados.',
        'fr': "la salle s'est remplie avant votre réponse — huit places, et "
              'toutes prises.',
        'de': 'der Raum war voll, bevor du geantwortet hast — acht Plätze, '
              'und jeder besetzt.',
        'pt': 'a sala encheu antes de responderes: oito lugares, e todos '
              'ocupados.',
        'it': 'la stanza si è riempita prima della tua risposta — otto posti, '
              'e tutti occupati.',
        'ja': 'あなたが答える前に部屋がいっぱいになりました。席は八つ、すべて埋まっています。',
        'zh': '你还没回应，房间就满了——八个座位，全都坐了人。',
        'hi': 'आपके जवाब देने से पहले ही कमरा भर गया — आठ सीटें, और हर एक भरी हुई।',
        'ar': 'امتلأت الغرفة قبل أن تجيب — ثمانية مقاعد، وكلها مشغولة.',
    },
    'you have not been asked into this room': {
        'es': 'no te han invitado a esta sala.',
        'fr': "vous n'avez pas été invité dans cette salle.",
        'de': 'du wurdest nicht in diesen Raum eingeladen.',
        'pt': 'não foste convidado para esta sala.',
        'it': 'non sei stato invitato in questa stanza.',
        'ja': 'あなたはこの部屋に招かれていません。',
        'zh': '没有人邀请你进这个房间。',
        'hi': 'आपको इस कमरे में नहीं बुलाया गया है।',
        'ar': 'لم تُدعَ إلى هذه الغرفة.',
    },
    'a box holds a picture — JPEG, PNG, GIF or WebP': {
        'es': 'un recuadro contiene una imagen: JPEG, PNG, GIF o WebP.',
        'fr': 'une case contient une image — JPEG, PNG, GIF ou WebP.',
        'de': 'ein Kästchen hält ein Bild — JPEG, PNG, GIF oder WebP.',
        'pt': 'um quadrado contém uma imagem — JPEG, PNG, GIF ou WebP.',
        'it': "un riquadro contiene un'immagine — JPEG, PNG, GIF o WebP.",
        'ja': '枠に入るのは写真です。JPEG、PNG、GIF、WebP のいずれか。',
        'zh': '方框里放的是图片——JPEG、PNG、GIF 或 WebP。',
        'hi': 'खाने में तस्वीर आती है — JPEG, PNG, GIF या WebP।',
        'ar': 'المربع يحمل صورة — JPEG أو PNG أو GIF أو WebP.',
    },
    'this room has closed': {
        'es': 'esta sala ha cerrado.',
        'fr': 'cette salle a fermé.',
        'de': 'dieser Raum hat geschlossen.',
        'pt': 'esta sala fechou.',
        'it': 'questa stanza ha chiuso.',
        'ja': 'この部屋は閉じられました。',
        'zh': '这个房间已经关闭。',
        'hi': 'यह कमरा बंद हो चुका है।',
        'ar': 'أُغلقت هذه الغرفة.',
    },
    'this room is full — eight seats, and every one taken': {
        'es': 'esta sala está llena: ocho asientos, y todos ocupados.',
        'fr': 'cette salle est pleine — huit places, toutes prises.',
        'de': 'dieser Raum ist voll — acht Plätze, und jeder ist besetzt.',
        'pt': 'esta sala está cheia — oito lugares, todos ocupados.',
        'it': 'questa stanza è piena — otto posti, tutti occupati.',
        'ja': 'この部屋は満席です。8つの席がすべて埋まっています。',
        'zh': '这个房间已满——八个座位，全部有人。',
        'hi': 'यह कमरा भर गया है — आठ सीटें, और हर एक भरी हुई।',
        'ar': 'هذه الغرفة ممتلئة — ثمانية مقاعد وكلها مشغولة.',
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
    'answer': {'en': 'The answer', 'es': 'La respuesta', 'fr': 'La réponse', 'de': 'Die Antwort', 'pt': 'A resposta', 'it': 'La risposta', 'ja': '回答', 'zh': '答复', 'hi': 'उत्तर', 'ar': 'الردّ'},
    'helped': {'en': 'The help box answered it', 'es': 'La ayuda lo respondió', 'fr': "L'aide y a répondu", 'de': 'Die Hilfe hat es beantwortet', 'pt': 'A ajuda respondeu', 'it': "L'aiuto ha risposto", 'ja': 'ヘルプで解決した', 'zh': '帮助框已解答', 'hi': 'सहायता ने उत्तर दिया', 'ar': 'أجاب عنه مربّع المساعدة'},
    'did': {'en': 'What was done', 'es': 'Qué se hizo', 'fr': 'Ce qui a été fait', 'de': 'Was getan wurde', 'pt': 'O que foi feito', 'it': 'Che cosa è stato fatto', 'ja': '行ったこと', 'zh': '做了什么', 'hi': 'क्या किया गया', 'ar': 'ما الذي جرى'},
    'trouble': {'en': 'What is wrong', 'es': 'Qué va mal', 'fr': "Ce qui ne va pas", 'de': 'Was nicht stimmt', 'pt': 'O que está errado', 'it': 'Che cosa non va', 'ja': '何が問題か', 'zh': '哪里出了问题', 'hi': 'क्या गड़बड़ है', 'ar': 'ما الخطأ'},
    'concerns': {'en': 'What this is about', 'es': 'De qué se trata', 'fr': "Ce que cela concerne", 'de': 'Worum es geht', 'pt': 'Do que se trata', 'it': 'Di che cosa si tratta', 'ja': '何についてか', 'zh': '这与什么有关', 'hi': 'यह किस बारे में है', 'ar': 'بشأن ماذا'},
    # The briefing form, and the one control on a kept person. Worded as the
    # screen asks them: a refusal naming `matter` reads as an error about a
    # schema nobody was shown.
    'matter': {'en': 'What this is about', 'es': 'De qué se trata', 'fr': 'De quoi il s’agit', 'de': 'Worum es geht', 'pt': 'Do que se trata', 'it': 'Di che cosa si tratta', 'ja': '何についてか', 'zh': '这是关于什么的', 'hi': 'यह किस बारे में है', 'ar': 'موضوع هذا'},
    # The one control on a row of the privilege roster. A switch, so the label
    # is what the switch decides rather than a name for the field — "on" alone
    # would be a refusal about the API's word for a thing nobody typed.
    'on': {'en': 'Allowed or not', 'es': 'Permitido o no', 'fr': 'Autorisé ou non', 'de': 'Erlaubt oder nicht', 'pt': 'Permitido ou não', 'it': 'Consentito o no', 'ja': '許可するかどうか', 'zh': '是否允许', 'hi': 'अनुमति है या नहीं', 'ar': 'مسموح أم لا'},
    'preferred': {'en': 'Asked first', 'es': 'Se le pregunta primero', 'fr': 'Sollicité en premier', 'de': 'Zuerst gefragt', 'pt': 'Perguntado primeiro', 'it': 'Interpellato per primo', 'ja': '最初に頼む相手', 'zh': '优先联系', 'hi': 'पहले पूछा जाएगा', 'ar': 'يُسأل أولًا'},
    # The open board's answer form. Somebody with no account is typing here,
    # so a refusal naming the API's word for the field would be a refusal
    # about a schema they have never seen.
    'points_to': {'en': 'Somewhere to look', 'es': 'Dónde mirar', 'fr': 'Où chercher', 'de': 'Wo man nachsehen kann', 'pt': 'Onde procurar', 'it': 'Dove guardare', 'ja': '調べ先', 'zh': '可以去哪里找', 'hi': 'कहाँ देखें', 'ar': 'أين يمكن البحث'},
    # The plug-in storefront's sign-in box. Both are worded as the shop
    # asks them, because a refusal that names `secret` reads as an
    # error about the API rather than about the field somebody typed.
    'secret': {'en': 'The key or password it needs', 'es': 'La clave o contraseña que necesita', 'fr': 'La clé ou le mot de passe requis', 'de': 'Der Schlüssel oder das Passwort, das es braucht', 'pt': 'A chave ou palavra-passe de que precisa', 'it': 'La chiave o password che serve', 'ja': '必要な鍵またはパスワード', 'zh': '它需要的密钥或密码', 'hi': 'जो कुंजी या पासवर्ड चाहिए', 'ar': 'المفتاح أو كلمة المرور المطلوبة'},
    'account': {'en': 'Which account there', 'es': 'Qué cuenta allí', 'fr': 'Quel compte là-bas', 'de': 'Welches Konto dort', 'pt': 'Que conta lá', 'it': 'Quale account là', 'ja': '先方のどのアカウントか', 'zh': '那边的哪个账号', 'hi': 'वहाँ कौन-सा खाता', 'ar': 'أي حساب هناك'},
    # The accessibility report's three questions, worded as the form asks
    # them — a refusal that names one of these should read like the form.
    'doing': {'en': 'What were you trying to do?', 'es': '¿Qué intentabas hacer?', 'fr': 'Qu’essayiez-vous de faire ?', 'de': 'Was hast du versucht zu tun?', 'pt': 'O que você estava tentando fazer?', 'it': 'Cosa stavi cercando di fare?', 'ja': '何をしようとしていましたか？', 'zh': '你当时想做什么？', 'hi': 'आप क्या करने की कोशिश कर रहे थे?', 'ar': 'ما الذي كنت تحاول فعله؟'},
    'wall': {'en': 'What stood in the way?', 'es': '¿Qué se interpuso?', 'fr': 'Qu’est-ce qui a fait obstacle ?', 'de': 'Was stand im Weg?', 'pt': 'O que ficou no caminho?', 'it': 'Cosa ti ha ostacolato?', 'ja': '何が妨げになりましたか？', 'zh': '是什么挡住了你？', 'hi': 'क्या आड़े आया?', 'ar': 'ما الذي وقف في الطريق؟'},
    'help': {'en': 'What would help?', 'es': '¿Qué ayudaría?', 'fr': 'Qu’est-ce qui aiderait ?', 'de': 'Was würde helfen?', 'pt': 'O que ajudaria?', 'it': 'Cosa aiuterebbe?', 'ja': '何があれば助かりますか？', 'zh': '什么会有帮助？', 'hi': 'क्या मदद करेगा?', 'ar': 'ما الذي قد يساعد؟'},
    # The room scene's box. `showing` is the one field here a person never
    # types: the console offers it as three buttons, so the label is the
    # question those buttons answer rather than a name for the field.
    'showing': {'en': 'What your box shows', 'es': 'Lo que muestra tu recuadro', 'fr': 'Ce que montre votre case', 'de': 'Was dein Kästchen zeigt', 'pt': 'O que o seu quadrado mostra', 'it': 'Cosa mostra il tuo riquadro', 'ja': 'あなたの枠に出るもの', 'zh': '你的方框显示什么', 'hi': 'आपका खाना क्या दिखाता है', 'ar': 'ما يعرضه مربعك'},
    'media_url': {'en': 'Picture', 'es': 'Imagen', 'fr': 'Image', 'de': 'Bild', 'pt': 'Imagem', 'it': 'Immagine', 'ja': '写真', 'zh': '图片', 'hi': 'तस्वीर', 'ar': 'الصورة'},
    'media_id': {'en': 'Upload', 'es': 'Archivo subido', 'fr': 'Fichier envoyé', 'de': 'Hochgeladene Datei', 'pt': 'Ficheiro enviado', 'it': 'File caricato', 'ja': 'アップロード', 'zh': '上传的文件', 'hi': 'अपलोड', 'ar': 'الملف المرفوع'},
    # The agent's proposal, handed back when somebody presses. Neither is a
    # field a person types — the console sends back what the turn showed —
    # but a refusal that named one of them still has to read as something,
    # and "tool" is a developer's word for it.
    'tool': {'en': 'Step', 'es': 'Paso', 'fr': 'Étape', 'de': 'Schritt', 'pt': 'Passo', 'it': 'Passo', 'ja': '手順', 'zh': '步骤', 'hi': 'चरण', 'ar': 'الخطوة'},
    'arguments': {'en': 'What it would use', 'es': 'Lo que usaría', 'fr': 'Ce qu’il utiliserait', 'de': 'Was es verwenden würde', 'pt': 'O que usaria', 'it': 'Cosa userebbe', 'ja': '使うもの', 'zh': '它会用到的内容', 'hi': 'यह क्या इस्तेमाल करेगा', 'ar': 'ما سيستخدمه'},
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
    # The transcript-curation doors: the checkboxes' selection, and the
    # mark a rewritten turn wears.
    'message_ids': {'en': 'Selected turns', 'es': 'Turnos seleccionados', 'fr': 'Tours sélectionnés', 'de': 'Ausgewählte Beiträge', 'pt': 'Turnos selecionados', 'it': 'Turni selezionati', 'ja': '選択した発言', 'zh': '所选发言', 'hi': 'चुनी हुई बारियाँ', 'ar': 'المداخلات المحددة'},
    'edited': {'en': 'Edited', 'es': 'Editado', 'fr': 'Modifié', 'de': 'Bearbeitet', 'pt': 'Editado', 'it': 'Modificato', 'ja': '編集済み', 'zh': '已编辑', 'hi': 'संपादित', 'ar': 'معدّل'},
    'lesson': {'en': 'Step', 'es': 'Paso', 'fr': 'Étape', 'de': 'Schritt', 'pt': 'Passo', 'it': 'Passo', 'ja': 'ステップ', 'zh': '步骤', 'hi': 'चरण', 'ar': 'الخطوة'},
    'position_s': {'en': 'Position, in seconds', 'es': 'Posición, en segundos', 'fr': 'Position, en secondes', 'de': 'Position, in Sekunden', 'pt': 'Posição, em segundos', 'it': 'Posizione, in secondi', 'ja': '位置（秒）', 'zh': '位置（秒）', 'hi': 'स्थिति, सेकंड में', 'ar': 'الموضع بالثواني'},
    'verification_ref': {'en': 'Verification reference', 'es': 'Referencia de verificación', 'fr': 'Référence de vérification', 'de': 'Verifizierungsnachweis', 'pt': 'Referência de verificação', 'it': 'Riferimento di verifica', 'ja': '確認書類の参照', 'zh': '核验凭证', 'hi': 'सत्यापन संदर्भ', 'ar': 'مرجع التحقق'},
    'interactor_id': {'en': 'Visitor', 'es': 'Visitante', 'fr': 'Visiteur', 'de': 'Besucher', 'pt': 'Visitante', 'it': 'Visitatore', 'ja': '訪問者', 'zh': '访客', 'hi': 'आगंतुक', 'ar': 'الزائर'},
    # The same visitor as the row above, named at the moment an account claims
    # them: the person who has been talking to profiles on this device without
    # signing in. Worded off `interactor_id` rather than invented, so the two
    # rows cannot come to disagree about what they name.
    'adopt_interactor_id': {'en': 'Visitor to attach', 'es': 'Visitante que vincular', 'fr': 'Visiteur à rattacher', 'de': 'Zu verknüpfender Besucher', 'pt': 'Visitante a associar', 'it': 'Visitatore da collegare', 'ja': '引き継ぐ訪問者', 'zh': '要关联的访客', 'hi': 'जोड़ने के लिए आगंतुक', 'ar': 'الزائر المراد ربطه'},
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
    'motion_style': {'en': 'Motion style', 'es': 'Estilo de movimiento', 'fr': 'Style de mouvement', 'de': 'Bewegungsstil', 'pt': 'Estilo de movimento', 'it': 'Stile di movimento', 'ja': '動きのスタイル', 'zh': '动态样式', 'hi': 'गति शैली', 'ar': 'نمط الحركة'},
    # `presentation_kind` rides in the same body as `motion_style`, set by the
    # same owner from the same panel. A refusal that labels one and hands back
    # the identifier for the other is the arbitrariness this table ends.
    'presentation_kind': {'en': 'What the avatar is', 'es': 'Qué es el avatar', 'fr': 'Ce qu’est l’avatar', 'de': 'Was der Avatar ist', 'pt': 'O que é o avatar', 'it': 'Che cos’è l’avatar', 'ja': 'アバターの種類', 'zh': '化身的类型', 'hi': 'अवतार क्या है', 'ar': 'ما هو الأفاتار'},
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
    'said': {'en': 'What you would like changed', 'es': 'Qué quieres cambiar', 'fr': 'Ce que vous voulez changer', 'de': 'Was Sie ändern möchten', 'pt': 'O que quer mudar', 'it': 'Che cosa vuoi cambiare', 'ja': '変えたいこと', 'zh': '你想改动什么', 'hi': 'आप क्या बदलना चाहते हैं', 'ar': 'ما تريد تغييره'},
    'history': {'en': 'The conversation so far', 'es': 'La conversación hasta ahora', 'fr': 'La conversation jusqu’ici', 'de': 'Das bisherige Gespräch', 'pt': 'A conversa até agora', 'it': 'La conversazione finora', 'ja': 'これまでの会話', 'zh': '此前的对话', 'hi': 'अब तक की बातचीत', 'ar': 'المحادثة حتى الآن'},
    'inputs': {'en': 'Inputs', 'es': 'Entradas', 'fr': 'Entrées', 'de': 'Eingaben', 'pt': 'Entradas', 'it': 'Ingressi', 'ja': '入力', 'zh': '输入', 'hi': 'इनपुट', 'ar': 'المدخلات'},
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
    'card': {'en': 'Character card', 'es': 'Tarjeta de personaje', 'fr': 'Carte de personnage', 'de': 'Charakterkarte', 'pt': 'Cartão de personagem', 'it': 'Scheda del personaggio', 'ja': 'キャラクターカード', 'zh': '角色卡', 'hi': 'चरित्र कार्ड', 'ar': 'بطاقة الشخصية'},
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
