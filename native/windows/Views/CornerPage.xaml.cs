using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

/// <summary>
/// Your corner: the homepage sandbox, friends-only messages, and the
/// switches. Every visible string comes from L10n; the server's refusal
/// sentences — including the ones that name a switch — are shown verbatim
/// in the reader's language.
/// </summary>
public sealed partial class CornerPage : Page
{
    public record Row(string Line);

    private bool _loading;

    public CornerPage()
    {
        InitializeComponent();
        TitleText.Text = L10n.T("corner.title");
        WallsText.Text = L10n.T("corner.walls");
        HeadlineBox.Header = L10n.T("corner.headline");
        AboutBox.Header = L10n.T("corner.about");
        BgBox.Header = L10n.T("corner.bg");
        AccentBox.Header = L10n.T("corner.accent");
        SaveButton.Content = L10n.T("corner.save");
        MessagingSwitch.Header = L10n.T("corner.switch.messaging");
        HomepageSwitch.Header = L10n.T("corner.switch.homepage");
        MessagesTitle.Text = L10n.T("corner.messages");
        FriendsOnlyText.Text = L10n.T("corner.friends_only");
        WithBox.Header = L10n.T("corner.to");
        OpenButton.Content = L10n.T("corner.open");
        DraftBox.Header = L10n.T("corner.send");
        SendButton.Content = L10n.T("corner.send");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        await Load();
    }

    private async System.Threading.Tasks.Task Load()
    {
        var s = AppState.Current;
        if (s.Pid is null || s.Token is null) return;
        _loading = true;
        try
        {
            var page = await ApiClient.Shared.HomepageOf(s.Pid, s.Token);
            HeadlineBox.Text = page.Headline;
            AboutBox.Text = page.About;
            BgBox.Text = page.Theme.Bg;
            AccentBox.Text = page.Theme.Accent;
            var flags = await ApiClient.Shared.Features(s.Pid, s.Token);
            MessagingSwitch.IsOn = flags.TryGetValue("messaging", out var m) && m;
            HomepageSwitch.IsOn = flags.TryGetValue("homepage", out var h) && h;
            var box = await ApiClient.Shared.DmThreads(s.Pid, s.Token);
            ThreadList.ItemsSource = box.Threads.Select(t => new Row(
                $"{t.OtherId} · {t.OtherName ?? ""} · {t.MessagesCount}")).ToList();
        }
        catch { /* leave as-is */ }
        _loading = false;
    }

    private async void OnSave(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        if (s.Pid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.EditHomepage(s.Pid, HeadlineBox.Text,
                AboutBox.Text, BgBox.Text.Trim(), AccentBox.Text.Trim(),
                s.Token);
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnMessagingToggled(object sender, RoutedEventArgs e) =>
        await Flip("messaging", MessagingSwitch.IsOn);

    private async void OnHomepageToggled(object sender, RoutedEventArgs e) =>
        await Flip("homepage", HomepageSwitch.IsOn);

    private async System.Threading.Tasks.Task Flip(string feature, bool on)
    {
        if (_loading) return;
        var s = AppState.Current;
        if (s.Pid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.SetFeature(s.Pid, feature, on, s.Token);
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnOpenThread(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var other = WithBox.Text.Trim();
        if (other.Length == 0 || s.Pid is null || s.Token is null) return;
        try
        {
            var view = await ApiClient.Shared.DmThread(s.Pid, other, s.Token);
            MessageList.ItemsSource = view.Messages.Select(m => new Row(
                (m.SenderId == s.Pid ? "→ " : "← ") + m.Body)).ToList();
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnSend(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var other = WithBox.Text.Trim();
        var body = DraftBox.Text.Trim();
        if (other.Length == 0 || body.Length == 0 ||
            s.Pid is null || s.Token is null) return;
        try
        {
            await ApiClient.Shared.SendDm(s.Pid, other, body, s.Token);
            DraftBox.Text = "";
            OnOpenThread(sender, e);
            await Load();
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }
}
