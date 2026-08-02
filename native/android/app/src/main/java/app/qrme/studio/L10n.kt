package app.qrme.studio

import android.content.res.Resources

/**
 * App-chrome localization: tab names, screen titles, and the most common
 * actions, in every language the backend supports. Content (chat, guidance,
 * persona text) is localized server-side by the profile's language setting;
 * this table covers the frame around it. Missing keys fall back to English.
 */
object L10n {
    fun t(key: String, lang: String): String =
        table[key]?.let { it[lang] ?: it["en"] } ?: key

    val supported = listOf("en", "es", "fr", "de", "pt", "it", "ja", "zh",
                           "hi", "ar")

    /**
     * The language of somebody who has no profile to take one from.
     *
     * `AppState.language` comes from the profile's stored setting and is
     * "en" until one exists — right for the tab bar, useless for the
     * without-an-account screen, which exists for a person who has no
     * profile and is not going to make one. Their phone has been carrying
     * the answer in the system configuration all along.
     *
     * Region dropped; anything this app does not carry falls back to English
     * rather than guessing.
     */
    fun deviceLanguage(): String {
        val locales = Resources.getSystem().configuration.locales
        for (i in 0 until locales.size()) {
            val base = locales[i].language.lowercase()
            if (supported.contains(base)) return base
        }
        return "en"
    }

    private val table: Map<String, Map<String, String>> = mapOf(
        "obj.timeline.title" to mapOf("en" to "What has happened to your case", "es" to "Qué ha pasado con su caso", "fr" to "Ce qu'il est advenu de votre dossier", "de" to "Was mit Ihrem Fall geschehen ist", "pt" to "O que aconteceu ao seu caso", "it" to "Cosa è successo al tuo caso", "ja" to "あなたの案件の経過", "zh" to "你的案件进展如何", "hi" to "आपके मामले में क्या हुआ", "ar" to "ما جرى في قضيتك"),
        "obj.timeline.go" to mapOf("en" to "Show the record", "es" to "Ver el registro", "fr" to "Afficher le registre", "de" to "Akte anzeigen", "pt" to "Ver o registo", "it" to "Mostra il registro", "ja" to "記録を見る", "zh" to "查看记录", "hi" to "रिकॉर्ड दिखाएँ", "ar" to "أظهر السجل"),
        "obj.timeline.sealed" to mapOf("en" to "sealed in the vault", "es" to "sellado en la bóveda", "fr" to "scellé dans le coffre", "de" to "im Tresor versiegelt", "pt" to "selado no cofre", "it" to "sigillato nella cassaforte", "ja" to "保管庫に封印済み", "zh" to "已封存于保险库", "hi" to "वॉल्ट में सील किया गया", "ar" to "مختوم في الخزنة"),
        "obj.timeline.empty" to mapOf("en" to "Nothing on this case yet.", "es" to "Todavía nada en este caso.", "fr" to "Rien encore sur ce dossier.", "de" to "Zu diesem Fall noch nichts.", "pt" to "Ainda nada neste caso.", "it" to "Ancora nulla su questo caso.", "ja" to "この案件にはまだ何もありません。", "zh" to "此案件暂无记录。", "hi" to "इस मामले पर अभी कुछ नहीं।", "ar" to "لا شيء في هذه القضية بعد."),
        "obj.event.opened" to mapOf("en" to "opened", "es" to "abierta", "fr" to "ouverte", "de" to "eröffnet", "pt" to "aberta", "it" to "aperta", "ja" to "受理", "zh" to "已提出", "hi" to "खोला गया", "ar" to "فُتحت"),
        "obj.event.reattested" to mapOf("en" to "basis re-attested", "es" to "base reacreditada", "fr" to "base réattestée", "de" to "Grundlage erneut bestätigt", "pt" to "base reatestada", "it" to "base riattestata", "ja" to "根拠を再証明", "zh" to "已重新证明依据", "hi" to "आधार पुनः प्रमाणित", "ar" to "أُعيد إثبات الأساس"),
        "obj.event.upheld" to mapOf("en" to "upheld", "es" to "estimada", "fr" to "retenue", "de" to "stattgegeben", "pt" to "deferida", "it" to "accolta", "ja" to "認容", "zh" to "已支持", "hi" to "स्वीकृत", "ar" to "قُبلت"),
        "obj.event.dismissed" to mapOf("en" to "dismissed", "es" to "desestimada", "fr" to "rejetée", "de" to "abgewiesen", "pt" to "indeferida", "it" to "respinta", "ja" to "却下", "zh" to "已驳回", "hi" to "खारिज", "ar" to "رُفضت"),
        "obj.event.withdrawn" to mapOf("en" to "consent withdrawn", "es" to "consentimiento retirado", "fr" to "consentement retiré", "de" to "Einwilligung zurückgezogen", "pt" to "consentimento retirado", "it" to "consenso ritirato", "ja" to "同意の撤回", "zh" to "已撤回同意", "hi" to "सहमति वापस", "ar" to "سُحبت الموافقة"),
        "obj.event.revoked" to mapOf("en" to "authorization revoked", "es" to "autorización revocada", "fr" to "autorisation révoquée", "de" to "Autorisierung widerrufen", "pt" to "autorização revogada", "it" to "autorizzazione revocata", "ja" to "承認の取り消し", "zh" to "已撤销授权", "hi" to "प्राधिकरण रद्द", "ar" to "أُلغي التفويض"),
        "obj.event.terminated" to mapOf("en" to "profile terminated", "es" to "perfil terminado", "fr" to "profil supprimé", "de" to "Profil beendet", "pt" to "perfil terminado", "it" to "profilo terminato", "ja" to "プロフィール終了", "zh" to "资料已终止", "hi" to "प्रोफ़ाइल समाप्त", "ar" to "أُنهي الملف"),
        "obj.actor.objector" to mapOf("en" to "you", "es" to "usted", "fr" to "vous", "de" to "Sie", "pt" to "você", "it" to "tu", "ja" to "あなた", "zh" to "你", "hi" to "आप", "ar" to "أنت"),
        "obj.actor.owner" to mapOf("en" to "the owner", "es" to "el titular", "fr" to "le propriétaire", "de" to "die Inhaberin oder der Inhaber", "pt" to "o titular", "it" to "il titolare", "ja" to "所有者", "zh" to "所有者", "hi" to "स्वामी", "ar" to "المالك"),
        "obj.actor.reviewer" to mapOf("en" to "a reviewer", "es" to "un revisor", "fr" to "un examinateur", "de" to "eine prüfende Person", "pt" to "um revisor", "it" to "un revisore", "ja" to "審査担当", "zh" to "审核人", "hi" to "समीक्षक", "ar" to "مُراجِع"),
        "obj.actor.subject" to mapOf("en" to "the subject", "es" to "el sujeto", "fr" to "la personne concernée", "de" to "die betroffene Person", "pt" to "o titular dos dados", "it" to "la persona interessata", "ja" to "本人", "zh" to "当事人", "hi" to "संबंधित व्यक्ति", "ar" to "الشخص المعني"),
        "obj.actor.estate" to mapOf("en" to "the estate", "es" to "la sucesión", "fr" to "la succession", "de" to "der Nachlass", "pt" to "o espólio", "it" to "gli eredi", "ja" to "遺族", "zh" to "遗产代表", "hi" to "संपदा", "ar" to "الورثة"),
        "obj.actor.system" to mapOf("en" to "the platform", "es" to "la plataforma", "fr" to "la plateforme", "de" to "die Plattform", "pt" to "a plataforma", "it" to "la piattaforma", "ja" to "プラットフォーム", "zh" to "平台", "hi" to "प्लेटफ़ॉर्म", "ar" to "المنصة"),
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
