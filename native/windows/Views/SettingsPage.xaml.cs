using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
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
        // The card reads three stored choices, so it has to be told when
        // the page appears rather than only when a button is pressed.
        Loaded += (_, _) => RefreshProblemsCard();
        FeedbackCategory.ItemsSource = FeedbackCategories
            .Select(c => char.ToUpper(c[0]) + c[1..]).ToList();
        FeedbackCategory.SelectedIndex = 0;
        FeedbackRating.ItemsSource = new[] { "—", "1", "2", "3", "4", "5" };
        FeedbackRating.SelectedIndex = 0;
        // `t.Replace('_', ' ')` rendered the API's member as if it were a
        // word. `OnSaveRelationship` reads the value back by index, so the
        // visible text is free to be the console's own `rel.t.*` wording.
        RelTypeBox.ItemsSource = RelationshipTypes
            .Select(t => L10n.T($"ns.rel.t.{t}")).ToList();
        RelTypeBox.SelectedIndex = 2;   // friend
        Localize();
    }

    /// Every visible string on the blocks this round covers, set from L10n
    /// rather than from the markup. The steering, relationship and feedback
    /// panels below still carry theirs in XAML and are counted as such.
    private void Localize()
    {
        var lang = AppState.Current.Language;
        TitleText.Text = L10n.T("tab.settings", lang);

        ModelHead.Text = L10n.T("ns.model", lang);
        ModelSub.Text = L10n.T("ns.model.sub", lang);

        LangHead.Text = L10n.T("ns.lang", lang);
        LangSub.Text = L10n.T("ns.lang.sub", lang);
        PreTranslateToggle.Header = L10n.T("ns.lang.pre", lang);
        PreTranslateToggle.OnContent = L10n.T("ns.lang.pre.on", lang);
        PreTranslateToggle.OffContent = L10n.T("ns.lang.pre.off", lang);
        TranslateBox.Header = L10n.T("ns.tr", lang);
        TranslateBox.PlaceholderText = L10n.T("ns.tr.ph", lang);
        TranslateButton.Content = L10n.T("action.translate", lang);

        WmHead.Text = L10n.T("ns.wm", lang);
        WmSub.Text = L10n.T("ns.wm.sub", lang);
        WatermarkMarkBox.Header = L10n.T("ns.wm.mark", lang);
        WatermarkLabelBox.Header = L10n.T("ns.wm.label", lang);
        WatermarkLabelBox.PlaceholderText = L10n.Fill(
            "ns.wm.label.ph", lang, ("name", AppState.Current.DisplayName));
        WatermarkSaveButton.Content = L10n.T("ns.wm.save", lang);
        WatermarkResetButton.Content = L10n.T("ns.wm.reset", lang);
        WatermarkSaved.Text = L10n.T("ns.wm.saved", lang);

        ObjHead.Text = L10n.T("ns.obj", lang);
        NoObjections.Text = L10n.T("ns.obj.none", lang);
        AttestButton.Content = L10n.T("ns.obj.attest", lang);

        WhoHead.Text = L10n.T("ns.who", lang);
        WhoSub.Text = L10n.T("ns.who.sub", lang);
        RecoverBox.PlaceholderText = L10n.T("ns.who.ph", lang);
        RecoverButton.Content = L10n.T("ns.who.check", lang);

        ObjectHead.Text = L10n.T("ns.object", lang);
        ObjectSub.Text = L10n.T("ns.object.sub", lang);
        ObjectProfileBox.PlaceholderText = L10n.T("ns.object.pid", lang);
        ObjectContactBox.PlaceholderText = L10n.T("ns.object.contact", lang);
        ObjectReasonBox.PlaceholderText = L10n.T("ns.object.reason", lang);
        ObjectButton.Content = L10n.T("ns.object.go", lang);

        StHead.Text = L10n.T("ns.st", lang);
        StSub.Text = L10n.Fill("ns.st.sub", lang,
                               ("name", L10n.T("ns.st.the_profile", lang)));
        AppearanceBox.Header = L10n.T("ns.st.appearance", lang);
        AppearanceBox.PlaceholderText = L10n.T("ns.st.appearance.ph", lang);
        BaseAgeBox.Header = L10n.T("ns.st.baseage", lang);
        AgingToggle.Header = L10n.T("ns.st.aging", lang);
        ApplySteeringButton.Content = L10n.T("ns.st.apply", lang);

        RelHead.Text = L10n.T("ns.rel", lang);
        RelSub.Text = L10n.T("ns.rel.sub", lang);
        RelTypeBox.Header = L10n.T("ns.rel.type", lang);
        RelNicknameBox.PlaceholderText = L10n.T("ns.rel.nick.ph", lang);
        RelToneBox.PlaceholderText = L10n.T("ns.rel.tone.ph", lang);
        SaveRelButton.Content = L10n.T("ns.rel.save", lang);

        FbHead.Text = L10n.T("ns.fb", lang);
        FbSub.Text = L10n.T("ns.fb.sub", lang);
        FeedbackCategory.Header = L10n.T("ns.fb.cat", lang);
        FeedbackMessage.PlaceholderText = L10n.T("ns.fb.msg.ph", lang);
        FeedbackRating.Header = L10n.T("ns.fb.rating.opt", lang);
        FeedbackSend.Content = L10n.T("ns.fb.send", lang);
        FeedbackMineHeader.Text = L10n.T("ns.fb.mine", lang);

        PrHead.Text = L10n.T("ns.pr", lang);
        ProblemsYes.Content = L10n.T("ns.pr.send", lang);
        ProblemsNo.Content = L10n.T("ns.pr.dont", lang);
        ProblemsSwitch.Header = L10n.T("ns.pr.toggle", lang);
        ProblemsPreviewButton.Content = L10n.T("ns.pr.show", lang);
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
                $"{p.Label}  ({L10n.T(p.Configured ? "nvoi.ready" : "ns.model.nokeyword")})").ToList();
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
        await LoadWatermark();
    }

    private async System.Threading.Tasks.Task LoadWatermark()
    {
        var s = AppState.Current;
        try
        {
            var d = await ApiClient.Shared.GetWatermarkDesign(s.Pid!);
            WatermarkLine.Text = d.Line;
            WatermarkResetButton.Visibility =
                d.Custom ? Visibility.Visible : Visibility.Collapsed;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnSaveWatermark(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var d = await ApiClient.Shared.SetWatermarkDesign(
                s.Pid!, s.Token!, WatermarkMarkBox.Text.Trim(),
                WatermarkLabelBox.Text.Trim());
            WatermarkLine.Text = d.Line;
            WatermarkResetButton.Visibility =
                d.Custom ? Visibility.Visible : Visibility.Collapsed;
            WatermarkSaved.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnResetWatermark(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var d = await ApiClient.Shared.SetWatermarkDesign(
                s.Pid!, s.Token!, null, null);
            WatermarkLine.Text = d.Line;
            WatermarkMarkBox.Text = "";
            WatermarkLabelBox.Text = "";
            WatermarkResetButton.Visibility = Visibility.Collapsed;
            WatermarkSaved.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { ShowError(ex.Message); }
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
                s.RememberInteractor(created.Id, token: created.Token);
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

    // MARK: Object to a profile — the public's half of governance
    //
    // `open_objection` takes no credential, and says why: the objecting party
    // need not own an account. Somebody who has found a synthetic profile of
    // themselves therefore has no console either, and this shell carried only
    // the owner's side of the same feature until 0.23.0.

    private async void OnRaiseObjection(object sender, RoutedEventArgs e)
    {
        var pid = ObjectProfileBox.Text?.Trim() ?? "";
        var why = ObjectReasonBox.Text?.Trim() ?? "";
        if (pid.Length == 0 || why.Length == 0)
        {
            ObjectVerdict.Text = "A profile id and a reason are both needed.";
            return;
        }
        try
        {
            var r = await ApiClient.Shared.OpenObjection(
                pid, ObjectContactBox.Text?.Trim() ?? "", why);
            // Restricted immediately, pending review — the part the person
            // raising it needs told, because the remedy is now rather than
            // after somebody gets round to it.
            ObjectVerdict.Text =
                $"Raised. The profile is {r.ProfileStatus ?? "restricted"} pending review.";
            ObjectNote.Text = r.Note ?? "";
        }
        catch (System.Exception ex)
        {
            ObjectVerdict.Text = ex.Message;
            ObjectNote.Text = "";
        }
    }

    // MARK: Who wrote this? — extract and reconstruct

    /// <summary>
    /// Never a bare yes: the counts travel with the claim so it can be checked,
    /// and below the threshold nobody is named at all — ordinary phrases travel
    /// between unrelated texts, and a coincidence must not read as an accusation.
    /// </summary>
    private async void OnRecover(object sender, RoutedEventArgs e)
    {
        var text = RecoverBox.Text;
        if (string.IsNullOrWhiteSpace(text)) return;
        RecoverButton.IsEnabled = false;
        try
        {
            var r = await ApiClient.Shared.RecoverWatermark(text);
            if (r.Recovered && r.ProfileId is { } pid)
            {
                RecoverVerdict.Text = r.Verbatim
                    ? $"Written by {pid}, unaltered."
                    : $"Written by {pid} — altered since.";
                RecoverVerdict.Foreground = new SolidColorBrush(r.Verbatim
                    ? Microsoft.UI.Colors.MediumSpringGreen
                    : Microsoft.UI.Colors.Orange);
                RecoverCounts.Text =
                    $"{r.MatchedWindows} of {r.StoredWindows} passages matched · "
                  + $"similarity {r.Similarity}";
                RecoverDetail.Text = string.Join("  ", new[]
                {
                    r.Display?.Line, r.Disclosure, r.Method,
                }.Where(x => !string.IsNullOrEmpty(x)));
            }
            else
            {
                RecoverVerdict.Text = r.Reason ?? "No profile here produced this text.";
                RecoverVerdict.Foreground = new SolidColorBrush(
                    Microsoft.UI.Colors.Gray);
                RecoverCounts.Text = r.BestSimilarity is { } best && r.Threshold is { } th
                    ? $"closest overlap {best}, below the {th} threshold for naming anyone"
                    : "";
                RecoverDetail.Text = r.Method ?? "";
            }
            RecoverVerdict.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            RecoverVerdict.Text = ex.Message;
            RecoverVerdict.Foreground = new SolidColorBrush(Microsoft.UI.Colors.OrangeRed);
            RecoverVerdict.Visibility = Visibility.Visible;
        }
        finally { RecoverButton.IsEnabled = true; }
    }

    // ---- When something breaks ------------------------------------------
    //
    // The notice that has to be answered before anything leaves this machine.
    // The sending half landed last round and answered AwaitingNotice on every
    // launch because there was no surface to answer it on — safe to be wrong
    // in that direction, and still wrong: a mechanism nobody can reach is a
    // mechanism nobody chose.
    //
    // The preview is built by Problems.Report, the same call the sender posts,
    // so what is on screen is the payload rather than a description of it. A
    // preview that could drift from the message would be worse than none,
    // because it would look like a promise.

    private void RefreshProblemsCard()
    {
        var hasCollector = Problems.CollectorUrl().Length > 0;
        var answered = Problems.NoticeAnswered();

        if (!hasCollector)
        {
            // Not a failure and not a thing to hide: this build has no address
            // compiled in, so there is nothing to consent to.
            ProblemsExplain.Text = L10n.T("ns.pr.nowhere");
            ProblemsAsk.Visibility = Visibility.Collapsed;
            ProblemsSwitch.Visibility = Visibility.Collapsed;
            return;
        }
        if (!answered)
        {
            // Three wordings of one sentence across three shells before
            // this round; one row now.
            ProblemsExplain.Text = L10n.T("ns.pr.explain");
            ProblemsAsk.Visibility = Visibility.Visible;
            ProblemsSwitch.Visibility = Visibility.Collapsed;
            return;
        }
        ProblemsExplain.Text = L10n.T("ns.pr.short");
        ProblemsAsk.Visibility = Visibility.Collapsed;
        ProblemsSwitch.Visibility = Visibility.Visible;
        ProblemsSwitch.IsOn = Problems.SendingEnabled();
    }

    private async void OnProblemsYes(object sender, RoutedEventArgs e)
    {
        Problems.AnswerNotice(true);
        RefreshProblemsCard();
        // The first moment a send is permitted. Doing it now rather than at
        // the next launch means the person who just agreed watches the buffer
        // drain, instead of being told something happened later.
        await Problems.Send();
    }

    private void OnProblemsNo(object sender, RoutedEventArgs e)
    {
        Problems.AnswerNotice(false);
        RefreshProblemsCard();
    }

    private void OnProblemsToggled(object sender, RoutedEventArgs e) =>
        Problems.SetSending(ProblemsSwitch.IsOn);

    private void OnProblemsPreview(object sender, RoutedEventArgs e)
    {
        if (ProblemsPreview.Visibility == Visibility.Visible)
        {
            ProblemsPreview.Visibility = Visibility.Collapsed;
            ProblemsPreviewButton.Content = L10n.T("ns.pr.show");
            return;
        }
        var owed = Problems.Report()["problems"]
            as List<Dictionary<string, object>> ?? new();
        ProblemsPreview.Text = owed.Count == 0
            ? L10n.T("ns.pr.owed")
            : string.Join("\n", owed.Select(r =>
                $"{r["op"]} → {r["status"]}  ×{r["count"]}  {r["day"]}"));
        ProblemsPreview.Visibility = Visibility.Visible;
        ProblemsPreviewButton.Content = L10n.T("ns.pr.hide");
    }
}
