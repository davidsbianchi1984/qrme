// Chrome localization for the desktop console, mirroring the native apps'
// L10n tables (native/ios/Sources/L10n.swift and siblings): the app's own
// frame follows the profile's language. Content localization was always
// server-side — this closes the console's frame around it. Keys fall back
// to English so a missing translation shows words, never a blank.

export type Lang =
  | "en" | "es" | "fr" | "de" | "pt" | "it" | "ja" | "zh" | "hi" | "ar";

type Table = Record<string, Partial<Record<Lang, string>>>;

const CHROME: Table = {
  "nav.home": {
    en: "Home", es: "Inicio", fr: "Accueil", de: "Start", pt: "Início",
    it: "Home", ja: "ホーム", zh: "主页", hi: "होम", ar: "الرئيسية",
  },
  "nav.chat": {
    en: "Chat", es: "Chat", fr: "Discussion", de: "Chat", pt: "Conversa",
    it: "Chat", ja: "チャット", zh: "聊天", hi: "चैट", ar: "دردشة",
  },
  "nav.discover": {
    en: "Discover", es: "Descubrir", fr: "Découvrir", de: "Entdecken",
    pt: "Descobrir", it: "Scopri", ja: "発見", zh: "发现", hi: "खोजें",
    ar: "استكشف",
  },
  "nav.wall": {
    en: "Wall", es: "Muro", fr: "Mur", de: "Pinnwand", pt: "Mural",
    it: "Bacheca", ja: "ウォール", zh: "动态墙", hi: "वॉल", ar: "الحائط",
  },
  "nav.friends": {
    en: "Friends", es: "Amigos", fr: "Amis", de: "Freunde", pt: "Amigos",
    it: "Amici", ja: "友達", zh: "好友", hi: "मित्र", ar: "الأصدقاء",
  },
  "nav.rooms": {
    en: "Rooms", es: "Salas", fr: "Salons", de: "Räume", pt: "Salas",
    it: "Stanze", ja: "ルーム", zh: "房间", hi: "कक्ष", ar: "الغرف",
  },
  "nav.blend": {
    en: "Blend", es: "Fusionar", fr: "Fusionner", de: "Mischen",
    pt: "Mesclar", it: "Fondere", ja: "ブレンド", zh: "融合",
    hi: "मिश्रण", ar: "مزج",
  },
  "nav.simulate": {
    en: "What If", es: "¿Y si…?", fr: "Et si…", de: "Was wäre wenn",
    pt: "E se…", it: "E se…", ja: "もしも", zh: "假如", hi: "क्या होगा",
    ar: "ماذا لو",
  },
  "nav.campaigns": {
    en: "Campaigns", es: "Campañas", fr: "Campagnes", de: "Kampagnen",
    pt: "Campanhas", it: "Campagne", ja: "キャンペーン", zh: "众筹",
    hi: "अभियान", ar: "الحملات",
  },
  "nav.org": {
    en: "Org", es: "Organización", fr: "Organisation", de: "Organisation",
    pt: "Organização", it: "Organizzazione", ja: "組織", zh: "组织",
    hi: "संगठन", ar: "المنظمة",
  },
  "nav.relationships": {
    en: "Relationships", es: "Relaciones", fr: "Relations",
    de: "Beziehungen", pt: "Relações", it: "Relazioni", ja: "関係",
    zh: "关系", hi: "संबंध", ar: "العلاقات",
  },
  "nav.memory": {
    en: "Memory Vault", es: "Bóveda de memoria", fr: "Coffre de mémoire",
    de: "Erinnerungstresor", pt: "Cofre de memória", it: "Cassaforte dei ricordi",
    ja: "メモリー保管庫", zh: "记忆保险库", hi: "स्मृति तिजोरी",
    ar: "خزنة الذكريات",
  },
  "nav.settings": {
    en: "Control", es: "Control", fr: "Contrôle", de: "Steuerung",
    pt: "Controle", it: "Controllo", ja: "コントロール", zh: "控制",
    hi: "नियंत्रण", ar: "التحكم",
  },
  // The four below were missing, and a missing key here does not fall back
  // to the English label sitting right next to it in NAV — `t()` returns the
  // key itself, so the sidebar has been reading "nav.market", "nav.delegate",
  // "nav.desk" and "nav.voice" in every language including English. The
  // fallback chain was written to never show a blank and it never did; it
  // showed an identifier instead, which is worse, because a blank looks
  // broken and an identifier looks like a label somebody chose.
  //
  // `test_nav_labels_are_localised` fails now if a tab arrives without one.
  "nav.market": {
    en: "Marketplace", es: "Mercado", fr: "Place de marché", de: "Marktplatz",
    pt: "Mercado", it: "Mercato", ja: "マーケット", zh: "市场",
    hi: "बाज़ार", ar: "السوق",
  },
  "nav.delegate": {
    en: "Delegation", es: "Delegación", fr: "Délégation", de: "Delegation",
    pt: "Delegação", it: "Delega", ja: "委任", zh: "委托",
    hi: "प्रत्यायोजन", ar: "التفويض",
  },
  "nav.desk": {
    en: "Desk", es: "Mostrador", fr: "Comptoir", de: "Tresen", pt: "Balcão",
    it: "Banco", ja: "デスク", zh: "服务台", hi: "डेस्क", ar: "المكتب",
  },
  "nav.voice": {
    en: "Voice", es: "Voz", fr: "Voix", de: "Stimme", pt: "Voz",
    it: "Voce", ja: "音声", zh: "语音", hi: "आवाज़", ar: "الصوت",
  },
  "nav.identity": {
    en: "Identity", es: "Identidad", fr: "Identité", de: "Identität",
    pt: "Identidade", it: "Identità", ja: "本人確認", zh: "身份",
    hi: "पहचान", ar: "الهوية",
  },
  "nav.presence": {
    en: "Where it is seen", es: "Dónde se ve", fr: "Où on le voit",
    de: "Wo es zu sehen ist", pt: "Onde aparece", it: "Dove si vede",
    ja: "表示される場所", zh: "展示位置", hi: "कहाँ दिखता है",
    ar: "أين يُعرض",
  },
  "nav.live": {
    en: "What is live", es: "Qué está activo", fr: "Ce qui est en direct",
    de: "Was gerade läuft", pt: "O que está ativo", it: "Cosa è attivo",
    ja: "起動中のもの", zh: "正在进行", hi: "क्या चालू है",
    ar: "ما هو نشط",
  },
  "nav.contest": {
    en: "Contest a profile", es: "Impugnar un perfil",
    fr: "Contester un profil", de: "Profil anfechten",
    pt: "Contestar um perfil", it: "Contestare un profilo",
    ja: "プロフィールの異議", zh: "申诉档案", hi: "प्रोफ़ाइल पर आपत्ति",
    ar: "الاعتراض على ملف",
  },
  "nav.guide": {
    en: "Show me around", es: "Guíame", fr: "Faire le tour",
    de: "Rundgang", pt: "Mostrar tudo", it: "Fammi da guida",
    ja: "案内して", zh: "带我熟悉", hi: "मुझे दिखाएँ",
    ar: "جولة تعريفية",
  },
  "nav.workshop": {
    en: "What it is made of", es: "De qué está hecho",
    fr: "Ce qui le compose", de: "Woraus es besteht",
    pt: "Do que é feito", it: "Di cosa è fatto",
    ja: "何でできているか", zh: "由什么构成", hi: "किससे बना है",
    ar: "مِمَّ يتكوّن",
  },
  "nav.assist": {
    en: "What it can do for you", es: "Qué puede hacer por ti",
    fr: "Ce qu'il peut faire pour vous", de: "Was es für dich tun kann",
    pt: "O que pode fazer por si", it: "Cosa può fare per te",
    ja: "できること", zh: "它能为你做什么", hi: "यह आपके लिए क्या कर सकता है",
    ar: "ما يمكنه فعله لك",
  },
  "nav.referrals": {
    en: "Somebody qualified", es: "Alguien cualificado",
    fr: "Quelqu'un de qualifié", de: "Jemand mit Qualifikation",
    pt: "Alguém qualificado", it: "Qualcuno di qualificato",
    ja: "専門家へ", zh: "转给专业人士", hi: "योग्य व्यक्ति",
    ar: "شخص مؤهل",
  },
  "nav.lobby": {
    en: "In the game", es: "En la partida", fr: "Dans la partie",
    de: "Im Spiel", pt: "Na partida", it: "In partita",
    ja: "ゲーム中", zh: "对局中", hi: "खेल में", ar: "في اللعبة",
  },
  "nav.audience": {
    en: "Who follows", es: "Quién sigue", fr: "Qui suit",
    de: "Wer folgt", pt: "Quem segue", it: "Chi segue",
    ja: "フォロワー", zh: "谁在关注", hi: "कौन फ़ॉलो करता है",
    ar: "من يتابع",
  },
  "nav.beacons": {
    en: "Where people find you", es: "Dónde te encuentran",
    fr: "Où l'on vous trouve", de: "Wo man dich findet",
    pt: "Onde te encontram", it: "Dove ti trovano",
    ja: "見つけられる場所", zh: "别人从哪里找到你",
    hi: "लोग आपको कहाँ पाते हैं", ar: "أين يجدونك",
  },
  "nav.reaching": {
    en: "Reaching out", es: "Contactar", fr: "Prendre contact",
    de: "Sich melden", pt: "Entrar em contacto", it: "Farsi vivo",
    ja: "こちらから連絡", zh: "主动联系", hi: "पहल करना",
    ar: "المبادرة بالتواصل",
  },
  "nav.leaving": {
    en: "What leaves", es: "Qué sale", fr: "Ce qui sort",
    de: "Was hinausgeht", pt: "O que sai", it: "Cosa esce",
    ja: "外へ出るもの", zh: "哪些内容外流", hi: "क्या बाहर जाता है",
    ar: "ما الذي يخرج",
  },
  "nav.selling": {
    en: "What you are owed", es: "Lo que se te debe",
    fr: "Ce qui vous est dû", de: "Was Ihnen zusteht",
    pt: "O que lhe é devido", it: "Quanto ti spetta",
    ja: "受け取るべきもの", zh: "该付给你的",
    hi: "जो आपको मिलना है", ar: "ما هو مستحق لك",
  },
  "nav.inside": {
    en: "Inside a room", es: "Dentro de una sala", fr: "Dans un salon",
    de: "Im Raum", pt: "Dentro de uma sala", it: "Dentro una stanza",
    ja: "ルームの中", zh: "在房间里", hi: "कमरे के भीतर",
    ar: "داخل الغرفة",
  },
  "nav.signing": {
    en: "Signing", es: "Firmar", fr: "Signature",
    de: "Signieren", pt: "Assinatura", it: "Firma",
    ja: "署名", zh: "签名", hi: "हस्ताक्षर",
    ar: "التوقيع",
  },
  "nav.visiting": {
    en: "Visiting", es: "De visita", fr: "En visite",
    de: "Zu Besuch", pt: "Em visita", it: "In visita",
    ja: "訪ねる", zh: "上门", hi: "मिलने जाना",
    ar: "زيارة",
  },
  "nav.stranger": {
    en: "Strangers", es: "Desconocidos", fr: "Inconnus",
    de: "Fremde", pt: "Desconhecidos", it: "Sconosciuti",
    ja: "見知らぬ人", zh: "陌生人", hi: "अजनबी",
    ar: "الغرباء",
  },
  "nav.themark": {
    en: "The mark", es: "La marca", fr: "La marque",
    de: "Die Kennzeichnung", pt: "A marca", it: "Il marchio",
    ja: "表示マーク", zh: "标识", hi: "चिह्न",
    ar: "العلامة",
  },
  "nav.inwords": {
    en: "In its words", es: "En sus palabras", fr: "Dans ses mots",
    de: "In seinen Worten", pt: "Nas suas palavras",
    it: "Con parole sue", ja: "その言葉で", zh: "用它的话",
    hi: "अपने शब्दों में", ar: "بكلماته",
  },
  "nav.remainder": {
    en: "Everything else", es: "Todo lo demás", fr: "Le reste",
    de: "Alles Übrige", pt: "Tudo o resto", it: "Tutto il resto",
    ja: "そのほか", zh: "其他", hi: "बाकी सब", ar: "كل ما تبقى",
  },
  "nav.named": {
    en: "One thing, named", es: "Una cosa, con nombre",
    fr: "Une chose, nommée", de: "Eine Sache, benannt",
    pt: "Uma coisa, nomeada", it: "Una cosa, per nome",
    ja: "名指しでひとつ", zh: "指名一件事", hi: "एक चीज़, नाम से",
    ar: "شيء واحد، بالاسم",
  },
  "nav.passing": {
    en: "Beginning and passing on", es: "Comienzo y sucesión",
    fr: "Naissance et transmission", de: "Anfang und Übergabe",
    pt: "Início e sucessão", it: "Inizio e successione",
    ja: "はじまりと引き継ぎ", zh: "开始与传承",
    hi: "आरंभ और उत्तराधिकार", ar: "البداية والانتقال",
  },
  "nav.robots": {
    en: "Bodies", es: "Cuerpos", fr: "Corps", de: "Körper",
    pt: "Corpos", it: "Corpi", ja: "ボディ", zh: "机体",
    hi: "देह", ar: "الأجساد",
  },
  "nav.placements": {
    en: "Where it is marketed", es: "Dónde se anuncia",
    fr: "Où c'est diffusé", de: "Wo es beworben wird",
    pt: "Onde é divulgado", it: "Dove è promosso",
    ja: "掲載先", zh: "投放位置", hi: "कहाँ प्रचारित",
    ar: "أين يُعرض",
  },
  "nav.plans": {
    en: "Plans", es: "Planes", fr: "Formules", de: "Tarife",
    pt: "Planos", it: "Piani", ja: "プラン", zh: "方案",
    hi: "योजनाएँ", ar: "الخطط",
  },
  "nav.exchanges": {
    en: "Exchanges", es: "Intercambios", fr: "Échanges", de: "Austausch",
    pt: "Trocas", it: "Scambi", ja: "取り決め", zh: "交换", hi: "विनिमय",
    ar: "التبادلات",
  },
  "nav.grants": {
    en: "Lent skills", es: "Aptitudes prestadas", fr: "Compétences prêtées",
    de: "Geliehene Fähigkeiten", pt: "Aptidões emprestadas",
    it: "Abilità prestate", ja: "貸した技能", zh: "借出的技能",
    hi: "उधार दिए कौशल", ar: "المهارات المُعارة",
  },
  "nav.party": {
    en: "Watch together", es: "Ver juntos", fr: "Regarder ensemble",
    de: "Zusammen ansehen", pt: "Assistir juntos", it: "Guardare insieme",
    ja: "一緒に見る", zh: "一起观看", hi: "साथ देखें", ar: "المشاهدة معًا",
  },
  "signout": {
    en: "Sign out", es: "Cerrar sesión", fr: "Se déconnecter", de: "Abmelden",
    pt: "Sair", it: "Esci", ja: "サインアウト", zh: "退出登录",
    hi: "साइन आउट", ar: "تسجيل الخروج",
  },

  // ---- the surface for people with no profile (screens/Public.tsx) ----
  //
  // Everything above is chrome for somebody signed in, and takes its
  // language from their profile. These take it from `visitorLang` below,
  // because the reader of this screen is by construction the one person in
  // the product who has no profile to take a setting from.
  "pub.sub": {
    en: "Without an account", es: "Sin cuenta", fr: "Sans compte",
    de: "Ohne Konto", pt: "Sem conta", it: "Senza account",
    ja: "アカウントなしで", zh: "无需账户", hi: "बिना खाते के",
    ar: "بدون حساب",
  },
  "pub.back": {
    en: "Back to sign in", es: "Volver a iniciar sesión",
    fr: "Retour à la connexion", de: "Zurück zur Anmeldung",
    pt: "Voltar a iniciar sessão", it: "Torna all'accesso",
    ja: "サインインに戻る", zh: "返回登录", hi: "साइन इन पर लौटें",
    ar: "العودة لتسجيل الدخول",
  },
  "pub.tab.object": {
    en: "Object to a profile", es: "Objetar a un perfil",
    fr: "Contester un profil", de: "Einem Profil widersprechen",
    pt: "Contestar um perfil", it: "Contestare un profilo",
    ja: "プロフィールに異議を申し立てる", zh: "对某个资料提出异议",
    hi: "किसी प्रोफ़ाइल पर आपत्ति", ar: "الاعتراض على ملف",
  },
  "pub.tab.mark": {
    en: "Is this genuine?", es: "¿Esto es auténtico?",
    fr: "Est-ce authentique ?", de: "Ist das echt?",
    pt: "Isto é genuíno?", it: "È autentico?", ja: "これは本物ですか？",
    zh: "这是真的吗？", hi: "क्या यह असली है?", ar: "هل هذا أصلي؟",
  },
  "pub.tab.same": {
    en: "Is this the same one?", es: "¿Es el mismo?",
    fr: "Est-ce le même ?", de: "Ist das dasselbe?",
    pt: "É o mesmo?", it: "È lo stesso?", ja: "これは同じものですか？",
    zh: "这是同一个吗？", hi: "क्या यह वही है?", ar: "هل هذا هو نفسه؟",
  },
  "pub.object.title": {
    en: "A profile depicts me", es: "Un perfil me representa",
    fr: "Un profil me représente", de: "Ein Profil stellt mich dar",
    pt: "Um perfil representa-me", it: "Un profilo mi rappresenta",
    ja: "私を模したプロフィールがあります", zh: "有一个资料在描绘我",
    hi: "एक प्रोफ़ाइल मुझे दर्शाती है", ar: "هناك ملف يصوّرني",
  },
  "pub.object.profileId": {
    en: "the profile's id", es: "el id del perfil",
    fr: "l'identifiant du profil", de: "die ID des Profils",
    pt: "o id do perfil", it: "l'id del profilo", ja: "プロフィールのID",
    zh: "该资料的 id", hi: "प्रोफ़ाइल की आईडी", ar: "معرّف الملف",
  },
  "pub.object.ref": {
    en: "your proof reference", es: "su referencia de prueba",
    fr: "votre référence de preuve", de: "Ihr Nachweis-Aktenzeichen",
    pt: "a sua referência de prova", it: "il tuo riferimento di prova",
    ja: "本人確認の参照番号", zh: "你的证明编号",
    hi: "आपका प्रमाण संदर्भ", ar: "مرجع إثباتك",
  },
  "pub.object.reason": {
    en: "why — in your own words", es: "por qué — con sus palabras",
    fr: "pourquoi — avec vos mots", de: "warum — in Ihren eigenen Worten",
    pt: "porquê — nas suas palavras", it: "perché — con parole tue",
    ja: "理由 — ご自身の言葉で", zh: "原因 — 用你自己的话",
    hi: "क्यों — अपने शब्दों में", ar: "لماذا — بكلماتك",
  },
  "pub.object.open": {
    en: "Open it", es: "Abrirla", fr: "L'ouvrir", de: "Einreichen",
    pt: "Abrir", it: "Aprila", ja: "申し立てる", zh: "提出",
    hi: "दर्ज करें", ar: "افتحه",
  },
  "pub.check.title": {
    en: "Check a case", es: "Consultar un caso", fr: "Suivre un dossier",
    de: "Einen Fall prüfen", pt: "Consultar um caso",
    it: "Controlla un caso", ja: "申し立てを確認する", zh: "查询案件",
    hi: "मामला देखें", ar: "تحقّق من قضية",
  },
  "pub.check.id": {
    en: "objection id", es: "id de la objeción", fr: "identifiant du dossier",
    de: "ID des Widerspruchs", pt: "id da contestação",
    it: "id della contestazione", ja: "申し立てID", zh: "异议 id",
    hi: "आपत्ति आईडी", ar: "معرّف الاعتراض",
  },
  "pub.check.go": {
    en: "Check", es: "Consultar", fr: "Vérifier", de: "Prüfen",
    pt: "Consultar", it: "Controlla", ja: "確認", zh: "查询",
    hi: "जाँचें", ar: "تحقّق",
  },
  "pub.mark.title": {
    en: "Somebody sent me this", es: "Alguien me envió esto",
    fr: "Quelqu'un m'a envoyé ceci", de: "Jemand hat mir das geschickt",
    pt: "Alguém enviou-me isto", it: "Qualcuno mi ha mandato questo",
    ja: "これを送られてきました", zh: "有人给我发了这个",
    hi: "किसी ने मुझे यह भेजा", ar: "أرسل لي أحدهم هذا",
  },
  "pub.mark.paste": {
    en: "paste the text", es: "pegue el texto", fr: "collez le texte",
    de: "Text einfügen", pt: "cole o texto", it: "incolla il testo",
    ja: "テキストを貼り付けてください", zh: "粘贴文本",
    hi: "पाठ चिपकाएँ", ar: "الصق النص",
  },
  "pub.mark.ask": {
    en: "Ask who wrote it", es: "Preguntar quién lo escribió",
    fr: "Demander qui l'a écrit", de: "Fragen, wer es geschrieben hat",
    pt: "Perguntar quem o escreveu", it: "Chiedi chi l'ha scritto",
    ja: "誰が書いたか調べる", zh: "查询是谁写的",
    hi: "पूछें किसने लिखा", ar: "اسأل من كتبه",
  },
  "pub.mark.unknown": {
    en: "Not recognised", es: "No reconocido", fr: "Non reconnu",
    de: "Nicht erkannt", pt: "Não reconhecido", it: "Non riconosciuto",
    ja: "該当なし", zh: "未识别", hi: "पहचाना नहीं गया",
    ar: "غير معروف",
  },
  "pub.same.title": {
    en: "I met one of these somewhere else",
    es: "Me encontré con uno de estos en otro sitio",
    fr: "J'en ai rencontré un ailleurs",
    de: "Ich bin so einem anderswo begegnet",
    pt: "Encontrei um destes noutro lugar",
    it: "Ne ho incontrato uno altrove",
    ja: "別の場所で会ったことがあります",
    zh: "我在别处遇到过其中一个",
    hi: "मैं इनमें से एक से कहीं और मिला था",
    ar: "قابلت واحدًا من هؤلاء في مكان آخر",
  },
  "pub.same.go": {
    en: "Look it up", es: "Buscarlo", fr: "Rechercher", de: "Nachschlagen",
    pt: "Procurar", it: "Cerca", ja: "調べる", zh: "查询",
    hi: "देखें", ar: "ابحث عنه",
  },
  "pub.notoken": {
    en: "Nothing on this page reads or needs a token.",
    es: "Nada en esta página lee ni necesita una credencial.",
    fr: "Rien sur cette page ne lit ni ne requiert d'identifiant.",
    de: "Nichts auf dieser Seite liest oder braucht ein Token.",
    pt: "Nada nesta página lê ou precisa de uma credencial.",
    it: "Nulla in questa pagina legge o richiede una credenziale.",
    ja: "このページは資格情報を読み取らず、必要ともしません。",
    zh: "本页面既不读取也不需要任何凭据。",
    hi: "इस पृष्ठ पर कुछ भी टोकन नहीं पढ़ता और न ही चाहिए।",
    ar: "لا شيء في هذه الصفحة يقرأ رمزًا أو يحتاج إليه.",
  },
  "pub.object.restricts": {
    en: "You do not need an account, and this page is the proof of it rather than a promise about it. Opening an objection restricts the profile straight away — public surfaces off, no new interactors — before anybody reviews it.",
    es: "No necesita una cuenta, y esta página es la prueba de ello, no una promesa al respecto. Abrir una objeción restringe el perfil de inmediato —superficies públicas desactivadas, sin nuevos interlocutores— antes de que nadie lo revise.",
    fr: "Vous n'avez pas besoin de compte, et cette page en est la preuve plutôt qu'une promesse. Ouvrir une contestation restreint le profil immédiatement — surfaces publiques coupées, aucun nouvel interlocuteur — avant tout examen.",
    de: "Sie brauchen kein Konto, und diese Seite ist der Beweis dafür statt eines Versprechens darüber. Ein Widerspruch beschränkt das Profil sofort — öffentliche Flächen aus, keine neuen Gesprächspartner — noch bevor jemand es prüft.",
    pt: "Não precisa de conta, e esta página é a prova disso e não uma promessa sobre isso. Abrir uma contestação restringe o perfil de imediato — superfícies públicas desligadas, sem novos interlocutores — antes de alguém a analisar.",
    it: "Non serve un account, e questa pagina ne è la prova anziché una promessa. Aprire una contestazione limita subito il profilo — superfici pubbliche spente, nessun nuovo interlocutore — prima che qualcuno la esamini.",
    ja: "アカウントは不要です。このページはその約束ではなく、その証拠です。異議を申し立てると、誰かが審査する前に、プロフィールは直ちに制限されます（公開面は停止、新しい相手とのやり取りも停止）。",
    zh: "你不需要账户，本页面就是证明，而不是关于它的承诺。提出异议会立即限制该资料 — 关闭公开界面、不再接受新的互动对象 — 在任何人审核之前。",
    hi: "आपको खाते की ज़रूरत नहीं, और यह पृष्ठ उसका वादा नहीं बल्कि प्रमाण है। आपत्ति दर्ज करते ही प्रोफ़ाइल तुरंत सीमित हो जाती है — सार्वजनिक सतहें बंद, कोई नया संवादकर्ता नहीं — किसी की समीक्षा से पहले।",
    ar: "لا تحتاج إلى حساب، وهذه الصفحة هي الدليل على ذلك لا وعدًا به. فتح اعتراض يقيّد الملف فورًا — إيقاف الواجهات العامة، ولا متفاعلين جدد — قبل أن يراجعه أحد.",
  },
  "pub.object.ref.note": {
    en: "The proof reference points at an identity check held outside this system — it is not a login, and it is what lets you object without one.",
    es: "La referencia de prueba apunta a una comprobación de identidad realizada fuera de este sistema: no es un inicio de sesión, y es lo que le permite objetar sin tener uno.",
    fr: "La référence de preuve renvoie à une vérification d'identité effectuée hors de ce système : ce n'est pas une connexion, et c'est ce qui vous permet de contester sans en avoir une.",
    de: "Das Nachweis-Aktenzeichen verweist auf eine Identitätsprüfung außerhalb dieses Systems — es ist keine Anmeldung, und genau deshalb können Sie ohne eine widersprechen.",
    pt: "A referência de prova aponta para uma verificação de identidade feita fora deste sistema: não é um início de sessão, e é o que lhe permite contestar sem ter um.",
    it: "Il riferimento di prova rimanda a una verifica d'identità tenuta fuori da questo sistema: non è un accesso, ed è ciò che ti permette di contestare senza averne uno.",
    ja: "参照番号は、この仕組みの外で行われた本人確認を指します。ログインではなく、ログインなしで異議を申し立てられるようにするためのものです。",
    zh: "证明编号指向在本系统之外完成的身份核验 — 它不是登录凭据，正是它让你无需登录也能提出异议。",
    hi: "प्रमाण संदर्भ इस प्रणाली के बाहर हुई पहचान-जाँच की ओर इशारा करता है — यह लॉगिन नहीं है, और यही आपको बिना लॉगिन के आपत्ति दर्ज करने देता है।",
    ar: "مرجع الإثبات يشير إلى تحقّق من الهوية جرى خارج هذا النظام — ليس تسجيل دخول، وهو ما يتيح لك الاعتراض بدونه.",
  },
  "pub.object.writeitdown": {
    en: "Write the id down. It is how you check this case later without an account — there is no inbox here to come back to.",
    es: "Anote el identificador. Es cómo consultará este caso más adelante sin una cuenta: aquí no hay bandeja de entrada a la que volver.",
    fr: "Notez l'identifiant. C'est ainsi que vous suivrez ce dossier plus tard sans compte : il n'y a pas de boîte de réception ici où revenir.",
    de: "Notieren Sie die ID. So prüfen Sie diesen Fall später ohne Konto — hier gibt es keinen Posteingang, zu dem Sie zurückkehren könnten.",
    pt: "Anote o id. É assim que consultará este caso mais tarde sem conta — aqui não há caixa de entrada para onde voltar.",
    it: "Annota l'id. È così che controllerai questo caso più avanti senza un account: qui non c'è una casella a cui tornare.",
    ja: "IDを控えてください。アカウントなしで後からこの件を確認する唯一の方法です。戻ってこられる受信箱はありません。",
    zh: "请记下这个 id。这是你日后在没有账户的情况下查询本案的方式 — 这里没有可供你回来查看的收件箱。",
    hi: "यह आईडी लिख लें। बिना खाते के बाद में इस मामले को देखने का यही तरीका है — यहाँ लौटने के लिए कोई इनबॉक्स नहीं है।",
    ar: "دوّن المعرّف. فهو كيف تتابع هذه القضية لاحقًا بدون حساب — لا يوجد هنا صندوق وارد تعود إليه.",
  },
  "pub.mark.altered": {
    en: "The wording has changed since it was stamped. That does not make it less traceable — it is what the score above is measuring.",
    es: "La redacción ha cambiado desde que se selló. Eso no lo hace menos rastreable: es precisamente lo que mide la puntuación anterior.",
    fr: "La formulation a changé depuis l'horodatage. Cela ne le rend pas moins traçable : c'est justement ce que mesure le score ci-dessus.",
    de: "Der Wortlaut hat sich seit der Kennzeichnung geändert. Das macht ihn nicht weniger nachverfolgbar — genau das misst der Wert oben.",
    pt: "A redação mudou desde que foi selada. Isso não a torna menos rastreável: é precisamente o que a pontuação acima mede.",
    it: "Il testo è cambiato da quando è stato marcato. Questo non lo rende meno tracciabile: è proprio ciò che il punteggio sopra misura.",
    ja: "刻印されてから文言が変わっています。それで追跡できなくなるわけではありません。上のスコアが測っているのはまさにその差です。",
    zh: "自加盖标记以来措辞已经改变。这并不会让它更难追溯 — 上面的分数衡量的正是这一点。",
    hi: "मुहर लगने के बाद शब्द बदले हैं। इससे यह कम पता लगाने योग्य नहीं होता — ऊपर का स्कोर यही माप रहा है।",
    ar: "تغيّرت الصياغة منذ ختمه. هذا لا يجعله أقل قابلية للتتبّع — فذلك تحديدًا ما تقيسه الدرجة أعلاه.",
  },
  "pub.same.explain": {
    en: "A profile keeps one identity signature across every form it takes — a chat window, a voice on a speaker, a body in a room. Put the id in and compare it with the one you were given elsewhere.",
    es: "Un perfil conserva una única firma de identidad en todas las formas que adopta: una ventana de chat, una voz en un altavoz, un cuerpo en una sala. Introduzca el identificador y compárelo con el que le dieron en otro sitio.",
    fr: "Un profil conserve une seule signature d'identité sous toutes ses formes : une fenêtre de discussion, une voix sur un haut-parleur, un corps dans une pièce. Saisissez l'identifiant et comparez-le à celui qu'on vous a donné ailleurs.",
    de: "Ein Profil behält über alle seine Formen hinweg eine einzige Identitätssignatur — ein Chatfenster, eine Stimme aus einem Lautsprecher, ein Körper im Raum. Geben Sie die ID ein und vergleichen Sie sie mit der, die Sie anderswo erhalten haben.",
    pt: "Um perfil mantém uma única assinatura de identidade em todas as formas que assume: uma janela de conversa, uma voz num altifalante, um corpo numa sala. Introduza o id e compare-o com o que lhe deram noutro lugar.",
    it: "Un profilo mantiene un'unica firma d'identità in ogni forma che assume: una finestra di chat, una voce da un altoparlante, un corpo in una stanza. Inserisci l'id e confrontalo con quello che ti è stato dato altrove.",
    ja: "プロフィールは、チャット画面でも、スピーカーから聞こえる声でも、部屋にいる身体でも、どの形をとっても同じ一つの識別署名を保ちます。IDを入力して、別の場所で示されたものと照合してください。",
    zh: "一个资料在它呈现的每一种形态中都保持同一个身份签名 — 聊天窗口、扬声器里的声音、房间里的身体。输入 id，与你在别处拿到的那个比对。",
    hi: "प्रोफ़ाइल हर रूप में एक ही पहचान-हस्ताक्षर रखती है — चैट विंडो, स्पीकर पर आवाज़, कमरे में एक शरीर। आईडी डालें और उससे मिलाएँ जो आपको कहीं और दिया गया था।",
    ar: "يحتفظ الملف بتوقيع هوية واحد في كل صورة يتّخذها — نافذة محادثة، صوت من مكبّر، جسد في غرفة. أدخل المعرّف وقارنه بالذي أُعطي لك في مكان آخر.",
  },
  "pub.invite": {
    en: "Here about a profile, not for one?",
    es: "¿Viene por un perfil, no a crear uno?",
    fr: "Ici à propos d'un profil, pas pour en créer un ?",
    de: "Wegen eines Profils hier, nicht für eines?",
    pt: "Está aqui por causa de um perfil, não para criar um?",
    it: "Sei qui per un profilo, non per crearne uno?",
    ja: "プロフィールを作りに来たのではなく、あるプロフィールの件でしょうか？",
    zh: "你是为某个资料而来，而不是来创建一个？",
    hi: "किसी प्रोफ़ाइल के बारे में आए हैं, बनाने नहीं?",
    ar: "أتيت بشأن ملف، لا لإنشاء واحد؟",
  },
  "pub.invite.none": {
    en: "Neither needs an account.",
    es: "Ninguna de las dos necesita cuenta.",
    fr: "Aucun des deux ne nécessite de compte.",
    de: "Für beides ist kein Konto nötig.",
    pt: "Nenhuma das duas precisa de conta.",
    it: "Nessuna delle due richiede un account.",
    ja: "どちらもアカウントは不要です。",
    zh: "两者都不需要账户。",
    hi: "दोनों के लिए खाता ज़रूरी नहीं।",
    ar: "لا يحتاج أيٌّ منهما إلى حساب.",
  },
};

export function t(key: string, lang: string | undefined): string {
  const row = CHROME[key];
  if (!row) return key;
  return row[(lang as Lang) || "en"] || row.en || key;
}

const SUPPORTED: Lang[] =
  ["en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"];

/**
 * The language of somebody who has no profile to take one from.
 *
 * Everything above this line is keyed on the profile's setting — the header
 * comment says so, and it is right for the console. It is useless for the
 * one surface in this app built for people who do not have a profile: the
 * person contesting a synthetic profile of themselves, the person asking
 * whether what they were sent was written by a human, the person checking
 * they met the same profile twice.
 *
 * Their browser has been saying which language they read on every request
 * and in `navigator.languages` on every render. Nothing looked, so the page
 * built for the person with no account was also the page with no language.
 *
 * Region is dropped (`es-419` and `es-ES` are both `es`) and anything
 * unrecognised falls back to English rather than guessing.
 */
export function visitorLang(
  preferred: readonly string[] =
    typeof navigator === "undefined" ? [] : navigator.languages ?? [],
): Lang {
  for (const tag of preferred) {
    const base = tag.split("-")[0].toLowerCase() as Lang;
    if (SUPPORTED.includes(base)) return base;
  }
  return "en";
}
