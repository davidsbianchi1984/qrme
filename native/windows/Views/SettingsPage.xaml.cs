using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class SettingsPage : Page
{
    public sealed class ObjectionRow
    {
        public string Id { get; init; } = "";
        public string Status { get; init; } = "";
        public string Reason { get; init; } = "";
        public bool CanAttest { get; init; }
        public Visibility AttestVisibility =>
            CanAttest ? Visibility.Visible : Visibility.Collapsed;
    }

    public sealed class FeedbackRow
    {
        public string Line { get; init; } = "";
    }

    private static readonly string[] FeedbackCategories =
        { "idea", "improvement", "bug", "praise", "other" };

    private LanguageInfo[] _languages = Array.Empty<LanguageInfo>();
    private ProviderInfo[] _providers = Array.Empty<ProviderInfo>();
    private bool _loading;   // suppress SelectionChanged while populating

    private static readonly string[] RelationshipTypes =
        { "family", "grandchild", "friend", "romantic_partner",
          "professional", "fan", "stranger" };

    private readonly System.Collections.Generic.Dictionary<string, Slider>
        _dialSliders = new();

    public SettingsPage()
    {
        InitializeComponent();
        FeedbackCategory.ItemsSource = FeedbackCategories
            .Select(c => char.ToUpper(c[0]) + c[1..]).ToList();
        FeedbackCategory.SelectedIndex = 0;
        FeedbackRating.ItemsSource = new[] { "—", "1", "2", "3", "4", "5" };
        FeedbackRating.SelectedIndex = 0;
        RelTypeBox.ItemsSource = RelationshipTypes
            .Select(t => t.Replace('_', ' ')).ToList();
        RelTypeBox.SelectedIndex = 2;   // friend
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) => await Reload();

    private async System.Threading.Tasks.Task Reload()
    {
        var s = AppState.Current;
        _loading = true;
        try
        {
            _providers = (await ApiClient.Shared.Models()).Providers;
            ProviderBox.ItemsSource = _providers.Select(p =>
                $"{p.Label}  ({(p.Configured ? "ready" : "no key")})").ToList();
            var current = await ApiClient.Shared.ProfileModel(s.Pid!);
            var idx = Array.FindIndex(_providers, p => p.Name == current.Provider);
            ProviderBox.SelectedIndex = idx >= 0 ? idx : 0;
            EffectiveText.Text = $"Effective now: {current.Effective}";

            _languages = (await ApiClient.Shared.Languages()).Languages;
            LanguageBox.ItemsSource = _languages.Select(l => l.Label).ToList();
            var lang = await ApiClient.Shared.ProfileLanguage(s.Pid!);
            var lidx = Array.FindIndex(_languages, l => l.Code == lang.Language);
            LanguageBox.SelectedIndex = lidx >= 0 ? lidx : 0;
            PreTranslateToggle.IsOn = (lang.Mode ?? "pre") == "pre";
            s.RememberLanguage(lang.Language);   // chrome follows the profile
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { _loading = false; }

        try
        {
            var objections = await ApiClient.Shared.Objections(s.Pid!, s.Token!);
            ObjectionsList.ItemsSource = objections.Select(o => new ObjectionRow
            {
                Id = o.Id,
                Status = o.Status.ToUpper()
                         + (o.Reattested == 1 ? " · basis re-attested" : ""),
                Reason = o.Reason ?? "",
                CanAttest = o.Status == "open" && o.Reattested == 0,
            }).ToList();
            NoObjections.Visibility =
                objections.Length == 0 ? Visibility.Visible : Visibility.Collapsed;
        }
        catch (Exception ex) { ShowError(ex.Message); }

        await LoadFeedback();
        await LoadSteering();
    }

    private async System.Threading.Tasks.Task LoadSteering()
    {
        var s = AppState.Current;
        try
        {
            var hub = await ApiClient.Shared.SteeringHub(s.Pid!, s.Token!);
            SteeringDials.Children.Clear();
            _dialSliders.Clear();
            string? lastGroup = null;
            var groupLabels = new System.Collections.Generic.Dictionary<string, string>
            {
                ["system"] = "System", ["behavior"] = "Behavior",
                ["intimacy"] = "Intimacy (18+)",
            };
            foreach (var dial in hub.Dials)
            {
                if (dial.Group != lastGroup)
                {
                    SteeringDials.Children.Add(new TextBlock
                    {
                        Text = groupLabels.GetValueOrDefault(dial.Group, dial.Group),
                        FontSize = 12,
                        FontWeight = Microsoft.UI.Text.FontWeights.Bold,
                        Foreground = (Microsoft.UI.Xaml.Media.Brush)
                            Application.Current.Resources["QrmeBrandABrush"],
                    });
                    lastGroup = dial.Group;
                }
                var slider = new Slider
                {
                    Header = $"{dial.Label}  ({dial.Low} ↔ {dial.High})",
                    Minimum = dial.Min,
                    Maximum = dial.Max,
                    Value = hub.Values.GetValueOrDefault(dial.Name, 50),
                };
                _dialSliders[dial.Name] = slider;
                SteeringDials.Children.Add(slider);
            }
            AppearanceBox.Text = hub.Appearance.Description ?? "";
            BaseAgeBox.Text = hub.Age.BaseAge?.ToString() ?? "";
            AgingToggle.IsOn = hub.Age.AgingEnabled;
            if (hub.Age.EffectiveAge is { } eff)
            {
                EffectiveAgeText.Text = $"Effective age now: {eff}";
                EffectiveAgeText.Visibility = Visibility.Visible;
            }
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnApplySteering(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var values = _dialSliders.ToDictionary(kv => kv.Key,
                                                   kv => (int)kv.Value.Value);
            int? baseAge = int.TryParse(BaseAgeBox.Text.Trim(), out var n) ? n : null;
            var hub = await ApiClient.Shared.SetSteeringHub(
                s.Pid!, s.Token!, values, baseAge, AgingToggle.IsOn,
                AppearanceBox.Text.Trim() is { Length: > 0 } a ? a : null);
            if (hub.Age.EffectiveAge is { } eff)
            {
                EffectiveAgeText.Text = $"Effective age now: {eff}";
                EffectiveAgeText.Visibility = Visibility.Visible;
            }
            SteeringStatus.Text = "Steering applied — it rides on every reply.";
            SteeringStatus.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnSaveRelationship(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            if (s.InteractorId is null)
            {
                var created = await ApiClient.Shared.CreateInteractor("You");
                s.RememberInteractor(created.Id);
            }
            var type = RelationshipTypes[Math.Max(0, RelTypeBox.SelectedIndex)];
            var r = await ApiClient.Shared.SetRelationship(
                s.Pid!, s.Token!, s.InteractorId!, type,
                RelNicknameBox.Text.Trim(), RelToneBox.Text.Trim());
            RelStatus.Text = $"Saved — it now treats you as {r.RelationshipType.Replace('_', ' ')}.";
            RelStatus.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async System.Threading.Tasks.Task LoadFeedback()
    {
        try
        {
            var fb = await ApiClient.Shared.Feedback(AppState.Current.Token);
            if (fb.Total > 0)
            {
                var parts = FeedbackCategories
                    .Where(c => fb.Tally.TryGetValue(c, out var n) && n > 0)
                    .Select(c => $"{fb.Tally[c]} {c}");
                FeedbackTally.Text = "So far: " + string.Join(" · ", parts);
                FeedbackTally.Visibility = Visibility.Visible;
            }
            else FeedbackTally.Visibility = Visibility.Collapsed;

            var mine = fb.Mine.Select(f => new FeedbackRow
            {
                Line = $"[{f.Category}] {f.Message}  ·  {f.Status}",
            }).ToList();
            FeedbackMine.ItemsSource = mine;
            var hasMine = mine.Count > 0 ? Visibility.Visible : Visibility.Collapsed;
            FeedbackMineHeader.Visibility = hasMine;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnSendFeedback(object sender, RoutedEventArgs e)
    {
        var message = FeedbackMessage.Text.Trim();
        if (message.Length == 0) return;
        var cat = FeedbackCategories[Math.Max(0, FeedbackCategory.SelectedIndex)];
        int? rating = FeedbackRating.SelectedIndex >= 1 ? FeedbackRating.SelectedIndex : null;
        try
        {
            await ApiClient.Shared.SubmitFeedback(AppState.Current.Token, cat, message, rating);
            FeedbackMessage.Text = "";
            FeedbackRating.SelectedIndex = 0;
            FeedbackThanks.Text = "Thank you — sent.";
            FeedbackThanks.Visibility = Visibility.Visible;
            await LoadFeedback();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private string CurrentMode => PreTranslateToggle.IsOn ? "pre" : "on_demand";

    private async void OnLanguagePicked(object sender, SelectionChangedEventArgs e)
    {
        if (_loading) return;
        var idx = LanguageBox.SelectedIndex;
        if (idx < 0 || idx >= _languages.Length) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.SetLanguage(s.Pid!, s.Token!, _languages[idx].Code, CurrentMode);
            s.RememberLanguage(_languages[idx].Code);
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnModeToggled(object sender, RoutedEventArgs e)
    {
        if (_loading) return;
        var idx = LanguageBox.SelectedIndex;
        if (idx < 0 || idx >= _languages.Length) return;
        var s = AppState.Current;
        try { await ApiClient.Shared.SetLanguage(s.Pid!, s.Token!, _languages[idx].Code, CurrentMode); }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnTranslate(object sender, RoutedEventArgs e)
    {
        var text = TranslateBox.Text.Trim();
        if (text.Length == 0) return;
        var s = AppState.Current;
        try
        {
            var r = await ApiClient.Shared.Translate(s.Pid!, s.Token!, text);
            TranslateOut.Text = r.Translation;
            TranslateOut.Visibility = Visibility.Visible;
            TranslateEngine.Text = $"engine: {r.Engine}" +
                (r.Note is { } n ? $" — {n}" : "");
            TranslateEngine.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnProviderPicked(object sender, SelectionChangedEventArgs e)
    {
        if (_loading) return;
        var idx = ProviderBox.SelectedIndex;
        if (idx < 0 || idx >= _providers.Length) return;
        var s = AppState.Current;
        try
        {
            var m = await ApiClient.Shared.SetModel(s.Pid!, s.Token!,
                                                    _providers[idx].Name);
            EffectiveText.Text = $"Effective now: {m.Effective}";
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnAttest(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string oid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.Attest(s.Pid!, oid, s.Token!);
            await Reload();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
