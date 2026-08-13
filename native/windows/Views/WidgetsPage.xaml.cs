using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace QrmeStudio.Views;

/// <summary>
/// Widgets: small programs somebody writes for their own profile.
///
/// The code never runs on this machine. It goes to the backend and runs
/// there in a box with no network, no files but its own, no child processes
/// and finite time — which is what lets a person write whatever they like
/// without reaching anybody else's profile.
///
/// A run that throws, runs too long, or is stopped by a limit comes back
/// with a status rather than a refusal: the request was fine, the code was
/// not, and the sentence beside it is the backend's, in the reader's
/// language.
/// </summary>
public sealed partial class WidgetsPage : Page
{
    private WidgetRow[] _widgets = Array.Empty<WidgetRow>();
    private WidgetRow? _open;
    private WidgetCaps? _caps;
    // The agent. Its conversation lives here rather than on the server: it
    // has no memory of its own, so leaving this page is all of forgetting.
    private AgentReach? _reach;
    private readonly System.Collections.Generic.List<AgentSaid> _talk = new();
    private bool _showsReach;

    public WidgetsPage()
    {
        InitializeComponent();
        Localize();
        Loaded += async (_, _) => await LoadAsync();
    }

    private void Localize()
    {
        var lang = AppState.Current.Language;
        Title.Text = L10n.T("wdg.title", lang);
        Sub.Text = L10n.T("wdg.yours", lang);
        YoursLabel.Text = L10n.T("wdg.yours", lang);
        NoBox.Text = L10n.T("wdg.nobox", lang);
        NameBox.Header = L10n.T("wdg.name", lang);
        SourceBox.Header = L10n.T("wdg.code", lang);
        SaveButton.Content = L10n.T("wdg.save", lang);
        RunButton.Content = L10n.T("wdg.run", lang);
        RemoveButton.Content = L10n.T("wdg.remove", lang);
        Walls.Text = L10n.T("wdg.walls", lang);
        AskTitle.Text = L10n.T("wdg.ask.title", lang);
        AskSub.Text = L10n.T("wdg.ask.sub", lang);
        AskButton.Content = L10n.T("wdg.ask.go", lang);
        ForgetButton.Content = L10n.T("wdg.ask.forget", lang);
        NoModel.Text = L10n.T("wdg.ask.nomodel", lang);
        ReachButton.Content = L10n.T(
            _showsReach ? "wdg.reach.hide" : "wdg.reach.show", lang);
    }

    private void OnToggleReach(object sender, RoutedEventArgs e)
    {
        _showsReach = !_showsReach;
        ReachList.Visibility = _showsReach && _reach is not null
            ? Visibility.Visible : Visibility.Collapsed;
        if (_reach is not null)
            ReachList.Text = string.Join("\n",
                _reach.CanTouch.Select(line => "\u2022 " + line));
        Localize();
    }

    /// <summary>Ask for it in words. Afterwards the list and the open draft
    /// are re-read rather than reasoned about: it may have written, revised
    /// or removed one, and a stale list is the thing here that can be wrong
    /// without anybody noticing.</summary>
    private async void OnAsk(object sender, RoutedEventArgs e)
    {
        var state = AppState.Current;
        if (state.Pid is null || state.Token is null) return;
        var said = AskBox.Text.Trim();
        if (said.Length == 0) return;
        AskButton.IsEnabled = false;
        try
        {
            var turn = await ApiClient.Shared.AuthoringTurn(
                state.Pid, said, _talk.ToArray(), state.Token);
            _talk.Add(new AgentSaid("user", said));
            _talk.Add(new AgentSaid("assistant", turn.Reply));
            AskBox.Text = "";
            TalkText.Text = string.Join("\n",
                _talk.Select(t => t.Content));
            TalkText.Visibility = Visibility.Visible;
            ForgetButton.Visibility = Visibility.Visible;
            StepsText.Text = string.Join("\n",
                new[] { turn.Said ?? "" }
                    .Concat(turn.Acted.Select(
                        s => s.Said ?? $"{s.Tool} \u2014 {s.Answered ?? 0}"))
                    .Where(line => line.Length > 0));
            StepsText.Visibility = StepsText.Text.Length == 0
                ? Visibility.Collapsed : Visibility.Visible;
            await LoadAsync();
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { AskButton.IsEnabled = true; }
    }

    private void OnForget(object sender, RoutedEventArgs e)
    {
        _talk.Clear();
        TalkText.Visibility = Visibility.Collapsed;
        StepsText.Visibility = Visibility.Collapsed;
        ForgetButton.Visibility = Visibility.Collapsed;
    }

    private async System.Threading.Tasks.Task LoadAsync()
    {
        var state = AppState.Current;
        if (state.Pid is null || state.Token is null) return;
        try
        {
            _caps = await ApiClient.Shared.WidgetLimits();
            NoBox.Visibility = _caps.Available ? Visibility.Collapsed
                                               : Visibility.Visible;
            RunButton.IsEnabled = _caps.Available;
            _reach = await ApiClient.Shared.StudioAgent();
            NoModel.Visibility = _reach.Available ? Visibility.Collapsed
                                                  : Visibility.Visible;
            _widgets = await ApiClient.Shared.Widgets(state.Pid, state.Token);
            WidgetList.ItemsSource = _widgets.Select(w => w.Name).ToList();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    /// <summary>Re-read the one being opened rather than trusting the list:
    /// a list fetched a minute ago holds a draft from a minute ago, and
    /// saving over it is how an edit made on the phone disappears.</summary>
    private async void OnPick(object sender, SelectionChangedEventArgs e)
    {
        var index = WidgetList.SelectedIndex;
        if (index < 0 || index >= _widgets.Length) return;
        var state = AppState.Current;
        if (state.Pid is null || state.Token is null) return;
        try
        {
            var fresh = await ApiClient.Shared.Widget(state.Pid,
                                               _widgets[index].Id, state.Token);
            _open = fresh;
            NameBox.Text = fresh.Name;
            SourceBox.Text = fresh.Source;
            HideAnswer();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnSave(object sender, RoutedEventArgs e)
    {
        var state = AppState.Current;
        if (state.Pid is null || state.Token is null) return;
        var name = NameBox.Text.Trim();
        if (name.Length == 0) return;
        try
        {
            _open = _open is null
                ? await ApiClient.Shared.CreateWidget(state.Pid, name,
                                               SourceBox.Text, state.Token)
                : await ApiClient.Shared.UpdateWidget(state.Pid, _open.Id, name,
                                               SourceBox.Text, state.Token);
            await LoadAsync();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnRun(object sender, RoutedEventArgs e)
    {
        var state = AppState.Current;
        if (state.Pid is null || state.Token is null || _open is null) return;
        try
        {
            var answer = await ApiClient.Shared.RunWidget(state.Pid, _open.Id,
                                                   state.Token);
            var lang = state.Language;
            AnswerStatus.Text = L10n.T($"wdg.status.{answer.Status}", lang);
            AnswerStatus.Visibility = Visibility.Visible;
            AnswerSaid.Text = answer.Said ?? "";
            AnswerSaid.Visibility = answer.Said is null ? Visibility.Collapsed
                                                        : Visibility.Visible;
            AnswerBody.Text = answer.Message ?? answer.Value?.ToString() ?? "";
            AnswerBody.Visibility = AnswerBody.Text.Length == 0
                ? Visibility.Collapsed : Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnRemove(object sender, RoutedEventArgs e)
    {
        var state = AppState.Current;
        if (state.Pid is null || state.Token is null || _open is null) return;
        try
        {
            await ApiClient.Shared.DeleteWidget(state.Pid, _open.Id, state.Token);
            _open = null;
            NameBox.Text = "";
            HideAnswer();
            await LoadAsync();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private void HideAnswer()
    {
        AnswerStatus.Visibility = Visibility.Collapsed;
        AnswerSaid.Visibility = Visibility.Collapsed;
        AnswerBody.Visibility = Visibility.Collapsed;
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
