using System;
using System.Linq;
using System.Threading.Tasks;
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
        CrowdTitle.Text = L10n.T("crowd.title");
        CrowdKindBox.Header = "kind";
        CrowdKindBox.Text = "profiles";
        CrowdTargetBox.Header = L10n.T("crowd.target");
        LikeButton.Content = L10n.T("crowd.like");
        UnlikeButton.Content = L10n.T("crowd.unlike");
        ShareButton.Content = L10n.T("crowd.share");
        CountsButton.Content = L10n.T("crowd.counts");
        FollowButton.Content = L10n.T("crowd.follow");
        UnfollowButton.Content = L10n.T("crowd.unfollow");
        SubscribersButton.Content = L10n.T("crowd.subscribers");
        GiftNoteText.Text = L10n.T("crowd.gift.note");
        GiftAmountBox.Header = L10n.T("crowd.gift.amount");
        GiftWordsBox.Header = L10n.T("crowd.gift.words");
        GiftButton.Content = L10n.T("crowd.gift");
        GiftsButton.Content = L10n.T("crowd.gifts");
        PartyTitle.Text = L10n.T("party.title");
        PartyPostBox.Header = L10n.T("party.post");
        PartyNameBox.Header = L10n.T("party.name");
        PartyStartButton.Content = L10n.T("party.start");
        PartyIdBox.Header = L10n.T("party.id");
        PartyJoinButton.Content = L10n.T("party.join");
        PartyShowButton.Content = L10n.T("party.show");
        PartyLeaveButton.Content = L10n.T("party.leave");
        PartyEndButton.Content = L10n.T("party.end");
        PartySeekBox.Header = L10n.T("party.seek");
        PartySeekButton.Content = L10n.T("party.seek.go");
        PartySayBox.Header = L10n.T("party.say");
        PartySayButton.Content = L10n.T("people.send");
        PartyContextButton.Content = L10n.T("party.context");
        LendTitle.Text = L10n.T("lend.title");
        LendRulesButton.Content = L10n.T("lend.rules");
        LendBorrowerBox.Header = L10n.T("lend.borrower");
        LendSurfaceBox.Header = L10n.T("lend.surface");
        LendSurfaceBox.Text = "room";
        LendSurfaceIdBox.Header = L10n.T("lend.surface.id");
        LendKindBox.Header = L10n.T("lend.kind");
        LendRefBox.Header = L10n.T("lend.ref");
        LendNameBox.Header = L10n.T("lend.name");
        LendOfferButton.Content = L10n.T("lend.offer");
        LendMineButton.Content = L10n.T("lend.mine");
        LendIdBox.Header = L10n.T("lend.id");
        LendAcceptButton.Content = L10n.T("lend.accept");
        LendDeclineButton.Content = L10n.T("lend.decline");
        LendCloseButton.Content = L10n.T("lend.close");
        LendShowButton.Content = L10n.T("lend.show");
        LendWhatBox.Header = L10n.T("lend.what");
        LendUseButton.Content = L10n.T("lend.use");
        LendUsesButton.Content = L10n.T("lend.uses");
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

    // -- the crowd, the couch and the loan --------------------------------

    private async Task Try(Func<Task> op)
    {
        try { StatusText.Text = ""; await op(); }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnLike(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.Like(
            CrowdKindBox.Text.Trim(), CrowdTargetBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnUnlike(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.Unlike(
            CrowdKindBox.Text.Trim(), CrowdTargetBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnShare(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Share(CrowdKindBox.Text.Trim(),
                CrowdTargetBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = outp.Url ?? "";
        });

    private async void OnCounts(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.AudienceOf(CrowdKindBox.Text.Trim(),
                CrowdTargetBox.Text.Trim(), AppState.Current.Token!);
            CountsText.Text =
                $"♥ {c.Likes} · 💬 {c.Comments} · ↗ {c.Shares} · ⊕ {c.Subscribers}";
        });

    private async void OnFollow(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.Subscribe(
            CrowdKindBox.Text.Trim(), CrowdTargetBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnUnfollow(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.Unsubscribe(
            CrowdKindBox.Text.Trim(), CrowdTargetBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnSubscribers(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var box = await ApiClient.Shared.Subscribers(
                CrowdKindBox.Text.Trim(), CrowdTargetBox.Text.Trim(),
                AppState.Current.Token!);
            CountsText.Text = box.Subscribers.Length.ToString();
        });

    private async void OnGift(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.Gift(
            CrowdKindBox.Text.Trim(), CrowdTargetBox.Text.Trim(),
            double.TryParse(GiftAmountBox.Text, out var a) ? a : 0,
            GiftWordsBox.Text.Trim(), AppState.Current.Token!));

    private async void OnGifts(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var box = await ApiClient.Shared.Gifts(CrowdKindBox.Text.Trim(),
                CrowdTargetBox.Text.Trim(), AppState.Current.Token!);
            GiftList.ItemsSource = box.Gifts.Select(g => new Row(
                $"{g.GiverId} · {g.Amount} · {g.Note}")).ToList();
        });

    private void ShowParty(PartyCard c) =>
        PartyStateText.Text =
            $"{c.Title} · {c.State} · {c.PositionS}s · {c.Members?.Length ?? 0}";

    private async void OnPartyStart(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.StartParty(
                PartyPostBox.Text.Trim(), AppState.Current.Pid!,
                PartyNameBox.Text.Trim(), AppState.Current.Token!);
            PartyIdBox.Text = c.Id ?? "";
            ShowParty(c);
        });

    private async void OnPartyJoin(object sender, RoutedEventArgs e) =>
        await Try(async () => ShowParty(await ApiClient.Shared.JoinParty(
            PartyIdBox.Text.Trim(), AppState.Current.Pid!,
            AppState.Current.Token!)));

    private async void OnPartyShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            ShowParty(await ApiClient.Shared.Party(PartyIdBox.Text.Trim(),
                AppState.Current.Token!));
            var chat = await ApiClient.Shared.PartyChat(
                PartyIdBox.Text.Trim(), AppState.Current.Token!);
            PartyChatList.ItemsSource = chat.Lines.Select(l => new Row(
                $"{l.MemberId}: {l.Body}")).ToList();
        });

    private async void OnPartyLeave(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.LeaveParty(
            PartyIdBox.Text.Trim(), AppState.Current.Pid!,
            AppState.Current.Token!));

    private async void OnPartyEnd(object sender, RoutedEventArgs e) =>
        await Try(async () => ShowParty(await ApiClient.Shared.EndParty(
            PartyIdBox.Text.Trim(), AppState.Current.Token!)));

    private async void OnPartySeek(object sender, RoutedEventArgs e) =>
        await Try(async () => ShowParty(await ApiClient.Shared.SeekParty(
            PartyIdBox.Text.Trim(), AppState.Current.Pid!,
            int.TryParse(PartySeekBox.Text, out var pos) ? pos : 0,
            AppState.Current.Token!)));

    private async void OnPartySay(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.SayInParty(PartyIdBox.Text.Trim(),
                AppState.Current.Pid!, PartySayBox.Text.Trim(),
                AppState.Current.Token!);
            PartySayBox.Text = "";
        });

    private async void OnPartyContext(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var ctx = await ApiClient.Shared.PartyContextOf(
                PartyIdBox.Text.Trim(), AppState.Current.Token!);
            PartyContextText.Text = ctx.YouHaveNotSeenIt ?? "";
        });

    private async void OnLendRules(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.GrantVocabulary();
            LendTermsList.ItemsSource =
                v.Terms.Select(t => new Row($"· {t}")).ToList();
        });

    private async void OnLendOffer(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var g = await ApiClient.Shared.OfferGrant(AppState.Current.Pid!,
                LendBorrowerBox.Text.Trim(), LendSurfaceBox.Text.Trim(),
                LendSurfaceIdBox.Text.Trim(), LendKindBox.Text.Trim(),
                LendRefBox.Text.Trim(), LendNameBox.Text.Trim(),
                AppState.Current.Token!);
            LendIdBox.Text = g.Id ?? "";
        });

    private async void OnLendMine(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var mine = await ApiClient.Shared.MyGrants(AppState.Current.Pid!,
                AppState.Current.Token!);
            var rows = (mine.Lending ?? Array.Empty<GrantCard>())
                .Concat(mine.Borrowing ?? Array.Empty<GrantCard>())
                .Select(g => new Row($"{g.Id} · {g.Title} · {g.State}"))
                .ToList();
            LendMineList.ItemsSource = rows;
            var sid = LendSurfaceIdBox.Text.Trim();
            await ApiClient.Shared.GrantsInSurface(LendSurfaceBox.Text.Trim(),
                sid.Length == 0 ? "x" : sid, AppState.Current.Token!);
        });

    private async void OnLendAccept(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.AcceptGrant(
            LendIdBox.Text.Trim(), AppState.Current.Pid!,
            AppState.Current.Token!));

    private async void OnLendDecline(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.DeclineGrant(
            LendIdBox.Text.Trim(), AppState.Current.Pid!,
            AppState.Current.Token!));

    private async void OnLendClose(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.CloseGrant(
            LendIdBox.Text.Trim(), AppState.Current.Pid!,
            AppState.Current.Token!));

    private async void OnLendShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var g = await ApiClient.Shared.Grant(LendIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = $"{g.Title} · {g.State}";
        });

    private async void OnLendUse(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.UseGrant(
            LendIdBox.Text.Trim(), AppState.Current.Pid!,
            LendWhatBox.Text.Trim(), AppState.Current.Token!));

    private async void OnLendUses(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var box = await ApiClient.Shared.GrantUses(LendIdBox.Text.Trim(),
                AppState.Current.Token!);
            LendUsesList.ItemsSource = box.Uses.Select(u => new Row(
                $"{u.UsedAt} · {u.What}")).ToList();
        });
}
