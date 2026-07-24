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
    public static string T(string key)
    {
        var lang = AppState.Current.Language;
        if (Table.TryGetValue(key, out var row))
            return row.TryGetValue(lang, out var s) ? s
                 : row.TryGetValue("en", out var en) ? en : key;
        return key;
    }

    private static readonly Dictionary<string, Dictionary<string, string>> Table = new()
    {
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
        ["tab.settings"] = new() { ["en"] = "Settings", ["es"] = "Ajustes", ["fr"] = "Réglages", ["de"] = "Einstellungen", ["pt"] = "Configurações", ["it"] = "Impostazioni", ["ja"] = "設定", ["zh"] = "设置", ["hi"] = "सेटिंग्स", ["ar"] = "الإعدادات" },
        ["action.send"] = new() { ["en"] = "Send", ["es"] = "Enviar", ["fr"] = "Envoyer", ["de"] = "Senden", ["pt"] = "Enviar", ["it"] = "Invia", ["ja"] = "送信", ["zh"] = "发送", ["hi"] = "भेजें", ["ar"] = "إرسال" },
        ["action.save"] = new() { ["en"] = "Save", ["es"] = "Guardar", ["fr"] = "Enregistrer", ["de"] = "Speichern", ["pt"] = "Salvar", ["it"] = "Salva", ["ja"] = "保存", ["zh"] = "保存", ["hi"] = "सहेजें", ["ar"] = "حفظ" },
        ["action.translate"] = new() { ["en"] = "Translate", ["es"] = "Traducir", ["fr"] = "Traduire", ["de"] = "Übersetzen", ["pt"] = "Traduzir", ["it"] = "Traduci", ["ja"] = "翻訳", ["zh"] = "翻译", ["hi"] = "अनुवाद", ["ar"] = "ترجمة" },
        ["action.refresh"] = new() { ["en"] = "Refresh", ["es"] = "Actualizar", ["fr"] = "Actualiser", ["de"] = "Aktualisieren", ["pt"] = "Atualizar", ["it"] = "Aggiorna", ["ja"] = "更新", ["zh"] = "刷新", ["hi"] = "रीफ़्रेश", ["ar"] = "تحديث" },
    };
}
