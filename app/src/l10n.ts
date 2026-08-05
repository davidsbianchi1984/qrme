// Chrome localization for the desktop console, mirroring the native apps'
// L10n tables (native/ios/Sources/L10n.swift and siblings): the app's own
// frame follows the profile's language. Content localization was always
// server-side — this closes the console's frame around it. Keys fall back
// to English so a missing translation shows words, never a blank.

import { createElement, Fragment, type ReactNode } from "react";

export type Lang =
  | "en" | "es" | "fr" | "de" | "pt" | "it" | "ja" | "zh" | "hi" | "ar";

type Table = Record<string, Partial<Record<Lang, string>>>;

const CHROME: Table = {
  // The plan gate's card. The sentence inside it comes translated from the
  // server (`qrme/tiers.py:refusal`); these are the console's own chrome
  // around it, and they are here rather than inline for the reason every
  // other console string is.
  "refusal.see_plans": {
    en: "See the plans", es: "Ver los planes", fr: "Voir les formules",
    de: "Die Tarife ansehen", pt: "Ver os planos", it: "Vedi i piani",
    ja: "プランを見る", zh: "查看方案", hi: "योजनाएँ देखें",
    ar: "عرض الخطط",
  },
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
  "nav.shop": {
    en: "Shops", es: "Tiendas", fr: "Boutiques", de: "Läden",
    pt: "Lojas", it: "Negozi", ja: "ショップ", zh: "商店",
    hi: "दुकानें", ar: "المتاجر",
  },
  "lights.unreachable": {
    en: "The agent lights can’t reach the backend — press to retry",
    es: "Las luces de agentes no alcanzan el servidor — pulsa para reintentar",
    fr: "Les voyants d’agents n’atteignent pas le serveur — appuyez pour réessayer",
    de: "Die Agenten-Lichter erreichen das Backend nicht — zum Wiederholen drücken",
    pt: "As luzes dos agentes não alcançam o servidor — toque para tentar de novo",
    it: "Le luci degli agenti non raggiungono il server — premi per riprovare",
    ja: "エージェントライトがバックエンドに届きません — 押して再試行",
    zh: "智能体指示灯无法连接后端 — 点按重试",
    hi: "एजेंट लाइटें बैकएंड तक नहीं पहुँच पा रहीं — फिर से आज़माने के लिए दबाएँ",
    ar: "أضواء الوكلاء لا تصل إلى الخادم — اضغط لإعادة المحاولة",
  },
  // The inbox card on Friends. The same rows the three shells carry — the
  // backend names the deed, and every client composes the sentence from
  // its own vocabulary.
  "inbox.title": {
    en: "What happened", es: "Qué pasó", fr: "Ce qui s'est passé",
    de: "Was geschehen ist", pt: "O que aconteceu", it: "Cosa è successo",
    ja: "何があったか", zh: "发生了什么", hi: "क्या हुआ", ar: "ما الذي حدث",
  },
  "inbox.new": {
    en: "new", es: "nuevo", fr: "nouveau", de: "neu", pt: "novo",
    it: "nuovo", ja: "新着", zh: "新", hi: "नया", ar: "جديد",
  },
  "inbox.seen": {
    en: "Mark all seen", es: "Marcar todo como visto",
    fr: "Tout marquer comme vu", de: "Alles als gesehen markieren",
    pt: "Marcar tudo como visto", it: "Segna tutto come visto",
    ja: "すべて既読にする", zh: "全部标为已读",
    hi: "सभी को देखा हुआ चिह्नित करें", ar: "وضع علامة مقروء على الكل",
  },
  "inbox.kind.message": {
    en: "sent you a message", es: "te envió un mensaje",
    fr: "vous a envoyé un message", de: "hat dir eine Nachricht geschickt",
    pt: "enviou uma mensagem para você", it: "ti ha inviato un messaggio",
    ja: "からメッセージが届きました", zh: "给你发了一条消息",
    hi: "ने आपको संदेश भेजा", ar: "أرسل لك رسالة",
  },
  "inbox.kind.comment": {
    en: "commented on something of yours", es: "comentó algo tuyo",
    fr: "a commenté quelque chose à vous", de: "hat etwas von dir kommentiert",
    pt: "comentou algo seu", it: "ha commentato qualcosa di tuo",
    ja: "があなたの投稿にコメントしました", zh: "评论了你的内容",
    hi: "ने आपकी किसी चीज़ पर टिप्पणी की", ar: "علّق على شيء يخصك",
  },
  "inbox.kind.friend": {
    en: "added you as a friend", es: "te añadió como amigo",
    fr: "vous a ajouté comme ami", de: "hat dich als Freund hinzugefügt",
    pt: "adicionou você como amigo", it: "ti ha aggiunto come amico",
    ja: "があなたを友達に追加しました", zh: "把你加为好友",
    hi: "ने आपको मित्र के रूप में जोड़ा", ar: "أضافك صديقًا",
  },
  "inbox.kind.exchange_signed": {
    en: "signed your exchange", es: "firmó tu intercambio",
    fr: "a signé votre échange", de: "hat deinen Austausch unterzeichnet",
    pt: "assinou sua troca", it: "ha firmato il tuo scambio",
    ja: "があなたの取引に署名しました", zh: "签署了你的交换协议",
    hi: "ने आपके विनिमय पर हस्ताक्षर किए", ar: "وقّع على تبادلك",
  },
  "inbox.kind.guest_accepted": {
    en: "gave you a place on their stream",
    es: "te dio un lugar en su transmisión",
    fr: "vous a donné une place dans son direct",
    de: "hat dir einen Platz in seinem Stream gegeben",
    pt: "deu a você um lugar na transmissão",
    it: "ti ha dato un posto nella sua diretta",
    ja: "が配信への出演を認めました", zh: "让你加入了他们的直播",
    hi: "ने आपको अपनी स्ट्रीम में जगह दी", ar: "منحك مكانًا في بثه",
  },
  "nav.corner": {
    en: "Your corner", es: "Tu rincón", fr: "Votre coin", de: "Deine Ecke",
    pt: "O seu cantinho", it: "Il tuo angolo", ja: "あなたのコーナー", zh: "你的角落",
    hi: "आपका कोना", ar: "ركنك",
  },
  "corner.title": {
    en: "Your corner", es: "Tu rincón", fr: "Votre coin", de: "Deine Ecke",
    pt: "O seu cantinho", it: "Il tuo angolo", ja: "あなたのコーナー", zh: "你的角落",
    hi: "आपका कोना", ar: "ركنك",
  },
  "corner.sub": {
    en: "your homepage and your messages — the person's own surfaces",
    es: "tu página personal y tus mensajes — las superficies de la persona",
    fr: "votre page personnelle et vos messages — les surfaces de la personne",
    de: "deine Startseite und deine Nachrichten — die Flächen der Person",
    pt: "a sua página pessoal e as suas mensagens — as superfícies da pessoa",
    it: "la tua pagina personale e i tuoi messaggi — le superfici della persona",
    ja: "あなたのホームページとメッセージ — 本人のための場所",
    zh: "你的主页和你的消息 — 属于本人的界面",
    hi: "आपका होमपेज और आपके संदेश — व्यक्ति की अपनी जगहें",
    ar: "صفحتك الشخصية ورسائلك — مساحات الشخص نفسه",
  },
  "corner.page": {
    en: "Your homepage", es: "Tu página personal", fr: "Votre page personnelle",
    de: "Deine Startseite", pt: "A sua página pessoal", it: "La tua pagina personale",
    ja: "あなたのホームページ", zh: "你的主页", hi: "आपका होमपेज", ar: "صفحتك الشخصية",
  },
  "corner.walls": {
    en: "Hex colors, http(s) links, plain text, real friends — the sandbox walls.",
    es: "Colores hex, enlaces http(s), texto plano, amigos reales — los muros del sandbox.",
    fr: "Couleurs hex, liens http(s), texte brut, vrais amis — les murs du bac à sable.",
    de: "Hex-Farben, http(s)-Links, Klartext, echte Freunde — die Wände der Sandbox.",
    pt: "Cores hex, links http(s), texto simples, amigos reais — as paredes da sandbox.",
    it: "Colori hex, link http(s), testo semplice, amici veri — i muri della sandbox.",
    ja: "16進カラー、http(s) リンク、プレーンテキスト、実際の友だち — サンドボックスの壁。",
    zh: "十六进制颜色、http(s) 链接、纯文本、真实好友 — 沙盒之墙。",
    hi: "हेक्स रंग, http(s) लिंक, सादा पाठ, असली दोस्त — सैंडबॉक्स की दीवारें।",
    ar: "ألوان سداسية وروابط http(s) ونص عادي وأصدقاء حقيقيون — جدران الصندوق الرملي.",
  },
  "corner.headline": {
    en: "Headline", es: "Titular", fr: "Accroche", de: "Überschrift",
    pt: "Título", it: "Titolo", ja: "見出し", zh: "标题", hi: "शीर्षक", ar: "العنوان",
  },
  "corner.about": {
    en: "About you", es: "Sobre ti", fr: "À propos de vous", de: "Über dich",
    pt: "Sobre si", it: "Su di te", ja: "自己紹介", zh: "关于你", hi: "आपके बारे में", ar: "عنك",
  },
  "corner.bg": {
    en: "Background color", es: "Color de fondo", fr: "Couleur de fond",
    de: "Hintergrundfarbe", pt: "Cor de fundo", it: "Colore di sfondo",
    ja: "背景色", zh: "背景色", hi: "पृष्ठभूमि रंग", ar: "لون الخلفية",
  },
  "corner.accent": {
    en: "Accent color", es: "Color de acento", fr: "Couleur d'accent",
    de: "Akzentfarbe", pt: "Cor de destaque", it: "Colore d'accento",
    ja: "アクセント色", zh: "强调色", hi: "मुख्य रंग", ar: "لون التمييز",
  },
  "corner.links": {
    en: "Links (one per line: label then URL)",
    es: "Enlaces (uno por línea: etiqueta y URL)",
    fr: "Liens (un par ligne : libellé puis URL)",
    de: "Links (einer pro Zeile: Titel, dann URL)",
    pt: "Links (um por linha: rótulo e URL)",
    it: "Link (uno per riga: etichetta poi URL)",
    ja: "リンク（1行に1つ：ラベルとURL）", zh: "链接（每行一个：名称加网址）",
    hi: "लिंक (प्रति पंक्ति एक: लेबल फिर URL)", ar: "روابط (واحد لكل سطر: التسمية ثم الرابط)",
  },
  "corner.tops": {
    en: "Top friends (profile ids, comma-separated)",
    es: "Mejores amigos (ids de perfil, separados por comas)",
    fr: "Meilleurs amis (ids de profil, séparés par des virgules)",
    de: "Top-Freunde (Profil-IDs, kommagetrennt)",
    pt: "Melhores amigos (ids de perfil, separados por vírgulas)",
    it: "Migliori amici (id profilo, separati da virgole)",
    ja: "トップフレンド（プロフィールID、カンマ区切り）",
    zh: "挚友（档案 ID，用逗号分隔）",
    hi: "टॉप फ्रेंड्स (प्रोफ़ाइल आईडी, अल्पविराम से अलग)",
    ar: "أفضل الأصدقاء (معرّفات الملفات، مفصولة بفواصل)",
  },
  "corner.save": {
    en: "Save the page", es: "Guardar la página", fr: "Enregistrer la page",
    de: "Seite speichern", pt: "Guardar a página", it: "Salva la pagina",
    ja: "ページを保存", zh: "保存页面", hi: "पृष्ठ सहेजें", ar: "احفظ الصفحة",
  },
  "corner.saved": {
    en: "Saved.", es: "Guardado.", fr: "Enregistré.", de: "Gespeichert.",
    pt: "Guardado.", it: "Salvato.", ja: "保存しました。", zh: "已保存。",
    hi: "सहेज लिया गया।", ar: "تم الحفظ.",
  },
  "corner.visit": {
    en: "Visit a homepage", es: "Visitar una página", fr: "Visiter une page",
    de: "Eine Startseite besuchen", pt: "Visitar uma página", it: "Visita una pagina",
    ja: "ホームページを見る", zh: "访问主页", hi: "होमपेज देखें", ar: "زر صفحة",
  },
  "corner.visit_id": {
    en: "Profile id", es: "Id del perfil", fr: "Id du profil", de: "Profil-ID",
    pt: "Id do perfil", it: "Id del profilo", ja: "プロフィールID", zh: "档案 ID",
    hi: "प्रोफ़ाइल आईडी", ar: "معرّف الملف",
  },
  "corner.visit_go": {
    en: "Look", es: "Ver", fr: "Voir", de: "Ansehen", pt: "Ver", it: "Guarda",
    ja: "見る", zh: "查看", hi: "देखें", ar: "اعرض",
  },
  "corner.their_tops": {
    en: "Top friends", es: "Mejores amigos", fr: "Meilleurs amis",
    de: "Top-Freunde", pt: "Melhores amigos", it: "Migliori amici",
    ja: "トップフレンド", zh: "挚友", hi: "टॉप फ्रेंड्स", ar: "أفضل الأصدقاء",
  },
  "corner.messages": {
    en: "Messages", es: "Mensajes", fr: "Messages", de: "Nachrichten",
    pt: "Mensagens", it: "Messaggi", ja: "メッセージ", zh: "消息", hi: "संदेश", ar: "الرسائل",
  },
  "corner.friends_only": {
    en: "Between friends only — the friendship is the consent record.",
    es: "Solo entre amigos — la amistad es el registro de consentimiento.",
    fr: "Entre amis seulement — l'amitié est le registre du consentement.",
    de: "Nur unter Freunden — die Freundschaft ist die Einwilligung.",
    pt: "Só entre amigos — a amizade é o registo de consentimento.",
    it: "Solo tra amici — l'amicizia è il registro del consenso.",
    ja: "友だち同士だけ — 友情が同意の記録です。",
    zh: "仅限好友之间 — 友谊即同意记录。",
    hi: "केवल दोस्तों के बीच — दोस्ती ही सहमति का रिकॉर्ड है।",
    ar: "بين الأصدقاء فقط — الصداقة هي سجل الموافقة.",
  },
  "corner.open": {
    en: "Open", es: "Abrir", fr: "Ouvrir", de: "Öffnen", pt: "Abrir",
    it: "Apri", ja: "開く", zh: "打开", hi: "खोलें", ar: "افتح",
  },
  "corner.to": {
    en: "To (profile id)", es: "Para (id de perfil)", fr: "À (id de profil)",
    de: "An (Profil-ID)", pt: "Para (id de perfil)", it: "A (id profilo)",
    ja: "宛先（プロフィールID）", zh: "发给（档案 ID）", hi: "किसे (प्रोफ़ाइल आईडी)",
    ar: "إلى (معرّف الملف)",
  },
  "corner.send": {
    en: "Send", es: "Enviar", fr: "Envoyer", de: "Senden", pt: "Enviar",
    it: "Invia", ja: "送信", zh: "发送", hi: "भेजें", ar: "أرسل",
  },
  "switches.title": {
    en: "Your switches", es: "Tus interruptores", fr: "Vos interrupteurs",
    de: "Deine Schalter", pt: "Os seus interruptores", it: "I tuoi interruttori",
    ja: "あなたのスイッチ", zh: "你的开关", hi: "आपके स्विच", ar: "مفاتيحك",
  },
  "switches.note": {
    en: "Turn a feature off and everything downstream refuses by naming this switch.",
    es: "Apaga una función y todo lo demás rehúsa nombrando este interruptor.",
    fr: "Coupez une fonction et tout l'aval refuse en nommant cet interrupteur.",
    de: "Schalte etwas ab, und alles Nachgelagerte lehnt unter Nennung dieses Schalters ab.",
    pt: "Desligue uma função e tudo a jusante recusa nomeando este interruptor.",
    it: "Spegni una funzione e tutto a valle rifiuta nominando questo interruttore.",
    ja: "機能をオフにすると、以後の拒否はこのスイッチの名を挙げて行われます。",
    zh: "关闭某项功能后，下游的一切拒绝都会点名这个开关。",
    hi: "कोई सुविधा बंद करें — आगे की हर मनाही इसी स्विच का नाम लेगी।",
    ar: "أطفئ ميزة وسيرفض كل ما بعدها مع ذكر هذا المفتاح بالاسم.",
  },
  "switches.messaging": {
    en: "Messaging", es: "Mensajería", fr: "Messagerie", de: "Nachrichten",
    pt: "Mensagens", it: "Messaggi", ja: "メッセージ", zh: "消息", hi: "संदेश", ar: "المراسلة",
  },
  "switches.homepage": {
    en: "Homepage is public", es: "Página personal pública",
    fr: "Page personnelle publique", de: "Startseite öffentlich",
    pt: "Página pessoal pública", it: "Pagina personale pubblica",
    ja: "ホームページを公開", zh: "主页公开", hi: "होमपेज सार्वजनिक", ar: "الصفحة عامة",
  },
  "shops.title": {
    en: "Shops", es: "Tiendas", fr: "Boutiques", de: "Läden",
    pt: "Lojas", it: "Negozi", ja: "ショップ", zh: "商店",
    hi: "दुकानें", ar: "المتاجر",
  },
  "shops.sub": {
    en: "goods and services, from businesses and people — not a desk, no sessions",
    es: "bienes y servicios, de negocios y personas — no es un mostrador, sin sesiones",
    fr: "biens et services, d'entreprises et de particuliers — pas un comptoir, pas de sessions",
    de: "Waren und Dienstleistungen von Firmen und Leuten — kein Schalter, keine Sitzungen",
    pt: "bens e serviços, de negócios e pessoas — não é um balcão, sem sessões",
    it: "beni e servizi, da attività e persone — non è un banco, niente sessioni",
    ja: "企業や個人が売る品物とサービス — カウンターではなく、セッションもありません",
    zh: "来自商家和个人的商品与服务 — 不是柜台，没有会话",
    hi: "व्यवसायों और लोगों से सामान और सेवाएँ — यह डेस्क नहीं है, कोई सत्र नहीं",
    ar: "سلع وخدمات من الشركات والأفراد — ليس مكتبًا ولا جلسات",
  },
  "shops.filter": {
    en: "Filter by tag", es: "Filtrar por etiqueta", fr: "Filtrer par étiquette",
    de: "Nach Schlagwort filtern", pt: "Filtrar por etiqueta", it: "Filtra per etichetta",
    ja: "タグで絞り込む", zh: "按标签筛选", hi: "टैग से छाँटें", ar: "تصفية حسب الوسم",
  },
  "shops.search": {
    en: "Search", es: "Buscar", fr: "Rechercher", de: "Suchen",
    pt: "Pesquisar", it: "Cerca", ja: "検索", zh: "搜索", hi: "खोजें", ar: "بحث",
  },
  "shops.none": {
    en: "No shops yet — open the first one below.",
    es: "Aún no hay tiendas — abre la primera abajo.",
    fr: "Pas encore de boutique — ouvrez la première ci-dessous.",
    de: "Noch keine Läden — eröffne unten den ersten.",
    pt: "Ainda não há lojas — abra a primeira abaixo.",
    it: "Ancora nessun negozio — apri il primo qui sotto.",
    ja: "まだショップがありません — 下から最初の一軒を開いてください。",
    zh: "还没有商店 — 在下方开设第一家。",
    hi: "अभी कोई दुकान नहीं — नीचे पहली दुकान खोलें।",
    ar: "لا متاجر بعد — افتح أول متجر أدناه.",
  },
  "shops.browse": {
    en: "Browse", es: "Ver", fr: "Parcourir", de: "Ansehen",
    pt: "Ver", it: "Sfoglia", ja: "見る", zh: "逛逛", hi: "देखें", ar: "تصفّح",
  },
  "shops.buyer_id": {
    en: "Buyer (interactor id)", es: "Comprador (id de interactor)",
    fr: "Acheteur (id d'interacteur)", de: "Käufer (Interactor-ID)",
    pt: "Comprador (id de interator)", it: "Acquirente (id interactor)",
    ja: "購入者（インタラクターID）", zh: "买家（互动者 ID）",
    hi: "खरीदार (इंटरैक्टर आईडी)", ar: "المشتري (معرّف المتفاعل)",
  },
  "shops.buyer_token": {
    en: "Buyer token", es: "Token del comprador", fr: "Jeton de l'acheteur",
    de: "Käufer-Token", pt: "Token do comprador", it: "Token dell'acquirente",
    ja: "購入者トークン", zh: "买家令牌", hi: "खरीदार टोकन", ar: "رمز المشتري",
  },
  "shops.quantity": {
    en: "Quantity", es: "Cantidad", fr: "Quantité", de: "Menge",
    pt: "Quantidade", it: "Quantità", ja: "数量", zh: "数量", hi: "मात्रा", ar: "الكمية",
  },
  "shops.order": {
    en: "Order", es: "Pedir", fr: "Commander", de: "Bestellen",
    pt: "Encomendar", it: "Ordina", ja: "注文", zh: "下单", hi: "ऑर्डर करें", ar: "اطلب",
  },
  "shops.ordered": {
    en: "Order placed", es: "Pedido realizado", fr: "Commande passée",
    de: "Bestellung aufgegeben", pt: "Pedido feito", it: "Ordine effettuato",
    ja: "注文しました", zh: "已下单", hi: "ऑर्डर हो गया", ar: "تم الطلب",
  },
  "shops.mine": {
    en: "Your orders", es: "Tus pedidos", fr: "Vos commandes",
    de: "Deine Bestellungen", pt: "Os seus pedidos", it: "I tuoi ordini",
    ja: "あなたの注文", zh: "你的订单", hi: "आपके ऑर्डर", ar: "طلباتك",
  },
  "shops.cancel": {
    en: "Cancel", es: "Cancelar", fr: "Annuler", de: "Stornieren",
    pt: "Cancelar", it: "Annulla", ja: "キャンセル", zh: "取消", hi: "रद्द करें", ar: "إلغاء",
  },
  "shops.till": {
    en: "Your till", es: "Tu caja", fr: "Votre caisse", de: "Deine Kasse",
    pt: "A sua caixa", it: "La tua cassa", ja: "あなたのレジ", zh: "你的收银台",
    hi: "आपका गल्ला", ar: "صندوقك",
  },
  "shops.till_note": {
    en: "One shop per profile; opening again edits it. Fulfilment credits your ledger — simulated money, real accounting.",
    es: "Una tienda por perfil; abrir de nuevo la edita. Completar un pedido abona tu libro — dinero simulado, contabilidad real.",
    fr: "Une boutique par profil ; rouvrir la modifie. L'exécution crédite votre registre — argent simulé, comptabilité réelle.",
    de: "Ein Laden pro Profil; erneutes Öffnen bearbeitet ihn. Erfüllung schreibt deinem Buch gut — simuliertes Geld, echte Buchführung.",
    pt: "Uma loja por perfil; abrir de novo edita-a. Concluir credita o seu livro — dinheiro simulado, contabilidade real.",
    it: "Un negozio per profilo; riaprirlo lo modifica. L'evasione accredita il tuo registro — denaro simulato, contabilità reale.",
    ja: "プロフィールごとに一軒。再度開くと編集になります。履行で台帳に記帳 — お金は擬似、記帳は本物。",
    zh: "每个档案一家店；再次开店即编辑。履约会记入你的账本 — 模拟货币，真实记账。",
    hi: "प्रति प्रोफ़ाइल एक दुकान; दोबारा खोलना संपादन है। पूर्ति आपके बहीखाते में जमा होती है — नकली पैसा, असली हिसाब।",
    ar: "متجر واحد لكل ملف؛ فتحه مجددًا يعدّله. الإنجاز يُقيّد في دفترك — مال محاكى ومحاسبة حقيقية.",
  },
  "shops.name": {
    en: "Shop name", es: "Nombre de la tienda", fr: "Nom de la boutique",
    de: "Ladenname", pt: "Nome da loja", it: "Nome del negozio",
    ja: "ショップ名", zh: "店铺名称", hi: "दुकान का नाम", ar: "اسم المتجر",
  },
  "shops.tag": {
    en: "Tag", es: "Etiqueta", fr: "Étiquette", de: "Schlagwort",
    pt: "Etiqueta", it: "Etichetta", ja: "タグ", zh: "标签", hi: "टैग", ar: "الوسم",
  },
  "shops.blurb": {
    en: "Blurb", es: "Descripción", fr: "Présentation", de: "Beschreibung",
    pt: "Descrição", it: "Descrizione", ja: "紹介文", zh: "简介", hi: "विवरण", ar: "نبذة",
  },
  "shops.open": {
    en: "Open the shop", es: "Abrir la tienda", fr: "Ouvrir la boutique",
    de: "Laden eröffnen", pt: "Abrir a loja", it: "Apri il negozio",
    ja: "ショップを開く", zh: "开店", hi: "दुकान खोलें", ar: "افتح المتجر",
  },
  "shops.signin": {
    en: "Sign in as the profile owner first.",
    es: "Primero inicia sesión como propietario del perfil.",
    fr: "Connectez-vous d'abord comme propriétaire du profil.",
    de: "Melde dich zuerst als Profilinhaber an.",
    pt: "Inicie sessão primeiro como proprietário do perfil.",
    it: "Accedi prima come proprietario del profilo.",
    ja: "先にプロフィールの所有者としてサインインしてください。",
    zh: "请先以档案所有者身份登录。",
    hi: "पहले प्रोफ़ाइल स्वामी के रूप में साइन इन करें।",
    ar: "سجّل الدخول أولًا بصفتك مالك الملف.",
  },
  "shops.offer_title": {
    en: "Offering", es: "Artículo", fr: "Article", de: "Angebot",
    pt: "Artigo", it: "Articolo", ja: "商品", zh: "商品", hi: "पेशकश", ar: "المعروض",
  },
  "shops.price": {
    en: "Price", es: "Precio", fr: "Prix", de: "Preis",
    pt: "Preço", it: "Prezzo", ja: "価格", zh: "价格", hi: "क़ीमत", ar: "السعر",
  },
  "shops.goods": {
    en: "goods", es: "bienes", fr: "biens", de: "Waren",
    pt: "bens", it: "beni", ja: "品物", zh: "商品", hi: "सामान", ar: "سلع",
  },
  "shops.service": {
    en: "service", es: "servicio", fr: "service", de: "Dienstleistung",
    pt: "serviço", it: "servizio", ja: "サービス", zh: "服务", hi: "सेवा", ar: "خدمة",
  },
  "shops.kind": {
    en: "Kind", es: "Tipo", fr: "Type", de: "Art",
    pt: "Tipo", it: "Tipo", ja: "種類", zh: "类型", hi: "प्रकार", ar: "النوع",
  },
  "shops.add": {
    en: "Add", es: "Añadir", fr: "Ajouter", de: "Hinzufügen",
    pt: "Adicionar", it: "Aggiungi", ja: "追加", zh: "添加", hi: "जोड़ें", ar: "أضف",
  },
  "shops.retire": {
    en: "Retire", es: "Retirar", fr: "Retirer", de: "Zurückziehen",
    pt: "Retirar", it: "Ritira", ja: "取り下げる", zh: "下架", hi: "हटाएँ", ar: "اسحب",
  },
  "shops.book": {
    en: "Order book", es: "Libro de pedidos", fr: "Carnet de commandes",
    de: "Auftragsbuch", pt: "Livro de pedidos", it: "Registro ordini",
    ja: "受注一覧", zh: "订单簿", hi: "ऑर्डर बही", ar: "سجل الطلبات",
  },
  "shops.accept": {
    en: "Accept", es: "Aceptar", fr: "Accepter", de: "Annehmen",
    pt: "Aceitar", it: "Accetta", ja: "受ける", zh: "接受", hi: "स्वीकारें", ar: "اقبل",
  },
  "shops.decline": {
    en: "Decline", es: "Rechazar", fr: "Refuser", de: "Ablehnen",
    pt: "Recusar", it: "Rifiuta", ja: "断る", zh: "拒绝", hi: "अस्वीकारें", ar: "ارفض",
  },
  "shops.fulfil": {
    en: "Fulfil", es: "Completar", fr: "Exécuter", de: "Erfüllen",
    pt: "Concluir", it: "Evadi", ja: "履行する", zh: "履约", hi: "पूर्ति करें", ar: "أنجز",
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
  "pub.event.opened": {
    en: "opened",
    es: "abierta",
    fr: "ouverte",
    de: "eröffnet",
    pt: "aberta",
    it: "aperta",
    ja: "受理",
    zh: "已提出",
    hi: "खोला गया",
    ar: "فُتحت",
  },
  "pub.event.reattested": {
    en: "basis re-attested",
    es: "base reacreditada",
    fr: "base réattestée",
    de: "Grundlage erneut bestätigt",
    pt: "base reatestada",
    it: "base riattestata",
    ja: "根拠を再証明",
    zh: "已重新证明依据",
    hi: "आधार पुनः प्रमाणित",
    ar: "أُعيد إثبات الأساس",
  },
  "pub.event.upheld": {
    en: "upheld",
    es: "estimada",
    fr: "retenue",
    de: "stattgegeben",
    pt: "deferida",
    it: "accolta",
    ja: "認容",
    zh: "已支持",
    hi: "स्वीकृत",
    ar: "قُبلت",
  },
  "pub.event.dismissed": {
    en: "dismissed",
    es: "desestimada",
    fr: "rejetée",
    de: "abgewiesen",
    pt: "indeferida",
    it: "respinta",
    ja: "却下",
    zh: "已驳回",
    hi: "खारिज",
    ar: "رُفضت",
  },
  "pub.event.withdrawn": {
    en: "consent withdrawn",
    es: "consentimiento retirado",
    fr: "consentement retiré",
    de: "Einwilligung zurückgezogen",
    pt: "consentimento retirado",
    it: "consenso ritirato",
    ja: "同意の撤回",
    zh: "已撤回同意",
    hi: "सहमति वापस",
    ar: "سُحبت الموافقة",
  },
  "pub.event.revoked": {
    en: "authorization revoked",
    es: "autorización revocada",
    fr: "autorisation révoquée",
    de: "Autorisierung widerrufen",
    pt: "autorização revogada",
    it: "autorizzazione revocata",
    ja: "承認の取り消し",
    zh: "已撤销授权",
    hi: "प्राधिकरण रद्द",
    ar: "أُلغي التفويض",
  },
  "pub.event.terminated": {
    en: "profile terminated",
    es: "perfil terminado",
    fr: "profil supprimé",
    de: "Profil beendet",
    pt: "perfil terminado",
    it: "profilo terminato",
    ja: "プロフィール終了",
    zh: "资料已终止",
    hi: "प्रोफ़ाइल समाप्त",
    ar: "أُنهي الملف",
  },
  "pub.actor.objector": {
    en: "you",
    es: "usted",
    fr: "vous",
    de: "Sie",
    pt: "você",
    it: "tu",
    ja: "あなた",
    zh: "你",
    hi: "आप",
    ar: "أنت",
  },
  "pub.actor.owner": {
    en: "the owner",
    es: "el titular",
    fr: "le propriétaire",
    de: "die Inhaberin oder der Inhaber",
    pt: "o titular",
    it: "il titolare",
    ja: "所有者",
    zh: "所有者",
    hi: "स्वामी",
    ar: "المالك",
  },
  "pub.actor.reviewer": {
    en: "a reviewer",
    es: "un revisor",
    fr: "un examinateur",
    de: "eine prüfende Person",
    pt: "um revisor",
    it: "un revisore",
    ja: "審査担当",
    zh: "审核人",
    hi: "समीक्षक",
    ar: "مُراجِع",
  },
  "pub.actor.subject": {
    en: "the subject",
    es: "el sujeto",
    fr: "la personne concernée",
    de: "die betroffene Person",
    pt: "o titular dos dados",
    it: "la persona interessata",
    ja: "本人",
    zh: "当事人",
    hi: "संबंधित व्यक्ति",
    ar: "الشخص المعني",
  },
  "pub.actor.estate": {
    en: "the estate",
    es: "la sucesión",
    fr: "la succession",
    de: "der Nachlass",
    pt: "o espólio",
    it: "gli eredi",
    ja: "遺族",
    zh: "遗产代表",
    hi: "संपदा",
    ar: "الورثة",
  },
  "pub.actor.system": {
    en: "the platform",
    es: "la plataforma",
    fr: "la plateforme",
    de: "die Plattform",
    pt: "a plataforma",
    it: "la piattaforma",
    ja: "プラットフォーム",
    zh: "平台",
    hi: "प्लेटफ़ॉर्म",
    ar: "المنصة",
  },
  "pub.timeline.title": {
    en: "What has happened to your case",
    es: "Qué ha pasado con su caso",
    fr: "Ce qu'il est advenu de votre dossier",
    de: "Was mit Ihrem Fall geschehen ist",
    pt: "O que aconteceu ao seu caso",
    it: "Cosa è successo al tuo caso",
    ja: "あなたの案件の経過",
    zh: "你的案件进展如何",
    hi: "आपके मामले में क्या हुआ",
    ar: "ما جرى في قضيتك",
  },
  "pub.timeline.lead": {
    en: "The record of your own case: what happened, who did it, and when. Reasons and other free text are not repeated here — you wrote yours, and nobody else's is yours to read.",
    es: "El registro de su propio caso: qué ocurrió, quién lo hizo y cuándo. Los motivos y demás texto libre no se repiten aquí: el suyo lo escribió usted, y el de los demás no le corresponde leerlo.",
    fr: "Le registre de votre propre dossier : ce qui s'est passé, qui l'a fait et quand. Les motifs et autres textes libres ne sont pas repris ici — le vôtre, vous l'avez écrit, et celui des autres ne vous revient pas.",
    de: "Die Akte Ihres eigenen Falls: was geschah, wer es tat und wann. Begründungen und anderer Freitext werden hier nicht wiederholt — Ihre haben Sie selbst geschrieben, und die anderer steht Ihnen nicht zu.",
    pt: "O registo do seu próprio caso: o que aconteceu, quem o fez e quando. Os motivos e outro texto livre não são repetidos aqui — o seu escreveu-o você, e o dos outros não lhe cabe ler.",
    it: "Il registro del tuo caso: cosa è successo, chi lo ha fatto e quando. Le motivazioni e gli altri testi liberi non sono ripetuti qui — la tua l'hai scritta tu, e quella altrui non spetta a te leggerla.",
    ja: "あなた自身の案件の記録です。何が、誰によって、いつ行われたか。理由などの自由記述はここには載せません。あなたの理由はあなたが書いたものであり、他人のものはあなたが読むべきものではないからです。",
    zh: "你自己案件的记录：发生了什么、由谁执行、在何时。理由和其他自由文本不在此重复 — 你的理由是你自己写的，而别人的不该由你来读。",
    hi: "आपके अपने मामले का रिकॉर्ड: क्या हुआ, किसने किया, और कब। कारण और अन्य मुक्त पाठ यहाँ दोहराए नहीं जाते — अपना आपने लिखा था, और दूसरों का पढ़ना आपका काम नहीं।",
    ar: "سجل قضيتك أنت: ما الذي حدث، ومن فعله، ومتى. أما الأسباب وسائر النص الحر فلا تتكرر هنا — سببك كتبته أنت، وسبب غيرك ليس لك أن تقرأه.",
  },
  "chat.degraded.head": {
    en: "Written by the built-in fallback on this machine, not by",
    es: "Escrito por el motor de reserva de esta máquina, no por",
    fr: "Écrit par le moteur de secours de cette machine, et non par",
    de: "Geschrieben vom eingebauten Ersatz auf diesem Rechner, nicht von",
    pt: "Escrito pelo motor de reserva desta máquina e não por",
    it: "Scritto dal motore di riserva di questa macchina, non da",
    ja: "この端末の内蔵フォールバックが書いたもので、次のモデルではありません:",
    zh: "由本机内置的后备模型写成，而不是",
    hi: "इस मशीन के अंतर्निहित फ़ॉलबैक द्वारा लिखा गया, न कि",
    ar: "كتبه البديل المدمج في هذا الجهاز، لا",
  },
  "chat.degraded.tail": {
    en: "— that model could not be reached. Check the key in Settings → Model.",
    es: "— no se pudo contactar con ese modelo. Revise la clave en Ajustes → Modelo.",
    fr: "— ce modèle n'a pas pu être joint. Vérifiez la clé dans Réglages → Modèle.",
    de: "— dieses Modell war nicht erreichbar. Prüfen Sie den Schlüssel unter Einstellungen → Modell.",
    pt: "— não foi possível contactar esse modelo. Verifique a chave em Definições → Modelo.",
    it: "— non è stato possibile raggiungere quel modello. Controlla la chiave in Impostazioni → Modello.",
    ja: "— そのモデルに接続できませんでした。設定 → モデル でキーをご確認ください。",
    zh: "— 无法连接该模型。请在“设置 → 模型”中检查密钥。",
    hi: "— उस मॉडल तक पहुँचा नहीं जा सका। सेटिंग्स → मॉडल में कुंजी जाँचें।",
    ar: "— تعذّر الوصول إلى ذلك النموذج. تحقّق من المفتاح في الإعدادات ← النموذج.",
  },
  "pub.timeline.go": {
    en: "Show the record",
    es: "Ver el registro",
    fr: "Afficher le registre",
    de: "Akte anzeigen",
    pt: "Ver o registo",
    it: "Mostra il registro",
    ja: "記録を見る",
    zh: "查看记录",
    hi: "रिकॉर्ड दिखाएँ",
    ar: "أظهر السجل",
  },
  "pub.timeline.sealed": {
    en: "sealed in the vault",
    es: "sellado en la bóveda",
    fr: "scellé dans le coffre",
    de: "im Tresor versiegelt",
    pt: "selado no cofre",
    it: "sigillato nella cassaforte",
    ja: "保管庫に封印済み",
    zh: "已封存于保险库",
    hi: "वॉल्ट में सील किया गया",
    ar: "مختوم في الخزنة",
  },
  "pub.timeline.empty": {
    en: "Nothing on this case yet.",
    es: "Todavía nada en este caso.",
    fr: "Rien encore sur ce dossier.",
    de: "Zu diesem Fall noch nichts.",
    pt: "Ainda nada neste caso.",
    it: "Ancora nulla su questo caso.",
    ja: "この案件にはまだ何もありません。",
    zh: "此案件暂无记录。",
    hi: "इस मामले पर अभी कुछ नहीं।",
    ar: "لا شيء في هذه القضية بعد.",
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
  "pub.notoken.signedin": {
    en: "If you do have a profile, signing in gets you the same forms with your own case history beside them.",
    es: "Si sí tiene un perfil, iniciar sesión le da los mismos formularios con su propio historial de casos al lado.",
    fr: "Si vous avez un profil, vous connecter vous donne les mêmes formulaires avec l'historique de vos dossiers à côté.",
    de: "Wenn Sie doch ein Profil haben, bekommen Sie nach der Anmeldung dieselben Formulare mit Ihrem eigenen Fallverlauf daneben.",
    pt: "Se você tiver um perfil, entrar dá acesso aos mesmos formulários com o seu próprio histórico de casos ao lado.",
    it: "Se hai un profilo, accedendo trovi gli stessi moduli con accanto lo storico dei tuoi casi.",
    ja: "プロフィールをお持ちの場合は、サインインすると同じフォームがご自身の申立て履歴とともに表示されます。",
    zh: "如果你确实有资料，登录后可看到同样的表单，旁边还会列出你自己的案件记录。",
    hi: "यदि आपके पास प्रोफ़ाइल है, तो साइन इन करने पर वही फ़ॉर्म आपके अपने केस इतिहास के साथ मिलते हैं।",
    ar: "إن كان لديك ملف بالفعل، فتسجيل الدخول يمنحك النماذج نفسها مع سجل قضاياك بجانبها.",
  },
  "pub.object.opened": {
    en: "Opened — {id}",
    es: "Abierta — {id}",
    fr: "Ouverte — {id}",
    de: "Eröffnet — {id}",
    pt: "Aberta — {id}",
    it: "Aperta — {id}",
    ja: "受付済み — {id}",
    zh: "已提出 — {id}",
    hi: "दर्ज — {id}",
    ar: "فُتح — {id}",
  },
  "pub.object.opened.status": {
    en: "The profile is {now} from this moment. It was {before}, and if the objection is dismissed it goes back to exactly that.",
    es: "El perfil queda {now} desde este momento. Era {before}, y si la objeción se desestima vuelve exactamente a eso.",
    fr: "Le profil est {now} à partir de maintenant. Il était {before}, et si la contestation est rejetée il y revient exactement.",
    de: "Das Profil ist ab sofort {now}. Es war {before}, und wenn der Widerspruch abgewiesen wird, kehrt es genau dorthin zurück.",
    pt: "O perfil fica {now} a partir deste momento. Era {before}, e se a contestação for rejeitada volta exatamente a isso.",
    it: "Il profilo è {now} da questo momento. Era {before}, e se la contestazione viene respinta torna esattamente a quello.",
    ja: "プロフィールはこの時点から {now} になります。それまでは {before} でした。異議が棄却されれば、そのままの状態に戻ります。",
    zh: "该资料从此刻起为 {now}。此前是 {before}；若异议被驳回，将完全恢复原状。",
    hi: "इस क्षण से प्रोफ़ाइल {now} है। यह {before} थी, और यदि आपत्ति खारिज होती है तो वह ठीक वैसी ही हो जाएगी।",
    ar: "الملف {now} اعتبارًا من هذه اللحظة. كان {before}، وإذا رُفض الاعتراض عاد إلى ذلك تمامًا.",
  },
  "pub.check.against": {
    en: "· opened against {ref}",
    es: "· abierta con la referencia {ref}",
    fr: "· ouverte au nom de {ref}",
    de: "· eröffnet unter {ref}",
    pt: "· aberta com a referência {ref}",
    it: "· aperta con il riferimento {ref}",
    ja: "· 申立て参照 {ref}",
    zh: "· 以 {ref} 提出",
    hi: "· {ref} के संदर्भ से दर्ज",
    ar: "· فُتح باسم {ref}",
  },
  "pub.same.signature": {
    en: "Signature {sig} · invariant across {across}.",
    es: "Firma {sig} · invariable en {across}.",
    fr: "Signature {sig} · invariante sur {across}.",
    de: "Signatur {sig} · unverändert über {across}.",
    pt: "Assinatura {sig} · invariável em {across}.",
    it: "Firma {sig} · invariante su {across}.",
    ja: "署名 {sig} · {across} を通じて不変。",
    zh: "签名 {sig} · 在 {across} 之间保持不变。",
    hi: "हस्ताक्षर {sig} · {across} में अपरिवर्तित।",
    ar: "التوقيع {sig} · ثابت عبر {across}.",
  },
  "pub.same.alsoon": {
    en: "Also present on: {surfaces}.",
    es: "También presente en: {surfaces}.",
    fr: "Également présent sur : {surfaces}.",
    de: "Auch vorhanden auf: {surfaces}.",
    pt: "Também presente em: {surfaces}.",
    it: "Presente anche su: {surfaces}.",
    ja: "他にも次の場所にあります: {surfaces}。",
    zh: "同时出现在：{surfaces}。",
    hi: "यहाँ भी मौजूद: {surfaces}।",
    ar: "موجود أيضًا على: {surfaces}.",
  },
  "pub.same.forms": {
    en: "Forms: {forms}.",
    es: "Formas: {forms}.",
    fr: "Formes : {forms}.",
    de: "Formen: {forms}.",
    pt: "Formas: {forms}.",
    it: "Forme: {forms}.",
    ja: "形態: {forms}。",
    zh: "形态：{forms}。",
    hi: "रूप: {forms}।",
    ar: "الأشكال: {forms}.",
  },
  "pub.mark.explain": {
    en: "Paste it. This asks whose work it is with no credential id, and keeps answering after the text has been reworded — which is the state text usually arrives in. It is the right question for a stranger holding a screenshot; checking a credential you already hold is a different one and lives inside an account.",
    es: "Péguelo. Esto pregunta de quién es el trabajo sin ningún identificador de credencial, y sigue respondiendo después de que el texto haya sido reescrito, que es el estado en el que suele llegar. Es la pregunta correcta para un desconocido con una captura de pantalla; comprobar una credencial que ya tiene es otra distinta y vive dentro de una cuenta.",
    fr: "Collez-le. Ceci demande à qui appartient le contenu sans aucun identifiant de justificatif, et répond encore après reformulation du texte — l'état dans lequel il arrive le plus souvent. C'est la bonne question pour un inconnu tenant une capture d'écran ; vérifier un justificatif que vous détenez déjà en est une autre, et elle vit dans un compte.",
    de: "Fügen Sie ihn ein. Das fragt, wessen Werk es ist, ohne jede Credential-ID, und antwortet auch noch, nachdem der Text umformuliert wurde — der Zustand, in dem Text meist ankommt. Es ist die richtige Frage für eine fremde Person mit einem Screenshot; ein Nachweis, den Sie bereits halten, ist eine andere Frage und lebt in einem Konto.",
    pt: "Cole-o. Isto pergunta de quem é o trabalho sem qualquer identificador de credencial, e continua respondendo depois de o texto ter sido reescrito — o estado em que o texto costuma chegar. É a pergunta certa para um desconhecido com uma captura de tela; verificar uma credencial que você já possui é outra e vive dentro de uma conta.",
    it: "Incollalo. Questo chiede di chi è il lavoro senza alcun identificativo di credenziale, e continua a rispondere dopo che il testo è stato riformulato — lo stato in cui il testo di solito arriva. È la domanda giusta per uno sconosciuto con uno screenshot; verificare una credenziale che già possiedi è un'altra cosa e vive dentro un account.",
    ja: "貼り付けてください。これは資格情報の ID なしに、それが誰の作かを尋ねます。文章が書き換えられた後でも答え続けます — 実際に届く文章はたいていその状態です。スクリーンショットを手にした見知らぬ人にとって正しい問いです。すでに持っている資格情報を確認するのは別の問いで、それはアカウントの中にあります。",
    zh: "粘贴进来。这会在不需要任何凭据 ID 的情况下询问它出自谁手，并且在文本被改写之后仍能作答 — 而文本通常正是以这种状态出现的。对于手持截图的陌生人，这是正确的问题；核验你已经持有的凭据是另一个问题，它属于账户内部。",
    hi: "इसे चिपकाएँ। यह बिना किसी क्रेडेंशियल आईडी के पूछता है कि यह किसका काम है, और पाठ के शब्द बदल दिए जाने के बाद भी उत्तर देता रहता है — पाठ आम तौर पर इसी हालत में पहुँचता है। स्क्रीनशॉट थामे किसी अजनबी के लिए यही सही सवाल है; जो क्रेडेंशियल आपके पास पहले से है उसे जाँचना अलग सवाल है और वह खाते के भीतर रहता है।",
    ar: "الصقه هنا. هذا يسأل عن صاحب العمل دون أي معرّف اعتماد، ويظل يجيب بعد إعادة صياغة النص — وهي الحالة التي يصل بها النص عادةً. إنه السؤال الصحيح لغريب يحمل لقطة شاشة؛ أما التحقق من اعتماد تملكه بالفعل فسؤال آخر يعيش داخل حساب.",
  },
  "pub.mark.producedby": {
    en: "Produced by a QRME synthetic profile — {state}.",
    es: "Producido por un perfil sintético de QRME — {state}.",
    fr: "Produit par un profil synthétique QRME — {state}.",
    de: "Erzeugt von einem synthetischen QRME-Profil — {state}.",
    pt: "Produzido por um perfil sintético do QRME — {state}.",
    it: "Prodotto da un profilo sintetico QRME — {state}.",
    ja: "QRME の合成プロフィールによる生成物 — {state}。",
    zh: "由 QRME 合成资料生成 — {state}。",
    hi: "QRME की सिंथेटिक प्रोफ़ाइल द्वारा निर्मित — {state}।",
    ar: "من إنتاج ملف اصطناعي في QRME — {state}.",
  },
  "pub.mark.windows": {
    en: "{matched} of {stored} stored windows matched, out of {examined} examined (similarity {similarity}).",
    es: "Coincidieron {matched} de {stored} ventanas almacenadas, de {examined} examinadas (similitud {similarity}).",
    fr: "{matched} fenêtres enregistrées sur {stored} correspondent, sur {examined} examinées (similarité {similarity}).",
    de: "{matched} von {stored} gespeicherten Fenstern stimmten überein, bei {examined} geprüften (Ähnlichkeit {similarity}).",
    pt: "Coincidiram {matched} de {stored} janelas armazenadas, entre {examined} examinadas (similaridade {similarity}).",
    it: "Hanno corrisposto {matched} finestre su {stored} memorizzate, su {examined} esaminate (somiglianza {similarity}).",
    ja: "保存済み {stored} 個のウィンドウのうち {matched} 個が一致しました（検査対象 {examined} 個、類似度 {similarity}）。",
    zh: "在 {examined} 个受检窗口中，已存储的 {stored} 个窗口有 {matched} 个匹配（相似度 {similarity}）。",
    hi: "संग्रहीत {stored} विंडो में से {matched} मेल खाईं, कुल {examined} जाँची गईं (समानता {similarity})।",
    ar: "تطابقت {matched} من أصل {stored} نافذة مخزّنة، من بين {examined} جرى فحصها (التشابه {similarity}).",
  },
  "pub.mark.here": {
    en: "on this deployment",
    es: "en esta instalación",
    fr: "sur ce déploiement",
    de: "auf dieser Installation",
    pt: "nesta instalação",
    it: "su questa installazione",
    ja: "この環境で",
    zh: "在本部署中",
    hi: "इस परिनियोजन पर",
    ar: "في هذا التنصيب",
  },
  "pub.mark.unknown.explain": {
    en: "This says nothing about whether a person wrote it. It says no profile {here} has stamped work that shares enough wording with it.",
    es: "Esto no dice nada sobre si lo escribió una persona. Dice que ningún perfil {here} ha firmado un trabajo que comparta suficiente redacción con él.",
    fr: "Cela ne dit rien sur le fait qu'une personne l'ait écrit. Cela dit qu'aucun profil {here} n'a signé un contenu partageant assez de formulations avec lui.",
    de: "Das sagt nichts darüber, ob ein Mensch es geschrieben hat. Es sagt, dass kein Profil {here} eine Arbeit gestempelt hat, die genug Wortlaut mit ihr teilt.",
    pt: "Isto não diz nada sobre se uma pessoa o escreveu. Diz que nenhum perfil {here} carimbou um trabalho que partilhe redação suficiente com ele.",
    it: "Questo non dice nulla sul fatto che l'abbia scritto una persona. Dice che nessun profilo {here} ha timbrato un lavoro che condivida abbastanza formulazioni con esso.",
    ja: "これは人が書いたかどうかについては何も述べていません。{here}、これと十分に語句を共有する作品に印を付けたプロフィールが存在しない、という意味です。",
    zh: "这并不说明它是否由人所写。它说明的是：{here}没有任何资料曾为与之用词足够相近的作品加过标记。",
    hi: "इससे यह पता नहीं चलता कि इसे किसी व्यक्ति ने लिखा या नहीं। इसका अर्थ है कि {here} किसी प्रोफ़ाइल ने ऐसा काम मुहरबंद नहीं किया जिसकी शब्दावली इससे पर्याप्त मेल खाती हो।",
    ar: "هذا لا يقول شيئًا عمّا إذا كان قد كتبه إنسان. إنه يقول إنه ما من ملف {here} ختم عملًا يشترك معه في ما يكفي من الصياغة.",
  },
  "pub.state.active": {
    en: "active",
    es: "activo",
    fr: "actif",
    de: "aktiv",
    pt: "ativo",
    it: "attivo",
    ja: "有効",
    zh: "有效",
    hi: "सक्रिय",
    ar: "نشط",
  },
  "pub.state.restricted": {
    en: "restricted",
    es: "restringido",
    fr: "restreint",
    de: "beschränkt",
    pt: "restringido",
    it: "limitato",
    ja: "制限中",
    zh: "受限",
    hi: "सीमित",
    ar: "مقيَّد",
  },
  "pub.state.departed": {
    en: "departed",
    es: "fallecido",
    fr: "disparu",
    de: "verstorben",
    pt: "falecido",
    it: "scomparso",
    ja: "故人",
    zh: "已故",
    hi: "दिवंगत",
    ar: "متوفى",
  },
  "pub.state.terminated": {
    en: "terminated",
    es: "terminado",
    fr: "supprimé",
    de: "beendet",
    pt: "terminado",
    it: "terminato",
    ja: "終了",
    zh: "已终止",
    hi: "समाप्त",
    ar: "مُنهى",
  },
  "onb.tagline": {
    en: "Your identity. Your AI.",
    es: "Tu identidad. Tu IA.",
    fr: "Votre identité. Votre IA.",
    de: "Deine Identität. Deine KI.",
    pt: "A sua identidade. A sua IA.",
    it: "La tua identità. La tua IA.",
    ja: "あなたの人格を、あなたのAIに。",
    zh: "你的身份，你的 AI。",
    hi: "आपकी पहचान। आपका AI।",
    ar: "هويتك. ذكاؤك الاصطناعي.",
  },
  "onb.create": {
    en: "Create account",
    es: "Crear cuenta",
    fr: "Créer un compte",
    de: "Konto erstellen",
    pt: "Criar conta",
    it: "Crea account",
    ja: "アカウントを作成",
    zh: "创建账户",
    hi: "खाता बनाएँ",
    ar: "إنشاء حساب",
  },
  "onb.signin": {
    en: "Sign in",
    es: "Iniciar sesión",
    fr: "Se connecter",
    de: "Anmelden",
    pt: "Entrar",
    it: "Accedi",
    ja: "サインイン",
    zh: "登录",
    hi: "साइन इन करें",
    ar: "تسجيل الدخول",
  },
  "onb.signin.with": {
    en: "Sign in with",
    es: "Iniciar sesión con",
    fr: "Se connecter avec",
    de: "Anmelden mit",
    pt: "Entrar com",
    it: "Accedi con",
    ja: "でサインイン",
    zh: "使用以下方式登录",
    hi: "इससे साइन इन करें",
    ar: "تسجيل الدخول عبر",
  },
  "onb.yourname": {
    en: "Your name",
    es: "Tu nombre",
    fr: "Votre nom",
    de: "Dein Name",
    pt: "O seu nome",
    it: "Il tuo nome",
    ja: "お名前",
    zh: "你的名字",
    hi: "आपका नाम",
    ar: "اسمك",
  },
  "onb.email": {
    en: "Email",
    es: "Correo electrónico",
    fr: "E-mail",
    de: "E-Mail",
    pt: "E-mail",
    it: "Email",
    ja: "メールアドレス",
    zh: "电子邮箱",
    hi: "ईमेल",
    ar: "البريد الإلكتروني",
  },
  "onb.password": {
    en: "Password",
    es: "Contraseña",
    fr: "Mot de passe",
    de: "Passwort",
    pt: "Palavra-passe",
    it: "Password",
    ja: "パスワード",
    zh: "密码",
    hi: "पासवर्ड",
    ar: "كلمة المرور",
  },
  "onb.password.again": {
    en: "Re-enter password",
    es: "Repite la contraseña",
    fr: "Confirmez le mot de passe",
    de: "Passwort wiederholen",
    pt: "Repita a palavra-passe",
    it: "Ripeti la password",
    ja: "パスワードを再入力",
    zh: "再次输入密码",
    hi: "पासवर्ड दोबारा दर्ज करें",
    ar: "أعد إدخال كلمة المرور",
  },
  "onb.password.min": {
    en: "At least 8 characters",
    es: "Al menos 8 caracteres",
    fr: "Au moins 8 caractères",
    de: "Mindestens 8 Zeichen",
    pt: "Pelo menos 8 caracteres",
    it: "Almeno 8 caratteri",
    ja: "8文字以上",
    zh: "至少 8 个字符",
    hi: "कम से कम 8 अक्षर",
    ar: "٨ أحرف على الأقل",
  },
  "onb.password.same": {
    en: "Same password again",
    es: "La misma contraseña otra vez",
    fr: "Le même mot de passe",
    de: "Dasselbe Passwort erneut",
    pt: "A mesma palavra-passe",
    it: "La stessa password",
    ja: "同じパスワードをもう一度",
    zh: "再输入一次相同的密码",
    hi: "वही पासवर्ड दोबारा",
    ar: "نفس كلمة المرور مرة أخرى",
  },
  "onb.password.mismatch": {
    en: "⚠ The passwords don't match yet.",
    es: "⚠ Las contraseñas aún no coinciden.",
    fr: "⚠ Les mots de passe ne correspondent pas encore.",
    de: "⚠ Die Passwörter stimmen noch nicht überein.",
    pt: "⚠ As palavras-passe ainda não coincidem.",
    it: "⚠ Le password non coincidono ancora.",
    ja: "⚠ パスワードがまだ一致していません。",
    zh: "⚠ 两次输入的密码还不一致。",
    hi: "⚠ पासवर्ड अभी मेल नहीं खाते।",
    ar: "⚠ كلمتا المرور غير متطابقتين بعد.",
  },
  "onb.code": {
    en: "Verification code",
    es: "Código de verificación",
    fr: "Code de vérification",
    de: "Bestätigungscode",
    pt: "Código de verificação",
    it: "Codice di verifica",
    ja: "確認コード",
    zh: "验证码",
    hi: "सत्यापन कोड",
    ar: "رمز التحقق",
  },
  "onb.code.resend": {
    en: "Resend code",
    es: "Reenviar código",
    fr: "Renvoyer le code",
    de: "Code erneut senden",
    pt: "Reenviar código",
    it: "Invia di nuovo il codice",
    ja: "コードを再送",
    zh: "重新发送验证码",
    hi: "कोड फिर भेजें",
    ar: "إعادة إرسال الرمز",
  },
  "onb.reset.code": {
    en: "Reset code",
    es: "Código de restablecimiento",
    fr: "Code de réinitialisation",
    de: "Zurücksetz-Code",
    pt: "Código de reposição",
    it: "Codice di reimpostazione",
    ja: "リセットコード",
    zh: "重置码",
    hi: "रीसेट कोड",
    ar: "رمز إعادة التعيين",
  },
  "onb.reset.send": {
    en: "Send reset code",
    es: "Enviar código de restablecimiento",
    fr: "Envoyer le code de réinitialisation",
    de: "Zurücksetz-Code senden",
    pt: "Enviar código de reposição",
    it: "Invia codice di reimpostazione",
    ja: "リセットコードを送信",
    zh: "发送重置码",
    hi: "रीसेट कोड भेजें",
    ar: "إرسال رمز إعادة التعيين",
  },
  "onb.password.new": {
    en: "New password",
    es: "Nueva contraseña",
    fr: "Nouveau mot de passe",
    de: "Neues Passwort",
    pt: "Nova palavra-passe",
    it: "Nuova password",
    ja: "新しいパスワード",
    zh: "新密码",
    hi: "नया पासवर्ड",
    ar: "كلمة مرور جديدة",
  },
  "onb.password.new.again": {
    en: "Re-enter new password",
    es: "Repite la nueva contraseña",
    fr: "Confirmez le nouveau mot de passe",
    de: "Neues Passwort wiederholen",
    pt: "Repita a nova palavra-passe",
    it: "Ripeti la nuova password",
    ja: "新しいパスワードを再入力",
    zh: "再次输入新密码",
    hi: "नया पासवर्ड दोबारा दर्ज करें",
    ar: "أعد إدخال كلمة المرور الجديدة",
  },
  "onb.forgot": {
    en: "Forgot password?",
    es: "¿Olvidaste tu contraseña?",
    fr: "Mot de passe oublié ?",
    de: "Passwort vergessen?",
    pt: "Esqueceu-se da palavra-passe?",
    it: "Password dimenticata?",
    ja: "パスワードをお忘れですか？",
    zh: "忘记密码？",
    hi: "पासवर्ड भूल गए?",
    ar: "هل نسيت كلمة المرور؟",
  },
  "onb.back": {
    en: "Back to sign in",
    es: "Volver a iniciar sesión",
    fr: "Retour à la connexion",
    de: "Zurück zur Anmeldung",
    pt: "Voltar a entrar",
    it: "Torna all'accesso",
    ja: "サインインに戻る",
    zh: "返回登录",
    hi: "साइन इन पर वापस जाएँ",
    ar: "العودة إلى تسجيل الدخول",
  },
  "onb.profile.name": {
    en: "Profile name",
    es: "Nombre del perfil",
    fr: "Nom du profil",
    de: "Profilname",
    pt: "Nome do perfil",
    it: "Nome del profilo",
    ja: "プロフィール名",
    zh: "档案名称",
    hi: "प्रोफ़ाइल नाम",
    ar: "اسم الملف",
  },
  "onb.profile.placeholder": {
    en: "Name your assistant",
    es: "Ponle nombre a tu asistente",
    fr: "Nommez votre assistant",
    de: "Benenne deinen Assistenten",
    pt: "Dê um nome ao seu assistente",
    it: "Dai un nome al tuo assistente",
    ja: "アシスタントに名前をつけてください",
    zh: "为你的助手命名",
    hi: "अपने सहायक को नाम दें",
    ar: "سمِّ مساعدك",
  },
  // The desk's service counter — sessions and connections. Translated on
  // arrival rather than recorded: the console backlog is a ratchet that only
  // shrinks, and a new screen section must not add English to it.
  "desk.counter.head": {
    en: "Across the counter", es: "Al otro lado del mostrador",
    fr: "De l'autre côté du comptoir", de: "Über den Tresen",
    pt: "Do outro lado do balcão", it: "Al di là del banco",
    ja: "カウンター越しに", zh: "柜台服务",
    hi: "काउंटर के पार", ar: "عبر المكتب",
  },
  "desk.counter.pitch": {
    en: "The service itself: open a session with a caller and offer to connect something of theirs — their screen, their machine, a program, files. An offer grants nothing; their accept is what opens it, and either of you can end it at any moment.",
    es: "El servicio en sí: abre una sesión con quien llama y ofrece conectar algo suyo — su pantalla, su máquina, un programa, archivos. Una oferta no concede nada; su aceptación es lo que la abre, y cualquiera de los dos puede terminarla en cualquier momento.",
    fr: "Le service lui-même : ouvrez une session avec un appelant et proposez de connecter quelque chose qui lui appartient — son écran, sa machine, un programme, des fichiers. Une offre n'accorde rien ; c'est son accord qui l'ouvre, et chacun de vous peut y mettre fin à tout moment.",
    de: "Der eigentliche Dienst: Eine Sitzung mit einem Anrufer öffnen und anbieten, etwas von ihm zu verbinden — seinen Bildschirm, seine Maschine, ein Programm, Dateien. Ein Angebot gewährt nichts; erst seine Zustimmung öffnet es, und jeder von beiden kann es jederzeit beenden.",
    pt: "O serviço em si: abra uma sessão com quem chama e ofereça ligar algo que é dessa pessoa — o ecrã, a máquina, um programa, ficheiros. Uma oferta não concede nada; é o aceitar dela que a abre, e qualquer um dos dois pode terminá-la a qualquer momento.",
    it: "Il servizio vero e proprio: apri una sessione con chi chiama e offri di connettere qualcosa di suo — lo schermo, la macchina, un programma, dei file. Un'offerta non concede nulla; è il suo consenso ad aprirla, e ognuno dei due può chiuderla in qualsiasi momento.",
    ja: "サービスそのものです。呼び出した人とセッションを開き、その人の何か — 画面、マシン、プログラム、ファイル — の接続を提案します。提案だけでは何も許可されません。開くのは相手の承諾であり、どちらの側もいつでも終了できます。",
    zh: "服务本身：与来访者开启会话，提出连接对方的东西——屏幕、设备、程序、文件。邀请本身不授予任何权限；由对方接受才会打开，且双方任何一方都可随时终止。",
    hi: "सेवा स्वयं: कॉल करने वाले के साथ सत्र खोलें और उनकी कोई चीज़ जोड़ने की पेशकश करें — उनकी स्क्रीन, उनकी मशीन, कोई प्रोग्राम, फ़ाइलें। पेशकश से कुछ नहीं मिलता; उनके स्वीकारने से ही वह खुलती है, और आप दोनों में से कोई भी इसे किसी भी क्षण समाप्त कर सकता है।",
    ar: "الخدمة نفسها: افتح جلسة مع المتصل واعرض توصيل شيء يخصه — شاشته أو جهازه أو برنامجًا أو ملفات. العرض لا يمنح شيئًا؛ قبوله هو ما يفتحه، ويمكن لأي منكما إنهاؤه في أي لحظة.",
  },
  "desk.counter.caller_id": {
    en: "Caller's interactor id", es: "Id de interactor de quien llama",
    fr: "Identifiant d'interacteur de l'appelant", de: "Interactor-ID des Anrufers",
    pt: "Id de interator de quem chama", it: "Id interactor di chi chiama",
    ja: "呼び出した人のインタラクターID", zh: "来访者的互动者 id",
    hi: "कॉल करने वाले की इंटरैक्टर आईडी", ar: "معرّف المتفاعل للمتصل",
  },
  "desk.counter.open": {
    en: "Open a session", es: "Abrir una sesión", fr: "Ouvrir une session",
    de: "Sitzung öffnen", pt: "Abrir uma sessão", it: "Apri una sessione",
    ja: "セッションを開く", zh: "开启会话", hi: "सत्र खोलें", ar: "افتح جلسة",
  },
  "desk.counter.close": {
    en: "Close session", es: "Cerrar la sesión", fr: "Fermer la session",
    de: "Sitzung schließen", pt: "Fechar a sessão", it: "Chiudi la sessione",
    ja: "セッションを閉じる", zh: "关闭会话", hi: "सत्र बंद करें", ar: "أغلق الجلسة",
  },
  "desk.counter.end": {
    en: "End", es: "Terminar", fr: "Mettre fin", de: "Beenden",
    pt: "Terminar", it: "Termina", ja: "終了", zh: "终止", hi: "समाप्त करें", ar: "إنهاء",
  },
  "desk.counter.offer": {
    en: "Offer", es: "Ofrecer", fr: "Proposer", de: "Anbieten",
    pt: "Oferecer", it: "Offri", ja: "提案する", zh: "发出邀请", hi: "पेशकश करें", ar: "اعرض",
  },
  "desk.counter.target": {
    en: "What, by name", es: "Qué cosa, por su nombre", fr: "Quoi, par son nom",
    de: "Was, beim Namen", pt: "O quê, pelo nome", it: "Che cosa, per nome",
    ja: "何を（名前で）", zh: "连接什么（写明名称）", hi: "क्या, नाम से", ar: "ماذا، بالاسم",
  },
  "desk.counter.scope_opt": {
    en: "Scope (optional)", es: "Alcance (opcional)", fr: "Périmètre (facultatif)",
    de: "Umfang (optional)", pt: "Âmbito (opcional)", it: "Ambito (facoltativo)",
    ja: "範囲（任意）", zh: "范围（可选）", hi: "दायरा (वैकल्पिक)", ar: "النطاق (اختياري)",
  },
  "desk.counter.scope_req": {
    en: "Scope — required, in words they will read",
    es: "Alcance — obligatorio, en palabras que la persona leerá",
    fr: "Périmètre — obligatoire, en mots qu'elle lira",
    de: "Umfang — erforderlich, in Worten, die die Person lesen wird",
    pt: "Âmbito — obrigatório, em palavras que a pessoa lerá",
    it: "Ambito — obbligatorio, in parole che la persona leggerà",
    ja: "範囲 — 必須。相手が読む言葉で",
    zh: "范围——必填，用对方会读到的文字",
    hi: "दायरा — अनिवार्य, उन शब्दों में जो वह व्यक्ति पढ़ेगा",
    ar: "النطاق — إلزامي، بكلمات سيقرؤها الشخص",
  },
  "desk.counter.kind.screen": {
    en: "see their screen", es: "ver su pantalla", fr: "voir son écran",
    de: "ihren Bildschirm sehen", pt: "ver o ecrã da pessoa", it: "vedere il suo schermo",
    ja: "相手の画面を見る", zh: "查看对方屏幕", hi: "उनकी स्क्रीन देखें", ar: "رؤية شاشته",
  },
  "desk.counter.kind.remote": {
    en: "drive their machine", es: "manejar su máquina", fr: "piloter sa machine",
    de: "ihre Maschine steuern", pt: "conduzir a máquina da pessoa", it: "guidare la sua macchina",
    ja: "相手のマシンを操作する", zh: "操控对方设备", hi: "उनकी मशीन चलाएँ", ar: "قيادة جهازه",
  },
  "desk.counter.kind.app": {
    en: "use a program for them", es: "usar un programa por esa persona",
    fr: "utiliser un programme pour elle", de: "ein Programm für sie bedienen",
    pt: "usar um programa por essa pessoa", it: "usare un programma per suo conto",
    ja: "相手のためにプログラムを使う", zh: "代对方使用程序",
    hi: "उनके लिए कोई प्रोग्राम चलाएँ", ar: "استخدام برنامج نيابة عنه",
  },
  "desk.counter.kind.files": {
    en: "exchange files", es: "intercambiar archivos", fr: "échanger des fichiers",
    de: "Dateien austauschen", pt: "trocar ficheiros", it: "scambiare file",
    ja: "ファイルをやり取りする", zh: "交换文件", hi: "फ़ाइलें बदलें", ar: "تبادل الملفات",
  },
  "desk.mine.head": {
    en: "Your side of the counter", es: "Tu lado del mostrador",
    fr: "Votre côté du comptoir", de: "Deine Seite des Tresens",
    pt: "O seu lado do balcão", it: "Il tuo lato del banco",
    ja: "あなた側のカウンター", zh: "你这一侧的柜台",
    hi: "काउंटर का आपका पक्ष", ar: "جانبك من المكتب",
  },
  "desk.mine.pitch": {
    en: "If a desk has opened a session with you, its offers land here. Nothing they offered is connected until you say yes, the link token comes to you alone, and you can end any link — or the whole session — the moment you want it back.",
    es: "Si un escritorio ha abierto una sesión contigo, sus ofertas llegan aquí. Nada de lo que ofrecieron se conecta hasta que digas que sí, el token del enlace te llega solo a ti, y puedes terminar cualquier enlace — o toda la sesión — en el momento en que quieras recuperarlo.",
    fr: "Si un bureau a ouvert une session avec vous, ses offres arrivent ici. Rien de ce qu'il propose n'est connecté tant que vous ne dites pas oui, le jeton du lien ne parvient qu'à vous, et vous pouvez mettre fin à tout lien — ou à toute la session — dès l'instant où vous voulez le reprendre.",
    de: "Hat ein Desk eine Sitzung mit dir geöffnet, landen seine Angebote hier. Nichts davon ist verbunden, bis du Ja sagst, das Link-Token erhältst nur du, und du kannst jeden Link — oder die ganze Sitzung — in dem Moment beenden, in dem du ihn zurückwillst.",
    pt: "Se uma banca abriu uma sessão consigo, as ofertas chegam aqui. Nada do que ofereceram fica ligado até dizer que sim, o token da ligação chega só a si, e pode terminar qualquer ligação — ou a sessão inteira — no momento em que a quiser de volta.",
    it: "Se una postazione ha aperto una sessione con te, le sue offerte arrivano qui. Nulla di ciò che è stato offerto è connesso finché non dici di sì, il token del collegamento arriva solo a te, e puoi terminare qualsiasi collegamento — o l'intera sessione — nel momento in cui lo rivuoi.",
    ja: "デスクがあなたとのセッションを開くと、その提案はここに届きます。あなたが承諾するまで何も接続されず、リンクトークンはあなただけに届き、どのリンクも — セッション全体も — 取り戻したいと思ったその瞬間に終了できます。",
    zh: "如果某个展台与你开启了会话，其邀请会显示在这里。你说\"是\"之前什么都不会连接，链接令牌只发给你本人，而且你可以在想要收回的那一刻终止任何链接——或整个会话。",
    hi: "यदि किसी डेस्क ने आपके साथ सत्र खोला है, तो उसकी पेशकशें यहाँ आती हैं। जब तक आप हाँ नहीं कहते, कुछ भी नहीं जुड़ता; लिंक टोकन केवल आपको मिलता है, और जिस क्षण आप वापस लेना चाहें, कोई भी लिंक — या पूरा सत्र — समाप्त कर सकते हैं।",
    ar: "إذا فتح مكتب جلسة معك، تصل عروضه هنا. لا يُوصَل شيء مما عرضوه حتى توافق، ورمز الرابط يصلك وحدك، ويمكنك إنهاء أي رابط — أو الجلسة كلها — لحظة أن تريد استرجاعه.",
  },
  "desk.mine.your_id": {
    en: "Your interactor id", es: "Tu id de interactor",
    fr: "Votre identifiant d'interacteur", de: "Deine Interactor-ID",
    pt: "O seu id de interator", it: "Il tuo id interactor",
    ja: "あなたのインタラクターID", zh: "你的互动者 id",
    hi: "आपकी इंटरैक्टर आईडी", ar: "معرّف المتفاعل الخاص بك",
  },
  "desk.mine.your_token": {
    en: "Your interactor token", es: "Tu token de interactor",
    fr: "Votre jeton d'interacteur", de: "Dein Interactor-Token",
    pt: "O seu token de interator", it: "Il tuo token interactor",
    ja: "あなたのインタラクタートークン", zh: "你的互动者令牌",
    hi: "आपका इंटरैक्टर टोकन", ar: "رمز المتفاعل الخاص بك",
  },
  "desk.mine.show": {
    en: "Show my sessions", es: "Mostrar mis sesiones", fr: "Afficher mes sessions",
    de: "Meine Sitzungen zeigen", pt: "Mostrar as minhas sessões", it: "Mostra le mie sessioni",
    ja: "自分のセッションを表示", zh: "显示我的会话", hi: "मेरे सत्र दिखाएँ", ar: "أظهر جلساتي",
  },
  "desk.mine.refresh": {
    en: "Refresh", es: "Actualizar", fr: "Actualiser", de: "Aktualisieren",
    pt: "Atualizar", it: "Aggiorna", ja: "更新", zh: "刷新", hi: "ताज़ा करें", ar: "تحديث",
  },
  "desk.mine.close_all": {
    en: "Close it all", es: "Cerrarlo todo", fr: "Tout fermer", de: "Alles schließen",
    pt: "Fechar tudo", it: "Chiudi tutto", ja: "すべて閉じる", zh: "全部关闭",
    hi: "सब बंद करें", ar: "أغلق كل شيء",
  },
  "desk.mine.connect": {
    en: "Connect it", es: "Conectarlo", fr: "Le connecter", de: "Verbinden",
    pt: "Ligar", it: "Connettilo", ja: "接続する", zh: "连接", hi: "जोड़ें", ar: "وصِّله",
  },
  "desk.mine.no": {
    en: "No", es: "No", fr: "Non", de: "Nein", pt: "Não", it: "No",
    ja: "いいえ", zh: "不", hi: "नहीं", ar: "لا",
  },
  "desk.mine.end_link": {
    en: "End this link", es: "Terminar este enlace", fr: "Mettre fin à ce lien",
    de: "Diesen Link beenden", pt: "Terminar esta ligação", it: "Termina questo collegamento",
    ja: "このリンクを終了", zh: "终止此链接", hi: "यह लिंक समाप्त करें", ar: "أنهِ هذا الرابط",
  },
  "desk.mine.token": {
    en: "Link token (hand it to your own tooling):",
    es: "Token del enlace (entrégalo a tus propias herramientas):",
    fr: "Jeton du lien (à remettre à vos propres outils) :",
    de: "Link-Token (an dein eigenes Werkzeug übergeben):",
    pt: "Token da ligação (entregue-o às suas próprias ferramentas):",
    it: "Token del collegamento (consegnalo ai tuoi strumenti):",
    ja: "リンクトークン（自分のツールに渡してください）：",
    zh: "链接令牌（交给你自己的工具）：",
    hi: "लिंक टोकन (इसे अपने ही टूल को दें):",
    ar: "رمز الرابط (سلّمه إلى أدواتك أنت):",
  },
  "desk.mine.scope": {
    en: "Scope:", es: "Alcance:", fr: "Périmètre :", de: "Umfang:",
    pt: "Âmbito:", it: "Ambito:", ja: "範囲：", zh: "范围：", hi: "दायरा:", ar: "النطاق:",
  },
  "onb.persona": {
    en: "Persona",
    es: "Personalidad",
    fr: "Personnalité",
    de: "Persona",
    pt: "Persona",
    it: "Persona",
    ja: "ペルソナ",
    zh: "人设",
    hi: "व्यक्तित्व",
    ar: "الشخصية",
  },
  "onb.pitch": {
    en: "Create a synthetic profile that thinks, remembers, and evolves with you. It runs against your local QRME API — your data stays in your vault.",
    es: "Crea un perfil sintético que piensa, recuerda y evoluciona contigo. Funciona con tu API local de QRME: tus datos permanecen en tu bóveda.",
    fr: "Créez un profil synthétique qui pense, se souvient et évolue avec vous. Il fonctionne avec votre API QRME locale — vos données restent dans votre coffre.",
    de: "Erstelle ein synthetisches Profil, das denkt, sich erinnert und sich mit dir entwickelt. Es läuft gegen deine lokale QRME-API — deine Daten bleiben in deinem Tresor.",
    pt: "Crie um perfil sintético que pensa, recorda e evolui consigo. Funciona com a sua API QRME local — os seus dados ficam no seu cofre.",
    it: "Crea un profilo sintetico che pensa, ricorda ed evolve con te. Funziona con la tua API QRME locale: i tuoi dati restano nel tuo caveau.",
    ja: "考え、記憶し、あなたとともに成長する合成プロフィールを作成します。ローカルのQRME APIで動作し、データはあなたの保管庫に留まります。",
    zh: "创建一个会思考、会记忆、与你共同成长的合成档案。它运行在你本地的 QRME API 上——你的数据留在你的保险库里。",
    hi: "एक सिंथेटिक प्रोफ़ाइल बनाएँ जो सोचती है, याद रखती है और आपके साथ विकसित होती है। यह आपके स्थानीय QRME API पर चलती है — आपका डेटा आपकी वॉल्ट में रहता है।",
    ar: "أنشئ ملفًا تخليقيًا يفكر ويتذكر ويتطور معك. يعمل عبر واجهة QRME المحلية لديك — وتبقى بياناتك في خزنتك.",
  },
  "onb.oauth.note": {
    en: "A configured provider opens your browser and vouches for your email — no code to type. Grey means this deployment hasn't registered an OAuth client yet (hover for what to set).",
    es: "Un proveedor configurado abre tu navegador y da fe de tu correo: sin códigos que escribir. El gris indica que este despliegue aún no ha registrado un cliente OAuth (pasa el ratón para ver qué configurar).",
    fr: "Un fournisseur configuré ouvre votre navigateur et atteste de votre e-mail — aucun code à saisir. Le gris signifie que ce déploiement n'a pas encore enregistré de client OAuth (survolez pour voir quoi configurer).",
    de: "Ein konfigurierter Anbieter öffnet deinen Browser und bürgt für deine E-Mail — kein Code zum Eintippen. Grau bedeutet, dass diese Installation noch keinen OAuth-Client registriert hat (zum Anzeigen darüberfahren).",
    pt: "Um fornecedor configurado abre o seu navegador e atesta o seu e-mail — sem código para escrever. Cinzento significa que esta implementação ainda não registou um cliente OAuth (passe o rato para ver o que definir).",
    it: "Un provider configurato apre il browser e garantisce per la tua email: nessun codice da digitare. Il grigio indica che questa installazione non ha ancora registrato un client OAuth (passa sopra per sapere cosa impostare).",
    ja: "設定済みのプロバイダがブラウザを開き、あなたのメールアドレスを保証します。コード入力は不要です。グレーはこの環境でOAuthクライアントが未登録であることを示します（設定内容はホバーで確認）。",
    zh: "已配置的提供方会打开你的浏览器并为你的邮箱作证——无需输入验证码。灰色表示此部署尚未注册 OAuth 客户端（悬停查看需要设置的内容）。",
    hi: "कॉन्फ़िगर किया गया प्रदाता आपका ब्राउज़र खोलता है और आपके ईमेल की पुष्टि करता है — कोई कोड टाइप नहीं करना। धूसर का अर्थ है कि इस परिनियोजन ने अभी तक OAuth क्लाइंट पंजीकृत नहीं किया (क्या सेट करना है, देखने के लिए होवर करें)।",
    ar: "يفتح المزوّد المُهيَّأ متصفحك ويشهد على بريدك — دون رمز تكتبه. اللون الرمادي يعني أن هذا النشر لم يسجّل عميل OAuth بعد (مرّر المؤشر لمعرفة ما يجب ضبطه).",
  },
  "onb.birthdate": {
    en: "Owner birthdate (age verification)",
    es: "Fecha de nacimiento del titular (verificación de edad)",
    fr: "Date de naissance du titulaire (vérification de l'âge)",
    de: "Geburtsdatum des Inhabers (Altersprüfung)",
    pt: "Data de nascimento do titular (verificação de idade)",
    it: "Data di nascita del titolare (verifica dell'età)",
    ja: "所有者の生年月日（年齢確認）",
    zh: "所有者出生日期（年龄验证）",
    hi: "स्वामी की जन्म तिथि (आयु सत्यापन)",
    ar: "تاريخ ميلاد المالك (التحقق من العمر)",
  },
  "onb.verify.sent": {
    en: "We emailed a verification link to",
    es: "Enviamos un enlace de verificación a",
    fr: "Nous avons envoyé un lien de vérification à",
    de: "Wir haben einen Bestätigungslink gesendet an",
    pt: "Enviámos um link de verificação para",
    it: "Abbiamo inviato un link di verifica a",
    ja: "確認リンクを次の宛先に送信しました：",
    zh: "我们已将验证链接发送至",
    hi: "हमने सत्यापन लिंक भेजा है",
    ar: "أرسلنا رابط تحقق إلى",
  },
  "onb.verify.click": {
    en: "Click the link and this screen continues on its own.",
    es: "Haz clic en el enlace y esta pantalla continuará sola.",
    fr: "Cliquez sur le lien et cet écran continuera tout seul.",
    de: "Klicke auf den Link, und dieser Bildschirm macht von allein weiter.",
    pt: "Clique no link e este ecrã continua sozinho.",
    it: "Fai clic sul link e questa schermata proseguirà da sola.",
    ja: "リンクをクリックすると、この画面は自動的に進みます。",
    zh: "点击链接后，此页面会自动继续。",
    hi: "लिंक पर क्लिक करें और यह स्क्रीन अपने आप आगे बढ़ जाएगी।",
    ar: "انقر الرابط وستتابع هذه الشاشة من تلقاء نفسها.",
  },
  "onb.verify.type": {
    en: "Prefer typing? Enter the 6-digit code from the same email instead.",
    es: "¿Prefieres escribir? Introduce el código de 6 dígitos del mismo correo.",
    fr: "Vous préférez taper ? Saisissez plutôt le code à 6 chiffres du même e-mail.",
    de: "Lieber tippen? Gib stattdessen den sechsstelligen Code aus derselben E-Mail ein.",
    pt: "Prefere escrever? Introduza antes o código de 6 dígitos do mesmo e-mail.",
    it: "Preferisci digitare? Inserisci invece il codice a 6 cifre della stessa email.",
    ja: "入力の方がよろしいですか？同じメールに記載の6桁のコードを入力してください。",
    zh: "更想手动输入？请改用同一封邮件里的 6 位验证码。",
    hi: "टाइप करना पसंद करेंगे? उसी ईमेल से 6 अंकों का कोड दर्ज करें।",
    ar: "تفضّل الكتابة؟ أدخل الرمز المكوّن من ٦ أرقام من الرسالة نفسها.",
  },
  "onb.reset.hint": {
    en: "Enter your account's email; we'll send a 6-digit reset code",
    es: "Introduce el correo de tu cuenta; enviaremos un código de 6 dígitos",
    fr: "Saisissez l'e-mail de votre compte ; nous enverrons un code à 6 chiffres",
    de: "Gib die E-Mail deines Kontos ein; wir senden einen sechsstelligen Code",
    pt: "Introduza o e-mail da sua conta; enviaremos um código de 6 dígitos",
    it: "Inserisci l'email del tuo account; invieremo un codice a 6 cifre",
    ja: "アカウントのメールアドレスを入力してください。6桁のリセットコードを送信します",
    zh: "请输入账户邮箱，我们会发送 6 位重置码",
    hi: "अपने खाते का ईमेल दर्ज करें; हम 6 अंकों का रीसेट कोड भेजेंगे",
    ar: "أدخل بريد حسابك؛ سنرسل رمز إعادة تعيين من ٦ أرقام",
  },
  "onb.signedin": {
    en: "Signed in as",
    es: "Sesión iniciada como",
    fr: "Connecté en tant que",
    de: "Angemeldet als",
    pt: "Sessão iniciada como",
    it: "Accesso effettuato come",
    ja: "サインイン中：",
    zh: "已登录为",
    hi: "इस रूप में साइन इन",
    ar: "تم تسجيل الدخول باسم",
  },
  "onb.undercount": {
    en: "— your profile is created under this account.",
    es: "— tu perfil se crea bajo esta cuenta.",
    fr: "— votre profil est créé sous ce compte.",
    de: "— dein Profil wird unter diesem Konto angelegt.",
    pt: "— o seu perfil é criado sob esta conta.",
    it: "— il tuo profilo viene creato sotto questo account.",
    ja: "— プロフィールはこのアカウントの下に作成されます。",
    zh: "——你的档案将创建在此账户下。",
    hi: "— आपकी प्रोफ़ाइल इसी खाते के अंतर्गत बनेगी।",
    ar: "— يُنشأ ملفك ضمن هذا الحساب.",
  },
  "onb.nomail": {
    en: "— this deployment has no mail service configured, so the code was",
    es: "— este despliegue no tiene servicio de correo configurado, así que el código se",
    fr: "— ce déploiement n'a pas de service de messagerie configuré, le code a donc été",
    de: "— diese Installation hat keinen Mailversand konfiguriert, der Code wurde daher",
    pt: "— esta implementação não tem serviço de e-mail configurado, por isso o código foi",
    it: "— questa installazione non ha un servizio di posta configurato, quindi il codice è stato",
    ja: "— この環境ではメール送信が設定されていないため、コードは",
    zh: "——此部署未配置邮件服务，因此验证码已",
    hi: "— इस परिनियोजन में मेल सेवा कॉन्फ़िगर नहीं है, इसलिए कोड",
    ar: "— لم يُضبط في هذا النشر خدمة بريد، لذا فإن الرمز",
  },
  "onb.nomail.log": {
    en: "written to the app's backend log",
    es: "escribió en el registro del backend de la app",
    fr: "écrit dans le journal du backend de l'application",
    de: "ins Backend-Log der App geschrieben",
    pt: "escrito no registo do backend da aplicação",
    it: "scritto nel log del backend dell'app",
    ja: "アプリのバックエンドログに記録されました",
    zh: "写入了应用后端日志",
    hi: "ऐप के बैकएंड लॉग में लिखा गया",
    ar: "كُتب في سجل الخلفية للتطبيق",
  },
  "onb.nomail.terminal": {
    en: "printed in the terminal running the backend",
    es: "imprimió en la terminal que ejecuta el backend",
    fr: "affiché dans le terminal exécutant le backend",
    de: "im Terminal ausgegeben, das das Backend ausführt",
    pt: "impresso no terminal que executa o backend",
    it: "stampato nel terminale che esegue il backend",
    ja: "バックエンドを実行しているターミナルに出力されました",
    zh: "打印在运行后端的终端中",
    hi: "बैकएंड चला रहे टर्मिनल में प्रिंट किया गया",
    ar: "طُبع في الطرفية التي تشغّل الخلفية",
  },
  "onb.nomail.open": {
    en: "(button below opens it)",
    es: "(el botón de abajo lo abre)",
    fr: "(le bouton ci-dessous l'ouvre)",
    de: "(die Schaltfläche unten öffnet es)",
    pt: "(o botão abaixo abre-o)",
    it: "(il pulsante sotto lo apre)",
    ja: "（下のボタンで開けます）",
    zh: "（下方按钮可打开）",
    hi: "(नीचे का बटन इसे खोलता है)",
    ar: "(الزر أدناه يفتحه)",
  },
  "onb.oauth.absent": {
    en: "· not configured here",
    es: "· no configurado aquí",
    fr: "· non configuré ici",
    de: "· hier nicht konfiguriert",
    pt: "· não configurado aqui",
    it: "· non configurato qui",
    ja: "・この環境では未設定",
    zh: "· 此处未配置",
    hi: "· यहाँ कॉन्फ़िगर नहीं",
    ar: "· غير مُهيَّأ هنا",
  },
  "pub.state.open": {
    en: "open",
    es: "abierta",
    fr: "ouverte",
    de: "offen",
    pt: "aberta",
    it: "aperta",
    ja: "審査中",
    zh: "处理中",
    hi: "खुली",
    ar: "مفتوح",
  },
  "pub.state.upheld": {
    en: "upheld",
    es: "estimada",
    fr: "retenue",
    de: "stattgegeben",
    pt: "deferida",
    it: "accolta",
    ja: "認容",
    zh: "已支持",
    hi: "स्वीकृत",
    ar: "مقبول",
  },
  "pub.state.dismissed": {
    en: "dismissed",
    es: "desestimada",
    fr: "rejetée",
    de: "abgewiesen",
    pt: "indeferida",
    it: "respinta",
    ja: "棄却",
    zh: "已驳回",
    hi: "खारिज",
    ar: "مرفوض",
  },
  "asst.title": {
    en: "What it can do for you", es: "Lo que puede hacer por ti", fr: "Ce qu'il peut faire pour vous", de: "Was es für Sie tun kann", pt: "O que pode fazer por si", it: "Cosa può fare per te", ja: "あなたのためにできること", zh: "它能为你做什么", hi: "यह आपके लिए क्या कर सकता है", ar: "ما يمكنه فعله من أجلك",
  },
  "asst.lead": {
    en: "Sort a pile, fix a draft, make something worth keeping — and every generated thing carries a mark you can check.", es: "Ordena un montón, arregla un borrador, crea algo que valga la pena guardar — y todo lo generado lleva una marca que puedes comprobar.", fr: "Triez une pile, corrigez un brouillon, créez quelque chose à garder — et tout ce qui est généré porte une marque vérifiable.", de: "Einen Stapel sortieren, einen Entwurf verbessern, etwas Bleibendes schaffen — und alles Generierte trägt ein prüfbares Zeichen.", pt: "Ordene uma pilha, corrija um rascunho, crie algo que valha a pena guardar — e tudo o que é gerado traz uma marca verificável.", it: "Ordina una pila, sistema una bozza, crea qualcosa da tenere — e ogni cosa generata porta un marchio verificabile.", ja: "山を仕分け、下書きを直し、残す価値のあるものを作る — 生成されたものには必ず確認できるマークが付きます。", zh: "整理一堆、修改草稿、创作值得保留的东西 — 每件生成物都带有可核验的标记。", hi: "ढेर छाँटें, मसौदा सुधारें, रखने लायक कुछ बनाएँ — और हर जनित चीज़ पर जाँचने योग्य चिह्न होता है।", ar: "رتّب كومة، أصلح مسودة، اصنع شيئًا يستحق الحفظ — وكل ما يُولَّد يحمل علامة يمكنك التحقق منها.",
  },
  "asst.pile": {
    en: "Sort a pile", es: "Ordenar un montón", fr: "Trier une pile", de: "Einen Stapel sortieren", pt: "Ordenar uma pilha", it: "Ordina una pila", ja: "山を仕分ける", zh: "整理一堆", hi: "ढेर छाँटें", ar: "ترتيب كومة",
  },
  "asst.pile.lead": {
    en: "One item per line. You get back the best few with the reason each one survived — the ranking is meant to be arguable.", es: "Un elemento por línea. Recibes los mejores con la razón por la que cada uno sobrevivió — la clasificación está hecha para ser discutible.", fr: "Un élément par ligne. Vous recevez les meilleurs avec la raison pour laquelle chacun a survécu — le classement est fait pour être discutable.", de: "Ein Eintrag pro Zeile. Sie erhalten die besten zurück, mit dem Grund, warum jeder bestand — die Rangfolge soll anfechtbar sein.", pt: "Um item por linha. Recebe os melhores com a razão pela qual cada um sobreviveu — a classificação foi feita para ser discutível.", it: "Un elemento per riga. Ricevi i migliori con il motivo per cui ciascuno è sopravvissuto — la classifica è fatta per essere discutibile.", ja: "1行に1項目。最良のものが、それぞれが残った理由と共に返ります — 順位は議論できるように作られています。", zh: "每行一项。你会收到最好的几项及各自留下的理由 — 排名本就可以商榷。", hi: "प्रति पंक्ति एक आइटम। सर्वश्रेष्ठ कुछ, हर एक के बचने के कारण सहित मिलते हैं — रैंकिंग बहस योग्य होने के लिए ही है।", ar: "عنصر واحد في كل سطر. تستعيد الأفضل مع سبب بقاء كل منها — الترتيب مصمم ليكون قابلاً للنقاش.",
  },
  "asst.pile.ph": {
    en: "one candidate per line", es: "un candidato por línea", fr: "un candidat par ligne", de: "ein Kandidat pro Zeile", pt: "um candidato por linha", it: "un candidato per riga", ja: "1行に1候補", zh: "每行一个候选", hi: "प्रति पंक्ति एक उम्मीदवार", ar: "مرشح واحد في كل سطر",
  },
  "asst.pile.best": {
    en: "what best means to you", es: "qué significa mejor para ti", fr: "ce que « meilleur » veut dire pour vous", de: "was „am besten“ für Sie heißt", pt: "o que melhor significa para si", it: "cosa significa migliore per te", ja: "あなたにとっての「最良」とは", zh: "对你来说什么算最好", hi: "आपके लिए सर्वश्रेष्ठ का क्या अर्थ है", ar: "ما معنى الأفضل بالنسبة لك",
  },
  "asst.pile.go": {
    en: "Sort it", es: "Ordenarlo", fr: "Trier", de: "Sortieren", pt: "Ordenar", it: "Ordina", ja: "仕分ける", zh: "整理", hi: "छाँटें", ar: "رتّب",
  },
  "asst.tally": {
    en: "{reviewed} looked at, {kept} kept.", es: "{reviewed} revisados, {kept} conservados.", fr: "{reviewed} examinés, {kept} conservés.", de: "{reviewed} gesichtet, {kept} behalten.", pt: "{reviewed} analisados, {kept} mantidos.", it: "{reviewed} esaminati, {kept} tenuti.", ja: "{reviewed}件を確認し、{kept}件を残しました。", zh: "查看了{reviewed}项，保留了{kept}项。", hi: "{reviewed} देखे गए, {kept} रखे गए।", ar: "تمت مراجعة {reviewed}، واحتُفظ بـ {kept}.",
  },
  "asst.aside": {
    en: "Set aside: {n}.", es: "Apartados: {n}.", fr: "Mis de côté : {n}.", de: "Beiseitegelegt: {n}.", pt: "Postos de lado: {n}.", it: "Messi da parte: {n}.", ja: "保留: {n}件。", zh: "搁置：{n}项。", hi: "अलग रखे: {n}।", ar: "وُضع جانبًا: {n}.",
  },
  "asst.fix": {
    en: "Fix a draft", es: "Arreglar un borrador", fr: "Corriger un brouillon", de: "Einen Entwurf verbessern", pt: "Corrigir um rascunho", it: "Sistema una bozza", ja: "下書きを直す", zh: "修改草稿", hi: "मसौदा सुधारें", ar: "إصلاح مسودة",
  },
  "asst.fix.ph": {
    en: "paste something you wrote", es: "pega algo que escribiste", fr: "collez quelque chose que vous avez écrit", de: "fügen Sie etwas Eigenes ein", pt: "cole algo que escreveu", it: "incolla qualcosa che hai scritto", ja: "自分で書いたものを貼り付け", zh: "粘贴你写的内容", hi: "अपना लिखा कुछ चिपकाएँ", ar: "الصق شيئًا كتبته",
  },
  "asst.fix.go": {
    en: "Proofread", es: "Corregir", fr: "Relire", de: "Korrekturlesen", pt: "Rever", it: "Correggi", ja: "校正する", zh: "校对", hi: "प्रूफ़रीड करें", ar: "تدقيق",
  },
  "asst.make": {
    en: "Make something to keep", es: "Crear algo para guardar", fr: "Créer quelque chose à garder", de: "Etwas Bleibendes schaffen", pt: "Criar algo para guardar", it: "Crea qualcosa da tenere", ja: "残すものを作る", zh: "创作可保留之物", hi: "रखने लायक कुछ बनाएँ", ar: "اصنع شيئًا للاحتفاظ به",
  },
  "asst.make.ph": {
    en: "the moment to capture", es: "el momento a capturar", fr: "le moment à capturer", de: "der festzuhaltende Moment", pt: "o momento a capturar", it: "il momento da catturare", ja: "残したい瞬間", zh: "要记录的时刻", hi: "जो पल सहेजना है", ar: "اللحظة المراد التقاطها",
  },
  "asst.make.go": {
    en: "Compose", es: "Componer", fr: "Composer", de: "Verfassen", pt: "Compor", it: "Componi", ja: "作る", zh: "创作", hi: "रचें", ar: "تأليف",
  },
  "asst.make.none": {
    en: "Nothing kept yet.", es: "Nada guardado todavía.", fr: "Rien de gardé pour l'instant.", de: "Noch nichts aufbewahrt.", pt: "Ainda nada guardado.", it: "Ancora niente da tenere.", ja: "まだ何も残していません。", zh: "尚未保留任何内容。", hi: "अभी कुछ नहीं रखा गया।", ar: "لا شيء محفوظ بعد.",
  },
  "asst.make.check": {
    en: "check this mark", es: "comprobar esta marca", fr: "vérifier cette marque", de: "dieses Zeichen prüfen", pt: "verificar esta marca", it: "verifica questo marchio", ja: "このマークを確認", zh: "核验此标记", hi: "यह चिह्न जाँचें", ar: "تحقق من هذه العلامة",
  },
  "asst.mark": {
    en: "Check a mark", es: "Comprobar una marca", fr: "Vérifier une marque", de: "Ein Zeichen prüfen", pt: "Verificar uma marca", it: "Verifica un marchio", ja: "マークを確認", zh: "核验标记", hi: "चिह्न जाँचें", ar: "التحقق من علامة",
  },
  "asst.mark.lead": {
    en: "Two questions, and they are not the same one: was this credential issued here, and is this the content it was issued for.", es: "Dos preguntas, y no son la misma: ¿se emitió aquí esta credencial, y es este el contenido para el que se emitió?", fr: "Deux questions, et ce ne sont pas les mêmes : cette référence a-t-elle été émise ici, et est-ce le contenu pour lequel elle a été émise ?", de: "Zwei Fragen, und es sind nicht dieselben: Wurde dieser Nachweis hier ausgestellt, und ist dies der Inhalt, für den er ausgestellt wurde?", pt: "Duas perguntas, e não são a mesma: esta credencial foi emitida aqui, e é este o conteúdo para o qual foi emitida?", it: "Due domande, e non sono la stessa: questa credenziale è stata emessa qui, ed è questo il contenuto per cui è stata emessa?", ja: "二つの問いは同じではありません：この資格情報はここで発行されたのか、そしてこれは発行対象の内容なのか。", zh: "两个问题，并不相同：此凭证是否在这里签发，以及这是否是它签发时对应的内容。", hi: "दो प्रश्न, और वे एक नहीं हैं: क्या यह क्रेडेंशियल यहाँ जारी हुआ, और क्या यही वह सामग्री है जिसके लिए जारी हुआ।", ar: "سؤالان وليسا واحدًا: هل صدر هذا الاعتماد هنا، وهل هذا هو المحتوى الذي صدر من أجله.",
  },
  "asst.mark.id": {
    en: "a watermark id", es: "un id de marca de agua", fr: "un id de filigrane", de: "eine Wasserzeichen-Id", pt: "um id de marca de água", it: "un id di filigrana", ja: "ウォーターマークID", zh: "水印ID", hi: "वॉटरमार्क आईडी", ar: "معرّف علامة مائية",
  },
  "asst.mark.content": {
    en: "the content to check against it", es: "el contenido a comprobar contra ella", fr: "le contenu à vérifier avec", de: "der dagegen zu prüfende Inhalt", pt: "o conteúdo a verificar contra ela", it: "il contenuto da verificare", ja: "照合する内容", zh: "用于核对的内容", hi: "जिससे मिलान करना है वह सामग्री", ar: "المحتوى المراد فحصه",
  },
  "asst.mark.go": {
    en: "Check it", es: "Comprobar", fr: "Vérifier", de: "Prüfen", pt: "Verificar", it: "Verifica", ja: "確認する", zh: "核验", hi: "जाँचें", ar: "تحقق",
  },
  "asst.mark.issued": {
    en: "issued {date} for a {kind}", es: "emitida el {date} para un {kind}", fr: "émise le {date} pour un {kind}", de: "ausgestellt am {date} für {kind}", pt: "emitida em {date} para {kind}", it: "emessa il {date} per {kind}", ja: "{date}に{kind}向けに発行", zh: "{date}为{kind}签发", hi: "{date} को {kind} के लिए जारी", ar: "صدرت في {date} لـ {kind}",
  },
  "asst.mark.match": {
    en: "This is the content the credential was issued for.", es: "Este es el contenido para el que se emitió la credencial.", fr: "C'est le contenu pour lequel la référence a été émise.", de: "Dies ist der Inhalt, für den der Nachweis ausgestellt wurde.", pt: "Este é o conteúdo para o qual a credencial foi emitida.", it: "Questo è il contenuto per cui la credenziale è stata emessa.", ja: "これは資格情報の発行対象の内容です。", zh: "这是凭证签发时对应的内容。", hi: "यही वह सामग्री है जिसके लिए क्रेडेंशियल जारी हुआ।", ar: "هذا هو المحتوى الذي صدر الاعتماد من أجله.",
  },
  "asst.worn": {
    en: "What it is worn on", es: "En qué se lleva", fr: "Sur quoi il se porte", de: "Worauf es getragen wird", pt: "Onde é usado", it: "Su cosa si indossa", ja: "身につける場所", zh: "佩戴之处", hi: "किस पर पहना जाता है", ar: "على ماذا يُرتدى",
  },
  "asst.worn.revoked": {
    en: "include ones you have unpaired — the row stays, with the date", es: "incluir los que has desemparejado — la fila permanece, con la fecha", fr: "inclure ceux que vous avez désappairés — la ligne reste, avec la date", de: "auch entkoppelte zeigen — die Zeile bleibt, mit Datum", pt: "incluir os que desemparelhou — a linha fica, com a data", it: "includi quelli disaccoppiati — la riga resta, con la data", ja: "解除したものも表示 — 行は日付と共に残ります", zh: "包括已取消配对的 — 记录保留，附日期", hi: "अलग किए गए भी दिखाएँ — पंक्ति तिथि सहित रहती है", ar: "تضمين ما ألغيت إقرانه — يبقى الصف مع التاريخ",
  },
  "asst.worn.none": {
    en: "Nothing paired.", es: "Nada emparejado.", fr: "Rien d'appairé.", de: "Nichts gekoppelt.", pt: "Nada emparelhado.", it: "Niente di accoppiato.", ja: "ペアリングなし。", zh: "未配对任何设备。", hi: "कुछ नहीं जुड़ा।", ar: "لا شيء مقترن.",
  },
  "asst.worn.over": {
    en: "{kind} over {transport}", es: "{kind} por {transport}", fr: "{kind} via {transport}", de: "{kind} über {transport}", pt: "{kind} por {transport}", it: "{kind} via {transport}", ja: "{kind}（{transport}経由）", zh: "{kind}（经{transport}）", hi: "{kind}, {transport} से", ar: "{kind} عبر {transport}",
  },
  "asst.worn.showing": {
    en: "showing {faces}", es: "mostrando {faces}", fr: "affiche {faces}", de: "zeigt {faces}", pt: "a mostrar {faces}", it: "mostra {faces}", ja: "{faces}を表示中", zh: "显示{faces}", hi: "{faces} दिखा रहा है", ar: "يعرض {faces}",
  },
  "asst.worn.unpair": {
    en: "unpair", es: "desemparejar", fr: "désappairer", de: "entkoppeln", pt: "desemparelhar", it: "disaccoppia", ja: "解除", zh: "取消配对", hi: "अलग करें", ar: "إلغاء الإقران",
  },
  "asst.worn.unpaired": {
    en: "unpaired", es: "desemparejado", fr: "désappairé", de: "entkoppelt", pt: "desemparelhado", it: "disaccoppiato", ja: "解除済み", zh: "已取消配对", hi: "अलग किया गया", ar: "غير مقترن",
  },
  "asst.worn.name": {
    en: "what you call it", es: "cómo lo llamas", fr: "comment vous l'appelez", de: "wie Sie es nennen", pt: "como lhe chama", it: "come lo chiami", ja: "呼び名", zh: "你怎么称呼它", hi: "आप इसे क्या कहते हैं", ar: "ماذا تسميه",
  },
  "asst.worn.pair": {
    en: "Pair", es: "Emparejar", fr: "Appairer", de: "Koppeln", pt: "Emparelhar", it: "Accoppia", ja: "ペアリング", zh: "配对", hi: "जोड़ें", ar: "إقران",
  },
  "asst.worn.refused": {
    en: "What will not be paired", es: "Lo que no se emparejará", fr: "Ce qui ne sera pas appairé", de: "Was nicht gekoppelt wird", pt: "O que não será emparelhado", it: "Cosa non sarà accoppiato", ja: "ペアリングされないもの", zh: "不会被配对的设备", hi: "जो नहीं जोड़ा जाएगा", ar: "ما لن يُقرن",
  },
  "asst.said": {
    en: "What people said", es: "Lo que dijo la gente", fr: "Ce que les gens ont dit", de: "Was die Leute sagten", pt: "O que as pessoas disseram", it: "Cosa ha detto la gente", ja: "人々の声", zh: "人们的评价", hi: "लोगों ने क्या कहा", ar: "ما قاله الناس",
  },
  "asst.said.from": {
    en: "{avg} from {count} reviews", es: "{avg} de {count} reseñas", fr: "{avg} sur {count} avis", de: "{avg} aus {count} Bewertungen", pt: "{avg} de {count} avaliações", it: "{avg} da {count} recensioni", ja: "{count}件のレビューで{avg}", zh: "{count}条评价，平均{avg}", hi: "{count} समीक्षाओं से {avg}", ar: "{avg} من {count} مراجعة",
  },
  "asst.said.edited": {
    en: "edited", es: "editada", fr: "modifié", de: "bearbeitet", pt: "editada", it: "modificata", ja: "編集済み", zh: "已编辑", hi: "संपादित", ar: "معدَّلة",
  },
  "asst.said.ph": {
    en: "what you thought", es: "lo que pensaste", fr: "ce que vous en avez pensé", de: "was Sie dachten", pt: "o que achou", it: "cosa ne pensi", ja: "感想", zh: "你的想法", hi: "आपकी राय", ar: "ما رأيك",
  },
  "asst.said.leave": {
    en: "Leave a review", es: "Dejar una reseña", fr: "Laisser un avis", de: "Bewertung abgeben", pt: "Deixar avaliação", it: "Lascia una recensione", ja: "レビューを書く", zh: "留下评价", hi: "समीक्षा दें", ar: "اترك مراجعة",
  },
  "asst.said.rule": {
    en: "A review comes from somebody who actually talked to it — one per person, edited rather than stacked.", es: "Una reseña viene de alguien que realmente habló con él — una por persona, editada en vez de acumulada.", fr: "Un avis vient de quelqu'un qui lui a réellement parlé — un par personne, modifié plutôt qu'empilé.", de: "Eine Bewertung kommt von jemandem, der wirklich mit ihm sprach — eine pro Person, bearbeitet statt gestapelt.", pt: "Uma avaliação vem de alguém que realmente falou com ele — uma por pessoa, editada em vez de acumulada.", it: "Una recensione viene da chi ci ha davvero parlato — una a persona, modificata invece che accumulata.", ja: "レビューは実際に話した人からのもの — 一人一件、積み重ねではなく編集式です。", zh: "评价来自真正与之交谈过的人 — 每人一条，编辑而非叠加。", hi: "समीक्षा उसी से आती है जिसने वाकई बात की — प्रति व्यक्ति एक, जमा नहीं, संपादित।", ar: "المراجعة تأتي ممن تحدث إليه فعلاً — واحدة لكل شخص، تُعدَّل ولا تتكدس.",
  },
  "asst.you": {
    en: "Something you said", es: "Algo que dijiste", fr: "Quelque chose que vous avez dit", de: "Etwas, das Sie sagten", pt: "Algo que disse", it: "Qualcosa che hai detto", ja: "あなたの発言", zh: "你说过的话", hi: "आपने जो कहा", ar: "شيء قلته",
  },
  "asst.you.lead": {
    en: "You can correct or retract your own turn. The correction carries forward: the next reply reasons from what you meant.", es: "Puedes corregir o retirar tu propio turno. La corrección se propaga: la siguiente respuesta razona desde lo que quisiste decir.", fr: "Vous pouvez corriger ou retirer votre propre tour. La correction se propage : la réponse suivante raisonne à partir de ce que vous vouliez dire.", de: "Sie können Ihren eigenen Beitrag korrigieren oder zurücknehmen. Die Korrektur wirkt weiter: die nächste Antwort geht von dem aus, was Sie meinten.", pt: "Pode corrigir ou retirar a sua própria vez. A correção propaga-se: a próxima resposta raciocina a partir do que quis dizer.", it: "Puoi correggere o ritirare il tuo turno. La correzione si propaga: la risposta successiva ragiona da ciò che intendevi.", ja: "自分の発言は修正も撤回もできます。修正は引き継がれ、次の返答はあなたの意図から推論します。", zh: "你可以更正或撤回自己的发言。更正会延续：下一条回复将依据你的本意。", hi: "आप अपनी बारी सुधार या वापस ले सकते हैं। सुधार आगे बढ़ता है: अगला जवाब आपके आशय से तर्क करता है।", ar: "يمكنك تصحيح دورك أو سحبه. التصحيح يستمر: الرد التالي يستدل مما قصدته.",
  },
  "asst.you.times": {
    en: "edited {n} times", es: "editado {n} veces", fr: "modifié {n} fois", de: "{n}-mal bearbeitet", pt: "editado {n} vezes", it: "modificato {n} volte", ja: "{n}回編集", zh: "编辑{n}次", hi: "{n} बार संपादित", ar: "عُدّل {n} مرات",
  },
  "asst.you.stale": {
    en: "↑ written before the message above it was changed, so it answers the older wording.", es: "↑ escrito antes de que se cambiara el mensaje de arriba, así que responde a la redacción anterior.", fr: "↑ écrit avant la modification du message au-dessus, il répond donc à l'ancienne formulation.", de: "↑ geschrieben, bevor die Nachricht darüber geändert wurde — es beantwortet also den älteren Wortlaut.", pt: "↑ escrito antes de a mensagem acima ser alterada, por isso responde à redação anterior.", it: "↑ scritto prima che il messaggio sopra fosse cambiato, quindi risponde alla formulazione precedente.", ja: "↑ 上のメッセージが変更される前に書かれたため、以前の文面への返答です。", zh: "↑ 写于上方消息修改之前，因此回应的是旧的措辞。", hi: "↑ ऊपर का संदेश बदलने से पहले लिखा गया, इसलिए यह पुराने शब्दों का उत्तर है।", ar: "↑ كُتب قبل تغيير الرسالة أعلاه، فهو يجيب على الصياغة الأقدم.",
  },
  "asst.you.save": {
    en: "Save", es: "Guardar", fr: "Enregistrer", de: "Speichern", pt: "Guardar", it: "Salva", ja: "保存", zh: "保存", hi: "सहेजें", ar: "حفظ",
  },
  "asst.you.cancel": {
    en: "Cancel", es: "Cancelar", fr: "Annuler", de: "Abbrechen", pt: "Cancelar", it: "Annulla", ja: "キャンセル", zh: "取消", hi: "रद्द करें", ar: "إلغاء",
  },
  "asst.you.correct": {
    en: "correct it", es: "corregirlo", fr: "le corriger", de: "korrigieren", pt: "corrigir", it: "correggilo", ja: "修正する", zh: "更正", hi: "सुधारें", ar: "صحّحه",
  },
  "asst.you.retract": {
    en: "take it back", es: "retirarlo", fr: "le retirer", de: "zurücknehmen", pt: "retirar", it: "ritiralo", ja: "取り消す", zh: "撤回", hi: "वापस लें", ar: "استرجعه",
  },
  "asst.media": {
    en: "Add a photo or a document", es: "Añadir una foto o un documento", fr: "Ajouter une photo ou un document", de: "Foto oder Dokument hinzufügen", pt: "Adicionar uma foto ou documento", it: "Aggiungi una foto o un documento", ja: "写真や書類を追加", zh: "添加照片或文档", hi: "फ़ोटो या दस्तावेज़ जोड़ें", ar: "أضف صورة أو مستندًا",
  },
  "asst.media.lead": {
    en: "The kind is read from the bytes rather than the file name, and nothing you took yourself is AI-marked.", es: "El tipo se lee de los bytes y no del nombre del archivo, y nada que hayas tomado tú lleva la marca de IA.", fr: "Le type est lu dans les octets et non dans le nom du fichier, et rien de ce que vous avez pris vous-même n'est marqué IA.", de: "Die Art wird aus den Bytes gelesen, nicht aus dem Dateinamen, und nichts Selbstaufgenommenes trägt das KI-Zeichen.", pt: "O tipo é lido dos bytes e não do nome do ficheiro, e nada que tenha captado tem marca de IA.", it: "Il tipo si legge dai byte e non dal nome del file, e nulla di ciò che hai scattato tu porta il marchio IA.", ja: "種類はファイル名ではなくバイト列から読み取られ、自分で撮ったものにAIマークは付きません。", zh: "类型从字节读取而非文件名，你自己拍摄的内容不会带AI标记。", hi: "प्रकार फ़ाइल नाम से नहीं, बाइट्स से पढ़ा जाता है, और आपकी खुद की ली गई चीज़ों पर AI-चिह्न नहीं होता।", ar: "يُقرأ النوع من البايتات لا من اسم الملف، وما التقطته بنفسك لا يحمل علامة الذكاء الاصطناعي.",
  },
  "asst.media.bytes": {
    en: "{name} — {n} bytes", es: "{name} — {n} bytes", fr: "{name} — {n} octets", de: "{name} — {n} Bytes", pt: "{name} — {n} bytes", it: "{name} — {n} byte", ja: "{name} — {n}バイト", zh: "{name} — {n}字节", hi: "{name} — {n} बाइट", ar: "{name} — {n} بايت",
  },
  "asst.media.open": {
    en: "open", es: "abrir", fr: "ouvrir", de: "öffnen", pt: "abrir", it: "apri", ja: "開く", zh: "打开", hi: "खोलें", ar: "افتح",
  },
  "set.title": {
    en: "Control Center", es: "Centro de control", fr: "Centre de contrôle", de: "Kontrollzentrum", pt: "Centro de controlo", it: "Centro di controllo", ja: "コントロールセンター", zh: "控制中心", hi: "कंट्रोल सेंटर", ar: "مركز التحكم",
  },
  "set.tag": {
    en: "you are in control", es: "tú tienes el control", fr: "vous avez le contrôle", de: "Sie haben die Kontrolle", pt: "você está no controlo", it: "sei tu al comando", ja: "主導権はあなたに", zh: "一切由你掌控", hi: "नियंत्रण आपके हाथ में", ar: "أنت المتحكم",
  },
  "set.api": {
    en: "API connection — where this app's own server lives", es: "Conexión API — dónde vive el servidor de esta app", fr: "Connexion API — où vit le serveur de cette app", de: "API-Verbindung — wo der Server dieser App lebt", pt: "Ligação API — onde vive o servidor desta app", it: "Connessione API — dove vive il server di questa app", ja: "API接続 — このアプリのサーバーの場所", zh: "API连接 — 本应用服务器所在之处", hi: "API कनेक्शन — इस ऐप का सर्वर कहाँ है", ar: "اتصال API — أين يعيش خادم هذا التطبيق",
  },
  "set.api.lead": {
    en: "This is the address of the QRME backend this console talks to (the desktop app starts its own; a phone points here over Wi-Fi). It is an address, not a secret — and it is not the model API key below: the two are different things.", es: "Esta es la dirección del backend de QRME con el que habla esta consola (la app de escritorio arranca el suyo; un teléfono apunta aquí por Wi-Fi). Es una dirección, no un secreto — y no es la clave API del modelo de abajo: son dos cosas distintas.", fr: "C'est l'adresse du backend QRME auquel cette console parle (l'app de bureau démarre le sien ; un téléphone pointe ici par Wi-Fi). C'est une adresse, pas un secret — et ce n'est pas la clé API du modèle ci-dessous : ce sont deux choses différentes.", de: "Dies ist die Adresse des QRME-Backends, mit dem diese Konsole spricht (die Desktop-App startet ihr eigenes; ein Telefon zeigt per WLAN hierher). Es ist eine Adresse, kein Geheimnis — und nicht der Modell-API-Schlüssel unten: das sind zwei verschiedene Dinge.", pt: "Este é o endereço do backend QRME com que esta consola fala (a app de desktop arranca o seu; um telemóvel aponta aqui por Wi-Fi). É um endereço, não um segredo — e não é a chave API do modelo abaixo: são coisas diferentes.", it: "Questo è l'indirizzo del backend QRME con cui parla questa console (l'app desktop avvia il suo; un telefono punta qui via Wi-Fi). È un indirizzo, non un segreto — e non è la chiave API del modello qui sotto: sono due cose diverse.", ja: "これはこのコンソールが話すQRMEバックエンドのアドレスです（デスクトップアプリは自前で起動し、スマホはWi-Fi経由でここを指します）。これはアドレスであり秘密ではなく、下のモデルAPIキーとも別物です。", zh: "这是本控制台连接的QRME后端地址（桌面应用自行启动；手机通过Wi-Fi指向这里）。它是地址而非机密 — 也不是下方的模型API密钥：两者是不同的东西。", hi: "यह उस QRME बैकएंड का पता है जिससे यह कंसोल बात करती है (डेस्कटॉप ऐप अपना खुद चलाता है; फ़ोन Wi-Fi से यहाँ इंगित करता है)। यह पता है, रहस्य नहीं — और नीचे वाली मॉडल API कुंजी नहीं है: दोनों अलग चीज़ें हैं।", ar: "هذا عنوان خادم QRME الذي تتحدث إليه هذه الوحدة (تطبيق سطح المكتب يشغّل خادمه؛ والهاتف يشير هنا عبر Wi-Fi). إنه عنوان لا سر — وليس مفتاح API النموذج أدناه: هما شيئان مختلفان.",
  },
  "set.api.url": {
    en: "Backend base URL", es: "URL base del backend", fr: "URL de base du backend", de: "Backend-Basis-URL", pt: "URL base do backend", it: "URL base del backend", ja: "バックエンドのベースURL", zh: "后端基础URL", hi: "बैकएंड बेस URL", ar: "عنوان URL الأساسي للخادم",
  },
  "set.key": {
    en: "Your model API key — who pays for the AI's words", es: "Tu clave API del modelo — quién paga las palabras de la IA", fr: "Votre clé API du modèle — qui paie les mots de l'IA", de: "Ihr Modell-API-Schlüssel — wer für die Worte der KI zahlt", pt: "A sua chave API do modelo — quem paga as palavras da IA", it: "La tua chiave API del modello — chi paga le parole dell'IA", ja: "モデルAPIキー — AIの言葉の支払いは誰か", zh: "你的模型API密钥 — 谁为AI的话语付费", hi: "आपकी मॉडल API कुंजी — AI के शब्दों का भुगतान कौन करता है", ar: "مفتاح API النموذج الخاص بك — من يدفع ثمن كلمات الذكاء الاصطناعي",
  },
  "set.key.lead": {
    en: "Different from the connection above: that was where this app's server lives; this is whose credential the AI generation runs on. Paste your own key (Anthropic sk-ant-…, or OpenAI / xAI / Gemini for those providers) and your profiles' replies run on your credential. It is a secret: it stays on this device and rides only your own requests — the server never stores it. Leave it empty to use whatever key the deployment lends.", es: "Distinto de la conexión de arriba: aquello era dónde vive el servidor de esta app; esto es con qué credencial corre la generación de IA. Pega tu propia clave (Anthropic sk-ant-…, u OpenAI / xAI / Gemini para esos proveedores) y las respuestas de tus perfiles corren con tu credencial. Es un secreto: se queda en este dispositivo y viaja solo en tus propias peticiones — el servidor nunca la guarda. Déjala vacía para usar la clave que preste el despliegue.", fr: "Différent de la connexion ci-dessus : c'était où vit le serveur de cette app ; ici, c'est avec quelle référence tourne la génération d'IA. Collez votre propre clé (Anthropic sk-ant-…, ou OpenAI / xAI / Gemini pour ces fournisseurs) et les réponses de vos profils tournent sur votre référence. C'est un secret : elle reste sur cet appareil et ne voyage qu'avec vos propres requêtes — le serveur ne la stocke jamais. Laissez vide pour utiliser la clé prêtée par le déploiement.", de: "Anders als die Verbindung oben: das war, wo der Server dieser App lebt; dies ist, auf wessen Zugangsdaten die KI-Generierung läuft. Fügen Sie Ihren eigenen Schlüssel ein (Anthropic sk-ant-…, oder OpenAI / xAI / Gemini für diese Anbieter), und die Antworten Ihrer Profile laufen auf Ihren Zugangsdaten. Er ist geheim: er bleibt auf diesem Gerät und reist nur mit Ihren eigenen Anfragen — der Server speichert ihn nie. Leer lassen, um den vom Deployment geliehenen Schlüssel zu nutzen.", pt: "Diferente da ligação acima: aquilo era onde vive o servidor desta app; isto é com que credencial corre a geração de IA. Cole a sua própria chave (Anthropic sk-ant-…, ou OpenAI / xAI / Gemini para esses fornecedores) e as respostas dos seus perfis correm na sua credencial. É um segredo: fica neste dispositivo e viaja só nos seus próprios pedidos — o servidor nunca a guarda. Deixe vazio para usar a chave que o deployment empresta.", it: "Diverso dalla connessione sopra: quella era dove vive il server di questa app; questa è con quale credenziale gira la generazione IA. Incolla la tua chiave (Anthropic sk-ant-…, oppure OpenAI / xAI / Gemini per quei provider) e le risposte dei tuoi profili girano sulla tua credenziale. È un segreto: resta su questo dispositivo e viaggia solo con le tue richieste — il server non la conserva mai. Lasciala vuota per usare la chiave prestata dal deployment.", ja: "上の接続とは別物です。あれはサーバーの場所、これはAI生成が誰の資格情報で動くかです。自分のキー（Anthropicのsk-ant-…、または各プロバイダーのOpenAI / xAI / Gemini）を貼ると、プロフィールの返答はあなたの資格情報で動きます。これは秘密で、この端末に留まりあなた自身のリクエストにのみ載ります — サーバーは保存しません。空のままなら配備側のキーを使います。", zh: "与上面的连接不同：那是服务器的位置，这是AI生成使用谁的凭证。粘贴你自己的密钥（Anthropic的sk-ant-…，或相应提供方的OpenAI / xAI / Gemini），你的资料回复就用你的凭证运行。它是机密：只留在本设备、只随你自己的请求发送 — 服务器绝不存储。留空则使用部署方借出的密钥。", hi: "ऊपर के कनेक्शन से अलग: वह था सर्वर कहाँ है; यह है AI जनरेशन किसकी क्रेडेंशियल पर चलती है। अपनी कुंजी चिपकाएँ (Anthropic sk-ant-…, या उन प्रदाताओं के लिए OpenAI / xAI / Gemini) और आपके प्रोफ़ाइल के जवाब आपकी क्रेडेंशियल पर चलेंगे। यह रहस्य है: यह इसी डिवाइस पर रहती है और केवल आपके अनुरोधों के साथ जाती है — सर्वर इसे कभी नहीं रखता। खाली छोड़ें तो डिप्लॉयमेंट की कुंजी उपयोग होगी।", ar: "مختلف عن الاتصال أعلاه: ذاك كان مكان الخادم؛ وهذا هو بيان الاعتماد الذي يعمل عليه توليد الذكاء الاصطناعي. الصق مفتاحك (Anthropic sk-ant-…، أو OpenAI / xAI / Gemini لتلك الجهات) فتعمل ردود ملفاتك على اعتمادك. إنه سر: يبقى على هذا الجهاز ولا يسافر إلا مع طلباتك — والخادم لا يخزنه أبدًا. اتركه فارغًا لاستخدام مفتاح النشر المعار.",
  },
  "set.key.label": {
    en: "API key", es: "Clave API", fr: "Clé API", de: "API-Schlüssel", pt: "Chave API", it: "Chiave API", ja: "APIキー", zh: "API密钥", hi: "API कुंजी", ar: "مفتاح API",
  },
  "set.key.ph": {
    en: "sk-…", es: "sk-…", fr: "sk-…", de: "sk-…", pt: "sk-…", it: "sk-…", ja: "sk-…", zh: "sk-…", hi: "sk-…", ar: "sk-…",
  },
  "set.offline": {
    en: "Offline status", es: "Estado sin conexión", fr: "État hors ligne", de: "Offline-Status", pt: "Estado offline", it: "Stato offline", ja: "オフライン状態", zh: "离线状态", hi: "ऑफ़लाइन स्थिति", ar: "حالة عدم الاتصال",
  },
  "set.offline.unreachable": {
    en: "Not reachable — is the backend running?", es: "Inaccesible — ¿está corriendo el backend?", fr: "Injoignable — le backend tourne-t-il ?", de: "Nicht erreichbar — läuft das Backend?", pt: "Inacessível — o backend está a correr?", it: "Irraggiungibile — il backend è in esecuzione?", ja: "接続できません — バックエンドは起動していますか？", zh: "无法连接 — 后端在运行吗？", hi: "पहुँच नहीं — क्या बैकएंड चल रहा है?", ar: "غير قابل للوصول — هل الخادم يعمل؟",
  },
  "set.who": {
    en: "Who wrote this? — check any text", es: "¿Quién escribió esto? — comprueba cualquier texto", fr: "Qui a écrit ceci ? — vérifiez n'importe quel texte", de: "Wer schrieb das? — jeden Text prüfen", pt: "Quem escreveu isto? — verifique qualquer texto", it: "Chi l'ha scritto? — verifica qualsiasi testo", ja: "誰が書いた？ — どんなテキストも確認", zh: "这是谁写的？— 核验任意文本", hi: "यह किसने लिखा? — कोई भी पाठ जाँचें", ar: "من كتب هذا؟ — تحقق من أي نص",
  },
  "set.who.lead": {
    en: "Paste writing you think came from a profile here. It answers from the text alone, with no credential id, and still answers when the text has been edited.", es: "Pega un texto que creas que salió de un perfil de aquí. Responde solo a partir del texto, sin id de credencial, y sigue respondiendo aunque el texto haya sido editado.", fr: "Collez un texte qui, selon vous, vient d'un profil d'ici. Il répond à partir du texte seul, sans id de référence, et répond encore quand le texte a été modifié.", de: "Fügen Sie einen Text ein, der Ihrer Meinung nach von einem Profil hier stammt. Es antwortet aus dem Text allein, ohne Nachweis-Id, und antwortet auch, wenn der Text bearbeitet wurde.", pt: "Cole um texto que ache que veio de um perfil daqui. Responde só a partir do texto, sem id de credencial, e continua a responder mesmo com o texto editado.", it: "Incolla un testo che pensi venga da un profilo di qui. Risponde dal solo testo, senza id di credenziale, e risponde anche quando il testo è stato modificato.", ja: "ここのプロフィールが書いたと思われる文章を貼り付けてください。資格情報IDなしにテキストだけから答え、編集された後でも答えます。", zh: "粘贴你认为出自这里某个资料的文字。它仅凭文本作答，无需凭证ID，即使文本被编辑过也能作答。", hi: "वह लेख चिपकाएँ जो आपको लगता है यहाँ के किसी प्रोफ़ाइल से आया। यह केवल पाठ से उत्तर देता है, बिना क्रेडेंशियल आईडी के, और संपादित पाठ पर भी उत्तर देता है।", ar: "الصق نصًا تظن أنه صادر من ملف هنا. يجيب من النص وحده، بلا معرّف اعتماد، ويظل يجيب حتى بعد تعديل النص.",
  },
  "set.who.ph": {
    en: "Paste the text…", es: "Pega el texto…", fr: "Collez le texte…", de: "Text einfügen…", pt: "Cole o texto…", it: "Incolla il testo…", ja: "テキストを貼り付け…", zh: "粘贴文本…", hi: "पाठ चिपकाएँ…", ar: "الصق النص…",
  },
  "set.who.by": {
    en: "{mark} produced by {pid} · {state}", es: "{mark} producido por {pid} · {state}", fr: "{mark} produit par {pid} · {state}", de: "{mark} erzeugt von {pid} · {state}", pt: "{mark} produzido por {pid} · {state}", it: "{mark} prodotto da {pid} · {state}", ja: "{mark} 作成: {pid} · {state}", zh: "{mark} 由{pid}生成 · {state}", hi: "{mark} {pid} द्वारा निर्मित · {state}", ar: "{mark} أنتجه {pid} · {state}",
  },
  "set.who.match": {
    en: "{m} of {s} passages match ({pct}% similar).", es: "{m} de {s} pasajes coinciden ({pct}% de similitud).", fr: "{m} passages sur {s} correspondent ({pct} % de similarité).", de: "{m} von {s} Passagen stimmen überein ({pct} % ähnlich).", pt: "{m} de {s} passagens coincidem ({pct}% de semelhança).", it: "{m} passaggi su {s} corrispondono ({pct}% simile).", ja: "{s}節中{m}節が一致（類似度{pct}%）。", zh: "{s}段中{m}段匹配（相似度{pct}%）。", hi: "{s} में से {m} अंश मेल खाते हैं ({pct}% समान)।", ar: "{m} من {s} مقاطع متطابقة (تشابه {pct}%).",
  },
  "set.who.none": {
    en: "No profile here wrote this.", es: "Ningún perfil de aquí escribió esto.", fr: "Aucun profil d'ici n'a écrit ceci.", de: "Kein Profil hier hat das geschrieben.", pt: "Nenhum perfil daqui escreveu isto.", it: "Nessun profilo di qui l'ha scritto.", ja: "ここのプロフィールは書いていません。", zh: "这里没有资料写过这段文字。", hi: "यहाँ के किसी प्रोफ़ाइल ने यह नहीं लिखा।", ar: "لم يكتب هذا أي ملف هنا.",
  },
  "set.pair": {
    en: "Open on your phone", es: "Abrir en tu teléfono", fr: "Ouvrir sur votre téléphone", de: "Auf dem Telefon öffnen", pt: "Abrir no telemóvel", it: "Apri sul telefono", ja: "スマホで開く", zh: "在手机上打开", hi: "फ़ोन पर खोलें", ar: "افتح على هاتفك",
  },
  "set.pair.alt": {
    en: "QR code for the studio URL on this network", es: "Código QR de la URL del estudio en esta red", fr: "Code QR de l'URL du studio sur ce réseau", de: "QR-Code der Studio-URL in diesem Netzwerk", pt: "Código QR do URL do estúdio nesta rede", it: "Codice QR dell'URL dello studio su questa rete", ja: "このネットワーク上のスタジオURLのQRコード", zh: "本网络内工作室URL的二维码", hi: "इस नेटवर्क पर स्टूडियो URL का QR कोड", ar: "رمز QR لعنوان الاستوديو على هذه الشبكة",
  },
  "set.session": {
    en: "Session", es: "Sesión", fr: "Session", de: "Sitzung", pt: "Sessão", it: "Sessione", ja: "セッション", zh: "会话", hi: "सत्र", ar: "الجلسة",
  },
  "set.session.profile": {
    en: "Profile: {id}", es: "Perfil: {id}", fr: "Profil : {id}", de: "Profil: {id}", pt: "Perfil: {id}", it: "Profilo: {id}", ja: "プロフィール: {id}", zh: "资料：{id}", hi: "प्रोफ़ाइल: {id}", ar: "الملف: {id}",
  },
  "set.session.out": {
    en: "Sign out & end session", es: "Cerrar sesión y terminarla", fr: "Se déconnecter et clore la session", de: "Abmelden & Sitzung beenden", pt: "Terminar sessão", it: "Esci e chiudi la sessione", ja: "サインアウトしてセッションを終了", zh: "退出并结束会话", hi: "साइन आउट करें और सत्र समाप्त करें", ar: "تسجيل الخروج وإنهاء الجلسة",
  },
  "set.mail": {
    en: "Email delivery", es: "Envío de correo", fr: "Envoi d'e-mails", de: "E-Mail-Versand", pt: "Envio de e-mail", it: "Invio e-mail", ja: "メール配信", zh: "邮件投递", hi: "ईमेल डिलीवरी", ar: "تسليم البريد",
  },
  "set.mail.smtp": {
    en: "Mail goes out through {host}{env}. New accounts must verify by email.", es: "El correo sale por {host}{env}. Las cuentas nuevas deben verificarse por email.", fr: "Le courrier part via {host}{env}. Les nouveaux comptes doivent se vérifier par e-mail.", de: "Mail geht über {host}{env} hinaus. Neue Konten müssen sich per E-Mail verifizieren.", pt: "O correio sai por {host}{env}. As contas novas têm de verificar por e-mail.", it: "La posta esce tramite {host}{env}. I nuovi account devono verificarsi via e-mail.", ja: "メールは{host}{env}経由で送信されます。新規アカウントはメール認証が必要です。", zh: "邮件经由{host}{env}发出。新账户必须通过邮件验证。", hi: "मेल {host}{env} से जाती है। नए खातों को ईमेल से सत्यापन करना होगा।", ar: "يخرج البريد عبر {host}{env}. يجب على الحسابات الجديدة التحقق بالبريد.",
  },
  "set.mail.none": {
    en: "No mail server configured, so nothing can be emailed — verification messages are written to this app's log and signup on this machine simply goes straight in. Point it at a mail account below to send real verification links. For Gmail, turn on 2-Step Verification and create an App password; paste that here, not your normal password.", es: "No hay servidor de correo configurado, así que no se puede enviar nada — los mensajes de verificación se escriben en el log de esta app y el registro en esta máquina entra directamente. Apúntalo a una cuenta de correo abajo para enviar enlaces reales. Para Gmail, activa la verificación en dos pasos y crea una contraseña de aplicación; pega esa aquí, no tu contraseña normal.", fr: "Aucun serveur de messagerie configuré, donc rien ne peut être envoyé — les messages de vérification vont dans le journal de l'app et l'inscription sur cette machine entre directement. Pointez-le vers un compte mail ci-dessous pour envoyer de vrais liens. Pour Gmail, activez la validation en deux étapes et créez un mot de passe d'application ; collez celui-là ici, pas votre mot de passe habituel.", de: "Kein Mailserver konfiguriert, also kann nichts gemailt werden — Verifizierungsnachrichten landen im Log dieser App, und die Anmeldung auf dieser Maschine geht direkt durch. Richten Sie unten ein Mailkonto ein, um echte Links zu senden. Für Gmail: Bestätigung in zwei Schritten aktivieren und ein App-Passwort erstellen; das hier einfügen, nicht Ihr normales Passwort.", pt: "Nenhum servidor de correio configurado, portanto nada pode ser enviado — as mensagens de verificação vão para o log desta app e o registo nesta máquina entra diretamente. Aponte para uma conta de correio abaixo para enviar links reais. Para o Gmail, ative a verificação em dois passos e crie uma palavra-passe de app; cole essa aqui, não a sua normal.", it: "Nessun server di posta configurato, quindi non si può inviare nulla — i messaggi di verifica finiscono nel log dell'app e la registrazione su questa macchina entra direttamente. Puntalo a un account di posta qui sotto per inviare link veri. Per Gmail, attiva la verifica in due passaggi e crea una password per le app; incolla quella qui, non la tua normale.", ja: "メールサーバーが未設定のため送信できません — 認証メッセージはこのアプリのログに書かれ、この端末でのサインアップはそのまま通ります。実際の認証リンクを送るには下のメールアカウントを設定してください。Gmailの場合は2段階認証を有効にしてアプリパスワードを作成し、通常のパスワードではなくそれを貼り付けてください。", zh: "未配置邮件服务器，因此无法发送任何邮件 — 验证消息写入本应用日志，本机注册直接通过。在下方指向一个邮件账户即可发送真实验证链接。Gmail需开启两步验证并创建应用专用密码；粘贴该密码而非常规密码。", hi: "कोई मेल सर्वर कॉन्फ़िगर नहीं, इसलिए कुछ भी ईमेल नहीं हो सकता — सत्यापन संदेश ऐप के लॉग में लिखे जाते हैं और इस मशीन पर साइनअप सीधे हो जाता है। असली लिंक भेजने के लिए नीचे मेल खाता जोड़ें। Gmail के लिए 2-चरण सत्यापन चालू करें और ऐप पासवर्ड बनाएँ; वही यहाँ चिपकाएँ, अपना सामान्य पासवर्ड नहीं।", ar: "لا يوجد خادم بريد مهيأ، فلا يمكن إرسال شيء — رسائل التحقق تُكتب في سجل التطبيق والتسجيل على هذا الجهاز يمر مباشرة. وجّهه إلى حساب بريد أدناه لإرسال روابط حقيقية. لجيميل، فعّل التحقق بخطوتين وأنشئ كلمة مرور تطبيق؛ والصقها هنا لا كلمة مرورك العادية.",
  },
  "set.mail.host": {
    en: "Mail server", es: "Servidor de correo", fr: "Serveur de messagerie", de: "Mailserver", pt: "Servidor de correio", it: "Server di posta", ja: "メールサーバー", zh: "邮件服务器", hi: "मेल सर्वर", ar: "خادم البريد",
  },
  "set.mail.host.ph": {
    en: "smtp.gmail.com", es: "smtp.gmail.com", fr: "smtp.gmail.com", de: "smtp.gmail.com", pt: "smtp.gmail.com", it: "smtp.gmail.com", ja: "smtp.gmail.com", zh: "smtp.gmail.com", hi: "smtp.gmail.com", ar: "smtp.gmail.com",
  },
  "set.mail.port": {
    en: "Port", es: "Puerto", fr: "Port", de: "Port", pt: "Porta", it: "Porta", ja: "ポート", zh: "端口", hi: "पोर्ट", ar: "المنفذ",
  },
  "set.mail.user": {
    en: "Username", es: "Usuario", fr: "Nom d'utilisateur", de: "Benutzername", pt: "Utilizador", it: "Nome utente", ja: "ユーザー名", zh: "用户名", hi: "यूज़रनेम", ar: "اسم المستخدم",
  },
  "set.mail.user.ph": {
    en: "you@gmail.com", es: "tu@gmail.com", fr: "vous@gmail.com", de: "sie@gmail.com", pt: "voce@gmail.com", it: "tu@gmail.com", ja: "you@gmail.com", zh: "you@gmail.com", hi: "aap@gmail.com", ar: "you@gmail.com",
  },
  "set.mail.pass": {
    en: "Password", es: "Contraseña", fr: "Mot de passe", de: "Passwort", pt: "Palavra-passe", it: "Password", ja: "パスワード", zh: "密码", hi: "पासवर्ड", ar: "كلمة المرور",
  },
  "set.mail.pass.saved": {
    en: "(saved — type to replace)", es: "(guardada — escribe para reemplazar)", fr: "(enregistré — tapez pour remplacer)", de: "(gespeichert — tippen zum Ersetzen)", pt: "(guardada — escreva para substituir)", it: "(salvata — digita per sostituire)", ja: "（保存済み — 入力で置き換え）", zh: "（已保存 — 输入即可替换）", hi: "(सहेजा गया — बदलने के लिए टाइप करें)", ar: "(محفوظة — اكتب للاستبدال)",
  },
  "set.mail.pass.ph": {
    en: "app password", es: "contraseña de aplicación", fr: "mot de passe d'application", de: "App-Passwort", pt: "palavra-passe de app", it: "password per le app", ja: "アプリパスワード", zh: "应用专用密码", hi: "ऐप पासवर्ड", ar: "كلمة مرور التطبيق",
  },
  "set.mail.from": {
    en: "From address", es: "Dirección del remitente", fr: "Adresse d'expéditeur", de: "Absenderadresse", pt: "Endereço do remetente", it: "Indirizzo mittente", ja: "送信元アドレス", zh: "发件地址", hi: "प्रेषक पता", ar: "عنوان المرسل",
  },
  "set.mail.link": {
    en: "Link address", es: "Dirección de los enlaces", fr: "Adresse des liens", de: "Link-Adresse", pt: "Endereço dos links", it: "Indirizzo dei link", ja: "リンクアドレス", zh: "链接地址", hi: "लिंक पता", ar: "عنوان الروابط",
  },
  "set.mail.link.note": {
    en: "— what verification links point at", es: "— adónde apuntan los enlaces de verificación", fr: "— où pointent les liens de vérification", de: "— worauf Verifizierungslinks zeigen", pt: "— para onde apontam os links de verificação", it: "— dove puntano i link di verifica", ja: "— 認証リンクの宛先", zh: "— 验证链接指向何处", hi: "— सत्यापन लिंक कहाँ इंगित करते हैं", ar: "— إلى أين تشير روابط التحقق",
  },
  "set.mail.link.ph": {
    en: "http://127.0.0.1:8000", es: "http://127.0.0.1:8000", fr: "http://127.0.0.1:8000", de: "http://127.0.0.1:8000", pt: "http://127.0.0.1:8000", it: "http://127.0.0.1:8000", ja: "http://127.0.0.1:8000", zh: "http://127.0.0.1:8000", hi: "http://127.0.0.1:8000", ar: "http://127.0.0.1:8000",
  },
  "set.mail.clear": {
    en: "Clear", es: "Borrar", fr: "Effacer", de: "Löschen", pt: "Limpar", it: "Cancella", ja: "クリア", zh: "清除", hi: "हटाएँ", ar: "مسح",
  },
  "set.mail.test": {
    en: "Send a test message to", es: "Enviar un mensaje de prueba a", fr: "Envoyer un message de test à", de: "Testnachricht senden an", pt: "Enviar mensagem de teste para", it: "Invia un messaggio di prova a", ja: "テストメッセージの宛先", zh: "发送测试邮件至", hi: "परीक्षण संदेश भेजें", ar: "أرسل رسالة اختبار إلى",
  },
  "set.mail.test.ph": {
    en: "you@example.com", es: "tu@example.com", fr: "vous@example.com", de: "sie@example.com", pt: "voce@example.com", it: "tu@example.com", ja: "you@example.com", zh: "you@example.com", hi: "aap@example.com", ar: "you@example.com",
  },
  "set.model": {
    en: "Which model answers", es: "Qué modelo responde", fr: "Quel modèle répond", de: "Welches Modell antwortet", pt: "Que modelo responde", it: "Quale modello risponde", ja: "どのモデルが答えるか", zh: "由哪个模型作答", hi: "कौन-सा मॉडल जवाब देता है", ar: "أي نموذج يجيب",
  },
  "set.model.lead": {
    en: "Your profile's replies can run on any of these. Pick one and every reply uses it; Automatic uses whichever is configured.", es: "Las respuestas de tu perfil pueden correr en cualquiera de estos. Elige uno y todas las respuestas lo usan; Automático usa el que esté configurado.", fr: "Les réponses de votre profil peuvent tourner sur n'importe lequel. Choisissez-en un et chaque réponse l'utilise ; Automatique utilise celui qui est configuré.", de: "Die Antworten Ihres Profils können auf jedem davon laufen. Wählen Sie eines, und jede Antwort nutzt es; Automatisch nutzt das jeweils Konfigurierte.", pt: "As respostas do seu perfil podem correr em qualquer um destes. Escolha um e todas as respostas o usam; Automático usa o que estiver configurado.", it: "Le risposte del tuo profilo possono girare su uno qualsiasi. Scegline uno e ogni risposta lo usa; Automatico usa quello configurato.", ja: "プロフィールの返答はどれでも動かせます。選べばすべての返答がそれを使い、「自動」は設定済みのものを使います。", zh: "你的资料回复可运行在任一模型上。选定后每条回复都用它；「自动」使用已配置的模型。", hi: "आपके प्रोफ़ाइल के जवाब इनमें से किसी पर चल सकते हैं। एक चुनें और हर जवाब उसी का उपयोग करेगा; स्वचालित जो कॉन्फ़िगर है उसे लेता है।", ar: "يمكن أن تعمل ردود ملفك على أي منها. اختر واحدًا فتستخدمه كل الردود؛ التلقائي يستخدم ما هو مهيأ.",
  },
  "set.model.stub": {
    en: "⚠ Right now replies come from the built-in offline helper — no online model has a working key on this deployment. Pick a provider above and add its key.", es: "⚠ Ahora mismo las respuestas vienen del asistente offline integrado — ningún modelo en línea tiene clave válida en este despliegue. Elige un proveedor arriba y añade su clave.", fr: "⚠ En ce moment, les réponses viennent de l'assistant hors ligne intégré — aucun modèle en ligne n'a de clé valide sur ce déploiement. Choisissez un fournisseur ci-dessus et ajoutez sa clé.", de: "⚠ Derzeit kommen Antworten vom eingebauten Offline-Helfer — kein Online-Modell hat auf diesem Deployment einen gültigen Schlüssel. Wählen Sie oben einen Anbieter und fügen Sie dessen Schlüssel hinzu.", pt: "⚠ Neste momento as respostas vêm do assistente offline integrado — nenhum modelo online tem chave válida neste deployment. Escolha um fornecedor acima e adicione a sua chave.", it: "⚠ In questo momento le risposte vengono dall'assistente offline integrato — nessun modello online ha una chiave valida su questo deployment. Scegli un provider sopra e aggiungi la sua chiave.", ja: "⚠ 現在の返答は内蔵オフラインヘルパーからです — この配備で有効なキーを持つオンラインモデルがありません。上でプロバイダーを選びキーを追加してください。", zh: "⚠ 当前回复来自内置离线助手 — 此部署上没有任何在线模型持有有效密钥。请在上方选择提供方并添加其密钥。", hi: "⚠ अभी जवाब अंतर्निहित ऑफ़लाइन सहायक से आ रहे हैं — इस डिप्लॉयमेंट पर किसी ऑनलाइन मॉडल की कुंजी नहीं है। ऊपर प्रदाता चुनें और उसकी कुंजी जोड़ें।", ar: "⚠ الردود الآن من المساعد المدمج دون اتصال — لا يملك أي نموذج متصل مفتاحًا صالحًا في هذا النشر. اختر مزودًا أعلاه وأضف مفتاحه.",
  },
  "set.model.resolves": {
    en: "⚠ Right now it resolves to {effective} — the one you picked has no key on this deployment yet.", es: "⚠ Ahora mismo se resuelve a {effective} — el que elegiste aún no tiene clave en este despliegue.", fr: "⚠ En ce moment, cela se résout en {effective} — celui que vous avez choisi n'a pas encore de clé sur ce déploiement.", de: "⚠ Derzeit löst es zu {effective} auf — das gewählte hat auf diesem Deployment noch keinen Schlüssel.", pt: "⚠ Neste momento resolve para {effective} — o que escolheu ainda não tem chave neste deployment.", it: "⚠ In questo momento si risolve in {effective} — quello scelto non ha ancora una chiave su questo deployment.", ja: "⚠ 現在は{effective}に解決されます — 選んだものはまだこの配備にキーがありません。", zh: "⚠ 当前解析为{effective} — 你选的那个在此部署上还没有密钥。", hi: "⚠ अभी यह {effective} पर हल होता है — आपके चुने हुए की इस डिप्लॉयमेंट पर अभी कुंजी नहीं है।", ar: "⚠ الآن يُحل إلى {effective} — الذي اخترته لا مفتاح له في هذا النشر بعد.",
  },
  "sell.title": {
    en: "What you are owed", es: "Lo que se te debe", fr: "Ce qui vous est dû", de: "Was Ihnen zusteht", pt: "O que lhe é devido", it: "Ciò che ti è dovuto", ja: "あなたへの支払い", zh: "你应得的", hi: "आपका बकाया", ar: "ما يُستحق لك",
  },
  "sell.lead": {
    en: "The seller's side. What your profile is offered for, who holds a licence on it, what that has earned, and asking to be paid.", es: "El lado del vendedor. Por cuánto se ofrece tu perfil, quién tiene una licencia, qué ha ganado y cómo pedir el pago.", fr: "Le côté vendeur. À quel prix votre profil est offert, qui détient une licence, ce que cela a rapporté, et demander à être payé.", de: "Die Verkäuferseite. Wofür Ihr Profil angeboten wird, wer eine Lizenz hält, was das eingebracht hat, und die Auszahlung anfordern.", pt: "O lado do vendedor. Por quanto o seu perfil é oferecido, quem detém uma licença, o que isso rendeu, e pedir para ser pago.", it: "Il lato del venditore. A quanto è offerto il tuo profilo, chi ne detiene una licenza, cosa ha fruttato, e chiedere di essere pagato.", ja: "売り手側の画面。プロフィールの提供条件、ライセンス保持者、収益、そして支払いの請求。", zh: "卖方视角。你的资料以什么条件提供、谁持有许可、赚了多少、以及请求付款。", hi: "विक्रेता पक्ष। आपका प्रोफ़ाइल किस पर पेश है, किसके पास लाइसेंस है, उसने क्या कमाया, और भुगतान माँगना।", ar: "جانب البائع. بمَ يُعرض ملفك، ومن يحمل ترخيصًا عليه، وما كسبه، وطلب الدفع.",
  },
  "sell.offer": {
    en: "Your offer", es: "Tu oferta", fr: "Votre offre", de: "Ihr Angebot", pt: "A sua oferta", it: "La tua offerta", ja: "あなたのオファー", zh: "你的报价", hi: "आपकी पेशकश", ar: "عرضك",
  },
  "sell.offer.none": {
    en: "Not offered for licence. That is the ordinary state of a profile, not an error.", es: "No se ofrece bajo licencia. Ese es el estado normal de un perfil, no un error.", fr: "Non offert sous licence. C'est l'état ordinaire d'un profil, pas une erreur.", de: "Nicht zur Lizenz angeboten. Das ist der Normalzustand eines Profils, kein Fehler.", pt: "Não oferecido sob licença. É o estado normal de um perfil, não um erro.", it: "Non offerto in licenza. È lo stato ordinario di un profilo, non un errore.", ja: "ライセンス提供されていません。これはプロフィールの通常状態でありエラーではありません。", zh: "未提供许可。这是资料的常态，并非错误。", hi: "लाइसेंस के लिए पेश नहीं। यह प्रोफ़ाइल की सामान्य स्थिति है, त्रुटि नहीं।", ar: "غير معروض للترخيص. هذه الحالة العادية للملف، لا خطأ.",
  },
  "sell.offer.adult": {
    en: "A licence that permits derivatives can only be sold to a verified-18+ buyer. The check runs at the till, where the fee moves, rather than at delivery.", es: "Una licencia que permite derivados solo puede venderse a un comprador verificado de 18+. La comprobación corre en la caja, donde se mueve el dinero, no en la entrega.", fr: "Une licence permettant des dérivés ne peut être vendue qu'à un acheteur vérifié 18+. Le contrôle se fait à la caisse, où l'argent bouge, pas à la livraison.", de: "Eine Lizenz, die Ableitungen erlaubt, kann nur an verifizierte 18+-Käufer verkauft werden. Die Prüfung läuft an der Kasse, wo die Gebühr fließt, nicht bei der Lieferung.", pt: "Uma licença que permite derivados só pode ser vendida a um comprador verificado 18+. A verificação corre na caixa, onde o dinheiro se move, não na entrega.", it: "Una licenza che permette derivati può essere venduta solo a un acquirente verificato 18+. Il controllo gira alla cassa, dove si muove il denaro, non alla consegna.", ja: "派生を許すライセンスは18歳以上と確認済みの購入者にのみ販売できます。確認は配達時ではなく、料金が動くレジで行われます。", zh: "允许派生的许可只能卖给经过验证的18+买家。核验在钱款流动的收银处进行，而非交付时。", hi: "व्युत्पन्न की अनुमति वाला लाइसेंस केवल सत्यापित 18+ खरीदार को बेचा जा सकता है। जाँच वहीं होती है जहाँ पैसा चलता है — काउंटर पर, डिलीवरी पर नहीं।", ar: "الترخيص الذي يسمح بالمشتقات لا يُباع إلا لمشترٍ موثق فوق 18. يجري الفحص عند الصندوق حيث يتحرك المال، لا عند التسليم.",
  },
  "sell.kind.consult": {
    en: "consult", es: "consulta", fr: "consultation", de: "Beratung", pt: "consulta", it: "consulenza", ja: "相談", zh: "咨询", hi: "परामर्श", ar: "استشارة",
  },
  "sell.kind.finetune": {
    en: "finetune", es: "ajuste fino", fr: "affinage", de: "Feinabstimmung", pt: "afinação", it: "messa a punto", ja: "微調整", zh: "微调", hi: "फ़ाइन-ट्यून", ar: "ضبط دقيق",
  },
  "sell.kind.clone": {
    en: "clone", es: "clon", fr: "clone", de: "Klon", pt: "clone", it: "clone", ja: "クローン", zh: "克隆", hi: "क्लोन", ar: "استنساخ",
  },
  "sell.offer.price.ph": {
    en: "price", es: "precio", fr: "prix", de: "Preis", pt: "preço", it: "prezzo", ja: "価格", zh: "价格", hi: "मूल्य", ar: "السعر",
  },
  "sell.offer.ccy.ph": {
    en: "USD", es: "USD", fr: "USD", de: "USD", pt: "USD", it: "USD", ja: "USD", zh: "USD", hi: "USD", ar: "USD",
  },
  "sell.offer.terms.ph": {
    en: "terms", es: "condiciones", fr: "conditions", de: "Bedingungen", pt: "condições", it: "condizioni", ja: "条件", zh: "条款", hi: "शर्तें", ar: "الشروط",
  },
  "sell.offer.post": {
    en: "Post this offer", es: "Publicar esta oferta", fr: "Publier cette offre", de: "Dieses Angebot einstellen", pt: "Publicar esta oferta", it: "Pubblica questa offerta", ja: "このオファーを掲示", zh: "发布此报价", hi: "यह पेशकश डालें", ar: "انشر هذا العرض",
  },
  "sell.offer.stop": {
    en: "Stop offering it", es: "Dejar de ofrecerlo", fr: "Cesser de l'offrir", de: "Nicht mehr anbieten", pt: "Deixar de oferecer", it: "Smetti di offrirlo", ja: "提供をやめる", zh: "停止提供", hi: "पेश करना बंद करें", ar: "أوقف عرضه",
  },
  "sell.holders": {
    en: "Who holds a licence", es: "Quién tiene una licencia", fr: "Qui détient une licence", de: "Wer eine Lizenz hält", pt: "Quem detém uma licença", it: "Chi detiene una licenza", ja: "ライセンス保持者", zh: "谁持有许可", hi: "किसके पास लाइसेंस है", ar: "من يحمل ترخيصًا",
  },
  "sell.holders.none": {
    en: "Nobody yet.", es: "Nadie todavía.", fr: "Personne pour l'instant.", de: "Noch niemand.", pt: "Ninguém ainda.", it: "Ancora nessuno.", ja: "まだ誰もいません。", zh: "尚无人。", hi: "अभी कोई नहीं।", ar: "لا أحد بعد.",
  },
  "sell.holders.revoke": {
    en: "Revoke", es: "Revocar", fr: "Révoquer", de: "Widerrufen", pt: "Revogar", it: "Revoca", ja: "失効させる", zh: "撤销", hi: "रद्द करें", ar: "إلغاء",
  },
  "sell.holders.rule": {
    en: "Revoking stops the buyer deriving from that licence. It does not unmake an agent already derived from it, and it does not take the fee off your statement — a sale that happened stays on the record.", es: "Revocar impide que el comprador derive de esa licencia. No deshace un agente ya derivado, ni quita la tarifa de tu estado de cuenta — una venta ocurrida queda en el registro.", fr: "Révoquer empêche l'acheteur de dériver de cette licence. Cela ne défait pas un agent déjà dérivé, et ne retire pas les frais de votre relevé — une vente advenue reste au registre.", de: "Der Widerruf stoppt künftige Ableitungen aus dieser Lizenz. Er macht einen bereits abgeleiteten Agenten nicht ungeschehen und nimmt die Gebühr nicht von Ihrer Abrechnung — ein geschehener Verkauf bleibt verzeichnet.", pt: "Revogar impede o comprador de derivar dessa licença. Não desfaz um agente já derivado, nem tira a taxa do seu extrato — uma venda que aconteceu fica no registo.", it: "Revocare impedisce all'acquirente di derivare da quella licenza. Non disfa un agente già derivato, né toglie la tariffa dal tuo estratto — una vendita avvenuta resta a registro.", ja: "失効は購入者がそのライセンスから派生させることを止めます。既に派生したエージェントは消えず、明細から料金も消えません — 成立した販売は記録に残ります。", zh: "撤销会阻止买家继续从该许可派生。它不会撤销已派生的智能体，也不会从你的账单上抹去费用 — 已发生的销售留在记录上。", hi: "रद्द करने से खरीदार उस लाइसेंस से आगे व्युत्पन्न नहीं कर सकता। पहले से व्युत्पन्न एजेंट नहीं मिटता, न ही शुल्क आपके विवरण से हटता है — हुई बिक्री रिकॉर्ड में रहती है।", ar: "الإلغاء يمنع المشتري من الاشتقاق من ذلك الترخيص. لا يمحو وكيلاً مشتقًا بالفعل، ولا يزيل الرسوم من كشفك — البيع الذي حدث يبقى في السجل.",
  },
  "sell.earn": {
    en: "Earnings", es: "Ganancias", fr: "Revenus", de: "Einnahmen", pt: "Ganhos", it: "Guadagni", ja: "収益", zh: "收入", hi: "कमाई", ar: "الأرباح",
  },
  "sell.earn.signin": {
    en: "Nothing to show — sign in as the profile's owner.", es: "Nada que mostrar — inicia sesión como propietario del perfil.", fr: "Rien à montrer — connectez-vous comme propriétaire du profil.", de: "Nichts zu zeigen — melden Sie sich als Profilinhaber an.", pt: "Nada a mostrar — inicie sessão como proprietário do perfil.", it: "Niente da mostrare — accedi come proprietario del profilo.", ja: "表示できるものがありません — プロフィールの所有者としてサインインしてください。", zh: "无可显示 — 请以资料所有者身份登录。", hi: "दिखाने को कुछ नहीं — प्रोफ़ाइल स्वामी के रूप में साइन इन करें।", ar: "لا شيء للعرض — سجّل الدخول كمالك الملف.",
  },
  "sell.earn.line": {
    en: "Accrued {a} · paid {p} · lifetime {l}", es: "Acumulado {a} · pagado {p} · histórico {l}", fr: "Accumulé {a} · payé {p} · cumul {l}", de: "Aufgelaufen {a} · ausgezahlt {p} · gesamt {l}", pt: "Acumulado {a} · pago {p} · total {l}", it: "Maturato {a} · pagato {p} · totale {l}", ja: "未払 {a} · 支払済 {p} · 累計 {l}", zh: "应收{a} · 已付{p} · 累计{l}", hi: "संचित {a} · भुगतान {p} · कुल {l}", ar: "مستحق {a} · مدفوع {p} · إجمالي {l}",
  },
  "sell.earn.mixed": {
    en: "Those are your {ccy} figures. This account also earns in {others}, and the two are not added together — a total across currencies is not a number.", es: "Esas son tus cifras en {ccy}. Esta cuenta también gana en {others}, y no se suman — un total entre monedas no es un número.", fr: "Ce sont vos chiffres en {ccy}. Ce compte gagne aussi en {others}, et on ne les additionne pas — un total entre devises n'est pas un nombre.", de: "Das sind Ihre {ccy}-Zahlen. Dieses Konto verdient auch in {others}, und beides wird nicht addiert — eine Summe über Währungen ist keine Zahl.", pt: "Esses são os seus valores em {ccy}. Esta conta também ganha em {others}, e os dois não se somam — um total entre moedas não é um número.", it: "Quelle sono le tue cifre in {ccy}. Questo account guadagna anche in {others}, e le due non si sommano — un totale tra valute non è un numero.", ja: "これは{ccy}での数字です。このアカウントは{others}でも収益があり、両者は合算されません — 通貨をまたぐ合計は数字になりません。", zh: "这些是你的{ccy}数字。此账户还在{others}中有收入，两者不相加 — 跨币种的总额不是一个数。", hi: "ये आपके {ccy} आँकड़े हैं। यह खाता {others} में भी कमाता है, और दोनों जोड़े नहीं जाते — मुद्राओं के पार कुल कोई संख्या नहीं।", ar: "هذه أرقامك بعملة {ccy}. يكسب هذا الحساب أيضًا بعملات {others}، ولا يُجمعان — الإجمالي عبر العملات ليس رقمًا.",
  },
  "sell.earn.bycur": {
    en: "{c} — accrued {a} · paid {p}", es: "{c} — acumulado {a} · pagado {p}", fr: "{c} — accumulé {a} · payé {p}", de: "{c} — aufgelaufen {a} · ausgezahlt {p}", pt: "{c} — acumulado {a} · pago {p}", it: "{c} — maturato {a} · pagato {p}", ja: "{c} — 未払 {a} · 支払済 {p}", zh: "{c} — 应收{a} · 已付{p}", hi: "{c} — संचित {a} · भुगतान {p}", ar: "{c} — مستحق {a} · مدفوع {p}",
  },
  "sell.earn.none": {
    en: "No sales yet.", es: "Sin ventas todavía.", fr: "Pas encore de ventes.", de: "Noch keine Verkäufe.", pt: "Ainda sem vendas.", it: "Ancora nessuna vendita.", ja: "まだ販売はありません。", zh: "尚无销售。", hi: "अभी कोई बिक्री नहीं।", ar: "لا مبيعات بعد.",
  },
  "sell.earn.payout": {
    en: "Request a payout", es: "Solicitar un pago", fr: "Demander un versement", de: "Auszahlung anfordern", pt: "Pedir um pagamento", it: "Richiedi un pagamento", ja: "支払いを請求", zh: "申请付款", hi: "भुगतान माँगें", ar: "اطلب دفعة",
  },
  "sell.earn.payoutc": {
    en: "Pay out {c}", es: "Pagar {c}", fr: "Verser {c}", de: "{c} auszahlen", pt: "Pagar {c}", it: "Paga {c}", ja: "{c}を支払う", zh: "支付{c}", hi: "{c} का भुगतान", ar: "ادفع {c}",
  },
  "sell.earn.receipt": {
    en: "{total} across {n} entries — {note}", es: "{total} en {n} entradas — {note}", fr: "{total} sur {n} entrées — {note}", de: "{total} über {n} Einträge — {note}", pt: "{total} em {n} entradas — {note}", it: "{total} su {n} voci — {note}", ja: "{n}件で{total} — {note}", zh: "{n}条共{total} — {note}", hi: "{n} प्रविष्टियों में {total} — {note}", ar: "{total} عبر {n} قيود — {note}",
  },
  "sell.listing": {
    en: "A listing in the window", es: "Un anuncio en el escaparate", fr: "Une annonce en vitrine", de: "Ein Eintrag im Schaufenster", pt: "Um anúncio na montra", it: "Un annuncio in vetrina", ja: "ショーウィンドウの出品", zh: "橱窗里的商品", hi: "खिड़की में एक लिस्टिंग", ar: "إعلان في الواجهة",
  },
  "sell.listing.lead": {
    en: "Creating one needs no account — that is the design, and the seller is established when a price is attached. Signed in, the listing is recorded as yours, which is what lets you take it down again.", es: "Crearlo no necesita cuenta — así está diseñado, y el vendedor se establece al fijar un precio. Con sesión iniciada, el anuncio queda registrado como tuyo, que es lo que te permite retirarlo.", fr: "En créer une ne demande aucun compte — c'est voulu, et le vendeur est établi quand un prix est attaché. Connecté, l'annonce est enregistrée comme la vôtre, ce qui vous permet de la retirer.", de: "Zum Erstellen braucht es kein Konto — das ist Absicht, und der Verkäufer steht fest, sobald ein Preis dranhängt. Angemeldet wird der Eintrag als Ihrer verzeichnet, was Ihnen erlaubt, ihn wieder zu entfernen.", pt: "Criar um não precisa de conta — é o design, e o vendedor fica estabelecido quando se anexa um preço. Com sessão iniciada, o anúncio fica registado como seu, o que lhe permite retirá-lo.", it: "Crearne uno non richiede account — è il design, e il venditore si stabilisce quando si attacca un prezzo. Con l'accesso, l'annuncio è registrato come tuo, il che ti permette di toglierlo.", ja: "作成にアカウントは不要です — それが設計であり、価格が付いた時点で売り手が確定します。サインインしていれば出品はあなたのものとして記録され、だからこそ取り下げられます。", zh: "创建无需账户 — 这是设计使然，卖家在附上价格时确立。登录后，商品会记录为你的，这正是你能将其下架的原因。", hi: "बनाने के लिए खाता नहीं चाहिए — यही डिज़ाइन है, और मूल्य जुड़ते ही विक्रेता स्थापित होता है। साइन इन करने पर लिस्टिंग आपकी दर्ज होती है, जिसी से आप उसे हटा सकते हैं।", ar: "إنشاؤه لا يتطلب حسابًا — هذا هو التصميم، ويتحدد البائع عند إرفاق سعر. عند تسجيل الدخول يُسجل الإعلان باسمك، وهذا ما يتيح لك إنزاله.",
  },
  "sell.listing.title.ph": {
    en: "title", es: "título", fr: "titre", de: "Titel", pt: "título", it: "titolo", ja: "タイトル", zh: "标题", hi: "शीर्षक", ar: "العنوان",
  },
  "sell.listing.blurb.ph": {
    en: "blurb", es: "descripción", fr: "descriptif", de: "Kurztext", pt: "descrição", it: "descrizione", ja: "紹介文", zh: "简介", hi: "विवरण", ar: "نبذة",
  },
  "sell.listing.put": {
    en: "Put it in the window", es: "Ponerlo en el escaparate", fr: "Le mettre en vitrine", de: "Ins Schaufenster stellen", pt: "Pôr na montra", it: "Mettilo in vetrina", ja: "ウィンドウに出す", zh: "放入橱窗", hi: "खिड़की में रखें", ar: "ضعه في الواجهة",
  },
  "sell.listing.id.ph": {
    en: "listing id", es: "id del anuncio", fr: "id de l'annonce", de: "Eintrags-Id", pt: "id do anúncio", it: "id dell'annuncio", ja: "出品ID", zh: "商品ID", hi: "लिस्टिंग आईडी", ar: "معرّف الإعلان",
  },
  "sell.listing.down": {
    en: "Take it down", es: "Retirarlo", fr: "La retirer", de: "Herunternehmen", pt: "Retirá-lo", it: "Toglilo", ja: "取り下げる", zh: "下架", hi: "हटा लें", ar: "أنزله",
  },
  "sell.listing.rule": {
    en: "Only a claimant may take a listing down or move it: whoever made it, the seller on its offer, or the owner of the profile it advertises. It used to take no credential at all, so anyone could remove anyone's — while the same stranger asking to withdraw the offer on it was told it was not theirs.", es: "Solo un reclamante puede retirar o mover un anuncio: quien lo creó, el vendedor de su oferta o el propietario del perfil que anuncia. Antes no requería credencial alguna, así que cualquiera podía quitar el de cualquiera — mientras al mismo desconocido que pedía retirar la oferta se le decía que no era suya.", fr: "Seul un ayant droit peut retirer ou déplacer une annonce : celui qui l'a créée, le vendeur de son offre, ou le propriétaire du profil annoncé. Avant, aucune référence n'était exigée : n'importe qui pouvait retirer celle de n'importe qui — alors que le même inconnu demandant à retirer l'offre s'entendait dire qu'elle n'était pas à lui.", de: "Nur ein Berechtigter darf einen Eintrag entfernen oder verschieben: wer ihn erstellte, der Verkäufer seines Angebots oder der Inhaber des beworbenen Profils. Früher brauchte es gar keine Berechtigung, sodass jeder jeden entfernen konnte — während derselbe Fremde beim Zurückziehen des Angebots hörte, es sei nicht seins.", pt: "Só um requerente pode retirar ou mover um anúncio: quem o criou, o vendedor da sua oferta ou o dono do perfil anunciado. Antes não exigia credencial nenhuma, e qualquer um podia remover o de qualquer um — enquanto ao mesmo estranho que pedia para retirar a oferta se dizia que não era dele.", it: "Solo un avente diritto può togliere o spostare un annuncio: chi l'ha creato, il venditore della sua offerta o il proprietario del profilo pubblicizzato. Prima non serviva alcuna credenziale, così chiunque poteva rimuovere quello di chiunque — mentre allo stesso estraneo che chiedeva di ritirare l'offerta si diceva che non era sua.", ja: "出品を取り下げ・移動できるのは権利者のみです：作成者、そのオファーの売り手、または宣伝されるプロフィールの所有者。かつては資格情報が一切不要で、誰でも他人の出品を消せました — 同じ他人がオファーの取り下げを求めると「あなたのものではない」と言われたのにです。", zh: "只有权利人才能下架或移动商品：创建者、其报价的卖家、或它所宣传资料的所有者。过去完全不需凭证，任何人都能删除任何人的商品 — 而同一个陌生人想撤回报价时却被告知那不是他的。", hi: "लिस्टिंग केवल दावेदार ही हटा या स्थानांतरित कर सकता है: जिसने बनाई, उसकी पेशकश का विक्रेता, या जिस प्रोफ़ाइल का विज्ञापन है उसका स्वामी। पहले कोई क्रेडेंशियल नहीं लगती थी, तो कोई भी किसी की भी हटा सकता था — जबकि वही अजनबी पेशकश वापस लेने पर सुनता था कि वह उसकी नहीं।", ar: "لا يُنزل الإعلان أو ينقله إلا صاحب حق: من أنشأه، أو بائع عرضه، أو مالك الملف المعلن عنه. لم يكن يتطلب أي اعتماد من قبل، فكان بوسع أي أحد إزالة إعلان أي أحد — بينما يُقال للغريب نفسه عند طلب سحب العرض إنه ليس له.",
  },
  "sell.price": {
    en: "A price on it", es: "Un precio encima", fr: "Un prix dessus", de: "Ein Preis darauf", pt: "Um preço em cima", it: "Un prezzo sopra", ja: "価格を付ける", zh: "标上价格", hi: "इस पर मूल्य", ar: "سعر عليه",
  },
  "sell.price.lead": {
    en: "A listing is a shop window; an offer is what makes it a shop. The sale accrues to your account, not to the profile you happen to be signed in as — a distinction that cost real money before this screen existed: the sale went through, the receipt said it was on your statement, and the statement was empty.", es: "Un anuncio es un escaparate; una oferta es lo que lo hace tienda. La venta se acredita a tu cuenta, no al perfil con el que estés conectado — una distinción que costó dinero real antes de esta pantalla: la venta pasó, el recibo decía que estaba en tu estado de cuenta, y el estado estaba vacío.", fr: "Une annonce est une vitrine ; une offre en fait une boutique. La vente est créditée à votre compte, pas au profil avec lequel vous êtes connecté — une distinction qui a coûté de l'argent réel avant cet écran : la vente est passée, le reçu disait qu'elle était sur votre relevé, et le relevé était vide.", de: "Ein Eintrag ist ein Schaufenster; ein Angebot macht daraus einen Laden. Der Verkauf fließt Ihrem Konto zu, nicht dem gerade angemeldeten Profil — ein Unterschied, der vor diesem Bildschirm echtes Geld kostete: der Verkauf ging durch, die Quittung verwies auf Ihre Abrechnung, und die war leer.", pt: "Um anúncio é uma montra; uma oferta é o que faz dela uma loja. A venda credita na sua conta, não no perfil com que estiver ligado — uma distinção que custou dinheiro real antes deste ecrã: a venda passou, o recibo dizia que estava no seu extrato, e o extrato estava vazio.", it: "Un annuncio è una vetrina; un'offerta è ciò che la rende un negozio. La vendita matura sul tuo account, non sul profilo con cui sei collegato — una distinzione che è costata denaro vero prima di questa schermata: la vendita è passata, la ricevuta diceva che era sul tuo estratto, e l'estratto era vuoto.", ja: "出品はショーウィンドウで、オファーがそれを店にします。売上はあなたのアカウントに入り、たまたまサインイン中のプロフィールには入りません — この画面ができる前に実際の損失を生んだ区別です：販売は成立し、領収書は明細にあると言い、明細は空でした。", zh: "商品是橱窗；报价才使其成为商店。销售记入你的账户，而非你恰好登录的资料 — 在此屏幕出现前这个区别曾造成真金白银的损失：销售成功了，收据说钱在你的账单上，而账单是空的。", hi: "लिस्टिंग खिड़की है; पेशकश उसे दुकान बनाती है। बिक्री आपके खाते में जमा होती है, उस प्रोफ़ाइल में नहीं जिससे आप साइन इन हैं — यह फ़र्क़ इस स्क्रीन से पहले असली पैसे का पड़ा: बिक्री हुई, रसीद ने कहा आपके विवरण में है, और विवरण ख़ाली था।", ar: "الإعلان واجهة؛ والعرض هو ما يجعله متجرًا. يُقيد البيع في حسابك لا في الملف الذي صادف أنك مسجل به — فرق كلف مالاً حقيقيًا قبل هذه الشاشة: تم البيع، وقال الإيصال إنه في كشفك، وكان الكشف فارغًا.",
  },
  "sell.price.stock.ph": {
    en: "stock (blank = unlimited)", es: "existencias (vacío = ilimitado)", fr: "stock (vide = illimité)", de: "Bestand (leer = unbegrenzt)", pt: "stock (vazio = ilimitado)", it: "scorte (vuoto = illimitato)", ja: "在庫（空欄＝無制限）", zh: "库存（留空＝无限）", hi: "स्टॉक (खाली = असीमित)", ar: "المخزون (فارغ = غير محدود)",
  },
  "sell.price.put": {
    en: "Put a price on it", es: "Ponerle un precio", fr: "Y mettre un prix", de: "Einen Preis draufsetzen", pt: "Pôr-lhe um preço", it: "Mettici un prezzo", ja: "価格を付ける", zh: "标价", hi: "मूल्य लगाएँ", ar: "ضع سعرًا عليه",
  },
  "sell.price.stop": {
    en: "Stop selling it", es: "Dejar de venderlo", fr: "Cesser de le vendre", de: "Verkauf beenden", pt: "Deixar de vender", it: "Smetti di venderlo", ja: "販売をやめる", zh: "停止销售", hi: "बेचना बंद करें", ar: "أوقف بيعه",
  },
  "sell.price.sold": {
    en: "sold {n}", es: "vendidos {n}", fr: "vendus {n}", de: "verkauft {n}", pt: "vendidos {n}", it: "venduti {n}", ja: "販売数{n}", zh: "已售{n}", hi: "बिके {n}", ar: "بيع {n}",
  },
  "sell.place": {
    en: "Where it is offered", es: "Dónde se ofrece", fr: "Où c'est offert", de: "Wo es angeboten wird", pt: "Onde é oferecido", it: "Dove è offerto", ja: "提供される場所", zh: "提供地点", hi: "कहाँ पेश है", ar: "أين يُعرض",
  },
  "sell.place.lead": {
    en: "A named locality you type, never coordinates and never anything read off an address or an IP. A rated listing is refused a location outright: where a performer physically is has nothing to do with browsing them.", es: "Una localidad con nombre que tú escribes, nunca coordenadas ni nada leído de una dirección o una IP. A un anuncio clasificado se le niega la ubicación de plano: dónde está físicamente un artista no tiene nada que ver con explorarlo.", fr: "Une localité nommée que vous tapez, jamais de coordonnées ni rien lu d'une adresse ou d'une IP. Une annonce classée se voit refuser toute localisation : où se trouve physiquement un artiste n'a rien à voir avec sa consultation.", de: "Ein benannter Ort, den Sie eintippen, nie Koordinaten und nie etwas aus Adresse oder IP. Einem bewerteten Eintrag wird der Standort rundweg verweigert: wo jemand physisch ist, hat mit dem Stöbern nichts zu tun.", pt: "Uma localidade nomeada que você escreve, nunca coordenadas nem nada lido de um endereço ou IP. A um anúncio classificado é recusada a localização de imediato: onde um artista está fisicamente nada tem a ver com o navegar por ele.", it: "Una località con nome che digiti tu, mai coordinate né nulla letto da un indirizzo o un IP. A un annuncio classificato la posizione è rifiutata in blocco: dove si trova fisicamente un artista non c'entra col suo essere sfogliato.", ja: "入力するのは地名だけで、座標や住所・IPから読み取ったものは決して使いません。レーティング付き出品には所在地が一切拒否されます：出演者が物理的にどこにいるかは、閲覧とは無関係です。", zh: "只用你输入的地名，绝不用坐标，也绝不读取地址或IP。分级商品被直接拒绝定位：表演者的实际位置与浏览毫无关系。", hi: "आप जो नामित स्थान टाइप करें वही, कभी निर्देशांक नहीं, न ही पते या IP से पढ़ा कुछ। रेटेड लिस्टिंग को स्थान सिरे से मना है: कलाकार शारीरिक रूप से कहाँ है, उसे ब्राउज़ करने से कोई मतलब नहीं।", ar: "بلدة مسماة تكتبها أنت، لا إحداثيات أبدًا ولا شيء يُقرأ من عنوان أو IP. الإعلان المصنّف يُرفض له الموقع رفضًا تامًا: مكان الفنان الفعلي لا علاقة له بتصفحه.",
  },
  "sell.place.loc.ph": {
    en: "locality, e.g. Oakland, CA", es: "localidad, p. ej. Oakland, CA", fr: "localité, p. ex. Oakland, CA", de: "Ort, z. B. Oakland, CA", pt: "localidade, p. ex. Oakland, CA", it: "località, es. Oakland, CA", ja: "地名（例: Oakland, CA）", zh: "地名，如 Oakland, CA", hi: "स्थान, जैसे Oakland, CA", ar: "البلدة، مثل Oakland, CA",
  },
  "sell.place.region.ph": {
    en: "region", es: "región", fr: "région", de: "Region", pt: "região", it: "regione", ja: "地域", zh: "地区", hi: "क्षेत्र", ar: "المنطقة",
  },
  "sell.place.remote": {
    en: "also served from anywhere", es: "también se sirve desde cualquier lugar", fr: "aussi servi depuis n'importe où", de: "auch von überall bedient", pt: "também servido de qualquer lugar", it: "servito anche da ovunque", ja: "どこからでも提供可", zh: "也可远程提供", hi: "कहीं से भी सेवा उपलब्ध", ar: "يُقدَّم أيضًا من أي مكان",
  },
  "sell.place.say": {
    en: "Say where it is", es: "Decir dónde está", fr: "Dire où c'est", de: "Sagen, wo es ist", pt: "Dizer onde está", it: "Di' dov'è", ja: "場所を示す", zh: "标明位置", hi: "बताएँ कहाँ है", ar: "قل أين هو",
  },
  "sell.place.clear": {
    en: "Clear the place", es: "Borrar el lugar", fr: "Effacer le lieu", de: "Ort löschen", pt: "Limpar o lugar", it: "Cancella il luogo", ja: "場所を消す", zh: "清除位置", hi: "स्थान हटाएँ", ar: "امسح المكان",
  },
  "desk.title": {
    en: "Desk", es: "Mostrador", fr: "Comptoir", de: "Schalter", pt: "Balcão", it: "Banco", ja: "デスク", zh: "柜台", hi: "डेस्क", ar: "المكتب",
  },
  "desk.open.head": {
    en: "Open a desk", es: "Abrir un mostrador", fr: "Ouvrir un comptoir", de: "Einen Schalter eröffnen", pt: "Abrir um balcão", it: "Apri un banco", ja: "デスクを開く", zh: "开设柜台", hi: "डेस्क खोलें", ar: "افتح مكتبًا",
  },
  "desk.open.pitch": {
    en: "A desk claims a person is behind it, so it is opened with who attests that and on what basis — a guild, a licence number. The claim is shown to every visitor and can be burned, which is why it is asked for at the start rather than added later.", es: "Un mostrador afirma que hay una persona detrás, así que se abre indicando quién lo atestigua y sobre qué base — un gremio, un número de licencia. La afirmación se muestra a cada visitante y puede quemarse, por eso se pide al principio y no se añade después.", fr: "Un comptoir affirme qu'une personne est derrière, il s'ouvre donc avec qui l'atteste et sur quelle base — une guilde, un numéro de licence. L'affirmation est montrée à chaque visiteur et peut être brûlée, c'est pourquoi elle est demandée au départ plutôt qu'ajoutée après.", de: "Ein Schalter behauptet, dass eine Person dahintersteht, also wird er mit der Angabe eröffnet, wer das bezeugt und auf welcher Grundlage — eine Zunft, eine Lizenznummer. Die Behauptung wird jedem Besucher gezeigt und kann verbrannt werden, weshalb sie am Anfang verlangt wird statt später ergänzt.", pt: "Um balcão afirma que há uma pessoa atrás dele, por isso abre-se indicando quem o atesta e com que base — uma guilda, um número de licença. A afirmação é mostrada a cada visitante e pode ser queimada, e é por isso que se pede no início em vez de se acrescentar depois.", it: "Un banco afferma che dietro c'è una persona, quindi si apre indicando chi lo attesta e su quale base — una gilda, un numero di licenza. L'affermazione è mostrata a ogni visitatore e può essere bruciata, per questo viene chiesta all'inizio invece di essere aggiunta dopo.", ja: "デスクは「人がいる」と主張するものです。だから開設時に、誰が何を根拠に証明するのか — 組合、免許番号 — を求めます。この主張はすべての訪問者に示され、焼却されることもあります。後から足すのではなく最初に求めるのはそのためです。", zh: "柜台声称背后有一个人，因此开设时就要写明由谁证明、依据是什么 — 行会、执照号码。这项声明会展示给每位访客，也可能被焚毁，所以在一开始就要求提供，而不是事后补上。", hi: "डेस्क दावा करता है कि उसके पीछे एक व्यक्ति है, इसलिए खोलते समय पूछा जाता है कि कौन इसकी पुष्टि करता है और किस आधार पर — कोई संघ, कोई लाइसेंस नंबर। यह दावा हर आगंतुक को दिखाया जाता है और जलाया भी जा सकता है, इसीलिए इसे बाद में जोड़ने के बजाय शुरू में ही माँगा जाता है।", ar: "المكتب يدّعي أن خلفه شخصًا، لذا يُفتح ببيان من يشهد بذلك وعلى أي أساس — نقابة، رقم رخصة. يُعرض الادعاء على كل زائر ويمكن حرقه، ولهذا يُطلب في البداية بدل إضافته لاحقًا.",
  },
  "desk.open.owner.ph": {
    en: "Your owner id", es: "Tu id de propietario", fr: "Votre id de propriétaire", de: "Ihre Inhaber-Id", pt: "O seu id de proprietário", it: "Il tuo id proprietario", ja: "オーナーID", zh: "你的所有者ID", hi: "आपकी स्वामी आईडी", ar: "معرّف المالك",
  },
  "desk.open.name.ph": {
    en: "Name shown on the desk", es: "Nombre mostrado en el mostrador", fr: "Nom affiché sur le comptoir", de: "Am Schalter gezeigter Name", pt: "Nome mostrado no balcão", it: "Nome mostrato sul banco", ja: "デスクに表示する名前", zh: "柜台上显示的名字", hi: "डेस्क पर दिखने वाला नाम", ar: "الاسم المعروض على المكتب",
  },
  "desk.open.trade.ph": {
    en: "Trade", es: "Oficio", fr: "Métier", de: "Gewerbe", pt: "Ofício", it: "Mestiere", ja: "職種", zh: "行当", hi: "पेशा", ar: "الحرفة",
  },
  "desk.open.attestor.ph": {
    en: "Who attests it", es: "Quién lo atestigua", fr: "Qui l'atteste", de: "Wer es bezeugt", pt: "Quem o atesta", it: "Chi lo attesta", ja: "証明する者", zh: "由谁证明", hi: "कौन पुष्टि करता है", ar: "من يشهد به",
  },
  "desk.open.basis.ph": {
    en: "On what basis", es: "Sobre qué base", fr: "Sur quelle base", de: "Auf welcher Grundlage", pt: "Com que base", it: "Su quale base", ja: "その根拠", zh: "依据是什么", hi: "किस आधार पर", ar: "على أي أساس",
  },
  "desk.open.where.ph": {
    en: "Where (optional)", es: "Dónde (opcional)", fr: "Où (facultatif)", de: "Wo (optional)", pt: "Onde (opcional)", it: "Dove (facoltativo)", ja: "場所（任意）", zh: "地点（可选）", hi: "कहाँ (वैकल्पिक)", ar: "أين (اختياري)",
  },
  "desk.open.go": {
    en: "Open the desk", es: "Abrir el mostrador", fr: "Ouvrir le comptoir", de: "Schalter eröffnen", pt: "Abrir o balcão", it: "Apri il banco", ja: "デスクを開設", zh: "开设此柜台", hi: "डेस्क खोलें", ar: "افتح المكتب",
  },
  "desk.takeup.head": {
    en: "Or take up a desk you already have", es: "O retoma un mostrador que ya tienes", fr: "Ou reprenez un comptoir que vous avez déjà", de: "Oder einen vorhandenen Schalter übernehmen", pt: "Ou retome um balcão que já tem", it: "Oppure riprendi un banco che hai già", ja: "または既存のデスクに就く", zh: "或接手你已有的柜台", hi: "या पहले से मौजूद डेस्क सँभालें", ar: "أو تولَّ مكتبًا لديك بالفعل",
  },
  "desk.takeup.id.ph": {
    en: "Desk id", es: "Id del mostrador", fr: "Id du comptoir", de: "Schalter-Id", pt: "Id do balcão", it: "Id del banco", ja: "デスクID", zh: "柜台ID", hi: "डेस्क आईडी", ar: "معرّف المكتب",
  },
  "desk.takeup.token.ph": {
    en: "Desk token", es: "Token del mostrador", fr: "Jeton du comptoir", de: "Schalter-Token", pt: "Token do balcão", it: "Token del banco", ja: "デスクトークン", zh: "柜台令牌", hi: "डेस्क टोकन", ar: "رمز المكتب",
  },
  "desk.takeup.go": {
    en: "Take it up", es: "Retomarlo", fr: "Le reprendre", de: "Übernehmen", pt: "Retomá-lo", it: "Riprendilo", ja: "就く", zh: "接手", hi: "सँभालें", ar: "تولَّه",
  },
  "desk.rated": {
    en: "rated", es: "clasificado", fr: "classé", de: "bewertet", pt: "classificado", it: "classificato", ja: "レーティング付き", zh: "分级", hi: "रेटेड", ar: "مصنّف",
  },
  "desk.view.alt": {
    en: "the view from this desk", es: "la vista desde este mostrador", fr: "la vue depuis ce comptoir", de: "der Blick von diesem Schalter", pt: "a vista deste balcão", it: "la vista da questo banco", ja: "このデスクからの眺め", zh: "此柜台的画面", hi: "इस डेस्क से दृश्य", ar: "المشهد من هذا المكتب",
  },
  "desk.there.head": {
    en: "Is anybody there?", es: "¿Hay alguien ahí?", fr: "Y a-t-il quelqu'un ?", de: "Ist jemand da?", pt: "Está alguém aí?", it: "C'è qualcuno?", ja: "誰かいますか？", zh: "有人在吗？", hi: "क्या कोई है?", ar: "هل من أحد هناك؟",
  },
  "desk.there.pitch": {
    en: "The one thing a visitor most wants to know. Away says come back; closed says the counter is shut. They are different promises and the desk gets to make either.", es: "Lo que un visitante más quiere saber. «away» dice vuelve luego; «closed» dice que el mostrador está cerrado. Son promesas distintas y el mostrador puede hacer cualquiera.", fr: "La chose qu'un visiteur veut le plus savoir. « away » dit revenez ; « closed » dit que le comptoir est fermé. Ce sont des promesses différentes et le comptoir peut faire l'une ou l'autre.", de: "Das eine, was ein Besucher am meisten wissen will. »away« sagt komm wieder; »closed« sagt, der Schalter ist zu. Das sind verschiedene Versprechen, und der Schalter darf beide geben.", pt: "O que um visitante mais quer saber. «away» diz volte depois; «closed» diz que o balcão está fechado. São promessas diferentes e o balcão pode fazer qualquer uma.", it: "La cosa che un visitatore vuole sapere più di tutte. «away» dice torna dopo; «closed» dice che il banco è chiuso. Sono promesse diverse e il banco può fare l'una o l'altra.", ja: "訪問者が最も知りたいこと。「away」はまた来てくださいを、「closed」はカウンターが閉まっていることを意味します。異なる約束であり、デスクはどちらも選べます。", zh: "访客最想知道的一件事。「away」表示请再来；「closed」表示柜台已关。这是两种不同的承诺，柜台可以任选其一。", hi: "आगंतुक सबसे पहले यही जानना चाहता है। «away» कहता है फिर आना; «closed» कहता है काउंटर बंद है। ये अलग-अलग वादे हैं और डेस्क कोई भी कर सकता है।", ar: "أكثر ما يريد الزائر معرفته. «away» تقول عُد لاحقًا؛ و«closed» تقول إن المنضدة مغلقة. وعدان مختلفان وللمكتب أن يقطع أيًا منهما.",
  },
  "desk.bell.head": {
    en: "The bell", es: "El timbre", fr: "La sonnette", de: "Die Klingel", pt: "A campainha", it: "Il campanello", ja: "ベル", zh: "门铃", hi: "घंटी", ar: "الجرس",
  },
  "desk.bell.none": {
    en: "Nobody has rung.", es: "Nadie ha llamado.", fr: "Personne n'a sonné.", de: "Niemand hat geklingelt.", pt: "Ninguém tocou.", it: "Nessuno ha suonato.", ja: "誰も鳴らしていません。", zh: "无人按铃。", hi: "किसी ने घंटी नहीं बजाई।", ar: "لم يقرع أحد.",
  },
  "desk.bell.answered": {
    en: "answered", es: "atendido", fr: "répondu", de: "beantwortet", pt: "atendido", it: "risposto", ja: "応答済み", zh: "已应答", hi: "उत्तर दिया", ar: "أُجيب",
  },
  "desk.bell.answer": {
    en: "Answer", es: "Atender", fr: "Répondre", de: "Antworten", pt: "Atender", it: "Rispondi", ja: "応答", zh: "应答", hi: "उत्तर दें", ar: "أجب",
  },
  "desk.guests.head": {
    en: "Who wants to come up", es: "Quién quiere subir", fr: "Qui veut monter", de: "Wer heraufkommen will", pt: "Quem quer subir", it: "Chi vuole salire", ja: "上がりたい人", zh: "谁想上来", hi: "कौन ऊपर आना चाहता है", ar: "من يريد الصعود",
  },
  "desk.guests.none": {
    en: "Nobody waiting.", es: "Nadie esperando.", fr: "Personne n'attend.", de: "Niemand wartet.", pt: "Ninguém à espera.", it: "Nessuno in attesa.", ja: "待っている人はいません。", zh: "无人等待。", hi: "कोई प्रतीक्षा में नहीं।", ar: "لا أحد ينتظر.",
  },
  "desk.guests.up": {
    en: "Let them up", es: "Déjales subir", fr: "Les laisser monter", de: "Herauflassen", pt: "Deixá-los subir", it: "Falli salire", ja: "上がってもらう", zh: "让他们上来", hi: "उन्हें ऊपर आने दें", ar: "دعهم يصعدون",
  },
  "desk.guests.no": {
    en: "Not now", es: "Ahora no", fr: "Pas maintenant", de: "Jetzt nicht", pt: "Agora não", it: "Non ora", ja: "今は無理", zh: "现在不行", hi: "अभी नहीं", ar: "ليس الآن",
  },
  "desk.stream.head": {
    en: "On the stream", es: "En la transmisión", fr: "Sur le flux", de: "Im Stream", pt: "Na transmissão", it: "In diretta", ja: "配信中", zh: "直播中", hi: "स्ट्रीम पर", ar: "على البث",
  },
  "desk.stream.line": {
    en: "{up} up, {waiting} waiting · {likes} likes · {comments} comments · {shares} shares{gifts} · drawn over the picture at {pct}%, {anchor}", es: "{up} arriba, {waiting} esperando · {likes} me gusta · {comments} comentarios · {shares} compartidos{gifts} · dibujado sobre la imagen al {pct}%, {anchor}", fr: "{up} en haut, {waiting} en attente · {likes} j'aime · {comments} commentaires · {shares} partages{gifts} · dessiné sur l'image à {pct}%, {anchor}", de: "{up} oben, {waiting} wartend · {likes} Likes · {comments} Kommentare · {shares} geteilt{gifts} · über das Bild gezeichnet bei {pct}%, {anchor}", pt: "{up} em cima, {waiting} à espera · {likes} gostos · {comments} comentários · {shares} partilhas{gifts} · desenhado sobre a imagem a {pct}%, {anchor}", it: "{up} su, {waiting} in attesa · {likes} mi piace · {comments} commenti · {shares} condivisioni{gifts} · disegnato sull'immagine al {pct}%, {anchor}", ja: "{up}人が参加、{waiting}人待機 · いいね{likes} · コメント{comments} · シェア{shares}{gifts} · 画像上に{pct}%で描画、{anchor}", zh: "{up}人在线，{waiting}人等待 · {likes}赞 · {comments}评论 · {shares}分享{gifts} · 以{pct}%叠加在画面上，{anchor}", hi: "{up} ऊपर, {waiting} प्रतीक्षा में · {likes} पसंद · {comments} टिप्पणियाँ · {shares} साझा{gifts} · चित्र पर {pct}% पर आरेखित, {anchor}", ar: "{up} فوق، {waiting} ينتظرون · {likes} إعجابًا · {comments} تعليقًا · {shares} مشاركة{gifts} · مرسوم فوق الصورة بنسبة {pct}٪، {anchor}",
  },
  "desk.stream.down": {
    en: "Step down from the stream", es: "Bajarse de la transmisión", fr: "Se retirer du flux", de: "Aus dem Stream aussteigen", pt: "Sair da transmissão", it: "Scendi dalla diretta", ja: "配信から降りる", zh: "退出直播", hi: "स्ट्रीम से उतरें", ar: "انزل من البث",
  },
  "desk.look.head": {
    en: "Look and camera", es: "Aspecto y cámara", fr: "Apparence et caméra", de: "Aussehen und Kamera", pt: "Aspeto e câmara", it: "Aspetto e camera", ja: "外観とカメラ", zh: "外观与摄像头", hi: "रूप और कैमरा", ar: "المظهر والكاميرا",
  },
  "desk.look.portrait.ph": {
    en: "Portrait asset", es: "Recurso de retrato", fr: "Ressource de portrait", de: "Porträt-Asset", pt: "Recurso de retrato", it: "Risorsa ritratto", ja: "ポートレート素材", zh: "肖像素材", hi: "पोर्ट्रेट एसेट", ar: "أصل الصورة الشخصية",
  },
  "desk.look.set": {
    en: "Set portrait", es: "Fijar retrato", fr: "Définir le portrait", de: "Porträt setzen", pt: "Definir retrato", it: "Imposta ritratto", ja: "ポートレートを設定", zh: "设置肖像", hi: "पोर्ट्रेट लगाएँ", ar: "عيّن الصورة",
  },
  "desk.look.clear": {
    en: "Clear camera", es: "Quitar cámara", fr: "Retirer la caméra", de: "Kamera entfernen", pt: "Limpar câmara", it: "Rimuovi camera", ja: "カメラを外す", zh: "清除摄像头", hi: "कैमरा हटाएँ", ar: "امسح الكاميرا",
  },
  "desk.beacons.head": {
    en: "Beacons", es: "Balizas", fr: "Balises", de: "Baken", pt: "Balizas", it: "Beacon", ja: "ビーコン", zh: "信标", hi: "बीकन", ar: "المنارات",
  },
  "desk.beacons.pitch": {
    en: "The desk as a sticker: somebody scans it in the street and reaches this counter. Picking one up retires it — the sticker on the wall stops working, which is the point.", es: "El mostrador como pegatina: alguien la escanea en la calle y llega a este mostrador. Recogerla la retira — la pegatina en la pared deja de funcionar, que es justo la idea.", fr: "Le comptoir en autocollant : quelqu'un le scanne dans la rue et atteint ce guichet. Le ramasser le retire — l'autocollant au mur cesse de fonctionner, et c'est le but.", de: "Der Schalter als Aufkleber: jemand scannt ihn auf der Straße und erreicht diesen Tresen. Ihn aufzuheben zieht ihn zurück — der Aufkleber an der Wand hört auf zu funktionieren, und genau das ist der Sinn.", pt: "O balcão como autocolante: alguém o digitaliza na rua e chega a este balcão. Apanhá-lo retira-o — o autocolante na parede deixa de funcionar, e é essa a ideia.", it: "Il banco come adesivo: qualcuno lo scansiona per strada e raggiunge questo bancone. Raccoglierlo lo ritira — l'adesivo sul muro smette di funzionare, ed è proprio il punto.", ja: "デスクをステッカーに：街で誰かがスキャンするとこのカウンターに届きます。回収すると引退します — 壁のステッカーは機能しなくなり、それこそが狙いです。", zh: "柜台化作贴纸：有人在街上扫一下就能到达这个柜台。收回它即让它退役 — 墙上的贴纸随即失效，这正是目的所在。", hi: "डेस्क एक स्टिकर के रूप में: कोई सड़क पर उसे स्कैन करता है और इस काउंटर तक पहुँचता है। उठा लेने से वह सेवानिवृत्त हो जाता है — दीवार का स्टिकर काम करना बंद कर देता है, और यही उद्देश्य है।", ar: "المكتب كملصق: يمسحه أحدهم في الشارع فيصل إلى هذه المنضدة. التقاطه يقاعده — يتوقف الملصق على الجدار عن العمل، وهذا هو المقصود.",
  },
  "desk.beacons.scans": {
    en: "{n} scan{s}", es: "{n} escaneos", fr: "{n} scans", de: "{n} Scans", pt: "{n} digitalizações", it: "{n} scansioni", ja: "スキャン{n}件", zh: "{n}次扫描", hi: "{n} स्कैन", ar: "{n} مسحة",
  },
  "desk.beacons.retired": {
    en: "retired", es: "retirada", fr: "retirée", de: "zurückgezogen", pt: "retirada", it: "ritirato", ja: "引退済み", zh: "已退役", hi: "सेवानिवृत्त", ar: "متقاعد",
  },
  "desk.beacons.qr.alt": {
    en: "this desk code's QR", es: "el QR del código de este mostrador", fr: "le QR du code de ce comptoir", de: "der QR dieses Schalter-Codes", pt: "o QR do código deste balcão", it: "il QR del codice di questo banco", ja: "このデスクコードのQR", zh: "此柜台代码的二维码", hi: "इस डेस्क कोड का QR", ar: "رمز QR لهذا المكتب",
  },
  "desk.beacons.open": {
    en: "open it here (counts as a scan)", es: "abrirlo aquí (cuenta como escaneo)", fr: "l'ouvrir ici (compte comme un scan)", de: "hier öffnen (zählt als Scan)", pt: "abrir aqui (conta como digitalização)", it: "aprilo qui (conta come scansione)", ja: "ここで開く（スキャンとして数えます）", zh: "在此打开（计为一次扫描）", hi: "यहाँ खोलें (स्कैन के रूप में गिना जाएगा)", ar: "افتحه هنا (يُحسب مسحة)",
  },
  "desk.beacons.printed": {
    en: "Printed:", es: "Impreso:", fr: "Imprimé :", de: "Gedruckt:", pt: "Impresso:", it: "Stampato:", ja: "印刷内容：", zh: "印制内容：", hi: "मुद्रित:", ar: "المطبوع:",
  },
  "desk.beacons.card": {
    en: "What a scanner sees", es: "Lo que ve quien escanea", fr: "Ce que voit le scanneur", de: "Was ein Scanner sieht", pt: "O que vê quem digitaliza", it: "Cosa vede chi scansiona", ja: "スキャンした人に見えるもの", zh: "扫描者看到的内容", hi: "स्कैन करने वाले को क्या दिखता है", ar: "ما يراه الماسح",
  },
  "desk.beacons.pickup": {
    en: "Pick it up", es: "Recogerla", fr: "Le ramasser", de: "Aufheben", pt: "Apanhá-la", it: "Raccoglilo", ja: "回収する", zh: "收回", hi: "उठा लें", ar: "التقطه",
  },
  "desk.beacons.label.ph": {
    en: "Label (Shop window)", es: "Etiqueta (Escaparate)", fr: "Étiquette (Vitrine)", de: "Beschriftung (Schaufenster)", pt: "Etiqueta (Montra)", it: "Etichetta (Vetrina)", ja: "ラベル（ショーウィンドウ）", zh: "标签（橱窗）", hi: "लेबल (दुकान की खिड़की)", ar: "التسمية (واجهة المتجر)",
  },
  "desk.beacons.place": {
    en: "Place a beacon", es: "Colocar una baliza", fr: "Poser une balise", de: "Eine Bake platzieren", pt: "Colocar uma baliza", it: "Colloca un beacon", ja: "ビーコンを設置", zh: "放置信标", hi: "बीकन रखें", ar: "ضع منارة",
  },
  "desk.card.agewall": {
    en: "This desk is rated, so a scan lands on the age wall. A sticker carries no token that could clear it — that is the right answer rather than a gap.", es: "Este mostrador está clasificado, así que un escaneo cae en el muro de edad. Una pegatina no lleva token que pueda superarlo — esa es la respuesta correcta, no un hueco.", fr: "Ce comptoir est classé, donc un scan tombe sur le mur d'âge. Un autocollant ne porte aucun jeton qui pourrait le franchir — c'est la bonne réponse, pas une lacune.", de: "Dieser Schalter ist bewertet, also landet ein Scan auf der Alterswand. Ein Aufkleber trägt kein Token, das sie überwinden könnte — das ist die richtige Antwort, keine Lücke.", pt: "Este balcão é classificado, por isso uma digitalização cai no muro de idade. Um autocolante não carrega token que o possa passar — essa é a resposta certa, não uma falha.", it: "Questo banco è classificato, quindi una scansione finisce sul muro dell'età. Un adesivo non porta alcun token che possa superarlo — quella è la risposta giusta, non una lacuna.", ja: "このデスクはレーティング付きのため、スキャンは年齢の壁に着地します。ステッカーはそれを通過できるトークンを持ちません — それは欠陥ではなく正しい答えです。", zh: "此柜台已分级，因此扫描会落在年龄墙上。贴纸不携带任何能通过它的令牌 — 这是正确的答案，而非缺口。", hi: "यह डेस्क रेटेड है, इसलिए स्कैन आयु-दीवार पर उतरता है। स्टिकर में ऐसा कोई टोकन नहीं जो उसे पार कर सके — यही सही उत्तर है, कोई कमी नहीं।", ar: "هذا المكتب مصنّف، فيهبط المسح على جدار العمر. الملصق لا يحمل رمزًا يجتازه — وهذا هو الجواب الصحيح لا ثغرة.",
  },
  "desk.card.attested": {
    en: "Attested by {who}: {basis}. {note}", es: "Atestiguado por {who}: {basis}. {note}", fr: "Attesté par {who} : {basis}. {note}", de: "Bezeugt von {who}: {basis}. {note}", pt: "Atestado por {who}: {basis}. {note}", it: "Attestato da {who}: {basis}. {note}", ja: "{who}による証明：{basis}。{note}", zh: "由{who}证明：{basis}。{note}", hi: "{who} द्वारा पुष्टि: {basis}। {note}", ar: "شهد به {who}: {basis}. {note}",
  },
  "desk.card.counted": {
    en: "That read counted as a scan.", es: "Esa lectura contó como escaneo.", fr: "Cette lecture a compté comme un scan.", de: "Dieses Lesen zählte als Scan.", pt: "Essa leitura contou como digitalização.", it: "Quella lettura è contata come scansione.", ja: "この閲覧は1回のスキャンとして数えられました。", zh: "这次读取已计为一次扫描。", hi: "यह पढ़ना एक स्कैन के रूप में गिना गया।", ar: "حُسبت تلك القراءة مسحة.",
  },
  "ref.title": {
    en: "Handing it to somebody qualified", es: "Entregarlo a alguien cualificado", fr: "Le remettre à quelqu'un de qualifié", de: "Übergabe an jemand Qualifizierten", pt: "Entregá-lo a alguém qualificado", it: "Consegnarlo a qualcuno di qualificato", ja: "資格ある人へ手渡す", zh: "交给有资质的人", hi: "किसी योग्य व्यक्ति को सौंपना", ar: "تسليمه إلى مؤهل",
  },
  "ref.lead": {
    en: "A profile is not a clinician. This is how a conversation with one reaches somebody who is — once, and only under your signature.", es: "Un perfil no es un clínico. Así es como una conversación con uno llega a alguien que sí lo es — una vez, y solo bajo tu firma.", fr: "Un profil n'est pas un clinicien. Voici comment une conversation avec l'un parvient à quelqu'un qui l'est — une fois, et seulement sous votre signature.", de: "Ein Profil ist kein Kliniker. So erreicht ein Gespräch mit einem jemanden, der einer ist — einmal, und nur unter Ihrer Unterschrift.", pt: "Um perfil não é um clínico. É assim que uma conversa com um chega a alguém que o é — uma vez, e só sob a sua assinatura.", it: "Un profilo non è un clinico. È così che una conversazione con uno arriva a qualcuno che lo è — una volta, e solo sotto la tua firma.", ja: "プロフィールは臨床医ではありません。これは、プロフィールとの会話を本物の臨床医へ届ける方法です — 一度だけ、あなたの署名の下でのみ。", zh: "资料并非临床医生。这就是让与它的对话抵达真正医生的方式 — 仅一次，且必须经你签名。", hi: "प्रोफ़ाइल चिकित्सक नहीं है। यह वह तरीक़ा है जिससे उसके साथ की बातचीत किसी असली चिकित्सक तक पहुँचती है — एक बार, और केवल आपके हस्ताक्षर के तहत।", ar: "الملف ليس طبيبًا سريريًا. هكذا تصل محادثة معه إلى من هو كذلك — مرة واحدة، وتحت توقيعك فقط.",
  },
  "ref.find": {
    en: "Who can help", es: "Quién puede ayudar", fr: "Qui peut aider", de: "Wer helfen kann", pt: "Quem pode ajudar", it: "Chi può aiutare", ja: "助けられる人", zh: "谁能帮忙", hi: "कौन मदद कर सकता है", ar: "من يستطيع المساعدة",
  },
  "ref.find.pitch": {
    en: "Expertise filters and geography ranks, never the other way round — a cardiologist two streets away is not a substitute for a psychiatrist. An empty list is an answer.", es: "La especialidad filtra y la geografía ordena, nunca al revés — un cardiólogo a dos calles no sustituye a un psiquiatra. Una lista vacía es una respuesta.", fr: "L'expertise filtre et la géographie classe, jamais l'inverse — un cardiologue à deux rues ne remplace pas un psychiatre. Une liste vide est une réponse.", de: "Fachgebiet filtert und Geografie sortiert, nie umgekehrt — ein Kardiologe zwei Straßen weiter ersetzt keinen Psychiater. Eine leere Liste ist eine Antwort.", pt: "A especialidade filtra e a geografia ordena, nunca ao contrário — um cardiologista a duas ruas não substitui um psiquiatra. Uma lista vazia é uma resposta.", it: "La specialità filtra e la geografia ordina, mai il contrario — un cardiologo a due strade non sostituisce uno psichiatra. Una lista vuota è una risposta.", ja: "専門で絞り、地理で並べる — 逆は決してしません。二筋先の循環器医は精神科医の代わりになりません。空のリストもひとつの答えです。", zh: "专长过滤，地理排序，绝不颠倒 — 两条街外的心脏科医生替代不了精神科医生。空列表也是一种回答。", hi: "विशेषज्ञता छानती है और भूगोल क्रम देता है, कभी उलटा नहीं — दो गली दूर का हृदय-रोग विशेषज्ञ मनोचिकित्सक का विकल्प नहीं। खाली सूची भी एक उत्तर है।", ar: "التخصص يرشّح والجغرافيا ترتّب، لا العكس أبدًا — طبيب قلب على بعد شارعين ليس بديلًا عن طبيب نفسي. القائمة الفارغة جواب.",
  },
  "ref.find.area.ph": {
    en: "what you need, e.g. physiotherapy", es: "lo que necesitas, p. ej. fisioterapia", fr: "ce dont vous avez besoin, p. ex. kinésithérapie", de: "was Sie brauchen, z. B. Physiotherapie", pt: "o que precisa, p. ex. fisioterapia", it: "ciò che ti serve, es. fisioterapia", ja: "必要なもの（例: 理学療法）", zh: "你需要什么，如物理治疗", hi: "आपको क्या चाहिए, जैसे फ़िज़ियोथेरेपी", ar: "ما تحتاجه، مثل العلاج الطبيعي",
  },
  "ref.find.where.ph": {
    en: "where you are", es: "dónde estás", fr: "où vous êtes", de: "wo Sie sind", pt: "onde está", it: "dove sei", ja: "あなたの居場所", zh: "你在哪里", hi: "आप कहाँ हैं", ar: "أين أنت",
  },
  "ref.find.go": {
    en: "Find", es: "Buscar", fr: "Chercher", de: "Suchen", pt: "Procurar", it: "Cerca", ja: "探す", zh: "查找", hi: "खोजें", ar: "ابحث",
  },
  "ref.find.none": {
    en: "Nobody listed for that yet — which is said plainly rather than offering a near-miss.", es: "Nadie listado para eso todavía — lo cual se dice claramente en vez de ofrecer un casi-acierto.", fr: "Personne d'inscrit pour cela encore — ce qui est dit clairement plutôt que d'offrir un à-peu-près.", de: "Dafür ist noch niemand gelistet — was klar gesagt wird, statt einen Beinahe-Treffer anzubieten.", pt: "Ninguém listado para isso ainda — o que se diz claramente em vez de oferecer um quase-acerto.", it: "Nessuno in elenco per questo ancora — il che viene detto chiaramente invece di offrire un quasi-risultato.", ja: "まだ該当者はいません — 近い候補を出すのではなく、そのまま率直に伝えます。", zh: "尚无人登记该项 — 直说无人，而非给出近似的替代。", hi: "इसके लिए अभी कोई सूचीबद्ध नहीं — जो साफ़ कहा जाता है, बजाय मिलते-जुलते विकल्प देने के।", ar: "لا أحد مدرج لذلك بعد — ويُقال ذلك بوضوح بدل تقديم شبه تطابق.",
  },
  "ref.find.matched": {
    en: "matched on", es: "coincide en", fr: "correspond sur", de: "passt auf", pt: "corresponde em", it: "corrisponde su", ja: "一致項目:", zh: "匹配依据:", hi: "मिलान आधार:", ar: "تطابق على",
  },
  "ref.find.prepare": {
    en: "Prepare", es: "Preparar", fr: "Préparer", de: "Vorbereiten", pt: "Preparar", it: "Prepara", ja: "準備", zh: "准备", hi: "तैयार करें", ar: "جهّز",
  },
  "ref.find.dir": {
    en: "The directory — {n} {word} listed", es: "El directorio — {n} en la lista", fr: "L'annuaire — {n} inscrits", de: "Das Verzeichnis — {n} gelistet", pt: "O diretório — {n} listados", it: "L'elenco — {n} in lista", ja: "名簿 — {n}名掲載", zh: "名录 — 已列{n}人", hi: "निर्देशिका — {n} सूचीबद्ध", ar: "الدليل — {n} مدرجون",
  },
  "ref.add.name.ph": {
    en: "name", es: "nombre", fr: "nom", de: "Name", pt: "nome", it: "nome", ja: "名前", zh: "姓名", hi: "नाम", ar: "الاسم",
  },
  "ref.add.area.ph": {
    en: "area of expertise", es: "área de especialidad", fr: "domaine d'expertise", de: "Fachgebiet", pt: "área de especialidade", it: "area di competenza", ja: "専門分野", zh: "专长领域", hi: "विशेषज्ञता का क्षेत्र", ar: "مجال الخبرة",
  },
  "ref.add.where.ph": {
    en: "where", es: "dónde", fr: "où", de: "wo", pt: "onde", it: "dove", ja: "場所", zh: "地点", hi: "कहाँ", ar: "أين",
  },
  "ref.add.contact.ph": {
    en: "how to reach them", es: "cómo contactarle", fr: "comment le joindre", de: "wie man sie erreicht", pt: "como contactá-lo", it: "come raggiungerlo", ja: "連絡方法", zh: "如何联系", hi: "उन तक कैसे पहुँचें", ar: "كيف تصل إليه",
  },
  "ref.add.go": {
    en: "Add", es: "Añadir", fr: "Ajouter", de: "Hinzufügen", pt: "Adicionar", it: "Aggiungi", ja: "追加", zh: "添加", hi: "जोड़ें", ar: "أضف",
  },
  "ref.sign": {
    en: "Read this before you sign", es: "Lee esto antes de firmar", fr: "Lisez ceci avant de signer", de: "Lesen Sie das, bevor Sie unterschreiben", pt: "Leia isto antes de assinar", it: "Leggi questo prima di firmare", ja: "署名する前に読んでください", zh: "签名前请阅读", hi: "हस्ताक्षर से पहले इसे पढ़ें", ar: "اقرأ هذا قبل أن توقّع",
  },
  "ref.sign.nothing": {
    en: "Nothing has gone anywhere yet. This is what would.", es: "Nada ha salido a ningún sitio todavía. Esto es lo que saldría.", fr: "Rien n'est encore parti nulle part. Voici ce qui partirait.", de: "Noch ist nichts irgendwohin gegangen. Das hier würde gehen.", pt: "Nada foi para lado nenhum ainda. Isto é o que iria.", it: "Niente è ancora andato da nessuna parte. Questo è ciò che andrebbe.", ja: "まだ何もどこへも送られていません。送られるとすればこれです。", zh: "尚未有任何内容发出。要发出的就是这些。", hi: "अभी कुछ भी कहीं नहीं गया। जाएगा तो यह जाएगा।", ar: "لم يذهب شيء إلى أي مكان بعد. هذا ما سيذهب.",
  },
  "ref.sign.summary": {
    en: "The summary", es: "El resumen", fr: "Le résumé", de: "Die Zusammenfassung", pt: "O resumo", it: "Il riepilogo", ja: "要約", zh: "摘要", hi: "सारांश", ar: "الملخص",
  },
  "ref.sign.hash": {
    en: "The signature is over these exact words — the challenge is their hash — so a summary changed afterwards cannot ride it.", es: "La firma cubre exactamente estas palabras — el desafío es su hash — así que un resumen cambiado después no puede aprovecharla.", fr: "La signature porte sur ces mots exacts — le défi est leur empreinte — donc un résumé modifié ensuite ne peut pas s'en servir.", de: "Die Unterschrift gilt genau diesen Worten — die Challenge ist ihr Hash — also kann eine später geänderte Zusammenfassung nicht auf ihr reiten.", pt: "A assinatura cobre exatamente estas palavras — o desafio é o seu hash — pelo que um resumo alterado depois não pode aproveitá-la.", it: "La firma copre esattamente queste parole — la challenge è il loro hash — quindi un riepilogo cambiato dopo non può cavalcarla.", ja: "署名はこの正確な文言に対して行われます — チャレンジはそのハッシュです — 後から変更された要約が署名に便乗することはできません。", zh: "签名覆盖的正是这些原话 — 挑战值是它们的哈希 — 因此事后改动的摘要无法搭上这个签名。", hi: "हस्ताक्षर ठीक इन्हीं शब्दों पर है — चुनौती उनका हैश है — इसलिए बाद में बदला गया सारांश उस पर सवार नहीं हो सकता।", ar: "التوقيع على هذه الكلمات بعينها — التحدي هو تجزئتها — فالملخص المعدل لاحقًا لا يمكنه ركوبه.",
  },
  "ref.sign.go": {
    en: "Sign it with your device", es: "Fírmalo con tu dispositivo", fr: "Signez-le avec votre appareil", de: "Mit Ihrem Gerät unterschreiben", pt: "Assine com o seu dispositivo", it: "Firmalo con il tuo dispositivo", ja: "デバイスで署名する", zh: "用你的设备签名", hi: "अपने डिवाइस से हस्ताक्षर करें", ar: "وقّعه بجهازك",
  },
  "ref.sign.sid.ph": {
    en: "the signature id the ceremony gave back", es: "el id de firma que devolvió la ceremonia", fr: "l'id de signature rendu par la cérémonie", de: "die Signatur-Id, die die Zeremonie zurückgab", pt: "o id de assinatura que a cerimónia devolveu", it: "l'id di firma restituito dalla cerimonia", ja: "セレモニーが返した署名ID", zh: "仪式返回的签名ID", hi: "समारोह से मिली हस्ताक्षर आईडी", ar: "معرّف التوقيع الذي أعادته المراسم",
  },
  "ref.sign.release": {
    en: "Release it", es: "Liberarlo", fr: "Le libérer", de: "Freigeben", pt: "Libertá-lo", it: "Rilascialo", ja: "リリースする", zh: "放行", hi: "जारी करें", ar: "أطلقه",
  },
  "ref.link": {
    en: "The link for the clinician", es: "El enlace para el clínico", fr: "Le lien pour le clinicien", de: "Der Link für den Kliniker", pt: "O link para o clínico", it: "Il link per il clinico", ja: "臨床医向けのリンク", zh: "给医生的链接", hi: "चिकित्सक के लिए लिंक", ar: "الرابط للطبيب",
  },
  "ref.link.once": {
    en: "It opens once. A second attempt fails with the time of the first, rather than quietly working — a replayed link is something you should be able to find out about.", es: "Se abre una vez. Un segundo intento falla mostrando la hora del primero, en vez de funcionar en silencio — un enlace reutilizado es algo que deberías poder descubrir.", fr: "Il s'ouvre une fois. Une seconde tentative échoue avec l'heure de la première, plutôt que de marcher en silence — un lien rejoué est une chose que vous devez pouvoir découvrir.", de: "Er öffnet sich einmal. Ein zweiter Versuch scheitert mit der Zeit des ersten, statt still zu funktionieren — ein wiederverwendeter Link ist etwas, das Sie erfahren können sollten.", pt: "Abre uma vez. Uma segunda tentativa falha com a hora da primeira, em vez de funcionar em silêncio — um link repetido é algo que deve poder descobrir.", it: "Si apre una volta. Un secondo tentativo fallisce con l'ora del primo, invece di funzionare in silenzio — un link riusato è qualcosa che dovresti poter scoprire.", ja: "一度だけ開きます。二度目の試みは最初に開かれた時刻とともに失敗します。静かに動いたりはしません — 再利用されたリンクは、あなたが気づけるべきものだからです。", zh: "它只打开一次。第二次尝试会带着第一次的时间失败，而不是悄悄生效 — 被重放的链接是你应当能够察觉的事。", hi: "यह एक बार खुलता है। दूसरा प्रयास पहली बार के समय के साथ विफल होता है, चुपचाप काम नहीं करता — दोहराया गया लिंक ऐसी चीज़ है जिसका आपको पता चल सकना चाहिए।", ar: "يفتح مرة واحدة. المحاولة الثانية تفشل مع وقت الأولى بدل أن تعمل بصمت — الرابط المعاد تشغيله شيء ينبغي أن تستطيع اكتشافه.",
  },
  "ref.creds": {
    en: "Your signing credentials", es: "Tus credenciales de firma", fr: "Vos identifiants de signature", de: "Ihre Signatur-Berechtigungen", pt: "As suas credenciais de assinatura", it: "Le tue credenziali di firma", ja: "署名クレデンシャル", zh: "你的签名凭证", hi: "आपके हस्ताक्षर क्रेडेंशियल", ar: "بيانات توقيعك",
  },
  "ref.creds.pitch": {
    en: "A referral is a high-tier signature. What a credential can sign follows from how your identity was checked, and from whether the key stayed on one device.", es: "Un volante es una firma de nivel «high». Lo que una credencial puede firmar se sigue de cómo se verificó tu identidad, y de si la clave permaneció en un solo dispositivo.", fr: "Une orientation est une signature de niveau « high ». Ce qu'un identifiant peut signer découle de la façon dont votre identité a été vérifiée, et de si la clé est restée sur un seul appareil.", de: "Eine Überweisung ist eine Unterschrift der Stufe »high«. Was eine Berechtigung unterschreiben darf, folgt daraus, wie Ihre Identität geprüft wurde und ob der Schlüssel auf einem Gerät blieb.", pt: "Um encaminhamento é uma assinatura de nível «high». O que uma credencial pode assinar decorre de como a sua identidade foi verificada, e de se a chave ficou num só dispositivo.", it: "Un invio è una firma di livello «high». Ciò che una credenziale può firmare segue da come è stata verificata la tua identità, e da se la chiave è rimasta su un solo dispositivo.", ja: "紹介は「high」層の署名です。クレデンシャルが何に署名できるかは、本人確認の方法と、鍵が一台の端末に留まったかどうかで決まります。", zh: "转诊是「high」级签名。凭证能签什么，取决于你的身份如何核验、密钥是否只留在一台设备上。", hi: "रेफ़रल «high» स्तर का हस्ताक्षर है। क्रेडेंशियल क्या साइन कर सकता है, यह इस पर निर्भर है कि आपकी पहचान कैसे जाँची गई और कुंजी एक ही डिवाइस पर रही या नहीं।", ar: "الإحالة توقيع من مستوى «high». ما يمكن للاعتماد توقيعه يتبع كيفية التحقق من هويتك، وهل بقي المفتاح على جهاز واحد.",
  },
  "ref.creds.none": {
    en: "None enrolled. The ceremony can enrol one.", es: "Ninguna inscrita. La ceremonia puede inscribir una.", fr: "Aucun enrôlé. La cérémonie peut en enrôler un.", de: "Keine registriert. Die Zeremonie kann eine registrieren.", pt: "Nenhuma inscrita. A cerimónia pode inscrever uma.", it: "Nessuna registrata. La cerimonia può registrarne una.", ja: "未登録です。セレモニーで登録できます。", zh: "尚未注册。可通过仪式注册一个。", hi: "कोई नामांकित नहीं। समारोह एक नामांकित कर सकता है।", ar: "لا شيء مسجل. يمكن للمراسم تسجيل واحد.",
  },
  "ref.creds.checked": {
    en: "{name} — checked as {level}", es: "{name} — verificada como {level}", fr: "{name} — vérifié comme {level}", de: "{name} — geprüft als {level}", pt: "{name} — verificada como {level}", it: "{name} — verificata come {level}", ja: "{name} — {level}として確認済み", zh: "{name} — 核验为{level}", hi: "{name} — {level} के रूप में जाँची गई", ar: "{name} — تم التحقق كـ{level}",
  },
  "ref.creds.syncs": {
    en: "· syncs between devices", es: "· se sincroniza entre dispositivos", fr: "· se synchronise entre appareils", de: "· synchronisiert zwischen Geräten", pt: "· sincroniza entre dispositivos", it: "· si sincronizza tra dispositivi", ja: "· 端末間で同期", zh: "· 在设备间同步", hi: "· डिवाइसों के बीच सिंक होती है", ar: "· يتزامن بين الأجهزة",
  },
  "ref.creds.cansign": {
    en: "Can sign:", es: "Puede firmar:", fr: "Peut signer :", de: "Darf unterschreiben:", pt: "Pode assinar:", it: "Può firmare:", ja: "署名可能:", zh: "可签署:", hi: "साइन कर सकती है:", ar: "يمكنه التوقيع:",
  },
  "ref.creds.attestor.ph": {
    en: "who checked it", es: "quién lo verificó", fr: "qui l'a vérifié", de: "wer es prüfte", pt: "quem verificou", it: "chi l'ha verificato", ja: "確認した者", zh: "由谁核验", hi: "किसने जाँचा", ar: "من تحقق منه",
  },
  "ref.creds.record": {
    en: "Record a check", es: "Registrar una verificación", fr: "Enregistrer une vérification", de: "Prüfung erfassen", pt: "Registar uma verificação", it: "Registra una verifica", ja: "確認を記録", zh: "记录一次核验", hi: "जाँच दर्ज करें", ar: "سجّل تحققًا",
  },
  "ref.hist": {
    en: "What you have released", es: "Lo que has liberado", fr: "Ce que vous avez libéré", de: "Was Sie freigegeben haben", pt: "O que libertou", it: "Ciò che hai rilasciato", ja: "リリース済みのもの", zh: "你已放行的内容", hi: "आपने जो जारी किया", ar: "ما أطلقته",
  },
  "ref.hist.cert": {
    en: "certificate", es: "certificado", fr: "certificat", de: "Zertifikat", pt: "certificado", it: "certificato", ja: "証明書", zh: "证书", hi: "प्रमाणपत्र", ar: "الشهادة",
  },
  "ref.cert": {
    en: "The certificate", es: "El certificado", fr: "Le certificat", de: "Das Zertifikat", pt: "O certificado", it: "Il certificato", ja: "証明書", zh: "证书内容", hi: "प्रमाणपत्र", ar: "الشهادة",
  },
  "ref.cert.line": {
    en: "{name} signed {at}, identity checked as {level} ({tier}).", es: "{name} firmó el {at}, identidad verificada como {level} ({tier}).", fr: "{name} a signé le {at}, identité vérifiée comme {level} ({tier}).", de: "{name} unterschrieb am {at}, Identität geprüft als {level} ({tier}).", pt: "{name} assinou a {at}, identidade verificada como {level} ({tier}).", it: "{name} ha firmato il {at}, identità verificata come {level} ({tier}).", ja: "{name}が{at}に署名。本人確認は{level}（{tier}）。", zh: "{name}于{at}签署，身份核验为{level}（{tier}）。", hi: "{name} ने {at} को हस्ताक्षर किए, पहचान {level} ({tier}) के रूप में जाँची गई।", ar: "وقّع {name} في {at}، وتم التحقق من الهوية كـ{level} ({tier}).",
  },
  "ref.cert.shown": {
    en: "What was on the screen", es: "Lo que estaba en pantalla", fr: "Ce qui était à l'écran", de: "Was auf dem Bildschirm stand", pt: "O que estava no ecrã", it: "Cosa c'era sullo schermo", ja: "画面に表示されていたもの", zh: "屏幕上显示的内容", hi: "स्क्रीन पर क्या था", ar: "ما كان على الشاشة",
  },
  "ref.cert.doc": {
    en: "Document", es: "Documento", fr: "Document", de: "Dokument", pt: "Documento", it: "Documento", ja: "文書", zh: "文档", hi: "दस्तावेज़", ar: "الوثيقة",
  },
  "ref.notes": {
    en: "What the clinician wrote back", es: "Lo que el clínico respondió", fr: "Ce que le clinicien a répondu", de: "Was der Kliniker zurückschrieb", pt: "O que o clínico respondeu", it: "Cosa ha risposto il clinico", ja: "臨床医からの返信", zh: "医生的回信", hi: "चिकित्सक ने क्या लिखा", ar: "ما كتبه الطبيب ردًا",
  },
  "ref.notes.pitch": {
    en: "Their words, attributed to them. The profile never recites this as its own knowledge.", es: "Sus palabras, atribuidas a ellos. El perfil nunca recita esto como conocimiento propio.", fr: "Leurs mots, qui leur sont attribués. Le profil ne récite jamais cela comme son propre savoir.", de: "Ihre Worte, ihnen zugeschrieben. Das Profil gibt das nie als eigenes Wissen aus.", pt: "As palavras deles, atribuídas a eles. O perfil nunca recita isto como conhecimento próprio.", it: "Le loro parole, attribuite a loro. Il profilo non recita mai questo come conoscenza propria.", ja: "本人の言葉として帰属表示されます。プロフィールがこれを自分の知識として語ることは決してありません。", zh: "他们的话，署他们的名。资料绝不会把这当作自己的知识来复述。", hi: "उनके शब्द, उन्हीं के नाम। प्रोफ़ाइल इसे कभी अपने ज्ञान के रूप में नहीं दोहराता।", ar: "كلماتهم منسوبة إليهم. الملف لا يرددها أبدًا كمعرفته الخاصة.",
  },
  "ref.clin": {
    en: "If you are the clinician", es: "Si tú eres el clínico", fr: "Si vous êtes le clinicien", de: "Wenn Sie der Kliniker sind", pt: "Se você é o clínico", it: "Se il clinico sei tu", ja: "あなたが臨床医なら", zh: "如果你是那位医生", hi: "यदि आप चिकित्सक हैं", ar: "إن كنت أنت الطبيب",
  },
  "ref.clin.pitch": {
    en: "No account needed — the link is the credential, and it works once.", es: "No hace falta cuenta — el enlace es la credencial, y funciona una vez.", fr: "Aucun compte requis — le lien est l'identifiant, et il marche une fois.", de: "Kein Konto nötig — der Link ist die Berechtigung, und er funktioniert einmal.", pt: "Não é preciso conta — o link é a credencial, e funciona uma vez.", it: "Nessun account necessario — il link è la credenziale, e funziona una volta.", ja: "アカウント不要です — リンクそのものが資格情報で、一度だけ使えます。", zh: "无需账户 — 链接就是凭证，且只能用一次。", hi: "खाते की ज़रूरत नहीं — लिंक ही क्रेडेंशियल है, और एक बार चलता है।", ar: "لا حاجة لحساب — الرابط هو الاعتماد، ويعمل مرة واحدة.",
  },
  "ref.clin.id.ph": {
    en: "referral id", es: "id del volante", fr: "id de l'orientation", de: "Überweisungs-Id", pt: "id do encaminhamento", it: "id dell'invio", ja: "紹介ID", zh: "转诊ID", hi: "रेफ़रल आईडी", ar: "معرّف الإحالة",
  },
  "ref.clin.token.ph": {
    en: "the token from the link", es: "el token del enlace", fr: "le jeton du lien", de: "das Token aus dem Link", pt: "o token do link", it: "il token del link", ja: "リンクのトークン", zh: "链接中的令牌", hi: "लिंक से मिला टोकन", ar: "الرمز من الرابط",
  },
  "ref.clin.open": {
    en: "Open it", es: "Abrirlo", fr: "L'ouvrir", de: "Öffnen", pt: "Abri-lo", it: "Aprilo", ja: "開く", zh: "打开", hi: "खोलें", ar: "افتحه",
  },
  "ref.clin.reply": {
    en: "Write back, once", es: "Responde, una vez", fr: "Répondez, une fois", de: "Zurückschreiben, einmal", pt: "Responda, uma vez", it: "Rispondi, una volta", ja: "一度だけ返信", zh: "回信，仅一次", hi: "एक बार जवाब लिखें", ar: "اكتب ردًا، مرة واحدة",
  },
  "ref.clin.reply.ph": {
    en: "what you want the patient to know", es: "lo que quieres que el paciente sepa", fr: "ce que vous voulez que le patient sache", de: "was der Patient wissen soll", pt: "o que quer que o paciente saiba", it: "ciò che vuoi che il paziente sappia", ja: "患者に知らせたいこと", zh: "你想让患者知道的内容", hi: "आप मरीज़ को क्या बताना चाहते हैं", ar: "ما تريد أن يعرفه المريض",
  },
  "ref.clin.send": {
    en: "Send it", es: "Enviarlo", fr: "L'envoyer", de: "Absenden", pt: "Enviá-lo", it: "Invialo", ja: "送信する", zh: "发送", hi: "भेजें", ar: "أرسله",
  },
  "rem.title": {
    en: "Everything else", es: "Todo lo demás", fr: "Tout le reste", de: "Alles Übrige", pt: "Tudo o resto", it: "Tutto il resto", ja: "その他すべて", zh: "其他一切", hi: "बाक़ी सब", ar: "كل ما تبقى",
  },
  "rem.fb": {
    en: "Tell us about the app", es: "Cuéntanos sobre la app", fr: "Parlez-nous de l'appli", de: "Erzählen Sie uns von der App", pt: "Fale-nos da app", it: "Parlaci dell'app", ja: "アプリについて教えてください", zh: "跟我们聊聊这个应用", hi: "ऐप के बारे में बताएँ", ar: "أخبرنا عن التطبيق",
  },
  "rem.fb.pitch": {
    en: "Your own submissions come back to you and to nobody else. All anyone else ever sees is the count by category.", es: "Tus propios envíos vuelven a ti y a nadie más. Lo único que ve cualquier otro es el recuento por categoría.", fr: "Vos propres envois vous reviennent, à vous et à personne d'autre. Tout ce que les autres voient, c'est le décompte par catégorie.", de: "Ihre eigenen Einsendungen kommen zu Ihnen zurück und zu niemandem sonst. Alle anderen sehen nur die Anzahl je Kategorie.", pt: "Os seus próprios envios voltam para si e para mais ninguém. Tudo o que qualquer outro vê é a contagem por categoria.", it: "I tuoi invii tornano a te e a nessun altro. Tutto ciò che chiunque altro vede è il conteggio per categoria.", ja: "あなたの投稿が返ってくるのはあなたにだけで、他の誰にも返りません。他の人が見られるのはカテゴリ別の件数だけです。", zh: "你提交的内容只回到你这里，不给其他任何人。别人能看到的只有按类别的数量。", hi: "आपके भेजे गए संदेश केवल आपके पास लौटते हैं, किसी और के पास नहीं। बाक़ी सबको सिर्फ़ श्रेणीवार गिनती दिखती है।", ar: "ما ترسله يعود إليك وحدك لا إلى غيرك. كل ما يراه الآخرون هو العدد حسب الفئة.",
  },
  "rem.fb.msg.ph": {
    en: "what would make this better", es: "qué lo mejoraría", fr: "ce qui rendrait cela meilleur", de: "was das besser machen würde", pt: "o que tornaria isto melhor", it: "cosa lo renderebbe migliore", ja: "何があれば良くなるか", zh: "怎样能做得更好", hi: "इसे बेहतर क्या बनाएगा", ar: "ما الذي يجعله أفضل",
  },
  "rem.fb.send": {
    en: "Send it", es: "Enviarlo", fr: "L'envoyer", de: "Absenden", pt: "Enviá-lo", it: "Invialo", ja: "送信する", zh: "发送", hi: "भेजें", ar: "أرسله",
  },
  "rem.fb.total": {
    en: "{n} in total across everybody.", es: "{n} en total entre todos.", fr: "{n} au total, tous confondus.", de: "{n} insgesamt über alle hinweg.", pt: "{n} no total entre todos.", it: "{n} in totale fra tutti.", ja: "全員合わせて{n}件。", zh: "所有人合计{n}条。", hi: "सब मिलाकर कुल {n}।", ar: "{n} إجمالًا من الجميع.",
  },
  "rem.mods": {
    en: "Where mods come from", es: "De dónde vienen los mods", fr: "D'où viennent les mods", de: "Woher Mods kommen", pt: "De onde vêm os mods", it: "Da dove arrivano i mod", ja: "モッドの出どころ", zh: "模组从哪来", hi: "मॉड कहाँ से आते हैं", ar: "من أين تأتي الإضافات",
  },
  "rem.mods.pitch": {
    en: "Third-party catalogues. `audience` says what each one stocks — task mods for a robot body, or knowledge mods for a profile.", es: "Catálogos de terceros. «audience» dice qué guarda cada uno — mods de tareas para un cuerpo robótico, o mods de conocimiento para un perfil.", fr: "Catalogues tiers. « audience » indique ce que chacun propose — des mods de tâches pour un corps robotique, ou des mods de savoir pour un profil.", de: "Kataloge Dritter. »audience« sagt, was jeder führt — Aufgaben-Mods für einen Roboterkörper oder Wissens-Mods für ein Profil.", pt: "Catálogos de terceiros. «audience» diz o que cada um tem — mods de tarefas para um corpo robótico, ou mods de conhecimento para um perfil.", it: "Cataloghi di terze parti. «audience» dice cosa tiene ciascuno — mod di compiti per un corpo robotico, o mod di conoscenza per un profilo.", ja: "サードパーティのカタログです。「audience」が各カタログの品揃えを示します — ロボット身体向けのタスクモッドか、プロフィール向けの知識モッドか。", zh: "第三方目录。「audience」说明各家备的是什么 — 给机器人身体的任务模组，还是给资料的知识模组。", hi: "तृतीय-पक्ष कैटलॉग। «audience» बताता है कि किसके पास क्या है — रोबोट शरीर के लिए कार्य-मॉड, या प्रोफ़ाइल के लिए ज्ञान-मॉड।", ar: "كتالوجات طرف ثالث. «audience» يقول ماذا يخزّن كل واحد — إضافات مهام لجسد آلي، أو إضافات معرفة لملف.",
  },
  "rem.mods.counts": {
    en: "{pub} · {items} items · {installs} installs", es: "{pub} · {items} elementos · {installs} instalaciones", fr: "{pub} · {items} éléments · {installs} installations", de: "{pub} · {items} Elemente · {installs} Installationen", pt: "{pub} · {items} itens · {installs} instalações", it: "{pub} · {items} elementi · {installs} installazioni", ja: "{pub} · {items}項目 · {installs}インストール", zh: "{pub} · {items}项 · {installs}次安装", hi: "{pub} · {items} आइटम · {installs} इंस्टॉल", ar: "{pub} · {items} عنصرًا · {installs} تثبيتًا",
  },
  "rem.mods.reg": {
    en: "for a {aud} · {avail} available, {sync} synced", es: "para un {aud} · {avail} disponibles, {sync} sincronizados", fr: "pour un {aud} · {avail} disponibles, {sync} synchronisés", de: "für ein {aud} · {avail} verfügbar, {sync} synchronisiert", pt: "para um {aud} · {avail} disponíveis, {sync} sincronizados", it: "per un {aud} · {avail} disponibili, {sync} sincronizzati", ja: "{aud}向け · {avail}件利用可能、{sync}件同期済み", zh: "面向{aud} · 可用{avail}项，已同步{sync}项", hi: "{aud} के लिए · {avail} उपलब्ध, {sync} सिंक", ar: "لـ{aud} · {avail} متاحة، {sync} متزامنة",
  },
  "rem.mods.sync": {
    en: "Sync", es: "Sincronizar", fr: "Synchroniser", de: "Synchronisieren", pt: "Sincronizar", it: "Sincronizza", ja: "同期", zh: "同步", hi: "सिंक करें", ar: "زامن",
  },
  "rem.apps": {
    en: "Apps it is connected to", es: "Apps a las que está conectado", fr: "Applis auxquelles il est connecté", de: "Apps, mit denen es verbunden ist", pt: "Apps a que está ligado", it: "App a cui è collegato", ja: "接続中のアプリ", zh: "它已连接的应用", hi: "जुड़े हुए ऐप", ar: "التطبيقات المتصل بها",
  },
  "rem.apps.none": {
    en: "None yet.", es: "Ninguna todavía.", fr: "Aucune pour l'instant.", de: "Noch keine.", pt: "Nenhuma ainda.", it: "Ancora nessuna.", ja: "まだありません。", zh: "尚无。", hi: "अभी कोई नहीं।", ar: "لا شيء بعد.",
  },
  "rem.apps.gcal": {
    en: "Connect Google Calendar", es: "Conectar Google Calendar", fr: "Connecter Google Agenda", de: "Google Kalender verbinden", pt: "Ligar o Google Calendar", it: "Collega Google Calendar", ja: "Googleカレンダーを接続", zh: "连接 Google 日历", hi: "Google कैलेंडर जोड़ें", ar: "اربط تقويم Google",
  },
  "rem.trip": {
    en: "Going out to look something up", es: "Salir a consultar algo", fr: "Sortir chercher quelque chose", de: "Hinausgehen, um etwas nachzuschlagen", pt: "Sair para consultar algo", it: "Uscire a cercare qualcosa", ja: "何かを調べに出かける", zh: "出门去查点东西", hi: "कुछ पता करने बाहर जाना", ar: "الخروج للبحث عن شيء",
  },
  "rem.trip.pitch": {
    en: "The question is stripped before it leaves. The answer says how much was taken out and whether it left this machine at all — which is the part worth reading, not the findings.", es: "La pregunta se despoja antes de salir. La respuesta dice cuánto se quitó y si llegó a salir de esta máquina — que es la parte que vale la pena leer, no los hallazgos.", fr: "La question est expurgée avant de partir. La réponse dit combien a été retiré et si elle a seulement quitté cette machine — c'est la partie qui mérite d'être lue, pas les résultats.", de: "Die Frage wird bereinigt, bevor sie geht. Die Antwort sagt, wie viel entfernt wurde und ob sie diese Maschine überhaupt verließ — das ist der lesenswerte Teil, nicht die Befunde.", pt: "A pergunta é despojada antes de sair. A resposta diz quanto foi retirado e se chegou a sair desta máquina — e é essa a parte que vale a pena ler, não os resultados.", it: "La domanda viene spogliata prima di partire. La risposta dice quanto è stato tolto e se è mai uscita da questa macchina — ed è quella la parte che vale la pena leggere, non i risultati.", ja: "質問は出発前に情報を削ぎ落とされます。答えは、どれだけ取り除かれたか、そしてそもそもこの機械を出たのかを述べます — 読む価値があるのは所見ではなくそちらです。", zh: "问题在离开前会被剥除信息。答案会说明删去了多少，以及它究竟有没有离开这台机器 — 值得读的是这部分，而非查到的结果。", hi: "प्रश्न निकलने से पहले छाँटा जाता है। उत्तर बताता है कि कितना हटाया गया और वह इस मशीन से बाहर गया भी या नहीं — पढ़ने लायक़ हिस्सा वही है, निष्कर्ष नहीं।", ar: "يُجرَّد السؤال قبل أن يغادر. والجواب يقول كم أُزيل وهل غادر هذه الآلة أصلًا — وهذا هو الجزء الجدير بالقراءة لا النتائج.",
  },
  "rem.trip.topic.ph": {
    en: "topic", es: "tema", fr: "sujet", de: "Thema", pt: "tema", it: "argomento", ja: "トピック", zh: "主题", hi: "विषय", ar: "الموضوع",
  },
  "rem.trip.q.ph": {
    en: "what to find out", es: "qué averiguar", fr: "ce qu'il faut découvrir", de: "was herauszufinden ist", pt: "o que descobrir", it: "cosa scoprire", ja: "調べる内容", zh: "要查什么", hi: "क्या पता करना है", ar: "ما المطلوب معرفته",
  },
  "rem.trip.go": {
    en: "Go and look", es: "Ir a mirar", fr: "Aller voir", de: "Nachsehen gehen", pt: "Ir ver", it: "Vai a vedere", ja: "見に行く", zh: "去查看", hi: "जाकर देखें", ar: "اذهب وانظر",
  },
  "rem.trip.fold": {
    en: "Fold it in", es: "Incorporarlo", fr: "L'intégrer", de: "Einarbeiten", pt: "Incorporá-lo", it: "Integralo", ja: "取り込む", zh: "并入", hi: "इसे समेट लें", ar: "أدمجه",
  },
  "rem.hub": {
    en: "Every dial in one place", es: "Todos los diales en un sitio", fr: "Tous les réglages au même endroit", de: "Alle Regler an einem Ort", pt: "Todos os botões num só lugar", it: "Tutte le manopole in un posto", ja: "すべてのつまみを一箇所に", zh: "所有旋钮集于一处", hi: "सारे डायल एक जगह", ar: "كل الأقراص في مكان واحد",
  },
  "rem.hub.dials": {
    en: "{n} dials", es: "{n} diales", fr: "{n} réglages", de: "{n} Regler", pt: "{n} botões", it: "{n} manopole", ja: "つまみ{n}個", zh: "{n}个旋钮", hi: "{n} डायल", ar: "{n} أقراص",
  },
  "rem.play": {
    en: "Playing alongside somebody", es: "Jugar junto a alguien", fr: "Jouer aux côtés de quelqu'un", de: "An jemandes Seite spielen", pt: "Jogar ao lado de alguém", it: "Giocare accanto a qualcuno", ja: "誰かと並んで遊ぶ", zh: "陪某人一起玩", hi: "किसी के साथ खेलना", ar: "اللعب إلى جانب أحدهم",
  },
  "rem.play.pitch": {
    en: "The companion plays within the game's rules. Fair play is enforced rather than promised.", es: "El acompañante juega dentro de las reglas del juego. El juego limpio se impone, no se promete.", fr: "Le compagnon joue dans les règles du jeu. Le fair-play est imposé, pas promis.", de: "Der Begleiter spielt innerhalb der Spielregeln. Fairplay wird erzwungen, nicht versprochen.", pt: "O companheiro joga dentro das regras do jogo. O jogo limpo é imposto, não prometido.", it: "Il compagno gioca dentro le regole del gioco. Il fair play è imposto, non promesso.", ja: "コンパニオンはゲームのルールの内側で遊びます。フェアプレーは約束ではなく強制されます。", zh: "同伴在游戏规则之内游玩。公平竞技是强制的，不是承诺的。", hi: "साथी खेल के नियमों के भीतर खेलता है। निष्पक्ष खेल का वादा नहीं, प्रवर्तन होता है।", ar: "الرفيق يلعب ضمن قواعد اللعبة. اللعب النظيف مفروض لا موعود.",
  },
  "rem.play.platform.ph": {
    en: "steam, xbox, playstation…", es: "steam, xbox, playstation…", fr: "steam, xbox, playstation…", de: "steam, xbox, playstation…", pt: "steam, xbox, playstation…", it: "steam, xbox, playstation…", ja: "steam、xbox、playstation…", zh: "steam、xbox、playstation…", hi: "steam, xbox, playstation…", ar: "steam، xbox، playstation…",
  },
  "rem.play.game.ph": {
    en: "which game", es: "qué juego", fr: "quel jeu", de: "welches Spiel", pt: "que jogo", it: "quale gioco", ja: "どのゲーム", zh: "哪款游戏", hi: "कौन-सा खेल", ar: "أي لعبة",
  },
  "rem.play.start": {
    en: "Start a session", es: "Iniciar una sesión", fr: "Démarrer une session", de: "Sitzung starten", pt: "Iniciar uma sessão", it: "Avvia una sessione", ja: "セッションを開始", zh: "开始一局", hi: "सत्र शुरू करें", ar: "ابدأ جلسة",
  },
  "rem.play.line": {
    en: "{game} on {platform} · {role}", es: "{game} en {platform} · {role}", fr: "{game} sur {platform} · {role}", de: "{game} auf {platform} · {role}", pt: "{game} em {platform} · {role}", it: "{game} su {platform} · {role}", ja: "{platform}の{game} · {role}", zh: "{platform}上的{game} · {role}", hi: "{platform} पर {game} · {role}", ar: "{game} على {platform} · {role}",
  },
  "rem.play.ask": {
    en: "Ask it", es: "Preguntarle", fr: "Lui demander", de: "Fragen", pt: "Perguntar-lhe", it: "Chiediglielo", ja: "尋ねる", zh: "问它", hi: "इससे पूछें", ar: "اسأله",
  },
  "rem.play.end": {
    en: "End", es: "Terminar", fr: "Terminer", de: "Beenden", pt: "Terminar", it: "Termina", ja: "終了", zh: "结束", hi: "समाप्त", ar: "أنهِ",
  },
  "rem.look": {
    en: "Look something up by its id", es: "Buscar algo por su id", fr: "Chercher quelque chose par son id", de: "Etwas anhand seiner Id nachschlagen", pt: "Procurar algo pelo seu id", it: "Cerca qualcosa dal suo id", ja: "IDで何かを引く", zh: "按ID查找记录", hi: "आईडी से कुछ खोजें", ar: "ابحث عن شيء بمعرّفه",
  },
  "rem.look.pitch": {
    en: "Nine of these reads had a binding written for them and no screen calling it. They are not nine features — they are one question asked about nine kinds of record, so this is one control rather than nine buttons nobody would find.", es: "Nueve de estas lecturas tenían un enlace escrito y ninguna pantalla que lo llamara. No son nueve funciones — son una pregunta hecha sobre nueve tipos de registro, así que esto es un control y no nueve botones que nadie encontraría.", fr: "Neuf de ces lectures avaient une liaison écrite et aucun écran pour l'appeler. Ce ne sont pas neuf fonctions — c'est une seule question posée sur neuf sortes d'enregistrement, donc voici un contrôle plutôt que neuf boutons introuvables.", de: "Neun dieser Abrufe hatten eine geschriebene Anbindung und keinen Bildschirm, der sie aufrief. Es sind nicht neun Funktionen — es ist eine Frage, gestellt zu neun Arten von Datensatz, also ist dies ein Bedienelement statt neun Knöpfe, die niemand fände.", pt: "Nove destas leituras tinham uma ligação escrita e nenhum ecrã a chamá-la. Não são nove funcionalidades — são uma pergunta feita sobre nove tipos de registo, por isso isto é um controlo em vez de nove botões que ninguém encontraria.", it: "Nove di queste letture avevano un binding scritto e nessuna schermata che lo chiamasse. Non sono nove funzioni — sono una domanda posta su nove tipi di record, quindi questo è un controllo invece di nove pulsanti che nessuno troverebbe.", ja: "これらの読み取りのうち九つには、バインディングだけが書かれ、それを呼ぶ画面がありませんでした。九つの機能ではなく、九種類のレコードに対する一つの問いです。だから九つのボタンではなく一つのコントロールにしてあります。", zh: "其中九项读取写好了绑定，却没有任何界面去调用。它们不是九个功能 — 而是对九类记录问同一个问题，所以这里是一个控件，而非九个没人找得到的按钮。", hi: "इनमें से नौ पठनों के लिए बाइंडिंग लिखी थी और कोई स्क्रीन उसे नहीं बुलाती थी। ये नौ सुविधाएँ नहीं — यह नौ प्रकार के रिकॉर्ड से पूछा गया एक ही प्रश्न है, इसलिए यह एक नियंत्रण है, न कि नौ बटन जो किसी को न मिलें।", ar: "تسع من هذه القراءات كُتب لها ربط ولم تستدعِها أي شاشة. ليست تسع ميزات — بل سؤال واحد يُطرح على تسعة أنواع من السجلات، فجعلناها أداة واحدة بدل تسعة أزرار لا يجدها أحد.",
  },
  "rem.look.id.ph": {
    en: "the id", es: "el id", fr: "l'id", de: "die Id", pt: "o id", it: "l'id", ja: "ID", zh: "该ID", hi: "वह आईडी", ar: "المعرّف",
  },
  "rem.look.go": {
    en: "Fetch it", es: "Traerlo", fr: "Le récupérer", de: "Holen", pt: "Buscá-lo", it: "Recuperalo", ja: "取得する", zh: "取回", hi: "लाएँ", ar: "أحضره",
  },
  "rem.avatar": {
    en: "Its portrait", es: "Su retrato", fr: "Son portrait", de: "Sein Porträt", pt: "O seu retrato", it: "Il suo ritratto", ja: "その肖像", zh: "它的肖像", hi: "इसका चित्र", ar: "صورته",
  },
  "rem.avatar.pitch": {
    en: "The mark is burned into the pixels rather than drawn over them, so it survives a screenshot or a crop.", es: "La marca se graba en los píxeles en vez de dibujarse encima, así que sobrevive a una captura o a un recorte.", fr: "La marque est gravée dans les pixels plutôt que dessinée par-dessus, elle survit donc à une capture d'écran ou à un recadrage.", de: "Das Zeichen wird in die Pixel gebrannt statt darübergezeichnet, also übersteht es einen Screenshot oder einen Zuschnitt.", pt: "A marca é gravada nos pixels em vez de desenhada por cima, por isso sobrevive a uma captura de ecrã ou a um recorte.", it: "Il marchio è bruciato nei pixel invece che disegnato sopra, quindi sopravvive a uno screenshot o a un ritaglio.", ja: "印は画素の上に描かれるのではなく焼き込まれるため、スクリーンショットや切り抜きにも残ります。", zh: "标记是烧进像素里的，而非画在上面，因此截图或裁剪都抹不掉它。", hi: "निशान पिक्सलों पर खींचा नहीं, उनमें जलाकर बैठाया जाता है, इसलिए स्क्रीनशॉट या कतरन के बाद भी बचा रहता है।", ar: "العلامة محروقة داخل البكسلات لا مرسومة فوقها، فتنجو من لقطة شاشة أو اقتصاص.",
  },
  "rem.avatar.limits": {
    en: " Up to {img} MB for a picture, {vid} MB for video.", es: " Hasta {img} MB para una imagen, {vid} MB para vídeo.", fr: " Jusqu'à {img} Mo pour une image, {vid} Mo pour la vidéo.", de: " Bis zu {img} MB für ein Bild, {vid} MB für Video.", pt: " Até {img} MB para uma imagem, {vid} MB para vídeo.", it: " Fino a {img} MB per un'immagine, {vid} MB per il video.", ja: " 画像は最大{img} MB、動画は{vid} MBまで。", zh: " 图片最多{img} MB，视频最多{vid} MB。", hi: " चित्र के लिए {img} MB तक, वीडियो के लिए {vid} MB तक।", ar: " حتى {img} ميغابايت للصورة، و{vid} ميغابايت للفيديو.",
  },
  "rem.avatar.asset.ph": {
    en: "an asset path", es: "una ruta de recurso", fr: "un chemin de ressource", de: "ein Asset-Pfad", pt: "um caminho de recurso", it: "un percorso di risorsa", ja: "アセットのパス", zh: "一个素材路径", hi: "एक एसेट पथ", ar: "مسار أصل",
  },
  "rem.avatar.set": {
    en: "Set it", es: "Fijarlo", fr: "Le définir", de: "Setzen", pt: "Defini-lo", it: "Impostalo", ja: "設定する", zh: "设置", hi: "लगाएँ", ar: "عيّنه",
  },
  "rem.pub": {
    en: "Publishing to a platform we do not run", es: "Publicar en una plataforma que no gestionamos", fr: "Publier sur une plateforme que nous n'exploitons pas", de: "Auf einer Plattform veröffentlichen, die wir nicht betreiben", pt: "Publicar numa plataforma que não gerimos", it: "Pubblicare su una piattaforma che non gestiamo", ja: "私たちが運営しないプラットフォームへの投稿", zh: "发布到我们并不运营的平台", hi: "ऐसे मंच पर प्रकाशन जो हम नहीं चलाते", ar: "النشر على منصة لا ندير نحن",
  },
  "rem.pub.pitch": {
    en: "This is the one place a profile's words genuinely leave. It runs the strict filter — not the profile's own setting — and it stamps a synthetic-media credential, because content going somewhere we cannot see is the case the mark exists for. It used to do neither.", es: "Este es el único sitio donde las palabras de un perfil salen de verdad. Aplica el filtro estricto — no el ajuste del propio perfil — y estampa una credencial de medio sintético, porque el contenido que va a donde no podemos ver es justo el caso para el que existe la marca. Antes no hacía ninguna de las dos cosas.", fr: "C'est le seul endroit où les mots d'un profil partent vraiment. Il applique le filtre strict — pas le réglage du profil — et appose un justificatif de média synthétique, car un contenu qui part là où nous ne voyons pas est précisément le cas pour lequel la marque existe. Il ne faisait ni l'un ni l'autre auparavant.", de: "Das ist der eine Ort, an dem die Worte eines Profils wirklich hinausgehen. Er wendet den strengen Filter an — nicht die Einstellung des Profils — und prägt einen Synthetik-Medien-Nachweis auf, denn Inhalt, der dorthin geht, wo wir nicht sehen können, ist genau der Fall, für den das Zeichen existiert. Früher tat er beides nicht.", pt: "Este é o único sítio onde as palavras de um perfil saem mesmo. Aplica o filtro estrito — não a definição do próprio perfil — e carimba uma credencial de média sintética, porque conteúdo que vai para onde não podemos ver é precisamente o caso para que a marca existe. Antes não fazia nenhuma das duas.", it: "Questo è l'unico posto in cui le parole di un profilo escono davvero. Applica il filtro rigoroso — non l'impostazione del profilo — e imprime una credenziale di media sintetico, perché il contenuto che va dove non possiamo vedere è proprio il caso per cui il marchio esiste. Prima non faceva né l'una né l'altra cosa.", ja: "ここはプロフィールの言葉が本当に外へ出る唯一の場所です。プロフィール自身の設定ではなく厳格フィルタを適用し、合成メディアの証明を刻印します。私たちの見えない場所へ出ていく内容こそ、この印が存在する理由だからです。以前はそのどちらも行っていませんでした。", zh: "这是资料的话语真正离开的唯一出口。它执行严格过滤 — 而非资料自身的设置 — 并加盖合成媒体凭证，因为发往我们看不见之处的内容正是这枚标记存在的理由。此前它两样都没做。", hi: "यही एकमात्र जगह है जहाँ प्रोफ़ाइल के शब्द सचमुच बाहर जाते हैं। यह सख़्त फ़िल्टर लगाता है — प्रोफ़ाइल की अपनी सेटिंग नहीं — और सिंथेटिक-मीडिया प्रमाण मुहर करता है, क्योंकि जो सामग्री हमारी दृष्टि से बाहर जाती है वही वह स्थिति है जिसके लिए यह निशान बना है। पहले यह दोनों में से कुछ नहीं करता था।", ar: "هذا هو المكان الوحيد الذي تغادر منه كلمات الملف فعلًا. يطبّق المرشّح الصارم — لا إعداد الملف نفسه — ويختم اعتماد وسائط اصطناعية، لأن المحتوى الذاهب إلى حيث لا نرى هو بالضبط الحالة التي وُجدت العلامة لأجلها. ولم يكن يفعل أيًّا منهما من قبل.",
  },
  "rem.pub.cid.ph": {
    en: "a publish connection id", es: "un id de conexión de publicación", fr: "un id de connexion de publication", de: "eine Veröffentlichungs-Verbindungs-Id", pt: "um id de ligação de publicação", it: "un id di connessione di pubblicazione", ja: "投稿用の接続ID", zh: "一个发布连接ID", hi: "एक प्रकाशन कनेक्शन आईडी", ar: "معرّف اتصال نشر",
  },
  "rem.pub.text.ph": {
    en: "what to post", es: "qué publicar", fr: "quoi publier", de: "was gepostet wird", pt: "o que publicar", it: "cosa pubblicare", ja: "投稿する内容", zh: "要发什么", hi: "क्या पोस्ट करना है", ar: "ماذا تنشر",
  },
  "rem.pub.go": {
    en: "Publish it", es: "Publicarlo", fr: "Le publier", de: "Veröffentlichen", pt: "Publicá-lo", it: "Pubblicalo", ja: "投稿する", zh: "发布", hi: "प्रकाशित करें", ar: "انشره",
  },
  "rem.pub.read": {
    en: "Or read from one", es: "O leer desde una", fr: "Ou lire depuis l'une d'elles", de: "Oder von einer lesen", pt: "Ou ler de uma", it: "Oppure leggi da una", ja: "あるいは読み込む", zh: "或从中读入", hi: "या उसी से पढ़ें", ar: "أو اقرأ من واحدة",
  },
  "rem.pub.read.pitch": {
    en: "The other direction on the same connection: what the account already published becomes source material this profile is built from.", es: "La otra dirección de la misma conexión: lo que la cuenta ya publicó se convierte en material de origen con el que se construye este perfil.", fr: "L'autre sens sur la même connexion : ce que le compte a déjà publié devient la matière première dont ce profil est construit.", de: "Die andere Richtung auf derselben Verbindung: was das Konto bereits veröffentlicht hat, wird zum Quellmaterial, aus dem dieses Profil gebaut ist.", pt: "A outra direção na mesma ligação: o que a conta já publicou torna-se material de origem com que este perfil é construído.", it: "L'altra direzione sulla stessa connessione: ciò che l'account ha già pubblicato diventa materiale di partenza da cui questo profilo è costruito.", ja: "同じ接続の逆方向です：そのアカウントが既に公開したものが、このプロフィールを形づくる材料になります。", zh: "同一连接的另一方向：该账号已经发布的内容，成为构建这份资料的素材。", hi: "उसी कनेक्शन की दूसरी दिशा: खाते ने जो पहले ही प्रकाशित किया है, वह इस प्रोफ़ाइल के निर्माण की सामग्री बन जाता है।", ar: "الاتجاه الآخر على الاتصال نفسه: ما نشره الحساب سابقًا يصير مادة يُبنى منها هذا الملف.",
  },
  "rem.pub.collect.ph": {
    en: "a post to read in", es: "una publicación para leer", fr: "un post à lire", de: "ein Beitrag zum Einlesen", pt: "uma publicação para ler", it: "un post da leggere", ja: "読み込む投稿", zh: "要读入的一条帖子", hi: "पढ़ने के लिए एक पोस्ट", ar: "منشور لقراءته",
  },
  "rem.pub.collect": {
    en: "Read it in", es: "Leerlo", fr: "L'importer", de: "Einlesen", pt: "Lê-lo", it: "Leggilo", ja: "読み込む", zh: "读入", hi: "पढ़ लें", ar: "اقرأه",
  },
  "rem.pub.cred": {
    en: "Credential {id} · {disclosure}", es: "Credencial {id} · {disclosure}", fr: "Justificatif {id} · {disclosure}", de: "Nachweis {id} · {disclosure}", pt: "Credencial {id} · {disclosure}", it: "Credenziale {id} · {disclosure}", ja: "証明 {id} · {disclosure}", zh: "凭证 {id} · {disclosure}", hi: "प्रमाण {id} · {disclosure}", ar: "الاعتماد {id} · {disclosure}",
  },
};

export function t(key: string, lang: string | undefined): string {
  const row = CHROME[key];
  if (!row) return key;
  return row[(lang as Lang) || "en"] || row.en || key;
}


/**
 * A translated sentence with its values put back in.
 *
 * The alternative — and what `Public.tsx` did until this round — is to break
 * the sentence at every interpolation and let JSX stitch the pieces:
 *
 *     The profile is <strong>{status}</strong> from this moment. It was …
 *
 * Which is three English fragments, and fragments cannot be translated. Word
 * order around an inserted value is not English's in most of the ten
 * languages here; handing a translator "from this moment. It was" produces
 * something that looks done and reads broken. Worse, the guard that watches
 * for untranslated copy could only see the brace-free scraps, so the parts it
 * reported were the parts that mattered least.
 *
 * So the table holds the whole sentence with its holes named — `{now}`,
 * `{before}` — and each language puts the holes wherever its grammar wants
 * them. An unknown name renders as itself rather than vanishing: a visible
 * `{typo}` on screen is a bug report, an empty space is a mystery.
 */
export function fill(
  template: string,
  values: Readonly<Record<string, ReactNode>>,
): ReactNode[] {
  const out: ReactNode[] = [];
  const hole = /\{(\w+)\}/g;
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = hole.exec(template)) !== null) {
    if (match.index > last) out.push(template.slice(last, match.index));
    const value = match[1] in values ? values[match[1]] : match[0];
    // Keyed, because React warns about array children without one and a
    // console full of warnings is how a real one gets missed.
    out.push(createElement(Fragment, { key: out.length }, value));
    last = match.index + match[0].length;
  }
  if (last < template.length) out.push(template.slice(last));
  return out;
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
