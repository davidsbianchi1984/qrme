"""Per-profile language: the persona speaks it everywhere.

A synthetic profile has one voice across every surface — chat, composed
posts, room turns, robot speech. Setting a language makes that voice speak
it natively: the directive rides on the persona system prompt, so every
generation site inherits it without per-endpoint plumbing. Owner-set,
like the model preference.
"""

from __future__ import annotations

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
