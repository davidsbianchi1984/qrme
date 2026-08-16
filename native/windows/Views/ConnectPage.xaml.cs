using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class ConnectPage : Page
{
    public sealed class SocialVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Handle { get; init; } = "";
        public string Tally { get; init; } = "";
        public bool Collect { get; init; }
        public bool Active { get; init; }
        public Visibility ActiveVisibility =>
            Active ? Visibility.Visible : Visibility.Collapsed;
        public Visibility CollectVisibility =>
            Collect ? Visibility.Visible : Visibility.Collapsed;
        public Visibility PublishVisibility =>
            Collect ? Visibility.Collapsed : Visibility.Visible;
        public bool HasHandle { get; init; }
        public Visibility ScrapeVisibility =>
            Collect && HasHandle ? Visibility.Visible : Visibility.Collapsed;
        public string CollectLabel => L10n.T("ncon.collect.sample");
        public string ScrapeLabel => L10n.T("ncon.scrape");
        public string PublishLabel => L10n.T("ncon.publish.update");
        public string DisconnectLabel => L10n.T("ncon.disconnect");
    }

    public sealed class CatalogVm
    {
        public string Provider { get; init; } = "";
        public string App { get; init; } = "";
        public string Label { get; init; } = "";
        /// <summary>What this connector must be given before it can reach
        /// the far side: "nothing", "sign-in" or "key".</summary>
        public string NeedsFirst { get; init; } = "";
        public string Key => $"{Provider}|{App}";
        public string ConnectLabel => L10n.T("tab.connect");
        public string Lock => NeedsFirst switch
        {
            "key" => "\U0001F511",
            "nothing" => "",
            _ => "\U0001F512",
        };
    }

    public sealed class AppConnVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Provider { get; init; } = "";
        public string Capability { get; init; } = "";
        public bool Active { get; init; }
        public string NeedsFirst { get; init; } = "";
        public bool Authorized { get; init; }
        public Visibility ActiveVisibility =>
            Active ? Visibility.Visible : Visibility.Collapsed;
        public string InvokeLabel => $"Invoke {Capability}";
        public string AppCollectLabel => L10n.T("ncon.collect");
        public string RemoveLabel => L10n.T("ncon.remove");
        public string SignInLabel => L10n.T("ncon.signin");
        public string SecretLabel => L10n.T("ncon.secret");
        /// <summary>The lock, said in full: either it is signed in, or this
        /// is what it is still waiting for.</summary>
        public string Posture => Authorized
            ? L10n.T("ncon.on") : L10n.T($"ncon.needs.{NeedsFirst}");
        public Visibility SignInVisibility =>
            !Authorized && NeedsFirst != "nothing" ? Visibility.Visible : Visibility.Collapsed;
        public Visibility InvokeVisibility =>
            Capability.Length > 0 ? Visibility.Visible : Visibility.Collapsed;
    }

    private static readonly string[] Platforms =
    {
        "instagram", "x", "tiktok", "facebook", "linkedin", "youtube",
        "reddit", "threads", "whatsapp", "meta", "mastodon", "twitch",
        "snapchat", "roblox", "pinterest", "discord",
    };

    private SocialConn[] _social = Array.Empty<SocialConn>();
    private AppConn[] _appConns = Array.Empty<AppConn>();
    private CatalogVm[] _catalog = Array.Empty<CatalogVm>();

    /// <summary>The search box's own placeholder. Bound rather than set
    /// in code so the row is asked for where it is shown.</summary>
    public string AppFindLabel => L10n.T("ncon.apps.find");

    public ConnectPage()
    {
        InitializeComponent();
        Localize();
    }

    private void Localize()
    {
        var lang = AppState.Current.Language;
        SocialPivot.Header = L10n.T("ncon.tab.social", lang);
        AppsPivot.Header = L10n.T("ncon.tab.apps", lang);
        SocialHead.Text = L10n.T("ncon.social", lang);
        SocialSub.Text = L10n.T("ncon.social.sub", lang);
        PlatformBox.Header = L10n.T("ngam.platform", lang);
        HandleBox.Header = L10n.T("ncon.h.handle", lang);
        CollectButton.Content = L10n.T("ncon.to.collect", lang);
        PublishButton.Content = L10n.T("ncon.to.publish", lang);
        AppsHead.Text = L10n.T("ncon.apps", lang);
        AppsSub.Text = L10n.T("ncon.apps.sub", lang);
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        PlatformBox.ItemsSource = Platforms.ToList();
        PlatformBox.SelectedIndex = 0;
        await ReloadSocial();
        await ReloadApps();
    }

    // -- Social --

    private async System.Threading.Tasks.Task ReloadSocial()
    {
        var s = AppState.Current;
        try
        {
            _social = await ApiClient.Shared.SocialConnections(s.Pid!, s.Token!);
            SocialList.ItemsSource = _social.Select(c => new SocialVm
            {
                Id = c.Id,
                Title = $"{Cap(c.Platform)} · {c.Direction}",
                Handle = c.Handle ?? "",
                Tally = c.Direction == "collect"
                    ? L10n.Fill("ncon.collected", AppState.Current.Language,
                                ("n", c.Collected.ToString()))
                    : L10n.Fill("ncon.published", AppState.Current.Language,
                                ("n", c.Published.ToString())),
                Collect = c.Direction == "collect",
                HasHandle = !string.IsNullOrEmpty(c.Handle),
                Active = c.Status != "revoked",
            }).ToList();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private void OnConnectCollect(object sender, RoutedEventArgs e) => Connect("collect");

    private void OnConnectPublish(object sender, RoutedEventArgs e) => Connect("publish");

    private async void Connect(string direction)
    {
        if (PlatformBox.SelectedItem is not string platform) return;
        var s = AppState.Current;
        SocialError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.SocialConnect(
                s.Pid!, s.Token!, platform, direction, HandleBox.Text.Trim());
            HandleBox.Text = "";
            await ReloadSocial();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private async void OnCollect(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _social.FirstOrDefault(c => c.Id == cid);
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SocialCollect(
                cid, s.Token!, $"sample post from {conn?.Platform}");
            ShowSocialStatus($"collected one item from {conn?.Platform} — it now feeds training");
            await ReloadSocial();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private async void OnScrape(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _social.FirstOrDefault(c => c.Id == cid);
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SocialScrape(cid, s.Token!);
            ShowSocialStatus($"fetched {conn?.Platform} — the page now feeds training");
            await ReloadSocial();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private async void OnPublish(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _social.FirstOrDefault(c => c.Id == cid);
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SocialPublish(
                cid, s.Token!, "An update from my synthetic profile.");
            ShowSocialStatus($"published to {conn?.Platform}");
            await ReloadSocial();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    private async void OnRevoke(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.RevokeSocial(cid, s.Token!);
            await ReloadSocial();
        }
        catch (Exception ex) { ShowSocialError(ex.Message); }
    }

    // -- Apps --

    private async System.Threading.Tasks.Task ReloadApps()
    {
        var s = AppState.Current;
        try
        {
            var cat = await ApiClient.Shared.ConnectorCatalog();
            _catalog = cat.Providers
                .SelectMany(p => p.Apps.Select(a => new CatalogVm
                {
                    Provider = p.Provider,
                    App = a.App,
                    Label = a.Label,
                    NeedsFirst = a.NeedsFirst,
                }))
                .ToArray();
            ShowCatalog();
            _appConns = await ApiClient.Shared.AppConnections(s.Pid!, s.Token!);
            AppConnList.ItemsSource = _appConns.Select(c => new AppConnVm
            {
                Id = c.Id,
                Title = c.Label,
                Provider = c.Provider,
                Capability = c.Capabilities.FirstOrDefault() ?? "",
                Active = c.Status != "revoked",
                NeedsFirst = c.NeedsFirst,
                Authorized = c.Authorized,
            }).ToList();
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    /// <summary>The board, filtered. No Take(12) — a search that hides the
    /// answer below row twelve is not a search.</summary>
    private void ShowCatalog()
    {
        var needle = (AppFind.Text ?? "").Trim().ToLowerInvariant();
        CatalogList.ItemsSource = (needle.Length == 0
            ? _catalog.Take(24)
            : _catalog.Where(c => c.Label.ToLowerInvariant().Contains(needle)
                                  || c.App.ToLowerInvariant().Contains(needle)
                                  || c.Provider.ToLowerInvariant().Contains(needle)))
            .ToList();
    }

    private void OnAppFind(object sender, TextChangedEventArgs e) => ShowCatalog();

    private async void OnAppRevoke(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.AppRevoke(cid, s.Token!);
            await ReloadApps();
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    private async void OnAppAuthorize(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        // The field beside this button, found by the same connector id.
        var box = FindSecretBox(sender as Button);
        var secret = box?.Text ?? "";
        if (secret.Length == 0) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.AppAuthorize(cid, s.Token!, secret);
            if (box is not null) box.Text = "";
            await ReloadApps();
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    /// <summary>The secret box sharing this button's row. Walks up to the
    /// row's panel rather than naming the element, because the template is
    /// repeated once per connector and the names repeat with it.</summary>
    private static TextBox? FindSecretBox(Button? button)
    {
        if (button?.Parent is not Panel row) return null;
        foreach (var child in row.Children)
            if (child is TextBox box) return box;
        return null;
    }

    private async void OnAppConnect(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string key) return;
        var parts = key.Split('|', 2);
        if (parts.Length != 2) return;
        var s = AppState.Current;
        AppsError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.AppConnect(s.Pid!, s.Token!, parts[0], parts[1]);
            ShowAppsStatus($"connected {parts[0]}/{parts[1]}");
            await ReloadApps();
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    private async void OnAppCollect(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _appConns.FirstOrDefault(c => c.Id == cid);
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.AppCollect(
                cid, s.Token!, $"sample context from {conn?.App}");
            ShowAppsStatus($"collected from {conn?.Label} — it now feeds training");
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    private async void OnAppInvoke(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var conn = _appConns.FirstOrDefault(c => c.Id == cid);
        var cap = conn?.Capabilities.FirstOrDefault();
        if (conn is null || cap is null) return;
        var s = AppState.Current;
        try
        {
            var r = await ApiClient.Shared.AppInvoke(conn.Id, s.Token!, cap);
            ShowAppsStatus(r.Result);
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
    }

    // -- helpers --

    private void ShowSocialStatus(string message)
    {
        SocialStatus.Text = message;
        SocialStatus.Visibility = Visibility.Visible;
    }

    private void ShowSocialError(string message)
    {
        SocialError.Text = message;
        SocialError.Visibility = Visibility.Visible;
    }

    private void ShowAppsStatus(string message)
    {
        AppsStatus.Text = message;
        AppsStatus.Visibility = Visibility.Visible;
    }

    private void ShowAppsError(string message)
    {
        AppsError.Text = message;
        AppsError.Visibility = Visibility.Visible;
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];
}
