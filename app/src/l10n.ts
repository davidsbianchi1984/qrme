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
};

export function t(key: string, lang: string | undefined): string {
  const row = CHROME[key];
  if (!row) return key;
  return row[(lang as Lang) || "en"] || row.en || key;
}
