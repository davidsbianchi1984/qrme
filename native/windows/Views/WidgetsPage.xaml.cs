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
    }

    private async System.Threading.Tasks.Task LoadAsync()
    {
        var state = AppState.Current;
        if (state.ProfileId is null || state.Token is null) return;
        try
        {
            _caps = await state.Api.WidgetLimits();
            NoBox.Visibility = _caps.Available ? Visibility.Collapsed
                                               : Visibility.Visible;
            RunButton.IsEnabled = _caps.Available;
            _widgets = await state.Api.Widgets(state.ProfileId, state.Token);
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
        if (state.ProfileId is null || state.Token is null) return;
        try
        {
            var fresh = await state.Api.Widget(state.ProfileId,
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
        if (state.ProfileId is null || state.Token is null) return;
        var name = NameBox.Text.Trim();
        if (name.Length == 0) return;
        try
        {
            _open = _open is null
                ? await state.Api.CreateWidget(state.ProfileId, name,
                                               SourceBox.Text, state.Token)
                : await state.Api.UpdateWidget(state.ProfileId, _open.Id, name,
                                               SourceBox.Text, state.Token);
            await LoadAsync();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnRun(object sender, RoutedEventArgs e)
    {
        var state = AppState.Current;
        if (state.ProfileId is null || state.Token is null || _open is null) return;
        try
        {
            var answer = await state.Api.RunWidget(state.ProfileId, _open.Id,
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
        if (state.ProfileId is null || state.Token is null || _open is null) return;
        try
        {
            await state.Api.DeleteWidget(state.ProfileId, _open.Id, state.Token);
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
