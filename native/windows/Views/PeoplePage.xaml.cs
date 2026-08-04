using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

/// <summary>
/// The people around a profile: friends, who the platform suggests and
/// why, the wall, and the comments under a post. Nine routes the backend
/// has carried since the community round, with a door on every client but
/// this one.
///
/// Three rules kept rather than invented: a pinned row carries the word
/// rather than a control (deletion refuses with 409 and the list says
/// `pinned` so a client can leave the button off); a blocked post or
/// comment comes back to its author with its status, because the words
/// *were* recorded; and a suggestion is shown with the reason the route
/// returned for it. Every visible string comes from L10n.
/// </summary>
public sealed partial class PeoplePage : Page
{
    public record Row(string Line);

    public PeoplePage()
    {
        InitializeComponent();
        TitleText.Text = L10n.T("people.friends");
        InboxTitle.Text = L10n.T("inbox.title");
        InboxSeenButton.Content = L10n.T("inbox.seen");
        FriendIdBox.Header = L10n.T("people.add");
        AddFriendButton.Content = L10n.T("people.add.go");
        RemoveFriendButton.Content = L10n.T("people.remove");
        PinnedNote.Text = L10n.T("people.pinned");
        SuggestedTitle.Text = L10n.T("people.suggested");
        RankedText.Text = L10n.T("people.ranked");
        WallTitle.Text = L10n.T("people.wall");
        PostBox.Header = L10n.T("people.say");
        PostButton.Content = L10n.T("people.post");
        CommentsTitle.Text = L10n.T("people.comments");
        PostIdBox.Header = L10n.T("people.comments");
        OpenCommentsButton.Content = L10n.T("people.comments");
        CommentBox.Header = L10n.T("people.reply");
        CommentButton.Content = L10n.T("people.send");
        CommentIdBox.Header = L10n.T("people.withdraw");
        WithdrawButton.Content = L10n.T("people.withdraw");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) =>
        await Load();

    private async System.Threading.Tasks.Task Load()
    {
        var s = AppState.Current;
        if (s.Pid is null) return;
        try
        {
            // The deed, never the words: each row names the kind and the
            // actor; the sentence per kind is this shell's, from L10n.
            if (s.Token is not null)
            {
                var page = await ApiClient.Shared.Inbox(s.Pid, s.Token);
                InboxCard.Visibility = page.Events.Length > 0
                    ? Visibility.Visible : Visibility.Collapsed;
                InboxTitle.Text = L10n.T("inbox.title")
                    + (page.Unseen > 0
                       ? $" · {page.Unseen} {L10n.T("inbox.new")}" : "");
                InboxSeenButton.Visibility = page.Unseen > 0
                    ? Visibility.Visible : Visibility.Collapsed;
                InboxList.ItemsSource = page.Events.Select(ev => new Row(
                    $"{ev.ActorName ?? ev.ActorId} "
                    + L10n.T($"inbox.kind.{ev.Kind}"))).ToList();
            }
            var friends = await ApiClient.Shared.Friends(s.Pid);
            FriendList.ItemsSource = friends.Select(f => new Row(
                $"{f.ProfileId} · {f.DisplayName ?? ""}"
                + (f.Founder ? " ★" : "")
                + (f.Pinned ? $" · {L10n.T("people.pinned")}" : ""))).ToList();
            var suggested = await ApiClient.Shared.SuggestedFriends(s.Pid);
            SuggestedList.ItemsSource = suggested.Select(x => new Row(
                $"{x.ProfileId} · {x.DisplayName ?? ""}"
                + (string.IsNullOrWhiteSpace(x.Because) ? "" : $" · {x.Because}")))
                .ToList();
            var posts = await ApiClient.Shared.Wall(s.Pid);
            PostList.ItemsSource = posts.Select(p => new Row(
                $"{p.Id} · {p.Body}"
                + (p.Status == "blocked" ? $" · {L10n.T("people.blocked")}" : "")))
                .ToList();
        }
        catch { /* leave as-is */ }
    }

    private async void OnInboxSeen(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.MarkInboxSeen(s.Pid!, s.Token!);
            await Load();
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnAddFriend(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var who = FriendIdBox.Text.Trim();
        if (who.Length == 0) return;
        try
        {
            await ApiClient.Shared.AddFriend(s.Pid!, who, s.Token!);
            FriendIdBox.Text = "";
            StatusText.Text = "";
            await Load();
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnRemoveFriend(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var who = FriendIdBox.Text.Trim();
        if (who.Length == 0) return;
        try
        {
            await ApiClient.Shared.RemoveFriend(s.Pid!, who, s.Token!);
            FriendIdBox.Text = "";
            StatusText.Text = "";
            await Load();
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnPost(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var words = PostBox.Text.Trim();
        if (words.Length == 0) return;
        try
        {
            var made = await ApiClient.Shared.PostToWall(s.Pid!, words, s.Token!);
            PostBox.Text = "";
            // 201 with `blocked` is not an error: the words were recorded,
            // and their status is what happened to them.
            StatusText.Text = made.Status == "blocked"
                ? L10n.T("people.blocked") : "";
            await Load();
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnOpenComments(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var postId = PostIdBox.Text.Trim();
        if (postId.Length == 0) return;
        try
        {
            var comments = await ApiClient.Shared.Comments("posts", postId,
                                                           s.Token!);
            CommentList.ItemsSource = comments.Select(c => new Row(
                $"{c.Id} · {c.Body}")).ToList();
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnComment(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var postId = PostIdBox.Text.Trim();
        var words = CommentBox.Text.Trim();
        if (postId.Length == 0 || words.Length == 0) return;
        try
        {
            var made = await ApiClient.Shared.AddComment("posts", postId,
                                                         words, s.Token!);
            CommentBox.Text = "";
            StatusText.Text = made.Status == "blocked"
                ? L10n.T("people.blocked") : "";
            OnOpenComments(sender, e);
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnWithdraw(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var commentId = CommentIdBox.Text.Trim();
        if (commentId.Length == 0) return;
        try
        {
            await ApiClient.Shared.DeleteComment(commentId, s.Token!);
            CommentIdBox.Text = "";
            StatusText.Text = "";
            OnOpenComments(sender, e);
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }
}
