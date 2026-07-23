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
    }

    public sealed class CatalogVm
    {
        public string Provider { get; init; } = "";
        public string App { get; init; } = "";
        public string Label { get; init; } = "";
        public string Key => $"{Provider}|{App}";
    }

    public sealed class AppConnVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Provider { get; init; } = "";
        public string Capability { get; init; } = "";
        public bool Active { get; init; }
        public Visibility ActiveVisibility =>
            Active ? Visibility.Visible : Visibility.Collapsed;
        public string InvokeLabel => $"Invoke {Capability}";
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

    public ConnectPage() => InitializeComponent();

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
                    ? $"{c.Collected} item(s) collected"
                    : $"{c.Published} post(s) published",
                Collect = c.Direction == "collect",
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
            CatalogList.ItemsSource = cat.Providers
                .SelectMany(p => p.Apps.Select(a => new CatalogVm
                {
                    Provider = p.Provider,
                    App = a.App,
                    Label = a.Label,
                }))
                .Take(12).ToList();
            _appConns = await ApiClient.Shared.AppConnections(s.Pid!, s.Token!);
            AppConnList.ItemsSource = _appConns.Select(c => new AppConnVm
            {
                Id = c.Id,
                Title = c.Label,
                Provider = c.Provider,
                Capability = c.Capabilities.FirstOrDefault() ?? "",
                Active = c.Status != "revoked",
            }).ToList();
        }
        catch (Exception ex) { ShowAppsError(ex.Message); }
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
