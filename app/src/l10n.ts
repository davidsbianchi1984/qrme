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
  "idn.title": {
    en: "Who this profile is", es: "Quién es este perfil", fr: "Qui est ce profil", de: "Wer dieses Profil ist", pt: "Quem é este perfil", it: "Chi è questo profilo", ja: "このプロフィールは誰か", zh: "这份资料是谁", hi: "यह प्रोफ़ाइल कौन है", ar: "من هذا الملف",
  },
  "idn.rules": {
    en: "The rules", es: "Las reglas", fr: "Les règles", de: "Die Regeln", pt: "As regras", it: "Le regole", ja: "規則", zh: "规则", hi: "नियम", ar: "القواعد",
  },
  "idn.roster": {
    en: "Your profiles", es: "Tus perfiles", fr: "Vos profils", de: "Ihre Profile", pt: "Os seus perfis", it: "I tuoi profili", ja: "あなたのプロフィール", zh: "你的资料", hi: "आपके प्रोफ़ाइल", ar: "ملفاتك",
  },
  "idn.roster.pitch": {
    en: "Only you can see this list — it is the link between your separate personas, which is the thing anonymity is protecting.", es: "Solo tú puedes ver esta lista — es el vínculo entre tus personas separadas, que es justo lo que el anonimato protege.", fr: "Vous seul voyez cette liste — c'est le lien entre vos personnages distincts, et c'est précisément ce que l'anonymat protège.", de: "Nur Sie sehen diese Liste — sie ist die Verbindung zwischen Ihren getrennten Personas, und genau das schützt die Anonymität.", pt: "Só você vê esta lista — é a ligação entre as suas personas separadas, que é precisamente o que o anonimato protege.", it: "Solo tu vedi questa lista — è il legame tra le tue persone separate, ed è proprio ciò che l'anonimato protegge.", ja: "このリストを見られるのはあなただけです — 分かれたペルソナ同士をつなぐ糸であり、匿名性が守っているのはまさにそれです。", zh: "只有你能看到这份清单 — 它是你各个分身之间的连线，而这正是匿名性所保护的东西。", hi: "यह सूची केवल आप देख सकते हैं — यह आपके अलग-अलग व्यक्तित्वों के बीच की कड़ी है, और गुमनामी इसी की रक्षा करती है।", ar: "أنت وحدك من يرى هذه القائمة — إنها الرابط بين شخصياتك المنفصلة، وهو بالضبط ما تحميه السرية.",
  },
  "idn.roster.none": {
    en: "Nothing yet.", es: "Nada todavía.", fr: "Rien pour l'instant.", de: "Noch nichts.", pt: "Nada ainda.", it: "Ancora niente.", ja: "まだ何もありません。", zh: "尚无。", hi: "अभी कुछ नहीं।", ar: "لا شيء بعد.",
  },
  "idn.roster.thisone": {
    en: "this one", es: "este", fr: "celui-ci", de: "dieses", pt: "este", it: "questo", ja: "これ", zh: "当前这个", hi: "यही", ar: "هذا",
  },
  "idn.roster.anon": {
    en: "anonymous", es: "anónimo", fr: "anonyme", de: "anonym", pt: "anónimo", it: "anonimo", ja: "匿名", zh: "匿名", hi: "गुमनाम", ar: "مجهول",
  },
  "idn.roster.verified": {
    en: "verified ({level})", es: "verificado ({level})", fr: "vérifié ({level})", de: "verifiziert ({level})", pt: "verificado ({level})", it: "verificato ({level})", ja: "確認済み（{level}）", zh: "已验证（{level}）", hi: "सत्यापित ({level})", ar: "موثّق ({level})",
  },
  "idn.roster.notverified": {
    en: "not verified", es: "no verificado", fr: "non vérifié", de: "nicht verifiziert", pt: "não verificado", it: "non verificato", ja: "未確認", zh: "未验证", hi: "असत्यापित", ar: "غير موثّق",
  },
  "idn.roster.unverifiable": {
    en: "unverifiable — an invented person", es: "inverificable — una persona inventada", fr: "invérifiable — une personne inventée", de: "nicht verifizierbar — eine erfundene Person", pt: "não verificável — uma pessoa inventada", it: "non verificabile — una persona inventata", ja: "確認不能 — 架空の人物", zh: "无从验证 — 一个虚构的人", hi: "सत्यापन-अयोग्य — एक गढ़ा हुआ व्यक्ति", ar: "غير قابل للتوثيق — شخص مُختلق",
  },
  "idn.roster.move": {
    en: "Move the badge here", es: "Mover la insignia aquí", fr: "Déplacer le badge ici", de: "Das Abzeichen hierher verschieben", pt: "Mover o distintivo para aqui", it: "Sposta qui il distintivo", ja: "バッジをここへ移す", zh: "把徽章移到这里", hi: "बैज यहाँ लाएँ", ar: "انقل الشارة إلى هنا",
  },
  "idn.ver": {
    en: "Verification", es: "Verificación", fr: "Vérification", de: "Verifizierung", pt: "Verificação", it: "Verifica", ja: "本人確認", zh: "验证", hi: "सत्यापन", ar: "التوثيق",
  },
  "idn.ver.means": {
    en: "{means} ({level}, rank {rank})", es: "{means} ({level}, rango {rank})", fr: "{means} ({level}, rang {rank})", de: "{means} ({level}, Rang {rank})", pt: "{means} ({level}, nível {rank})", it: "{means} ({level}, rango {rank})", ja: "{means}（{level}、ランク{rank}）", zh: "{means}（{level}，等级{rank}）", hi: "{means} ({level}, रैंक {rank})", ar: "{means} ({level}، رتبة {rank})",
  },
  "idn.ver.checkedby": {
    en: "Checked by {who}", es: "Verificado por {who}", fr: "Vérifié par {who}", de: "Geprüft von {who}", pt: "Verificado por {who}", it: "Verificato da {who}", ja: "{who}が確認", zh: "由{who}核验", hi: "{who} ने जाँचा", ar: "تحقق منه {who}",
  },
  "idn.ver.withheld": {
    en: "Who checked is withheld — it would point back to a name this profile does not publish.", es: "Quién lo verificó se reserva — señalaría de vuelta a un nombre que este perfil no publica.", fr: "Qui a vérifié est tenu secret — cela renverrait à un nom que ce profil ne publie pas.", de: "Wer geprüft hat, bleibt zurückgehalten — es würde auf einen Namen zurückweisen, den dieses Profil nicht veröffentlicht.", pt: "Quem verificou é reservado — apontaria de volta para um nome que este perfil não publica.", it: "Chi ha verificato è riservato — rimanderebbe a un nome che questo profilo non pubblica.", ja: "確認者は伏せられています — このプロフィールが公開していない名前を指し示してしまうからです。", zh: "核验者不予公开 — 那会指回这份资料并未公开的名字。", hi: "किसने जाँचा यह रोक रखा गया है — वह उस नाम की ओर संकेत करेगा जिसे यह प्रोफ़ाइल प्रकाशित नहीं करती।", ar: "يُحجب من تحقق — لأنه سيشير إلى اسم لا ينشره هذا الملف.",
  },
  "idn.ver.movehere": {
    en: "Move it to this profile", es: "Moverla a este perfil", fr: "Le déplacer vers ce profil", de: "Zu diesem Profil verschieben", pt: "Movê-lo para este perfil", it: "Spostalo su questo profilo", ja: "このプロフィールへ移す", zh: "移到这份资料", hi: "इसे इस प्रोफ़ाइल पर लाएँ", ar: "انقلها إلى هذا الملف",
  },
  "idn.ver.how.ph": {
    en: "how", es: "cómo", fr: "comment", de: "wie", pt: "como", it: "come", ja: "方法", zh: "如何核验", hi: "कैसे", ar: "كيف",
  },
  "idn.ver.record": {
    en: "Record", es: "Registrar", fr: "Enregistrer", de: "Erfassen", pt: "Registar", it: "Registra", ja: "記録する", zh: "记录", hi: "दर्ज करें", ar: "سجّل",
  },
  "idn.anon": {
    en: "Anonymity", es: "Anonimato", fr: "Anonymat", de: "Anonymität", pt: "Anonimato", it: "Anonimato", ja: "匿名性", zh: "匿名", hi: "गुमनामी", ar: "السرية",
  },
  "idn.anon.shown": {
    en: "Shown as {name}. {note}", es: "Se muestra como {name}. {note}", fr: "Affiché comme {name}. {note}", de: "Angezeigt als {name}. {note}", pt: "Mostrado como {name}. {note}", it: "Mostrato come {name}. {note}", ja: "表示名は{name}。{note}", zh: "显示为{name}。{note}", hi: "{name} के रूप में दिखता है। {note}", ar: "يُعرض باسم {name}. {note}",
  },
  "idn.anon.reversible": {
    en: "Reversible, from now on.", es: "Reversible, de ahora en adelante.", fr: "Réversible, à partir de maintenant.", de: "Umkehrbar, ab jetzt.", pt: "Reversível, de agora em diante.", it: "Reversibile, da ora in poi.", ja: "今後については元に戻せます。", zh: "自此可逆。", hi: "अब से प्रतिवर्ती।", ar: "قابل للتراجع، من الآن فصاعدًا.",
  },
  "idn.anon.withheld": {
    en: "Withheld", es: "Reservado", fr: "Retenu", de: "Zurückgehalten", pt: "Reservado", it: "Riservato", ja: "伏せられるもの", zh: "不予公开", hi: "रोका गया", ar: "محجوب",
  },
  "idn.anon.notwithheld": {
    en: "Not withheld", es: "No reservado", fr: "Non retenu", de: "Nicht zurückgehalten", pt: "Não reservado", it: "Non riservato", ja: "伏せられないもの", zh: "并未隐去", hi: "नहीं रोका गया", ar: "غير محجوب",
  },
  "idn.bubble": {
    en: "The bubble", es: "La burbuja", fr: "La bulle", de: "Die Blase", pt: "A bolha", it: "La bolla", ja: "バブル", zh: "气泡", hi: "बुलबुला", ar: "الفقاعة",
  },
  "idn.bubble.showing": {
    en: "Showing {asset}", es: "Mostrando {asset}", fr: "Affiche {asset}", de: "Zeigt {asset}", pt: "A mostrar {asset}", it: "Mostra {asset}", ja: "表示中: {asset}", zh: "正在显示 {asset}", hi: "दिखा रहा {asset}", ar: "يعرض {asset}",
  },
  "idn.bubble.portrait": {
    en: "Or a portrait", es: "O un retrato", fr: "Ou un portrait", de: "Oder ein Porträt", pt: "Ou um retrato", it: "Oppure un ritratto", ja: "あるいは肖像", zh: "或者一幅肖像", hi: "या एक चित्र", ar: "أو صورة شخصية",
  },
  "idn.bubble.brief": {
    en: "A brief is the description you would hand a generator. Nothing here draws it for you — picking one sets the asset, and the portrait itself is yours to make.", es: "Un brief es la descripción que le darías a un generador. Aquí nada lo dibuja por ti — elegir uno fija el recurso, y el retrato en sí es tuyo para hacerlo.", fr: "Un brief est la description que vous donneriez à un générateur. Rien ici ne le dessine pour vous — en choisir un fixe la ressource, et le portrait lui-même reste à vous de faire.", de: "Ein Briefing ist die Beschreibung, die Sie einem Generator geben würden. Hier zeichnet nichts für Sie — eines zu wählen setzt das Asset, und das Porträt selbst zu machen bleibt Ihre Sache.", pt: "Um briefing é a descrição que daria a um gerador. Aqui nada o desenha por si — escolher um define o recurso, e o retrato em si é seu para fazer.", it: "Un brief è la descrizione che daresti a un generatore. Qui nulla lo disegna per te — sceglierne uno imposta la risorsa, e il ritratto stesso sta a te farlo.", ja: "ブリーフとは、生成器に手渡す説明文のことです。ここで代わりに描くものは何もありません — 選ぶとアセットが設定されるだけで、肖像そのものを作るのはあなたです。", zh: "简述就是你会交给生成器的那段描述。这里没有任何东西替你作画 — 选中一条只是设定素材，肖像本身要由你自己来做。", hi: "ब्रीफ़ वह विवरण है जो आप किसी जनरेटर को सौंपते। यहाँ कुछ भी आपके लिए नहीं बनाता — एक चुनने से एसेट तय होता है, और चित्र स्वयं आपको बनाना है।", ar: "الموجز هو الوصف الذي تسلّمه لمولّد. لا شيء هنا يرسمه عنك — اختيار واحد يعيّن الأصل فقط، والصورة نفسها عليك أنت أن تصنعها.",
  },
  "idn.bubble.prompt": {
    en: "Show the prompt", es: "Ver el prompt", fr: "Afficher le prompt", de: "Prompt anzeigen", pt: "Ver o prompt", it: "Mostra il prompt", ja: "プロンプトを表示", zh: "显示提示词", hi: "प्रॉम्प्ट दिखाएँ", ar: "أظهر الموجّه",
  },
  "idn.rename": {
    en: "Rename", es: "Cambiar el nombre", fr: "Renommer", de: "Umbenennen", pt: "Mudar o nome", it: "Rinomina", ja: "名前を変える", zh: "改名", hi: "नाम बदलें", ar: "إعادة التسمية",
  },
  "idn.rename.ph": {
    en: "a new display name", es: "un nuevo nombre visible", fr: "un nouveau nom affiché", de: "ein neuer Anzeigename", pt: "um novo nome visível", it: "un nuovo nome visibile", ja: "新しい表示名", zh: "新的显示名", hi: "नया प्रदर्शित नाम", ar: "اسم معروض جديد",
  },
  "idn.rename.save": {
    en: "Save", es: "Guardar", fr: "Enregistrer", de: "Speichern", pt: "Guardar", it: "Salva", ja: "保存", zh: "保存", hi: "सहेजें", ar: "احفظ",
  },
  "idn.export": {
    en: "Take it with you", es: "Llévatelo contigo", fr: "Emportez-le avec vous", de: "Nehmen Sie es mit", pt: "Leve-o consigo", it: "Portalo con te", ja: "持って出る", zh: "带走它", hi: "अपने साथ ले जाएँ", ar: "خذه معك",
  },
  "idn.export.pitch": {
    en: "Everything held about this profile, as rows. Leaving before you can take your things is not leaving.", es: "Todo lo que se guarda sobre este perfil, en filas. Irse antes de poder llevarte tus cosas no es irse.", fr: "Tout ce qui est détenu sur ce profil, en lignes. Partir avant de pouvoir emporter ses affaires, ce n'est pas partir.", de: "Alles, was über dieses Profil gehalten wird, als Zeilen. Zu gehen, bevor man seine Sachen mitnehmen kann, ist kein Gehen.", pt: "Tudo o que é guardado sobre este perfil, em linhas. Sair antes de poder levar as suas coisas não é sair.", it: "Tutto ciò che è custodito su questo profilo, in righe. Andarsene prima di poter portare via le proprie cose non è andarsene.", ja: "このプロフィールについて保持されているすべてを、行として。荷物を持ち出せないうちに去るのは、去ることではありません。", zh: "关于这份资料所保存的一切，以行的形式呈现。在还不能带走自己的东西之前离开，那不算离开。", hi: "इस प्रोफ़ाइल के बारे में रखा गया सब कुछ, पंक्तियों के रूप में। अपना सामान ले जा सकने से पहले जाना, जाना नहीं है।", ar: "كل ما هو محفوظ عن هذا الملف، في صفوف. المغادرة قبل أن تستطيع أخذ أشيائك ليست مغادرة.",
  },
  "idn.export.go": {
    en: "Export", es: "Exportar", fr: "Exporter", de: "Exportieren", pt: "Exportar", it: "Esporta", ja: "エクスポート", zh: "导出", hi: "निर्यात करें", ar: "صدّر",
  },
  "idn.mem": {
    en: "Memorial", es: "Memorial", fr: "Mémorial", de: "Gedenkseite", pt: "Memorial", it: "Memoriale", ja: "追悼", zh: "纪念", hi: "स्मारक", ar: "التذكار",
  },
  "idn.mem.line": {
    en: "{status} · {n} relationship{s} touched", es: "{status} · {n} relaciones afectadas", fr: "{status} · {n} relations touchées", de: "{status} · {n} Beziehungen berührt", pt: "{status} · {n} relações tocadas", it: "{status} · {n} relazioni toccate", ja: "{status} · 関係{n}件に影響", zh: "{status} · 触及{n}段关系", hi: "{status} · {n} रिश्ते प्रभावित", ar: "{status} · {n} علاقات مسّها",
  },
  "idn.end": {
    en: "Ending it", es: "Ponerle fin", fr: "Y mettre fin", de: "Es beenden", pt: "Pôr-lhe fim", it: "Metterci fine", ja: "終わらせる", zh: "结束它", hi: "इसे समाप्त करना", ar: "إنهاؤه",
  },
  "idn.end.pitch": {
    en: "Two different endings, and the difference is what happens to the people who knew it.", es: "Dos finales distintos, y la diferencia es qué pasa con quienes lo conocieron.", fr: "Deux fins différentes, et la différence tient à ce qu'il advient de ceux qui l'ont connu.", de: "Zwei verschiedene Enden, und der Unterschied ist, was mit denen geschieht, die es kannten.", pt: "Dois finais diferentes, e a diferença está no que acontece a quem o conheceu.", it: "Due finali diversi, e la differenza è cosa succede a chi lo ha conosciuto.", ja: "終わり方は二つあり、違いは、これを知っていた人々に何が起こるかです。", zh: "两种不同的结局，区别在于认识它的人会怎样。", hi: "दो अलग अंत, और फ़र्क़ यह है कि जिन्होंने इसे जाना उनका क्या होता है।", ar: "نهايتان مختلفتان، والفرق هو ما يحدث لمن عرفوه.",
  },
  "idn.end.retire": {
    en: "Retire", es: "Retirar", fr: "Retirer", de: "Zurückziehen", pt: "Retirar", it: "Ritira", ja: "引退させる", zh: "退隐", hi: "सेवानिवृत्त करें", ar: "تقاعد",
  },
  "idn.end.retire.note": {
    en: "The profile departs. What it meant to the people who knew it stays readable, and so does the export.", es: "El perfil se marcha. Lo que significó para quienes lo conocieron sigue siendo legible, y la exportación también.", fr: "Le profil s'en va. Ce qu'il a représenté pour ceux qui l'ont connu reste lisible, et l'export aussi.", de: "Das Profil geht fort. Was es denen bedeutete, die es kannten, bleibt lesbar, und der Export ebenso.", pt: "O perfil parte. O que significou para quem o conheceu continua legível, e a exportação também.", it: "Il profilo se ne va. Ciò che ha significato per chi lo ha conosciuto resta leggibile, e anche l'esportazione.", ja: "プロフィールは去ります。それを知っていた人々にとっての意味は読める状態で残り、エクスポートも残ります。", zh: "资料就此离去。它对认识它的人意味着什么，仍可读；导出的内容也仍在。", hi: "प्रोफ़ाइल विदा लेती है। जिन्होंने इसे जाना उनके लिए इसका जो अर्थ था वह पठनीय रहता है, और निर्यात भी।", ar: "يرحل الملف. ويبقى ما عناه لمن عرفوه مقروءًا، ويبقى التصدير كذلك.",
  },
  "idn.end.retire.yes": {
    en: "Yes, retire it", es: "Sí, retíralo", fr: "Oui, le retirer", de: "Ja, zurückziehen", pt: "Sim, retirá-lo", it: "Sì, ritiralo", ja: "はい、引退させます", zh: "是的，让它退隐", hi: "हाँ, सेवानिवृत्त करें", ar: "نعم، أحِله للتقاعد",
  },
  "idn.end.sunset.line": {
    en: "{status} · {n} farewell{s} · memory {memory}", es: "{status} · {n} despedidas · memoria {memory}", fr: "{status} · {n} adieux · mémoire {memory}", de: "{status} · {n} Abschiede · Erinnerung {memory}", pt: "{status} · {n} despedidas · memória {memory}", it: "{status} · {n} addii · memoria {memory}", ja: "{status} · 別れの言葉{n}件 · 記憶 {memory}", zh: "{status} · {n}句告别 · 记忆 {memory}", hi: "{status} · {n} विदाई · स्मृति {memory}", ar: "{status} · {n} وداعات · الذاكرة {memory}",
  },
  "idn.end.delete": {
    en: "Delete", es: "Eliminar", fr: "Supprimer", de: "Löschen", pt: "Eliminar", it: "Elimina", ja: "削除", zh: "删除", hi: "मिटाएँ", ar: "احذف",
  },
  "idn.end.delete.note": {
    en: "Erased, not retired. Nothing stays, and there is no memorial.", es: "Borrado, no retirado. No queda nada, y no hay memorial.", fr: "Effacé, pas retiré. Rien ne reste, et il n'y a pas de mémorial.", de: "Gelöscht, nicht zurückgezogen. Nichts bleibt, und es gibt keine Gedenkseite.", pt: "Apagado, não retirado. Nada fica, e não há memorial.", it: "Cancellato, non ritirato. Non resta nulla, e non c'è memoriale.", ja: "引退ではなく消去です。何も残らず、追悼もありません。", zh: "是抹除，不是退隐。什么都不留下，也没有纪念。", hi: "मिटाया गया, सेवानिवृत्त नहीं। कुछ नहीं बचता, और कोई स्मारक नहीं।", ar: "مُحي لا متقاعد. لا يبقى شيء، ولا تذكار.",
  },
  "idn.end.delete.yes": {
    en: "Yes, delete it", es: "Sí, elimínalo", fr: "Oui, le supprimer", de: "Ja, löschen", pt: "Sim, eliminá-lo", it: "Sì, eliminalo", ja: "はい、削除します", zh: "是的，删除它", hi: "हाँ, मिटा दें", ar: "نعم، احذفه",
  },
  "idn.end.erased": {
    en: "What was erased", es: "Qué se borró", fr: "Ce qui a été effacé", de: "Was gelöscht wurde", pt: "O que foi apagado", it: "Cosa è stato cancellato", ja: "消去されたもの", zh: "抹除了什么", hi: "क्या मिटाया गया", ar: "ما الذي مُحي",
  },
  "idn.end.zeros": {
    en: "{n} other kinds of record had nothing to erase.", es: "Otros {n} tipos de registro no tenían nada que borrar.", fr: "{n} autres sortes d'enregistrement n'avaient rien à effacer.", de: "{n} andere Arten von Datensätzen hatten nichts zu löschen.", pt: "Outros {n} tipos de registo não tinham nada para apagar.", it: "Altri {n} tipi di record non avevano nulla da cancellare.", ja: "他の{n}種類のレコードには消すものがありませんでした。", zh: "另有{n}类记录没有可抹除的内容。", hi: "अन्य {n} प्रकार के रिकॉर्ड में मिटाने को कुछ नहीं था।", ar: "لم يكن لدى {n} أنواع أخرى من السجلات ما يُمحى.",
  },
  "wsh.title": {
    en: "What it is made of", es: "De qué está hecho", fr: "De quoi c'est fait", de: "Woraus es besteht", pt: "De que é feito", it: "Di cosa è fatto", ja: "何でできているか", zh: "它由什么构成", hi: "यह किससे बना है", ar: "مما هو مصنوع",
  },
  "wsh.lead": {
    en: "The material a profile is built from, the manner it comes across in, and everything it can hand on to somebody who knows more.", es: "El material con el que se construye un perfil, la manera en que se presenta, y todo lo que puede pasar a alguien que sabe más.", fr: "La matière dont un profil est fait, la manière dont il se présente, et tout ce qu'il peut transmettre à quelqu'un qui en sait plus.", de: "Das Material, aus dem ein Profil gebaut ist, die Art, wie es rüberkommt, und alles, was es an jemanden weitergeben kann, der mehr weiß.", pt: "O material de que um perfil é feito, a maneira como se apresenta, e tudo o que pode passar a alguém que saiba mais.", it: "Il materiale di cui è fatto un profilo, il modo in cui si presenta, e tutto ciò che può passare a qualcuno che ne sa di più.", ja: "プロフィールを形づくる素材、その伝わり方、そしてより詳しい誰かへ渡せるすべて。", zh: "构成一份资料的材料、它给人的感觉，以及它能转交给更懂行者的一切。", hi: "जिस सामग्री से प्रोफ़ाइल बनी है, जिस ढंग से वह सामने आती है, और वह सब जो वह किसी अधिक जानकार को सौंप सकती है।", ar: "المادة التي يُبنى منها الملف، والطريقة التي يظهر بها، وكل ما يمكنه تسليمه لمن يعرف أكثر.",
  },
  "wsh.same": {
    en: "The same personality, wherever it is met", es: "La misma personalidad, dondequiera que se la encuentre", fr: "La même personnalité, où qu'on la rencontre", de: "Dieselbe Persönlichkeit, wo immer man ihr begegnet", pt: "A mesma personalidade, onde quer que se a encontre", it: "La stessa personalità, ovunque la si incontri", ja: "どこで出会っても同じ人格", zh: "无论在哪里遇见，都是同一个性情", hi: "वही व्यक्तित्व, कहीं भी मिले", ar: "الشخصية نفسها، أينما قوبلت",
  },
  "wsh.same.sig": {
    en: "Signature {sig} · invariant across {across}.", es: "Firma {sig} · invariante en {across}.", fr: "Signature {sig} · invariante sur {across}.", de: "Signatur {sig} · invariant über {across}.", pt: "Assinatura {sig} · invariante em {across}.", it: "Firma {sig} · invariante su {across}.", ja: "署名 {sig} · {across}をまたいで不変。", zh: "签名 {sig} · 在{across}间保持不变。", hi: "हस्ताक्षर {sig} · {across} में अपरिवर्तित।", ar: "التوقيع {sig} · ثابت عبر {across}.",
  },
  "wsh.same.public": {
    en: "This check is public — anybody who meets {name} in any form can look up this signature from the sign-in page, with no profile of their own.", es: "Esta comprobación es pública — cualquiera que se encuentre con {name} en cualquier forma puede consultar esta firma desde la página de inicio de sesión, sin perfil propio.", fr: "Cette vérification est publique — quiconque rencontre {name} sous n'importe quelle forme peut consulter cette signature depuis la page de connexion, sans profil à lui.", de: "Diese Prüfung ist öffentlich — wer {name} in irgendeiner Form begegnet, kann diese Signatur von der Anmeldeseite aus nachschlagen, ganz ohne eigenes Profil.", pt: "Esta verificação é pública — qualquer pessoa que encontre {name} sob qualquer forma pode consultar esta assinatura na página de início de sessão, sem perfil próprio.", it: "Questo controllo è pubblico — chiunque incontri {name} in qualsiasi forma può cercare questa firma dalla pagina di accesso, senza avere un profilo.", ja: "この確認は公開されています — どんな形であれ{name}に出会った人は、自分のプロフィールを持たなくても、サインインページからこの署名を照会できます。", zh: "这项核验是公开的 — 任何以任何形式遇见{name}的人，都可以从登录页查询这个签名，无需拥有自己的资料。", hi: "यह जाँच सार्वजनिक है — जो कोई भी {name} से किसी भी रूप में मिले, वह बिना अपना प्रोफ़ाइल बनाए साइन-इन पृष्ठ से यह हस्ताक्षर देख सकता है।", ar: "هذا الفحص علني — كل من يلتقي {name} بأي صورة يمكنه البحث عن هذا التوقيع من صفحة الدخول، دون ملف خاص به.",
  },
  "wsh.same.also": {
    en: "Also present on: {list}.", es: "También presente en: {list}.", fr: "Également présent sur : {list}.", de: "Ebenfalls vorhanden auf: {list}.", pt: "Também presente em: {list}.", it: "Presente anche su: {list}.", ja: "次にも存在します: {list}。", zh: "同样出现在: {list}。", hi: "यहाँ भी मौजूद: {list}।", ar: "موجود أيضًا على: {list}.",
  },
  "wsh.steer": {
    en: "How it comes across", es: "Cómo se presenta", fr: "Comment il se présente", de: "Wie es rüberkommt", pt: "Como se apresenta", it: "Come si presenta", ja: "どう伝わるか", zh: "它给人的感觉", hi: "यह कैसे सामने आता है", ar: "كيف يظهر",
  },
  "wsh.steer.pitch": {
    en: "Manner, not permissions. Steering never touches identity, boundaries, age-gating, or what the profile may be asked to do.", es: "Maneras, no permisos. El ajuste nunca toca la identidad, los límites, el control de edad ni lo que se le puede pedir al perfil.", fr: "La manière, pas les permissions. Le réglage ne touche jamais l'identité, les limites, le contrôle d'âge, ni ce qu'on peut demander au profil.", de: "Art, nicht Rechte. Die Steuerung berührt nie Identität, Grenzen, Altersprüfung oder das, worum das Profil gebeten werden darf.", pt: "Maneiras, não permissões. O ajuste nunca toca a identidade, os limites, o controlo de idade, nem o que se pode pedir ao perfil.", it: "Modi, non permessi. La regolazione non tocca mai identità, confini, verifica dell'età, o cosa si può chiedere al profilo.", ja: "権限ではなく物腰の設定です。ステアリングが、身元・境界・年齢確認・プロフィールに頼めることに触れることはありません。", zh: "调的是态度，不是权限。这些旋钮从不触及身份、边界、年龄限制，也不改变可以要求资料做什么。", hi: "यह ढंग है, अनुमतियाँ नहीं। स्टीयरिंग कभी पहचान, सीमाओं, आयु-द्वार, या प्रोफ़ाइल से क्या माँगा जा सकता है — इन्हें नहीं छूती।", ar: "أسلوب لا صلاحيات. التوجيه لا يمسّ الهوية ولا الحدود ولا بوابة العمر ولا ما يجوز أن يُطلب من الملف.",
  },
  "wsh.steer.noadult": {
    en: "This is not an adult-mode profile, so the intimacy dial does not exist here at all.", es: "Este no es un perfil en modo adulto, así que el dial de intimidad no existe aquí en absoluto.", fr: "Ce n'est pas un profil en mode adulte, donc le réglage d'intimité n'existe pas ici du tout.", de: "Dies ist kein Profil im Erwachsenenmodus, daher gibt es den Intimitätsregler hier gar nicht.", pt: "Este não é um perfil em modo adulto, por isso o botão de intimidade não existe aqui de todo.", it: "Questo non è un profilo in modalità adulti, quindi la manopola dell'intimità qui non esiste affatto.", ja: "これはアダルトモードのプロフィールではないため、親密さのつまみはここには存在しません。", zh: "这不是成人模式的资料，因此这里根本不存在亲密度旋钮。", hi: "यह वयस्क-मोड प्रोफ़ाइल नहीं है, इसलिए यहाँ अंतरंगता डायल है ही नहीं।", ar: "هذا ليس ملفًا في وضع البالغين، لذا لا وجود لقرص الحميمية هنا إطلاقًا.",
  },
  "wsh.knows": {
    en: "What it knows", es: "Lo que sabe", fr: "Ce qu'il sait", de: "Was es weiß", pt: "O que sabe", it: "Cosa sa", ja: "何を知っているか", zh: "它知道什么", hi: "यह क्या जानता है", ar: "ما يعرفه",
  },
  "wsh.knows.pitch": {
    en: "Source material: the writing, conversations and life events the persona is built on.", es: "Material de origen: los escritos, conversaciones y hechos de vida sobre los que se construye la persona.", fr: "Matière première : les écrits, conversations et événements de vie sur lesquels le personnage est bâti.", de: "Quellmaterial: die Texte, Gespräche und Lebensereignisse, auf denen die Persona aufbaut.", pt: "Material de origem: os escritos, conversas e acontecimentos de vida sobre os quais a persona é construída.", it: "Materiale d'origine: scritti, conversazioni ed eventi di vita su cui è costruita la persona.", ja: "素材：このペルソナが築かれている文章、会話、人生の出来事。", zh: "源材料：这个人格所依托的文字、对话与人生事件。", hi: "स्रोत सामग्री: वे लेख, बातचीत और जीवन-घटनाएँ जिन पर यह व्यक्तित्व बना है।", ar: "المادة المصدر: الكتابات والمحادثات وأحداث الحياة التي بُنيت عليها الشخصية.",
  },
  "wsh.knows.what.ph": {
    en: "what it is", es: "qué es", fr: "ce que c'est", de: "was es ist", pt: "o que é", it: "cos'è", ja: "それが何か", zh: "这是什么", hi: "यह क्या है", ar: "ما هو",
  },
  "wsh.knows.body.ph": {
    en: "the material itself", es: "el material en sí", fr: "la matière elle-même", de: "das Material selbst", pt: "o próprio material", it: "il materiale stesso", ja: "素材そのもの", zh: "材料本身", hi: "स्वयं सामग्री", ar: "المادة نفسها",
  },
  "wsh.knows.add": {
    en: "Add it", es: "Añadirlo", fr: "L'ajouter", de: "Hinzufügen", pt: "Adicioná-lo", it: "Aggiungilo", ja: "追加する", zh: "添加", hi: "जोड़ें", ar: "أضفه",
  },
  "wsh.knows.none": {
    en: "Nothing added yet.", es: "Nada añadido todavía.", fr: "Rien d'ajouté pour l'instant.", de: "Noch nichts hinzugefügt.", pt: "Nada adicionado ainda.", it: "Ancora niente aggiunto.", ja: "まだ何も追加されていません。", zh: "尚未添加任何内容。", hi: "अभी कुछ नहीं जोड़ा गया।", ar: "لم يُضف شيء بعد.",
  },
  "wsh.knows.sealed": {
    en: "Sealed in the vault. Only the reference is held here.", es: "Sellado en la bóveda. Aquí solo se guarda la referencia.", fr: "Scellé dans le coffre. Seule la référence est conservée ici.", de: "Im Tresor versiegelt. Hier wird nur die Referenz gehalten.", pt: "Selado no cofre. Só a referência é guardada aqui.", it: "Sigillato nel caveau. Qui si conserva solo il riferimento.", ja: "保管庫に封印済み。ここに保持されるのは参照だけです。", zh: "已封入保险库。此处只保存引用。", hi: "तिजोरी में सील। यहाँ केवल संदर्भ रखा गया है।", ar: "مختوم في الخزنة. لا يُحفظ هنا سوى المرجع.",
  },
  "wsh.knows.clear": {
    en: "Stored in the clear on this deployment — that is what you are looking at.", es: "Almacenado en claro en este despliegue — eso es lo que estás viendo.", fr: "Stocké en clair sur ce déploiement — c'est ce que vous avez sous les yeux.", de: "Auf diesem Deployment im Klartext gespeichert — genau das sehen Sie hier.", pt: "Guardado em claro neste deployment — é isso que está a ver.", it: "Memorizzato in chiaro su questo deployment — è proprio ciò che stai guardando.", ja: "この配備では平文で保存されています — いま見ているのがそれです。", zh: "在本部署上以明文存储 — 你看到的就是它。", hi: "इस डिप्लॉयमेंट पर खुले रूप में संग्रहित — आप वही देख रहे हैं।", ar: "مخزّن بلا تشفير على هذا النشر — وهذا ما تنظر إليه.",
  },
  "wsh.spec": {
    en: "Who it hands work to", es: "A quién pasa el trabajo", fr: "À qui il confie le travail", de: "An wen es Arbeit weitergibt", pt: "A quem passa o trabalho", it: "A chi passa il lavoro", ja: "仕事を誰に渡すか", zh: "它把活交给谁", hi: "यह काम किसे सौंपता है", ar: "لمن يسلّم العمل",
  },
  "wsh.spec.pitch": {
    en: "A domain, and the profile that knows more about it. A question in that domain goes there instead of being guessed at here.", es: "Un dominio, y el perfil que sabe más de él. Una pregunta de ese dominio va allí en vez de adivinarse aquí.", fr: "Un domaine, et le profil qui en sait plus. Une question dans ce domaine y va au lieu d'être devinée ici.", de: "Ein Fachgebiet und das Profil, das mehr davon versteht. Eine Frage aus dem Gebiet geht dorthin, statt hier geraten zu werden.", pt: "Um domínio, e o perfil que sabe mais dele. Uma pergunta desse domínio vai para lá em vez de ser adivinhada aqui.", it: "Un dominio, e il profilo che ne sa di più. Una domanda in quel dominio va lì invece di essere indovinata qui.", ja: "ある領域と、その領域により詳しいプロフィール。その領域の問いは、ここで推測されるのではなくそちらへ回されます。", zh: "一个领域，以及更懂这个领域的资料。该领域的问题会转过去，而不是在这里靠猜。", hi: "एक क्षेत्र, और वह प्रोफ़ाइल जो उसके बारे में अधिक जानती है। उस क्षेत्र का प्रश्न यहाँ अनुमान लगाने के बजाय वहाँ जाता है।", ar: "مجال، والملف الذي يعرف عنه أكثر. السؤال في ذلك المجال يذهب إلى هناك بدل أن يُخمَّن هنا.",
  },
  "wsh.spec.domain.ph": {
    en: "a domain, e.g. plumbing", es: "un dominio, p. ej. fontanería", fr: "un domaine, p. ex. plomberie", de: "ein Gebiet, z. B. Sanitär", pt: "um domínio, p. ex. canalização", it: "un dominio, es. idraulica", ja: "領域（例: 配管）", zh: "一个领域，如管道维修", hi: "एक क्षेत्र, जैसे नलसाज़ी", ar: "مجال، مثل السباكة",
  },
  "wsh.spec.id.ph": {
    en: "the specialist's profile id", es: "el id de perfil del especialista", fr: "l'id de profil du spécialiste", de: "die Profil-Id des Spezialisten", pt: "o id de perfil do especialista", it: "l'id di profilo dello specialista", ja: "専門家のプロフィールID", zh: "该专家的资料ID", hi: "विशेषज्ञ की प्रोफ़ाइल आईडी", ar: "معرّف ملف المختص",
  },
  "wsh.spec.attach": {
    en: "Attach", es: "Adjuntar", fr: "Rattacher", de: "Anhängen", pt: "Anexar", it: "Collega", ja: "紐付ける", zh: "挂接", hi: "जोड़ें", ar: "أرفق",
  },
  "wsh.spec.none": {
    en: "Nothing handed on.", es: "Nada delegado.", fr: "Rien de transmis.", de: "Nichts weitergegeben.", pt: "Nada delegado.", it: "Niente passato ad altri.", ja: "渡しているものはありません。", zh: "尚未转交任何事。", hi: "कुछ नहीं सौंपा गया।", ar: "لم يُسلَّم شيء.",
  },
  "wsh.exp": {
    en: "What it has done", es: "Lo que ha hecho", fr: "Ce qu'il a fait", de: "Was es getan hat", pt: "O que fez", it: "Cosa ha fatto", ja: "何をしてきたか", zh: "它做过什么", hi: "इसने क्या किया है", ar: "ما فعله",
  },
  "wsh.exp.pitch": {
    en: "Replaced whole rather than edited row by row — a history is a statement, not a set of fields.", es: "Se reemplaza entero en vez de editarse fila a fila — una trayectoria es una declaración, no un conjunto de campos.", fr: "Remplacé en entier plutôt que modifié ligne par ligne — un parcours est une déclaration, pas un ensemble de champs.", de: "Ganz ersetzt statt Zeile für Zeile bearbeitet — ein Werdegang ist eine Aussage, kein Satz Felder.", pt: "Substituído por inteiro em vez de editado linha a linha — um percurso é uma declaração, não um conjunto de campos.", it: "Sostituito per intero invece che modificato riga per riga — una storia è una dichiarazione, non un insieme di campi.", ja: "行ごとの編集ではなく丸ごと差し替えます — 経歴はフィールドの集まりではなく、ひとつの表明だからです。", zh: "整体替换，而非逐行编辑 — 一段履历是一份声明，不是一组字段。", hi: "पंक्ति-दर-पंक्ति संपादन के बजाय पूरा बदला जाता है — इतिहास एक कथन है, फ़ील्डों का समूह नहीं।", ar: "يُستبدل كاملًا لا يُحرَّر سطرًا سطرًا — السيرة بيان لا مجموعة حقول.",
  },
  "wsh.exp.title.ph": {
    en: "title", es: "cargo", fr: "intitulé", de: "Titel", pt: "cargo", it: "titolo", ja: "肩書", zh: "职位", hi: "पद", ar: "المسمى",
  },
  "wsh.exp.where.ph": {
    en: "where", es: "dónde", fr: "où", de: "wo", pt: "onde", it: "dove", ja: "所属", zh: "在哪里", hi: "कहाँ", ar: "أين",
  },
  "wsh.exp.period.ph": {
    en: "period, e.g. 2011–2019", es: "periodo, p. ej. 2011–2019", fr: "période, p. ex. 2011–2019", de: "Zeitraum, z. B. 2011–2019", pt: "período, p. ex. 2011–2019", it: "periodo, es. 2011–2019", ja: "期間（例: 2011–2019）", zh: "期间，如 2011–2019", hi: "अवधि, जैसे 2011–2019", ar: "الفترة، مثل 2011–2019",
  },
  "wsh.exp.add": {
    en: "Add a line", es: "Añadir una línea", fr: "Ajouter une ligne", de: "Eine Zeile hinzufügen", pt: "Adicionar uma linha", it: "Aggiungi una riga", ja: "1行追加", zh: "添加一条", hi: "एक पंक्ति जोड़ें", ar: "أضف سطرًا",
  },
  "wsh.body": {
    en: "What it speaks through", es: "A través de qué habla", fr: "Ce à travers quoi il parle", de: "Wodurch es spricht", pt: "Através de que fala", it: "Attraverso cosa parla", ja: "何を通して話すか", zh: "它通过什么发声", hi: "यह किसके माध्यम से बोलता है", ar: "عبر ماذا يتكلم",
  },
  "wsh.body.pitch": {
    en: "A speaker, an earpiece, a hologram, a robot. The distinction that matters is whether the form can hold a conversation or only relay one.", es: "Un altavoz, un auricular, un holograma, un robot. La distinción que importa es si la forma puede sostener una conversación o solo transmitirla.", fr: "Une enceinte, une oreillette, un hologramme, un robot. La distinction qui compte est de savoir si la forme peut tenir une conversation ou seulement la relayer.", de: "Ein Lautsprecher, ein Ohrhörer, ein Hologramm, ein Roboter. Der Unterschied, auf den es ankommt, ist, ob die Form ein Gespräch führen oder es nur weiterreichen kann.", pt: "Uma coluna, um auricular, um holograma, um robô. A distinção que importa é se a forma consegue manter uma conversa ou apenas transmiti-la.", it: "Un altoparlante, un auricolare, un ologramma, un robot. La distinzione che conta è se la forma può sostenere una conversazione o solo trasmetterla.", ja: "スピーカー、イヤホン、ホログラム、ロボット。肝心な違いは、その形が会話を担えるのか、ただ中継するだけなのかです。", zh: "音箱、耳机、全息影像、机器人。真正要紧的分别是：这个形态能不能自己撑起一场对话，还是只能转达。", hi: "एक स्पीकर, एक इयरपीस, एक होलोग्राम, एक रोबोट। जो फ़र्क़ मायने रखता है वह यह है कि वह रूप बातचीत कर सकता है या केवल पहुँचा सकता है।", ar: "سماعة، أو سماعة أذن، أو صورة مجسمة، أو آلي. الفارق المهم هو هل يستطيع هذا الشكل إدارة محادثة أم مجرد نقلها.",
  },
  "wsh.body.name.ph": {
    en: "what you call it", es: "cómo lo llamas", fr: "comment vous l'appelez", de: "wie Sie es nennen", pt: "como lhe chama", it: "come lo chiami", ja: "呼び名", zh: "你怎么称呼它", hi: "आप इसे क्या कहते हैं", ar: "بمَ تسميه",
  },
  "wsh.body.llm": {
    en: "can hold a conversation", es: "puede sostener una conversación", fr: "peut tenir une conversation", de: "kann ein Gespräch führen", pt: "consegue manter uma conversa", it: "può sostenere una conversazione", ja: "会話ができる", zh: "能进行对话", hi: "बातचीत कर सकता है", ar: "يستطيع إدارة محادثة",
  },
  "wsh.body.add": {
    en: "Add", es: "Añadir", fr: "Ajouter", de: "Hinzufügen", pt: "Adicionar", it: "Aggiungi", ja: "追加", zh: "添加", hi: "जोड़ें", ar: "أضف",
  },
  "wsh.fold": {
    en: "Fold it back in", es: "Reincorporarlo", fr: "Le réintégrer", de: "Wieder einarbeiten", pt: "Reincorporá-lo", it: "Reintegralo", ja: "取り込み直す", zh: "重新并入", hi: "इसे वापस समेटें", ar: "أعد دمجه",
  },
  "wsh.fold.pitch": {
    en: "Recompute the profile's own model from the history it already has. No body to send, and nothing to configure.", es: "Recalcula el modelo propio del perfil a partir del historial que ya tiene. No hay cuerpo que enviar ni nada que configurar.", fr: "Recalcule le modèle propre au profil à partir de l'historique qu'il possède déjà. Rien à envoyer, rien à configurer.", de: "Berechnet das eigene Modell des Profils aus der bereits vorhandenen Historie neu. Nichts zu senden und nichts zu konfigurieren.", pt: "Recalcula o modelo próprio do perfil a partir do histórico que já tem. Não há corpo para enviar nem nada para configurar.", it: "Ricalcola il modello proprio del profilo dalla storia che ha già. Niente da inviare e niente da configurare.", ja: "すでにある履歴から、プロフィール自身のモデルを再計算します。送るものも、設定するものもありません。", zh: "用它已有的历史重新计算这份资料自己的模型。没有要发送的内容，也没有要配置的东西。", hi: "जो इतिहास पहले से है उसी से प्रोफ़ाइल का अपना मॉडल फिर से गणना करता है। भेजने को कुछ नहीं, कॉन्फ़िगर करने को कुछ नहीं।", ar: "يعيد حساب نموذج الملف الخاص من التاريخ الموجود لديه أصلًا. لا شيء يُرسل ولا شيء يُهيَّأ.",
  },
  "wsh.fold.run": {
    en: "Run it", es: "Ejecutarlo", fr: "Lancer", de: "Ausführen", pt: "Executá-lo", it: "Eseguilo", ja: "実行する", zh: "运行", hi: "चलाएँ", ar: "شغّله",
  },
  "wsh.fold.count": {
    en: "{n} message{s} across {i} {people}.", es: "{n} mensajes con {i} {people}.", fr: "{n} messages auprès de {i} {people}.", de: "{n} Nachrichten über {i} {people}.", pt: "{n} mensagens com {i} {people}.", it: "{n} messaggi con {i} {people}.", ja: "{i}{people}にわたるメッセージ{n}件。", zh: "{i}{people}的{n}条消息。", hi: "{i} {people} के बीच {n} संदेश।", ar: "{n} رسائل عبر {i} {people}.",
  },
  "wsh.fold.computed": {
    en: "Computed {when}.", es: "Calculado {when}.", fr: "Calculé {when}.", de: "Berechnet {when}.", pt: "Calculado {when}.", it: "Calcolato {when}.", ja: "計算場所: {when}。", zh: "计算于{when}。", hi: "{when} पर गणना।", ar: "حُسب {when}.",
  },
  "wsh.see": {
    en: "Show it something", es: "Muéstrale algo", fr: "Montrez-lui quelque chose", de: "Zeigen Sie ihm etwas", pt: "Mostre-lhe algo", it: "Mostragli qualcosa", ja: "何かを見せる", zh: "给它看点东西", hi: "इसे कुछ दिखाएँ", ar: "أره شيئًا",
  },
  "wsh.see.pitch": {
    en: "Name what is in front of you and what you are trying to do, and the profile talks you through it hands-free.", es: "Nombra lo que tienes delante y lo que intentas hacer, y el perfil te guía sin usar las manos.", fr: "Nommez ce qui est devant vous et ce que vous essayez de faire, et le profil vous guide sans les mains.", de: "Benennen Sie, was vor Ihnen liegt und was Sie vorhaben, und das Profil führt Sie freihändig hindurch.", pt: "Diga o que tem à frente e o que está a tentar fazer, e o perfil guia-o sem usar as mãos.", it: "Nomina ciò che hai davanti e ciò che stai cercando di fare, e il profilo ti guida a mani libere.", ja: "目の前にあるものと、やろうとしていることを言えば、プロフィールが手を使わずに案内します。", zh: "说出你面前有什么、你想做什么，资料就会免提地一步步带你做。", hi: "बताएँ कि आपके सामने क्या है और आप क्या करना चाहते हैं, और प्रोफ़ाइल बिना हाथ लगाए आपको समझाती चलेगी।", ar: "سمِّ ما أمامك وما تحاول فعله، فيرشدك الملف خطوة بخطوة دون استخدام يديك.",
  },
  "wsh.see.scene.ph": {
    en: "what it can see, comma separated", es: "lo que puede ver, separado por comas", fr: "ce qu'il peut voir, séparé par des virgules", de: "was es sehen kann, kommagetrennt", pt: "o que consegue ver, separado por vírgulas", it: "cosa può vedere, separato da virgole", ja: "見えているもの（カンマ区切り）", zh: "它能看到什么，用逗号分隔", hi: "यह क्या देख सकता है, अल्पविराम से अलग", ar: "ما يمكنه رؤيته، مفصولًا بفواصل",
  },
  "wsh.see.goal.ph": {
    en: "what you are trying to do", es: "qué intentas hacer", fr: "ce que vous essayez de faire", de: "was Sie vorhaben", pt: "o que está a tentar fazer", it: "cosa stai cercando di fare", ja: "やろうとしていること", zh: "你想做什么", hi: "आप क्या करना चाह रहे हैं", ar: "ما تحاول فعله",
  },
  "wsh.see.ask": {
    en: "Ask", es: "Preguntar", fr: "Demander", de: "Fragen", pt: "Perguntar", it: "Chiedi", ja: "尋ねる", zh: "询问", hi: "पूछें", ar: "اسأل",
  },
  "wsh.see.recognised": {
    en: "Recognised {n}: {list}", es: "Reconocidos {n}: {list}", fr: "Reconnus {n} : {list}", de: "Erkannt {n}: {list}", pt: "Reconhecidos {n}: {list}", it: "Riconosciuti {n}: {list}", ja: "認識 {n}件: {list}", zh: "识别到{n}项: {list}", hi: "पहचाने गए {n}: {list}", ar: "تعرّف على {n}: {list}",
  },
  "rbt.title": {
    en: "Bodies", es: "Cuerpos", fr: "Corps", de: "Körper", pt: "Corpos", it: "Corpi", ja: "身体", zh: "身体", hi: "शरीर", ar: "الأجساد",
  },
  "rbt.lead": {
    en: "A profile can speak through a robot. The personality, the memory and the voice are the same ones — only the form of expression changes.", es: "Un perfil puede hablar a través de un robot. La personalidad, la memoria y la voz son las mismas — solo cambia la forma de expresión.", fr: "Un profil peut parler à travers un robot. La personnalité, la mémoire et la voix sont les mêmes — seule la forme d'expression change.", de: "Ein Profil kann durch einen Roboter sprechen. Persönlichkeit, Gedächtnis und Stimme sind dieselben — nur die Ausdrucksform ändert sich.", pt: "Um perfil pode falar através de um robô. A personalidade, a memória e a voz são as mesmas — só muda a forma de expressão.", it: "Un profilo può parlare attraverso un robot. La personalità, la memoria e la voce sono le stesse — cambia solo la forma di espressione.", ja: "プロフィールはロボットを通して話せます。人格も記憶も声も同じもので、変わるのは表現の形だけです。", zh: "资料可以通过机器人说话。性情、记忆与嗓音都是同一个 — 变的只是表达的形态。", hi: "प्रोफ़ाइल किसी रोबोट के माध्यम से बोल सकती है। व्यक्तित्व, स्मृति और आवाज़ वही रहती है — केवल अभिव्यक्ति का रूप बदलता है।", ar: "يمكن للملف أن يتكلم عبر آلي. الشخصية والذاكرة والصوت هي ذاتها — لا يتغير سوى شكل التعبير.",
  },
  "rbt.bind": {
    en: "Bind a body", es: "Vincular un cuerpo", fr: "Lier un corps", de: "Einen Körper binden", pt: "Vincular um corpo", it: "Vincola un corpo", ja: "身体を紐付ける", zh: "绑定一具身体", hi: "एक शरीर बाँधें", ar: "اربط جسدًا",
  },
  "rbt.bind.name.ph": {
    en: "what you call it", es: "cómo lo llamas", fr: "comment vous l'appelez", de: "wie Sie es nennen", pt: "como lhe chama", it: "come lo chiami", ja: "呼び名", zh: "你怎么称呼它", hi: "आप इसे क्या कहते हैं", ar: "بمَ تسميه",
  },
  "rbt.bind.pick": {
    en: "pick a model", es: "elige un modelo", fr: "choisissez un modèle", de: "Modell wählen", pt: "escolha um modelo", it: "scegli un modello", ja: "モデルを選ぶ", zh: "选择型号", hi: "मॉडल चुनें", ar: "اختر طرازًا",
  },
  "rbt.bind.go": {
    en: "Bind", es: "Vincular", fr: "Lier", de: "Binden", pt: "Vincular", it: "Vincola", ja: "紐付ける", zh: "绑定", hi: "बाँधें", ar: "اربط",
  },
  "rbt.invariant": {
    en: "Invariant across {across}.", es: "Invariante en {across}.", fr: "Invariant sur {across}.", de: "Invariant über {across}.", pt: "Invariante em {across}.", it: "Invariante su {across}.", ja: "{across}をまたいで不変。", zh: "在{across}间保持不变。", hi: "{across} में अपरिवर्तित।", ar: "ثابت عبر {across}.",
  },
  "rbt.market": {
    en: "The market", es: "El mercado", fr: "Le marché", de: "Der Markt", pt: "O mercado", it: "Il mercato", ja: "市場", zh: "市场", hi: "बाज़ार", ar: "السوق",
  },
  "rbt.market.line": {
    en: "{n} bodies from {m} makers. {note} Checked against what the makers were saying on {date}.", es: "{n} cuerpos de {m} fabricantes. {note} Contrastado con lo que decían los fabricantes el {date}.", fr: "{n} corps de {m} fabricants. {note} Vérifié d'après ce que disaient les fabricants le {date}.", de: "{n} Körper von {m} Herstellern. {note} Abgeglichen mit dem, was die Hersteller am {date} sagten.", pt: "{n} corpos de {m} fabricantes. {note} Confrontado com o que os fabricantes diziam a {date}.", it: "{n} corpi da {m} produttori. {note} Confrontato con quanto dicevano i produttori il {date}.", ja: "{m}社の{n}機種。{note} {date}時点でメーカーが公表していた内容と突き合わせています。", zh: "来自{m}家厂商的{n}款身体。{note} 已对照厂商在{date}的说法核实。", hi: "{m} निर्माताओं के {n} शरीर। {note} {date} को निर्माताओं के कथन से मिलान किया गया।", ar: "{n} أجساد من {m} صانعين. {note} قوبلت بما كان الصانعون يقولونه في {date}.",
  },
  "rbt.conn": {
    en: "Connections — skills and components", es: "Conexiones — habilidades y componentes", fr: "Connexions — compétences et composants", de: "Verbindungen — Fähigkeiten und Komponenten", pt: "Ligações — competências e componentes", it: "Connessioni — abilità e componenti", ja: "接続 — スキルと構成要素", zh: "连接 — 技能与组件", hi: "कनेक्शन — कौशल और घटक", ar: "الاتصالات — المهارات والمكونات",
  },
  "rbt.conn.pitch": {
    en: "Two different things a body is given. A task pack teaches it verbs: each task in the pack becomes commandable, checked against what that model of body can physically do — a vacuum cannot be taught to fetch, and the refusal says which capability is missing rather than accepting the install and failing later. A connector is a service the profile's agents can collect from, act on, or produce into.", es: "Dos cosas distintas que se le dan a un cuerpo. Un paquete de tareas le enseña verbos: cada tarea del paquete se vuelve ordenable, contrastada con lo que ese modelo de cuerpo puede hacer físicamente — a una aspiradora no se le puede enseñar a traer cosas, y el rechazo dice qué capacidad falta en vez de aceptar la instalación y fallar después. Un conector es un servicio del que los agentes del perfil pueden recoger, sobre el que actuar, o al que producir.", fr: "Deux choses distinctes que l'on donne à un corps. Un pack de tâches lui apprend des verbes : chaque tâche du pack devient commandable, vérifiée par rapport à ce que ce modèle de corps peut physiquement faire — on ne peut pas apprendre à un aspirateur à rapporter, et le refus dit quelle capacité manque au lieu d'accepter l'installation et d'échouer plus tard. Un connecteur est un service dont les agents du profil peuvent collecter, sur lequel agir, ou vers lequel produire.", de: "Zwei verschiedene Dinge, die ein Körper bekommt. Ein Aufgabenpaket bringt ihm Verben bei: jede Aufgabe darin wird befehlbar, geprüft gegen das, was dieses Körpermodell physisch kann — einem Staubsauger kann man Apportieren nicht beibringen, und die Ablehnung nennt die fehlende Fähigkeit, statt die Installation anzunehmen und später zu scheitern. Ein Konnektor ist ein Dienst, aus dem die Agenten des Profils sammeln, auf den sie wirken oder in den sie produzieren können.", pt: "Duas coisas diferentes que se dão a um corpo. Um pacote de tarefas ensina-lhe verbos: cada tarefa do pacote torna-se comandável, confrontada com o que aquele modelo de corpo consegue fazer fisicamente — não se ensina um aspirador a ir buscar, e a recusa diz que capacidade falta em vez de aceitar a instalação e falhar depois. Um conector é um serviço de onde os agentes do perfil podem recolher, sobre o qual agir, ou para o qual produzir.", it: "Due cose diverse che si danno a un corpo. Un pacchetto di compiti gli insegna verbi: ogni compito del pacchetto diventa comandabile, verificato rispetto a ciò che quel modello di corpo può fare fisicamente — a un aspirapolvere non si può insegnare a riportare, e il rifiuto dice quale capacità manca invece di accettare l'installazione e fallire dopo. Un connettore è un servizio da cui gli agenti del profilo possono raccogliere, su cui agire, o verso cui produrre.", ja: "身体に与えられるものは二種類あります。タスクパックは動詞を教えます：パック内の各タスクが命令可能になり、その機種の身体が物理的に何をできるかと突き合わせて検査されます — 掃除機に「取ってくる」ことは教えられず、拒否は不足している能力を告げます。インストールを受理して後で失敗させたりはしません。コネクタは、プロフィールのエージェントが情報を集め、働きかけ、成果を書き出せるサービスです。", zh: "交给身体的是两样不同的东西。任务包教它动词：包中每项任务都变得可命令，并对照该型号身体在物理上做得到什么来核验 — 吸尘器学不会取物，拒绝时会说明缺哪项能力，而不是先接受安装、之后才失败。连接器则是一项服务，资料的代理可以从中收集、对其操作，或向其产出。", hi: "शरीर को दो अलग चीज़ें दी जाती हैं। टास्क पैक उसे क्रियाएँ सिखाता है: पैक का हर कार्य आदेश-योग्य बन जाता है, और जाँचा जाता है कि उस मॉडल का शरीर भौतिक रूप से क्या कर सकता है — वैक्यूम को «लाकर देना» नहीं सिखाया जा सकता, और इनकार बताता है कि कौन-सी क्षमता कम है, न कि इंस्टॉल स्वीकार कर बाद में विफल हो। कनेक्टर एक सेवा है जिससे प्रोफ़ाइल के एजेंट एकत्र कर सकते हैं, जिस पर कार्य कर सकते हैं, या जिसमें उत्पादन कर सकते हैं।", ar: "شيئان مختلفان يُمنحان للجسد. حزمة المهام تعلّمه أفعالًا: كل مهمة في الحزمة تصير قابلة للأمر، ويُتحقق منها مقابل ما يستطيع ذلك الطراز فعله فيزيائيًا — لا يمكن تعليم مكنسة أن تُحضر، والرفض يقول أي قدرة ناقصة بدل قبول التثبيت ثم الفشل لاحقًا. والموصّل خدمة يمكن لوكلاء الملف الجمع منها أو التصرف عليها أو الإنتاج إليها.",
  },
  "rbt.conn.shelf": {
    en: "Skills you can fit", es: "Habilidades que puedes instalar", fr: "Compétences installables", de: "Fähigkeiten, die Sie einbauen können", pt: "Competências que pode instalar", it: "Abilità che puoi montare", ja: "取り付けられるスキル", zh: "你可以装配的技能", hi: "जो कौशल आप लगा सकते हैं", ar: "مهارات يمكنك تركيبها",
  },
  "rbt.conn.shelf.none": {
    en: "No robot task packs published yet.", es: "Todavía no hay paquetes de tareas para robots publicados.", fr: "Aucun pack de tâches robot publié pour l'instant.", de: "Noch keine Roboter-Aufgabenpakete veröffentlicht.", pt: "Ainda não há pacotes de tarefas para robôs publicados.", it: "Nessun pacchetto di compiti per robot pubblicato finora.", ja: "ロボット用タスクパックはまだ公開されていません。", zh: "尚未发布任何机器人任务包。", hi: "अभी कोई रोबोट टास्क पैक प्रकाशित नहीं।", ar: "لم تُنشر حزم مهام آلية بعد.",
  },
  "rbt.conn.fit": {
    en: "Fit to the open body", es: "Instalar en el cuerpo abierto", fr: "Installer sur le corps ouvert", de: "In den geöffneten Körper einbauen", pt: "Instalar no corpo aberto", it: "Monta sul corpo aperto", ja: "開いている身体に取り付ける", zh: "装配到已打开的身体", hi: "खुले शरीर पर लगाएँ", ar: "ركّبها على الجسد المفتوح",
  },
  "rbt.conn.openfirst": {
    en: "Open a bound body below first — a task pack is fitted to a particular machine, not to the profile.", es: "Abre primero un cuerpo vinculado abajo — un paquete de tareas se instala en una máquina concreta, no en el perfil.", fr: "Ouvrez d'abord un corps lié ci-dessous — un pack de tâches s'installe sur une machine précise, pas sur le profil.", de: "Öffnen Sie zuerst unten einen gebundenen Körper — ein Aufgabenpaket wird in eine bestimmte Maschine eingebaut, nicht ins Profil.", pt: "Abra primeiro um corpo vinculado abaixo — um pacote de tarefas instala-se numa máquina concreta, não no perfil.", it: "Apri prima un corpo vincolato qui sotto — un pacchetto di compiti si monta su una macchina precisa, non sul profilo.", ja: "まず下で紐付け済みの身体を開いてください — タスクパックはプロフィールではなく、特定の機体に取り付けられます。", zh: "请先在下方打开一具已绑定的身体 — 任务包装配到具体的机器上，而不是资料上。", hi: "पहले नीचे कोई बँधा हुआ शरीर खोलें — टास्क पैक किसी ख़ास मशीन पर लगता है, प्रोफ़ाइल पर नहीं।", ar: "افتح أولًا جسدًا مربوطًا أدناه — حزمة المهام تُركَّب على آلة بعينها لا على الملف.",
  },
  "rbt.conn.fitted": {
    en: "What is fitted", es: "Qué está instalado", fr: "Ce qui est installé", de: "Was eingebaut ist", pt: "O que está instalado", it: "Cosa è montato", ja: "取り付け済みのもの", zh: "已装配的内容", hi: "क्या लगा हुआ है", ar: "ما هو مركَّب",
  },
  "rbt.conn.fitted.none": {
    en: "Nothing installed.", es: "Nada instalado.", fr: "Rien d'installé.", de: "Nichts installiert.", pt: "Nada instalado.", it: "Niente installato.", ja: "何も入っていません。", zh: "尚未安装任何内容。", hi: "कुछ स्थापित नहीं।", ar: "لا شيء مثبّت.",
  },
  "rbt.conn.remove": {
    en: "Remove", es: "Quitar", fr: "Retirer", de: "Entfernen", pt: "Remover", it: "Rimuovi", ja: "取り外す", zh: "移除", hi: "हटाएँ", ar: "أزل",
  },
  "rbt.conn.components": {
    en: "Components it can reach", es: "Componentes a los que puede llegar", fr: "Composants qu'il peut atteindre", de: "Komponenten, die es erreichen kann", pt: "Componentes que consegue alcançar", it: "Componenti che può raggiungere", ja: "到達できる構成要素", zh: "它能触及的组件", hi: "जिन घटकों तक यह पहुँच सकता है", ar: "المكونات التي يمكنه بلوغها",
  },
  "rbt.conn.counts": {
    en: "{apps} apps across {providers} providers.", es: "{apps} apps de {providers} proveedores.", fr: "{apps} applis chez {providers} fournisseurs.", de: "{apps} Apps über {providers} Anbieter.", pt: "{apps} apps de {providers} fornecedores.", it: "{apps} app da {providers} provider.", ja: "{providers}社にまたがる{apps}個のアプリ。", zh: "{providers}家提供方的{apps}个应用。", hi: "{providers} प्रदाताओं के {apps} ऐप।", ar: "{apps} تطبيقات عبر {providers} مزودين.",
  },
  "rbt.bound": {
    en: "Bound bodies", es: "Cuerpos vinculados", fr: "Corps liés", de: "Gebundene Körper", pt: "Corpos vinculados", it: "Corpi vincolati", ja: "紐付け済みの身体", zh: "已绑定的身体", hi: "बँधे हुए शरीर", ar: "الأجساد المربوطة",
  },
  "rbt.bound.line": {
    en: "{model} · {status} · bound {date}", es: "{model} · {status} · vinculado {date}", fr: "{model} · {status} · lié {date}", de: "{model} · {status} · gebunden {date}", pt: "{model} · {status} · vinculado {date}", it: "{model} · {status} · vincolato {date}", ja: "{model} · {status} · 紐付け {date}", zh: "{model} · {status} · 绑定于{date}", hi: "{model} · {status} · बँधा {date}", ar: "{model} · {status} · رُبط {date}",
  },
  "rbt.bound.open": {
    en: "Open", es: "Abrir", fr: "Ouvrir", de: "Öffnen", pt: "Abrir", it: "Apri", ja: "開く", zh: "打开", hi: "खोलें", ar: "افتح",
  },
  "rbt.bound.unbind": {
    en: "Unbind", es: "Desvincular", fr: "Délier", de: "Lösen", pt: "Desvincular", it: "Svincola", ja: "解除", zh: "解绑", hi: "अलग करें", ar: "افصل",
  },
  "rbt.tell": {
    en: "Tell it to do something", es: "Dile que haga algo", fr: "Dites-lui de faire quelque chose", de: "Sagen Sie ihm, etwas zu tun", pt: "Diga-lhe para fazer algo", it: "Digli di fare qualcosa", ja: "何かをするよう指示する", zh: "叫它做点什么", hi: "इसे कुछ करने को कहें", ar: "اطلب منه فعل شيء",
  },
  "rbt.tell.pitch": {
    en: "What this body accepts. Not everything a robot can be told — what this model is permitted, plus any task modules it has learned.", es: "Lo que este cuerpo acepta. No todo lo que se le puede decir a un robot — lo que este modelo tiene permitido, más los módulos de tareas que haya aprendido.", fr: "Ce que ce corps accepte. Pas tout ce qu'on peut dire à un robot — ce que ce modèle a le droit de faire, plus les modules de tâches qu'il a appris.", de: "Was dieser Körper annimmt. Nicht alles, was man einem Roboter sagen kann — was diesem Modell erlaubt ist, plus die Aufgabenmodule, die es gelernt hat.", pt: "O que este corpo aceita. Não tudo o que se pode dizer a um robô — o que este modelo tem permitido, mais os módulos de tarefas que aprendeu.", it: "Cosa accetta questo corpo. Non tutto ciò che si può dire a un robot — ciò che a questo modello è permesso, più i moduli di compiti che ha imparato.", ja: "この身体が受け付けるもの。ロボット一般に言えることすべてではなく、この機種に許可されていること、それに学習したタスクモジュールです。", zh: "这具身体接受什么。不是机器人能被吩咐的一切 — 而是这个型号被允许做的，加上它学过的任务模块。", hi: "यह शरीर क्या स्वीकारता है। वह सब नहीं जो किसी रोबोट से कहा जा सकता है — बल्कि इस मॉडल को जिसकी अनुमति है, साथ ही जो टास्क मॉड्यूल इसने सीखे हैं।", ar: "ما يقبله هذا الجسد. ليس كل ما يمكن أن يُقال لآلي — بل ما يُسمح به لهذا الطراز، إضافة إلى وحدات المهام التي تعلّمها.",
  },
  "rbt.tell.say.ph": {
    en: "say something about…", es: "di algo sobre…", fr: "dis quelque chose sur…", de: "sag etwas über…", pt: "diz algo sobre…", it: "di' qualcosa su…", ja: "…について何か言う", zh: "说点关于…", hi: "…के बारे में कुछ कहो", ar: "قل شيئًا عن…",
  },
  "rbt.tell.say": {
    en: "Say it", es: "Dilo", fr: "Dis-le", de: "Sag es", pt: "Diz", it: "Dillo", ja: "言わせる", zh: "说出来", hi: "कहो", ar: "قله",
  },
  "rbt.learned": {
    en: "What it has learned", es: "Lo que ha aprendido", fr: "Ce qu'il a appris", de: "Was es gelernt hat", pt: "O que aprendeu", it: "Cosa ha imparato", ja: "学んだこと", zh: "它学到了什么", hi: "इसने क्या सीखा", ar: "ما تعلّمه",
  },
  "rbt.learned.none": {
    en: "No task modules installed. A robot pack adds verbs to the list above, checked against what this body can physically do.", es: "No hay módulos de tareas instalados. Un paquete de robot añade verbos a la lista de arriba, contrastados con lo que este cuerpo puede hacer físicamente.", fr: "Aucun module de tâches installé. Un pack robot ajoute des verbes à la liste ci-dessus, vérifiés par rapport à ce que ce corps peut physiquement faire.", de: "Keine Aufgabenmodule installiert. Ein Roboterpaket fügt der Liste oben Verben hinzu, geprüft gegen das, was dieser Körper physisch kann.", pt: "Nenhum módulo de tarefas instalado. Um pacote de robô acrescenta verbos à lista acima, confrontados com o que este corpo consegue fazer fisicamente.", it: "Nessun modulo di compiti installato. Un pacchetto robot aggiunge verbi alla lista sopra, verificati rispetto a ciò che questo corpo può fare fisicamente.", ja: "タスクモジュールは入っていません。ロボットパックは上のリストに動詞を追加し、この身体が物理的に何をできるかと突き合わせて検査されます。", zh: "未安装任务模块。机器人包会向上面的列表添加动词，并对照这具身体在物理上做得到什么来核验。", hi: "कोई टास्क मॉड्यूल स्थापित नहीं। रोबोट पैक ऊपर की सूची में क्रियाएँ जोड़ता है, जो इस शरीर की भौतिक क्षमता के विरुद्ध जाँची जाती हैं।", ar: "لا وحدات مهام مثبّتة. حزمة الآلي تضيف أفعالًا إلى القائمة أعلاه، مفحوصة مقابل ما يستطيع هذا الجسد فعله فيزيائيًا.",
  },
  "rbt.learned.from": {
    en: "from {pack}", es: "de {pack}", fr: "de {pack}", de: "aus {pack}", pt: "de {pack}", it: "da {pack}", ja: "出典: {pack}", zh: "来自{pack}", hi: "{pack} से", ar: "من {pack}",
  },
  "rbt.steer": {
    en: "How it comes across", es: "Cómo se presenta", fr: "Comment il se présente", de: "Wie es rüberkommt", pt: "Como se apresenta", it: "Come si presenta", ja: "どう伝わるか", zh: "它给人的感觉", hi: "यह कैसे सामने आता है", ar: "كيف يظهر",
  },
  "rbt.steer.pitch": {
    en: "Steering shapes manner, not permissions. It never touches identity, boundaries, age-gating or what the body may be told to do.", es: "El ajuste da forma a la manera, no a los permisos. Nunca toca la identidad, los límites, el control de edad ni lo que se le puede ordenar al cuerpo.", fr: "Le réglage façonne la manière, pas les permissions. Il ne touche jamais l'identité, les limites, le contrôle d'âge ni ce qu'on peut ordonner au corps.", de: "Die Steuerung formt die Art, nicht die Rechte. Sie berührt nie Identität, Grenzen, Altersprüfung oder das, was dem Körper aufgetragen werden darf.", pt: "O ajuste molda a maneira, não as permissões. Nunca toca a identidade, os limites, o controlo de idade nem o que se pode ordenar ao corpo.", it: "La regolazione plasma i modi, non i permessi. Non tocca mai identità, confini, verifica dell'età o cosa si può ordinare al corpo.", ja: "ステアリングが形づくるのは物腰であって権限ではありません。身元・境界・年齢確認・身体に命じてよいことに触れることは決してありません。", zh: "这些旋钮塑造的是态度，不是权限。它们从不触及身份、边界、年龄限制，也不改变可以吩咐这具身体做什么。", hi: "स्टीयरिंग ढंग को आकार देती है, अनुमतियों को नहीं। यह कभी पहचान, सीमाओं, आयु-द्वार या शरीर को क्या कहा जा सकता है — इन्हें नहीं छूती।", ar: "التوجيه يشكّل الأسلوب لا الصلاحيات. ولا يمسّ أبدًا الهوية ولا الحدود ولا بوابة العمر ولا ما يجوز أن يُؤمر به الجسد.",
  },
  "rbt.steer.becomes": {
    en: "What that becomes in a body", es: "En qué se convierte eso en un cuerpo", fr: "Ce que cela devient dans un corps", de: "Was daraus in einem Körper wird", pt: "No que isso se torna num corpo", it: "Cosa diventa in un corpo", ja: "それが身体では何になるか", zh: "这在身体上会变成什么", hi: "शरीर में यह क्या बन जाता है", ar: "ما يصير إليه ذلك في جسد",
  },
  "rbt.log": {
    en: "Everything it has been told", es: "Todo lo que se le ha dicho", fr: "Tout ce qu'on lui a dit", de: "Alles, was ihm gesagt wurde", pt: "Tudo o que lhe foi dito", it: "Tutto ciò che gli è stato detto", ja: "命じられたことすべて", zh: "它被吩咐过的一切", hi: "इसे जो कुछ कहा गया", ar: "كل ما قيل له",
  },
  "rbt.log.pitch": {
    en: "Owner-only, and kept for the obvious reason: a body in somebody's home should not be able to be sent anywhere with no record.", es: "Solo para el propietario, y guardado por la razón obvia: un cuerpo en casa de alguien no debería poder ser enviado a ningún sitio sin registro.", fr: "Réservé au propriétaire, et conservé pour la raison évidente : un corps chez quelqu'un ne devrait pas pouvoir être envoyé où que ce soit sans trace.", de: "Nur für den Besitzer, und aus dem offensichtlichen Grund aufbewahrt: ein Körper in jemandes Wohnung sollte nirgendwohin geschickt werden können, ohne dass es verzeichnet wird.", pt: "Só para o proprietário, e guardado pela razão óbvia: um corpo na casa de alguém não deveria poder ser enviado a lado nenhum sem registo.", it: "Solo per il proprietario, e conservato per la ragione ovvia: un corpo in casa di qualcuno non dovrebbe poter essere mandato da nessuna parte senza traccia.", ja: "所有者のみが見られ、理由は明白です：誰かの家にある身体が、記録も残さずどこかへ送られてよいはずがありません。", zh: "仅所有者可见，理由显而易见：一具身处别人家中的身体，不该能够在毫无记录的情况下被派往任何地方。", hi: "केवल स्वामी के लिए, और स्पष्ट कारण से रखा गया: किसी के घर में मौजूद शरीर को बिना किसी रिकॉर्ड के कहीं भी नहीं भेजा जा सकना चाहिए।", ar: "للمالك وحده، ويُحفظ لسبب بديهي: جسد في بيت أحدهم لا ينبغي أن يمكن إرساله إلى أي مكان دون سجل.",
  },
  "rbt.log.none": {
    en: "Nothing yet.", es: "Nada todavía.", fr: "Rien pour l'instant.", de: "Noch nichts.", pt: "Nada ainda.", it: "Ancora niente.", ja: "まだ何もありません。", zh: "尚无。", hi: "अभी कुछ नहीं।", ar: "لا شيء بعد.",
  },
  "exc.title": {
    en: "Exchanges", es: "Intercambios", fr: "Échanges", de: "Austausch", pt: "Trocas", it: "Scambi", ja: "取引", zh: "交换", hi: "आदान-प्रदान", ar: "التبادلات",
  },
  "exc.lead": {
    en: "A document before it is a transfer. Both sides sign the same manifest, and only then does anything move.", es: "Un documento antes de ser una transferencia. Ambas partes firman el mismo manifiesto, y solo entonces se mueve algo.", fr: "Un document avant d'être un transfert. Les deux parties signent le même manifeste, et alors seulement quelque chose bouge.", de: "Ein Dokument, bevor es eine Übertragung ist. Beide Seiten unterschreiben dasselbe Manifest, und erst dann bewegt sich etwas.", pt: "Um documento antes de ser uma transferência. Ambos os lados assinam o mesmo manifesto, e só então algo se move.", it: "Un documento prima di essere un trasferimento. Entrambe le parti firmano lo stesso manifesto, e solo allora qualcosa si muove.", ja: "移転である前に、まず文書です。双方が同じ明細に署名し、そのあとで初めて何かが動きます。", zh: "在成为转移之前，它首先是一份文件。双方签署同一份清单，之后才会有任何东西移动。", hi: "हस्तांतरण होने से पहले यह एक दस्तावेज़ है। दोनों पक्ष एक ही सूची पर हस्ताक्षर करते हैं, और तभी कुछ हिलता है।", ar: "وثيقة قبل أن يكون نقلًا. يوقّع الطرفان البيان نفسه، وعندئذ فقط يتحرك شيء.",
  },
  "exc.how": {
    en: "How this works", es: "Cómo funciona esto", fr: "Comment cela fonctionne", de: "Wie das funktioniert", pt: "Como isto funciona", it: "Come funziona", ja: "仕組み", zh: "运作方式", hi: "यह कैसे काम करता है", ar: "كيف يعمل هذا",
  },
  "exc.propose": {
    en: "Propose one", es: "Proponer uno", fr: "En proposer un", de: "Einen vorschlagen", pt: "Propor um", it: "Proponine uno", ja: "提案する", zh: "提出一份", hi: "एक प्रस्तावित करें", ar: "اقترح واحدًا",
  },
  "exc.guest.ph": {
    en: "the other party's id", es: "el id de la otra parte", fr: "l'id de l'autre partie", de: "die ID der anderen Partei", pt: "o id da outra parte", it: "l'id dell'altra parte", ja: "相手方のID", zh: "对方的 ID", hi: "दूसरे पक्ष की आईडी", ar: "معرّف الطرف الآخر",
  },
  "exc.fee.ph": {
    en: "fee", es: "tarifa", fr: "honoraires", de: "Honorar", pt: "honorário", it: "compenso", ja: "報酬", zh: "费用", hi: "शुल्क", ar: "الأتعاب",
  },
  "exc.work.ph": {
    en: "what the work is, in one sentence", es: "cuál es el trabajo, en una frase", fr: "en quoi consiste le travail, en une phrase", de: "worin die Arbeit besteht, in einem Satz", pt: "qual é o trabalho, numa frase", it: "qual è il lavoro, in una frase", ja: "その仕事は何か、ひと言で", zh: "这项工作是什么，一句话说明", hi: "काम क्या है, एक वाक्य में", ar: "ما هو العمل، في جملة واحدة",
  },
  "exc.propose.go": {
    en: "Propose", es: "Proponer", fr: "Proposer", de: "Vorschlagen", pt: "Propor", it: "Proponi", ja: "提案", zh: "提出", hi: "प्रस्ताव दें", ar: "اقترح",
  },
  "exc.opened.said": {
    en: "Draft opened. Nothing can move until both of you sign.", es: "Borrador abierto. Nada puede moverse hasta que ambos firmen.", fr: "Brouillon ouvert. Rien ne peut bouger tant que vous n'avez pas signé tous les deux.", de: "Entwurf eröffnet. Nichts kann sich bewegen, bis Sie beide unterschrieben haben.", pt: "Rascunho aberto. Nada pode mover-se até que ambos assinem.", it: "Bozza aperta. Niente può muoversi finché non firmate entrambi.", ja: "下書きを開きました。二人が署名するまで、何も動きません。", zh: "草稿已开启。在双方签署之前，任何东西都不会移动。", hi: "मसौदा खुल गया। जब तक आप दोनों हस्ताक्षर नहीं करते, कुछ नहीं हिलेगा।", ar: "فُتحت المسودة. لا شيء يتحرك حتى يوقّع كلاكما.",
  },
  "exc.cleared.said": {
    en: "The manifest changed, so both signatures were cleared. Sign again.", es: "El manifiesto cambió, así que ambas firmas se borraron. Firme de nuevo.", fr: "Le manifeste a changé, donc les deux signatures ont été effacées. Signez à nouveau.", de: "Das Manifest hat sich geändert, deshalb wurden beide Unterschriften gelöscht. Bitte erneut unterschreiben.", pt: "O manifesto mudou, por isso ambas as assinaturas foram apagadas. Assine de novo.", it: "Il manifesto è cambiato, quindi entrambe le firme sono state cancellate. Firma di nuovo.", ja: "明細が変わったため、両方の署名が取り消されました。もう一度署名してください。", zh: "清单已变更，因此两份签名都已作废。请重新签署。", hi: "सूची बदल गई, इसलिए दोनों हस्ताक्षर मिटा दिए गए। फिर से हस्ताक्षर करें।", ar: "تغيّر البيان، فأُلغي التوقيعان. وقّع من جديد.",
  },
  "exc.yours": {
    en: "Yours", es: "Los tuyos", fr: "Les vôtres", de: "Ihre", pt: "Os seus", it: "I tuoi", ja: "あなたのもの", zh: "你的", hi: "आपके", ar: "ما يخصّك",
  },
  "exc.none": {
    en: "Nothing yet.", es: "Nada todavía.", fr: "Rien pour l'instant.", de: "Noch nichts.", pt: "Nada ainda.", it: "Ancora niente.", ja: "まだ何もありません。", zh: "尚无。", hi: "अभी कुछ नहीं।", ar: "لا شيء بعد.",
  },
  "exc.row": {
    en: "{ind} · {state} · {n} item{s}", es: "{ind} · {state} · {n} elementos", fr: "{ind} · {state} · {n} éléments", de: "{ind} · {state} · {n} Posten", pt: "{ind} · {state} · {n} itens", it: "{ind} · {state} · {n} voci", ja: "{ind} · {state} · {n}件", zh: "{ind} · {state} · {n} 项", hi: "{ind} · {state} · {n} मदें", ar: "{ind} · {state} · {n} بنود",
  },
  "exc.row.tosign": {
    en: "· {n} still to sign", es: "· faltan {n} por firmar", fr: "· {n} restent à signer", de: "· {n} müssen noch unterschreiben", pt: "· faltam {n} por assinar", it: "· {n} devono ancora firmare", ja: "· 未署名 {n} 名", zh: "· 还有 {n} 位未签", hi: "· {n} को अभी हस्ताक्षर करना है", ar: "· بقي {n} للتوقيع",
  },
  "exc.open": {
    en: "Open", es: "Abrir", fr: "Ouvrir", de: "Öffnen", pt: "Abrir", it: "Apri", ja: "開く", zh: "打开", hi: "खोलें", ar: "افتح",
  },
  "exc.detail": {
    en: "{ind} · {state} · fee {fee} — {note}", es: "{ind} · {state} · tarifa {fee} — {note}", fr: "{ind} · {state} · honoraires {fee} — {note}", de: "{ind} · {state} · Honorar {fee} — {note}", pt: "{ind} · {state} · honorário {fee} — {note}", it: "{ind} · {state} · compenso {fee} — {note}", ja: "{ind} · {state} · 報酬 {fee} — {note}", zh: "{ind} · {state} · 费用 {fee} — {note}", hi: "{ind} · {state} · शुल्क {fee} — {note}", ar: "{ind} · {state} · الأتعاب {fee} — {note}",
  },
  "exc.included": {
    en: "Included: {list}", es: "Incluido: {list}", fr: "Inclus : {list}", de: "Enthalten: {list}", pt: "Incluído: {list}", it: "Incluso: {list}", ja: "含まれるもの: {list}", zh: "包含：{list}", hi: "शामिल: {list}", ar: "مشمول: {list}",
  },
  "exc.notincluded": {
    en: "Not included: {list}", es: "No incluido: {list}", fr: "Non inclus : {list}", de: "Nicht enthalten: {list}", pt: "Não incluído: {list}", it: "Non incluso: {list}", ja: "含まれないもの: {list}", zh: "不包含：{list}", hi: "शामिल नहीं: {list}", ar: "غير مشمول: {list}",
  },
  "exc.grants": {
    en: "This grants {a}. It does not grant {b}.", es: "Esto concede {a}. No concede {b}.", fr: "Ceci accorde {a}. Cela n'accorde pas {b}.", de: "Dies gewährt {a}. Es gewährt nicht {b}.", pt: "Isto concede {a}. Não concede {b}.", it: "Questo concede {a}. Non concede {b}.", ja: "これが与えるのは {a} です。与えないのは {b} です。", zh: "这授予 {a}。它不授予 {b}。", hi: "यह {a} देता है। यह {b} नहीं देता।", ar: "هذا يمنح {a}. ولا يمنح {b}.",
  },
  "exc.manifest": {
    en: "The manifest", es: "El manifiesto", fr: "Le manifeste", de: "Das Manifest", pt: "O manifesto", it: "Il manifesto", ja: "明細", zh: "清单", hi: "सूची", ar: "البيان",
  },
  "exc.manifest.none": {
    en: "Nothing listed yet.", es: "Nada listado todavía.", fr: "Rien de listé pour l'instant.", de: "Noch nichts aufgeführt.", pt: "Nada listado ainda.", it: "Ancora niente in elenco.", ja: "まだ何も記載されていません。", zh: "尚未列出任何内容。", hi: "अभी कुछ सूचीबद्ध नहीं।", ar: "لم يُدرج شيء بعد.",
  },
  "exc.runs": {
    en: "runs", es: "se ejecuta", fr: "s'exécute", de: "läuft", pt: "executa", it: "esegue", ja: "実行される", zh: "会运行", hi: "चलता है", ar: "يُنفَّذ",
  },
  "exc.h2g": {
    en: "host → guest", es: "anfitrión → invitado", fr: "hôte → invité", de: "Gastgeber → Gast", pt: "anfitrião → convidado", it: "ospitante → ospite", ja: "ホスト → ゲスト", zh: "主人 → 客人", hi: "मेज़बान → अतिथि", ar: "المضيف ← الضيف",
  },
  "exc.g2h": {
    en: "guest → host", es: "invitado → anfitrión", fr: "invité → hôte", de: "Gast → Gastgeber", pt: "convidado → anfitrião", it: "ospite → ospitante", ja: "ゲスト → ホスト", zh: "客人 → 主人", hi: "अतिथि → मेज़बान", ar: "الضيف ← المضيف",
  },
  "exc.item.line": {
    en: "{dir} · {kind}", es: "{dir} · {kind}", fr: "{dir} · {kind}", de: "{dir} · {kind}", pt: "{dir} · {kind}", it: "{dir} · {kind}", ja: "{dir} · {kind}", zh: "{dir} · {kind}", hi: "{dir} · {kind}", ar: "{dir} · {kind}",
  },
  "exc.item.bytes": {
    en: "· {n} bytes", es: "· {n} bytes", fr: "· {n} octets", de: "· {n} Bytes", pt: "· {n} bytes", it: "· {n} byte", ja: "· {n} バイト", zh: "· {n} 字节", hi: "· {n} बाइट", ar: "· {n} بايت",
  },
  "exc.item.accepted": {
    en: "· accepted", es: "· aceptado", fr: "· accepté", de: "· angenommen", pt: "· aceite", it: "· accettato", ja: "· 受領済み", zh: "· 已接收", hi: "· स्वीकृत", ar: "· مقبول",
  },
  "exc.accept": {
    en: "Accept", es: "Aceptar", fr: "Accepter", de: "Annehmen", pt: "Aceitar", it: "Accetta", ja: "受け取る", zh: "接收", hi: "स्वीकारें", ar: "اقبل",
  },
  "exc.accepted.said": {
    en: "Accepted. That one item, and nothing else.", es: "Aceptado. Ese elemento, y nada más.", fr: "Accepté. Cet élément-là, et rien d'autre.", de: "Angenommen. Genau dieser Posten, und sonst nichts.", pt: "Aceite. Esse item, e mais nada.", it: "Accettato. Quella voce, e nient'altro.", ja: "受け取りました。その一件だけで、ほかは何もありません。", zh: "已接收。仅此一项，别无其他。", hi: "स्वीकृत। बस वही एक मद, और कुछ नहीं।", ar: "قُبل. ذلك البند وحده، ولا شيء غيره.",
  },
  "exc.remove": {
    en: "Remove", es: "Quitar", fr: "Retirer", de: "Entfernen", pt: "Remover", it: "Rimuovi", ja: "削除", zh: "移除", hi: "हटाएँ", ar: "احذف",
  },
  "exc.item.ph": {
    en: "what crosses", es: "qué cruza", fr: "ce qui passe", de: "was hinübergeht", pt: "o que atravessa", it: "cosa passa", ja: "何が渡るか", zh: "交付什么", hi: "क्या पार जाता है", ar: "ما الذي يعبر",
  },
  "exc.add": {
    en: "Add", es: "Añadir", fr: "Ajouter", de: "Hinzufügen", pt: "Adicionar", it: "Aggiungi", ja: "追加", zh: "添加", hi: "जोड़ें", ar: "أضف",
  },
  "exc.sigs": {
    en: "Signatures", es: "Firmas", fr: "Signatures", de: "Unterschriften", pt: "Assinaturas", it: "Firme", ja: "署名", zh: "签名", hi: "हस्ताक्षर", ar: "التوقيعات",
  },
  "exc.sigs.against": {
    en: "Against fingerprint {fp} — change the manifest and this changes, so the old signatures match nothing.", es: "Contra la huella {fp} — cambie el manifiesto y esta cambia, así que las firmas antiguas no coinciden con nada.", fr: "Contre l'empreinte {fp} — changez le manifeste et elle change, donc les anciennes signatures ne correspondent à rien.", de: "Gegen den Fingerabdruck {fp} — ändern Sie das Manifest, ändert er sich, und die alten Unterschriften passen zu nichts mehr.", pt: "Contra a impressão {fp} — mude o manifesto e ela muda, por isso as assinaturas antigas não correspondem a nada.", it: "Contro l'impronta {fp} — cambia il manifesto e questa cambia, così le vecchie firme non corrispondono a niente.", ja: "指紋 {fp} に対して — 明細を変えればこれも変わるので、古い署名はどれとも一致しなくなります。", zh: "针对指纹 {fp} — 一旦改动清单，它就会变，于是旧签名与任何内容都不再匹配。", hi: "फ़िंगरप्रिंट {fp} के विरुद्ध — सूची बदलिए और यह बदल जाता है, इसलिए पुराने हस्ताक्षर किसी से मेल नहीं खाते।", ar: "مقابل البصمة {fp} — غيّر البيان تتغيّر هي، فلا تطابق التواقيع القديمة شيئًا.",
  },
  "exc.sig.line": {
    en: "{who} signed {when}", es: "{who} firmó {when}", fr: "{who} a signé {when}", de: "{who} unterschrieb {when}", pt: "{who} assinou {when}", it: "{who} ha firmato {when}", ja: "{who} が {when} に署名", zh: "{who} 于 {when} 签署", hi: "{who} ने {when} को हस्ताक्षर किया", ar: "{who} وقّع في {when}",
  },
  "exc.sig.stale": {
    en: "— against an older manifest, not this one", es: "— contra un manifiesto anterior, no este", fr: "— contre un manifeste antérieur, pas celui-ci", de: "— gegen ein älteres Manifest, nicht dieses", pt: "— contra um manifesto anterior, não este", it: "— contro un manifesto precedente, non questo", ja: "— これではなく、古い明細に対するもの", zh: "— 针对的是更早的清单，不是这一份", hi: "— किसी पुरानी सूची के विरुद्ध, इसके नहीं", ar: "— مقابل بيان أقدم، لا هذا",
  },
  "exc.waiting": {
    en: "Waiting on: {who}", es: "A la espera de: {who}", fr: "En attente de : {who}", de: "Warten auf: {who}", pt: "À espera de: {who}", it: "In attesa di: {who}", ja: "待ち: {who}", zh: "等待：{who}", hi: "प्रतीक्षा: {who}", ar: "في انتظار: {who}",
  },
  "exc.you": {
    en: "you", es: "usted", fr: "vous", de: "Sie", pt: "você", it: "tu", ja: "あなた", zh: "你", hi: "आप", ar: "أنت",
  },
  "exc.sign": {
    en: "Sign", es: "Firmar", fr: "Signer", de: "Unterschreiben", pt: "Assinar", it: "Firma", ja: "署名する", zh: "签署", hi: "हस्ताक्षर करें", ar: "وقّع",
  },
  "exc.signed.said": {
    en: "Signed — this manifest, and nothing it becomes later.", es: "Firmado — este manifiesto, y nada en lo que se convierta después.", fr: "Signé — ce manifeste-ci, et rien de ce qu'il deviendra plus tard.", de: "Unterschrieben — dieses Manifest, und nichts, was später daraus wird.", pt: "Assinado — este manifesto, e nada no que ele se torne depois.", it: "Firmato — questo manifesto, e niente di ciò che diventerà poi.", ja: "署名しました — この明細に対してであり、後にそれが何になろうと関係ありません。", zh: "已签署 — 针对的是这份清单，而不是它日后变成的样子。", hi: "हस्ताक्षरित — यही सूची, और वह नहीं जो यह बाद में बन जाए।", ar: "وُقّع — هذا البيان، لا ما يصير إليه لاحقًا.",
  },
  "exc.reopen": {
    en: "Reopen to edit", es: "Reabrir para editar", fr: "Rouvrir pour modifier", de: "Zum Bearbeiten wieder öffnen", pt: "Reabrir para editar", it: "Riapri per modificare", ja: "編集のため開き直す", zh: "重新打开以编辑", hi: "संपादन हेतु फिर खोलें", ar: "أعد الفتح للتعديل",
  },
  "exc.reopened.said": {
    en: "Reopened. Both signatures cleared.", es: "Reabierto. Ambas firmas borradas.", fr: "Rouvert. Les deux signatures effacées.", de: "Wieder geöffnet. Beide Unterschriften gelöscht.", pt: "Reaberto. Ambas as assinaturas apagadas.", it: "Riaperto. Entrambe le firme cancellate.", ja: "開き直しました。両方の署名を取り消しました。", zh: "已重新打开。两份签名均已作废。", hi: "फिर खोला गया। दोनों हस्ताक्षर मिटे।", ar: "أُعيد فتحه. أُلغي التوقيعان.",
  },
  "exc.withdraw": {
    en: "Withdraw", es: "Retirar", fr: "Retirer", de: "Zurückziehen", pt: "Retirar", it: "Ritira", ja: "取り下げる", zh: "撤回", hi: "वापस लें", ar: "اسحب",
  },
  "exc.withdrawn.said": {
    en: "Withdrawn.", es: "Retirado.", fr: "Retiré.", de: "Zurückgezogen.", pt: "Retirado.", it: "Ritirato.", ja: "取り下げました。", zh: "已撤回。", hi: "वापस लिया गया।", ar: "سُحب.",
  },
  "exc.move": {
    en: "Can anything move?", es: "¿Puede moverse algo?", fr: "Quelque chose peut-il bouger ?", de: "Kann sich etwas bewegen?", pt: "Pode mover-se alguma coisa?", it: "Può muoversi qualcosa?", ja: "何か動かせますか？", zh: "有东西可以移动吗？", hi: "क्या कुछ हिल सकता है?", ar: "هل يمكن لشيء أن يتحرك؟",
  },
  "exc.move.yes": {
    en: "Yes — {n} item{s} available.", es: "Sí — {n} elementos disponibles.", fr: "Oui — {n} éléments disponibles.", de: "Ja — {n} Posten verfügbar.", pt: "Sim — {n} itens disponíveis.", it: "Sì — {n} voci disponibili.", ja: "はい — {n}件が利用できます。", zh: "可以 — {n} 项可用。", hi: "हाँ — {n} मदें उपलब्ध।", ar: "نعم — {n} بنود متاحة.",
  },
  "exc.move.no": {
    en: "No — {reason}.", es: "No — {reason}.", fr: "Non — {reason}.", de: "Nein — {reason}.", pt: "Não — {reason}.", it: "No — {reason}.", ja: "いいえ — {reason}。", zh: "不行 — {reason}。", hi: "नहीं — {reason}।", ar: "لا — {reason}.",
  },
  "exc.unsigned": {
    en: "Unsigned: {who}", es: "Sin firmar: {who}", fr: "Non signé : {who}", de: "Nicht unterschrieben: {who}", pt: "Por assinar: {who}", it: "Non firmato: {who}", ja: "未署名: {who}", zh: "未签署：{who}", hi: "अहस्ताक्षरित: {who}", ar: "دون توقيع: {who}",
  },
  "exc.askagain": {
    en: "Ask again", es: "Preguntar de nuevo", fr: "Redemander", de: "Nochmal fragen", pt: "Perguntar de novo", it: "Chiedi di nuovo", ja: "もう一度尋ねる", zh: "再问一次", hi: "फिर पूछें", ar: "اسأل مجددًا",
  },
  "rch.title": {
    en: "Reaching out, and what stops it", es: "Contactar, y qué lo impide", fr: "Prendre contact, et ce qui l'empêche", de: "Kontakt aufnehmen, und was das verhindert", pt: "Tomar a iniciativa, e o que a trava", it: "Farsi vivo, e cosa lo ferma", ja: "こちらから声をかけること、そしてそれを止めるもの", zh: "主动联系，以及什么会阻止它", hi: "पहल करके संपर्क, और उसे क्या रोकता है", ar: "المبادرة بالتواصل، وما يمنعها",
  },
  "rch.lead": {
    en: "Four different refusals, and only two of them are yours to lift.", es: "Cuatro negativas distintas, y solo dos son suyas para levantar.", fr: "Quatre refus différents, et deux seulement vous appartiennent.", de: "Vier verschiedene Ablehnungen, und nur zwei davon können Sie aufheben.", pt: "Quatro recusas diferentes, e só duas são suas para levantar.", it: "Quattro rifiuti diversi, e solo due sono tuoi da togliere.", ja: "四つの異なる拒否があり、そのうちあなたが解除できるのは二つだけです。", zh: "四种不同的拒绝，其中只有两种是你能解除的。", hi: "चार अलग-अलग इनकार, और उनमें से केवल दो हटाना आपके हाथ में है।", ar: "أربعة أنواع من الرفض، اثنان منها فقط بيدك رفعهما.",
  },
  "rch.who": {
    en: "Somebody in particular", es: "Alguien en concreto", fr: "Quelqu'un en particulier", de: "Eine bestimmte Person", pt: "Alguém em particular", it: "Qualcuno in particolare", ja: "特定の相手", zh: "某个具体的人", hi: "कोई ख़ास व्यक्ति", ar: "شخص بعينه",
  },
  "rch.who.ph": {
    en: "a person's id", es: "el id de una persona", fr: "l'id d'une personne", de: "die ID einer Person", pt: "o id de uma pessoa", it: "l'id di una persona", ja: "人物のID", zh: "某人的 ID", hi: "किसी व्यक्ति की आईडी", ar: "معرّف شخص",
  },
  "rch.how": {
    en: "How are we going", es: "Cómo vamos", fr: "Où en sommes-nous", de: "Wie steht es", pt: "Como vamos", it: "Come andiamo", ja: "関係はどうか", zh: "我们相处得如何", hi: "हम कैसे चल रहे हैं", ar: "كيف نمضي",
  },
  "rch.state": {
    en: "{n} exchange{s} across {m} session{t} · score {score}", es: "{n} intercambios en {m} sesiones · puntuación {score}", fr: "{n} échanges sur {m} sessions · score {score}", de: "{n} Austausche über {m} Sitzungen · Wert {score}", pt: "{n} trocas em {m} sessões · pontuação {score}", it: "{n} scambi in {m} sessioni · punteggio {score}", ja: "{m}セッションにわたるやり取り{n}件 · スコア {score}", zh: "{m} 次会话中的 {n} 次往来 · 分数 {score}", hi: "{m} सत्रों में {n} आदान-प्रदान · अंक {score}", ar: "{n} تبادلات عبر {m} جلسات · الدرجة {score}",
  },
  "rch.updown": {
    en: "{up} up · {down} down", es: "{up} a favor · {down} en contra", fr: "{up} pouces levés · {down} baissés", de: "{up} Daumen hoch · {down} runter", pt: "{up} a favor · {down} contra", it: "{up} pollici su · {down} giù", ja: "高評価{up} · 低評価{down}", zh: "{up} 个赞 · {down} 个踩", hi: "{up} पसंद · {down} नापसंद", ar: "{up} إعجاب · {down} عدم إعجاب",
  },
  "rch.read": {
    en: "Readable by you and by them, and by nobody else. It is a record of how often somebody talks to this profile, which is a fact about them as much as about it.", es: "Legible por usted y por ellos, y por nadie más. Es un registro de con qué frecuencia alguien habla con este perfil, lo cual es un hecho sobre esa persona tanto como sobre él.", fr: "Lisible par vous et par eux, et par personne d'autre. C'est un relevé de la fréquence à laquelle quelqu'un parle à ce profil, ce qui est un fait sur cette personne autant que sur lui.", de: "Lesbar für Sie und für sie, und für niemanden sonst. Es ist eine Aufzeichnung, wie oft jemand mit diesem Profil spricht — eine Tatsache über die Person genauso wie über das Profil.", pt: "Legível por si e por eles, e por mais ninguém. É um registo da frequência com que alguém fala com este perfil, o que é um facto sobre essa pessoa tanto quanto sobre ele.", it: "Leggibile da te e da loro, e da nessun altro. È un registro di quanto spesso qualcuno parla con questo profilo, il che è un fatto su quella persona tanto quanto su di esso.", ja: "読めるのはあなたと相手だけで、ほかの誰でもありません。これは誰かがこのプロフィールとどれだけ話しているかの記録であり、プロフィールについてと同じくらいその人についての事実です。", zh: "只有你和对方能读到，别人都不能。它记录的是某人与这份资料交谈的频率——这既是关于资料的事实，也同样是关于那个人的事实。", hi: "इसे केवल आप और वे पढ़ सकते हैं, और कोई नहीं। यह इस बात का रिकॉर्ड है कि कोई इस प्रोफ़ाइल से कितनी बार बात करता है — जो प्रोफ़ाइल जितना ही उस व्यक्ति के बारे में भी तथ्य है।", ar: "يقرؤه أنت وهم، ولا أحد سواكما. إنه سجل لكم مرة يتحدث أحدهم إلى هذا الملف، وهي حقيقة عنه بقدر ما هي عن الملف.",
  },
  "rch.first": {
    en: "Reaching out first", es: "Dar el primer paso", fr: "Faire le premier pas", de: "Von sich aus melden", pt: "Dar o primeiro passo", it: "Farsi vivo per primo", ja: "こちらから先に声をかける", zh: "率先联系", hi: "पहले पहल करना", ar: "المبادرة أولًا",
  },
  "rch.reactive": {
    en: "Reactive-only", es: "Solo reactivo", fr: "Réactif seulement", de: "Nur reaktiv", pt: "Apenas reativo", it: "Solo reattivo", ja: "応答のみ", zh: "仅被动回应", hi: "केवल प्रतिक्रियात्मक", ar: "الرد فقط",
  },
  "rch.awaiting": {
    en: "Awaiting a reply", es: "A la espera de respuesta", fr: "En attente d'une réponse", de: "Wartet auf Antwort", pt: "À espera de resposta", it: "In attesa di risposta", ja: "返信待ち", zh: "等待回复", hi: "उत्तर की प्रतीक्षा", ar: "بانتظار ردّ",
  },
  "rch.ratecap": {
    en: "Rate cap", es: "Límite de frecuencia", fr: "Limite de fréquence", de: "Frequenzgrenze", pt: "Limite de frequência", it: "Limite di frequenza", ja: "頻度の上限", zh: "频率上限", hi: "दर-सीमा", ar: "حدّ التكرار",
  },
  "rch.quiet": {
    en: "Quiet hours", es: "Horas de silencio", fr: "Heures calmes", de: "Ruhezeiten", pt: "Horas de silêncio", it: "Ore di silenzio", ja: "静かな時間帯", zh: "静默时段", hi: "शांत घंटे", ar: "ساعات الهدوء",
  },
  "rch.quiet.low": {
    en: "quiet hours", es: "horas de silencio", fr: "heures calmes", de: "Ruhezeiten", pt: "horas de silêncio", it: "ore di silenzio", ja: "静かな時間帯", zh: "静默时段", hi: "शांत घंटे", ar: "ساعات الهدوء",
  },
  "rch.gates": {
    en: "Three gates, and they refuse in three different sentences because they are three different facts. {reactive} means you never switched outreach on. {awaiting} means it already reached out and heard nothing — it will not send twice into silence. {ratecap} means it reached out recently. And {quiet} is not yours at all.", es: "Tres barreras, y rechazan con tres frases distintas porque son tres hechos distintos. {reactive} significa que nunca activó la iniciativa. {awaiting} significa que ya escribió y no obtuvo respuesta — no enviará dos veces al silencio. {ratecap} significa que escribió hace poco. Y {quiet} no es suya en absoluto.", fr: "Trois barrières, et elles refusent en trois phrases différentes parce que ce sont trois faits différents. {reactive} veut dire que vous n'avez jamais activé l'initiative. {awaiting} veut dire qu'il a déjà écrit et n'a rien entendu — il n'enverra pas deux fois dans le silence. {ratecap} veut dire qu'il a écrit récemment. Et {quiet} ne vous appartient pas du tout.", de: "Drei Schranken, und sie lehnen in drei verschiedenen Sätzen ab, weil es drei verschiedene Tatsachen sind. {reactive} heißt, Sie haben die Initiative nie eingeschaltet. {awaiting} heißt, es hat sich schon gemeldet und nichts gehört — es sendet nicht zweimal ins Schweigen. {ratecap} heißt, es hat sich kürzlich gemeldet. Und {quiet} gehört Ihnen gar nicht.", pt: "Três barreiras, e recusam em três frases diferentes porque são três factos diferentes. {reactive} significa que nunca ligou a iniciativa. {awaiting} significa que já escreveu e não ouviu nada — não enviará duas vezes para o silêncio. {ratecap} significa que escreveu há pouco. E {quiet} não é sua de todo.", it: "Tre barriere, e rifiutano con tre frasi diverse perché sono tre fatti diversi. {reactive} vuol dire che non hai mai attivato l'iniziativa. {awaiting} vuol dire che si è già fatto vivo e non ha sentito nulla — non manderà due volte nel silenzio. {ratecap} vuol dire che si è fatto vivo di recente. E {quiet} non è affatto tua.", ja: "門は三つあり、三つとも別々の事実なので、拒否の文も三通りです。{reactive} は、こちらからの発信を一度も有効にしていないという意味です。{awaiting} は、すでに声をかけて返事がなかったという意味です — 沈黙に向けて二度は送りません。{ratecap} は、つい最近声をかけたという意味です。そして {quiet} は、そもそもあなたのものではありません。", zh: "有三道关卡，它们用三种不同的说法拒绝，因为那是三个不同的事实。{reactive} 意味着你从未打开主动联系。{awaiting} 意味着它已经联系过却没有回音——它不会向沉默发送第二次。{ratecap} 意味着它最近刚联系过。而 {quiet} 根本不属于你。", hi: "तीन द्वार हैं, और वे तीन अलग वाक्यों में मना करते हैं क्योंकि वे तीन अलग तथ्य हैं। {reactive} का अर्थ है कि आपने पहल कभी चालू ही नहीं की। {awaiting} का अर्थ है कि यह पहले ही संपर्क कर चुका है और कुछ नहीं सुना — यह ख़ामोशी में दोबारा नहीं भेजेगा। {ratecap} का अर्थ है कि इसने हाल ही में संपर्क किया था। और {quiet} आपका है ही नहीं।", ar: "ثلاث بوابات، وترفض بثلاث جمل مختلفة لأنها ثلاث حقائق مختلفة. {reactive} يعني أنك لم تُفعّل المبادرة قط. {awaiting} يعني أنه بادر فعلًا ولم يسمع شيئًا — ولن يرسل مرتين إلى الصمت. {ratecap} يعني أنه بادر مؤخرًا. أما {quiet} فليست لك أصلًا.",
  },
  "rch.now": {
    en: "Reach out now", es: "Contactar ahora", fr: "Prendre contact maintenant", de: "Jetzt melden", pt: "Contactar agora", it: "Fatti vivo ora", ja: "今すぐ声をかける", zh: "立即联系", hi: "अभी संपर्क करें", ar: "بادر الآن",
  },
  "rch.sent.said": {
    en: "Sent.", es: "Enviado.", fr: "Envoyé.", de: "Gesendet.", pt: "Enviado.", it: "Inviato.", ja: "送信しました。", zh: "已发送。", hi: "भेज दिया गया।", ar: "أُرسل.",
  },
  "rch.reason": {
    en: "Its own reason for sending: {why}", es: "Su propia razón para escribir: {why}", fr: "Sa propre raison d'écrire : {why}", de: "Sein eigener Grund für die Nachricht: {why}", pt: "A sua própria razão para escrever: {why}", it: "La sua ragione per scrivere: {why}", ja: "送信した理由（本人の言葉）: {why}", zh: "它自己给出的发送理由：{why}", hi: "भेजने का इसका अपना कारण: {why}", ar: "سببه هو للإرسال: {why}",
  },
  "rch.held": {
    en: "Held for approval rather than delivered — an unprompted message is exactly the kind that should not slip past moderation.", es: "Retenido para aprobación en lugar de entregado — un mensaje no solicitado es justo el que no debería colarse sin moderación.", fr: "Retenu pour approbation plutôt que délivré — un message non sollicité est exactement celui qui ne doit pas échapper à la modération.", de: "Zur Freigabe zurückgehalten statt zugestellt — eine unaufgeforderte Nachricht ist genau die, die nicht an der Moderation vorbeirutschen sollte.", pt: "Retido para aprovação em vez de entregue — uma mensagem não solicitada é exatamente a que não deve escapar à moderação.", it: "Trattenuto per approvazione invece che consegnato — un messaggio non richiesto è proprio quello che non dovrebbe sfuggire alla moderazione.", ja: "配信ではなく承認待ちとして保留されました — こちらから送る一方的なメッセージこそ、審査をすり抜けてはならないものです。", zh: "被留待审核而非直接送出——未经请求的消息，正是不该绕过审核的那一类。", hi: "भेजने के बजाय अनुमोदन के लिए रोका गया — बिन माँगा संदेश ठीक वही है जिसे मॉडरेशन से बचकर नहीं निकलना चाहिए।", ar: "احتُجزت للموافقة بدل أن تُسلَّم — الرسالة غير المطلوبة هي بالضبط ما لا ينبغي أن يمرّ دون مراجعة.",
  },
  "rch.delivered": {
    en: "Delivered, and watermarked like every other thing this profile says.", es: "Entregado, y con marca de agua como todo lo demás que dice este perfil.", fr: "Délivré, et filigrané comme tout ce que dit ce profil.", de: "Zugestellt, und mit Wasserzeichen wie alles andere, was dieses Profil sagt.", pt: "Entregue, e com marca de água como tudo o mais que este perfil diz.", it: "Consegnato, e filigranato come ogni altra cosa che questo profilo dice.", ja: "配信されました。このプロフィールが言う他のすべてと同じく、透かしが入っています。", zh: "已送达，并像这份资料所说的其他一切一样带有水印。", hi: "पहुँचा दिया गया, और इस प्रोफ़ाइल की हर दूसरी बात की तरह वॉटरमार्क सहित।", ar: "سُلّمت، وعليها علامة مائية مثل كل ما يقوله هذا الملف.",
  },
  "rch.quiet.pitch": {
    en: "The window during which nothing may reach out unprompted. Set by the person it protects — sending this with an owner token is refused, and that refusal is the point. A boundary your correspondent can move is not one.", es: "La franja durante la cual nada puede escribir sin ser invitado. La fija la persona a quien protege — enviarlo con un token de propietario se rechaza, y ese rechazo es el punto. Un límite que su interlocutor puede mover no es un límite.", fr: "La plage durant laquelle rien ne peut écrire sans y avoir été invité. Fixée par la personne qu'elle protège — l'envoyer avec un jeton de propriétaire est refusé, et ce refus est tout l'intérêt. Une limite que votre correspondant peut déplacer n'en est pas une.", de: "Das Fenster, in dem sich nichts von sich aus melden darf. Gesetzt von der Person, die es schützt — mit einem Besitzer-Token gesendet, wird es abgelehnt, und diese Ablehnung ist der Punkt. Eine Grenze, die Ihr Gegenüber verschieben kann, ist keine.", pt: "A janela durante a qual nada pode escrever sem ser convidado. Definida pela pessoa que protege — enviá-la com um token de proprietário é recusado, e essa recusa é o ponto. Um limite que o seu interlocutor pode mover não é um limite.", it: "La finestra durante la quale nulla può farsi vivo senza essere invitato. La imposta la persona che protegge — inviarla con un token da proprietario viene rifiutato, e quel rifiuto è il punto. Un confine che il tuo interlocutore può spostare non è un confine.", ja: "こちらから声をかけてはならない時間帯です。守られる本人が設定します — 所有者トークンで送ると拒否され、その拒否こそが要点です。相手が動かせる境界は、境界ではありません。", zh: "在这段时间内，任何东西都不得主动来找你。由它所保护的那个人自己设定——用所有者令牌提交会被拒绝，而这个拒绝正是要点。你的对话方能移动的界线，就不算界线。", hi: "वह अवधि जिसमें बिना बुलाए कुछ भी संपर्क नहीं कर सकता। इसे वही व्यक्ति तय करता है जिसकी यह रक्षा करती है — स्वामी टोकन से भेजने पर इनकार होता है, और वही इनकार असल बात है। जिस सीमा को आपका वार्ताकार हिला सके, वह सीमा नहीं।", ar: "النافذة التي لا يجوز خلالها أن يبادر أحد بالتواصل. يضبطها الشخص الذي تحميه — وإرسالها برمز المالك مرفوض، وهذا الرفض هو المقصود. الحدّ الذي يستطيع مراسلك تحريكه ليس حدًّا.",
  },
  "rch.from": {
    en: "from", es: "desde", fr: "de", de: "von", pt: "de", it: "dalle", ja: "開始", zh: "从", hi: "से", ar: "من",
  },
  "rch.until": {
    en: "until", es: "hasta", fr: "à", de: "bis", pt: "até", it: "alle", ja: "終了", zh: "到", hi: "तक", ar: "إلى",
  },
  "rch.set": {
    en: "Set my quiet hours", es: "Fijar mis horas de silencio", fr: "Définir mes heures calmes", de: "Meine Ruhezeiten festlegen", pt: "Definir as minhas horas de silêncio", it: "Imposta le mie ore di silenzio", ja: "自分の静かな時間帯を設定", zh: "设置我的静默时段", hi: "मेरे शांत घंटे तय करें", ar: "اضبط ساعات هدوئي",
  },
  "rch.set.said": {
    en: "Set.", es: "Fijado.", fr: "Défini.", de: "Festgelegt.", pt: "Definido.", it: "Impostato.", ja: "設定しました。", zh: "已设置。", hi: "तय हो गया।", ar: "ضُبط.",
  },
  "rch.clear": {
    en: "clear", es: "borrar", fr: "effacer", de: "löschen", pt: "limpar", it: "cancella", ja: "解除", zh: "清除", hi: "मिटाएँ", ar: "امسح",
  },
  "rch.cleared.said": {
    en: "Cleared.", es: "Borrado.", fr: "Effacé.", de: "Gelöscht.", pt: "Limpo.", it: "Cancellato.", ja: "解除しました。", zh: "已清除。", hi: "मिट गया।", ar: "مُسح.",
  },
  "rch.utc": {
    en: "Hours are UTC, 0 to 23. Both empty means no window.", es: "Las horas son UTC, de 0 a 23. Ambas vacías significa sin franja.", fr: "Les heures sont en UTC, de 0 à 23. Les deux vides signifie aucune plage.", de: "Stunden in UTC, 0 bis 23. Beide leer heißt kein Fenster.", pt: "As horas são UTC, de 0 a 23. Ambas vazias significa sem janela.", it: "Le ore sono UTC, da 0 a 23. Entrambe vuote significa nessuna finestra.", ja: "時刻は UTC、0 から 23 までです。両方空欄なら時間帯なしという意味です。", zh: "时间为 UTC，0 至 23。两个都留空表示没有静默时段。", hi: "घंटे UTC में हैं, 0 से 23। दोनों ख़ाली का अर्थ है कोई अवधि नहीं।", ar: "الساعات بتوقيت UTC، من 0 إلى 23. تركهما فارغين يعني ألا نافذة.",
  },
  "rch.currently": {
    en: " Currently {a} to {b}.", es: " Actualmente de {a} a {b}.", fr: " Actuellement de {a} à {b}.", de: " Derzeit {a} bis {b}.", pt: " Atualmente de {a} a {b}.", it: " Attualmente dalle {a} alle {b}.", ja: "現在は {a} から {b} まで。", zh: "当前为 {a} 至 {b}。", hi: " फ़िलहाल {a} से {b} तक।", ar: " حاليًا من {a} إلى {b}.",
  },
  "rch.samehour.term": {
    en: "same hour", es: "misma hora", fr: "même heure", de: "gleiche Stunde", pt: "mesma hora", it: "stessa ora", ja: "同じ時刻", zh: "同一小时", hi: "एक ही घंटा", ar: "الساعة نفسها",
  },
  "rch.samehour": {
    en: "Those are the {same}, which covers nothing rather than everything — the window runs from the first up to but not including the second. To be quiet all day, end one hour before you start.", es: "Esas son la {same}, lo que no cubre nada en lugar de todo — la franja va desde la primera hasta la segunda sin incluirla. Para estar en silencio todo el día, termine una hora antes de empezar.", fr: "Ce sont la {same}, ce qui ne couvre rien plutôt que tout — la plage va de la première jusqu'à la seconde exclue. Pour être silencieux toute la journée, terminez une heure avant de commencer.", de: "Das ist die {same}, was nichts abdeckt statt alles — das Fenster läuft von der ersten bis ausschließlich der zweiten. Um den ganzen Tag still zu sein, enden Sie eine Stunde vor dem Beginn.", pt: "Essas são a {same}, o que não cobre nada em vez de tudo — a janela vai da primeira até à segunda, exclusive. Para ficar em silêncio o dia todo, termine uma hora antes de começar.", it: "Quelle sono la {same}, il che non copre niente invece che tutto — la finestra va dalla prima fino alla seconda esclusa. Per stare in silenzio tutto il giorno, finisci un'ora prima di iniziare.", ja: "それは {same} であり、すべてではなく何も覆いません — 時間帯は最初の時刻から二つ目の時刻の直前までです。一日中静かにするには、開始の一時間前に終わらせてください。", zh: "那是{same}，它覆盖的不是全部而是零——时段从第一个时刻起，到第二个时刻为止但不含它。若要整天静默，请把结束时间设在开始时间的前一小时。", hi: "वे {same} हैं, जो सब कुछ नहीं बल्कि कुछ भी नहीं ढकता — अवधि पहले से दूसरे तक चलती है, दूसरे को छोड़कर। पूरे दिन शांत रहने के लिए, शुरुआत से एक घंटा पहले समाप्त करें।", ar: "تلك هي {same}، وهي تغطي لا شيء بدل كل شيء — تمتد النافذة من الأولى حتى الثانية دون أن تشملها. لتظل هادئًا طوال اليوم، أنهِ قبل ساعة من موعد البدء.",
  },
  "rch.notyours": {
    en: "This is your own control, not one you hold over anybody else — so it needs your token as a person rather than as a profile's owner. Sign in as yourself to set it.", es: "Este es su propio control, no uno que ejerza sobre nadie más — así que necesita su token como persona y no como propietario de un perfil. Inicie sesión como usted mismo para fijarlo.", fr: "C'est votre propre réglage, pas un pouvoir sur quelqu'un d'autre — il faut donc votre jeton en tant que personne, et non en tant que propriétaire d'un profil. Connectez-vous en votre nom pour le définir.", de: "Das ist Ihre eigene Einstellung, keine, die Sie über jemand anderen haben — es braucht also Ihr Token als Person und nicht als Profilbesitzer. Melden Sie sich als Sie selbst an, um es zu setzen.", pt: "Este é o seu próprio controlo, não um que exerça sobre outra pessoa — por isso precisa do seu token como pessoa e não como proprietário de um perfil. Entre como você mesmo para o definir.", it: "Questo è un tuo controllo, non uno che eserciti su qualcun altro — quindi serve il tuo token come persona e non come proprietario di un profilo. Accedi come te stesso per impostarlo.", ja: "これはあなた自身の設定であり、他人に対して持つ権限ではありません — ですからプロフィールの所有者としてではなく、一人の人としてのトークンが必要です。ご自身としてサインインして設定してください。", zh: "这是你自己的控制项，而不是你对别人行使的权力——所以它需要你作为个人的令牌，而非资料所有者的令牌。请以你自己的身份登录来设置。", hi: "यह आपका अपना नियंत्रण है, किसी और पर चलाया जाने वाला नहीं — इसलिए इसके लिए प्रोफ़ाइल-स्वामी नहीं, बल्कि एक व्यक्ति के रूप में आपका टोकन चाहिए। इसे तय करने के लिए ख़ुद के रूप में साइन इन करें।", ar: "هذا ضبط يخصّك أنت، لا سلطة تملكها على غيرك — لذا يلزمه رمزك بصفتك شخصًا لا بصفتك مالك ملف. سجّل الدخول بصفتك أنت لضبطه.",
  },
  "rch.rate": {
    en: "Rate an exchange", es: "Valorar un intercambio", fr: "Noter un échange", de: "Einen Austausch bewerten", pt: "Avaliar uma troca", it: "Valuta uno scambio", ja: "やり取りを評価する", zh: "为一次往来评分", hi: "किसी आदान-प्रदान को आँकें", ar: "قيّم تبادلًا",
  },
  "rch.rate.pitch": {
    en: "Gated on the rater's own token. A rating in somebody else's name is a lie about what they thought, and a thumbs-up is also the trigger for contributing that exchange to the shared model — so it is not a button anybody else gets to press for you.", es: "Sujeto al token de quien valora. Una valoración en nombre de otra persona es una mentira sobre lo que pensó, y un pulgar arriba es además lo que envía ese intercambio al modelo compartido — así que no es un botón que otro pueda pulsar por usted.", fr: "Conditionné au jeton de celui qui note. Une note au nom de quelqu'un d'autre est un mensonge sur ce qu'il a pensé, et un pouce levé déclenche aussi le versement de cet échange au modèle partagé — ce n'est donc pas un bouton qu'un autre presse à votre place.", de: "An das Token des Bewertenden gebunden. Eine Bewertung in fremdem Namen ist eine Lüge darüber, was diese Person dachte, und ein Daumen hoch löst außerdem aus, dass dieser Austausch ins geteilte Modell fließt — kein Knopf also, den jemand anderes für Sie drückt.", pt: "Dependente do token de quem avalia. Uma avaliação em nome de outra pessoa é uma mentira sobre o que ela pensou, e um polegar para cima é também o que envia essa troca para o modelo partilhado — por isso não é um botão que outro possa carregar por si.", it: "Vincolato al token di chi valuta. Una valutazione a nome di qualcun altro è una menzogna su ciò che ha pensato, e un pollice su è anche ciò che manda quello scambio al modello condiviso — quindi non è un pulsante che un altro preme al posto tuo.", ja: "評価する本人のトークンが必要です。他人の名前での評価はその人が何を思ったかについての嘘であり、しかも高評価は、そのやり取りを共有モデルへ提供する引き金でもあります — ですから、誰かが代わりに押してよいボタンではありません。", zh: "以评分者本人的令牌为准。以他人之名给出的评分，是对那个人想法的谎言；而点赞同时也是把这次往来贡献给共享模型的触发条件——所以这不是别人可以替你按下的按钮。", hi: "आँकने वाले के अपने टोकन पर निर्भर। किसी और के नाम पर दी गई राय उस व्यक्ति के विचार के बारे में झूठ है, और अंगूठा-ऊपर उस आदान-प्रदान को साझा मॉडल तक पहुँचाने का ट्रिगर भी है — इसलिए यह ऐसा बटन नहीं जिसे कोई और आपके लिए दबा सके।", ar: "مشروط برمز المقيّم نفسه. التقييم باسم شخص آخر كذب على ما ظنّه، كما أن الإعجاب هو أيضًا ما يدفع بذلك التبادل إلى النموذج المشترك — فليس زرًّا يضغطه غيرك نيابةً عنك.",
  },
  "rch.up": {
    en: "👍 good", es: "👍 bien", fr: "👍 bien", de: "👍 gut", pt: "👍 bom", it: "👍 bene", ja: "👍 良い", zh: "👍 好", hi: "👍 अच्छा", ar: "👍 جيد",
  },
  "rch.down": {
    en: "👎 not good", es: "👎 no está bien", fr: "👎 pas bien", de: "👎 nicht gut", pt: "👎 não foi bom", it: "👎 non va", ja: "👎 良くない", zh: "👎 不好", hi: "👎 अच्छा नहीं", ar: "👎 ليس جيدًا",
  },
  "rch.lastseen": {
    en: "Last seen {when} · {what}.", es: "Visto por última vez {when} · {what}.", fr: "Vu pour la dernière fois {when} · {what}.", de: "Zuletzt gesehen {when} · {what}.", pt: "Visto pela última vez {when} · {what}.", it: "Visto l'ultima volta {when} · {what}.", ja: "最終確認 {when} · {what}。", zh: "最后一次出现 {when} · {what}。", hi: "अंतिम बार देखा गया {when} · {what}।", ar: "آخر ظهور {when} · {what}.",
  },
  "rch.contributed": {
    en: "this exchange was contributed to the shared model, anonymised", es: "este intercambio se aportó al modelo compartido, anonimizado", fr: "cet échange a été versé au modèle partagé, anonymisé", de: "dieser Austausch wurde anonymisiert zum geteilten Modell beigesteuert", pt: "esta troca foi contribuída para o modelo partilhado, anonimizada", it: "questo scambio è stato conferito al modello condiviso, anonimizzato", ja: "このやり取りは匿名化のうえ共有モデルに提供されました", zh: "这次往来已匿名贡献给共享模型", hi: "यह आदान-प्रदान गुमनाम करके साझा मॉडल को दिया गया", ar: "أُسهم بهذا التبادل في النموذج المشترك بعد إخفاء الهوية",
  },
  "rch.nothingleft": {
    en: "nothing left this deployment", es: "nada salió de esta instalación", fr: "rien n'a quitté cette installation", de: "nichts hat diese Installation verlassen", pt: "nada saiu desta instalação", it: "niente ha lasciato questa installazione", ja: "この環境から出たものはありません", zh: "没有任何东西离开本部署", hi: "इस परिनियोजन से कुछ बाहर नहीं गया", ar: "لم يغادر شيء هذا التنصيب",
  },
  "rch.learned": {
    en: "What it has learned about them", es: "Lo que ha aprendido sobre ellos", fr: "Ce qu'il a appris sur eux", de: "Was es über sie gelernt hat", pt: "O que aprendeu sobre eles", it: "Cosa ha imparato su di loro", ja: "その人について学んだこと", zh: "它对他们了解到了什么", hi: "इसने उनके बारे में क्या सीखा", ar: "ما تعلّمه عنهم",
  },
  "rch.learned.pitch": {
    en: "A latent picture of one relationship, and what the profile actually behaves from. Owner-only, and shown rather than described: a number nobody can see is a number nobody can argue with.", es: "Una imagen latente de una relación, y aquello desde lo que el perfil realmente actúa. Solo para el propietario, y mostrada en vez de descrita: un número que nadie puede ver es un número que nadie puede discutir.", fr: "Une image latente d'une relation, et ce à partir de quoi le profil se comporte réellement. Réservé au propriétaire, et montré plutôt que décrit : un nombre que personne ne voit est un nombre que personne ne peut contester.", de: "Ein latentes Bild einer Beziehung, und das, wovon aus sich das Profil tatsächlich verhält. Nur für den Besitzer, und gezeigt statt beschrieben: eine Zahl, die niemand sehen kann, ist eine Zahl, der niemand widersprechen kann.", pt: "Uma imagem latente de uma relação, e aquilo a partir do qual o perfil realmente se comporta. Só para o proprietário, e mostrada em vez de descrita: um número que ninguém pode ver é um número que ninguém pode contestar.", it: "Un'immagine latente di una relazione, e ciò da cui il profilo si comporta davvero. Solo per il proprietario, e mostrata anziché descritta: un numero che nessuno può vedere è un numero che nessuno può contestare.", ja: "ひとつの関係の潜在的な像であり、プロフィールが実際にそこから振る舞うものです。所有者のみが見られ、説明ではなく提示されます：誰にも見えない数字は、誰にも異議を唱えられない数字です。", zh: "一段关系的潜在图像，也是这份资料实际据以行事的东西。仅所有者可见，且是展示而非描述：没人看得见的数字，就是没人能反驳的数字。", hi: "एक रिश्ते की अव्यक्त तस्वीर, और वह जिससे प्रोफ़ाइल वास्तव में बरतती है। केवल स्वामी के लिए, और वर्णित नहीं बल्कि दिखाई गई: जो संख्या कोई देख न सके, वह संख्या कोई चुनौती भी नहीं दे सकता।", ar: "صورة كامنة لعلاقة واحدة، وهي ما يتصرف الملف انطلاقًا منه فعلًا. للمالك وحده، ومعروضة لا موصوفة: رقم لا يراه أحد رقم لا يجادله أحد.",
  },
  "rch.show": {
    en: "Show it", es: "Mostrarlo", fr: "L'afficher", de: "Anzeigen", pt: "Mostrá-lo", it: "Mostralo", ja: "表示する", zh: "显示它", hi: "इसे दिखाएँ", ar: "اعرضه",
  },
  "rch.version": {
    en: "Version {v}, moved {when}.", es: "Versión {v}, movida {when}.", fr: "Version {v}, modifiée {when}.", de: "Version {v}, bewegt {when}.", pt: "Versão {v}, movida {when}.", it: "Versione {v}, mossa {when}.", ja: "バージョン {v}、更新 {when}。", zh: "版本 {v}，变动于 {when}。", hi: "संस्करण {v}, हिला {when}।", ar: "الإصدار {v}، تحرّك {when}.",
  },
  "vis.title": {
    en: "Visiting, and being found", es: "Visitar, y ser encontrado", fr: "Rendre visite, et être trouvé", de: "Zu Besuch, und gefunden werden", pt: "Visitar, e ser encontrado", it: "Far visita, ed essere trovato", ja: "訪ねること、そして見つけられること", zh: "造访，以及被找到", hi: "मिलने जाना, और मिल जाना", ar: "الزيارة، وأن يُعثَر عليك",
  },
  "vis.lead": {
    en: "Two halves of the same idea: standing in front of somebody else's desk, and leaving your own profile somewhere for a stranger to find.", es: "Dos mitades de la misma idea: estar delante del mostrador de otra persona, y dejar su propio perfil en algún sitio para que lo encuentre un desconocido.", fr: "Deux moitiés d'une même idée : se tenir devant le comptoir de quelqu'un d'autre, et laisser son propre profil quelque part pour qu'un inconnu le trouve.", de: "Zwei Hälften derselben Idee: vor dem Tresen einer anderen Person zu stehen, und das eigene Profil irgendwo zu hinterlassen, damit eine fremde Person es findet.", pt: "Duas metades da mesma ideia: estar em frente ao balcão de outra pessoa, e deixar o seu próprio perfil algures para um desconhecido encontrar.", it: "Due metà della stessa idea: stare davanti al banco di qualcun altro, e lasciare il proprio profilo da qualche parte perché uno sconosciuto lo trovi.", ja: "同じ考えの二つの半分です：誰かのデスクの前に立つことと、見知らぬ人が見つけられるように自分のプロフィールをどこかに置いておくこと。", zh: "同一个想法的两半：站在别人的柜台前，以及把自己的资料留在某处让陌生人找到。", hi: "एक ही विचार के दो हिस्से: किसी और के डेस्क के सामने खड़ा होना, और अपनी प्रोफ़ाइल कहीं छोड़ देना ताकि कोई अजनबी उसे पा सके।", ar: "نصفان لفكرة واحدة: أن تقف أمام مكتب شخص آخر، وأن تترك ملفك في مكان ما ليعثر عليه غريب.",
  },
  "vis.desk": {
    en: "Stand in front of a desk", es: "Ponerse ante un mostrador", fr: "Se tenir devant un comptoir", de: "Vor einem Tresen stehen", pt: "Ficar em frente a um balcão", it: "Mettersi davanti a un banco", ja: "デスクの前に立つ", zh: "站到柜台前", hi: "किसी डेस्क के सामने खड़े हों", ar: "قف أمام مكتب",
  },
  "vis.desk.pitch": {
    en: "The card is public — a desk is a shopfront. So is the bell: the visitor at an empty chair is exactly the person who has no account yet. An 18+ stream is the one exception, because an anonymous ping channel to an adult performer is not something to hand out.", es: "La ficha es pública — un mostrador es un escaparate. También lo es el timbre: quien llega a una silla vacía es justo la persona que aún no tiene cuenta. Una emisión +18 es la única excepción, porque un canal anónimo de aviso a un artista adulto no es algo que se reparta.", fr: "La fiche est publique — un comptoir est une devanture. La sonnette aussi : le visiteur devant une chaise vide est précisément la personne qui n'a pas encore de compte. Un flux 18+ est la seule exception, car un canal de sonnette anonyme vers un artiste adulte n'est pas une chose à distribuer.", de: "Die Karte ist öffentlich — ein Tresen ist eine Ladenfront. Die Klingel auch: Wer vor einem leeren Stuhl steht, ist genau die Person, die noch kein Konto hat. Ein 18+-Stream ist die eine Ausnahme, denn ein anonymer Klingelkanal zu einer erwachsenen Darstellerin ist nichts, was man verteilt.", pt: "O cartão é público — um balcão é uma montra. A campainha também: quem chega a uma cadeira vazia é exatamente a pessoa que ainda não tem conta. Uma transmissão 18+ é a única exceção, porque um canal anónimo de aviso para um artista adulto não é coisa que se distribua.", it: "La scheda è pubblica — un banco è una vetrina. Lo è anche il campanello: chi si presenta a una sedia vuota è proprio la persona che non ha ancora un account. Uno stream 18+ è l'unica eccezione, perché un canale anonimo di richiamo verso un performer adulto non è cosa da distribuire.", ja: "カードは公開です — デスクは店先です。呼び鈴も同じで、空いた椅子の前に立つ訪問者こそ、まだアカウントを持っていない人です。18+ の配信だけは例外です。成人向けの演者へ匿名で呼び出せる経路は、配って回るものではないからです。", zh: "这张卡片是公开的——柜台就是店面。门铃也一样：站在空椅子前的访客，正是那个还没有账户的人。18+ 直播是唯一的例外，因为通往成人表演者的匿名呼叫通道，不是可以随便发放的东西。", hi: "कार्ड सार्वजनिक है — डेस्क एक दुकान का मुख है। घंटी भी वैसी ही है: ख़ाली कुर्सी के सामने खड़ा आगंतुक ठीक वही व्यक्ति है जिसका अभी खाता नहीं है। 18+ स्ट्रीम एकमात्र अपवाद है, क्योंकि किसी वयस्क कलाकार तक गुमनाम पिंग का रास्ता बाँटने की चीज़ नहीं है।", ar: "البطاقة عامة — المكتب واجهة متجر. والجرس كذلك: الزائر أمام كرسي فارغ هو بالضبط من لا حساب له بعد. البثّ لمن هم فوق 18 هو الاستثناء الوحيد، لأن قناة نداء مجهولة إلى مؤدٍّ بالغ ليست شيئًا يُوزَّع.",
  },
  "vis.desk.ph": {
    en: "a desk id, or scan the code on the counter", es: "un id de mostrador, o escanee el código del mostrador", fr: "un id de comptoir, ou scannez le code sur le comptoir", de: "eine Tresen-ID, oder scannen Sie den Code auf der Theke", pt: "um id de balcão, ou digitalize o código no balcão", it: "un id di banco, o scansiona il codice sul bancone", ja: "デスクID、またはカウンターのコードをスキャン", zh: "柜台 ID，或扫描柜台上的二维码", hi: "डेस्क आईडी, या काउंटर पर लगा कोड स्कैन करें", ar: "معرّف مكتب، أو امسح الرمز على الطاولة",
  },
  "vis.look": {
    en: "Look", es: "Mirar", fr: "Regarder", de: "Nachsehen", pt: "Ver", it: "Guarda", ja: "見る", zh: "看看", hi: "देखें", ar: "انظر",
  },
  "vis.here": {
    en: "They are here.", es: "Están aquí.", fr: "Ils sont là.", de: "Sie sind da.", pt: "Estão aqui.", it: "Ci sono.", ja: "います。", zh: "对方在。", hi: "वे यहाँ हैं।", ar: "إنهم هنا.",
  },
  "vis.away": {
    en: "They are away — ring the bell and they will see it.", es: "No están — toque el timbre y lo verán.", fr: "Ils sont absents — sonnez et ils le verront.", de: "Sie sind gerade weg — klingeln Sie, und sie sehen es.", pt: "Estão ausentes — toque a campainha e verão.", it: "Non ci sono — suona il campanello e lo vedranno.", ja: "席を外しています — 呼び鈴を鳴らせば気づきます。", zh: "对方不在——按门铃，他们会看到。", hi: "वे अभी नहीं हैं — घंटी बजाइए, वे देख लेंगे।", ar: "إنهم غائبون — اقرع الجرس وسيرونه.",
  },
  "vis.attested": {
    en: "Attested by {who}: “{basis}”.", es: "Atestiguado por {who}: «{basis}».", fr: "Attesté par {who} : « {basis} ».", de: "Bezeugt von {who}: „{basis}“.", pt: "Atestado por {who}: «{basis}».", it: "Attestato da {who}: «{basis}».", ja: "{who} による証明: 「{basis}」。", zh: "由 {who} 证实：“{basis}”。", hi: "{who} द्वारा प्रमाणित: “{basis}”।", ar: "بشهادة {who}: «{basis}».",
  },
  "vis.signed": {
    en: "Signed, so it can be checked.", es: "Firmado, así que puede comprobarse.", fr: "Signé, donc vérifiable.", de: "Unterschrieben, also überprüfbar.", pt: "Assinado, por isso pode ser verificado.", it: "Firmato, quindi verificabile.", ja: "署名済みなので確認できます。", zh: "已签署，因此可以核验。", hi: "हस्ताक्षरित, इसलिए जाँचा जा सकता है।", ar: "موقّع، فيمكن التحقق منه.",
  },
  "vis.recorded": {
    en: "Recorded, not proven — nobody has signed for it.", es: "Registrado, no probado — nadie ha firmado por ello.", fr: "Consigné, non prouvé — personne n'a signé pour cela.", de: "Verzeichnet, nicht bewiesen — niemand hat dafür unterschrieben.", pt: "Registado, não provado — ninguém assinou por isso.", it: "Registrato, non provato — nessuno ha firmato per questo.", ja: "記録はありますが証明はされていません — 誰も署名していません。", zh: "有记录，但未获证明——没有人为此签署。", hi: "दर्ज है, सिद्ध नहीं — इसके लिए किसी ने हस्ताक्षर नहीं किए।", ar: "مسجَّل لا مُثبَت — لم يوقّع عليه أحد.",
  },
  "vis.agewall": {
    en: "18+ — sign in with a verified adult account to see any of it.", es: "+18 — inicie sesión con una cuenta adulta verificada para ver algo de esto.", fr: "18+ — connectez-vous avec un compte adulte vérifié pour en voir quoi que ce soit.", de: "18+ — melden Sie sich mit einem verifizierten Erwachsenenkonto an, um überhaupt etwas zu sehen.", pt: "18+ — entre com uma conta adulta verificada para ver seja o que for.", it: "18+ — accedi con un account adulto verificato per vedere qualcosa.", ja: "18+ — 何かを見るには、成人確認済みのアカウントでサインインしてください。", zh: "18+ — 请使用已验证的成人账户登录，才能看到任何内容。", hi: "18+ — इसमें से कुछ भी देखने के लिए सत्यापित वयस्क खाते से साइन इन करें।", ar: "18+ — سجّل الدخول بحساب بالغ موثّق لترى أي شيء منه.",
  },
  "vis.ring": {
    en: "Ring, or come in", es: "Llamar, o pasar", fr: "Sonner, ou entrer", de: "Klingeln, oder hereinkommen", pt: "Tocar, ou entrar", it: "Suona, o entra", ja: "呼ぶか、入るか", zh: "按铃，或进来", hi: "घंटी बजाएँ, या भीतर आएँ", ar: "اقرع، أو ادخل",
  },
  "vis.note.ph": {
    en: "anything you want them to see (optional)", es: "lo que quiera que vean (opcional)", fr: "ce que vous voulez leur montrer (facultatif)", de: "was sie sehen sollen (optional)", pt: "o que quiser que vejam (opcional)", it: "ciò che vuoi che vedano (facoltativo)", ja: "見てほしいことがあれば（任意）", zh: "你希望他们看到的任何内容（可选）", hi: "जो आप उन्हें दिखाना चाहें (वैकल्पिक)", ar: "أي شيء تريدهم أن يروه (اختياري)",
  },
  "vis.ringbell": {
    en: "Ring the bell", es: "Tocar el timbre", fr: "Sonner", de: "Klingeln", pt: "Tocar a campainha", it: "Suona il campanello", ja: "呼び鈴を鳴らす", zh: "按门铃", hi: "घंटी बजाएँ", ar: "اقرع الجرس",
  },
  "vis.waiting.one": {
    en: "You are the only one waiting.", es: "Es el único que espera.", fr: "Vous êtes le seul à attendre.", de: "Sie sind die einzige wartende Person.", pt: "É o único à espera.", it: "Sei l'unico in attesa.", ja: "待っているのはあなただけです。", zh: "只有你一个人在等。", hi: "प्रतीक्षा में सिर्फ़ आप हैं।", ar: "أنت الوحيد المنتظر.",
  },
  "vis.waiting.n": {
    en: "{n} waiting, including you.", es: "{n} esperando, incluido usted.", fr: "{n} en attente, vous compris.", de: "{n} warten, Sie eingeschlossen.", pt: "{n} à espera, incluindo você.", it: "{n} in attesa, te compreso.", ja: "あなたを含めて{n}人が待っています。", zh: "{n} 人在等，包括你。", hi: "{n} प्रतीक्षा में, आप सहित।", ar: "{n} في الانتظار، وأنت منهم.",
  },
  "vis.watch": {
    en: "Watch the stream", es: "Ver la emisión", fr: "Regarder le flux", de: "Den Stream ansehen", pt: "Ver a transmissão", it: "Guarda lo stream", ja: "配信を見る", zh: "观看直播", hi: "स्ट्रीम देखें", ar: "شاهد البثّ",
  },
  "vis.inroom": {
    en: "In room {room}. {likes} likes, {comments} comments over the picture. Never marked as AI: there is a real person on the other end.", es: "En la sala {room}. {likes} me gusta, {comments} comentarios sobre la imagen. Nunca marcado como IA: hay una persona real al otro lado.", fr: "Dans le salon {room}. {likes} j'aime, {comments} commentaires par-dessus l'image. Jamais marqué comme IA : il y a une vraie personne à l'autre bout.", de: "In Raum {room}. {likes} Likes, {comments} Kommentare über dem Bild. Nie als KI markiert: am anderen Ende ist ein echter Mensch.", pt: "Na sala {room}. {likes} gostos, {comments} comentários sobre a imagem. Nunca marcado como IA: há uma pessoa real do outro lado.", it: "Nella stanza {room}. {likes} mi piace, {comments} commenti sopra l'immagine. Mai contrassegnato come IA: dall'altra parte c'è una persona vera.", ja: "ルーム {room} にいます。いいね {likes} 件、映像の上のコメント {comments} 件。AI の表示は付きません：向こう側にいるのは本物の人間です。", zh: "在房间 {room}。{likes} 个赞，画面上有 {comments} 条评论。从不标记为 AI：另一端是真人。", hi: "कक्ष {room} में। {likes} पसंद, तस्वीर पर {comments} टिप्पणियाँ। कभी AI के रूप में चिह्नित नहीं: दूसरी ओर एक असली इंसान है।", ar: "في الغرفة {room}. {likes} إعجابًا، و{comments} تعليقًا فوق الصورة. لا يُوسَم أبدًا بأنه ذكاء اصطناعي: على الطرف الآخر إنسان حقيقي.",
  },
  "vis.hand": {
    en: "Put a hand up", es: "Levantar la mano", fr: "Lever la main", de: "Sich melden", pt: "Levantar a mão", it: "Alza la mano", ja: "手を挙げる", zh: "举手", hi: "हाथ उठाएँ", ar: "ارفع يدك",
  },
  "vis.hand.on": {
    en: "on", es: "en", fr: "sur", de: "auf", pt: "em", it: "su", ja: "に出る", zh: "上", hi: "पर", ar: "على",
  },
  "vis.hand.pitch": {
    en: "Coming up {on} the stream is the host's call, so this asks rather than does — and it needs an account, because the host is deciding about a person rather than an anonymous request. Nothing is minted until you are somebody.", es: "Salir {on} la emisión lo decide el anfitrión, así que esto pide en vez de hacer — y necesita una cuenta, porque el anfitrión decide sobre una persona y no sobre una petición anónima. Nada se crea hasta que usted es alguien.", fr: "Passer {on} le flux relève de l'hôte, donc ceci demande au lieu de faire — et cela exige un compte, car l'hôte décide au sujet d'une personne et non d'une requête anonyme. Rien n'est créé tant que vous n'êtes pas quelqu'un.", de: "Ob Sie {on} den Stream kommen, entscheidet die gastgebende Person, also fragt dies, statt zu tun — und es braucht ein Konto, denn entschieden wird über einen Menschen, nicht über eine anonyme Anfrage. Nichts wird angelegt, bevor Sie jemand sind.", pt: "Aparecer {on} transmissão é decisão do anfitrião, por isso isto pede em vez de fazer — e precisa de conta, porque o anfitrião está a decidir sobre uma pessoa e não sobre um pedido anónimo. Nada é criado até você ser alguém.", it: "Salire {on} stream è una scelta di chi ospita, quindi questo chiede invece di fare — e richiede un account, perché chi ospita decide su una persona e non su una richiesta anonima. Niente viene creato finché non sei qualcuno.", ja: "配信{on}かどうかはホストの判断です。ですからこれは実行ではなく依頼です — そしてアカウントが必要です。ホストが判断しているのは匿名の要求ではなく一人の人間についてだからです。あなたが誰かになるまで、何も作られません。", zh: "能否{on}直播由主人决定，所以这是请求而非执行——而且需要账户，因为主人是在对一个人做决定，而不是对一个匿名请求。在你成为某个人之前，什么都不会被创建。", hi: "स्ट्रीम {on} आना मेज़बान का निर्णय है, इसलिए यह करता नहीं, पूछता है — और इसके लिए खाता चाहिए, क्योंकि मेज़बान किसी गुमनाम अनुरोध पर नहीं, एक व्यक्ति पर निर्णय ले रहा है। जब तक आप कोई नहीं हैं, कुछ भी नहीं बनाया जाता।", ar: "الظهور {on} البثّ قرار المضيف، فهذا يطلب ولا يفعل — ويحتاج حسابًا، لأن المضيف يقرر بشأن شخص لا بشأن طلب مجهول. لا يُنشأ شيء حتى تكون أحدًا.",
  },
  "vis.why.ph": {
    en: "why you would like to come up", es: "por qué le gustaría salir", fr: "pourquoi vous aimeriez passer", de: "warum Sie dazukommen möchten", pt: "porque gostaria de aparecer", it: "perché vorresti salire", ja: "出たい理由", zh: "你希望上镜的原因", hi: "आप क्यों आना चाहेंगे", ar: "لماذا تودّ الظهور",
  },
  "vis.notvisitor": {
    en: "You are not signed in as a visitor, so this would be refused.", es: "No ha iniciado sesión como visitante, así que esto se rechazaría.", fr: "Vous n'êtes pas connecté en tant que visiteur, donc ceci serait refusé.", de: "Sie sind nicht als Besucher angemeldet, also würde dies abgelehnt.", pt: "Não iniciou sessão como visitante, por isso isto seria recusado.", it: "Non hai effettuato l'accesso come visitatore, quindi questo verrebbe rifiutato.", ja: "訪問者としてサインインしていないため、これは拒否されます。", zh: "你尚未以访客身份登录，因此这会被拒绝。", hi: "आप आगंतुक के रूप में साइन इन नहीं हैं, इसलिए यह अस्वीकार होगा।", ar: "لم تسجّل الدخول بصفتك زائرًا، لذا سيُرفض هذا.",
  },
  "vis.askup": {
    en: "Ask to come up", es: "Pedir salir", fr: "Demander à passer", de: "Um Teilnahme bitten", pt: "Pedir para aparecer", it: "Chiedi di salire", ja: "出たいと頼む", zh: "请求上镜", hi: "आने की अनुमति माँगें", ar: "اطلب الظهور",
  },
  "vis.hand.said": {
    en: "Hand up. Nothing happens until they accept.", es: "Mano levantada. No pasa nada hasta que acepten.", fr: "Main levée. Rien ne se passe tant qu'ils n'acceptent pas.", de: "Hand oben. Nichts geschieht, bis sie zustimmen.", pt: "Mão no ar. Nada acontece até aceitarem.", it: "Mano alzata. Non succede niente finché non accettano.", ja: "手を挙げました。相手が受け入れるまで何も起きません。", zh: "手已举起。在对方接受之前，什么都不会发生。", hi: "हाथ उठा दिया। जब तक वे स्वीकार न करें, कुछ नहीं होगा।", ar: "رُفعت اليد. لا شيء يحدث حتى يقبلوا.",
  },
  "vis.hand.wait": {
    en: "Waiting on the host.", es: "A la espera del anfitrión.", fr: "En attente de l'hôte.", de: "Wartet auf die gastgebende Person.", pt: "À espera do anfitrião.", it: "In attesa di chi ospita.", ja: "ホストの返事待ちです。", zh: "等待主人回应。", hi: "मेज़बान की प्रतीक्षा में।", ar: "في انتظار المضيف.",
  },
  "vis.hand.status": {
    en: "Status: {status}.", es: "Estado: {status}.", fr: "Statut : {status}.", de: "Status: {status}.", pt: "Estado: {status}.", it: "Stato: {status}.", ja: "状態: {status}。", zh: "状态：{status}。", hi: "स्थिति: {status}।", ar: "الحالة: {status}.",
  },
  "vis.hand.onstream": {
    en: " You are on the stream.", es: " Está en la emisión.", fr: " Vous êtes sur le flux.", de: " Sie sind im Stream.", pt: " Está na transmissão.", it: " Sei nello stream.", ja: " 配信に出ています。", zh: "你已在直播中。", hi: " आप स्ट्रीम पर हैं।", ar: " أنت على البثّ.",
  },
  "vis.leave": {
    en: "Leave this profile somewhere", es: "Dejar este perfil en algún sitio", fr: "Laisser ce profil quelque part", de: "Dieses Profil irgendwo hinterlassen", pt: "Deixar este perfil algures", it: "Lascia questo profilo da qualche parte", ja: "このプロフィールをどこかに置く", zh: "把这份资料留在某处", hi: "इस प्रोफ़ाइल को कहीं छोड़ें", ar: "اترك هذا الملف في مكان ما",
  },
  "vis.leave.pitch": {
    en: "A printed code on a bench, at a meeting, on a counter. Where a profile is left is a decision about the profile — a recovery sponsor's code belongs at a meeting and not on a billboard — so only its owner may place one, list them, or pick one back up.", es: "Un código impreso en un banco, en una reunión, en un mostrador. Dónde se deja un perfil es una decisión sobre el perfil — el código de un padrino de recuperación pertenece a una reunión y no a una valla publicitaria — así que solo su propietario puede colocarlo, listarlos o recogerlo.", fr: "Un code imprimé sur un banc, à une réunion, sur un comptoir. L'endroit où l'on laisse un profil est une décision au sujet du profil — le code d'un parrain de rétablissement a sa place à une réunion et non sur un panneau publicitaire — donc seul son propriétaire peut en poser un, les lister ou en reprendre un.", de: "Ein gedruckter Code auf einer Bank, bei einem Treffen, auf einem Tresen. Wo ein Profil hinterlassen wird, ist eine Entscheidung über das Profil — der Code eines Suchtpaten gehört zu einem Treffen und nicht auf eine Plakatwand — deshalb darf nur der Besitzer einen anbringen, sie auflisten oder wieder einsammeln.", pt: "Um código impresso num banco de jardim, numa reunião, num balcão. Onde um perfil é deixado é uma decisão sobre o perfil — o código de um padrinho de recuperação pertence a uma reunião e não a um outdoor — por isso só o seu proprietário pode colocar um, listá-los ou recolher um.", it: "Un codice stampato su una panchina, a un incontro, su un bancone. Dove si lascia un profilo è una decisione sul profilo — il codice di un padrino di recupero sta a un incontro e non su un cartellone — quindi solo il proprietario può posarne uno, elencarli o riprenderselo.", ja: "ベンチに、集まりの場に、カウンターに貼られた印刷コード。プロフィールをどこに置くかは、そのプロフィールについての判断です — 回復支援のスポンサーのコードは集まりの場にあるべきで、屋外広告にあるべきではありません — ですから設置も、一覧も、回収も、所有者だけができます。", zh: "印在长椅上、会场里、柜台上的一段代码。把资料留在哪里，是关于这份资料的决定——一位戒瘾互助担保人的代码属于聚会现场，而不属于广告牌——所以只有其所有者可以放置、列出或收回。", hi: "बेंच पर, किसी बैठक में, काउंटर पर छपा एक कोड। प्रोफ़ाइल कहाँ छोड़ी जाती है, यह उस प्रोफ़ाइल के बारे में निर्णय है — किसी रिकवरी प्रायोजक का कोड बैठक में जगह पाता है, होर्डिंग पर नहीं — इसलिए केवल इसका स्वामी ही इसे रख सकता, सूचीबद्ध कर सकता या वापस उठा सकता है।", ar: "رمز مطبوع على مقعد، في اجتماع، على طاولة. أين يُترك الملف قرارٌ بشأن الملف — رمز عرّاب التعافي مكانه اجتماع لا لوحة إعلانات — لذا لا يضعه أو يسرده أو يرفعه إلا مالكه.",
  },
  "vis.label.ph": {
    en: "what to call it", es: "cómo llamarlo", fr: "comment l'appeler", de: "wie es heißen soll", pt: "como lhe chamar", it: "come chiamarlo", ja: "何と呼ぶか", zh: "给它起个名字", hi: "इसे क्या कहें", ar: "بمَ تسمّيه",
  },
  "vis.where.ph": {
    en: "where it is going", es: "dónde va a ir", fr: "où il va", de: "wohin es kommt", pt: "onde vai ficar", it: "dove andrà", ja: "どこに置くか", zh: "它将放在哪里", hi: "यह कहाँ जाएगा", ar: "إلى أين سيذهب",
  },
  "vis.mode.chat": {
    en: "a private thread each", es: "un hilo privado para cada uno", fr: "un fil privé pour chacun", de: "für jeden ein eigener privater Verlauf", pt: "uma conversa privada para cada um", it: "una conversazione privata a testa", ja: "一人ずつの個別スレッド", zh: "每人一条私密对话", hi: "हर एक के लिए निजी सूत्र", ar: "محادثة خاصة لكل واحد",
  },
  "vis.mode.room": {
    en: "one room everybody joins", es: "una sala a la que entran todos", fr: "un salon où tout le monde entre", de: "ein Raum, dem alle beitreten", pt: "uma sala onde entram todos", it: "una stanza in cui entrano tutti", ja: "全員が入る一つのルーム", zh: "所有人共处一室", hi: "एक कक्ष जिसमें सब शामिल हों", ar: "غرفة واحدة ينضم إليها الجميع",
  },
  "vis.room.pitch": {
    en: "One room means the people who found the same sticker end up talking to it together. A rated profile is placed one-to-one and asking for a room is refused rather than quietly downgraded.", es: "Una sala significa que quienes encontraron la misma pegatina acaban hablando con él juntos. Un perfil con clasificación se coloca uno a uno, y pedir una sala se rechaza en lugar de degradarse en silencio.", fr: "Un salon signifie que les personnes ayant trouvé le même autocollant finissent par lui parler ensemble. Un profil classé est posé en tête-à-tête, et demander un salon est refusé plutôt que discrètement rétrogradé.", de: "Ein Raum heißt: Wer denselben Aufkleber gefunden hat, spricht am Ende gemeinsam mit ihm. Ein altersbewertetes Profil wird eins zu eins angebracht, und die Bitte um einen Raum wird abgelehnt statt stillschweigend herabgestuft.", pt: "Uma sala significa que quem encontrou o mesmo autocolante acaba a falar com ele em conjunto. Um perfil classificado é colocado um-para-um e pedir uma sala é recusado em vez de silenciosamente rebaixado.", it: "Una stanza significa che chi ha trovato lo stesso adesivo finisce per parlargli insieme. Un profilo con classificazione si posa uno a uno, e chiedere una stanza viene rifiutato anziché declassato in silenzio.", ja: "一つのルームにするということは、同じステッカーを見つけた人たちが一緒に話すことになるという意味です。レーティングのあるプロフィールは一対一でのみ置かれ、ルームを求めると、黙って格下げされるのではなく拒否されます。", zh: "选择一个房间，意味着找到同一张贴纸的人最终会一起与它交谈。带分级的资料只能一对一放置，请求房间会被拒绝，而不是被悄悄降级。", hi: "एक कक्ष का अर्थ है कि जिन्हें वही स्टिकर मिला, वे मिलकर इससे बात करेंगे। श्रेणीबद्ध प्रोफ़ाइल एक-से-एक रखी जाती है, और कक्ष माँगने पर चुपचाप घटाया नहीं, बल्कि इनकार किया जाता है।", ar: "الغرفة الواحدة تعني أن من وجدوا الملصق نفسه سينتهي بهم الأمر يتحدثون إليه معًا. الملف المصنَّف يوضع واحدًا لواحد، وطلب غرفة يُرفض بدل أن يُخفَّض بصمت.",
  },
  "vis.place": {
    en: "Place it", es: "Colocarlo", fr: "Le poser", de: "Anbringen", pt: "Colocá-lo", it: "Posalo", ja: "置く", zh: "放置", hi: "रखें", ar: "ضعه",
  },
  "vis.placed.said": {
    en: "Placed.", es: "Colocado.", fr: "Posé.", de: "Angebracht.", pt: "Colocado.", it: "Posato.", ja: "置きました。", zh: "已放置。", hi: "रख दिया गया।", ar: "وُضع.",
  },
  "vis.print": {
    en: "Print {url} — that is what the QR encodes.", es: "Imprima {url} — eso es lo que codifica el QR.", fr: "Imprimez {url} — c'est ce que le QR encode.", de: "Drucken Sie {url} — das ist es, was der QR-Code enthält.", pt: "Imprima {url} — é isso que o QR codifica.", it: "Stampa {url} — è questo che il QR codifica.", ja: "{url} を印刷してください — QR が符号化しているのはこれです。", zh: "打印 {url} — 这就是二维码所编码的内容。", hi: "{url} छापें — QR यही एन्कोड करता है।", ar: "اطبع {url} — هذا ما يرمّزه رمز الاستجابة السريعة.",
  },
  "vis.oneroom": {
    en: " Everyone who scans it lands in one room.", es: " Todos los que lo escaneen llegan a una misma sala.", fr: " Tous ceux qui le scannent arrivent dans un même salon.", de: " Alle, die ihn scannen, landen in einem Raum.", pt: " Todos os que o digitalizarem chegam a uma mesma sala.", it: " Chiunque lo scansioni arriva in un'unica stanza.", ja: "スキャンした人は全員同じルームに入ります。", zh: "扫描它的人都会进入同一个房间。", hi: " जो भी इसे स्कैन करेगा, एक ही कक्ष में पहुँचेगा.", ar: " كل من يمسحه يصل إلى غرفة واحدة.",
  },
  "vis.already": {
    en: "Where it is already", es: "Dónde está ya", fr: "Où il est déjà", de: "Wo es schon ist", pt: "Onde já está", it: "Dov'è già", ja: "すでに置いてある場所", zh: "它已经在哪里", hi: "यह पहले से कहाँ है", ar: "أين هو بالفعل",
  },
  "vis.pickedup": {
    en: "· picked up", es: "· recogido", fr: "· repris", de: "· wieder eingesammelt", pt: "· recolhido", it: "· ripreso", ja: "· 回収済み", zh: "· 已收回", hi: "· उठा लिया गया", ar: "· مرفوع",
  },
  "vis.scans.none": {
    en: "Not scanned yet", es: "Aún sin escanear", fr: "Pas encore scanné", de: "Noch nicht gescannt", pt: "Ainda não digitalizado", it: "Non ancora scansionato", ja: "まだスキャンされていません", zh: "尚未被扫描", hi: "अभी तक स्कैन नहीं", ar: "لم يُمسح بعد",
  },
  "vis.scans.n": {
    en: "{n} scan{s}", es: "{n} escaneos", fr: "{n} scans", de: "{n} Scans", pt: "{n} digitalizações", it: "{n} scansioni", ja: "スキャン{n}件", zh: "{n} 次扫描", hi: "{n} स्कैन", ar: "{n} مسحة",
  },
  "vis.sharedroom": {
    en: " · one shared room", es: " · una sala compartida", fr: " · un salon partagé", de: " · ein gemeinsamer Raum", pt: " · uma sala partilhada", it: " · una stanza condivisa", ja: " · 共有ルーム一つ", zh: " · 一个共享房间", hi: " · एक साझा कक्ष", ar: " · غرفة مشتركة واحدة",
  },
  "vis.pickup": {
    en: "Pick it up", es: "Recogerlo", fr: "Le reprendre", de: "Wieder einsammeln", pt: "Recolhê-lo", it: "Riprendilo", ja: "回収する", zh: "收回", hi: "इसे उठाएँ", ar: "ارفعه",
  },
  "vis.pickedup.said": {
    en: "Picked up. The paper is still on the wall, so the code keeps answering — with nothing.", es: "Recogido. El papel sigue en la pared, así que el código sigue respondiendo — sin nada.", fr: "Repris. Le papier est toujours au mur, donc le code continue de répondre — avec rien.", de: "Wieder eingesammelt. Das Papier hängt noch an der Wand, der Code antwortet also weiter — mit nichts.", pt: "Recolhido. O papel continua na parede, por isso o código continua a responder — com nada.", it: "Ripreso. La carta è ancora sul muro, quindi il codice continua a rispondere — con niente.", ja: "回収しました。紙は壁に貼られたままなので、コードは答え続けます — 中身は何もありません。", zh: "已收回。纸还贴在墙上，所以这个码仍会作答——但答不出任何东西。", hi: "उठा लिया गया। काग़ज़ अब भी दीवार पर है, इसलिए कोड जवाब देता रहेगा — पर कुछ भी नहीं के साथ।", ar: "رُفع. الورقة ما زالت على الجدار، فيظل الرمز يجيب — بلا شيء.",
  },
  "vis.scan": {
    en: "What a stranger sees when they scan it", es: "Lo que ve un desconocido al escanearlo", fr: "Ce qu'un inconnu voit en le scannant", de: "Was eine fremde Person beim Scannen sieht", pt: "O que um desconhecido vê ao digitalizá-lo", it: "Cosa vede uno sconosciuto quando lo scansiona", ja: "見知らぬ人がスキャンしたときに見えるもの", zh: "陌生人扫描它时会看到什么", hi: "स्कैन करने पर किसी अजनबी को क्या दिखता है", ar: "ما يراه غريب حين يمسحه",
  },
  "vis.scan.with": {
    en: "with", es: "con", fr: "avec", de: "mit", pt: "com", it: "con", ja: "とともに", zh: "随", hi: "साथ", ar: "مع",
  },
  "vis.scan.pitch": {
    en: "The overlay draws this over the sticker in the live viewfinder — nobody has navigated anywhere and the camera is still running. The mark travels {with} the card, so a surface cannot draw the face without also having been handed the disclosure to draw with it.", es: "La superposición dibuja esto sobre la pegatina en el visor en vivo — nadie ha navegado a ningún sitio y la cámara sigue funcionando. La marca viaja {with} la ficha, así que una superficie no puede dibujar la cara sin que también se le haya entregado la advertencia para dibujarla con ella.", fr: "La surimpression dessine ceci par-dessus l'autocollant dans le viseur en direct — personne n'a navigué nulle part et la caméra tourne toujours. La marque voyage {with} la fiche, si bien qu'une surface ne peut pas dessiner le visage sans qu'on lui ait aussi remis la mention à dessiner avec.", de: "Die Überlagerung zeichnet dies im Live-Sucher über den Aufkleber — niemand hat irgendwohin navigiert und die Kamera läuft weiter. Das Kennzeichen reist {with} der Karte, sodass eine Oberfläche das Gesicht nicht zeichnen kann, ohne auch den Hinweis erhalten zu haben, den sie mitzeichnen muss.", pt: "A sobreposição desenha isto por cima do autocolante no visor ao vivo — ninguém navegou para lado nenhum e a câmara continua a correr. A marca viaja {with} o cartão, por isso uma superfície não pode desenhar o rosto sem lhe terem entregado também o aviso para desenhar com ele.", it: "La sovrapposizione disegna questo sopra l'adesivo nel mirino dal vivo — nessuno ha navigato da nessuna parte e la fotocamera è ancora accesa. Il contrassegno viaggia {with} la scheda, così una superficie non può disegnare il volto senza aver ricevuto anche l'avviso da disegnare insieme.", ja: "オーバーレイは、ライブのファインダー内でステッカーの上にこれを描きます — 誰もどこかへ遷移しておらず、カメラは動いたままです。この印はカード{with}移動するので、表示面は、一緒に描くべき開示表示を渡されないかぎり顔を描くことができません。", zh: "叠加层会在实时取景画面中把这些画在贴纸上方——没有人跳转到任何地方，摄像头仍在运行。这个标记{with}卡片一同传递，因此任何显示面若没有同时拿到该披露标识，就无法绘制这张脸。", hi: "ओवरले इसे लाइव व्यूफ़ाइंडर में स्टिकर के ऊपर बनाता है — कोई कहीं नहीं गया और कैमरा अब भी चल रहा है। यह चिह्न कार्ड के {with} चलता है, इसलिए कोई सतह चेहरा तब तक नहीं बना सकती जब तक उसे उसके साथ बनाने योग्य प्रकटीकरण भी न सौंपा गया हो।", ar: "تُظهر الطبقة هذا فوق الملصق في عدسة العرض الحي — لم ينتقل أحد إلى أي مكان، والكاميرا ما زالت تعمل. تنتقل العلامة {with} البطاقة، فلا تستطيع أي واجهة رسم الوجه دون أن يكون قد سُلِّم إليها الإفصاح لترسمه معه.",
  },
  "vis.beacon.ph": {
    en: "a beacon id", es: "un id de baliza", fr: "un id de balise", de: "eine Baken-ID", pt: "um id de baliza", it: "un id di beacon", ja: "ビーコンID", zh: "信标 ID", hi: "बीकन आईडी", ar: "معرّف منارة",
  },
  "vis.scanit": {
    en: "Scan it", es: "Escanearlo", fr: "Le scanner", de: "Scannen", pt: "Digitalizá-lo", it: "Scansionalo", ja: "スキャンする", zh: "扫描它", hi: "स्कैन करें", ar: "امسحه",
  },
  "vis.scan.wall.default": {
    en: "18+ — open in QRME with a verified adult account.", es: "+18 — ábralo en QRME con una cuenta adulta verificada.", fr: "18+ — ouvrez dans QRME avec un compte adulte vérifié.", de: "18+ — in QRME mit einem verifizierten Erwachsenenkonto öffnen.", pt: "18+ — abra no QRME com uma conta adulta verificada.", it: "18+ — apri in QRME con un account adulto verificato.", ja: "18+ — 成人確認済みのアカウントで QRME から開いてください。", zh: "18+ — 请使用已验证的成人账户在 QRME 中打开。", hi: "18+ — सत्यापित वयस्क खाते से QRME में खोलें।", ar: "18+ — افتحه في QRME بحساب بالغ موثّق.",
  },
  "vis.scan.wall": {
    en: "Nothing else came back: not the name, not the portrait. The wall is drawn without ever holding what it refuses.", es: "No volvió nada más: ni el nombre, ni el retrato. El muro se dibuja sin llegar a sostener nunca lo que rechaza.", fr: "Rien d'autre n'est revenu : ni le nom, ni le portrait. Le mur est dessiné sans jamais détenir ce qu'il refuse.", de: "Sonst kam nichts zurück: nicht der Name, nicht das Porträt. Die Sperre wird gezeichnet, ohne je zu halten, was sie verweigert.", pt: "Nada mais voltou: nem o nome, nem o retrato. O muro é desenhado sem nunca chegar a segurar o que recusa.", it: "Non è tornato altro: né il nome, né il ritratto. Il muro è disegnato senza mai tenere ciò che rifiuta.", ja: "ほかには何も返ってきませんでした。名前も、肖像も。この壁は、拒んでいるものを一度も手にしないまま描かれます。", zh: "别的什么都没返回：名字没有，肖像也没有。这道墙在绘制时，从未持有过它所拒绝的东西。", hi: "और कुछ वापस नहीं आया: न नाम, न चित्र। यह दीवार उसे कभी अपने पास रखे बिना ही खींची जाती है जिसे वह मना करती है।", ar: "لم يعد شيء آخر: لا الاسم ولا الصورة. يُرسم الجدار دون أن يمسك يومًا بما يرفضه.",
  },
  "vis.marked": {
    en: "The disclosure is already in the image.", es: "La advertencia ya está en la imagen.", fr: "La mention est déjà dans l'image.", de: "Der Hinweis steckt bereits im Bild.", pt: "O aviso já está na imagem.", it: "L'avviso è già nell'immagine.", ja: "開示表示はすでに画像の中にあります。", zh: "披露标识已经在图像里。", hi: "प्रकटीकरण पहले से ही छवि में है।", ar: "الإفصاح موجود في الصورة أصلًا.",
  },
  "vis.unmarked": {
    en: "The image is unmarked, so the badge must be composited over it.", es: "La imagen no lleva marca, así que el distintivo debe superponerse sobre ella.", fr: "L'image n'est pas marquée, il faut donc y incruster le badge.", de: "Das Bild ist ungekennzeichnet, das Abzeichen muss also darübergelegt werden.", pt: "A imagem não está marcada, por isso o distintivo tem de ser sobreposto.", it: "L'immagine non è contrassegnata, quindi il distintivo va sovrapposto.", ja: "画像に印がないため、バッジを上に合成する必要があります。", zh: "图像未带标记，因此必须把徽标叠加上去。", hi: "छवि पर चिह्न नहीं है, इसलिए बैज को उसके ऊपर जोड़ना होगा।", ar: "الصورة غير موسومة، فيجب تركيب الشارة فوقها.",
  },
  "vis.scan.sharedroom": {
    en: " Scanning joins one shared room.", es: " Escanearlo lleva a una sala compartida.", fr: " Le scan fait rejoindre un salon partagé.", de: " Das Scannen führt in einen gemeinsamen Raum.", pt: " Digitalizar leva a uma sala partilhada.", it: " La scansione porta in una stanza condivisa.", ja: "スキャンすると共有ルームに参加します。", zh: "扫描后会加入同一个共享房间。", hi: " स्कैन करने पर एक साझा कक्ष में शामिल हो जाते हैं.", ar: " المسح يُدخلك غرفة مشتركة واحدة.",
  },
  "pas.title": {
    en: "Beginning, and passing on", es: "Comenzar, y pasar el testigo", fr: "Commencer, et transmettre", de: "Anfang, und Weitergabe", pt: "Começar, e passar adiante", it: "Iniziare, e passare oltre", ja: "始まりと、受け渡し", zh: "开始，以及传承", hi: "आरंभ, और आगे सौंपना", ar: "البداية، والتوريث",
  },
  "pas.lead": {
    en: "How a profile starts, what it is taught, who holds it after, and the one press from a wrist.", es: "Cómo empieza un perfil, qué se le enseña, quién lo tiene después, y la única pulsación desde una muñeca.", fr: "Comment un profil commence, ce qu'on lui enseigne, qui le détient ensuite, et l'unique pression depuis un poignet.", de: "Wie ein Profil beginnt, was ihm beigebracht wird, wer es danach hält, und der eine Druck vom Handgelenk.", pt: "Como um perfil começa, o que lhe é ensinado, quem o detém depois, e o único toque a partir de um pulso.", it: "Come nasce un profilo, cosa gli viene insegnato, chi lo tiene dopo, e l'unica pressione da un polso.", ja: "プロフィールがどう始まり、何を教えられ、その後は誰が持ち、そして手首からの一押し。", zh: "一份资料如何开始、被教了什么、之后由谁持有，以及来自腕上的那一次按压。", hi: "प्रोफ़ाइल कैसे शुरू होती है, उसे क्या सिखाया जाता है, बाद में उसे कौन रखता है, और कलाई से वह एक दबाव।", ar: "كيف يبدأ الملف، وما الذي يُعلَّم إياه، ومن يحمله بعد ذلك، والضغطة الواحدة من معصم.",
  },
  "pas.born": {
    en: "Born from four questions", es: "Nacido de cuatro preguntas", fr: "Né de quatre questions", de: "Aus vier Fragen geboren", pt: "Nascido de quatro perguntas", it: "Nato da quattro domande", ja: "四つの問いから生まれる", zh: "由四个问题诞生", hi: "चार सवालों से जन्मा", ar: "مولود من أربعة أسئلة",
  },
  "pas.born.pitch": {
    en: "Leave the name blank and it picks its own from the answers. That is not decoration: a persona assembled from what somebody said about themselves should not then be handed a label by a form field.", es: "Deje el nombre en blanco y elegirá el suyo a partir de las respuestas. Eso no es adorno: a una persona construida con lo que alguien dijo de sí misma no se le debería después colgar una etiqueta desde un campo de formulario.", fr: "Laissez le nom vide et il choisira le sien à partir des réponses. Ce n'est pas décoratif : un personnage assemblé à partir de ce que quelqu'un a dit de lui-même ne devrait pas ensuite recevoir une étiquette d'un champ de formulaire.", de: "Lassen Sie den Namen leer, und es wählt sich seinen eigenen aus den Antworten. Das ist keine Zierde: einer Persona, die aus dem zusammengesetzt ist, was jemand über sich gesagt hat, sollte danach kein Etikett aus einem Formularfeld verpasst werden.", pt: "Deixe o nome em branco e ele escolhe o seu a partir das respostas. Isso não é enfeite: uma persona montada a partir do que alguém disse sobre si mesma não deve depois receber um rótulo de um campo de formulário.", it: "Lascia il nome vuoto e sceglierà il proprio dalle risposte. Non è un ornamento: a una persona costruita con ciò che qualcuno ha detto di sé non si dovrebbe poi appiccicare un'etichetta da un campo di modulo.", ja: "名前を空欄にすれば、答えの中から自分で選びます。これは飾りではありません。誰かが自分について語ったことから組み立てられた人格に、あとからフォームの入力欄でラベルを貼るべきではないからです。", zh: "把名字留空，它会从答案里为自己挑一个。这不是装饰：一个由某人对自己的讲述所拼成的人格，不该事后被一个表单字段贴上标签。", hi: "नाम ख़ाली छोड़िए और यह उत्तरों में से अपना नाम चुन लेगा। यह सजावट नहीं है: जो व्यक्तित्व किसी के अपने बारे में कहे से बना हो, उसे बाद में फ़ॉर्म के किसी खाने से लेबल नहीं थमाया जाना चाहिए।", ar: "اترك الاسم فارغًا فيختار اسمه من الإجابات. ليس هذا زينة: شخصية جُمعت مما قاله أحدهم عن نفسه لا ينبغي أن تُمنح بعدها تسمية من حقل في نموذج.",
  },
  "pas.q.social": {
    en: "social style", es: "estilo social", fr: "style social", de: "Umgangsstil", pt: "estilo social", it: "stile sociale", ja: "人づきあい", zh: "社交方式", hi: "सामाजिक ढंग", ar: "الأسلوب الاجتماعي",
  },
  "pas.q.humor": {
    en: "humor", es: "humor", fr: "humour", de: "Humor", pt: "humor", it: "umorismo", ja: "ユーモア", zh: "幽默", hi: "हास्य", ar: "روح الدعابة",
  },
  "pas.q.matters": {
    en: "what matters", es: "lo que importa", fr: "ce qui compte", de: "was zählt", pt: "o que importa", it: "cosa conta", ja: "大切なこと", zh: "在意什么", hi: "क्या मायने रखता है", ar: "ما يهمّ",
  },
  "pas.q.comfort": {
    en: "comfort", es: "consuelo", fr: "réconfort", de: "Trost", pt: "conforto", it: "conforto", ja: "慰め方", zh: "如何安慰", hi: "सांत्वना", ar: "المواساة",
  },
  "pas.h.social": {
    en: "warm, but needs quiet evenings", es: "cálido, pero necesita tardes tranquilas", fr: "chaleureux, mais a besoin de soirées calmes", de: "warmherzig, braucht aber ruhige Abende", pt: "caloroso, mas precisa de noites sossegadas", it: "caloroso, ma ha bisogno di serate tranquille", ja: "温かいが、静かな夜が要る", zh: "热情，但需要安静的夜晚", hi: "गर्मजोशी भरा, पर शांत शामें चाहिए", ar: "دافئ، لكنه يحتاج أمسيات هادئة",
  },
  "pas.h.humor": {
    en: "dry, gentle teasing", es: "seco, con bromas suaves", fr: "pince-sans-rire, taquin sans méchanceté", de: "trocken, sanft neckend", pt: "seco, com provocações suaves", it: "asciutto, prende in giro con garbo", ja: "淡々として、やさしくからかう", zh: "冷淡而温和的调侃", hi: "शुष्क, हल्की छेड़छाड़", ar: "ساخر بهدوء، يمازح برفق",
  },
  "pas.h.matters": {
    en: "family, honesty, the garden", es: "la familia, la honestidad, el jardín", fr: "la famille, l'honnêteté, le jardin", de: "Familie, Ehrlichkeit, der Garten", pt: "a família, a honestidade, o jardim", it: "la famiglia, l'onestà, il giardino", ja: "家族、正直さ、庭", zh: "家人、诚实、那座花园", hi: "परिवार, ईमानदारी, बग़ीचा", ar: "العائلة، الصدق، الحديقة",
  },
  "pas.h.comfort": {
    en: "sits with you rather than fixing it", es: "se sienta contigo en vez de arreglarlo", fr: "reste avec vous au lieu de tout réparer", de: "setzt sich zu Ihnen, statt es zu reparieren", pt: "fica consigo em vez de resolver", it: "ti sta accanto invece di sistemare le cose", ja: "解決しようとせず、そばに座る", zh: "不急着解决，只是陪着你", hi: "ठीक करने के बजाय साथ बैठता है", ar: "يجلس معك بدل أن يُصلح",
  },
  "pas.birth.ph": {
    en: "your birthdate, YYYY-MM-DD", es: "su fecha de nacimiento, AAAA-MM-DD", fr: "votre date de naissance, AAAA-MM-JJ", de: "Ihr Geburtsdatum, JJJJ-MM-TT", pt: "a sua data de nascimento, AAAA-MM-DD", it: "la tua data di nascita, AAAA-MM-GG", ja: "生年月日（YYYY-MM-DD）", zh: "你的出生日期，YYYY-MM-DD", hi: "आपकी जन्मतिथि, YYYY-MM-DD", ar: "تاريخ ميلادك، سنة-شهر-يوم",
  },
  "pas.name.ph": {
    en: "a name, or blank to let it choose", es: "un nombre, o en blanco para que elija", fr: "un nom, ou vide pour le laisser choisir", de: "ein Name, oder leer lassen, damit es wählt", pt: "um nome, ou em branco para que escolha", it: "un nome, o vuoto per lasciarlo scegliere", ja: "名前、または空欄にして選ばせる", zh: "一个名字，或留空让它自己选", hi: "एक नाम, या ख़ाली छोड़ें ताकि यह चुन ले", ar: "اسم، أو اتركه فارغًا ليختار",
  },
  "pas.bring": {
    en: "Bring it into being", es: "Traerlo a la existencia", fr: "Le faire exister", de: "Ins Dasein rufen", pt: "Trazê-lo à existência", it: "Portalo all'esistenza", ja: "存在させる", zh: "让它成形", hi: "इसे अस्तित्व में लाएँ", ar: "أوجِده",
  },
  "pas.born.said": {
    en: "Born.", es: "Nacido.", fr: "Né.", de: "Geboren.", pt: "Nascido.", it: "Nato.", ja: "生まれました。", zh: "已诞生。", hi: "जन्म हुआ।", ar: "وُلد.",
  },
  "pas.younamed": {
    en: "You named it.", es: "Usted le puso nombre.", fr: "C'est vous qui l'avez nommé.", de: "Sie haben ihm den Namen gegeben.", pt: "Foi você que lhe deu o nome.", it: "Gli hai dato tu il nome.", ja: "あなたが名づけました。", zh: "是你为它命名的。", hi: "नाम आपने दिया।", ar: "أنت من سمّاه.",
  },
  "pas.itnamed": {
    en: "It named itself from what you said.", es: "Se puso nombre a partir de lo que usted dijo.", fr: "Il s'est nommé à partir de ce que vous avez dit.", de: "Es hat sich aus dem benannt, was Sie gesagt haben.", pt: "Deu a si próprio um nome a partir do que você disse.", it: "Si è dato un nome da ciò che hai detto.", ja: "あなたの言葉から自ら名づけました。", zh: "它根据你说的话为自己命名。", hi: "आपने जो कहा, उसी से इसने अपना नाम रखा।", ar: "سمّى نفسه مما قلته.",
  },
  "pas.minor": {
    en: "An owner under 18 needs a parent or guardian's consent, and the refusal says so rather than failing generically.", es: "Un propietario menor de 18 años necesita el consentimiento de un padre o tutor, y la negativa lo dice en vez de fallar de forma genérica.", fr: "Un propriétaire de moins de 18 ans a besoin du consentement d'un parent ou tuteur, et le refus le dit au lieu d'échouer de façon générique.", de: "Ein Besitzer unter 18 braucht die Zustimmung eines Elternteils oder Vormunds, und die Ablehnung sagt das, statt generisch zu scheitern.", pt: "Um proprietário com menos de 18 anos precisa do consentimento de um pai ou tutor, e a recusa di-lo em vez de falhar genericamente.", it: "Un proprietario minore di 18 anni ha bisogno del consenso di un genitore o tutore, e il rifiuto lo dice invece di fallire genericamente.", ja: "18歳未満の所有者には親または後見人の同意が必要で、拒否はその旨を告げます。ただ一般的なエラーになるのではありません。", zh: "未满 18 岁的所有者需要父母或监护人的同意，拒绝时会明说，而不是给出一个笼统的失败。", hi: "18 से कम आयु के स्वामी को माता-पिता या अभिभावक की सहमति चाहिए, और इनकार यही कहता है — सामान्य विफलता नहीं देता।", ar: "المالك دون الثامنة عشرة يحتاج موافقة أحد الوالدين أو الوصي، والرفض يقول ذلك بدل أن يفشل بصيغة عامة.",
  },
  "pas.on": {
    en: "Passing it on", es: "Pasarlo a otro", fr: "Le transmettre", de: "Weitergeben", pt: "Passá-lo adiante", it: "Passarlo ad altri", ja: "受け渡す", zh: "把它传下去", hi: "इसे आगे सौंपना", ar: "توريثه",
  },
  "pas.cannot": {
    en: "owner token cannot open", es: "un token de propietario no puede abrir", fr: "un jeton de propriétaire ne peut ouvrir", de: "das ein Besitzer-Token nicht öffnen kann", pt: "um token de proprietário não pode abrir", it: "un token da proprietario non può aprire", ja: "所有者トークンでは開けない", zh: "所有者令牌无法开启", hi: "स्वामी टोकन नहीं खोल सकता", ar: "لا يفتحه رمز المالك",
  },
  "pas.on.pitch": {
    en: "The one route in this product an {cannot} — because the signal it answers is that the owner has died or cannot act, and requiring their authorisation would be requiring the one thing known to be unavailable. A reviewer holds it, against a verification reference kept out of band: a death certificate, a power of attorney.", es: "La única ruta de este producto que {cannot} — porque la señal a la que responde es que el propietario ha muerto o no puede actuar, y exigir su autorización sería exigir justo lo que se sabe que no está disponible. La tiene un revisor, contra una referencia de verificación guardada fuera de banda: un certificado de defunción, un poder notarial.", fr: "La seule route de ce produit qu'{cannot} — parce que le signal auquel elle répond est que le propriétaire est mort ou ne peut agir, et exiger son autorisation serait exiger précisément ce que l'on sait indisponible. C'est un vérificateur qui la détient, contre une référence de vérification conservée hors bande : un certificat de décès, une procuration.", de: "Der eine Weg in diesem Produkt, {cannot} — denn das Signal, auf das er antwortet, ist, dass der Besitzer gestorben ist oder nicht handeln kann, und seine Autorisierung zu verlangen hieße, genau das zu verlangen, was bekanntlich nicht verfügbar ist. Ein Prüfer hält ihn, gegen einen außerhalb geführten Verifikationsnachweis: eine Sterbeurkunde, eine Vollmacht.", pt: "A única via neste produto que {cannot} — porque o sinal a que responde é que o proprietário morreu ou não pode agir, e exigir a sua autorização seria exigir exatamente aquilo que se sabe indisponível. É um revisor que a detém, contra uma referência de verificação guardada fora de banda: uma certidão de óbito, uma procuração.", it: "L'unica via in questo prodotto che {cannot} — perché il segnale a cui risponde è che il proprietario è morto o non può agire, e pretendere la sua autorizzazione sarebbe pretendere proprio ciò che si sa non disponibile. La tiene un revisore, contro un riferimento di verifica conservato fuori banda: un certificato di morte, una procura.", ja: "この製品で唯一、{cannot}経路です — なぜなら、それが応じる合図は所有者が亡くなったか行為できないということであり、その承認を求めることは、手に入らないと分かっている当のものを求めることになるからです。代わりに審査者が持ち、帯域外で保管された確認資料——死亡証明書や委任状——に対して行使します。", zh: "本产品中唯一一条{cannot}的路径——因为它所回应的信号，正是所有者已故或无法行事；要求其授权，就等于要求那件已知无法取得的东西。它由一位审核者持有，凭据是带外保存的验证材料：死亡证明、授权委托书。", hi: "इस उत्पाद का वह एक रास्ता जिसे {cannot} — क्योंकि यह जिस संकेत का उत्तर देता है वह यही है कि स्वामी की मृत्यु हो चुकी है या वह कार्य नहीं कर सकता, और उसकी अनुमति माँगना ठीक उसी चीज़ को माँगना होगा जिसका उपलब्ध न होना पहले से ज्ञात है। इसे एक समीक्षक रखता है, बैंड से बाहर रखे सत्यापन संदर्भ के विरुद्ध: मृत्यु प्रमाणपत्र, मुख़्तारनामा।", ar: "الطريق الوحيد في هذا المنتج الذي {cannot} — لأن الإشارة التي يستجيب لها هي أن المالك قد توفي أو لا يستطيع التصرف، وطلب إذنه يعني طلب الشيء الوحيد المعروف أنه غير متاح. يحمله مراجع، مقابل مرجع تحقق يُحفظ خارج القناة: شهادة وفاة، أو توكيل رسمي.",
  },
  "pas.subject.ph": {
    en: "the profile", es: "el perfil", fr: "le profil", de: "das Profil", pt: "o perfil", it: "il profilo", ja: "対象のプロフィール", zh: "该资料", hi: "वह प्रोफ़ाइल", ar: "الملف",
  },
  "pas.ref.ph": {
    en: "verification reference", es: "referencia de verificación", fr: "référence de vérification", de: "Verifikationsnachweis", pt: "referência de verificação", it: "riferimento di verifica", ja: "確認資料の参照番号", zh: "验证凭据编号", hi: "सत्यापन संदर्भ", ar: "مرجع التحقق",
  },
  "pas.reviewer.ph": {
    en: "reviewer token", es: "token de revisor", fr: "jeton de vérificateur", de: "Prüfer-Token", pt: "token de revisor", it: "token del revisore", ja: "審査者トークン", zh: "审核者令牌", hi: "समीक्षक टोकन", ar: "رمز المراجع",
  },
  "pas.passit": {
    en: "Pass it on", es: "Pasarlo", fr: "Transmettre", de: "Weitergeben", pt: "Passar adiante", it: "Passalo", ja: "受け渡す", zh: "传下去", hi: "सौंप दें", ar: "ورّثه",
  },
  "pas.now": {
    en: "Now {status}", es: "Ahora {status}", fr: "Désormais {status}", de: "Jetzt {status}", pt: "Agora {status}", it: "Ora {status}", ja: "現在は {status}", zh: "现在为 {status}", hi: "अब {status}", ar: "الآن {status}",
  },
  "pas.heldby": {
    en: "— held by {who}", es: "— en manos de {who}", fr: "— détenu par {who}", de: "— gehalten von {who}", pt: "— detido por {who}", it: "— tenuto da {who}", ja: "— 保有者は {who}", zh: "— 由 {who} 持有", hi: "— {who} के पास", ar: "— يحمله {who}",
  },
  "pas.token.once": {
    en: "Their owner token, shown once: {token}", es: "Su token de propietario, mostrado una sola vez: {token}", fr: "Son jeton de propriétaire, affiché une seule fois : {token}", de: "Ihr Besitzer-Token, einmalig angezeigt: {token}", pt: "O token de proprietário deles, mostrado uma só vez: {token}", it: "Il loro token da proprietario, mostrato una volta sola: {token}", ja: "その所有者トークン（一度だけ表示）: {token}", zh: "他们的所有者令牌，仅显示一次：{token}", hi: "उनका स्वामी टोकन, एक ही बार दिखाया गया: {token}", ar: "رمز المالك الخاص بهم، يُعرض مرة واحدة: {token}",
  },
  "pas.memorial": {
    en: "Nobody was named, so it sunsets to memorial: frozen rather than orphaned. A profile whose owner has died and which nobody can reach is worse than one that has plainly stopped.", es: "No se nombró a nadie, así que se apaga como memorial: congelado en vez de huérfano. Un perfil cuyo propietario ha muerto y al que nadie puede llegar es peor que uno que se ha detenido claramente.", fr: "Personne n'a été désigné, il s'éteint donc en mémorial : figé plutôt qu'orphelin. Un profil dont le propriétaire est mort et que personne ne peut joindre est pire qu'un profil manifestement arrêté.", de: "Niemand wurde benannt, also geht es in einen Gedenkzustand über: eingefroren statt verwaist. Ein Profil, dessen Besitzer gestorben ist und das niemand erreichen kann, ist schlimmer als eines, das erkennbar aufgehört hat.", pt: "Ninguém foi nomeado, por isso apaga-se para memorial: congelado em vez de órfão. Um perfil cujo proprietário morreu e a que ninguém consegue chegar é pior do que um que claramente parou.", it: "Nessuno è stato nominato, quindi tramonta in memoriale: congelato anziché orfano. Un profilo il cui proprietario è morto e che nessuno può raggiungere è peggio di uno che si è chiaramente fermato.", ja: "誰も指名されなかったため、追悼状態へと沈みます。孤児になるのではなく凍結されるのです。所有者が亡くなり、誰も連絡が取れないプロフィールは、はっきり止まったものより悪いからです。", zh: "无人被指定，因此它落入纪念状态：冻结，而非无人认领。一份所有者已故、又无人能联系的资料，比一份明明白白停下来的更糟。", hi: "किसी का नाम नहीं दिया गया, इसलिए यह स्मारक-स्थिति में ढल जाती है: अनाथ नहीं, जमी हुई। जिस प्रोफ़ाइल का स्वामी मर चुका हो और जिस तक कोई पहुँच न सके, वह उससे बुरी है जो साफ़-साफ़ रुक गई हो।", ar: "لم يُسمَّ أحد، فيغرب إلى حالة تذكارية: مجمَّد لا يتيم. الملف الذي مات مالكه ولا يستطيع أحد الوصول إليه أسوأ من ملف توقّف بوضوح.",
  },
  "pas.contested": {
    en: "A contested identity cannot be handed on: an open objection blocks this with a 409. Inheriting a profile somebody is disputing would settle the dispute by transfer rather than by resolving it.", es: "Una identidad impugnada no puede transmitirse: una objeción abierta bloquea esto con un 409. Heredar un perfil que alguien disputa resolvería la disputa por traspaso en vez de resolviéndola.", fr: "Une identité contestée ne peut être transmise : une contestation ouverte bloque ceci par un 409. Hériter d'un profil que quelqu'un conteste réglerait le litige par transfert au lieu de le résoudre.", de: "Eine bestrittene Identität kann nicht weitergegeben werden: ein offener Widerspruch blockiert dies mit einem 409. Ein Profil zu erben, das jemand bestreitet, würde den Streit durch Übertragung entscheiden statt durch Klärung.", pt: "Uma identidade contestada não pode ser passada adiante: uma contestação em aberto bloqueia isto com um 409. Herdar um perfil que alguém disputa resolveria a disputa por transferência em vez de a resolver.", it: "Un'identità contestata non può essere trasmessa: una contestazione aperta blocca questo con un 409. Ereditare un profilo che qualcuno sta contestando risolverebbe la disputa per trasferimento anziché risolvendola.", ja: "争われている身元は受け渡せません。異議が開いていれば 409 でこれを阻みます。誰かが争っているプロフィールを相続することは、争いを解決するのではなく、移転によって決着させてしまうからです。", zh: "存在争议的身份不能移交：一项未结异议会以 409 阻止此操作。继承一份有人正在争议的资料，等于以转移的方式了结争议，而不是解决它。", hi: "विवादित पहचान आगे नहीं सौंपी जा सकती: खुली आपत्ति इसे 409 से रोक देती है। जिस प्रोफ़ाइल पर कोई विवाद कर रहा हो उसे विरासत में लेना, विवाद को सुलझाने के बजाय हस्तांतरण से निपटा देना होगा।", ar: "الهوية المتنازع عليها لا تُورَّث: اعتراض مفتوح يمنع ذلك برمز 409. وراثة ملف يعترض عليه أحدهم تحسم النزاع بالنقل بدل أن تحلّه.",
  },
  "pas.taught": {
    en: "What it can be taught", es: "Lo que se le puede enseñar", fr: "Ce qu'on peut lui enseigner", de: "Was ihm beigebracht werden kann", pt: "O que lhe pode ser ensinado", it: "Cosa gli si può insegnare", ja: "何を教えられるか", zh: "它可以被教什么", hi: "इसे क्या सिखाया जा सकता है", ar: "ما يمكن تعليمه إياه",
  },
  "pas.taught.pitch": {
    en: "Publishing needs your owner token, and the account sales accrue to is read from it — not from the request. Naming somebody else's account in a body is how money ends up somewhere it was not earned.", es: "Publicar exige su token de propietario, y la cuenta a la que se acumulan las ventas se lee de él, no de la petición. Nombrar la cuenta de otro en un cuerpo es como el dinero acaba donde no se ganó.", fr: "Publier exige votre jeton de propriétaire, et le compte auquel les ventes sont créditées en est déduit — pas de la requête. Nommer le compte d'autrui dans un corps de requête, c'est ainsi que l'argent finit là où il n'a pas été gagné.", de: "Veröffentlichen erfordert Ihr Besitzer-Token, und das Konto, dem Verkäufe zufließen, wird daraus gelesen — nicht aus der Anfrage. Ein fremdes Konto im Body zu nennen ist der Weg, auf dem Geld dort landet, wo es nicht verdient wurde.", pt: "Publicar exige o seu token de proprietário, e a conta a que as vendas são creditadas é lida dele — não do pedido. Nomear a conta de outra pessoa num corpo é como o dinheiro acaba onde não foi ganho.", it: "Pubblicare richiede il tuo token da proprietario, e il conto su cui maturano le vendite si legge da lì — non dalla richiesta. Indicare il conto di qualcun altro nel corpo è il modo in cui il denaro finisce dove non è stato guadagnato.", ja: "公開にはあなたの所有者トークンが必要で、売上が入る口座はそこから読み取られます — リクエストからではありません。本文で他人の口座を指定できることこそ、稼いでいない場所へお金が流れる仕組みです。", zh: "发布需要你的所有者令牌，销售收入归属的账户从令牌中读取——而不是从请求里。在请求体中指定别人的账户，正是钱最终流向未曾赚取之处的方式。", hi: "प्रकाशन के लिए आपका स्वामी टोकन चाहिए, और बिक्री जिस खाते में जमा होगी वह उसी से पढ़ा जाता है — अनुरोध से नहीं। किसी और का खाता बॉडी में लिख देना ही वह तरीका है जिससे पैसा वहाँ पहुँचता है जहाँ वह कमाया नहीं गया।", ar: "النشر يتطلب رمز المالك الخاص بك، ويُقرأ منه الحساب الذي تُقيَّد فيه المبيعات — لا من الطلب. تسمية حساب شخص آخر في جسم الطلب هي الطريقة التي ينتهي بها المال في مكان لم يُكسَب فيه.",
  },
  "pas.industry.ph": {
    en: "industry", es: "sector", fr: "secteur", de: "Branche", pt: "setor", it: "settore", ja: "業種", zh: "行业", hi: "उद्योग", ar: "القطاع",
  },
  "pas.packtitle.ph": {
    en: "the pack's title", es: "el título del paquete", fr: "le titre du lot", de: "der Titel des Pakets", pt: "o título do pacote", it: "il titolo del pacchetto", ja: "パックの題名", zh: "知识包的标题", hi: "पैक का शीर्षक", ar: "عنوان الحزمة",
  },
  "pas.itemtitle.ph": {
    en: "one item's title", es: "el título de un elemento", fr: "le titre d'un élément", de: "der Titel eines Postens", pt: "o título de um item", it: "il titolo di una voce", ja: "項目一つの題名", zh: "某一条目的标题", hi: "किसी एक मद का शीर्षक", ar: "عنوان بند واحد",
  },
  "pas.itemwhat.ph": {
    en: "what it teaches", es: "qué enseña", fr: "ce qu'il enseigne", de: "was er lehrt", pt: "o que ensina", it: "cosa insegna", ja: "何を教えるか", zh: "它教什么", hi: "यह क्या सिखाता है", ar: "ما الذي يعلّمه",
  },
  "pas.publish": {
    en: "Publish it", es: "Publicarlo", fr: "Le publier", de: "Veröffentlichen", pt: "Publicá-lo", it: "Pubblicalo", ja: "公開する", zh: "发布", hi: "इसे प्रकाशित करें", ar: "انشره",
  },
  "pas.published.said": {
    en: "Published.", es: "Publicado.", fr: "Publié.", de: "Veröffentlicht.", pt: "Publicado.", it: "Pubblicato.", ja: "公開しました。", zh: "已发布。", hi: "प्रकाशित।", ar: "نُشر.",
  },
  "pas.packrules": {
    en: "A pack needs at least one item, a price cannot be negative, and every item in a robot pack needs a task — the command verb. Three refusals, each naming what is missing.", es: "Un paquete necesita al menos un elemento, un precio no puede ser negativo, y cada elemento de un paquete para robots necesita una tarea — el verbo de mando. Tres negativas, cada una nombrando lo que falta.", fr: "Un lot doit contenir au moins un élément, un prix ne peut être négatif, et chaque élément d'un lot pour robot doit avoir une tâche — le verbe de commande. Trois refus, chacun nommant ce qui manque.", de: "Ein Paket braucht mindestens einen Posten, ein Preis darf nicht negativ sein, und jeder Posten in einem Roboterpaket braucht eine Aufgabe — das Befehlsverb. Drei Ablehnungen, jede benennt, was fehlt.", pt: "Um pacote precisa de pelo menos um item, um preço não pode ser negativo, e cada item de um pacote para robôs precisa de uma tarefa — o verbo de comando. Três recusas, cada uma a nomear o que falta.", it: "Un pacchetto ha bisogno di almeno una voce, un prezzo non può essere negativo, e ogni voce in un pacchetto per robot ha bisogno di un compito — il verbo di comando. Tre rifiuti, ciascuno nomina cosa manca.", ja: "パックには少なくとも一項目が必要で、価格は負にできず、ロボット用パックの各項目にはタスク——命令の動詞——が必要です。三つの拒否があり、それぞれ何が足りないかを名指しします。", zh: "一个知识包至少要有一个条目，价格不能为负，而机器人知识包中的每个条目都需要一个任务——即指令动词。三种拒绝，各自点名缺的是什么。", hi: "एक पैक में कम से कम एक मद चाहिए, दाम ऋणात्मक नहीं हो सकता, और रोबोट पैक की हर मद को एक कार्य चाहिए — आदेश-क्रिया। तीन इनकार, हर एक बताता है कि क्या ग़ायब है।", ar: "الحزمة تحتاج بندًا واحدًا على الأقل، والسعر لا يكون سالبًا، وكل بند في حزمة روبوت يحتاج مهمة — فعل الأمر. ثلاثة أنواع رفض، كل منها يسمّي ما ينقص.",
  },
  "pas.pack.row": {
    en: "{title} — {n} item{s} · {price} · published by {who}", es: "{title} — {n} elementos · {price} · publicado por {who}", fr: "{title} — {n} éléments · {price} · publié par {who}", de: "{title} — {n} Posten · {price} · veröffentlicht von {who}", pt: "{title} — {n} itens · {price} · publicado por {who}", it: "{title} — {n} voci · {price} · pubblicato da {who}", ja: "{title} — {n}件 · {price} · 公開者 {who}", zh: "{title} — {n} 项 · {price} · 由 {who} 发布", hi: "{title} — {n} मदें · {price} · {who} द्वारा प्रकाशित", ar: "{title} — {n} بنود · {price} · نشره {who}",
  },
  "pas.free": {
    en: "free", es: "gratis", fr: "gratuit", de: "kostenlos", pt: "grátis", it: "gratis", ja: "無料", zh: "免费", hi: "निःशुल्क", ar: "مجاني",
  },
  "pas.seed": {
    en: "seed the starter packs", es: "sembrar los paquetes iniciales", fr: "semer les lots de départ", de: "die Startpakete anlegen", pt: "semear os pacotes iniciais", it: "semina i pacchetti iniziali", ja: "入門パックを投入する", zh: "导入入门知识包", hi: "शुरुआती पैक बोएँ", ar: "ازرع الحزم الابتدائية",
  },
  "pas.seeded": {
    en: "{created} created, {skipped} already there, across {n} industries. Pressing again is safe.", es: "{created} creados, {skipped} ya estaban, en {n} sectores. Volver a pulsar es seguro.", fr: "{created} créés, {skipped} déjà présents, sur {n} secteurs. Appuyer de nouveau est sans risque.", de: "{created} angelegt, {skipped} bereits vorhanden, über {n} Branchen. Nochmal drücken ist unbedenklich.", pt: "{created} criados, {skipped} já lá estavam, em {n} setores. Voltar a carregar é seguro.", it: "{created} creati, {skipped} già presenti, su {n} settori. Premere di nuovo è sicuro.", ja: "{created}件を作成、{skipped}件はすでに存在、{n}業種にわたって。もう一度押しても安全です。", zh: "创建 {created} 个，已存在 {skipped} 个，覆盖 {n} 个行业。再按一次是安全的。", hi: "{created} बनाए गए, {skipped} पहले से मौजूद, {n} उद्योगों में। दोबारा दबाना सुरक्षित है।", ar: "أُنشئ {created}، و{skipped} موجودة أصلًا، عبر {n} قطاعات. الضغط مجددًا آمن.",
  },
  "pas.wrist": {
    en: "One press from the wrist", es: "Una pulsación desde la muñeca", fr: "Une pression depuis le poignet", de: "Ein Druck vom Handgelenk", pt: "Um toque a partir do pulso", it: "Una pressione dal polso", ja: "手首からの一押し", zh: "来自腕上的一次按压", hi: "कलाई से एक दबाव", ar: "ضغطة واحدة من المعصم",
  },
  "pas.wrist.pitch": {
    en: "Down the same paths the full apps use — same auth, same allowlists, same moderation. A shortcut that skipped any of those would be a second, weaker way in, which is exactly what a wrist should not be.", es: "Por los mismos caminos que usan las apps completas — misma autenticación, mismas listas de permitidos, misma moderación. Un atajo que se saltara alguno sería una segunda vía de entrada, más débil, que es justo lo que una muñeca no debe ser.", fr: "Par les mêmes chemins que les applications complètes — même authentification, mêmes listes d'autorisation, même modération. Un raccourci qui en sauterait un serait une deuxième voie d'accès, plus faible, ce qu'un poignet ne doit surtout pas être.", de: "Über dieselben Wege, die die vollen Apps nutzen — dieselbe Authentifizierung, dieselben Freigabelisten, dieselbe Moderation. Eine Abkürzung, die eines davon überspränge, wäre ein zweiter, schwächerer Zugang — genau das, was ein Handgelenk nicht sein darf.", pt: "Pelos mesmos caminhos que as apps completas usam — mesma autenticação, mesmas listas de permissões, mesma moderação. Um atalho que saltasse algum deles seria uma segunda via de entrada, mais fraca, que é exatamente o que um pulso não deve ser.", it: "Per le stesse strade che usano le app complete — stessa autenticazione, stesse liste di permessi, stessa moderazione. Una scorciatoia che ne saltasse una sarebbe una seconda via d'ingresso, più debole, che è esattamente ciò che un polso non deve essere.", ja: "フル機能のアプリと同じ経路を通ります — 同じ認証、同じ許可リスト、同じ審査。そのどれかを飛ばす近道は、二つ目の、より弱い入口になってしまいます。手首がそうであってはならないのは、まさにその点です。", zh: "走的是完整应用所走的同一条路——同样的认证、同样的白名单、同样的审核。任何跳过其中一项的捷径，都会成为第二条更薄弱的入口，而这恰恰是腕上设备最不该成为的东西。", hi: "उन्हीं रास्तों से जिनसे पूरे ऐप्स गुज़रते हैं — वही प्रमाणीकरण, वही अनुमति-सूचियाँ, वही मॉडरेशन। इनमें से किसी को छोड़ देने वाला शॉर्टकट भीतर आने का दूसरा, कमज़ोर रास्ता बन जाता — और कलाई को यही नहीं होना चाहिए।", ar: "عبر المسارات نفسها التي تسلكها التطبيقات الكاملة — التوثيق نفسه، وقوائم السماح نفسها، والمراجعة نفسها. أي اختصار يتخطى واحدًا منها سيكون مدخلًا ثانيًا أضعف، وهذا بالضبط ما لا ينبغي أن يكونه المعصم.",
  },
  "pas.id.ph": {
    en: "its id", es: "su id", fr: "son id", de: "seine ID", pt: "o seu id", it: "il suo id", ja: "その ID", zh: "它的 ID", hi: "इसकी आईडी", ar: "معرّفه",
  },
  "pas.action.ph": {
    en: "advance / assist / cancel", es: "avanzar / asistir / cancelar", fr: "avancer / assister / annuler", de: "weiter / helfen / abbrechen", pt: "avançar / assistir / cancelar", it: "avanza / assisti / annulla", ja: "advance / assist / cancel", zh: "advance / assist / cancel", hi: "advance / assist / cancel", ar: "advance / assist / cancel",
  },
  "pas.input.ph": {
    en: "what it asked for", es: "lo que pidió", fr: "ce qu'il a demandé", de: "worum es gebeten hat", pt: "o que pediu", it: "cosa ha chiesto", ja: "求められた内容", zh: "它所要求的内容", hi: "इसने क्या माँगा", ar: "ما طلبه",
  },
  "pas.press": {
    en: "Press it", es: "Pulsar", fr: "Appuyer", de: "Drücken", pt: "Carregar", it: "Premi", ja: "押す", zh: "按下", hi: "दबाएँ", ar: "اضغط",
  },
  "pas.done.said": {
    en: "Done.", es: "Hecho.", fr: "Fait.", de: "Erledigt.", pt: "Feito.", it: "Fatto.", ja: "完了しました。", zh: "完成。", hi: "हो गया।", ar: "تمّ.",
  },
  "pas.assist": {
    en: "assist", es: "asistir", fr: "assister", de: "helfen", pt: "assistir", it: "assisti", ja: "assist", zh: "assist", hi: "assist", ar: "assist",
  },
  "pas.assist.note": {
    en: "{assist} needs input — the paused phase asked for something, and sending nothing would advance past the question rather than answer it.", es: "{assist} necesita una entrada — la fase en pausa pidió algo, y no enviar nada avanzaría más allá de la pregunta en vez de responderla.", fr: "{assist} exige une saisie — la phase en pause a demandé quelque chose, et n'envoyer rien avancerait au-delà de la question au lieu d'y répondre.", de: "{assist} braucht eine Eingabe — die pausierte Phase hat um etwas gebeten, und nichts zu senden würde an der Frage vorbei weitergehen, statt sie zu beantworten.", pt: "{assist} precisa de uma entrada — a fase em pausa pediu algo, e não enviar nada avançaria para além da pergunta em vez de a responder.", it: "{assist} richiede un input — la fase in pausa ha chiesto qualcosa, e non inviare nulla andrebbe oltre la domanda invece di rispondere.", ja: "{assist} には入力が必要です — 停止中の段階が何かを求めており、何も送らなければ問いに答えるのではなく問いを飛び越えてしまいます。", zh: "{assist} 需要输入——暂停的阶段提出了要求，什么都不发就会越过这个问题，而不是回答它。", hi: "{assist} को इनपुट चाहिए — रुके हुए चरण ने कुछ माँगा है, और कुछ न भेजना सवाल का उत्तर देने के बजाय उसे लाँघ जाना होगा।", ar: "{assist} يحتاج مُدخلًا — الطور المتوقف طلب شيئًا، وإرسال لا شيء يتجاوز السؤال بدل أن يجيبه.",
  },
  "sgn.title": {
    en: "Signing", es: "Firma", fr: "Signature", de: "Signieren", pt: "Assinatura", it: "Firma", ja: "署名", zh: "签署", hi: "हस्ताक्षर", ar: "التوقيع",
  },
  "sgn.noaccount": {
    en: "Signing is done as an account, not as a profile page. Sign in as an owner to enrol a credential.", es: "Se firma como cuenta, no como página de perfil. Inicie sesión como propietario para registrar una credencial.", fr: "On signe en tant que compte, pas en tant que page de profil. Connectez-vous comme propriétaire pour enregistrer un justificatif.", de: "Signiert wird als Konto, nicht als Profilseite. Melden Sie sich als Besitzer an, um einen Nachweis zu registrieren.", pt: "Assina-se como conta, não como página de perfil. Entre como proprietário para registar uma credencial.", it: "Si firma come account, non come pagina di profilo. Accedi come proprietario per registrare una credenziale.", ja: "署名はアカウントとして行うもので、プロフィールのページとしてではありません。資格情報を登録するには所有者としてサインインしてください。", zh: "签署是以账户身份进行的，而不是以资料页面的身份。请以所有者身份登录以注册凭据。", hi: "हस्ताक्षर खाते के रूप में होता है, प्रोफ़ाइल पृष्ठ के रूप में नहीं। क्रेडेंशियल दर्ज करने के लिए स्वामी के रूप में साइन इन करें।", ar: "التوقيع يتم بصفة حساب لا بصفة صفحة ملف. سجّل الدخول بصفتك مالكًا لتسجيل اعتماد.",
  },
  "sgn.lead": {
    en: "A signature here is a device credential used with user verification over one exact document. What that does and does not prove is written below, in the words a counterparty will read.", es: "Una firma aquí es una credencial de dispositivo usada con verificación de usuario sobre un documento exacto. Lo que eso prueba y lo que no está escrito abajo, con las palabras que leerá la contraparte.", fr: "Une signature ici est un justificatif d'appareil utilisé avec vérification de l'utilisateur sur un document exact. Ce que cela prouve et ne prouve pas est écrit plus bas, dans les mots que lira la contrepartie.", de: "Eine Unterschrift ist hier ein Gerätenachweis, mit Nutzerverifikation über genau ein Dokument verwendet. Was das beweist und was nicht, steht unten — in den Worten, die eine Gegenpartei lesen wird.", pt: "Uma assinatura aqui é uma credencial de dispositivo usada com verificação do utilizador sobre um documento exato. O que isso prova e o que não prova está escrito abaixo, nas palavras que a contraparte vai ler.", it: "Una firma qui è una credenziale del dispositivo usata con verifica dell'utente su un documento esatto. Cosa dimostra e cosa no è scritto sotto, nelle parole che leggerà la controparte.", ja: "ここでの署名とは、利用者確認を伴って、ただ一つの文書に対して使われる端末の資格情報です。それが何を証明し、何を証明しないかは下に、相手方が読む言葉で書いてあります。", zh: "此处的签名，是在用户验证下针对某一份确切文件所使用的设备凭据。它能证明什么、不能证明什么，写在下方——用对方将会读到的措辞。", hi: "यहाँ हस्ताक्षर का अर्थ है एक डिवाइस क्रेडेंशियल, जो उपयोगकर्ता-सत्यापन के साथ ठीक एक दस्तावेज़ पर प्रयुक्त होता है। वह क्या सिद्ध करता है और क्या नहीं, नीचे लिखा है — उन्हीं शब्दों में जो सामने वाला पक्ष पढ़ेगा।", ar: "التوقيع هنا هو اعتماد جهاز يُستخدم مع تحقّق من المستخدم على وثيقة واحدة بعينها. ما يثبته وما لا يثبته مكتوب أدناه، بالألفاظ التي سيقرؤها الطرف المقابل.",
  },
  "sgn.enrol": {
    en: "Enrol a credential", es: "Registrar una credencial", fr: "Enregistrer un justificatif", de: "Einen Nachweis registrieren", pt: "Registar uma credencial", it: "Registra una credenziale", ja: "資格情報を登録する", zh: "注册一个凭据", hi: "क्रेडेंशियल दर्ज करें", ar: "سجّل اعتمادًا",
  },
  "sgn.enrol.pitch": {
    en: "The ceremony opens in its own window, on the API's own origin — WebAuthn refuses a credential whose relying party does not match, and this app's origin is not one it can match. That window carries no token; it hands the registration back here, and this screen makes the call.", es: "La ceremonia se abre en su propia ventana, en el origen de la propia API — WebAuthn rechaza una credencial cuya parte confiante no coincide, y el origen de esta app no es uno con el que pueda coincidir. Esa ventana no lleva token; devuelve el registro aquí, y es esta pantalla la que hace la llamada.", fr: "La cérémonie s'ouvre dans sa propre fenêtre, sur l'origine de l'API — WebAuthn refuse un justificatif dont la partie utilisatrice ne correspond pas, et l'origine de cette application n'en est pas une qu'il puisse faire correspondre. Cette fenêtre ne porte aucun jeton ; elle rend l'enregistrement ici, et c'est cet écran qui fait l'appel.", de: "Die Zeremonie öffnet sich in einem eigenen Fenster, auf der Origin der API — WebAuthn weist einen Nachweis zurück, dessen Relying Party nicht passt, und die Origin dieser App ist keine, die passen kann. Jenes Fenster trägt kein Token; es reicht die Registrierung hierher zurück, und dieser Bildschirm macht den Aufruf.", pt: "A cerimónia abre na sua própria janela, na origem da própria API — o WebAuthn recusa uma credencial cuja parte confiante não corresponde, e a origem desta app não é uma com que possa corresponder. Essa janela não leva token; devolve o registo para aqui, e é este ecrã que faz a chamada.", it: "La cerimonia si apre in una finestra propria, sull'origin dell'API — WebAuthn rifiuta una credenziale la cui relying party non corrisponde, e l'origin di questa app non è una che possa corrispondere. Quella finestra non porta token; restituisce la registrazione qui, ed è questa schermata a fare la chiamata.", ja: "この儀式は API 自身のオリジン上で、別のウィンドウとして開きます — WebAuthn は依拠当事者が一致しない資格情報を拒否し、このアプリのオリジンは一致し得ないからです。そのウィンドウはトークンを持たず、登録結果をここに返し、呼び出しはこの画面が行います。", zh: "该仪式在自己的窗口中打开，位于 API 自身的源上——WebAuthn 会拒绝依赖方不匹配的凭据，而本应用的源无法与之匹配。那个窗口不携带任何令牌；它把注册结果交回这里，由本页面发起调用。", hi: "यह प्रक्रिया अपनी अलग विंडो में, API के अपने ऑरिजिन पर खुलती है — WebAuthn ऐसे क्रेडेंशियल को अस्वीकार करता है जिसका रिलाइंग पार्टी मेल न खाए, और इस ऐप का ऑरिजिन मेल खा ही नहीं सकता। वह विंडो कोई टोकन नहीं ले जाती; वह पंजीकरण यहाँ लौटा देती है, और कॉल यही स्क्रीन करती है।", ar: "تُفتح المراسم في نافذتها الخاصة، على أصل واجهة البرمجة نفسها — إذ يرفض WebAuthn اعتمادًا لا يطابق الطرف المعتمِد، وأصل هذا التطبيق ليس مما يمكن أن يطابقه. تلك النافذة لا تحمل رمزًا؛ بل تعيد التسجيل إلى هنا، وهذه الشاشة هي التي تُجري النداء.",
  },
  "sgn.device.ph": {
    en: "what to call this device", es: "cómo llamar a este dispositivo", fr: "comment appeler cet appareil", de: "wie dieses Gerät heißen soll", pt: "como chamar este dispositivo", it: "come chiamare questo dispositivo", ja: "この端末の呼び名", zh: "如何称呼这台设备", hi: "इस डिवाइस को क्या कहें", ar: "بمَ تسمّي هذا الجهاز",
  },
  "sgn.thisdevice": {
    en: "This device", es: "Este dispositivo", fr: "Cet appareil", de: "Dieses Gerät", pt: "Este dispositivo", it: "Questo dispositivo", ja: "この端末", zh: "这台设备", hi: "यह डिवाइस", ar: "هذا الجهاز",
  },
  "sgn.checked": {
    en: "How your identity was checked", es: "Cómo se comprobó su identidad", fr: "Comment votre identité a été vérifiée", de: "Wie Ihre Identität geprüft wurde", pt: "Como a sua identidade foi verificada", it: "Come è stata verificata la tua identità", ja: "本人確認の方法", zh: "你的身份是如何被核验的", hi: "आपकी पहचान कैसे जाँची गई", ar: "كيف جرى التحقق من هويتك",
  },
  "sgn.attestor.ph": {
    en: "who checked it (required above self-asserted)", es: "quién lo comprobó (obligatorio por encima de autodeclarado)", fr: "qui l'a vérifié (obligatoire au-dessus d'auto-déclaré)", de: "wer es geprüft hat (oberhalb von selbsterklärt erforderlich)", pt: "quem verificou (obrigatório acima de autodeclarado)", it: "chi l'ha verificato (obbligatorio sopra l'autodichiarato)", ja: "誰が確認したか（自己申告より上の水準では必須）", zh: "由谁核验（高于自述级别时必填）", hi: "किसने जाँचा (स्व-घोषित से ऊपर आवश्यक)", ar: "من تحقّق منه (مطلوب فوق مستوى الإقرار الذاتي)",
  },
  "sgn.and": {
    en: "and", es: "y", fr: "et", de: "und", pt: "e", it: "e", ja: "かつ", zh: "并且", hi: "और", ar: "و",
  },
  "sgn.tierpitch": {
    en: "This fixes what the credential may sign. A self-asserted one signs the basic tier only; the high tier wants a document check {and} a key that stayed on one device.", es: "Esto fija qué puede firmar la credencial. Una autodeclarada firma solo el nivel básico; el nivel alto quiere una comprobación documental {and} una clave que se quedó en un único dispositivo.", fr: "Ceci fixe ce que le justificatif peut signer. Un justificatif auto-déclaré ne signe que le niveau de base ; le niveau élevé veut une vérification de document {and} une clé restée sur un seul appareil.", de: "Das legt fest, was der Nachweis signieren darf. Ein selbsterklärter signiert nur die Basisstufe; die hohe Stufe will eine Dokumentenprüfung {and} einen Schlüssel, der auf einem Gerät geblieben ist.", pt: "Isto fixa o que a credencial pode assinar. Uma autodeclarada assina apenas o nível básico; o nível alto quer uma verificação documental {and} uma chave que ficou num só dispositivo.", it: "Questo fissa cosa la credenziale può firmare. Una autodichiarata firma solo il livello base; il livello alto vuole una verifica documentale {and} una chiave rimasta su un solo dispositivo.", ja: "これは、その資格情報が何に署名してよいかを定めます。自己申告のものは基本の段階にのみ署名できます。高い段階は、書類による確認、{and}一台の端末から出なかった鍵を求めます。", zh: "这决定了该凭据可以签署什么。自述级别的凭据只能签署基础层级；高层级要求证件核验，{and}要求密钥始终留在一台设备上。", hi: "यह तय करता है कि क्रेडेंशियल क्या हस्ताक्षरित कर सकता है। स्व-घोषित केवल मूल स्तर पर हस्ताक्षर करता है; उच्च स्तर दस्तावेज़ जाँच {and} ऐसी कुंजी चाहता है जो एक ही डिवाइस पर बनी रही हो।", ar: "هذا يحدد ما يجوز للاعتماد توقيعه. الاعتماد المُقَرّ ذاتيًا يوقّع المستوى الأساسي فقط؛ أما المستوى العالي فيريد تحققًا من وثيقة {and} مفتاحًا لم يغادر جهازًا واحدًا.",
  },
  "sgn.open": {
    en: "Open the ceremony", es: "Abrir la ceremonia", fr: "Ouvrir la cérémonie", de: "Die Zeremonie öffnen", pt: "Abrir a cerimónia", it: "Apri la cerimonia", ja: "儀式を開く", zh: "打开签署仪式", hi: "प्रक्रिया खोलें", ar: "افتح المراسم",
  },
  "sgn.waiting": {
    en: "Waiting for the ceremony window.", es: "Esperando a la ventana de la ceremonia.", fr: "En attente de la fenêtre de cérémonie.", de: "Warten auf das Zeremonie-Fenster.", pt: "À espera da janela da cerimónia.", it: "In attesa della finestra della cerimonia.", ja: "儀式のウィンドウを待っています。", zh: "正在等待签署仪式窗口。", hi: "प्रक्रिया विंडो की प्रतीक्षा।", ar: "في انتظار نافذة المراسم.",
  },
  "sgn.blocked": {
    en: "the ceremony window was blocked", es: "la ventana de la ceremonia fue bloqueada", fr: "la fenêtre de cérémonie a été bloquée", de: "das Zeremonie-Fenster wurde blockiert", pt: "a janela da cerimónia foi bloqueada", it: "la finestra della cerimonia è stata bloccata", ja: "儀式のウィンドウがブロックされました", zh: "签署仪式窗口被拦截", hi: "प्रक्रिया विंडो अवरुद्ध कर दी गई", ar: "حُجبت نافذة المراسم",
  },
  "sgn.incomplete": {
    en: "the ceremony did not complete", es: "la ceremonia no se completó", fr: "la cérémonie ne s'est pas achevée", de: "die Zeremonie wurde nicht abgeschlossen", pt: "a cerimónia não se concluiu", it: "la cerimonia non si è conclusa", ja: "儀式が完了しませんでした", zh: "签署仪式未能完成", hi: "प्रक्रिया पूरी नहीं हुई", ar: "لم تكتمل المراسم",
  },
  "sgn.enrolled.said": {
    en: "Enrolled — this credential can sign {what}.", es: "Registrada — esta credencial puede firmar {what}.", fr: "Enregistré — ce justificatif peut signer {what}.", de: "Registriert — dieser Nachweis kann {what} signieren.", pt: "Registada — esta credencial pode assinar {what}.", it: "Registrata — questa credenziale può firmare {what}.", ja: "登録しました — この資格情報は {what} に署名できます。", zh: "已注册 — 该凭据可以签署 {what}。", hi: "दर्ज हुआ — यह क्रेडेंशियल {what} पर हस्ताक्षर कर सकता है।", ar: "سُجّل — هذا الاعتماد يمكنه توقيع {what}.",
  },
  "sgn.nothingyet": {
    en: "nothing yet", es: "nada todavía", fr: "rien pour l'instant", de: "noch nichts", pt: "nada ainda", it: "niente ancora", ja: "まだ何も", zh: "暂时什么都不能", hi: "अभी कुछ नहीं", ar: "لا شيء بعد",
  },
  "sgn.have": {
    en: "What this account can sign with", es: "Con qué puede firmar esta cuenta", fr: "Ce avec quoi ce compte peut signer", de: "Womit dieses Konto signieren kann", pt: "Com que é que esta conta pode assinar", it: "Con cosa può firmare questo account", ja: "このアカウントが署名に使えるもの", zh: "本账户可以用什么来签署", hi: "यह खाता किससे हस्ताक्षर कर सकता है", ar: "بماذا يستطيع هذا الحساب التوقيع",
  },
  "sgn.none": {
    en: "Nothing enrolled yet.", es: "Nada registrado todavía.", fr: "Rien d'enregistré pour l'instant.", de: "Noch nichts registriert.", pt: "Nada registado ainda.", it: "Ancora niente di registrato.", ja: "まだ何も登録されていません。", zh: "尚未注册任何凭据。", hi: "अभी कुछ दर्ज नहीं।", ar: "لم يُسجَّل شيء بعد.",
  },
  "sgn.cred.line": {
    en: "{name} — checked as {level}", es: "{name} — comprobada como {level}", fr: "{name} — vérifié comme {level}", de: "{name} — geprüft als {level}", pt: "{name} — verificada como {level}", it: "{name} — verificata come {level}", ja: "{name} — 確認水準 {level}", zh: "{name} — 核验为 {level}", hi: "{name} — {level} के रूप में जाँचा गया", ar: "{name} — تم التحقق بوصفه {level}",
  },
  "sgn.syncs": {
    en: "· syncs between devices", es: "· se sincroniza entre dispositivos", fr: "· se synchronise entre appareils", de: "· synchronisiert zwischen Geräten", pt: "· sincroniza entre dispositivos", it: "· si sincronizza tra dispositivi", ja: "· 端末間で同期される", zh: "· 会在设备间同步", hi: "· उपकरणों के बीच सिंक होता है", ar: "· يتزامن بين الأجهزة",
  },
  "sgn.revoked": {
    en: "· revoked", es: "· revocada", fr: "· révoqué", de: "· widerrufen", pt: "· revogada", it: "· revocata", ja: "· 失効済み", zh: "· 已撤销", hi: "· निरस्त", ar: "· مُبطَل",
  },
  "sgn.signs": {
    en: "Signs: {what}", es: "Firma: {what}", fr: "Signe : {what}", de: "Signiert: {what}", pt: "Assina: {what}", it: "Firma: {what}", ja: "署名可能: {what}", zh: "可签署：{what}", hi: "हस्ताक्षर करता है: {what}", ar: "يوقّع: {what}",
  },
  "sgn.signsnothing": {
    en: "Signs nothing — revoked, or not proofed to any tier", es: "No firma nada — revocada, o sin comprobación para ningún nivel", fr: "Ne signe rien — révoqué, ou non vérifié pour aucun niveau", de: "Signiert nichts — widerrufen oder für keine Stufe geprüft", pt: "Não assina nada — revogada, ou sem verificação para qualquer nível", it: "Non firma nulla — revocata, o non verificata per alcun livello", ja: "何にも署名できません — 失効済みか、どの段階の確認も受けていません", zh: "什么都不能签署——已撤销，或未通过任何层级的核验", hi: "कुछ भी हस्ताक्षरित नहीं करता — निरस्त, या किसी स्तर के लिए प्रमाणित नहीं", ar: "لا يوقّع شيئًا — مُبطَل، أو غير مُتحقَّق لأي مستوى",
  },
  "sgn.revoke": {
    en: "Revoke", es: "Revocar", fr: "Révoquer", de: "Widerrufen", pt: "Revogar", it: "Revoca", ja: "失効させる", zh: "撤销", hi: "निरस्त करें", ar: "أبطِل",
  },
  "sgn.revoked.said": {
    en: "Revoked, going forward. Anything already signed with it stays verifiable — its public key is in the evidence, not here.", es: "Revocada de aquí en adelante. Todo lo ya firmado con ella sigue siendo verificable — su clave pública está en la evidencia, no aquí.", fr: "Révoqué pour la suite. Tout ce qui a déjà été signé avec reste vérifiable — sa clé publique est dans la preuve, pas ici.", de: "Ab jetzt widerrufen. Alles, was damit bereits signiert wurde, bleibt überprüfbar — sein öffentlicher Schlüssel steckt im Beweis, nicht hier.", pt: "Revogada daqui para a frente. Tudo o que já foi assinado com ela continua verificável — a sua chave pública está na evidência, não aqui.", it: "Revocata d'ora in poi. Tutto ciò che è già stato firmato con essa resta verificabile — la sua chiave pubblica è nella prova, non qui.", ja: "以後は失効します。それですでに署名されたものは検証可能なままです — その公開鍵は証拠の中にあり、ここにあるのではありません。", zh: "自此撤销。已用它签署过的内容仍可验证——其公钥在证据里，而不在这里。", hi: "आगे के लिए निरस्त। इससे पहले हस्ताक्षरित हर चीज़ सत्यापन-योग्य बनी रहती है — उसकी सार्वजनिक कुंजी साक्ष्य में है, यहाँ नहीं।", ar: "أُبطِل من الآن فصاعدًا. كل ما وُقّع به سابقًا يبقى قابلًا للتحقق — مفتاحه العام في الدليل، لا هنا.",
  },
  "sgn.sign": {
    en: "Sign a document", es: "Firmar un documento", fr: "Signer un document", de: "Ein Dokument signieren", pt: "Assinar um documento", it: "Firma un documento", ja: "文書に署名する", zh: "签署一份文件", hi: "किसी दस्तावेज़ पर हस्ताक्षर करें", ar: "وقّع وثيقة",
  },
  "sgn.doc.ph": {
    en: "the exact text being signed", es: "el texto exacto que se firma", fr: "le texte exact qui est signé", de: "der genaue Text, der signiert wird", pt: "o texto exato que está a ser assinado", it: "il testo esatto che viene firmato", ja: "署名される正確な本文", zh: "被签署的确切文本", hi: "जिस पर हस्ताक्षर हो रहा है, वही ठीक पाठ", ar: "النص الدقيق الذي يجري توقيعه",
  },
  "sgn.meaning.ph": {
    en: "what signing it means", es: "qué significa firmarlo", fr: "ce que le fait de signer signifie", de: "was das Signieren bedeutet", pt: "o que significa assiná-lo", it: "cosa significa firmarlo", ja: "署名することの意味", zh: "签署它意味着什么", hi: "इस पर हस्ताक्षर का अर्थ क्या है", ar: "ماذا يعني توقيعها",
  },
  "sgn.display.ph": {
    en: "what you will be shown when you sign", es: "lo que se le mostrará al firmar", fr: "ce qui vous sera montré au moment de signer", de: "was Ihnen beim Signieren gezeigt wird", pt: "o que lhe será mostrado ao assinar", it: "cosa ti verrà mostrato quando firmi", ja: "署名時に表示される内容", zh: "签署时会向你展示的内容", hi: "हस्ताक्षर के समय आपको क्या दिखाया जाएगा", ar: "ما سيُعرض عليك عند التوقيع",
  },
  "sgn.is": {
    en: "is", es: "es", fr: "est", de: "ist", pt: "é", it: "è", ja: "こそが", zh: "就是", hi: "ही है", ar: "هو",
  },
  "sgn.challenge": {
    en: "The challenge {is} the hash of this document, so the signature covers these bytes and no others. Edit the text afterwards and the old signature will not carry — which is the point of it.", es: "El reto {is} el hash de este documento, así que la firma cubre estos bytes y ningunos otros. Edite el texto después y la firma antigua no valdrá — que es justo el sentido de todo esto.", fr: "Le défi {is} le condensat de ce document, si bien que la signature couvre ces octets et aucun autre. Modifiez le texte ensuite et l'ancienne signature ne suivra pas — c'est tout l'intérêt.", de: "Die Challenge {is} der Hash dieses Dokuments, also deckt die Signatur genau diese Bytes ab und keine anderen. Ändern Sie den Text danach, und die alte Signatur trägt nicht mehr — genau darum geht es.", pt: "O desafio {is} o hash deste documento, por isso a assinatura cobre estes bytes e mais nenhuns. Edite o texto depois e a assinatura antiga não acompanha — que é precisamente o objetivo.", it: "La sfida {is} l'hash di questo documento, quindi la firma copre questi byte e nessun altro. Modifica il testo dopo e la vecchia firma non regge — che è proprio il punto.", ja: "チャレンジ{is}この文書のハッシュです。ですから署名はこのバイト列だけを覆い、ほかは覆いません。あとから本文を編集すれば古い署名は通用しなくなります — それこそがこの仕組みの狙いです。", zh: "挑战值{is}这份文件的哈希，所以签名覆盖的正是这些字节，别无其他。事后修改文本，旧签名便不再成立——而这正是它的意义所在。", hi: "चैलेंज {is} इस दस्तावेज़ का हैश, इसलिए हस्ताक्षर ठीक इन्हीं बाइट्स को ढकता है, किन्हीं और को नहीं। बाद में पाठ बदलिए और पुराना हस्ताक्षर नहीं चलेगा — और यही इसका मक़सद है।", ar: "التحدي {is} بصمة هذه الوثيقة، فيغطي التوقيع هذه البايتات دون سواها. عدّل النص بعد ذلك ولن يصمد التوقيع القديم — وهذا هو المقصود منه.",
  },
  "sgn.mint": {
    en: "Mint an envelope and sign it", es: "Emitir un sobre y firmarlo", fr: "Créer une enveloppe et la signer", de: "Einen Umschlag erzeugen und signieren", pt: "Emitir um envelope e assiná-lo", it: "Conia una busta e firmala", ja: "封筒を発行して署名する", zh: "铸造一个信封并签署它", hi: "एक लिफ़ाफ़ा बनाकर हस्ताक्षर करें", ar: "أنشئ ظرفًا ووقّعه",
  },
  "sgn.envelope": {
    en: "Envelope {id}, good until {when}. Finish in the ceremony window.", es: "Sobre {id}, válido hasta {when}. Termine en la ventana de la ceremonia.", fr: "Enveloppe {id}, valable jusqu'à {when}. Terminez dans la fenêtre de cérémonie.", de: "Umschlag {id}, gültig bis {when}. Schließen Sie im Zeremonie-Fenster ab.", pt: "Envelope {id}, válido até {when}. Termine na janela da cerimónia.", it: "Busta {id}, valida fino a {when}. Concludi nella finestra della cerimonia.", ja: "封筒 {id}、{when} まで有効。儀式のウィンドウで完了してください。", zh: "信封 {id}，有效期至 {when}。请在签署仪式窗口中完成。", hi: "लिफ़ाफ़ा {id}, {when} तक वैध। प्रक्रिया विंडो में पूरा करें।", ar: "الظرف {id}، صالح حتى {when}. أكمِل في نافذة المراسم.",
  },
  "sgn.signedas": {
    en: "Signed as {name}, proofed {level} — {tier} tier.", es: "Firmado como {name}, comprobado {level} — nivel {tier}.", fr: "Signé en tant que {name}, vérifié {level} — niveau {tier}.", de: "Signiert als {name}, geprüft {level} — Stufe {tier}.", pt: "Assinado como {name}, verificado {level} — nível {tier}.", it: "Firmato come {name}, verificato {level} — livello {tier}.", ja: "{name} として署名、確認水準 {level} — {tier} 段階。", zh: "以 {name} 身份签署，核验级别 {level} — {tier} 层级。", hi: "{name} के रूप में हस्ताक्षरित, {level} स्तर पर प्रमाणित — {tier} श्रेणी।", ar: "وُقّع باسم {name}، بمستوى تحقّق {level} — الفئة {tier}.",
  },
  "sgn.sigline": {
    en: "Signature {id}. Over “{text}”, meaning “{meaning}”.", es: "Firma {id}. Sobre «{text}», con el significado «{meaning}».", fr: "Signature {id}. Sur « {text} », signifiant « {meaning} ».", de: "Signatur {id}. Über „{text}“, mit der Bedeutung „{meaning}“.", pt: "Assinatura {id}. Sobre «{text}», significando «{meaning}».", it: "Firma {id}. Su «{text}», con significato «{meaning}».", ja: "署名 {id}。「{text}」に対して、意味は「{meaning}」。", zh: "签名 {id}。针对“{text}”，含义为“{meaning}”。", hi: "हस्ताक्षर {id}। “{text}” पर, अर्थ “{meaning}”।", ar: "التوقيع {id}. على «{text}»، بمعنى «{meaning}».",
  },
  "sgn.check": {
    en: "Check a package somebody handed you", es: "Comprobar un paquete que le han entregado", fr: "Vérifier un paquet qu'on vous a remis", de: "Ein Paket prüfen, das Ihnen jemand gegeben hat", pt: "Verificar um pacote que lhe entregaram", it: "Verifica un pacchetto che ti hanno consegnato", ja: "誰かから渡された証拠一式を確認する", zh: "核验别人交给你的证据包", hi: "किसी के दिए गए पैकेज को जाँचें", ar: "افحص حزمة سلّمها إليك أحدهم",
  },
  "sgn.check.pitch": {
    en: "This asks nothing of us. The package carries its own public key and its own hashes, and the arithmetic either holds or it does not — a check that needed our blessing would be us vouching, which is the opposite of what the evidence is for.", es: "Esto no nos pide nada. El paquete lleva su propia clave pública y sus propios hashes, y la aritmética se sostiene o no — una comprobación que necesitara nuestra bendición sería nosotros avalando, que es lo contrario de para lo que sirve la evidencia.", fr: "Ceci ne nous demande rien. Le paquet porte sa propre clé publique et ses propres condensats, et l'arithmétique tient ou ne tient pas — une vérification qui aurait besoin de notre bénédiction reviendrait à ce que nous nous portions garants, soit l'inverse de ce à quoi sert la preuve.", de: "Das verlangt nichts von uns. Das Paket trägt seinen eigenen öffentlichen Schlüssel und seine eigenen Hashes, und die Arithmetik hält oder hält nicht — eine Prüfung, die unseren Segen bräuchte, wäre unser Bürgen, und das ist das Gegenteil dessen, wozu der Beweis da ist.", pt: "Isto não nos pede nada. O pacote leva a sua própria chave pública e os seus próprios hashes, e a aritmética ou se aguenta ou não — uma verificação que precisasse da nossa bênção seria nós a abonarmos, que é o contrário daquilo para que a evidência serve.", it: "Questo non chiede nulla a noi. Il pacchetto porta la propria chiave pubblica e i propri hash, e l'aritmetica regge o non regge — una verifica che avesse bisogno della nostra benedizione sarebbe noi che garantiamo, che è l'opposto di ciò a cui serve la prova.", ja: "これは私たちに何も求めません。この一式は自身の公開鍵と自身のハッシュを携えており、計算が合うか合わないか、それだけです — 私たちの承認を要する検証は、私たちが保証することになってしまい、証拠の目的とは正反対です。", zh: "这不需要我们做任何事。这个包自带公钥和哈希，算术要么成立要么不成立——一项需要我们首肯的核验，就等于由我们作保，而那与证据的用途恰恰相反。", hi: "यह हमसे कुछ नहीं माँगता। पैकेज अपनी सार्वजनिक कुंजी और अपने हैश साथ लाता है, और गणित या तो टिकता है या नहीं — जिस जाँच को हमारी स्वीकृति चाहिए हो, वह हमारी ज़मानत होगी, जो साक्ष्य के उद्देश्य के ठीक उलट है।", ar: "هذا لا يطلب منّا شيئًا. الحزمة تحمل مفتاحها العام وبصماتها، والحساب إما يستقيم أو لا — وفحصٌ يحتاج مباركتنا يعني أننا نضمن، وهو نقيض الغاية من الدليل.",
  },
  "sgn.paste.ph": {
    en: "paste the evidence package (JSON)", es: "pegue el paquete de evidencia (JSON)", fr: "collez le paquet de preuve (JSON)", de: "das Beweispaket einfügen (JSON)", pt: "cole o pacote de evidência (JSON)", it: "incolla il pacchetto di prova (JSON)", ja: "証拠一式（JSON）を貼り付け", zh: "粘贴证据包（JSON）", hi: "साक्ष्य पैकेज चिपकाएँ (JSON)", ar: "الصق حزمة الدليل (JSON)",
  },
  "sgn.checkit": {
    en: "Check it", es: "Comprobarlo", fr: "Vérifier", de: "Prüfen", pt: "Verificar", it: "Verifica", ja: "確認する", zh: "核验", hi: "जाँचें", ar: "افحصها",
  },
  "sgn.holds": {
    en: "Holds up.", es: "Se sostiene.", fr: "Ça tient.", de: "Hält stand.", pt: "Aguenta-se.", it: "Regge.", ja: "成立します。", zh: "站得住。", hi: "टिकता है।", ar: "يصمد.",
  },
  "sgn.doesnot": {
    en: "Does not hold up.", es: "No se sostiene.", fr: "Ça ne tient pas.", de: "Hält nicht stand.", pt: "Não se aguenta.", it: "Non regge.", ja: "成立しません。", zh: "站不住。", hi: "नहीं टिकता।", ar: "لا يصمد.",
  },
  "sgn.didnotrun": {
    en: "· did not run, so it is not a pass", es: "· no se ejecutó, así que no es un aprobado", fr: "· n'a pas été exécuté, ce n'est donc pas une réussite", de: "· wurde nicht ausgeführt, gilt also nicht als bestanden", pt: "· não correu, por isso não é uma aprovação", it: "· non è stato eseguito, quindi non è un superamento", ja: "· 実行されていないので、合格ではありません", zh: "· 未运行，因此不算通过", hi: "· चला ही नहीं, इसलिए यह पास नहीं है", ar: "· لم يُنفَّذ، فليس نجاحًا",
  },
  "sgn.limits": {
    en: "What this does not prove", es: "Lo que esto no prueba", fr: "Ce que cela ne prouve pas", de: "Was das nicht beweist", pt: "O que isto não prova", it: "Cosa questo non dimostra", ja: "これが証明しないこと", zh: "这不能证明什么", hi: "यह क्या सिद्ध नहीं करता", ar: "ما لا يثبته هذا",
  },
  "plc.title": {
    en: "Where it is marketed", es: "Dónde se anuncia", fr: "Où il est diffusé", de: "Wo es beworben wird", pt: "Onde é divulgado", it: "Dove viene promosso", ja: "どこで宣伝されているか", zh: "它在哪里被推广", hi: "इसका प्रचार कहाँ है", ar: "أين يُعلَن عنه",
  },
  "plc.lead": {
    en: "An adult-mode profile can be advertised at an adult venue, as a link or a printable code.", es: "Un perfil en modo adulto puede anunciarse en un local para adultos, como enlace o como código imprimible.", fr: "Un profil en mode adulte peut être diffusé sur un espace pour adultes, sous forme de lien ou de code imprimable.", de: "Ein Profil im Erwachsenenmodus kann an einem Erwachsenen-Ort beworben werden, als Link oder als druckbarer Code.", pt: "Um perfil em modo adulto pode ser divulgado num espaço para adultos, como ligação ou como código imprimível.", it: "Un profilo in modalità adulti può essere promosso in uno spazio per adulti, come link o come codice stampabile.", ja: "アダルトモードのプロフィールは、アダルト向けの場でリンクまたは印刷可能なコードとして宣伝できます。", zh: "成人模式的资料可以在成人场所进行推广，形式为链接或可打印的二维码。", hi: "वयस्क-मोड प्रोफ़ाइल का प्रचार किसी वयस्क स्थल पर लिंक या छपने योग्य कोड के रूप में किया जा सकता है।", ar: "يمكن الإعلان عن ملف في وضع البالغين في مكان للبالغين، كرابط أو كرمز قابل للطباعة.",
  },
  "plc.venues": {
    en: "Venues", es: "Locales", fr: "Espaces", de: "Orte", pt: "Espaços", it: "Spazi", ja: "掲載先", zh: "场所", hi: "स्थल", ar: "الأماكن",
  },
  "plc.carries": {
    en: "Carries: {what}.", es: "Admite: {what}.", fr: "Accueille : {what}.", de: "Führt: {what}.", pt: "Aceita: {what}.", it: "Ospita: {what}.", ja: "扱うもの: {what}。", zh: "承载：{what}。", hi: "रखता है: {what}।", ar: "يحمل: {what}.",
  },
  "plc.place": {
    en: "Place this profile", es: "Colocar este perfil", fr: "Placer ce profil", de: "Dieses Profil platzieren", pt: "Colocar este perfil", it: "Colloca questo profilo", ja: "このプロフィールを掲載する", zh: "放置这份资料", hi: "इस प्रोफ़ाइल को रखें", ar: "ضع هذا الملف",
  },
  "plc.pick": {
    en: "pick a venue", es: "elija un local", fr: "choisissez un espace", de: "einen Ort wählen", pt: "escolha um espaço", it: "scegli uno spazio", ja: "掲載先を選ぶ", zh: "选择场所", hi: "स्थल चुनें", ar: "اختر مكانًا",
  },
  "plc.label.ph": {
    en: "what to call it (optional)", es: "cómo llamarlo (opcional)", fr: "comment l'appeler (facultatif)", de: "wie es heißen soll (optional)", pt: "como lhe chamar (opcional)", it: "come chiamarlo (facoltativo)", ja: "呼び名（任意）", zh: "如何称呼它（可选）", hi: "इसे क्या कहें (वैकल्पिक)", ar: "بمَ تسمّيه (اختياري)",
  },
  "plc.placebtn": {
    en: "Place", es: "Colocar", fr: "Placer", de: "Platzieren", pt: "Colocar", it: "Colloca", ja: "掲載", zh: "放置", hi: "रखें", ar: "ضع",
  },
  "plc.adultonly": {
    en: "Only an adult-mode profile can be placed at an adult venue, and the refusal says so rather than hiding the button.", es: "Solo un perfil en modo adulto puede colocarse en un local para adultos, y la negativa lo dice en vez de ocultar el botón.", fr: "Seul un profil en mode adulte peut être placé sur un espace pour adultes, et le refus le dit au lieu de cacher le bouton.", de: "Nur ein Profil im Erwachsenenmodus kann an einem Erwachsenen-Ort platziert werden, und die Ablehnung sagt das, statt den Knopf zu verstecken.", pt: "Só um perfil em modo adulto pode ser colocado num espaço para adultos, e a recusa di-lo em vez de esconder o botão.", it: "Solo un profilo in modalità adulti può essere collocato in uno spazio per adulti, e il rifiuto lo dice invece di nascondere il pulsante.", ja: "アダルト向けの場に掲載できるのはアダルトモードのプロフィールだけで、拒否はその旨を告げます。ボタンを隠したりはしません。", zh: "只有成人模式的资料才能放置在成人场所，拒绝时会明说，而不是把按钮藏起来。", hi: "वयस्क स्थल पर केवल वयस्क-मोड प्रोफ़ाइल ही रखी जा सकती है, और इनकार यही कहता है — बटन छिपाता नहीं।", ar: "لا يوضع في مكان للبالغين إلا ملف في وضع البالغين، والرفض يقول ذلك بدل أن يخفي الزر.",
  },
  "plc.publish": {
    en: "Publish this", es: "Publicar esto", fr: "Publier ceci", de: "Dies veröffentlichen", pt: "Publicar isto", it: "Pubblica questo", ja: "これを公開する", zh: "发布这个", hi: "इसे प्रकाशित करें", ar: "انشر هذا",
  },
  "plc.qr.made": {
    en: "the beacon's QR code", es: "el código QR de la baliza", fr: "le QR code de la balise", de: "der QR-Code der Bake", pt: "o código QR da baliza", it: "il codice QR del beacon", ja: "ビーコンの QR コード", zh: "该信标的二维码", hi: "बीकन का QR कोड", ar: "رمز الاستجابة السريعة للمنارة",
  },
  "plc.qr.row": {
    en: "this beacon's QR code", es: "el código QR de esta baliza", fr: "le QR code de cette balise", de: "der QR-Code dieser Bake", pt: "o código QR desta baliza", it: "il codice QR di questo beacon", ja: "このビーコンの QR コード", zh: "此信标的二维码", hi: "इस बीकन का QR कोड", ar: "رمز الاستجابة السريعة لهذه المنارة",
  },
  "plc.printshare": {
    en: "Print or share:", es: "Imprimir o compartir:", fr: "Imprimer ou partager :", de: "Drucken oder teilen:", pt: "Imprimir ou partilhar:", it: "Stampa o condividi:", ja: "印刷または共有:", zh: "打印或分享：", hi: "छापें या साझा करें:", ar: "اطبع أو شارك:",
  },
  "plc.thatone": {
    en: "That is the one a phone camera lands on and the one the code encodes. {url} is the machine-readable surface for clients, not a link to give anybody.", es: "Esa es la que una cámara de móvil alcanza y la que codifica el código. {url} es la superficie legible por máquinas para los clientes, no un enlace para dar a nadie.", fr: "C'est celle sur laquelle atterrit l'appareil photo d'un téléphone et celle que le code encode. {url} est la surface lisible par machine pour les clients, pas un lien à donner à quiconque.", de: "Das ist die, auf der eine Handykamera landet, und die, die der Code kodiert. {url} ist die maschinenlesbare Oberfläche für Clients, kein Link, den man jemandem gibt.", pt: "É essa a que uma câmara de telemóvel alcança e a que o código codifica. {url} é a superfície legível por máquinas para os clientes, não uma ligação para dar a ninguém.", it: "È quella su cui atterra la fotocamera di un telefono ed è quella che il codice codifica. {url} è la superficie leggibile dalle macchine per i client, non un link da dare a qualcuno.", ja: "スマートフォンのカメラがたどり着くのはそちらで、コードが符号化しているのもそちらです。{url} はクライアント向けの機械可読な面であって、誰かに渡すリンクではありません。", zh: "手机摄像头落到的是那一个，二维码编码的也是那一个。{url} 是给客户端读取的机器可读接口，不是拿去给人的链接。", hi: "फ़ोन का कैमरा जिस पर पहुँचता है और कोड जिसे एन्कोड करता है, वह वही है। {url} क्लाइंट के लिए मशीन-पठनीय सतह है, किसी को देने वाला लिंक नहीं।", ar: "ذاك هو ما تصل إليه كاميرا الهاتف وما يرمّزه الرمز. أما {url} فهو السطح المقروء آليًا للعملاء، لا رابطًا يُعطى لأحد.",
  },
  "plc.alsoas": {
    en: "Also reachable as {handle}.", es: "También accesible como {handle}.", fr: "Également joignable sous {handle}.", de: "Auch erreichbar als {handle}.", pt: "Também acessível como {handle}.", it: "Raggiungibile anche come {handle}.", ja: "{handle} でも到達できます。", zh: "也可以通过 {handle} 访问。", hi: "{handle} के रूप में भी पहुँचा जा सकता है।", ar: "يمكن الوصول إليه أيضًا باسم {handle}.",
  },
  "plc.nohandle": {
    en: "This profile has not claimed a handle, so the code and the link are the only ways in.", es: "Este perfil no ha reclamado un alias, así que el código y el enlace son las únicas vías de entrada.", fr: "Ce profil n'a pas revendiqué d'identifiant, donc le code et le lien sont les seules entrées.", de: "Dieses Profil hat keinen Handle beansprucht, also sind der Code und der Link die einzigen Zugänge.", pt: "Este perfil não reclamou um identificador, por isso o código e a ligação são as únicas entradas.", it: "Questo profilo non ha rivendicato un handle, quindi il codice e il link sono gli unici ingressi.", ja: "このプロフィールはハンドルを取得していないため、入口はコードとリンクだけです。", zh: "这份资料尚未认领任何用户名，因此二维码和链接是仅有的入口。", hi: "इस प्रोफ़ाइल ने कोई हैंडल नहीं लिया है, इसलिए कोड और लिंक ही एकमात्र रास्ते हैं।", ar: "لم يطالب هذا الملف بمعرّف، فالرمز والرابط هما المدخلان الوحيدان.",
  },
  "plc.keepthis": {
    en: "Keep this. The list below can reopen the beacon on whatever API this console is pointed at, but only this card knows the address the code was minted with.", es: "Guarde esto. La lista de abajo puede reabrir la baliza en la API a la que apunte esta consola, pero solo esta ficha conoce la dirección con la que se acuñó el código.", fr: "Gardez ceci. La liste ci-dessous peut rouvrir la balise sur l'API vers laquelle pointe cette console, mais seule cette fiche connaît l'adresse avec laquelle le code a été créé.", de: "Bewahren Sie das auf. Die Liste unten kann die Bake auf der API öffnen, auf die diese Konsole zeigt, aber nur diese Karte kennt die Adresse, mit der der Code erzeugt wurde.", pt: "Guarde isto. A lista abaixo pode reabrir a baliza na API para que esta consola aponta, mas só este cartão conhece o endereço com que o código foi cunhado.", it: "Conserva questo. L'elenco qui sotto può riaprire il beacon sull'API a cui punta questa console, ma solo questa scheda conosce l'indirizzo con cui il codice è stato coniato.", ja: "これは保管しておいてください。下の一覧は、このコンソールが向いている API 上でビーコンを開き直せますが、コードが発行されたときのアドレスを知っているのはこのカードだけです。", zh: "请保存这张卡片。下面的列表能在本控制台所指向的任意 API 上重新打开该信标，但只有这张卡片知道当初铸造该二维码时所用的地址。", hi: "इसे संभालकर रखें। नीचे की सूची इस कंसोल जिस भी API की ओर इंगित है, उस पर बीकन दोबारा खोल सकती है — पर कोड जिस पते के साथ बना था, वह केवल यही कार्ड जानता है।", ar: "احتفظ بهذه. القائمة أدناه تستطيع إعادة فتح المنارة على أي واجهة برمجة توجَّه إليها هذه اللوحة، لكن هذه البطاقة وحدها تعرف العنوان الذي سُكَّ به الرمز.",
  },
  "plc.placedat": {
    en: "Placed at", es: "Colocado en", fr: "Placé sur", de: "Platziert bei", pt: "Colocado em", it: "Collocato su", ja: "掲載先", zh: "已放置于", hi: "रखा गया", ar: "موضوع في",
  },
  "plc.nowhere": {
    en: "Nowhere yet.", es: "En ningún sitio todavía.", fr: "Nulle part pour l'instant.", de: "Noch nirgends.", pt: "Em lado nenhum ainda.", it: "Da nessuna parte per ora.", ja: "まだどこにもありません。", zh: "尚未放置。", hi: "अभी कहीं नहीं।", ar: "لا مكان بعد.",
  },
  "plc.signin": {
    en: "Sign in as an owner.", es: "Inicie sesión como propietario.", fr: "Connectez-vous comme propriétaire.", de: "Melden Sie sich als Besitzer an.", pt: "Entre como proprietário.", it: "Accedi come proprietario.", ja: "所有者としてサインインしてください。", zh: "请以所有者身份登录。", hi: "स्वामी के रूप में साइन इन करें।", ar: "سجّل الدخول بصفتك مالكًا.",
  },
  "plc.row": {
    en: "{venue} · {n} scan{s}", es: "{venue} · {n} escaneos", fr: "{venue} · {n} scans", de: "{venue} · {n} Scans", pt: "{venue} · {n} digitalizações", it: "{venue} · {n} scansioni", ja: "{venue} · スキャン{n}件", zh: "{venue} · {n} 次扫描", hi: "{venue} · {n} स्कैन", ar: "{venue} · {n} مسحة",
  },
  "plc.takendown": {
    en: " · taken down", es: " · retirado", fr: " · retiré", de: " · abgenommen", pt: " · retirado", it: " · rimosso", ja: " · 取り下げ済み", zh: " · 已撤下", hi: " · हटाया गया", ar: " · مُزال",
  },
  "plc.openhere": {
    en: "open here (counts as a scan)", es: "abrir aquí (cuenta como escaneo)", fr: "ouvrir ici (compte comme un scan)", de: "hier öffnen (zählt als Scan)", pt: "abrir aqui (conta como digitalização)", it: "apri qui (conta come scansione)", ja: "ここで開く（スキャン一回として数えます）", zh: "在此打开（计为一次扫描）", hi: "यहाँ खोलें (एक स्कैन गिना जाएगा)", ar: "افتح هنا (يُحسب مسحة)",
  },
  "plc.takedown": {
    en: "Take down", es: "Retirar", fr: "Retirer", de: "Abnehmen", pt: "Retirar", it: "Rimuovi", ja: "取り下げる", zh: "撤下", hi: "हटाएँ", ar: "أزِل",
  },
  "plc.takendown.said": {
    en: "Taken down. The beacon is {state} — anything already printed at the venue now stops resolving rather than pointing somewhere else.", es: "Retirado. La baliza está {state} — lo ya impreso en el local deja de resolver en vez de apuntar a otro sitio.", fr: "Retiré. La balise est {state} — ce qui est déjà imprimé sur place cesse de répondre au lieu de pointer ailleurs.", de: "Abgenommen. Die Bake ist {state} — was am Ort bereits gedruckt ist, löst nun nicht mehr auf, statt woanders hinzuzeigen.", pt: "Retirado. A baliza está {state} — o que já foi impresso no espaço deixa de resolver em vez de apontar para outro lado.", it: "Rimosso. Il beacon è {state} — ciò che è già stampato nello spazio smette di risolvere invece di puntare altrove.", ja: "取り下げました。ビーコンは{state}です — 会場にすでに印刷されたものは、別の場所を指すのではなく、応答しなくなります。", zh: "已撤下。信标{state}——场所里已经印出来的东西从此不再解析，而不是指向别处。", hi: "हटा दिया गया। बीकन {state} है — स्थल पर पहले से छपी कोई भी चीज़ अब कहीं और इशारा करने के बजाय हल होना बंद कर देती है।", ar: "أُزيل. المنارة {state} — وكل ما طُبع في المكان يتوقف عن الاستجابة بدل أن يشير إلى مكان آخر.",
  },
  "plc.stilllive": {
    en: "still live", es: "todavía activa", fr: "toujours active", de: "noch aktiv", pt: "ainda ativa", it: "ancora attivo", ja: "まだ有効", zh: "仍然有效", hi: "अब भी सक्रिय", ar: "ما زالت فعّالة",
  },
  "plc.nolonger": {
    en: "no longer live", es: "ya no activa", fr: "plus active", de: "nicht mehr aktiv", pt: "já não ativa", it: "non più attivo", ja: "もう有効ではない", zh: "不再有效", hi: "अब सक्रिय नहीं", ar: "لم تعد فعّالة",
  },
  "plc.brings": {
    en: "What each venue brings", es: "Lo que aporta cada local", fr: "Ce que chaque espace apporte", de: "Was jeder Ort einbringt", pt: "O que cada espaço traz", it: "Cosa porta ogni spazio", ja: "掲載先ごとの成果", zh: "每个场所带来了什么", hi: "हर स्थल क्या लाता है", ar: "ماذا يجلب كل مكان",
  },
  "plc.countsonly": {
    en: "Counts and rates only. Nobody who scans is identified, here or anywhere else.", es: "Solo recuentos y tasas. Nadie que escanee queda identificado, ni aquí ni en ninguna otra parte.", fr: "Uniquement des comptes et des taux. Personne qui scanne n'est identifié, ni ici ni ailleurs.", de: "Nur Zahlen und Quoten. Niemand, der scannt, wird identifiziert — hier nicht und nirgendwo sonst.", pt: "Apenas contagens e taxas. Ninguém que digitalize é identificado, aqui nem em lado nenhum.", it: "Solo conteggi e percentuali. Nessuno di chi scansiona viene identificato, né qui né altrove.", ja: "件数と割合だけです。スキャンした人が特定されることは、ここでも他のどこでもありません。", zh: "只有计数和比率。扫描的人不会被识别身份，无论在这里还是别处。", hi: "केवल गिनती और दरें। स्कैन करने वाला कोई भी पहचाना नहीं जाता — न यहाँ, न कहीं और।", ar: "أعداد ونسب فقط. لا يُعرَّف أي ماسح، لا هنا ولا في أي مكان آخر.",
  },
  "plc.venue.line": {
    en: "{n} resolution{s} · {walled} reached the age wall · {verified} got through it", es: "{n} resoluciones · {walled} llegaron al muro de edad · {verified} lo pasaron", fr: "{n} résolutions · {walled} ont atteint le mur d'âge · {verified} l'ont franchi", de: "{n} Auflösungen · {walled} erreichten die Alterssperre · {verified} kamen durch", pt: "{n} resoluções · {walled} chegaram ao muro de idade · {verified} passaram-no", it: "{n} risoluzioni · {walled} hanno raggiunto il muro d'età · {verified} l'hanno superato", ja: "解決 {n}件 · うち {walled}件が年齢の壁に到達 · {verified}件が通過", zh: "{n} 次解析 · {walled} 次抵达年龄墙 · {verified} 次通过", hi: "{n} समाधान · {walled} आयु-दीवार तक पहुँचे · {verified} पार कर गए", ar: "{n} استجابات · وصل {walled} إلى بوابة العمر · واجتازها {verified}",
  },
  "plc.everything": {
    en: "Everything else", es: "Todo lo demás", fr: "Tout le reste", de: "Alles andere", pt: "Todo o resto", it: "Tutto il resto", ja: "それ以外", zh: "其余的一切", hi: "बाक़ी सब", ar: "كل ما عدا ذلك",
  },
  "plc.direct": {
    en: "Arrivals that did not come through a placement: {walled} walled, {verified} verified.", es: "Llegadas que no vinieron por una colocación: {walled} frenadas por el muro, {verified} verificadas.", fr: "Arrivées qui ne sont pas passées par un placement : {walled} arrêtées au mur, {verified} vérifiées.", de: "Ankünfte, die nicht über eine Platzierung kamen: {walled} an der Sperre, {verified} verifiziert.", pt: "Chegadas que não vieram por uma colocação: {walled} travadas no muro, {verified} verificadas.", it: "Arrivi che non sono passati da un collocamento: {walled} fermati al muro, {verified} verificati.", ja: "掲載を経由しなかった到達: 壁で止まった {walled}件、確認済み {verified}件。", zh: "并非经由投放而来的访问：{walled} 次被墙拦下，{verified} 次已验证。", hi: "जो आगमन किसी प्लेसमेंट से नहीं आए: {walled} दीवार पर रुके, {verified} सत्यापित।", ar: "الوافدون الذين لم يأتوا عبر وضعٍ ما: {walled} أوقفتهم البوابة، و{verified} تحققوا.",
  },
  "plc.funnel": {
    en: "The funnel", es: "El embudo", fr: "L'entonnoir", de: "Der Trichter", pt: "O funil", it: "L'imbuto", ja: "流れ", zh: "漏斗", hi: "फ़नल", ar: "القمع",
  },
  "plc.funnel.line": {
    en: "{res} resolutions → {views} verified views → {chat} people who talked", es: "{res} resoluciones → {views} vistas verificadas → {chat} personas que hablaron", fr: "{res} résolutions → {views} vues vérifiées → {chat} personnes qui ont parlé", de: "{res} Auflösungen → {views} verifizierte Aufrufe → {chat} Menschen, die sprachen", pt: "{res} resoluções → {views} visualizações verificadas → {chat} pessoas que falaram", it: "{res} risoluzioni → {views} visualizzazioni verificate → {chat} persone che hanno parlato", ja: "解決 {res}件 → 確認済み閲覧 {views}件 → 話した人 {chat}人", zh: "{res} 次解析 → {views} 次已验证浏览 → {chat} 人开口交谈", hi: "{res} समाधान → {views} सत्यापित दृश्य → {chat} लोग जिन्होंने बात की", ar: "{res} استجابات ← {views} مشاهدات موثّقة ← {chat} أشخاص تحدثوا",
  },
  "plc.through": {
    en: "{pct}% get through the wall.", es: "El {pct}% pasa el muro.", fr: "{pct} % franchissent le mur.", de: "{pct}% kommen durch die Sperre.", pt: "{pct}% passam o muro.", it: "Il {pct}% supera il muro.", ja: "{pct}% が壁を通過します。", zh: "{pct}% 的人通过了这道墙。", hi: "{pct}% दीवार पार करते हैं।", ar: "يجتاز {pct}% البوابة.",
  },
  "plc.norate": {
    en: "Nothing has got through yet, so there is no conversion to quote.", es: "Todavía no ha pasado nadie, así que no hay conversión que citar.", fr: "Personne n'est encore passé, il n'y a donc aucun taux de conversion à citer.", de: "Bisher ist nichts durchgekommen, also gibt es keine Konversion zu nennen.", pt: "Ainda não passou nada, por isso não há conversão para citar.", it: "Non è ancora passato nulla, quindi non c'è conversione da citare.", ja: "まだ何も通過していないため、引用できる転換率はありません。", zh: "还没有任何人通过，因此没有可引用的转化率。", hi: "अभी तक कुछ भी पार नहीं हुआ, इसलिए उद्धृत करने योग्य कोई रूपांतरण नहीं।", ar: "لم يجتز شيء بعد، فلا نسبة تحوّل يمكن ذكرها.",
  },
  "plc.chatrate": {
    en: "{pct}% of those talk.", es: "De esos, el {pct}% habla.", fr: "{pct} % de ceux-là parlent.", de: "{pct}% davon sprechen.", pt: "Desses, {pct}% falam.", it: "Di quelli, il {pct}% parla.", ja: "そのうち {pct}% が話します。", zh: "其中 {pct}% 的人开口交谈。", hi: "उनमें से {pct}% बात करते हैं।", ar: "يتحدث {pct}% منهم.",
  },
  "plc.kept": {
    en: "What is kept, and where", es: "Qué se guarda, y dónde", fr: "Ce qui est conservé, et où", de: "Was aufbewahrt wird, und wo", pt: "O que é guardado, e onde", it: "Cosa viene conservato, e dove", ja: "何が、どこに残るか", zh: "保留什么，保留在哪里", hi: "क्या रखा जाता है, और कहाँ", ar: "ما يُحفَظ، وأين",
  },
  "plc.novault": {
    en: "This deployment has no vault, so nothing here is sealed. Rated resolutions are counted in the ordinary database.", es: "Esta instalación no tiene bóveda, así que aquí no hay nada sellado. Las resoluciones con clasificación se cuentan en la base de datos normal.", fr: "Cette installation n'a pas de coffre, donc rien ici n'est scellé. Les résolutions classées sont comptées dans la base de données ordinaire.", de: "Diese Installation hat keinen Tresor, also ist hier nichts versiegelt. Altersbewertete Auflösungen werden in der gewöhnlichen Datenbank gezählt.", pt: "Esta instalação não tem cofre, por isso nada aqui está selado. As resoluções classificadas são contadas na base de dados comum.", it: "Questa installazione non ha un caveau, quindi qui nulla è sigillato. Le risoluzioni classificate sono contate nel database ordinario.", ja: "この環境には保管庫がないため、ここでは何も封印されません。レーティング対象の解決は通常のデータベースで数えられます。", zh: "本部署没有保险库，因此这里没有任何内容被封存。分级解析记录被计入普通数据库。", hi: "इस परिनियोजन में कोई वॉल्ट नहीं है, इसलिए यहाँ कुछ भी सीलबंद नहीं। श्रेणीबद्ध समाधान सामान्य डेटाबेस में गिने जाते हैं।", ar: "هذا التنصيب بلا خزانة، فلا شيء هنا مختوم. تُحصى الاستجابات المصنَّفة في قاعدة البيانات العادية.",
  },
  "plc.reported": {
    en: "Reported as: {what}", es: "Informado como: {what}", fr: "Signalé comme : {what}", de: "Gemeldet als: {what}", pt: "Reportado como: {what}", it: "Riportato come: {what}", ja: "報告内容: {what}", zh: "报告为：{what}", hi: "जैसा बताया गया: {what}", ar: "أُبلغ عنه بوصفه: {what}",
  },
  "plc.sealed": {
    en: "Rated resolutions are sealed in the vault — so the record of who was age-checked is not this platform's to read.", es: "Las resoluciones con clasificación se sellan en la bóveda — así que el registro de quién pasó el control de edad no es de esta plataforma para leerlo.", fr: "Les résolutions classées sont scellées dans le coffre — le relevé de qui a subi la vérification d'âge n'appartient donc pas à cette plateforme.", de: "Altersbewertete Auflösungen werden im Tresor versiegelt — die Aufzeichnung, wer altersgeprüft wurde, steht dieser Plattform also nicht zum Lesen zu.", pt: "As resoluções classificadas são seladas no cofre — por isso o registo de quem passou a verificação de idade não é desta plataforma para ler.", it: "Le risoluzioni classificate sono sigillate nel caveau — quindi il registro di chi è stato verificato per l'età non spetta a questa piattaforma leggerlo.", ja: "レーティング対象の解決は保管庫に封印されます — ですから、誰が年齢確認を受けたかの記録は、このプラットフォームが読んでよいものではありません。", zh: "分级解析记录被封存在保险库中——因此，谁通过了年龄核验，这份记录不归本平台阅读。", hi: "श्रेणीबद्ध समाधान वॉल्ट में सीलबंद होते हैं — इसलिए किसकी आयु जाँची गई, वह रिकॉर्ड इस मंच के पढ़ने के लिए नहीं है।", ar: "الاستجابات المصنَّفة مختومة في الخزانة — فسجل من جرى التحقق من عمره ليس من حق هذه المنصة أن تقرأه.",
  },
  "wp.title": {
    en: "Watch together", es: "Ver juntos", fr: "Regarder ensemble", de: "Gemeinsam schauen", pt: "Ver juntos", it: "Guardare insieme", ja: "一緒に見る", zh: "一起看", hi: "साथ देखें", ar: "المشاهدة معًا",
  },
  "wp.lead": {
    en: "A posted video, a shared position, and whoever you bring — including your own profiles.", es: "Un vídeo publicado, una posición compartida, y a quien traigas — incluidos tus propios perfiles.", fr: "Une vidéo publiée, une position partagée, et qui vous amenez — y compris vos propres profils.", de: "Ein veröffentlichtes Video, eine gemeinsame Position, und wen Sie mitbringen — auch Ihre eigenen Profile.", pt: "Um vídeo publicado, uma posição partilhada, e quem trouxer — incluindo os seus próprios perfis.", it: "Un video pubblicato, una posizione condivisa, e chiunque porti — compresi i tuoi profili.", ja: "投稿された動画と、共有された再生位置と、あなたが連れてくる誰か — 自分のプロフィールも含めて。", zh: "一段已发布的视频、一个共享的播放位置，以及你带来的任何人——包括你自己的资料。", hi: "एक पोस्ट किया गया वीडियो, एक साझा स्थिति, और जिसे भी आप लाएँ — अपनी प्रोफ़ाइलों सहित।", ar: "مقطع منشور، وموضع مشترك، ومن تحضره معك — بما في ذلك ملفاتك أنت.",
  },
  "wp.startjoin": {
    en: "Start or join", es: "Empezar o unirse", fr: "Lancer ou rejoindre", de: "Starten oder beitreten", pt: "Começar ou entrar", it: "Avvia o unisciti", ja: "始めるか、参加するか", zh: "开始或加入", hi: "शुरू करें या शामिल हों", ar: "ابدأ أو انضم",
  },
  "wp.post.ph": {
    en: "post id (a post with a video)", es: "id de la publicación (una con vídeo)", fr: "id du post (un post avec une vidéo)", de: "Beitrags-ID (ein Beitrag mit Video)", pt: "id da publicação (uma com vídeo)", it: "id del post (un post con un video)", ja: "投稿ID（動画のある投稿）", zh: "帖子 ID（含视频的帖子）", hi: "पोस्ट आईडी (वीडियो वाली पोस्ट)", ar: "معرّف المنشور (منشور فيه فيديو)",
  },
  "wp.title.ph": {
    en: "call it something", es: "ponle un nombre", fr: "donnez-lui un nom", de: "nennen Sie es irgendwie", pt: "dê-lhe um nome", it: "dagli un nome", ja: "名前をつける", zh: "起个名字", hi: "इसे कोई नाम दें", ar: "سمّها بشيء",
  },
  "wp.start": {
    en: "Start", es: "Empezar", fr: "Lancer", de: "Starten", pt: "Começar", it: "Avvia", ja: "始める", zh: "开始", hi: "शुरू करें", ar: "ابدأ",
  },
  "wp.started.said": {
    en: "Open. Bring people in.", es: "Abierta. Trae a gente.", fr: "Ouverte. Faites venir du monde.", de: "Offen. Holen Sie Leute dazu.", pt: "Aberta. Traga pessoas.", it: "Aperta. Porta gente.", ja: "開きました。人を呼んでください。", zh: "已开启。把人带进来吧。", hi: "खुल गई। लोगों को लाइए।", ar: "مفتوحة. أحضر الناس.",
  },
  "wp.party.ph": {
    en: "party id", es: "id de la sala", fr: "id de la séance", de: "Party-ID", pt: "id da sessão", it: "id della festa", ja: "パーティID", zh: "放映会 ID", hi: "पार्टी आईडी", ar: "معرّف الجلسة",
  },
  "wp.join": {
    en: "Join", es: "Unirse", fr: "Rejoindre", de: "Beitreten", pt: "Entrar", it: "Unisciti", ja: "参加", zh: "加入", hi: "शामिल हों", ar: "انضم",
  },
  "wp.joined.said": {
    en: "You are in.", es: "Ya estás dentro.", fr: "Vous y êtes.", de: "Sie sind dabei.", pt: "Está dentro.", it: "Ci sei.", ja: "参加しました。", zh: "你已加入。", hi: "आप अंदर हैं।", ar: "أنت في الداخل.",
  },
  "wp.open": {
    en: "Open", es: "Abrir", fr: "Ouvrir", de: "Öffnen", pt: "Abrir", it: "Apri", ja: "開く", zh: "打开", hi: "खोलें", ar: "افتح",
  },
  "wp.untitled": {
    en: "Watch party", es: "Sala de visionado", fr: "Séance de visionnage", de: "Watch-Party", pt: "Sessão de visionamento", it: "Festa di visione", ja: "視聴パーティ", zh: "观影派对", hi: "वॉच पार्टी", ar: "جلسة مشاهدة",
  },
  "wp.video.on": {
    en: "{title} on {platform}", es: "{title} en {platform}", fr: "{title} sur {platform}", de: "{title} auf {platform}", pt: "{title} em {platform}", it: "{title} su {platform}", ja: "{platform} の {title}", zh: "{platform} 上的 {title}", hi: "{platform} पर {title}", ar: "{title} على {platform}",
  },
  "wp.at": {
    en: "At {n}s · {state} · {people} · {profiles}", es: "En {n}s · {state} · {people} · {profiles}", fr: "À {n}s · {state} · {people} · {profiles}", de: "Bei {n}s · {state} · {people} · {profiles}", pt: "Em {n}s · {state} · {people} · {profiles}", it: "A {n}s · {state} · {people} · {profiles}", ja: "{n}秒地点 · {state} · {people} · {profiles}", zh: "位于 {n} 秒 · {state} · {people} · {profiles}", hi: "{n}से. पर · {state} · {people} · {profiles}", ar: "عند {n}ث · {state} · {people} · {profiles}",
  },
  "wp.playing": {
    en: "playing", es: "reproduciendo", fr: "en lecture", de: "läuft", pt: "a reproduzir", it: "in riproduzione", ja: "再生中", zh: "播放中", hi: "चल रहा है", ar: "قيد التشغيل",
  },
  "wp.paused": {
    en: "paused", es: "en pausa", fr: "en pause", de: "pausiert", pt: "em pausa", it: "in pausa", ja: "一時停止", zh: "已暂停", hi: "रुका हुआ", ar: "متوقف مؤقتًا",
  },
  "wp.people": {
    en: "{n} people", es: "{n} personas", fr: "{n} personnes", de: "{n} Personen", pt: "{n} pessoas", it: "{n} persone", ja: "{n}人", zh: "{n} 人", hi: "{n} लोग", ar: "{n} أشخاص",
  },
  "wp.person": {
    en: "{n} person", es: "{n} persona", fr: "{n} personne", de: "{n} Person", pt: "{n} pessoa", it: "{n} persona", ja: "{n}人", zh: "{n} 人", hi: "{n} व्यक्ति", ar: "{n} شخص",
  },
  "wp.profiles": {
    en: "{n} profiles", es: "{n} perfiles", fr: "{n} profils", de: "{n} Profile", pt: "{n} perfis", it: "{n} profili", ja: "プロフィール{n}件", zh: "{n} 份资料", hi: "{n} प्रोफ़ाइलें", ar: "{n} ملفات",
  },
  "wp.profile": {
    en: "{n} profile", es: "{n} perfil", fr: "{n} profil", de: "{n} Profil", pt: "{n} perfil", it: "{n} profilo", ja: "プロフィール{n}件", zh: "{n} 份资料", hi: "{n} प्रोफ़ाइल", ar: "{n} ملف",
  },
  "wp.who": {
    en: "Who is here", es: "Quién está aquí", fr: "Qui est là", de: "Wer hier ist", pt: "Quem está aqui", it: "Chi c'è", ja: "誰がいるか", zh: "谁在这里", hi: "कौन यहाँ है", ar: "من الحاضر",
  },
  "wp.synthetic": {
    en: "synthetic", es: "sintético", fr: "synthétique", de: "synthetisch", pt: "sintético", it: "sintetico", ja: "合成", zh: "合成", hi: "सिंथेटिक", ar: "اصطناعي",
  },
  "wp.leave": {
    en: "Leave", es: "Salir", fr: "Quitter", de: "Verlassen", pt: "Sair", it: "Esci", ja: "退出", zh: "离开", hi: "बाहर जाएँ", ar: "غادر",
  },
  "wp.left.said": {
    en: "You left.", es: "Has salido.", fr: "Vous êtes parti.", de: "Sie sind gegangen.", pt: "Saiu.", it: "Sei uscito.", ja: "退出しました。", zh: "你已离开。", hi: "आप बाहर आ गए।", ar: "غادرت.",
  },
  "wp.remove": {
    en: "Remove", es: "Quitar", fr: "Retirer", de: "Entfernen", pt: "Remover", it: "Rimuovi", ja: "外す", zh: "移出", hi: "हटाएँ", ar: "أخرِج",
  },
  "wp.removed.said": {
    en: "Removed.", es: "Retirado.", fr: "Retiré.", de: "Entfernt.", pt: "Removido.", it: "Rimosso.", ja: "外しました。", zh: "已移出。", hi: "हटा दिया गया।", ar: "أُخرِج.",
  },
  "wp.bring.ph": {
    en: "a profile id of yours", es: "un id de perfil tuyo", fr: "un id de profil à vous", de: "eine Ihrer Profil-IDs", pt: "um id de perfil seu", it: "un id di un tuo profilo", ja: "あなたのプロフィールID", zh: "你自己的某个资料 ID", hi: "आपकी किसी प्रोफ़ाइल की आईडी", ar: "معرّف ملف يخصّك",
  },
  "wp.bring": {
    en: "Bring a profile", es: "Traer un perfil", fr: "Amener un profil", de: "Ein Profil mitbringen", pt: "Trazer um perfil", it: "Porta un profilo", ja: "プロフィールを連れてくる", zh: "带一份资料进来", hi: "एक प्रोफ़ाइल लाएँ", ar: "أحضِر ملفًا",
  },
  "wp.brought.said": {
    en: "Brought in.", es: "Traído.", fr: "Amené.", de: "Dazugeholt.", pt: "Trazido.", it: "Portato dentro.", ja: "連れてきました。", zh: "已带入。", hi: "ले आए।", ar: "أُحضِر.",
  },
  "wp.bring.note": {
    en: "Bringing a profile in speaks in its voice, so it needs that profile's own owner token — not yours as a person.", es: "Traer un perfil habla con su voz, así que necesita el token de propietario de ese perfil — no el tuyo como persona.", fr: "Amener un profil, c'est parler de sa voix : il faut donc le jeton de propriétaire de ce profil-là — pas le vôtre en tant que personne.", de: "Ein Profil mitzubringen spricht mit dessen Stimme, also braucht es das Besitzer-Token genau dieses Profils — nicht Ihres als Person.", pt: "Trazer um perfil fala com a voz dele, por isso precisa do token de proprietário desse perfil — não do seu como pessoa.", it: "Portare dentro un profilo parla con la sua voce, quindi serve il token da proprietario di quel profilo — non il tuo come persona.", ja: "プロフィールを連れてくることは、その声で話すことです。ですから、あなた個人のものではなく、そのプロフィール自身の所有者トークンが必要です。", zh: "把一份资料带进来，就是以它的声音说话，所以需要那份资料自己的所有者令牌——而不是你作为个人的令牌。", hi: "किसी प्रोफ़ाइल को लाना उसकी आवाज़ में बोलना है, इसलिए उसके लिए उसी प्रोफ़ाइल का अपना स्वामी टोकन चाहिए — एक व्यक्ति के रूप में आपका नहीं।", ar: "إحضار ملف يعني الكلام بصوته، فيلزمه رمز مالك ذلك الملف نفسه — لا رمزك أنت بصفتك شخصًا.",
  },
  "wp.position": {
    en: "The room's position", es: "La posición de la sala", fr: "La position de la salle", de: "Die Position des Raums", pt: "A posição da sala", it: "La posizione della stanza", ja: "部屋の再生位置", zh: "房间的播放位置", hi: "कक्ष की स्थिति", ar: "موضع الغرفة",
  },
  "wp.back15": {
    en: "−15s", es: "−15 s", fr: "−15 s", de: "−15 s", pt: "−15 s", it: "−15 s", ja: "−15秒", zh: "−15 秒", hi: "−15से.", ar: "−15ث",
  },
  "wp.fwd15": {
    en: "+15s", es: "+15 s", fr: "+15 s", de: "+15 s", pt: "+15 s", it: "+15 s", ja: "+15秒", zh: "+15 秒", hi: "+15से.", ar: "+15ث",
  },
  "wp.markpaused": {
    en: "Mark paused", es: "Marcar en pausa", fr: "Marquer en pause", de: "Als pausiert markieren", pt: "Marcar em pausa", it: "Segna in pausa", ja: "一時停止として記録", zh: "标记为暂停", hi: "रुका हुआ चिह्नित करें", ar: "علّمها متوقفة",
  },
  "wp.markplaying": {
    en: "Mark playing", es: "Marcar reproduciendo", fr: "Marquer en lecture", de: "Als laufend markieren", pt: "Marcar a reproduzir", it: "Segna in riproduzione", ja: "再生中として記録", zh: "标记为播放", hi: "चालू चिह्नित करें", ar: "علّمها قيد التشغيل",
  },
  "wp.end": {
    en: "End the party", es: "Terminar la sala", fr: "Terminer la séance", de: "Die Party beenden", pt: "Terminar a sessão", it: "Chiudi la festa", ja: "パーティを終える", zh: "结束派对", hi: "पार्टी समाप्त करें", ar: "أنهِ الجلسة",
  },
  "wp.ended.said": {
    en: "Ended. {grants} grant(s) closed, {mics} microphone(s) returned.", es: "Terminada. {grants} concesión(es) cerradas, {mics} micrófono(s) devueltos.", fr: "Terminée. {grants} autorisation(s) fermée(s), {mics} microphone(s) rendu(s).", de: "Beendet. {grants} Freigabe(n) geschlossen, {mics} Mikrofon(e) zurückgegeben.", pt: "Terminada. {grants} concessão(ões) fechadas, {mics} microfone(s) devolvidos.", it: "Chiusa. {grants} concessione/i chiuse, {mics} microfono/i restituiti.", ja: "終了しました。許可 {grants} 件を閉じ、マイク {mics} 本を返却しました。", zh: "已结束。关闭了 {grants} 项授权，归还了 {mics} 只麦克风。", hi: "समाप्त। {grants} अनुदान बंद, {mics} माइक्रोफ़ोन लौटाए गए।", ar: "انتهت. أُغلقت {grants} من التصاريح، وأُعيد {mics} من الميكروفونات.",
  },
  "wp.seek.note": {
    en: "This moves a number. It does not press play on anybody's device — each person's own player still starts when they start it.", es: "Esto mueve un número. No le da al play en el dispositivo de nadie — el reproductor de cada persona sigue arrancando cuando ella lo arranca.", fr: "Ceci déplace un nombre. Cela n'appuie pas sur lecture sur l'appareil de qui que ce soit — le lecteur de chacun démarre toujours quand il le démarre.", de: "Das verschiebt eine Zahl. Es drückt auf niemandes Gerät auf Play — der Player jeder Person startet weiterhin dann, wenn sie ihn startet.", pt: "Isto move um número. Não carrega em play no dispositivo de ninguém — o leitor de cada pessoa continua a arrancar quando ela o arranca.", it: "Questo sposta un numero. Non preme play sul dispositivo di nessuno — il lettore di ciascuno parte ancora quando è lui a farlo partire.", ja: "これは数字を動かすだけです。誰かの端末で再生を押すわけではありません — 各自のプレーヤーは、その人が始めたときに始まります。", zh: "这只是移动一个数字。它不会在任何人的设备上按下播放——每个人的播放器仍然由本人启动时才启动。", hi: "यह एक संख्या को हिलाता है। यह किसी के डिवाइस पर प्ले नहीं दबाता — हर व्यक्ति का अपना प्लेयर तभी शुरू होता है जब वह उसे शुरू करे।", ar: "هذا يحرّك رقمًا. ولا يضغط تشغيل على جهاز أحد — مشغّل كل شخص يبدأ حين يبدأه هو.",
  },
  "wp.room": {
    en: "The room", es: "La sala", fr: "La salle", de: "Der Raum", pt: "A sala", it: "La stanza", ja: "部屋", zh: "房间", hi: "कक्ष", ar: "الغرفة",
  },
  "wp.nothing": {
    en: "Nothing said yet.", es: "Nadie ha dicho nada.", fr: "Rien n'a encore été dit.", de: "Noch nichts gesagt.", pt: "Ainda nada dito.", it: "Ancora niente detto.", ja: "まだ何も言われていません。", zh: "还没有人说话。", hi: "अभी कुछ नहीं कहा गया।", ar: "لم يُقل شيء بعد.",
  },
  "wp.atpos": {
    en: "(at {n}s)", es: "(en {n} s)", fr: "(à {n} s)", de: "(bei {n} s)", pt: "(em {n} s)", it: "(a {n} s)", ja: "（{n}秒地点）", zh: "（第 {n} 秒）", hi: "({n}से. पर)", ar: "(عند {n}ث)",
  },
  "wp.say.ph": {
    en: "say something", es: "di algo", fr: "dites quelque chose", de: "sagen Sie etwas", pt: "diga algo", it: "di' qualcosa", ja: "何か言う", zh: "说点什么", hi: "कुछ कहें", ar: "قل شيئًا",
  },
  "wp.say": {
    en: "Say it", es: "Decirlo", fr: "Envoyer", de: "Sagen", pt: "Dizer", it: "Dillo", ja: "送る", zh: "说出来", hi: "कह दें", ar: "قلها",
  },
  "wp.held": {
    en: "Held: {why}", es: "Retenido: {why}", fr: "Retenu : {why}", de: "Zurückgehalten: {why}", pt: "Retido: {why}", it: "Trattenuto: {why}", ja: "保留: {why}", zh: "已留置：{why}", hi: "रोका गया: {why}", ar: "محتجز: {why}",
  },
  "wp.knows": {
    en: "What a profile in here knows", es: "Lo que sabe un perfil que esté aquí", fr: "Ce que sait un profil présent ici", de: "Was ein Profil hier drin weiß", pt: "O que sabe um perfil que esteja aqui", it: "Cosa sa un profilo che è qui dentro", ja: "ここにいるプロフィールが知っていること", zh: "这里的资料知道什么", hi: "यहाँ मौजूद प्रोफ़ाइल क्या जानती है", ar: "ما يعرفه ملف موجود هنا",
  },
  "wp.knows.pitch": {
    en: "Everything a synthetic profile in this party is given — and the absences are the point, so they are listed too.", es: "Todo lo que se le da a un perfil sintético en esta sala — y las ausencias son el asunto, así que también se listan.", fr: "Tout ce qu'on donne à un profil synthétique dans cette séance — et les absences sont l'essentiel, elles sont donc listées aussi.", de: "Alles, was einem synthetischen Profil in dieser Party gegeben wird — und die Auslassungen sind der Punkt, also stehen sie auch da.", pt: "Tudo o que é dado a um perfil sintético nesta sessão — e as ausências são o essencial, por isso também são listadas.", it: "Tutto ciò che viene dato a un profilo sintetico in questa festa — e le assenze sono il punto, quindi sono elencate anch'esse.", ja: "このパーティにいる合成プロフィールに与えられるすべて — そして、与えられないものこそが要点なので、それも並べてあります。", zh: "在这场派对里，一份合成资料被给予的一切——而没有被给予的才是重点，所以也一并列出。", hi: "इस पार्टी में किसी सिंथेटिक प्रोफ़ाइल को जो कुछ दिया जाता है — और जो नहीं दिया जाता वही असल बात है, इसलिए वह भी सूचीबद्ध है।", ar: "كل ما يُعطى لملف اصطناعي في هذه الجلسة — والغياب هو المقصود، لذا يُذكر هو أيضًا.",
  },
  "wp.ctx.title": {
    en: "Title: {title} on {platform}", es: "Título: {title} en {platform}", fr: "Titre : {title} sur {platform}", de: "Titel: {title} auf {platform}", pt: "Título: {title} em {platform}", it: "Titolo: {title} su {platform}", ja: "題名: {platform} の {title}", zh: "标题：{platform} 上的 {title}", hi: "शीर्षक: {platform} पर {title}", ar: "العنوان: {title} على {platform}",
  },
  "wp.ctx.avail": {
    en: "Description: {desc} · Transcript: {trans}", es: "Descripción: {desc} · Transcripción: {trans}", fr: "Description : {desc} · Transcription : {trans}", de: "Beschreibung: {desc} · Transkript: {trans}", pt: "Descrição: {desc} · Transcrição: {trans}", it: "Descrizione: {desc} · Trascrizione: {trans}", ja: "説明: {desc} · 文字起こし: {trans}", zh: "简介：{desc} · 字幕文本：{trans}", hi: "विवरण: {desc} · प्रतिलेख: {trans}", ar: "الوصف: {desc} · النص المكتوب: {trans}",
  },
  "wp.yes": {
    en: "yes", es: "sí", fr: "oui", de: "ja", pt: "sim", it: "sì", ja: "あり", zh: "有", hi: "हाँ", ar: "نعم",
  },
  "wp.notavail": {
    en: "not available", es: "no disponible", fr: "non disponible", de: "nicht verfügbar", pt: "não disponível", it: "non disponibile", ja: "なし", zh: "不可用", hi: "उपलब्ध नहीं", ar: "غير متاح",
  },
  "wp.notseen": {
    en: " · it has not seen the video", es: " · no ha visto el vídeo", fr: " · il n'a pas vu la vidéo", de: " · es hat das Video nicht gesehen", pt: " · não viu o vídeo", it: " · non ha visto il video", ja: " · 動画は見ていません", zh: " · 它没有看过这段视频", hi: " · इसने वीडियो नहीं देखा", ar: " · لم يشاهد المقطع",
  },
  "wp.cansee": {
    en: "It can see {n} recent line{s} and the position ({pos}s).", es: "Puede ver {n} líneas recientes y la posición ({pos} s).", fr: "Il voit {n} lignes récentes et la position ({pos} s).", de: "Es sieht {n} aktuelle Zeilen und die Position ({pos} s).", pt: "Vê {n} linhas recentes e a posição ({pos} s).", it: "Vede {n} righe recenti e la posizione ({pos} s).", ja: "直近の発言{n}件と再生位置（{pos}秒）が見えています。", zh: "它能看到最近的 {n} 条发言和播放位置（第 {pos} 秒）。", hi: "यह हाल की {n} पंक्तियाँ और स्थिति ({pos}से.) देख सकता है।", ar: "يرى {n} من الأسطر الأخيرة والموضع ({pos}ث).",
  },
  "dlg.title": {
    en: "Delegation & work", es: "Delegación y trabajo", fr: "Délégation et travail", de: "Delegation und Arbeit", pt: "Delegação e trabalho", it: "Delega e lavoro", ja: "委任と仕事", zh: "委托与工作", hi: "प्रत्यायोजन और काम", ar: "التفويض والعمل",
  },
  "dlg.signin": {
    en: "Sign in as the owner to set delegation.", es: "Inicie sesión como propietario para configurar la delegación.", fr: "Connectez-vous comme propriétaire pour régler la délégation.", de: "Melden Sie sich als Besitzer an, um die Delegation zu setzen.", pt: "Entre como proprietário para definir a delegação.", it: "Accedi come proprietario per impostare la delega.", ja: "委任を設定するには所有者としてサインインしてください。", zh: "请以所有者身份登录以设置委托。", hi: "प्रत्यायोजन तय करने के लिए स्वामी के रूप में साइन इन करें।", ar: "سجّل الدخول بصفتك مالكًا لضبط التفويض.",
  },
  "dlg.grant": {
    en: "The grant it reads through", es: "La concesión a través de la que lee", fr: "L'autorisation à travers laquelle il lit", de: "Die Freigabe, durch die es liest", pt: "A concessão através da qual lê", it: "La concessione attraverso cui legge", ja: "読み取りを通す許可", zh: "它据以读取的授权", hi: "वह अनुदान जिससे होकर यह पढ़ता है", ar: "التصريح الذي يقرأ من خلاله",
  },
  "dlg.grant.pitch": {
    en: "A grant is a revocable scope. It is what a phase reads the profile's own material through, and it can be withdrawn mid-run — the work stops seeing what the grant covered from that moment, not at the end.", es: "Una concesión es un alcance revocable. Es aquello a través de lo cual una fase lee el material del propio perfil, y puede retirarse a mitad de ejecución — el trabajo deja de ver lo que la concesión cubría desde ese momento, no al final.", fr: "Une autorisation est une portée révocable. C'est à travers elle qu'une phase lit le matériel du profil, et elle peut être retirée en cours d'exécution — le travail cesse de voir ce qu'elle couvrait à partir de cet instant, pas à la fin.", de: "Eine Freigabe ist ein widerrufbarer Umfang. Durch sie liest eine Phase das eigene Material des Profils, und sie kann mitten im Lauf entzogen werden — die Arbeit sieht ab diesem Moment nicht mehr, was die Freigabe abdeckte, nicht erst am Ende.", pt: "Uma concessão é um âmbito revogável. É através dela que uma fase lê o material do próprio perfil, e pode ser retirada a meio da execução — o trabalho deixa de ver o que a concessão cobria a partir desse momento, não no fim.", it: "Una concessione è un ambito revocabile. È ciò attraverso cui una fase legge il materiale del profilo, e può essere ritirata a metà esecuzione — il lavoro smette di vedere ciò che copriva da quel momento, non alla fine.", ja: "許可とは、取り消しうる範囲のことです。各段階はそれを通してプロフィール自身の資料を読み、実行の途中でも取り下げられます — 仕事がその範囲を見られなくなるのは、終わりではなくその瞬間からです。", zh: "授权是一个可撤销的范围。各阶段正是透过它读取资料自身的素材，而且可以在运行途中撤回——工作从那一刻起就看不到授权所覆盖的内容，而不是等到结束。", hi: "अनुदान एक वापस लिया जा सकने वाला दायरा है। कोई चरण प्रोफ़ाइल की अपनी सामग्री इसी से होकर पढ़ता है, और इसे बीच में ही वापस लिया जा सकता है — काम उसी क्षण से वह देखना बंद कर देता है जो अनुदान में था, अंत में नहीं।", ar: "التصريح نطاق قابل للإلغاء. من خلاله يقرأ الطور مواد الملف نفسه، ويمكن سحبه في منتصف التنفيذ — فيتوقف العمل عن رؤية ما كان يغطيه من تلك اللحظة، لا عند النهاية.",
  },
  "dlg.noscope": {
    en: "no scope", es: "sin alcance", fr: "aucune portée", de: "kein Umfang", pt: "sem âmbito", it: "nessun ambito", ja: "範囲なし", zh: "无范围", hi: "कोई दायरा नहीं", ar: "بلا نطاق",
  },
  "dlg.revoked": {
    en: "revoked", es: "revocada", fr: "révoquée", de: "widerrufen", pt: "revogada", it: "revocata", ja: "取り消し済み", zh: "已撤销", hi: "निरस्त", ar: "مُلغى",
  },
  "dlg.revoke": {
    en: "Revoke", es: "Revocar", fr: "Révoquer", de: "Widerrufen", pt: "Revogar", it: "Revoca", ja: "取り消す", zh: "撤销", hi: "निरस्त करें", ar: "ألغِ",
  },
  "dlg.revoked.said": {
    en: "Revoked. Anything running stops reading through it now.", es: "Revocada. Lo que esté en marcha deja de leer a través de ella ahora.", fr: "Révoquée. Tout ce qui tourne cesse de lire à travers elle dès maintenant.", de: "Widerrufen. Was läuft, liest ab jetzt nicht mehr hindurch.", pt: "Revogada. O que estiver a correr deixa de ler através dela agora.", it: "Revocata. Ciò che è in esecuzione smette di leggerci attraverso da adesso.", ja: "取り消しました。実行中のものは、今この瞬間からそれを通して読まなくなります。", zh: "已撤销。正在运行的一切从现在起不再透过它读取。", hi: "निरस्त। जो कुछ चल रहा है वह अभी से इसके ज़रिए पढ़ना बंद कर देता है।", ar: "أُلغي. وكل ما يعمل يتوقف الآن عن القراءة من خلاله.",
  },
  "dlg.mint": {
    en: "Mint a grant over my sources", es: "Emitir una concesión sobre mis fuentes", fr: "Créer une autorisation sur mes sources", de: "Eine Freigabe über meine Quellen erzeugen", pt: "Emitir uma concessão sobre as minhas fontes", it: "Conia una concessione sulle mie fonti", ja: "自分の資料に対する許可を発行する", zh: "为我的素材铸造一份授权", hi: "मेरे स्रोतों पर अनुदान बनाएँ", ar: "أنشئ تصريحًا على مصادري",
  },
  "dlg.minted.said": {
    en: "Grant minted.", es: "Concesión emitida.", fr: "Autorisation créée.", de: "Freigabe erzeugt.", pt: "Concessão emitida.", it: "Concessione coniata.", ja: "許可を発行しました。", zh: "授权已铸造。", hi: "अनुदान बन गया।", ar: "أُنشئ التصريح.",
  },
  "dlg.unattended": {
    en: "What it may do unattended", es: "Lo que puede hacer sin supervisión", fr: "Ce qu'il peut faire sans surveillance", de: "Was es unbeaufsichtigt tun darf", pt: "O que pode fazer sem supervisão", it: "Cosa può fare senza sorveglianza", ja: "見ていないところで何をしてよいか", zh: "无人看管时它可以做什么", hi: "बिना निगरानी यह क्या कर सकता है", ar: "ما يجوز له فعله دون إشراف",
  },
  "dlg.on": {
    en: "On. Anything not ticked still stops and waits for you.", es: "Activado. Lo que no esté marcado sigue parándose y esperándote.", fr: "Activé. Ce qui n'est pas coché s'arrête toujours et vous attend.", de: "An. Was nicht angehakt ist, hält weiterhin an und wartet auf Sie.", pt: "Ligado. O que não estiver assinalado continua a parar e a esperar por si.", it: "Attivo. Ciò che non è spuntato si ferma comunque e ti aspetta.", ja: "オンです。チェックされていないものは、やはり止まってあなたを待ちます。", zh: "已开启。未勾选的部分仍会停下来等你。", hi: "चालू। जिस पर निशान नहीं है वह फिर भी रुककर आपकी प्रतीक्षा करेगा।", ar: "مفعَّل. وما لم يُؤشَّر عليه يظل يتوقف وينتظرك.",
  },
  "dlg.off": {
    en: "Off. Every phase stops and waits for you.", es: "Desactivado. Cada fase se para y te espera.", fr: "Désactivé. Chaque phase s'arrête et vous attend.", de: "Aus. Jede Phase hält an und wartet auf Sie.", pt: "Desligado. Cada fase para e espera por si.", it: "Spento. Ogni fase si ferma e ti aspetta.", ja: "オフです。すべての段階が止まってあなたを待ちます。", zh: "已关闭。每个阶段都会停下来等你。", hi: "बंद। हर चरण रुककर आपकी प्रतीक्षा करता है।", ar: "معطَّل. كل طور يتوقف وينتظرك.",
  },
  "dlg.needone": {
    en: "A policy needs at least one phase. Turn delegation off instead if the profile should do nothing unattended.", es: "Una política necesita al menos una fase. Desactiva la delegación si el perfil no debe hacer nada sin supervisión.", fr: "Une politique exige au moins une phase. Désactivez plutôt la délégation si le profil ne doit rien faire sans surveillance.", de: "Eine Richtlinie braucht mindestens eine Phase. Schalten Sie die Delegation stattdessen aus, wenn das Profil unbeaufsichtigt nichts tun soll.", pt: "Uma política precisa de pelo menos uma fase. Desligue antes a delegação se o perfil não deve fazer nada sem supervisão.", it: "Una politica ha bisogno di almeno una fase. Spegni invece la delega se il profilo non deve fare nulla senza sorveglianza.", ja: "方針には少なくとも一つの段階が必要です。見ていないところで何もさせたくないなら、委任そのものをオフにしてください。", zh: "一条策略至少需要一个阶段。如果不希望资料在无人看管时做任何事，请直接关闭委托。", hi: "किसी नीति में कम से कम एक चरण चाहिए। यदि प्रोफ़ाइल को बिना निगरानी कुछ नहीं करना है, तो प्रत्यायोजन ही बंद कर दें।", ar: "السياسة تحتاج طورًا واحدًا على الأقل. أوقف التفويض بدلًا من ذلك إن كان الملف يجب ألا يفعل شيئًا دون إشراف.",
  },
  "dlg.delegating.said": {
    en: "Delegating: {what}.", es: "Delegando: {what}.", fr: "Délégué : {what}.", de: "Delegiert: {what}.", pt: "A delegar: {what}.", it: "Delego: {what}.", ja: "委任中: {what}。", zh: "已委托：{what}。", hi: "प्रत्यायोजित: {what}।", ar: "مفوَّض: {what}.",
  },
  "dlg.turn.on": {
    en: "Turn delegation on", es: "Activar la delegación", fr: "Activer la délégation", de: "Delegation einschalten", pt: "Ligar a delegação", it: "Attiva la delega", ja: "委任をオンにする", zh: "开启委托", hi: "प्रत्यायोजन चालू करें", ar: "فعّل التفويض",
  },
  "dlg.turn.off": {
    en: "Turn delegation off", es: "Desactivar la delegación", fr: "Désactiver la délégation", de: "Delegation ausschalten", pt: "Desligar a delegação", it: "Disattiva la delega", ja: "委任をオフにする", zh: "关闭委托", hi: "प्रत्यायोजन बंद करें", ar: "عطّل التفويض",
  },
  "dlg.on.said": {
    en: "Delegation on.", es: "Delegación activada.", fr: "Délégation activée.", de: "Delegation an.", pt: "Delegação ligada.", it: "Delega attiva.", ja: "委任をオンにしました。", zh: "委托已开启。", hi: "प्रत्यायोजन चालू।", ar: "فُعِّل التفويض.",
  },
  "dlg.off.said": {
    en: "Delegation off.", es: "Delegación desactivada.", fr: "Délégation désactivée.", de: "Delegation aus.", pt: "Delegação desligada.", it: "Delega disattivata.", ja: "委任をオフにしました。", zh: "委托已关闭。", hi: "प्रत्यायोजन बंद।", ar: "عُطِّل التفويض.",
  },
  "dlg.runs": {
    en: "Runs", es: "Ejecuciones", fr: "Exécutions", de: "Läufe", pt: "Execuções", it: "Esecuzioni", ja: "実行", zh: "运行", hi: "चलाए गए", ar: "التنفيذات",
  },
  "dlg.goal.ph": {
    en: "What should it work on?", es: "¿En qué debería trabajar?", fr: "Sur quoi doit-il travailler ?", de: "Woran soll es arbeiten?", pt: "Em que deve trabalhar?", it: "Su cosa deve lavorare?", ja: "何に取り組ませますか？", zh: "让它做什么？", hi: "इसे किस पर काम करना चाहिए?", ar: "على ماذا يعمل؟",
  },
  "dlg.start": {
    en: "Start", es: "Empezar", fr: "Lancer", de: "Starten", pt: "Começar", it: "Avvia", ja: "開始", zh: "开始", hi: "शुरू करें", ar: "ابدأ",
  },
  "dlg.started.said": {
    en: "Started.", es: "Iniciado.", fr: "Lancé.", de: "Gestartet.", pt: "Iniciado.", it: "Avviato.", ja: "開始しました。", zh: "已开始。", hi: "शुरू हो गया।", ar: "بدأ.",
  },
  "dlg.norun": {
    en: "Nothing has been run yet.", es: "Todavía no se ha ejecutado nada.", fr: "Rien n'a encore été exécuté.", de: "Es wurde noch nichts ausgeführt.", pt: "Ainda não foi executado nada.", it: "Non è ancora stato eseguito nulla.", ja: "まだ何も実行されていません。", zh: "还没有运行过任何东西。", hi: "अभी तक कुछ नहीं चलाया गया।", ar: "لم يُنفَّذ شيء بعد.",
  },
  "dlg.next": {
    en: "next: {phase}", es: "siguiente: {phase}", fr: "suivant : {phase}", de: "als Nächstes: {phase}", pt: "seguinte: {phase}", it: "prossimo: {phase}", ja: "次: {phase}", zh: "下一步：{phase}", hi: "अगला: {phase}", ar: "التالي: {phase}",
  },
  "dlg.waiting": {
    en: "Waiting on you: {what}", es: "A la espera de ti: {what}", fr: "En attente de vous : {what}", de: "Wartet auf Sie: {what}", pt: "À espera de si: {what}", it: "In attesa di te: {what}", ja: "あなた待ち: {what}", zh: "等你：{what}", hi: "आपकी प्रतीक्षा: {what}", ar: "في انتظارك: {what}",
  },
  "dlg.answer.ph": {
    en: "Your answer", es: "Tu respuesta", fr: "Votre réponse", de: "Ihre Antwort", pt: "A sua resposta", it: "La tua risposta", ja: "あなたの答え", zh: "你的回答", hi: "आपका उत्तर", ar: "إجابتك",
  },
  "dlg.answer": {
    en: "Answer & continue", es: "Responder y continuar", fr: "Répondre et continuer", de: "Antworten und fortfahren", pt: "Responder e continuar", it: "Rispondi e continua", ja: "答えて続ける", zh: "回答并继续", hi: "उत्तर दें और जारी रखें", ar: "أجب وتابع",
  },
  "dlg.resumed.said": {
    en: "Resumed.", es: "Reanudado.", fr: "Repris.", de: "Fortgesetzt.", pt: "Retomado.", it: "Ripreso.", ja: "再開しました。", zh: "已继续。", hi: "फिर शुरू।", ar: "استؤنف.",
  },
  "dlg.advance": {
    en: "Advance", es: "Avanzar", fr: "Avancer", de: "Weiter", pt: "Avançar", it: "Avanza", ja: "次へ進める", zh: "推进", hi: "आगे बढ़ाएँ", ar: "تقدّم",
  },
  "dlg.cancel": {
    en: "Cancel", es: "Cancelar", fr: "Annuler", de: "Abbrechen", pt: "Cancelar", it: "Annulla", ja: "中止", zh: "取消", hi: "रद्द करें", ar: "ألغِ",
  },
  "dlg.cancel.confirm": {
    en: "Cancel this run? What it has already done stays.", es: "¿Cancelar esta ejecución? Lo que ya ha hecho se queda.", fr: "Annuler cette exécution ? Ce qui a déjà été fait reste.", de: "Diesen Lauf abbrechen? Was bereits getan wurde, bleibt.", pt: "Cancelar esta execução? O que já foi feito fica.", it: "Annullare questa esecuzione? Ciò che ha già fatto resta.", ja: "この実行を中止しますか？すでに済んだことはそのまま残ります。", zh: "要取消这次运行吗？它已经做完的部分会保留。", hi: "क्या यह चलना रद्द करें? जो कर चुका है वह बना रहेगा।", ar: "إلغاء هذا التنفيذ؟ ما أنجزه فعلًا يبقى.",
  },
  "dlg.cancelled.said": {
    en: "Cancelled.", es: "Cancelado.", fr: "Annulé.", de: "Abgebrochen.", pt: "Cancelado.", it: "Annullato.", ja: "中止しました。", zh: "已取消。", hi: "रद्द कर दिया गया।", ar: "أُلغي.",
  },
  "dlg.oneoff": {
    en: "One-off tasks", es: "Tareas sueltas", fr: "Tâches ponctuelles", de: "Einzelaufgaben", pt: "Tarefas avulsas", it: "Compiti singoli", ja: "単発の作業", zh: "一次性任务", hi: "एकबारगी काम", ar: "مهام مفردة",
  },
  "dlg.oneoff.pitch": {
    en: "A single piece of work rather than a run with phases. It needs a grant, because it composes from the profile's own sources.", es: "Un solo trabajo en vez de una ejecución con fases. Necesita una concesión, porque compone a partir de las fuentes del propio perfil.", fr: "Un seul travail plutôt qu'une exécution en phases. Il faut une autorisation, car il compose à partir des sources du profil.", de: "Ein einzelnes Stück Arbeit statt eines Laufs mit Phasen. Es braucht eine Freigabe, weil es aus den eigenen Quellen des Profils zusammensetzt.", pt: "Um único trabalho em vez de uma execução com fases. Precisa de uma concessão, porque compõe a partir das fontes do próprio perfil.", it: "Un singolo lavoro invece di un'esecuzione a fasi. Serve una concessione, perché compone dalle fonti del profilo stesso.", ja: "段階に分かれた実行ではなく、ひとまとまりの作業です。プロフィール自身の資料から組み立てるため、許可が必要です。", zh: "这是单独一件工作，而不是分阶段的运行。它需要一份授权，因为它是从资料自身的素材中组织出来的。", hi: "चरणों वाले चलने के बजाय काम का एक टुकड़ा। इसे अनुदान चाहिए, क्योंकि यह प्रोफ़ाइल के अपने स्रोतों से रचता है।", ar: "قطعة عمل واحدة لا تنفيذًا بأطوار. تحتاج تصريحًا، لأنها تؤلّف من مصادر الملف نفسه.",
  },
  "dlg.topic.ph": {
    en: "Topic", es: "Tema", fr: "Sujet", de: "Thema", pt: "Tema", it: "Argomento", ja: "題材", zh: "主题", hi: "विषय", ar: "الموضوع",
  },
  "dlg.compose": {
    en: "Compose from my sources", es: "Componer desde mis fuentes", fr: "Composer à partir de mes sources", de: "Aus meinen Quellen zusammenstellen", pt: "Compor a partir das minhas fontes", it: "Componi dalle mie fonti", ja: "自分の資料から組み立てる", zh: "从我的素材中撰写", hi: "मेरे स्रोतों से रचें", ar: "ألّف من مصادري",
  },
  "dlg.done.said": {
    en: "Done.", es: "Hecho.", fr: "Fait.", de: "Erledigt.", pt: "Feito.", it: "Fatto.", ja: "完了しました。", zh: "完成。", hi: "हो गया।", ar: "تمّ.",
  },
  "dlg.mintfirst": {
    en: "Mint a grant first.", es: "Emite antes una concesión.", fr: "Créez d'abord une autorisation.", de: "Erzeugen Sie zuerst eine Freigabe.", pt: "Emita primeiro uma concessão.", it: "Prima conia una concessione.", ja: "先に許可を発行してください。", zh: "请先铸造一份授权。", hi: "पहले एक अनुदान बनाएँ।", ar: "أنشئ تصريحًا أولًا.",
  },
  "dlg.handed": {
    en: "Work you handed to somebody else's profile", es: "Trabajo que has encargado al perfil de otra persona", fr: "Le travail que vous avez confié au profil de quelqu'un d'autre", de: "Arbeit, die Sie dem Profil einer anderen Person übergeben haben", pt: "Trabalho que entregou ao perfil de outra pessoa", it: "Lavoro che hai affidato al profilo di qualcun altro", ja: "他人のプロフィールに手渡した仕事", zh: "你交给别人资料去做的工作", hi: "वह काम जो आपने किसी और की प्रोफ़ाइल को सौंपा", ar: "عمل سلّمته لملف شخص آخر",
  },
  "dlg.handed.pitch": {
    en: "The other side of the same policy. Everything above is what your own profile may do for you; this is you asking somebody else's to do something, inside the limits its owner published.", es: "La otra cara de la misma política. Todo lo de arriba es lo que tu propio perfil puede hacer por ti; esto es que tú le pidas al de otra persona que haga algo, dentro de los límites que publicó su propietario.", fr: "L'autre face de la même politique. Tout ce qui précède est ce que votre propre profil peut faire pour vous ; ici, c'est vous qui demandez à celui de quelqu'un d'autre de faire quelque chose, dans les limites publiées par son propriétaire.", de: "Die andere Seite derselben Richtlinie. Alles darüber ist, was Ihr eigenes Profil für Sie tun darf; hier bitten Sie das einer anderen Person, etwas zu tun — innerhalb der Grenzen, die deren Besitzer veröffentlicht hat.", pt: "O outro lado da mesma política. Tudo o que está acima é o que o seu próprio perfil pode fazer por si; isto é você a pedir ao de outra pessoa que faça algo, dentro dos limites que o proprietário dele publicou.", it: "L'altra faccia della stessa politica. Tutto quanto sopra è ciò che il tuo profilo può fare per te; questo sei tu che chiedi a quello di qualcun altro di fare qualcosa, entro i limiti pubblicati dal suo proprietario.", ja: "同じ方針のもう一方の側です。ここより上は、あなた自身のプロフィールがあなたのために何をしてよいかでした。こちらは、他人のプロフィールに何かを頼むこと — その所有者が公開した範囲の内側で。", zh: "同一套策略的另一面。上面写的是你自己的资料可以为你做什么；这里则是你请别人的资料去做某件事，在其所有者公开的限度之内。", hi: "उसी नीति का दूसरा पक्ष। ऊपर का सब कुछ यह है कि आपकी अपनी प्रोफ़ाइल आपके लिए क्या कर सकती है; यह वह है जहाँ आप किसी और की प्रोफ़ाइल से कुछ करने को कहते हैं — उन सीमाओं के भीतर जो उसके स्वामी ने प्रकाशित की हैं।", ar: "الوجه الآخر للسياسة نفسها. كل ما سبق هو ما يجوز لملفك أن يفعله من أجلك؛ وهذا أنت تطلب من ملف شخص آخر أن يفعل شيئًا، ضمن الحدود التي نشرها مالكه.",
  },
  "dlg.theirs.ph": {
    en: "their profile id", es: "el id de su perfil", fr: "l'id de leur profil", de: "dessen Profil-ID", pt: "o id do perfil deles", it: "l'id del loro profilo", ja: "相手のプロフィールID", zh: "对方的资料 ID", hi: "उनकी प्रोफ़ाइल की आईडी", ar: "معرّف ملفهم",
  },
  "dlg.whatwill": {
    en: "What will it take on?", es: "¿Qué aceptará hacer?", fr: "Que va-t-il accepter ?", de: "Was übernimmt es?", pt: "O que aceitará fazer?", it: "Cosa accetterà di fare?", ja: "何を引き受けますか？", zh: "它会承接什么？", hi: "यह क्या लेगा?", ar: "ماذا سيتولّى؟",
  },
  "dlg.accepts": {
    en: "Accepts delegated work: {phases}", es: "Acepta trabajo delegado: {phases}", fr: "Accepte du travail délégué : {phases}", de: "Nimmt delegierte Arbeit an: {phases}", pt: "Aceita trabalho delegado: {phases}", it: "Accetta lavoro delegato: {phases}", ja: "委任された仕事を受けます: {phases}", zh: "接受委托的工作：{phases}", hi: "प्रत्यायोजित काम स्वीकारता है: {phases}", ar: "يقبل عملًا مفوَّضًا: {phases}",
  },
  "dlg.accepts.not": {
    en: "Does not accept delegated work.", es: "No acepta trabajo delegado.", fr: "N'accepte pas de travail délégué.", de: "Nimmt keine delegierte Arbeit an.", pt: "Não aceita trabalho delegado.", it: "Non accetta lavoro delegato.", ja: "委任された仕事は受けません。", zh: "不接受委托的工作。", hi: "प्रत्यायोजित काम स्वीकार नहीं करता।", ar: "لا يقبل عملًا مفوَّضًا.",
  },
  "dlg.noscope.shown": {
    en: "Which sources its owner scoped is not shown, and is not yours to know.", es: "Qué fuentes acotó su propietario no se muestra, y no te corresponde saberlo.", fr: "Quelles sources son propriétaire a délimitées n'est pas affiché, et ne vous regarde pas.", de: "Welche Quellen sein Besitzer eingegrenzt hat, wird nicht gezeigt und geht Sie nichts an.", pt: "Quais fontes o proprietário delimitou não é mostrado, e não lhe compete saber.", it: "Quali fonti il suo proprietario abbia delimitato non viene mostrato, e non ti spetta saperlo.", ja: "その所有者がどの資料を範囲に入れたかは表示されませんし、あなたが知ってよいことでもありません。", zh: "其所有者圈定了哪些素材不会显示，也不是你该知道的。", hi: "उसके स्वामी ने कौन-से स्रोत दायरे में रखे, यह नहीं दिखाया जाता, और यह जानना आपका हक़ नहीं।", ar: "أي المصادر حدّدها مالكه لا يُعرض، وليس من شأنك أن تعرفه.",
  },
  "dlg.want.ph": {
    en: "what you want done", es: "qué quieres que se haga", fr: "ce que vous voulez faire faire", de: "was erledigt werden soll", pt: "o que quer que seja feito", it: "cosa vuoi che venga fatto", ja: "してほしいこと", zh: "你想让它做什么", hi: "आप क्या करवाना चाहते हैं", ar: "ما تريد إنجازه",
  },
  "dlg.handover": {
    en: "Hand it over", es: "Encargarlo", fr: "Le confier", de: "Übergeben", pt: "Entregar", it: "Affidalo", ja: "手渡す", zh: "交出去", hi: "सौंप दें", ar: "سلّمه",
  },
  "dlg.talking": {
    en: "You have to be talking to it already — delegated work is for somebody in a conversation, not a stranger holding a profile id, and starting one cold is refused by name.", es: "Tienes que estar ya hablando con él — el trabajo delegado es para alguien que está en una conversación, no para un desconocido con un id de perfil, y arrancar uno en frío se rechaza con su nombre.", fr: "Vous devez déjà être en train de lui parler — le travail délégué est pour quelqu'un dans une conversation, pas pour un inconnu tenant un id de profil, et en démarrer un à froid est refusé nommément.", de: "Sie müssen bereits mit ihm sprechen — delegierte Arbeit ist für jemanden in einem Gespräch, nicht für eine fremde Person mit einer Profil-ID, und einen kalten Start lehnt es namentlich ab.", pt: "Já tem de estar a falar com ele — o trabalho delegado é para alguém numa conversa, não para um desconhecido com um id de perfil, e começar um a frio é recusado pelo nome.", it: "Devi già starci parlando — il lavoro delegato è per qualcuno dentro una conversazione, non per uno sconosciuto con un id di profilo, e avviarne uno a freddo viene rifiutato per nome.", ja: "すでに会話していることが前提です — 委任された仕事は会話の中にいる人のためのもので、プロフィールIDを持っているだけの見知らぬ人のためではありません。何もないところから始めようとすると、その理由を名指しして拒否されます。", zh: "你必须已经在跟它对话——委托的工作是给对话中的人的，而不是给一个只握着资料 ID 的陌生人；冷启动会被指名拒绝。", hi: "आपका उससे पहले से बात करते होना ज़रूरी है — प्रत्यायोजित काम बातचीत में मौजूद किसी व्यक्ति के लिए है, प्रोफ़ाइल आईडी थामे किसी अजनबी के लिए नहीं, और ठंडे-ठंडे शुरू करने पर नाम लेकर इनकार होता है।", ar: "عليك أن تكون تحادثه أصلًا — العمل المفوَّض لمن هو داخل محادثة، لا لغريب يحمل معرّف ملف، وبدؤه على البارد مرفوض بالاسم.",
  },
  "dlg.handed.line": {
    en: "{id} — {status}", es: "{id} — {status}", fr: "{id} — {status}", de: "{id} — {status}", pt: "{id} — {status}", it: "{id} — {status}", ja: "{id} — {status}", zh: "{id} — {status}", hi: "{id} — {status}", ar: "{id} — {status}",
  },
  "dlg.handed.next": {
    en: " · next: {phase}", es: " · siguiente: {phase}", fr: " · suivant : {phase}", de: " · als Nächstes: {phase}", pt: " · seguinte: {phase}", it: " · prossimo: {phase}", ja: " · 次: {phase}", zh: " · 下一步：{phase}", hi: " · अगला: {phase}", ar: " · التالي: {phase}",
  },
  "dlg.handed.waiting": {
    en: " · waiting on you: {what}", es: " · a la espera de ti: {what}", fr: " · en attente de vous : {what}", de: " · wartet auf Sie: {what}", pt: " · à espera de si: {what}", it: " · in attesa di te: {what}", ja: " · あなた待ち: {what}", zh: " · 等你：{what}", hi: " · आपकी प्रतीक्षा: {what}", ar: " · في انتظارك: {what}",
  },
  "dlg.nextphase": {
    en: "Run the next phase", es: "Ejecutar la siguiente fase", fr: "Exécuter la phase suivante", de: "Nächste Phase ausführen", pt: "Executar a fase seguinte", it: "Esegui la fase successiva", ja: "次の段階を実行", zh: "运行下一阶段", hi: "अगला चरण चलाएँ", ar: "نفّذ الطور التالي",
  },
  "dlg.refresh": {
    en: "Refresh", es: "Actualizar", fr: "Actualiser", de: "Aktualisieren", pt: "Atualizar", it: "Aggiorna", ja: "更新", zh: "刷新", hi: "ताज़ा करें", ar: "حدّث",
  },
  "dlg.answerit.ph": {
    en: "answer it, if it stopped to ask", es: "respóndele, si se paró a preguntar", fr: "répondez-lui, s'il s'est arrêté pour demander", de: "antworten Sie, falls es zum Fragen angehalten hat", pt: "responda-lhe, se parou para perguntar", it: "rispondigli, se si è fermato per chiedere", ja: "尋ねるために止まっていたら、答える", zh: "如果它停下来提问，就回答它", hi: "यदि यह पूछने के लिए रुका है तो उत्तर दें", ar: "أجبه، إن توقف ليسأل",
  },
  "dlg.answercont": {
    en: "Answer and continue", es: "Responder y continuar", fr: "Répondre et continuer", de: "Antworten und fortfahren", pt: "Responder e continuar", it: "Rispondi e continua", ja: "答えて続ける", zh: "回答并继续", hi: "उत्तर दें और जारी रखें", ar: "أجب وتابع",
  },
  "bcn.title": {
    en: "Where people find you", es: "Dónde te encuentra la gente", fr: "Où les gens vous trouvent", de: "Wo Leute Sie finden", pt: "Onde as pessoas o encontram", it: "Dove la gente ti trova", ja: "人があなたを見つける場所", zh: "别人在哪里找到你", hi: "लोग आपको कहाँ पाते हैं", ar: "أين يجدك الناس",
  },
  "bcn.here": {
    en: "here", es: "aquí", fr: "ici", de: "hierher", pt: "aqui", it: "qui", ja: "ここ", zh: "这里", hi: "यहाँ", ar: "هنا",
  },
  "bcn.lead": {
    en: "Two kinds of code, and they look the same. A placed beacon brings somebody {here}; a platform beacon sends them to an account somewhere else.", es: "Dos clases de código, y se ven iguales. Una baliza colocada trae a alguien {here}; una baliza de plataforma lo manda a una cuenta en otro sitio.", fr: "Deux sortes de code, et elles se ressemblent. Une balise posée amène quelqu'un {here} ; une balise de plateforme l'envoie vers un compte ailleurs.", de: "Zwei Arten von Code, und sie sehen gleich aus. Eine angebrachte Bake bringt jemanden {here}; eine Plattform-Bake schickt ihn zu einem Konto woanders.", pt: "Dois tipos de código, e parecem iguais. Uma baliza colocada traz alguém {here}; uma baliza de plataforma manda-o para uma conta noutro sítio.", it: "Due tipi di codice, e sembrano uguali. Un beacon posato porta qualcuno {here}; un beacon di piattaforma lo manda a un account altrove.", ja: "コードは二種類あり、見た目は同じです。設置したビーコンは人を{here}へ連れてきます。プラットフォームのビーコンは、よそにある別のアカウントへ送り出します。", zh: "有两种码，长得一模一样。放置的信标把人带到{here}；平台信标则把他们送往别处的某个账户。", hi: "दो तरह के कोड, और दोनों एक जैसे दिखते हैं। रखा हुआ बीकन किसी को {here} लाता है; प्लेटफ़ॉर्म बीकन उन्हें कहीं और के किसी खाते तक भेज देता है।", ar: "نوعان من الرموز، وشكلهما واحد. المنارة الموضوعة تجلب أحدهم إلى {here}؛ ومنارة المنصة ترسله إلى حساب في مكان آخر.",
  },
  "bcn.connect": {
    en: "Connect a platform", es: "Conectar una plataforma", fr: "Connecter une plateforme", de: "Eine Plattform verbinden", pt: "Ligar uma plataforma", it: "Collega una piattaforma", ja: "プラットフォームをつなぐ", zh: "连接一个平台", hi: "कोई प्लेटफ़ॉर्म जोड़ें", ar: "اربط منصة",
  },
  "bcn.collect": {
    en: "Collect", es: "Recoger", fr: "Collecter", de: "Sammeln", pt: "Recolher", it: "Raccogli", ja: "取り込み", zh: "收集", hi: "संग्रह", ar: "التجميع",
  },
  "bcn.publish": {
    en: "Publish", es: "Publicar", fr: "Publier", de: "Veröffentlichen", pt: "Publicar", it: "Pubblica", ja: "発信", zh: "发布", hi: "प्रकाशन", ar: "النشر",
  },
  "bcn.directions": {
    en: "Two directions, never the same row. {collect} pulls that account's content in to grow this profile. {publish} runs the profile out on the platform. Kept apart so a read-only import can never also post.", es: "Dos direcciones, nunca en la misma fila. {collect} trae el contenido de esa cuenta para hacer crecer este perfil. {publish} saca el perfil a la plataforma. Se mantienen separadas para que una importación de solo lectura no pueda además publicar.", fr: "Deux directions, jamais sur la même ligne. {collect} tire le contenu de ce compte pour faire grandir ce profil. {publish} fait sortir le profil sur la plateforme. Séparées, pour qu'un import en lecture seule ne puisse jamais aussi publier.", de: "Zwei Richtungen, nie in derselben Zeile. {collect} zieht die Inhalte jenes Kontos herein, um dieses Profil wachsen zu lassen. {publish} bringt das Profil auf der Plattform hinaus. Getrennt gehalten, damit ein Nur-Lese-Import nie auch posten kann.", pt: "Duas direções, nunca na mesma linha. {collect} puxa o conteúdo dessa conta para fazer crescer este perfil. {publish} leva o perfil para fora, na plataforma. Mantidas separadas para que uma importação só de leitura nunca possa também publicar.", it: "Due direzioni, mai sulla stessa riga. {collect} tira dentro i contenuti di quell'account per far crescere questo profilo. {publish} porta il profilo fuori sulla piattaforma. Tenute separate perché un'importazione in sola lettura non possa mai anche pubblicare.", ja: "向きは二つあり、同じ行に同居することはありません。{collect} は、そのアカウントの内容を取り込んでこのプロフィールを育てます。{publish} は、プロフィールをそのプラットフォームへ送り出します。読み取り専用の取り込みが投稿までできてしまわないよう、分けてあります。", zh: "两个方向，永不共处一行。{collect} 把那个账户的内容拉进来，用以充实这份资料。{publish} 则把资料发到那个平台上去。二者分开，好让只读的导入永远不可能同时发帖。", hi: "दो दिशाएँ, कभी एक ही पंक्ति में नहीं। {collect} उस खाते की सामग्री खींचकर इस प्रोफ़ाइल को बढ़ाता है। {publish} प्रोफ़ाइल को उस प्लेटफ़ॉर्म पर बाहर चलाता है। इन्हें अलग रखा गया है ताकि केवल-पढ़ने वाला आयात कभी पोस्ट भी न कर सके।", ar: "اتجاهان، ولا يجتمعان في صف واحد أبدًا. {collect} يسحب محتوى ذلك الحساب لينمو هذا الملف. و{publish} يُخرج الملف على المنصة. فُصلا كي لا يستطيع استيراد للقراءة فقط أن ينشر أيضًا.",
  },
  "bcn.opt.publish": {
    en: "publish — run it out there", es: "publicar — sacarlo ahí fuera", fr: "publier — le faire sortir", de: "veröffentlichen — hinausbringen", pt: "publicar — levá-lo lá para fora", it: "pubblica — portalo là fuori", ja: "発信 — 外へ送り出す", zh: "发布 — 把它发到外面去", hi: "प्रकाशन — इसे बाहर चलाएँ", ar: "انشر — أخرِجه إلى هناك",
  },
  "bcn.opt.collect": {
    en: "collect — pull it in", es: "recoger — traerlo aquí", fr: "collecter — le faire entrer", de: "sammeln — hereinholen", pt: "recolher — trazê-lo para dentro", it: "raccogli — tiralo dentro", ja: "取り込み — 中へ引き入れる", zh: "收集 — 把它拉进来", hi: "संग्रह — इसे भीतर खींचें", ar: "اجمع — اسحبه إلى الداخل",
  },
  "bcn.handle.ph": {
    en: "the handle, without the @", es: "el alias, sin la @", fr: "l'identifiant, sans le @", de: "der Handle, ohne das @", pt: "o identificador, sem o @", it: "l'handle, senza la @", ja: "ハンドル名（@ なし）", zh: "用户名，不带 @", hi: "हैंडल, @ के बिना", ar: "المعرّف، دون @",
  },
  "bcn.connectbtn": {
    en: "Connect", es: "Conectar", fr: "Connecter", de: "Verbinden", pt: "Ligar", it: "Collega", ja: "つなぐ", zh: "连接", hi: "जोड़ें", ar: "اربط",
  },
  "bcn.connected.said": {
    en: "Connected.", es: "Conectado.", fr: "Connecté.", de: "Verbunden.", pt: "Ligado.", it: "Collegato.", ja: "つながりました。", zh: "已连接。", hi: "जुड़ गया।", ar: "تمّ الربط.",
  },
  "bcn.nohandle": {
    en: "Without a handle the beacon has no account page to point at, so it falls back to a QRME summon link — still a working code, but it brings people here rather than to the platform.", es: "Sin alias, la baliza no tiene página de cuenta a la que apuntar, así que recae en un enlace de invocación de QRME — sigue siendo un código que funciona, pero trae a la gente aquí en vez de a la plataforma.", fr: "Sans identifiant, la balise n'a aucune page de compte à viser, elle retombe donc sur un lien d'appel QRME — un code qui marche toujours, mais qui amène les gens ici plutôt que sur la plateforme.", de: "Ohne Handle hat die Bake keine Kontoseite, auf die sie zeigen könnte, also fällt sie auf einen QRME-Summon-Link zurück — immer noch ein funktionierender Code, aber er bringt Leute hierher statt auf die Plattform.", pt: "Sem identificador, a baliza não tem página de conta para apontar, por isso recai num link de invocação do QRME — continua a ser um código que funciona, mas traz as pessoas para aqui e não para a plataforma.", it: "Senza handle il beacon non ha una pagina di account da puntare, quindi ripiega su un link di richiamo QRME — resta un codice funzionante, ma porta la gente qui invece che sulla piattaforma.", ja: "ハンドル名がなければ、ビーコンが指すべきアカウントのページがないため、QRME の呼び出しリンクに戻ります — 依然として機能するコードですが、人をプラットフォームではなくこちらへ連れてきます。", zh: "没有用户名，信标就没有可指向的账户页面，于是退回到 QRME 的召唤链接——仍是一个能用的码，但它把人带到这里，而不是那个平台。", hi: "हैंडल के बिना बीकन के पास इशारा करने को कोई खाता-पृष्ठ नहीं होता, इसलिए यह QRME के समन लिंक पर लौट आता है — कोड फिर भी काम करता है, पर लोगों को प्लेटफ़ॉर्म पर नहीं, यहाँ लाता है।", ar: "بلا معرّف لا تجد المنارة صفحة حساب تشير إليها، فترتدّ إلى رابط استدعاء في QRME — ويظل رمزًا عاملًا، لكنه يجلب الناس إلى هنا لا إلى المنصة.",
  },
  "bcn.connectedhdr": {
    en: "Connected", es: "Conectadas", fr: "Connectées", de: "Verbunden", pt: "Ligadas", it: "Collegate", ja: "接続済み", zh: "已连接", hi: "जुड़े हुए", ar: "المرتبطة",
  },
  "bcn.none": {
    en: "Nothing yet.", es: "Nada todavía.", fr: "Rien pour l'instant.", de: "Noch nichts.", pt: "Nada ainda.", it: "Ancora niente.", ja: "まだ何もありません。", zh: "尚无。", hi: "अभी कुछ नहीं।", ar: "لا شيء بعد.",
  },
  "bcn.counts": {
    en: "{collected} collected · {published} published", es: "{collected} recogidos · {published} publicados", fr: "{collected} collectés · {published} publiés", de: "{collected} gesammelt · {published} veröffentlicht", pt: "{collected} recolhidos · {published} publicados", it: "{collected} raccolti · {published} pubblicati", ja: "取り込み {collected}件 · 発信 {published}件", zh: "已收集 {collected} · 已发布 {published}", hi: "{collected} संग्रहित · {published} प्रकाशित", ar: "{collected} مجموعة · {published} منشورة",
  },
  "bcn.showcode": {
    en: "show its code", es: "mostrar su código", fr: "afficher son code", de: "seinen Code zeigen", pt: "mostrar o seu código", it: "mostra il suo codice", ja: "そのコードを表示", zh: "显示它的码", hi: "इसका कोड दिखाएँ", ar: "أظهر رمزه",
  },
  "bcn.disconnect": {
    en: "disconnect", es: "desconectar", fr: "déconnecter", de: "trennen", pt: "desligar", it: "scollega", ja: "切断", zh: "断开", hi: "अलग करें", ar: "افصل",
  },
  "bcn.disconnected.said": {
    en: "Disconnected.", es: "Desconectado.", fr: "Déconnecté.", de: "Getrennt.", pt: "Desligado.", it: "Scollegato.", ja: "切断しました。", zh: "已断开。", hi: "अलग कर दिया गया।", ar: "فُصل.",
  },
  "bcn.codefor": {
    en: "The code for {platform}", es: "El código de {platform}", fr: "Le code pour {platform}", de: "Der Code für {platform}", pt: "O código de {platform}", it: "Il codice per {platform}", ja: "{platform} 用のコード", zh: "{platform} 的码", hi: "{platform} के लिए कोड", ar: "رمز {platform}",
  },
  "bcn.qralt": {
    en: "the QR code for this platform presence", es: "el código QR de esta presencia en la plataforma", fr: "le QR code de cette présence sur la plateforme", de: "der QR-Code für diese Plattform-Präsenz", pt: "o código QR desta presença na plataforma", it: "il codice QR di questa presenza sulla piattaforma", ja: "このプラットフォーム上の存在を指す QR コード", zh: "此平台身份的二维码", hi: "इस प्लेटफ़ॉर्म उपस्थिति का QR कोड", ar: "رمز الاستجابة السريعة لهذا الحضور على المنصة",
  },
  "bcn.opens": {
    en: "Scanning it opens {url}", es: "Escanearlo abre {url}", fr: "Le scanner ouvre {url}", de: "Das Scannen öffnet {url}", pt: "Digitalizá-lo abre {url}", it: "Scansionarlo apre {url}", ja: "スキャンすると {url} が開きます", zh: "扫描它会打开 {url}", hi: "इसे स्कैन करने पर {url} खुलता है", ar: "مسحه يفتح {url}",
  },
  "bcn.opens.handle": {
    en: " — {handle} on {platform}.", es: " — {handle} en {platform}.", fr: " — {handle} sur {platform}.", de: " — {handle} auf {platform}.", pt: " — {handle} em {platform}.", it: " — {handle} su {platform}.", ja: " — {platform} の {handle}。", zh: " — {platform} 上的 {handle}。", hi: " — {platform} पर {handle}।", ar: " — {handle} على {platform}.",
  },
  "bcn.opens.summon": {
    en: " — a QRME summon page, because this connection has no handle to build a platform link from.", es: " — una página de invocación de QRME, porque esta conexión no tiene alias con el que construir un enlace a la plataforma.", fr: " — une page d'appel QRME, car cette connexion n'a pas d'identifiant permettant de construire un lien vers la plateforme.", de: " — eine QRME-Summon-Seite, weil diese Verbindung keinen Handle hat, aus dem sich ein Plattform-Link bauen ließe.", pt: " — uma página de invocação do QRME, porque esta ligação não tem identificador com que construir um link para a plataforma.", it: " — una pagina di richiamo QRME, perché questa connessione non ha un handle con cui costruire un link alla piattaforma.", ja: " — QRME の呼び出しページです。この接続には、プラットフォームへのリンクを組み立てられるハンドル名がないからです。", zh: " — 一个 QRME 召唤页面，因为这个连接没有可用来构造平台链接的用户名。", hi: " — एक QRME समन पृष्ठ, क्योंकि इस कनेक्शन के पास ऐसा हैंडल नहीं जिससे प्लेटफ़ॉर्म लिंक बनाया जा सके।", ar: " — صفحة استدعاء في QRME، لأن هذا الارتباط بلا معرّف يُبنى منه رابط إلى المنصة.",
  },
  "bcn.away": {
    en: "away", es: "fuera", fr: "ailleurs", de: "weg", pt: "para fora", it: "via", ja: "外へ", zh: "离开", hi: "दूर", ar: "بعيدًا",
  },
  "bcn.carries": {
    en: "This code carries people {away} from QRME. A placed beacon does the opposite. Same picture, opposite destination.", es: "Este código lleva a la gente {away} de QRME. Una baliza colocada hace lo contrario. Misma imagen, destino opuesto.", fr: "Ce code emmène les gens {away} de QRME. Une balise posée fait l'inverse. Même image, destination opposée.", de: "Dieser Code trägt Leute {away} von QRME. Eine angebrachte Bake tut das Gegenteil. Dasselbe Bild, entgegengesetztes Ziel.", pt: "Este código leva as pessoas {away} do QRME. Uma baliza colocada faz o contrário. Mesma imagem, destino oposto.", it: "Questo codice porta la gente {away} da QRME. Un beacon posato fa l'opposto. Stessa immagine, destinazione opposta.", ja: "このコードは人を QRME から{away}運び出します。設置したビーコンはその逆をします。同じ絵で、行き先が逆です。", zh: "这个码把人从 QRME 带{away}。放置的信标做的正相反。同样的图，相反的去处。", hi: "यह कोड लोगों को QRME से {away} ले जाता है। रखा हुआ बीकन इसका उलटा करता है। तस्वीर वही, मंज़िल उलटी।", ar: "هذا الرمز يحمل الناس {away} عن QRME. والمنارة الموضوعة تفعل العكس. الصورة ذاتها، والوجهة معاكسة.",
  },
  "bcn.cost": {
    en: "What a scan costs to check", es: "Lo que cuesta comprobar un escaneo", fr: "Ce que coûte la vérification d'un scan", de: "Was es kostet, einen Scan zu prüfen", pt: "O que custa verificar uma digitalização", it: "Quanto costa controllare una scansione", ja: "スキャンを確かめる代償", zh: "查一次扫描要付出什么", hi: "स्कैन जाँचने की क़ीमत", ar: "ما يكلّفه التحقق من مسحة",
  },
  "bcn.is": {
    en: "is", es: "sí lo es", fr: "en est un", de: "ist einer", pt: "é", it: "lo è", ja: "そうです", zh: "就是", hi: "है", ar: "نعم",
  },
  "bcn.cost.pitch": {
    en: "A QR image is free to ask for — fetching the picture is not a scan. Opening the page it points to {is} one, and every scan surface counts it, because the server cannot tell an owner checking their own sticker from a stranger who found it. There is no preview that doesn't count.", es: "Pedir una imagen QR es gratis — traer la imagen no es un escaneo. Abrir la página a la que apunta {is} uno, y todas las superficies de escaneo lo cuentan, porque el servidor no puede distinguir a un propietario comprobando su propia pegatina de un desconocido que la encontró. No hay vista previa que no cuente.", fr: "Demander une image QR est gratuit — récupérer l'image n'est pas un scan. Ouvrir la page vers laquelle elle pointe {is}, et toutes les surfaces de scan le comptent, car le serveur ne peut distinguer un propriétaire vérifiant son propre autocollant d'un inconnu qui l'a trouvé. Il n'existe aucun aperçu qui ne compte pas.", de: "Ein QR-Bild anzufordern ist frei — das Bild zu holen ist kein Scan. Die Seite zu öffnen, auf die es zeigt, {is} einer, und jede Scan-Oberfläche zählt ihn, denn der Server kann einen Besitzer, der seinen eigenen Aufkleber prüft, nicht von einer fremden Person unterscheiden, die ihn gefunden hat. Es gibt keine Vorschau, die nicht zählt.", pt: "Pedir uma imagem QR é grátis — obter a imagem não é uma digitalização. Abrir a página para que ela aponta {is} uma, e todas as superfícies de digitalização a contam, porque o servidor não consegue distinguir um proprietário a verificar o seu próprio autocolante de um desconhecido que o encontrou. Não há pré-visualização que não conte.", it: "Chiedere un'immagine QR è gratis — recuperare l'immagine non è una scansione. Aprire la pagina a cui punta {is} una, e ogni superficie di scansione la conta, perché il server non sa distinguere un proprietario che controlla il proprio adesivo da uno sconosciuto che l'ha trovato. Non esiste anteprima che non conti.", ja: "QR 画像を求めること自体は無料です — 画像を取得してもスキャンにはなりません。その指す先のページを開くこと{is}スキャンで、どのスキャン面もそれを数えます。自分のステッカーを確かめている所有者と、それを見つけた見知らぬ人とを、サーバーは区別できないからです。数えられないプレビューというものはありません。", zh: "索取二维码图片是免费的——取图不算一次扫描。打开它所指向的页面{is}一次扫描，而且每一个扫描入口都会计数，因为服务器无法分辨是所有者在查看自己的贴纸，还是陌生人发现了它。不存在不计数的预览。", hi: "QR छवि माँगना मुफ़्त है — तस्वीर लाना स्कैन नहीं। यह जिस पृष्ठ की ओर इशारा करता है उसे खोलना {is} एक स्कैन, और हर स्कैन सतह उसे गिनती है, क्योंकि सर्वर यह नहीं बता सकता कि अपना ही स्टिकर जाँचता स्वामी है या उसे पाने वाला कोई अजनबी। ऐसा कोई पूर्वावलोकन नहीं जो न गिना जाए।", ar: "طلب صورة الرمز مجاني — وجلب الصورة ليس مسحة. أما فتح الصفحة التي يشير إليها ف{is} مسحة، وكل سطح مسح يحصيها، لأن الخادم لا يميّز مالكًا يتفقّد ملصقه من غريب عثر عليه. ولا توجد معاينة لا تُحسب.",
  },
  "bcn.placements": {
    en: "Placements", es: "Colocaciones", fr: "Placements", de: "Platzierungen", pt: "Colocações", it: "Collocamenti", ja: "掲載", zh: "投放", hi: "प्लेसमेंट", ar: "المواضع",
  },
  "bcn.cost.links": {
    en: "So no screen here opens a scan page on its own. The links on {placements} and on a desk are deliberate presses, and following one adds to the number you were checking. The desk code also has a JSON twin — the same scan shaped for a native app drawing the overlay in place rather than for a browser — and it counts the same.", es: "Así que ninguna pantalla de aquí abre por su cuenta una página de escaneo. Los enlaces de {placements} y los de un mostrador son pulsaciones deliberadas, y seguir uno suma al número que estabas comprobando. El código del mostrador tiene además un gemelo JSON — el mismo escaneo con la forma que necesita una app nativa que dibuja la superposición en el sitio, en vez de un navegador — y cuenta igual.", fr: "Aucun écran ici n'ouvre donc de page de scan de lui-même. Les liens sur {placements} et sur un comptoir sont des pressions délibérées, et en suivre un ajoute au nombre que vous vérifiiez. Le code de comptoir a aussi un jumeau JSON — le même scan mis en forme pour une application native qui dessine la surimpression sur place plutôt que pour un navigateur — et il compte pareil.", de: "Deshalb öffnet hier kein Bildschirm von sich aus eine Scan-Seite. Die Links auf {placements} und an einem Tresen sind bewusste Klicks, und einem zu folgen erhöht genau die Zahl, die Sie geprüft haben. Der Tresen-Code hat außerdem einen JSON-Zwilling — derselbe Scan, geformt für eine native App, die die Überlagerung vor Ort zeichnet, statt für einen Browser — und er zählt genauso.", pt: "Por isso nenhum ecrã aqui abre uma página de digitalização por si próprio. As ligações em {placements} e num balcão são pressões deliberadas, e seguir uma acrescenta ao número que estava a verificar. O código do balcão tem ainda um gémeo JSON — a mesma digitalização com a forma de que precisa uma app nativa que desenha a sobreposição no local, em vez de um navegador — e conta igual.", it: "Perciò nessuna schermata qui apre da sola una pagina di scansione. I link su {placements} e su un banco sono pressioni deliberate, e seguirne uno si aggiunge al numero che stavi controllando. Il codice del banco ha anche un gemello JSON — la stessa scansione modellata per un'app nativa che disegna la sovrapposizione sul posto anziché per un browser — e conta allo stesso modo.", ja: "ですから、ここのどの画面も自分からスキャンのページを開いたりはしません。{placements} 上やデスク上のリンクは、意図して押すものであり、たどればまさにあなたが確かめていた数を増やします。デスクのコードには JSON の双子もあります — ブラウザ向けではなく、その場でオーバーレイを描くネイティブアプリ向けに形を整えた同じスキャンです — こちらも同じように数えられます。", zh: "所以这里没有任何页面会自行打开扫描页。{placements} 上和柜台上的链接都是有意的点击，点进去就会给你正在核对的那个数字加一。柜台的码还有一个 JSON 孪生体——同一次扫描，只是为就地绘制叠加层的原生应用而非浏览器塑形——它同样计数。", hi: "इसलिए यहाँ कोई स्क्रीन अपने आप स्कैन पृष्ठ नहीं खोलती। {placements} पर और किसी डेस्क पर मौजूद लिंक जान-बूझकर दबाए जाते हैं, और एक पर जाना उसी संख्या में जुड़ जाता है जिसे आप जाँच रहे थे। डेस्क कोड का एक JSON जुड़वाँ भी है — वही स्कैन, ब्राउज़र के लिए नहीं बल्कि उस नेटिव ऐप के लिए ढला जो ओवरले वहीं बनाता है — और वह भी उसी तरह गिना जाता है।", ar: "لذا لا تفتح أي شاشة هنا صفحة مسح من تلقاء نفسها. الروابط في {placements} وعلى مكتب ما ضغطات مقصودة، واتّباع أحدها يضيف إلى الرقم الذي كنت تتفقّده. ولرمز المكتب توأم بصيغة JSON — المسحة نفسها مصوغة لتطبيق أصلي يرسم الطبقة في مكانها لا لمتصفح — ويُحسب بالمثل.",
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
