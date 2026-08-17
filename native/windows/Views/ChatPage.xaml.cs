using System;
using System.Collections.ObjectModel;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class ChatPage : Page
{
    public record BubbleRow(string Text, HorizontalAlignment Align);

    private readonly ObservableCollection<BubbleRow> _messages = new();

    // Index 0 is the empty default: "let it read my prompt". The label is a
    // key now — this shell and the console said what each role does while the
    // phones said only "Advisor" and "Operator", on the control that decides
    // whether a synthetic profile recommends something or goes and does it.
    private static readonly (string Value, string Key)[] Roles =
    {
        ("", "nchat.role.read"),
        ("advisor", "nchat.role.advisor"),
        ("collaborator", "nchat.role.collaborator"),
        ("operator", "nchat.role.operator"),
    };

    private string _escalationId = "";

    private async void OnEscShow(object sender, RoutedEventArgs e)
    {
        EscPanel.Visibility = Visibility.Visible;
        await LoadDialer();
    }

    private async System.Threading.Tasks.Task LoadDialer()
    {
        var s = AppState.Current;
        try
        {
            var d = await ApiClient.Shared.DialerPosture_(
                s.InteractorId!, s.InteractorToken!);
            EscWaiver.Text = d.Waiver;
            EscArmedLine.Text = d.Armed ? L10n.T("esc.armed") : L10n.T("esc.notarmed");
            // The deployment's posture, said now rather than at the press.
            EscSealedLine.Text = d.Sealed
                ? L10n.Fill("esc.sealed", AppState.Current.Language,
                            ("number", d.CallYourself))
                : "";
            EscArmButton.Visibility = d.Armed ? Visibility.Collapsed : Visibility.Visible;
            EscSigBox.Visibility = EscArmButton.Visibility;
        }
        catch (Exception ex) { EscSaid.Text = ex.Message; }
    }

    private async void OnEscArm(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.ArmDialer(s.InteractorId!,
                                             EscSigBox.Text.Trim(),
                                             s.InteractorToken!);
            await LoadDialer();
        }
        catch (Exception ex) { EscSaid.Text = ex.Message; }
    }

    private async void OnEscRaise(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var row = await ApiClient.Shared.CannotResolve(
                s.Pid!, s.InteractorId!, RealMatterBox.Text.Trim(),
                s.InteractorToken!);
            _escalationId = row.Id;
            EscPressButton.Visibility = Visibility.Visible;
            await ApiClient.Shared.MyEscalations(s.InteractorId!, s.InteractorToken!);
        }
        catch (Exception ex) { EscSaid.Text = ex.Message; }
    }

    /// <summary>The explicit press. While the deployment is sealed this
    /// throws, and what the person reads is the refusal itself — which says
    /// no call was placed and gives them the number.</summary>
    private async void OnEscPress(object sender, RoutedEventArgs e)
    {
        if (_escalationId.Length == 0) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.DialEmergency(_escalationId, s.InteractorId!,
                                                 s.InteractorToken!);
            EscSaid.Text = L10n.T("esc.placed");
        }
        catch (Exception ex) { EscSaid.Text = ex.Message; }
    }

    /// <summary>Somebody a person keeps, or somebody the search found. The
    /// two are different claims and the row says which.</summary>
    public sealed class RealRow
    {
        public string ProviderId { get; init; } = "";
        public string Name { get; init; } = "";
        public bool Yours { get; init; }
        public bool Preferred { get; init; }
        public string Whose => (Yours ? L10n.T("real.yours") : L10n.T("real.found"))
            + (Preferred ? " · " + L10n.T("real.first") : "");
        public string KeepLabel => L10n.T("real.keep");
        public string PreferLabel => L10n.T("real.prefer");
        public string DropLabel => L10n.T("real.drop");
        public string PreviewLabel =>
            L10n.Fill("real.preview", AppState.Current.Language, ("name", Name));
        public Visibility KeepVisibility =>
            Yours ? Visibility.Collapsed : Visibility.Visible;
        public Visibility MineVisibility =>
            Yours ? Visibility.Visible : Visibility.Collapsed;
        public Visibility PreferVisibility =>
            Yours && !Preferred ? Visibility.Visible : Visibility.Collapsed;
    }

    private void ShowPeople(MyPerson[] people) =>
        RealPeopleList.ItemsSource = people.Select(p => new RealRow
        {
            ProviderId = p.ProviderId, Name = p.Name, Yours = p.Yours,
            Preferred = p.Preferred ?? false,
        }).ToList();

    private async void OnRealOpen(object sender, RoutedEventArgs e)
    {
        RealPanel.Visibility = Visibility.Visible;
        var s = AppState.Current;
        // Yours first, before any area is typed: that is what keeping them
        // was for.
        try { ShowPeople(await ApiClient.Shared.MyPeople(
            s.InteractorId!, s.InteractorToken!)); }
        catch (Exception ex) { RealBriefText.Text = ex.Message; }
    }

    private async void OnRealFind(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try { ShowPeople(await ApiClient.Shared.PeopleForArea(
            s.InteractorId!, RealAreaBox.Text.Trim(), s.InteractorToken!)); }
        catch (Exception ex) { RealBriefText.Text = ex.Message; }
    }

    private async void OnRealKeep(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string pid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.KeepPerson(s.InteractorId!, pid, s.InteractorToken!);
            OnRealFind(sender, e);
        }
        catch (Exception ex) { RealBriefText.Text = ex.Message; }
    }

    private async void OnRealPrefer(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string pid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.PreferPerson(s.InteractorId!, pid, s.InteractorToken!);
            OnRealOpen(sender, e);
        }
        catch (Exception ex) { RealBriefText.Text = ex.Message; }
    }

    private async void OnRealDrop(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string pid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.DropPerson(s.InteractorId!, pid, s.InteractorToken!);
            OnRealOpen(sender, e);
        }
        catch (Exception ex) { RealBriefText.Text = ex.Message; }
    }

    /// <summary>Nothing is sent by this — the whole file is read first, so
    /// declining is still free.</summary>
    private async void OnRealPreview(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string pid) return;
        var s = AppState.Current;
        try
        {
            var b = await ApiClient.Shared.PreviewBriefing(
                s.InteractorId!, s.Pid!, pid, RealMatterBox.Text.Trim(),
                RealGrantBox.Password, s.InteractorToken!);
            RealBriefText.Text = b.Reads + "\n" + string.Join("\n",
                b.Package.Attachments.Select(a => $"{a.Kind} · {a.Title}"
                    + (a.Sealed ? " · " + L10n.T("real.sealed") : "")));
        }
        catch (Exception ex) { RealBriefText.Text = ex.Message; }
    }

    public ChatPage()
    {
        InitializeComponent();
        EscTitle.Text = L10n.T("esc.hdr");
        EscSub.Text = L10n.T("esc.pitch");
        EscShowButton.Content = L10n.T("esc.show");
        EscSigBox.PlaceholderText = L10n.T("esc.sig.ph");
        EscArmButton.Content = L10n.T("esc.arm");
        EscRaiseButton.Content = L10n.T("esc.raise");
        EscPressButton.Content = L10n.T("esc.press");
        RealTitle.Text = L10n.T("real.hdr");
        RealSub.Text = L10n.T("real.pitch");
        RealOpenButton.Content = L10n.T("real.open");
        RealAreaBox.PlaceholderText = L10n.T("real.area.ph");
        RealFindButton.Content = L10n.T("real.find");
        RealMatterBox.PlaceholderText = L10n.T("real.matter.ph");
        RealGrantBox.PlaceholderText = L10n.T("real.grant.ph");
        var lang = AppState.Current.Language;
        Title.Text = L10n.T("tab.chat", lang);
        RoleBox.Header = L10n.T("nchat.rolepick", lang);
        RoleBox.ItemsSource = Roles.Select(r => L10n.T(r.Key, lang)).ToList();
        RoleBox.SelectedIndex = 0;
        DraftBox.PlaceholderText = L10n.T("nchat.type.ph", lang);
        SendButton.Content = L10n.T("nchat.send", lang);
    }

    private string? SelectedRole()
    {
        var i = RoleBox.SelectedIndex;
        return i > 0 && i < Roles.Length ? Roles[i].Value : null;
    }

    protected override void OnNavigatedTo(NavigationEventArgs e)
    {
        Subtitle.Text = L10n.Fill("nchat.sub", AppState.Current.Language,
                                  ("name", AppState.Current.DisplayName));
        RehearsalBox.PlaceholderText = L10n.T("cht.rh.scenario.ph");
        RehearsalButton.Content = L10n.T("cht.rh.open");
        MessagesList.ItemsSource = _messages;
    }

    private string? _rehearsalId;
    private string _rehearsalScenario = "";

    // Rehearsal: open a room whose transcript lives only until it closes;
    // while it stands, sends go there and nothing is remembered.
    private async void OnRehearsal(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            if (_rehearsalId is { } roomId)
            {
                await ApiClient.Shared.CloseRehearsal(s.Pid!, roomId);
                _rehearsalId = null;
                RehearsalButton.Content = L10n.T("cht.rh.open");
                RehearsalLine.Visibility = Visibility.Collapsed;
                RehearsalBox.Visibility = Visibility.Visible;
                return;
            }
            var scenario = RehearsalBox.Text.Trim();
            if (scenario.Length == 0) return;
            if (string.IsNullOrEmpty(s.InteractorId))
            {
                var created = await ApiClient.Shared.CreateInteractor("You");
                s.RememberInteractor(created.Id, token: created.Token);
            }
            var room = await ApiClient.Shared.OpenRehearsal(
                s.Pid!, s.InteractorId!, scenario);
            _rehearsalId = room.Id;
            _rehearsalScenario = room.Scenario;
            RehearsalBox.Text = ""; RehearsalBox.Visibility = Visibility.Collapsed;
            RehearsalButton.Content = L10n.T("cht.rh.close");
            RehearsalLine.Text = "🎭 " + room.Scenario;
            RehearsalLine.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
    }

    private async void OnSend(object sender, RoutedEventArgs e)
    {
        var text = DraftBox.Text.Trim();
        if (text.Length == 0) return;
        DraftBox.Text = "";
        _messages.Add(new BubbleRow(text, HorizontalAlignment.Right));

        var s = AppState.Current;
        SendButton.IsEnabled = false;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            // An open rehearsal room takes the turn: nothing lands in the
            // remembered conversation, and the bubble says so.
            if (_rehearsalId is { } openRoom)
            {
                var turn = await ApiClient.Shared.Rehearse(
                    s.Pid!, openRoom, text);
                _messages.Add(new BubbleRow(turn.Reply, HorizontalAlignment.Left));
                _messages.Add(new BubbleRow("🎭 " + _rehearsalScenario,
                                            HorizontalAlignment.Left));
                return;
            }
            // Lazily mint the device owner's interactor identity once.
            if (string.IsNullOrEmpty(s.InteractorId))
            {
                var created = await ApiClient.Shared.CreateInteractor("You");
                s.RememberInteractor(created.Id, token: created.Token);
            }
            var reply = await ApiClient.Shared.Chat(s.Pid!, s.Token!,
                                                    s.InteractorId!, text,
                                                    SelectedRole());
            var p = reply.ProfileMessage;
            _messages.Add(new BubbleRow(
                p.Content is { } c && p.Status == "approved"
                    ? c
                    : "⏳ Held for review"
                      + (p.FlagReason is { } fr ? $" — {fr}" : ""),
                HorizontalAlignment.Left));
            if (p.Status == "approved")
                // The watermark rides on every AI render, always visible.
                _messages.Add(new BubbleRow(
                    p.Watermark?.Display?.Line ?? "✦ AI",
                    HorizontalAlignment.Left));
            if (p.Status == "approved" && reply.RoleContext is { } rc)
                _messages.Add(new BubbleRow(
                    $"◈ worked as {rc.Role} ({rc.How})",
                    HorizontalAlignment.Left));
            if (p.Status == "approved" && reply.Provenance is { } prov)
            {
                var lang = AppState.Current.Language;
                var trail = "ⓘ " + L10n.Fill(
                    "nprv.generated", lang,
                    ("model", prov.GeneratedBy),
                    ("n", $"{prov.GroundedInInfo.SourceItems}"),
                    ("status", prov.Moderation.Status));
                if (prov.LicensedFrom is { } lf)
                    trail += " · " + L10n.Fill("nprv.licensed", lang, ("source", lf));
                _messages.Add(new BubbleRow(trail, HorizontalAlignment.Left));
            }
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
        finally { SendButton.IsEnabled = true; }
    }
}
