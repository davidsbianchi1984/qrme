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
