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

    public CommunityPage() => InitializeComponent();

    protected override void OnNavigatedTo(NavigationEventArgs e) =>
        RoomBlurb.Text = $"A group chat with you and {AppState.Current.DisplayName}. " +
                         "Every profile turn is moderated; a room with a minor always runs strict.";

    /// Mint (and remember) the device owner's interactor identity — the same
    /// one Chat uses.
    private static async System.Threading.Tasks.Task<string> EnsureInteractor()
    {
        var s = AppState.Current;
        if (!string.IsNullOrEmpty(s.InteractorId)) return s.InteractorId!;
        var created = await ApiClient.Shared.CreateInteractor("You");
        s.RememberInteractor(created.Id);
        return created.Id;
    }

    // -- Stranger --

    private async void OnJoin(object sender, RoutedEventArgs e)
    {
        StrangerError.Visibility = Visibility.Collapsed;
        try
        {
            var me = await EnsureInteractor();
            var r = await ApiClient.Shared.JoinQueue(me, AliasBox.Text.Trim());
            if (r.Status == "matched" && r.ConnectionId is not null)
            {
                _connectionId = r.ConnectionId;
                MatchTitle.Text = $"Talking with {r.MatchedWith ?? "a stranger"}";
                JoinCard.Visibility = Visibility.Collapsed;
                TalkCard.Visibility = Visibility.Visible;
                await RefreshStranger();
            }
            else
            {
                JoinButton.Content = "Waiting for a match — check again";
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
            var msgs = await ApiClient.Shared.ConnectionMessages(_connectionId, s.InteractorId!);
            StrangerList.ItemsSource = msgs.Select(m => new MsgVm
            {
                From = m.From,
                Content = m.Content,
                Blocked = m.Status == "blocked",
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
            await ApiClient.Shared.SendConnectionMessage(_connectionId, me, text);
            await RefreshStranger();
        }
        catch (Exception ex) { ShowStrangerError(ex.Message); }
    }

    private async void OnEnd(object sender, RoutedEventArgs e)
    {
        if (_connectionId is null) return;
        try
        {
            await ApiClient.Shared.EndConnection(_connectionId, AppState.Current.InteractorId!);
        }
        catch (Exception ex) { ShowStrangerError(ex.Message); }
        _connectionId = null;
        StrangerList.ItemsSource = null;
        TalkCard.Visibility = Visibility.Collapsed;
        JoinCard.Visibility = Visibility.Visible;
        JoinButton.Content = "Find a match";
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
            var msgs = await ApiClient.Shared.RoomTranscript(_roomId);
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
            await ApiClient.Shared.RoomMessage(_roomId, me, text);
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
            await ApiClient.Shared.RoomAdvance(_roomId);
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
