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


def tr_refusal(text: str, language: str) -> str:
    """Translate one of the sentences this product refuses with.

    `_PUBLIC` is consulted too, and deliberately: "profile not found" is
    raised by `profile_or_404`, which the accountless routes and every owner
    route share. Two tables would be two translations of one sentence, free to
    drift, with nothing to say which reader got which.
    """
    if language == DEFAULT:
        return text
    return (_REFUSALS.get(text) or _VALIDATION.get(text)
            or _PUBLIC.get(text, {})).get(language, text)


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
    if isinstance(detail, str):
        return tr_refusal(detail, language)
    if isinstance(detail, dict) and isinstance(detail.get("message"), str):
        return {**detail, "message": tr_refusal(detail["message"], language)}
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
