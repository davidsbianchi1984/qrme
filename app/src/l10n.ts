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
