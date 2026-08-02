using System.Collections.Generic;

namespace QrmeStudio;

/// <summary>
/// App-chrome localization: nav names and the most common actions, in every
/// language the backend supports. Content (chat, posts, persona text) is
/// localized server-side by the profile's language setting; this table covers
/// the frame around it. Missing keys fall back to English.
/// </summary>
public static class L10n
{
    /// <summary>
    /// The language of somebody who has no profile to take one from.
    ///
    /// <para><c>AppState.Language</c> is the profile's stored setting and is
    /// "en" until one exists — right for the shell, useless for
    /// WithoutAnAccountPage, which is there for a person who has no profile
    /// and is not going to make one. Windows has been carrying the answer in
    /// CurrentUICulture the whole time.</para>
    ///
    /// <para>Region dropped; anything this app does not carry falls back to
    /// English rather than guessing.</para>
    /// </summary>
    public static readonly string[] Supported =
        { "en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar" };

    public static string DeviceLanguage()
    {
        var culture = System.Globalization.CultureInfo.CurrentUICulture;
        while (culture != null && !string.IsNullOrEmpty(culture.Name))
        {
            var code = culture.TwoLetterISOLanguageName.ToLowerInvariant();
            if (System.Array.IndexOf(Supported, code) >= 0) return code;
            culture = culture.Parent;
        }
        return "en";
    }

    /// <summary>The shell's chrome, in the signed-in profile's language.
    ///
    /// <para>Convenient and, on one screen, wrong: the language it reaches for
    /// is <c>AppState.Current.Language</c>, which is the profile's stored
    /// setting. WithoutAnAccountPage's reader has no profile, so this overload
    /// answers them in English no matter what their machine is set to — and
    /// does it without the screen ever naming the profile. iOS and Android
    /// cannot make that mistake: both of their <c>t</c> functions require the
    /// language as an argument. Windows was the one shell where the default
    /// was reachable by writing nothing.</para></summary>
    public static string T(string key) => T(key, AppState.Current.Language);

    /// <summary>The same table, asked in a language the caller names.
    ///
    /// <para>Pass <c>DeviceLanguage()</c> on any surface whose reader has no
    /// profile to take a language from.</para></summary>
    public static string T(string key, string lang)
    {
        if (Table.TryGetValue(key, out var row))
            return row.TryGetValue(lang, out var s) ? s
                 : row.TryGetValue("en", out var en) ? en : key;
        return key;
    }

    private static readonly Dictionary<string, Dictionary<string, string>> Table = new()
    {
        ["obj.timeline.title"] = new() { ["en"] = "What has happened to your case", ["es"] = "Qué ha pasado con su caso", ["fr"] = "Ce qu'il est advenu de votre dossier", ["de"] = "Was mit Ihrem Fall geschehen ist", ["pt"] = "O que aconteceu ao seu caso", ["it"] = "Cosa è successo al tuo caso", ["ja"] = "あなたの案件の経過", ["zh"] = "你的案件进展如何", ["hi"] = "आपके मामले में क्या हुआ", ["ar"] = "ما جرى في قضيتك" },
        ["obj.timeline.go"] = new() { ["en"] = "Show the record", ["es"] = "Ver el registro", ["fr"] = "Afficher le registre", ["de"] = "Akte anzeigen", ["pt"] = "Ver o registo", ["it"] = "Mostra il registro", ["ja"] = "記録を見る", ["zh"] = "查看记录", ["hi"] = "रिकॉर्ड दिखाएँ", ["ar"] = "أظهر السجل" },
        ["obj.timeline.need_id"] = new() { ["en"] = "Enter the objection's id.", ["es"] = "Introduzca el identificador de la objeción.", ["fr"] = "Saisissez l'identifiant de l'objection.", ["de"] = "Geben Sie die Kennung des Einspruchs ein.", ["pt"] = "Introduza o identificador da objeção.", ["it"] = "Inserisci l'identificativo dell'obiezione.", ["ja"] = "異議の ID を入力してください。", ["zh"] = "请输入异议编号。", ["hi"] = "आपत्ति की आईडी दर्ज करें।", ["ar"] = "أدخل معرّف الاعتراض." },
        ["obj.timeline.sealed"] =new() { ["en"] = "sealed in the vault", ["es"] = "sellado en la bóveda", ["fr"] = "scellé dans le coffre", ["de"] = "im Tresor versiegelt", ["pt"] = "selado no cofre", ["it"] = "sigillato nella cassaforte", ["ja"] = "保管庫に封印済み", ["zh"] = "已封存于保险库", ["hi"] = "वॉल्ट में सील किया गया", ["ar"] = "مختوم في الخزنة" },
        ["obj.timeline.empty"] = new() { ["en"] = "Nothing on this case yet.", ["es"] = "Todavía nada en este caso.", ["fr"] = "Rien encore sur ce dossier.", ["de"] = "Zu diesem Fall noch nichts.", ["pt"] = "Ainda nada neste caso.", ["it"] = "Ancora nulla su questo caso.", ["ja"] = "この案件にはまだ何もありません。", ["zh"] = "此案件暂无记录。", ["hi"] = "इस मामले पर अभी कुछ नहीं।", ["ar"] = "لا شيء في هذه القضية بعد." },
        ["obj.event.opened"] = new() { ["en"] = "opened", ["es"] = "abierta", ["fr"] = "ouverte", ["de"] = "eröffnet", ["pt"] = "aberta", ["it"] = "aperta", ["ja"] = "受理", ["zh"] = "已提出", ["hi"] = "खोला गया", ["ar"] = "فُتحت" },
        ["obj.event.reattested"] = new() { ["en"] = "basis re-attested", ["es"] = "base reacreditada", ["fr"] = "base réattestée", ["de"] = "Grundlage erneut bestätigt", ["pt"] = "base reatestada", ["it"] = "base riattestata", ["ja"] = "根拠を再証明", ["zh"] = "已重新证明依据", ["hi"] = "आधार पुनः प्रमाणित", ["ar"] = "أُعيد إثبات الأساس" },
        ["obj.event.upheld"] = new() { ["en"] = "upheld", ["es"] = "estimada", ["fr"] = "retenue", ["de"] = "stattgegeben", ["pt"] = "deferida", ["it"] = "accolta", ["ja"] = "認容", ["zh"] = "已支持", ["hi"] = "स्वीकृत", ["ar"] = "قُبلت" },
        ["obj.event.dismissed"] = new() { ["en"] = "dismissed", ["es"] = "desestimada", ["fr"] = "rejetée", ["de"] = "abgewiesen", ["pt"] = "indeferida", ["it"] = "respinta", ["ja"] = "却下", ["zh"] = "已驳回", ["hi"] = "खारिज", ["ar"] = "رُفضت" },
        ["obj.event.withdrawn"] = new() { ["en"] = "consent withdrawn", ["es"] = "consentimiento retirado", ["fr"] = "consentement retiré", ["de"] = "Einwilligung zurückgezogen", ["pt"] = "consentimento retirado", ["it"] = "consenso ritirato", ["ja"] = "同意の撤回", ["zh"] = "已撤回同意", ["hi"] = "सहमति वापस", ["ar"] = "سُحبت الموافقة" },
        ["obj.event.revoked"] = new() { ["en"] = "authorization revoked", ["es"] = "autorización revocada", ["fr"] = "autorisation révoquée", ["de"] = "Autorisierung widerrufen", ["pt"] = "autorização revogada", ["it"] = "autorizzazione revocata", ["ja"] = "承認の取り消し", ["zh"] = "已撤销授权", ["hi"] = "प्राधिकरण रद्द", ["ar"] = "أُلغي التفويض" },
        ["obj.event.terminated"] = new() { ["en"] = "profile terminated", ["es"] = "perfil terminado", ["fr"] = "profil supprimé", ["de"] = "Profil beendet", ["pt"] = "perfil terminado", ["it"] = "profilo terminato", ["ja"] = "プロフィール終了", ["zh"] = "资料已终止", ["hi"] = "प्रोफ़ाइल समाप्त", ["ar"] = "أُنهي الملف" },
        ["obj.actor.objector"] = new() { ["en"] = "you", ["es"] = "usted", ["fr"] = "vous", ["de"] = "Sie", ["pt"] = "você", ["it"] = "tu", ["ja"] = "あなた", ["zh"] = "你", ["hi"] = "आप", ["ar"] = "أنت" },
        ["obj.actor.owner"] = new() { ["en"] = "the owner", ["es"] = "el titular", ["fr"] = "le propriétaire", ["de"] = "die Inhaberin oder der Inhaber", ["pt"] = "o titular", ["it"] = "il titolare", ["ja"] = "所有者", ["zh"] = "所有者", ["hi"] = "स्वामी", ["ar"] = "المالك" },
        ["obj.actor.reviewer"] = new() { ["en"] = "a reviewer", ["es"] = "un revisor", ["fr"] = "un examinateur", ["de"] = "eine prüfende Person", ["pt"] = "um revisor", ["it"] = "un revisore", ["ja"] = "審査担当", ["zh"] = "审核人", ["hi"] = "समीक्षक", ["ar"] = "مُراجِع" },
        ["obj.actor.subject"] = new() { ["en"] = "the subject", ["es"] = "el sujeto", ["fr"] = "la personne concernée", ["de"] = "die betroffene Person", ["pt"] = "o titular dos dados", ["it"] = "la persona interessata", ["ja"] = "本人", ["zh"] = "当事人", ["hi"] = "संबंधित व्यक्ति", ["ar"] = "الشخص المعني" },
        ["obj.actor.estate"] = new() { ["en"] = "the estate", ["es"] = "la sucesión", ["fr"] = "la succession", ["de"] = "der Nachlass", ["pt"] = "o espólio", ["it"] = "gli eredi", ["ja"] = "遺族", ["zh"] = "遗产代表", ["hi"] = "संपदा", ["ar"] = "الورثة" },
        ["obj.actor.system"] = new() { ["en"] = "the platform", ["es"] = "la plataforma", ["fr"] = "la plateforme", ["de"] = "die Plattform", ["pt"] = "a plataforma", ["it"] = "la piattaforma", ["ja"] = "プラットフォーム", ["zh"] = "平台", ["hi"] = "प्लेटफ़ॉर्म", ["ar"] = "المنصة" },
        ["tab.overview"] = new() { ["en"] = "Overview", ["es"] = "Resumen", ["fr"] = "Aperçu", ["de"] = "Übersicht", ["pt"] = "Visão geral", ["it"] = "Panoramica", ["ja"] = "概要", ["zh"] = "概览", ["hi"] = "अवलोकन", ["ar"] = "نظرة عامة" },
        ["tab.chat"] = new() { ["en"] = "Chat", ["es"] = "Chat", ["fr"] = "Discussion", ["de"] = "Chat", ["pt"] = "Conversa", ["it"] = "Chat", ["ja"] = "チャット", ["zh"] = "聊天", ["hi"] = "चैट", ["ar"] = "محادثة" },
        ["tab.community"] = new() { ["en"] = "Community", ["es"] = "Comunidad", ["fr"] = "Communauté", ["de"] = "Community", ["pt"] = "Comunidade", ["it"] = "Comunità", ["ja"] = "コミュニティ", ["zh"] = "社区", ["hi"] = "समुदाय", ["ar"] = "مجتمع" },
        ["tab.compose"] = new() { ["en"] = "Compose", ["es"] = "Redactar", ["fr"] = "Composer", ["de"] = "Verfassen", ["pt"] = "Compor", ["it"] = "Componi", ["ja"] = "作成", ["zh"] = "撰写", ["hi"] = "लिखें", ["ar"] = "إنشاء" },
        ["tab.posts"] = new() { ["en"] = "Posts", ["es"] = "Publicaciones", ["fr"] = "Publications", ["de"] = "Beiträge", ["pt"] = "Publicações", ["it"] = "Post", ["ja"] = "投稿", ["zh"] = "帖子", ["hi"] = "पोस्ट", ["ar"] = "منشورات" },
        ["tab.study"] = new() { ["en"] = "Study", ["es"] = "Estudiar", ["fr"] = "Étude", ["de"] = "Studie", ["pt"] = "Estudo", ["it"] = "Studiare", ["ja"] = "学習", ["zh"] = "学习", ["hi"] = "अध्ययन", ["ar"] = "دراسة" },
        ["tab.connect"] = new() { ["en"] = "Connect", ["es"] = "Conectar", ["fr"] = "Connecter", ["de"] = "Verbinden", ["pt"] = "Conectar", ["it"] = "Connetti", ["ja"] = "接続", ["zh"] = "连接", ["hi"] = "कनेक्ट", ["ar"] = "اتصال" },
        ["tab.gaming"] = new() { ["en"] = "Gaming", ["es"] = "Juegos", ["fr"] = "Jeux", ["de"] = "Gaming", ["pt"] = "Jogos", ["it"] = "Gaming", ["ja"] = "ゲーム", ["zh"] = "游戏", ["hi"] = "गेमिंग", ["ar"] = "ألعاب" },
        ["tab.robots"] = new() { ["en"] = "Robots", ["es"] = "Robots", ["fr"] = "Robots", ["de"] = "Roboter", ["pt"] = "Robôs", ["it"] = "Robot", ["ja"] = "ロボット", ["zh"] = "机器人", ["hi"] = "रोबोट", ["ar"] = "روبوتات" },
        ["tab.reach"] = new() { ["en"] = "Reach", ["es"] = "Alcance", ["fr"] = "Portée", ["de"] = "Reichweite", ["pt"] = "Alcance", ["it"] = "Portata", ["ja"] = "リーチ", ["zh"] = "触达", ["hi"] = "पहुंच", ["ar"] = "انتشار" },
        ["tab.desk"] = new() { ["en"] = "Desk", ["es"] = "Mostrador", ["fr"] = "Comptoir", ["de"] = "Theke", ["pt"] = "Balcão", ["it"] = "Banco", ["ja"] = "受付", ["zh"] = "服务台", ["hi"] = "डेस्क", ["ar"] = "مكتب" },
        ["tab.signatures"] = new() { ["en"] = "Signatures", ["es"] = "Firmas", ["fr"] = "Signatures", ["de"] = "Signaturen", ["pt"] = "Assinaturas", ["it"] = "Firme", ["ja"] = "署名", ["zh"] = "签名", ["hi"] = "हस्ताक्षर", ["ar"] = "التوقيعات" },
        ["tab.voice"] = new() { ["en"] = "Voice", ["es"] = "Voz", ["fr"] = "Voix", ["de"] = "Stimme", ["pt"] = "Voz", ["it"] = "Voce", ["ja"] = "音声", ["zh"] = "语音", ["hi"] = "आवाज़", ["ar"] = "الصوت" },
        ["tab.settings"] = new() { ["en"] = "Settings", ["es"] = "Ajustes", ["fr"] = "Réglages", ["de"] = "Einstellungen", ["pt"] = "Configurações", ["it"] = "Impostazioni", ["ja"] = "設定", ["zh"] = "设置", ["hi"] = "सेटिंग्स", ["ar"] = "الإعدادات" },
        ["action.send"] = new() { ["en"] = "Send", ["es"] = "Enviar", ["fr"] = "Envoyer", ["de"] = "Senden", ["pt"] = "Enviar", ["it"] = "Invia", ["ja"] = "送信", ["zh"] = "发送", ["hi"] = "भेजें", ["ar"] = "إرسال" },
        ["action.save"] = new() { ["en"] = "Save", ["es"] = "Guardar", ["fr"] = "Enregistrer", ["de"] = "Speichern", ["pt"] = "Salvar", ["it"] = "Salva", ["ja"] = "保存", ["zh"] = "保存", ["hi"] = "सहेजें", ["ar"] = "حفظ" },
        ["action.translate"] = new() { ["en"] = "Translate", ["es"] = "Traducir", ["fr"] = "Traduire", ["de"] = "Übersetzen", ["pt"] = "Traduzir", ["it"] = "Traduci", ["ja"] = "翻訳", ["zh"] = "翻译", ["hi"] = "अनुवाद", ["ar"] = "ترجمة" },
        ["action.refresh"] = new() { ["en"] = "Refresh", ["es"] = "Actualizar", ["fr"] = "Actualiser", ["de"] = "Aktualisieren", ["pt"] = "Atualizar", ["it"] = "Aggiorna", ["ja"] = "更新", ["zh"] = "刷新", ["hi"] = "रीफ़्रेश", ["ar"] = "تحديث" },
    };
}
