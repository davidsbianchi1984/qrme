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
        // The label rides on the row, not on a page field: the button lives
        // inside a DataTemplate, so there is no `AttestButton` to reach for.
        public string AttestLabel { get; init; } = "";
        public Visibility AttestVisibility =>
            CanAttest ? Visibility.Visible : Visibility.Collapsed;
    }

    /// <summary>One row of the privilege roster. The labels ride on the row
    /// rather than on a page field, because the controls live inside a
    /// DataTemplate — there is no per-row button to reach for.</summary>
    public sealed class MayRow
    {
        public string Name { get; init; } = "";
        public string MayDo { get; init; } = "";
        public string Keeps { get; init; } = "";
        public string NeedsText { get; init; } = "";
        public string OthersText { get; init; } = "";
        public string StateText { get; init; } = "";
        public string ButtonLabel { get; init; } = "";
        public bool Chosen { get; init; }
        public bool TouchesOthers { get; init; }
        public Visibility NeedsVisibility =>
            NeedsText.Length > 0 ? Visibility.Visible : Visibility.Collapsed;
        public Visibility OthersVisibility =>
            TouchesOthers ? Visibility.Visible : Visibility.Collapsed;
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
        KeyHead.Text = L10n.T("set.key", lang);
        KeyLead.Text = L10n.T("set.key.lead", lang);
        KeyBox.Header = L10n.T("set.key.label", lang);
        KeyBox.PlaceholderText = L10n.T("set.key.ph", lang);
        SaveKeyButton.Content = L10n.T("action.save", lang);
        KeyBox.Password = AppState.Current.LlmKey;

        InviteHead.Text = L10n.T("set.invite", lang);
        InviteLead.Text = L10n.T("set.invite.lead", lang);
        InviteBox.PlaceholderText = L10n.T("set.invite", lang);
        SaveInviteButton.Content = L10n.T("action.save", lang);
        InviteBox.Password = AppState.Current.SignupKey;

        LangHead.Text = L10n.T("ns.lang", lang);
        LangSub.Text = L10n.T("ns.lang.sub", lang);
        PreTranslateToggle.Header = L10n.T("ns.lang.pre", lang);
        PreTranslateToggle.OnContent = L10n.T("ns.lang.pre.on", lang);
        PreTranslateToggle.OffContent = L10n.T("ns.lang.pre.off", lang);
        PreTranslateSub.Text = L10n.T("ns.lang.pre.sub", lang);
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

        SideHead.Text = L10n.T("ns.side", lang);
        SideSub.Text = L10n.T("ns.side.sub", lang);
        SideReadButton.Content = L10n.T("ns.side.read", lang);
        SideTakeButton.Content = L10n.T("ns.side.take", lang);
        SideNotNowButton.Content = L10n.T("counter.decline", lang);
        SideShowButton.Content = L10n.T("ns.side.show", lang);

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

        AccHead.Text = L10n.T("ns.acc", lang);
        AccLead.Text = L10n.T("ns.acc.lead", lang);
        AccNeedsTitle.Text = L10n.T("ns.acc.needs.title", lang);
        AccNeedsList.Text = string.Join("\n", new[]
        {
            "blind", "deaf", "mute", "motor", "cognitive", "dyslexia", "motion",
        }.Select(need => "• " + L10n.T($"ns.acc.needs.{need}", lang)));
        AccNeedsMore.Text = L10n.T("ns.acc.needs.more", lang);
        AccDoing.PlaceholderText = L10n.T("ns.acc.doing.ph", lang);
        AccWall.PlaceholderText = L10n.T("ns.acc.wall.ph", lang);
        AccHelp.PlaceholderText = L10n.T("ns.acc.help.ph", lang);
        AccSend.Content = L10n.T("ns.acc.send", lang);
        AccReviewerBox.PlaceholderText = L10n.T("ns.acc.token.ph", lang);
        AccLoad.Content = L10n.T("ns.acc.load", lang);
        AccEmpty.Text = L10n.T("ns.acc.none", lang);

        MtrHead.Text = L10n.T("ns.mtr", lang);
        MtrLead.Text = L10n.T("ns.mtr.lead", lang);
        MtrConcerns.ItemsSource = new[]
        {
            L10n.T("ns.mtr.app", lang), L10n.T("ns.mtr.profiles", lang),
            L10n.T("ns.mtr.platform", lang),
        };
        MtrSend.Content = L10n.T("ns.mtr.send", lang);
        MtrClaimNote.Text = L10n.T("ns.mtr.claim", lang);
        MtrWasIt.Content = L10n.T("ns.mtr.wasit", lang);
        MtrNotIt.Content = L10n.T("ns.mtr.notit", lang);
        MtrSettle.Content = L10n.T("ns.mtr.settle", lang);
        MtrEmpty.Text = L10n.T("ns.mtr.empty", lang);
        MtrReviewerBox.PlaceholderText = L10n.T("ns.acc.token.ph", lang);
        MtrQueueLoad.Content = L10n.T("ns.mtr.queue", lang);
        MtrTake.Content = L10n.T("ns.mtr.take", lang);

        PrHead.Text = L10n.T("ns.pr", lang);
        ProblemsYes.Content = L10n.T("ns.pr.send", lang);
        ProblemsNo.Content = L10n.T("ns.pr.dont", lang);
        ProblemsSwitch.Header = L10n.T("ns.pr.toggle", lang);
        ProblemsPreviewButton.Content = L10n.T("ns.pr.show", lang);
        ProblemsServerTitle.Text = L10n.T("prob.server");
        ProblemsKeyBox.PlaceholderText = L10n.T("prob.key.ph");
        ProblemsFetchButton.Content = L10n.T("prob.fetch");
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
            EffectiveText.Text = L10n.Fill("ns.model.effective",
                AppState.Current.Language, ("name", current.Effective));

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
                         + (o.Reattested ? " · basis re-attested" : ""),
                Reason = o.Reason ?? "",
                CanAttest = o.Status == "open" && !o.Reattested,
                AttestLabel = L10n.T("ns.obj.attest", AppState.Current.Language),
            }).ToList();
            NoObjections.Visibility =
                objections.Length == 0 ? Visibility.Visible : Visibility.Collapsed;
        }
        catch (Exception ex) { ShowError(ex.Message); }

        await LoadFeedback();
        await LoadSteering();
        await LoadWatermark();
        await LoadMay();
    }

    /// <summary>What this profile's agent may do. Every row, including the
    /// ones nobody has turned on — those are the half that makes the list mean
    /// anything.</summary>
    private async System.Threading.Tasks.Task LoadMay()
    {
        var s = AppState.Current;
        var lang = s.Language;
        MayHead.Text = L10n.T("may.title", lang);
        MayLead.Text = L10n.T("may.lead", lang);
        try
        {
            var rows = await ApiClient.Shared.Privileges(s.Pid!, s.Token);
            MayList.ItemsSource = rows.Select(r => new MayRow
            {
                Name = r.Name,
                MayDo = r.MayDo,
                Keeps = L10n.T("may.keeps", lang) + " "
                        + (r.Holds.Length > 0 ? r.Holds
                           : L10n.T("may.keeps.nothing", lang)),
                NeedsText = r.Needs.Length > 0
                    ? L10n.T("may.needs", lang) + " " + string.Join(" · ", r.Needs)
                    : "",
                OthersText = L10n.T("may.others", lang),
                TouchesOthers = r.TouchesOthers,
                Chosen = r.Chosen,
                StateText = r.Chosen ? L10n.T("may.on", lang)
                                     : L10n.T("may.off", lang),
                ButtonLabel = r.Chosen ? L10n.T("may.turnoff", lang)
                                       : L10n.T("may.turnon", lang),
            }).ToList();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    /// <summary>The whole roster comes back from the press, so the list is
    /// replaced rather than patched.</summary>
    private async void OnMayToggle(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var name = (string)((Button)sender).Tag;
        var row = ((IEnumerable<MayRow>)MayList.ItemsSource)
            .First(r => r.Name == name);
        try
        {
            await ApiClient.Shared.AllowPrivilege(s.Pid!, name, !row.Chosen,
                                                  s.Token!);
            await LoadMay();
        }
        catch (Exception ex) { ShowError(ex.Message); }
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
                // Labels, not ids. The keys are what the steering API
                // matches on and stay English; the words are read.
                ["system"] = L10n.T("ns.st.g.system"),
                ["behavior"] = L10n.T("ns.st.g.behavior"),
                ["intimacy"] = L10n.T("ns.st.g.intimacy"),
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
            _steeringLocked = hub.Lock is not null;
            ApplySteeringButton.IsEnabled = !_steeringLocked;
            SteeringLockButton.Content = _steeringLocked
                ? L10n.T("ns.st.unlock") : L10n.T("ns.st.lock");
            SteeringLockedText.Text = L10n.T("ns.st.locked");
            SteeringLockedText.Visibility = _steeringLocked
                ? Visibility.Visible : Visibility.Collapsed;
            AppearanceBox.Text = hub.Appearance.Description ?? "";
            BaseAgeBox.Text = hub.Age.BaseAge?.ToString() ?? "";
            AgingToggle.IsOn = hub.Age.AgingEnabled;
            if (hub.Age.EffectiveAge is { } eff)
            {
                EffectiveAgeText.Text = L10n.Fill("ns.st.effective",
                    AppState.Current.Language, ("age", $"{eff}"));
                EffectiveAgeText.Visibility = Visibility.Visible;
            }
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private bool _steeringLocked;

    private async void OnSteeringLock(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            if (_steeringLocked)
                await ApiClient.Shared.UnlockSteering(s.Pid!, s.Token!);
            else
                await ApiClient.Shared.LockSteering(s.Pid!, s.Token!);
            await LoadSteering();
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
                EffectiveAgeText.Text = L10n.Fill("ns.st.effective",
                    AppState.Current.Language, ("age", $"{eff}"));
                EffectiveAgeText.Visibility = Visibility.Visible;
            }
            SteeringStatus.Text = L10n.T("ns.st.applied");
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
            RelStatus.Text = L10n.Fill("ns.rel.saved", AppState.Current.Language,
                ("type", r.RelationshipType.Replace('_', ' ')));
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
                FeedbackTally.Text = L10n.T("fb.sofar").Replace("{list}", string.Join(" · ", parts));
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
            FeedbackThanks.Text = L10n.T("fb.thanks");
            FeedbackThanks.Visibility = Visibility.Visible;
            await LoadFeedback();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    // The accessibility door: tokenless on purpose — the person it exists
    // for may be the person the signup shut out.
    private async void OnSendAccessReport(object sender, RoutedEventArgs e)
    {
        var doing = AccDoing.Text.Trim();
        var wall = AccWall.Text.Trim();
        if (doing.Length == 0 || wall.Length == 0) return;
        try
        {
            await ApiClient.Shared.SendAccessReport(
                doing, wall, AccHelp.Text.Trim(), AppState.Current.Language);
            AccDoing.Text = ""; AccWall.Text = ""; AccHelp.Text = "";
            AccThanks.Text = L10n.T("ns.acc.sent", AppState.Current.Language);
            AccThanks.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnLoadAccessReports(object sender, RoutedEventArgs e)
    {
        try
        {
            var state = await ApiClient.Shared.AccessReports(AccReviewerBox.Password.Trim());
            AccEmpty.Visibility = state.Total == 0 ? Visibility.Visible : Visibility.Collapsed;
            AccReportsList.ItemsSource = state.Reports.Take(6).Select(r => new FeedbackRow
            {
                Line = $"{r.Doing} — {r.Wall}"
                       + (r.Help is { Length: > 0 } h ? $" ({h})" : "")
                       + $" · {r.Lang} · {r.CreatedAt}",
            }).ToList();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    // Somebody's matter. `_matterClaim` lives on the page and is written
    // nowhere else: it is the single thing that reads an anonymous matter
    // again, and the backend deliberately keeps only its hash.
    private string _matterClaim = "";
    private Matter? _matter;

    private static readonly string[] MatterConcerns =
        { "app", "profiles", "platform" };

    private void ShowMatter(Matter matter)
    {
        var lang = AppState.Current.Language;
        _matter = matter;
        MtrStanding.Text = L10n.T($"ns.mtr.st.{matter.Standing}", lang);
        MtrAnswer.Text = matter.Answer;
        // `answered` is drawn as a question, never as a tick: the server
        // refuses to let the help box settle anything, and a page that showed
        // it as done would put the closure back that the server took out.
        var waiting = matter.Standing == "answered"
            ? Visibility.Visible : Visibility.Collapsed;
        MtrWasIt.Visibility = waiting;
        MtrNotIt.Visibility = waiting;
        MtrOffered.Text = matter.Offered is { Length: > 0 } o
            ? L10n.T("ns.mtr.offered", lang) + " " + o : "";
    }

    private async void OnRaiseMatter(object sender, RoutedEventArgs e)
    {
        var trouble = MtrTrouble.Text.Trim();
        if (trouble.Length == 0) return;
        try
        {
            var index = Math.Max(0, MtrConcerns.SelectedIndex);
            var matter = await ApiClient.Shared.RaiseMatter(
                trouble, MatterConcerns[index]);
            _matterClaim = matter.Claim ?? "";
            MtrClaim.Text = _matterClaim;
            MtrClaimNote.Visibility = _matterClaim.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;
            MtrTrouble.Text = "";
            ShowMatter(matter);
            await LoadMyMatters();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async Task LoadMyMatters()
    {
        var lang = AppState.Current.Language;
        try
        {
            var listed = await ApiClient.Shared.MyMatters(null);
            MtrEmpty.Visibility = listed.MyMatters.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            MtrMineList.ItemsSource = listed.MyMatters.Take(6).Select(m => new FeedbackRow
            {
                Line = $"{m.Trouble} — " + L10n.T($"ns.mtr.st.{m.Standing}", lang),
            }).ToList();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnMatterWasIt(object sender, RoutedEventArgs e)
    {
        if (_matter is null) return;
        try
        {
            ShowMatter(await ApiClient.Shared.SettleMatter(
                _matter.Id, _matter.Answer, true, null, _matterClaim));
            await LoadMyMatters();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnMatterNotIt(object sender, RoutedEventArgs e)
    {
        if (_matter is null) return;
        try
        {
            ShowMatter(await ApiClient.Shared.RejectMatterAnswer(
                _matter.Id, null, _matterClaim));
            await LoadMyMatters();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnSettleMatter(object sender, RoutedEventArgs e)
    {
        if (_matter is null) return;
        var answer = MtrSettleText.Text.Trim();
        if (answer.Length == 0) return;
        try
        {
            ShowMatter(await ApiClient.Shared.SettleMatter(
                _matter.Id, answer, false, null, _matterClaim));
            MtrSettleText.Text = "";
            await LoadMyMatters();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnLoadMatterQueue(object sender, RoutedEventArgs e)
    {
        var lang = AppState.Current.Language;
        try
        {
            var queue = await ApiClient.Shared.MatterQueue(
                MtrReviewerBox.Password.Trim());
            MtrQueueList.ItemsSource = queue.Unsettled.Take(6).Select(m => new FeedbackRow
            {
                Line = $"{m.Trouble} — " + L10n.T($"ns.mtr.st.{m.Standing}", lang),
            }).ToList();
            if (queue.Unsettled.Length > 0) _matter = queue.Unsettled[0];
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnTakeMatter(object sender, RoutedEventArgs e)
    {
        if (_matter is null) return;
        var reviewer = MtrReviewerBox.Password.Trim();
        try
        {
            await ApiClient.Shared.TakeMatter(_matter.Id, reviewer);
            await ApiClient.Shared.RecordMatterStep(
                _matter.Id, "handed_to_a_person", "", reviewer);
            // Read it back the way its raiser will see it, not the way the
            // queue does.
            if (_matterClaim.Length > 0)
                ShowMatter(await ApiClient.Shared.Matter(_matter.Id, null,
                                                         _matterClaim));
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
            TranslateEngine.Text = L10n.Fill("ns.tr.engine",
                AppState.Current.Language, ("engine", r.Engine)) +
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
            EffectiveText.Text = L10n.Fill("ns.model.effective",
                AppState.Current.Language, ("name", m.Effective));
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
            ObjStatus.Text = L10n.T("ns.obj.attested",
                AppState.Current.Language);
            ObjStatus.Visibility = Visibility.Visible;
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
            ObjectVerdict.Text = L10n.T("ns.pr.needboth");
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
                L10n.Fill("ns.object.raised", AppState.Current.Language,
                          ("status", r.ProfileStatus ?? "restricted"));
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
    /// <summary>How much of this person's talking here went to a profile
    /// rather than to a person. Nothing is pushed and nothing opens itself:
    /// the counts appear because somebody pressed for them.</summary>
    private async void OnReadMyCounts(object sender, RoutedEventArgs e)
    {
        var who = AppState.Current.InteractorId;
        if (string.IsNullOrEmpty(who))
        {
            SideNote.Text = L10n.T("ns.side.signin");
            return;
        }
        SideReadButton.IsEnabled = false;
        try
        {
            var s = await ApiClient.Shared.Solitude(who);
            SideCounts.Text = $"{L10n.T("ns.side.toprofiles")} {s.Turns.ToProfiles}"
                            + $"   {L10n.T("ns.side.topeople")} {s.Turns.ToPeople}";
            // The server's own sentence, shown rather than paraphrased.
            // Rewording it here is how a count becomes a verdict.
            SideNote.Text = s.Note;
            SideWhy.Text = s.Offer?.Why ?? "";
            SideChoice.Visibility = s.Offer?.State == "available"
                ? Visibility.Visible : Visibility.Collapsed;
            SideShowButton.Visibility = s.Offer?.State == "accepted"
                ? Visibility.Visible : Visibility.Collapsed;
            if (s.Offer?.State == "declined") SideWhy.Text = L10n.T("ns.side.declined");
        }
        finally { SideReadButton.IsEnabled = true; }
    }

    private async void OnTakeTheDoor(object sender, RoutedEventArgs e) => await Decide(true);

    /// <summary>Closing the door is recorded too, so the offer is not made a
    /// second time. An offer somebody declined that reappears next month is
    /// the product overriding an answer it already got.</summary>
    private async void OnCloseTheDoor(object sender, RoutedEventArgs e) => await Decide(false);

    private async System.Threading.Tasks.Task Decide(bool accept)
    {
        var who = AppState.Current.InteractorId;
        if (string.IsNullOrEmpty(who)) return;
        await ApiClient.Shared.SolitudeHandoff(who, accept);
        OnReadMyCounts(this, new RoutedEventArgs());
    }

    /// <summary>What would travel, readable before it does. A referral
    /// somebody cannot look at is a referral they did not really consent
    /// to.</summary>
    private async void OnShowWhatWent(object sender, RoutedEventArgs e)
    {
        var who = AppState.Current.InteractorId;
        if (string.IsNullOrEmpty(who)) return;
        var r = await ApiClient.Shared.SolitudeReferral(who);
        SideReferral.Text = $"{r.Ref}   {L10n.T("ns.side.thatisall")}";
    }

    private async void OnRecover(object sender, RoutedEventArgs e)
    {
        var text = RecoverBox.Text;
        if (string.IsNullOrWhiteSpace(text)) return;
        RecoverButton.IsEnabled = false;
        RecoverVerdict.Text = L10n.T("ns.who.checking",
            AppState.Current.Language);
        try
        {
            var r = await ApiClient.Shared.RecoverWatermark(text);
            if (r.Recovered && r.ProfileId is { } pid)
            {
                RecoverVerdict.Text = L10n.Fill(
                    r.Verbatim ? "ns.who.by" : "ns.who.by.altered",
                    AppState.Current.Language, ("id", pid));
                RecoverVerdict.Foreground = new SolidColorBrush(r.Verbatim
                    ? Microsoft.UI.Colors.MediumSpringGreen
                    : Microsoft.UI.Colors.Orange);
                RecoverCounts.Text = L10n.Fill("ns.who.matched",
                    AppState.Current.Language,
                    ("matched", $"{r.MatchedWindows}"),
                    ("stored", $"{r.StoredWindows}"))
                  + $" · similarity {r.Similarity}";
                RecoverDetail.Text = string.Join("  ", new[]
                {
                    r.Display?.Line, r.Disclosure, r.Method,
                }.Where(x => !string.IsNullOrEmpty(x)));
            }
            else
            {
                RecoverVerdict.Text = r.Reason ?? L10n.T("ns.who.none");
                RecoverVerdict.Foreground = new SolidColorBrush(
                    Microsoft.UI.Colors.Gray);
                RecoverCounts.Text = r.BestSimilarity is { } best && r.Threshold is { } th
                    ? L10n.Fill("ns.who.below", AppState.Current.Language,
                                ("best", $"{best}"), ("threshold", $"{th}"))
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


    // The other end of the wire: what has reached this deployment's own
    // backend, from every client of it. Reading needs the problems key (or a
    // caller on the backend's machine); a refusal is rendered verbatim.
    private async void OnProblemsFetch(object sender, RoutedEventArgs e)
    {
        try
        {
            var r = await ApiClient.Shared.ProblemRows(ProblemsKeyBox.Password);
            ProblemsServerRows.Text = r.Rows.Length == 0
                ? L10n.T("prob.none")
                : string.Join("\n", r.Rows.Select(row =>
                    $"{row.Op}  {row.StatusCode}  ×{row.Count}  " +
                    $"{row.Source} {row.AppVersion} · {row.Platform} · {row.Day}"));
            // The other aggregate the same key opens: not what broke, but
            // where this address has been seen going. Hosts and counts,
            // never a profile.
            var been = await ApiClient.Shared.VisitsAcross(ProblemsKeyBox.Password);
            VisitsAcrossRows.Text = been.Length == 0 ? "" :
                L10n.T("prob.been") + "\n" + L10n.T("prob.been.pitch") + "\n"
                + string.Join("\n", been.Select(v =>
                    $"{v.Host}  ×{v.Times}  " + string.Join(", ", v.Reasons)));
            VisitsAcrossRows.Visibility = been.Length == 0
                ? Visibility.Collapsed : Visibility.Visible;
        }
        catch (Exception ex) { ProblemsServerRows.Text = ex.Message; }
        ProblemsServerRows.Visibility = Visibility.Visible;
    }

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

    /// <summary>Store or clear the person's own model key. An empty box is
    /// the clear — no key means the deployment's, and there is no flag to
    /// leave switched on by mistake.</summary>
    private void OnSaveKey(object sender, RoutedEventArgs e)
    {
        AppState.Current.RememberLlmKey(KeyBox.Password);
        KeyBox.Password = AppState.Current.LlmKey;
    }

    /// <summary>The deployment invite key, same clearing rule: empty means
    /// none, and a deployment that never gated signup never needs one.</summary>
    private void OnSaveInvite(object sender, RoutedEventArgs e)
    {
        AppState.Current.RememberSignupKey(InviteBox.Password);
        InviteBox.Password = AppState.Current.SignupKey;
    }
}
