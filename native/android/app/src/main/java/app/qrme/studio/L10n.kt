package app.qrme.studio

/**
 * App-chrome localization: tab names, screen titles, and the most common
 * actions, in every language the backend supports. Content (chat, guidance,
 * persona text) is localized server-side by the profile's language setting;
 * this table covers the frame around it. Missing keys fall back to English.
 */
object L10n {
    fun t(key: String, lang: String): String =
        table[key]?.let { it[lang] ?: it["en"] } ?: key

    private val table: Map<String, Map<String, String>> = mapOf(
        "tab.overview" to mapOf(
            "en" to "Overview", "es" to "Resumen", "fr" to "Aperçu",
            "de" to "Übersicht", "pt" to "Visão geral", "it" to "Panoramica",
            "ja" to "概要", "zh" to "概览", "hi" to "अवलोकन", "ar" to "نظرة عامة"),
        "tab.chat" to mapOf(
            "en" to "Chat", "es" to "Chat", "fr" to "Discussion",
            "de" to "Chat", "pt" to "Conversa", "it" to "Chat",
            "ja" to "チャット", "zh" to "聊天", "hi" to "चैट", "ar" to "محادثة"),
        "tab.studio" to mapOf(
            "en" to "Studio", "es" to "Estudio", "fr" to "Studio",
            "de" to "Studio", "pt" to "Estúdio", "it" to "Studio",
            "ja" to "スタジオ", "zh" to "工作室", "hi" to "स्टूडियो", "ar" to "الاستوديو"),
        "tab.connect" to mapOf(
            "en" to "Connect", "es" to "Conectar", "fr" to "Connecter",
            "de" to "Verbinden", "pt" to "Conectar", "it" to "Connetti",
            "ja" to "接続", "zh" to "连接", "hi" to "कनेक्ट", "ar" to "اتصال"),
        "tab.manage" to mapOf(
            "en" to "Manage", "es" to "Gestionar", "fr" to "Gérer",
            "de" to "Verwalten", "pt" to "Gerenciar", "it" to "Gestisci",
            "ja" to "管理", "zh" to "管理", "hi" to "प्रबंधन", "ar" to "إدارة"),
        "tab.settings" to mapOf(
            "en" to "Settings", "es" to "Ajustes", "fr" to "Réglages",
            "de" to "Einstellungen", "pt" to "Configurações", "it" to "Impostazioni",
            "ja" to "設定", "zh" to "设置", "hi" to "सेटिंग्स", "ar" to "الإعدادات"),
        "action.send" to mapOf(
            "en" to "Send", "es" to "Enviar", "fr" to "Envoyer",
            "de" to "Senden", "pt" to "Enviar", "it" to "Invia",
            "ja" to "送信", "zh" to "发送", "hi" to "भेजें", "ar" to "إرسال"),
        "action.save" to mapOf(
            "en" to "Save", "es" to "Guardar", "fr" to "Enregistrer",
            "de" to "Speichern", "pt" to "Salvar", "it" to "Salva",
            "ja" to "保存", "zh" to "保存", "hi" to "सहेजें", "ar" to "حفظ"),
        "action.translate" to mapOf(
            "en" to "Translate", "es" to "Traducir", "fr" to "Traduire",
            "de" to "Übersetzen", "pt" to "Traduzir", "it" to "Traduci",
            "ja" to "翻訳", "zh" to "翻译", "hi" to "अनुवाद", "ar" to "ترجمة"),
        "action.sign_out" to mapOf(
            "en" to "Sign out", "es" to "Cerrar sesión", "fr" to "Se déconnecter",
            "de" to "Abmelden", "pt" to "Sair", "it" to "Esci",
            "ja" to "サインアウト", "zh" to "退出登录", "hi" to "साइन आउट",
            "ar" to "تسجيل الخروج"),
        "action.refresh" to mapOf(
            "en" to "Refresh", "es" to "Actualizar", "fr" to "Actualiser",
            "de" to "Aktualisieren", "pt" to "Atualizar", "it" to "Aggiorna",
            "ja" to "更新", "zh" to "刷新", "hi" to "रीफ़्रेश", "ar" to "تحديث"),
    )
}
