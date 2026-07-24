using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

/// Gaming: a synthetic profile plays alongside real players — a companion,
/// teammate, or practice partner, agent-operated, in character and fair.
public sealed partial class GamingPage : Page
{
    private static readonly string[] Platforms =
        { "playstation", "xbox", "nintendo", "steam", "pc" };
    private static readonly string[] Roles =
        { "companion", "teammate", "practice_partner" };

    public sealed class SessionVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Meta { get; init; } = "";
        public bool Active { get; init; }
        public override string ToString() => Title;
    }

    public GamingPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        PlatformBox.ItemsSource = Platforms.ToList();
        PlatformBox.SelectedIndex = 1;
        RoleBox.ItemsSource = Roles.ToList();
        RoleBox.SelectedIndex = 1;
        await Reload();
    }

    private async Task Reload()
    {
        var s = AppState.Current;
        try
        {
            var sessions = await ApiClient.Shared.GameSessions(s.Pid!, s.Token!);
            var vms = sessions.Select(g => new SessionVm
            {
                Id = g.Id,
                Title = $"{g.Game} · {g.PlatformLabel ?? g.Platform}",
                Meta = $"{g.Role.Replace("_", " ")} · {g.Callouts ?? 0} callouts · {g.Status}",
                Active = g.Status == "active",
            }).ToList();
            SessionList.ItemsSource = vms;
            var active = vms.Where(v => v.Active).ToList();
            ActiveBox.ItemsSource = active;
            PlayCard.Visibility = active.Count > 0 ? Visibility.Visible : Visibility.Collapsed;
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
    }

    private async void OnStart(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.StartGameSession(s.Pid!, s.Token!,
                PlatformBox.SelectedItem as string ?? "pc",
                GameBox.Text.Trim(), RoleBox.SelectedItem as string ?? "companion");
            GameBox.Text = "";
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
        await Reload();
    }

    private void OnActiveChanged(object sender, SelectionChangedEventArgs e) =>
        LineText.Visibility = Visibility.Collapsed;

    private async void OnCallout(object sender, RoutedEventArgs e)
    {
        if (ActiveBox.SelectedItem is not SessionVm vm) return;
        var s = AppState.Current;
        try
        {
            var r = await ApiClient.Shared.GameCallout(vm.Id, s.Token!,
                SituationBox.Text.Trim(), MinorCheck.IsChecked == true);
            LineText.Text = r.Status == "spoken" && r.Line is { } line
                ? $"🎙 {line}"
                : $"⚠️ held — {r.FlagReason ?? "moderation"}";
            LineText.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
        await Reload();
    }

    private async void OnEnd(object sender, RoutedEventArgs e)
    {
        if (ActiveBox.SelectedItem is not SessionVm vm) return;
        try { await ApiClient.Shared.EndGameSession(vm.Id, AppState.Current.Token!); }
        catch (Exception ex) { ErrorText.Text = ex.Message; ErrorText.Visibility = Visibility.Visible; }
        await Reload();
    }
}
