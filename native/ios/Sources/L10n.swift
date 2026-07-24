import Foundation

/// App-chrome localization: tab names, screen titles, and the most common
/// actions, in every language the backend supports. Content (chat, guidance,
/// persona text) is localized server-side by the profile's language setting;
/// this table covers the frame around it. Missing keys fall back to English.
enum L10n {
    static func t(_ key: String, _ lang: String) -> String {
        table[key]?[lang] ?? table[key]?["en"] ?? key
    }

    private static let table: [String: [String: String]] = [
        "tab.overview": ["en": "Overview", "es": "Resumen", "fr": "Aperçu",
                         "de": "Übersicht", "pt": "Visão geral", "it": "Panoramica",
                         "ja": "概要", "zh": "概览", "hi": "अवलोकन", "ar": "نظرة عامة"],
        "tab.chat": ["en": "Chat", "es": "Chat", "fr": "Discussion",
                     "de": "Chat", "pt": "Conversa", "it": "Chat",
                     "ja": "チャット", "zh": "聊天", "hi": "चैट", "ar": "محادثة"],
        "tab.studio": ["en": "Studio", "es": "Estudio", "fr": "Studio",
                       "de": "Studio", "pt": "Estúdio", "it": "Studio",
                       "ja": "スタジオ", "zh": "工作室", "hi": "स्टूडियो", "ar": "الاستوديو"],
        "tab.connect": ["en": "Connect", "es": "Conectar", "fr": "Connecter",
                        "de": "Verbinden", "pt": "Conectar", "it": "Connetti",
                        "ja": "接続", "zh": "连接", "hi": "कनेक्ट", "ar": "اتصال"],
        "tab.manage": ["en": "Manage", "es": "Gestionar", "fr": "Gérer",
                       "de": "Verwalten", "pt": "Gerenciar", "it": "Gestisci",
                       "ja": "管理", "zh": "管理", "hi": "प्रबंधन", "ar": "إدارة"],
        "tab.community": ["en": "Community", "es": "Comunidad", "fr": "Communauté",
                          "de": "Community", "pt": "Comunidade", "it": "Comunità",
                          "ja": "コミュニティ", "zh": "社区", "hi": "समुदाय", "ar": "مجتمع"],
        "tab.compose": ["en": "Compose", "es": "Redactar", "fr": "Composer",
                        "de": "Verfassen", "pt": "Compor", "it": "Componi",
                        "ja": "作成", "zh": "撰写", "hi": "लिखें", "ar": "إنشاء"],
        "tab.posts": ["en": "Posts", "es": "Publicaciones", "fr": "Publications",
                      "de": "Beiträge", "pt": "Publicações", "it": "Post",
                      "ja": "投稿", "zh": "帖子", "hi": "पोस्ट", "ar": "منشورات"],
        "tab.study": ["en": "Study", "es": "Estudiar", "fr": "Étude",
                      "de": "Studie", "pt": "Estudo", "it": "Studiare",
                      "ja": "学習", "zh": "学习", "hi": "अध्ययन", "ar": "دراسة"],
        "tab.gaming": ["en": "Gaming", "es": "Juegos", "fr": "Jeux",
                       "de": "Gaming", "pt": "Jogos", "it": "Gaming",
                       "ja": "ゲーム", "zh": "游戏", "hi": "गेमिंग", "ar": "ألعاب"],
        "tab.robots": ["en": "Robots", "es": "Robots", "fr": "Robots",
                       "de": "Roboter", "pt": "Robôs", "it": "Robot",
                       "ja": "ロボット", "zh": "机器人", "hi": "रोबोट", "ar": "روبوتات"],
        "tab.reach": ["en": "Reach", "es": "Alcance", "fr": "Portée",
                      "de": "Reichweite", "pt": "Alcance", "it": "Portata",
                      "ja": "リーチ", "zh": "触达", "hi": "पहुंच", "ar": "انتشار"],
        "tab.settings": ["en": "Settings", "es": "Ajustes", "fr": "Réglages",
                         "de": "Einstellungen", "pt": "Configurações", "it": "Impostazioni",
                         "ja": "設定", "zh": "设置", "hi": "सेटिंग्स", "ar": "الإعدادات"],
        "action.send": ["en": "Send", "es": "Enviar", "fr": "Envoyer",
                        "de": "Senden", "pt": "Enviar", "it": "Invia",
                        "ja": "送信", "zh": "发送", "hi": "भेजें", "ar": "إرسال"],
        "action.save": ["en": "Save", "es": "Guardar", "fr": "Enregistrer",
                        "de": "Speichern", "pt": "Salvar", "it": "Salva",
                        "ja": "保存", "zh": "保存", "hi": "सहेजें", "ar": "حفظ"],
        "action.translate": ["en": "Translate", "es": "Traducir", "fr": "Traduire",
                             "de": "Übersetzen", "pt": "Traduzir", "it": "Traduci",
                             "ja": "翻訳", "zh": "翻译", "hi": "अनुवाद", "ar": "ترجمة"],
        "action.sign_out": ["en": "Sign out", "es": "Cerrar sesión", "fr": "Se déconnecter",
                            "de": "Abmelden", "pt": "Sair", "it": "Esci",
                            "ja": "サインアウト", "zh": "退出登录", "hi": "साइन आउट",
                            "ar": "تسجيل الخروج"],
        "action.refresh": ["en": "Refresh", "es": "Actualizar", "fr": "Actualiser",
                           "de": "Aktualisieren", "pt": "Atualizar", "it": "Aggiorna",
                           "ja": "更新", "zh": "刷新", "hi": "रीफ़्रेश", "ar": "تحديث"],
    ]
}
