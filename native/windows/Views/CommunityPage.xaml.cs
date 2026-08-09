using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class CommunityPage : Page
{
    public sealed class MsgVm
    {
        public string From { get; init; } = "";
        public string Content { get; init; } = "";
        public bool Blocked { get; init; }
        // Carried on the row: the note sits inside a DataTemplate, where
        // x:Name buys a code-behind field on nobody's copy of it.
        public string BlockedLabel { get; init; } = "";
        public Visibility BlockedVisibility =>
            Blocked ? Visibility.Visible : Visibility.Collapsed;
    }

    public sealed class RoomMsgVm
    {
        public string From { get; init; } = "";
        public string Body { get; init; } = "";
        public bool FromProfile { get; init; }
        public Brush FromBrush => (Brush)Application.Current.Resources[
            FromProfile ? "QrmeBrandABrush" : "QrmeT2Brush"];
    }

    private string? _connectionId;
    private string? _roomId;

    public CommunityPage()
    {
        InitializeComponent();
        // `Tier` reads the selection by index, so the visible words are free
        // to be looked up rather than compared against.
        TierBox.ItemsSource = new[] { L10n.T("nc.tier.friendly"),
                                      L10n.T("nc.tier.rated") };
        TierBox.SelectedIndex = 0;
        Localize();
    }

    private void Localize()
    {
        var lang = AppState.Current.Language;
        StrangerPivot.Header = L10n.T("nc.stranger", lang);
        StrangerHead.Text = L10n.T("nc.stranger", lang);
        StrangerSub.Text = L10n.T("nc.stranger.sub", lang);
        TierBox.Header = L10n.T("nc.tier", lang);
        VerifyNote.Text = L10n.T("nc.rated.sub", lang);
        BirthdateBox.Header = L10n.T("nc.birthdate.ph", lang);
        AliasBox.Header = L10n.T("nc.alias.ph", lang);
        JoinButton.Content = L10n.T("nc.find", lang);
        EndButton.Content = L10n.T("nc.end", lang);
        StrangerDraft.PlaceholderText = L10n.T("nc.say.ph", lang);
        SendStrangerButton.Content = L10n.T("nc.send", lang);
        RefreshStrangerButton.Content = L10n.T("nc.refresh", lang);

        RoomsPivot.Header = L10n.T("nc.rooms", lang);
        OpenRoomHead.Text = L10n.T("nc.room.open", lang);
        TopicBox.Header = L10n.T("nc.topic.ph", lang);
        OpenRoomButton.Content = L10n.T("nc.room.here", lang);
        LeaveRoomButton.Content = L10n.T("nc.leave", lang);
        RoomDraft.PlaceholderText = L10n.T("nc.say.ph", lang);
        SendRoomButton.Content = L10n.T("nc.send", lang);
        AdvanceButton.Content = L10n.T("nc.lettalk", lang);
    }

    protected override void OnNavigatedTo(NavigationEventArgs e) =>
        RoomBlurb.Text = L10n.Fill("nc.room.sub", AppState.Current.Language,
                                   ("name", AppState.Current.DisplayName));

    private string Tier => TierBox.SelectedIndex == 1 ? "rated" : "friendly";

    private void OnTierChanged(object sender, SelectionChangedEventArgs e)
    {
        var needsVerify = Tier == "rated" && !AppState.Current.InteractorVerified;
        VerifyNote.Visibility = needsVerify ? Visibility.Visible : Visibility.Collapsed;
        BirthdateBox.Visibility = needsVerify ? Visibility.Visible : Visibility.Collapsed;
    }

    /// Mint (and remember) the device owner's interactor identity — the same
    /// one Chat uses.
    private static async System.Threading.Tasks.Task<string> EnsureInteractor()
    {
        var s = AppState.Current;
        if (!string.IsNullOrEmpty(s.InteractorId)) return s.InteractorId!;
        var created = await ApiClient.Shared.CreateInteractor("You");
        s.RememberInteractor(created.Id, token: created.Token);
        return created.Id;
    }

    // -- Stranger --

    private async void OnJoin(object sender, RoutedEventArgs e)
    {
        StrangerError.Visibility = Visibility.Collapsed;
        try
        {
            var s = AppState.Current;
            string me;
            var minted = false;
            if (Tier == "rated" && !s.InteractorVerified)
            {
                // Verify 18+: mint a fresh identity carrying the birthdate —
                // the age wall checks it server-side.
                var created = await ApiClient.Shared.CreateInteractor(
                    "You", BirthdateBox.Text.Trim());
                s.RememberInteractor(created.Id, token: created.Token);
                me = created.Id;
                minted = true;
            }
            else me = await EnsureInteractor();
            var r = await ApiClient.Shared.JoinQueue(me, AliasBox.Text.Trim(), Tier,
                AppState.Current.InteractorToken ?? "");
            // A rated admit proves the 18+ verification stands — remember it.
            if (minted) s.RememberInteractor(me, adult: true);
            if (r.Status == "matched" && r.ConnectionId is not null)
            {
                _connectionId = r.ConnectionId;
                MatchTitle.Text = L10n.Fill("nc.talking", AppState.Current.Language,
                                            ("who", r.MatchedWith
                                                 ?? L10n.T("nc.stranger")));
                JoinCard.Visibility = Visibility.Collapsed;
                TalkCard.Visibility = Visibility.Visible;
                await RefreshStranger();
            }
            else
            {
                JoinButton.Content = L10n.T("nc.match.waiting");
            }
        }
        catch (Exception ex) { ShowStrangerError(ex.Message); }
    }

    private async System.Threading.Tasks.Task RefreshStranger()
    {
        if (_connectionId is null) return;
        var s = AppState.Current;
        try
        {
            var msgs = await ApiClient.Shared.ConnectionMessages(_connectionId,
                s.InteractorId!, s.InteractorToken ?? "");
            StrangerList.ItemsSource = msgs.Select(m => new MsgVm
            {
                From = m.From,
                Content = m.Content,
                Blocked = m.Status == "blocked",
                BlockedLabel = L10n.T("nc.blocked", s.Language),
            }).ToList();
        }
        catch (Exception ex) { ShowStrangerError(ex.Message); }
    }

    private async void OnRefreshStranger(object sender, RoutedEventArgs e) =>
        await RefreshStranger();

    private async void OnSendStranger(object sender, RoutedEventArgs e)
    {
        var text = StrangerDraft.Text.Trim();
        if (_connectionId is null || text.Length == 0) return;
        StrangerDraft.Text = "";
        StrangerError.Visibility = Visibility.Collapsed;
        try
        {
            var me = await EnsureInteractor();
            await ApiClient.Shared.SendConnectionMessage(_connectionId, me, text,
                AppState.Current.InteractorToken ?? "");
            await RefreshStranger();
        }
        catch (Exception ex) { ShowStrangerError(ex.Message); }
    }

    private async void OnEnd(object sender, RoutedEventArgs e)
    {
        if (_connectionId is null) return;
        try
        {
            await ApiClient.Shared.EndConnection(_connectionId,
                AppState.Current.InteractorId!,
                AppState.Current.InteractorToken ?? "");
        }
        catch (Exception ex) { ShowStrangerError(ex.Message); }
        _connectionId = null;
        StrangerList.ItemsSource = null;
        TalkCard.Visibility = Visibility.Collapsed;
        JoinCard.Visibility = Visibility.Visible;
        JoinButton.Content = L10n.T("nc.match.find");
    }

    // -- Rooms --

    private async void OnOpenRoom(object sender, RoutedEventArgs e)
    {
        var topic = TopicBox.Text.Trim();
        if (topic.Length == 0) return;
        var s = AppState.Current;
        RoomError.Visibility = Visibility.Collapsed;
        try
        {
            var me = await EnsureInteractor();
            var room = await ApiClient.Shared.CreateRoom(topic, s.Pid!, me);
            _roomId = room.Id;
            RoomTitle.Text = room.Topic;
            TopicBox.Text = "";
            RoomList.ItemsSource = null;
            OpenCard.Visibility = Visibility.Collapsed;
            RoomCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowRoomError(ex.Message); }
    }

    private async System.Threading.Tasks.Task ReloadRoom()
    {
        if (_roomId is null) return;
        try
        {
            var msgs = await ApiClient.Shared.RoomTranscript(
                _roomId, AppState.Current.InteractorToken ?? "");
            RoomList.ItemsSource = msgs.Select(m => new RoomMsgVm
            {
                From = m.From,
                Body = m.Content ?? "· blocked by moderation ·",
                FromProfile = m.SenderKind == "profile",
            }).ToList();
        }
        catch (Exception ex) { ShowRoomError(ex.Message); }
    }

    private async void OnSendRoom(object sender, RoutedEventArgs e)
    {
        var text = RoomDraft.Text.Trim();
        if (_roomId is null || text.Length == 0) return;
        RoomDraft.Text = "";
        RoomError.Visibility = Visibility.Collapsed;
        try
        {
            var me = await EnsureInteractor();
            await ApiClient.Shared.RoomMessage(
                _roomId, me, text, AppState.Current.InteractorToken ?? "");
            await ReloadRoom();
        }
        catch (Exception ex) { ShowRoomError(ex.Message); }
    }

    private async void OnAdvance(object sender, RoutedEventArgs e)
    {
        if (_roomId is null) return;
        RoomError.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.RoomAdvance(
                _roomId, AppState.Current.InteractorToken ?? "");
            await ReloadRoom();
        }
        catch (Exception ex) { ShowRoomError(ex.Message); }
    }

    private void OnLeaveRoom(object sender, RoutedEventArgs e)
    {
        _roomId = null;
        RoomList.ItemsSource = null;
        RoomCard.Visibility = Visibility.Collapsed;
        OpenCard.Visibility = Visibility.Visible;
    }

    // -- helpers --

    private void ShowStrangerError(string message)
    {
        StrangerError.Text = message;
        StrangerError.Visibility = Visibility.Visible;
    }

    private void ShowRoomError(string message)
    {
        RoomError.Text = message;
        RoomError.Visibility = Visibility.Visible;
    }
}
