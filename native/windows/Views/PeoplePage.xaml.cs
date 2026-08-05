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
        PlaceTitle.Text = L10n.T("place.title");
        PlaceSurfaceBox.Header = L10n.T("place.surface");
        PlaceSurfaceBox.Text = "room";
        PlaceSurfaceIdBox.Header = L10n.T("place.surface.id");
        WhoseButton.Content = L10n.T("place.whose");
        MicLendButton.Content = L10n.T("place.mic.lend");
        MicBackButton.Content = L10n.T("place.mic.back");
        MicWhoButton.Content = L10n.T("place.mic.who");
        MaskKindBox.Header = L10n.T("place.mask.kind");
        MaskKindBox.Text = "avatar";
        MaskNameBox.Header = L10n.T("place.mask.name");
        MaskWearButton.Content = L10n.T("place.mask.wear");
        MaskOffButton.Content = L10n.T("place.mask.off");
        MaskWhoButton.Content = L10n.T("place.mask.who");
        CamTitle.Text = L10n.T("cam.title");
        CamRulesButton.Content = L10n.T("cam.rules");
        CamSubjectBox.Header = L10n.T("cam.subject");
        CamSubjectBox.Text = "object";
        CamViewerBox.Header = L10n.T("cam.viewer");
        CamMinutesBox.Header = L10n.T("cam.minutes");
        CamMinutesBox.Text = "10";
        CamOpenButton.Content = L10n.T("cam.open");
        CamMineButton.Content = L10n.T("cam.mine");
        CamDisclosureButton.Content = L10n.T("cam.disclosure");
        CamSessionBox.Header = L10n.T("cam.session");
        CamShowButton.Content = L10n.T("cam.show");
        CamCloseButton.Content = L10n.T("cam.close");
        OrgTitle.Text = L10n.T("org.title");
        OrgNameBox.Header = L10n.T("org.name");
        OrgCreateButton.Content = L10n.T("org.create");
        OrgListButton.Content = L10n.T("org.list");
        OrgDemoButton.Content = L10n.T("org.demo");
        OrgIdBox.Header = L10n.T("org.id");
        OrgShowButton.Content = L10n.T("org.show");
        DeptNameBox.Header = L10n.T("org.dept.name");
        DeptRoleBox.Header = L10n.T("org.dept.role");
        DeptProfileBox.Header = L10n.T("org.dept.profile");
        DeptAddButton.Content = L10n.T("org.dept.add");
        GoalBox.Header = L10n.T("org.goal");
        CoordinateButton.Content = L10n.T("org.go");
        CoordLogButton.Content = L10n.T("org.log");
        TourTitle.Text = L10n.T("tut.title");
        TourOutlineButton.Content = L10n.T("tut.outline");
        TourStartButton.Content = L10n.T("tut.start");
        TourProgressButton.Content = L10n.T("tut.progress");
        TourStepBox.Header = L10n.T("tut.step");
        TourStepButton.Content = L10n.T("cam.show");
        TourDoneButton.Content = L10n.T("tut.done");
        TourScreenBox.Header = L10n.T("tut.screen");
        TourScreenButton.Content = L10n.T("tut.screen");
        BotTitle.Text = L10n.T("bot.title");
        BotIdBox.Header = L10n.T("bot.id");
        BotLogButton.Content = L10n.T("bot.log");
        BotSkillsButton.Content = L10n.T("bot.skills");
        BotDialsButton.Content = L10n.T("bot.dials");
        BotUnbindButton.Content = L10n.T("bot.unbind");
        BotPaceBox.Header = L10n.T("bot.pace");
        BotSteerButton.Content = L10n.T("bot.dials.set");
        ReferTitle.Text = L10n.T("refer.title");
        ReferAreaBox.Header = L10n.T("refer.area");
        ReferMatchButton.Content = L10n.T("refer.match");
        ReferProviderBox.Header = L10n.T("refer.provider");
        ReferPrepareButton.Content = L10n.T("refer.prepare");
        ReferIdBox.Header = L10n.T("refer.id");
        ReferSignatureBox.Header = L10n.T("refer.signature");
        ReferReleaseButton.Content = L10n.T("refer.release");
        ReferTokenBox.Header = L10n.T("refer.token");
        ReferOpenButton.Content = L10n.T("refer.open");
        ReferWordsBox.Header = L10n.T("refer.words");
        ReferReplyButton.Content = L10n.T("refer.reply");
        ObjectTitle.Text = L10n.T("object.title");
        ObjectIdBox.Header = L10n.T("object.id");
        ObjectShowButton.Content = L10n.T("object.show");
        ObjectAuditButton.Content = L10n.T("object.audit");
        ObjectWithdrawButton.Content = L10n.T("object.withdraw");
        ObjectRevokeButton.Content = L10n.T("object.revoke");
        ObjectResolveButton.Content =
            $"{L10n.T("object.resolve")} — {L10n.T("object.outcome")}";
        LobbyTitle.Text = L10n.T("lobby.title");
        LobbyRulesButton.Content = L10n.T("lobby.rules");
        LobbySessionBox.Header = L10n.T("lobby.session");
        LobbyKindBox.Header = L10n.T("lobby.kind");
        LobbyKindBox.Text = "profile";
        LobbyMemberBox.Header = L10n.T("lobby.member");
        LobbyRoleBox.Header = L10n.T("lobby.role");
        LobbyRoleBox.Text = "teammate";
        LobbySeatButton.Content = L10n.T("lobby.seat");
        LobbyRosterButton.Content = L10n.T("lobby.roster");
        LobbyLeaveButton.Content = L10n.T("lobby.leave");
        LobbyContextButton.Content = L10n.T("lobby.context");
        DockTitle.Text = L10n.T("dock.title");
        DockFacesButton.Content = L10n.T("dock.faces");
        DockMineButton.Content = L10n.T("dock.mine");
        DockFaceBox.Header = L10n.T("dock.face");
        DockWhereButton.Content = L10n.T("dock.where");
        DockFaceButton.Content = L10n.T("dock.face");
        DockCornerBox.Header = L10n.T("dock.corner");
        DockCornerBox.Text = "bottom_right";
        DockStateBox.Header = L10n.T("dock.state");
        DockStateBox.Text = "handle";
        DockSetButton.Content = L10n.T("dock.set");
        SigTitle.Text = L10n.T("sig.title");
        SigIdBox.Header = L10n.T("sig.id");
        SigCertButton.Content = L10n.T("sig.certificate");
        SigVerifyButton.Content = L10n.T("sig.verify");
        SigCeremonyButton.Content = L10n.T("sig.ceremony");
        SigCredBox.Header = L10n.T("sig.credential");
        SigProofButton.Content = L10n.T("sig.proofing");
        MailTitle.Text = L10n.T("mail.title");
        MailShowButton.Content = L10n.T("mail.title");
        MailHostBox.Header = L10n.T("mail.host");
        MailPortBox.Header = L10n.T("mail.port");
        MailPortBox.Text = "587";
        MailSenderBox.Header = L10n.T("mail.sender");
        MailSaveButton.Content = L10n.T("mail.save");
        MailForgetButton.Content = L10n.T("mail.forget");
        MailToBox.Header = L10n.T("mail.to");
        MailTestButton.Content = L10n.T("mail.test");
        RoomsTitle.Text = L10n.T("room.title");
        RoomsListButton.Content = L10n.T("room.list");
        RoomIdBox.Header = L10n.T("room.id");
        RoomMicLendButton.Content = L10n.T("room.mic.lend");
        RoomMicBackButton.Content = L10n.T("room.mic.back");
        RoomMicWhoButton.Content = L10n.T("room.mic.who");
        DispTitle.Text = L10n.T("disp.title");
        DispRulesButton.Content = L10n.T("disp.rules");
        DispIdBox.Header = L10n.T("disp.id");
        DispShowButton.Content = L10n.T("disp.show");
        DispFacesBox.Header = L10n.T("disp.faces");
        DispFacesButton.Content = L10n.T("disp.faces");
        DispDownButton.Content = L10n.T("disp.down");
        MemberTitle.Text = L10n.T("member.title");
        MemberAccountBox.Header = L10n.T("member.account");
        MemberShowButton.Content = L10n.T("member.show");
        MemberPlanBox.Header = L10n.T("member.plan");
        MemberPlanBox.Text = "basic";
        MemberJoinButton.Content = L10n.T("member.join");
        MemberCancelButton.Content = L10n.T("member.cancel");
        HandTitle.Text = L10n.T("hand.title");
        HandProviderBox.Header = L10n.T("hand.provider");
        HandCreateButton.Content = L10n.T("hand.create");
        HandIdBox.Header = L10n.T("hand.id");
        HandTokenBox.Header = L10n.T("hand.token");
        HandOpenButton.Content = L10n.T("hand.open");
        HandRevokeButton.Content = L10n.T("hand.revoke");
        CampTitle.Text = L10n.T("camp.title");
        CampIdBox.Header = L10n.T("camp.id");
        CampShowButton.Content = L10n.T("camp.show");
        CampAmountBox.Header = L10n.T("camp.amount");
        CampWordsBox.Header = L10n.T("crowd.gift.words");
        CampGiveButton.Content = L10n.T("camp.give");
        CampCloseButton.Content = L10n.T("camp.close");
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

    // -- the place, the camera, the organization and the tour -------------

    private async void OnWhose(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var w = await ApiClient.Shared.Whose(
                PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim());
            StatusText.Text = w.DisplayName ?? "";
        });

    private async void OnMicLend(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.LendMicrophone(
            PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim(),
            AppState.Current.Pid!, AppState.Current.Token!));

    private async void OnMicBack(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.TakeBackMicrophone(
            PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim(),
            AppState.Current.Pid!, AppState.Current.Token!));

    private async void OnMicWho(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var d = await ApiClient.Shared.MicrophoneDisclosure(
                PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim(),
                AppState.Current.Token!);
            PlaceList.ItemsSource = (d.Lent ?? Array.Empty<LentRow>())
                .Select(m => new Row($"{m.InteractorId} · {m.Device}"))
                .ToList();
        });

    private async void OnMaskWear(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.WearOverlay(
            PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim(),
            AppState.Current.Pid!, MaskKindBox.Text.Trim(),
            MaskNameBox.Text.Trim(), AppState.Current.Token!));

    private async void OnMaskOff(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.TakeOffOverlay(
            PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim(),
            AppState.Current.Pid!, AppState.Current.Token!));

    private async void OnMaskWho(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var d = await ApiClient.Shared.WornOverlays(
                PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim(),
                AppState.Current.Token!);
            PlaceList.ItemsSource = (d.Worn ?? Array.Empty<WornRow>())
                .Select(w => new Row($"{w.InteractorId} · {w.Title ?? w.Kind}"))
                .ToList();
        });

    private async void OnCamRules(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.CameraVocabulary();
            CamRulesList.ItemsSource = (v.Never
                ?? new System.Collections.Generic.Dictionary<string, string>())
                .Values.OrderBy(x => x).Select(r => new Row($"· {r}"))
                .ToList();
            await ApiClient.Shared.BystanderGuidance(
                CamSubjectBox.Text.Trim());
        });

    private async void OnCamOpen(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.OpenCamera(AppState.Current.Pid!,
                PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim(),
                CamSubjectBox.Text.Trim(), CamViewerBox.Text.Trim(),
                int.TryParse(CamMinutesBox.Text, out var m) ? m : 10,
                AppState.Current.Token!);
            CamSessionBox.Text = s.Id ?? "";
        });

    private async void OnCamMine(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var mine = await ApiClient.Shared.MyCameras(
                AppState.Current.Pid!, AppState.Current.Token!);
            CamList.ItemsSource = mine.Select(s => new Row(
                $"{s.Id} · {s.Subject} · {s.State}")).ToList();
        });

    private async void OnCamDisclosure(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var d = await ApiClient.Shared.CameraDisclosureOf(
                PlaceSurfaceBox.Text.Trim(), PlaceSurfaceIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = $"{d.Live} · {d.Recording}";
        });

    private async void OnCamShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.CameraSessionOf(
                CamSessionBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = $"{s.Subject} · {s.State}";
        });

    private async void OnCamClose(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.CloseCamera(
            CamSessionBox.Text.Trim(), AppState.Current.Pid!,
            AppState.Current.Token!));

    private async void OnOrgCreate(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.CreateOrganization(
                OrgNameBox.Text.Trim(), AppState.Current.Token!);
            OrgIdBox.Text = o.Id ?? "";
        });

    private async void OnOrgList(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var orgs = await ApiClient.Shared.Organizations(
                AppState.Current.Token!);
            OrgList.ItemsSource = orgs.Select(o => new Row(
                $"{o.Id} · {o.Name}")).ToList();
        });

    private async void OnOrgDemo(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.SeedDemoOrganization(
                AppState.Current.Token!);
            OrgIdBox.Text = o.Id ?? "";
        });

    private async void OnOrgShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.OrganizationOf(
                OrgIdBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = $"{o.Name} · {o.Departments?.Length ?? 0}";
        });

    private async void OnDeptAdd(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.AddDepartment(
            OrgIdBox.Text.Trim(), DeptNameBox.Text.Trim(),
            DeptRoleBox.Text.Trim(), DeptProfileBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnCoordinate(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.Coordinate(
            OrgIdBox.Text.Trim(), GoalBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnCoordLog(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var log = await ApiClient.Shared.Coordinations(
                OrgIdBox.Text.Trim(), AppState.Current.Token!);
            CoordList.ItemsSource = log.Select(c => new Row(
                $"{c.Goal} · {c.Status}")).ToList();
        });

    private async void OnTourOutline(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.TutorialOutline();
            var chapters = o.Chapters ?? o.Lessons
                ?? Array.Empty<TutorialChapter>();
            TourList.ItemsSource = chapters.Select(c => new Row(
                $"{c.Key} · {c.Title}")).ToList();
        });

    private async void OnTourStart(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.StartTutorial(
                AppState.Current.Pid ?? "walk-in");
            TourText.Text = s.Title ?? s.Key ?? "";
        });

    private async void OnTourProgress(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.TutorialProgress(
                AppState.Current.Pid ?? "walk-in");
            TourText.Text = s.Title ?? s.Next ?? "";
        });

    private async void OnTourStep(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.TutorialStepOf(
                TourStepBox.Text.Trim());
            TourText.Text = s.Body ?? s.Title ?? "";
        });

    private async void OnTourDone(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.MarkTutorialDone(
                AppState.Current.Pid ?? "walk-in", TourStepBox.Text.Trim());
            TourText.Text = s.Next ?? "";
        });

    private async void OnTourScreen(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            if (!int.TryParse(TourScreenBox.Text, out var n)) return;
            var s = await ApiClient.Shared.TutorialForScreen(n);
            TourText.Text = s.Title ?? "";
        });

    // -- the body, the referral, the objection, the lobby and the dock ----

    private async void OnBotLog(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var log = await ApiClient.Shared.RobotCommands(
                BotIdBox.Text.Trim(), AppState.Current.Token!);
            BotList.ItemsSource = log.Select(c => new Row(
                $"{c.CreatedAt} · {c.Command}")).ToList();
        });

    private async void OnBotSkills(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var skills = await ApiClient.Shared.RobotSkills(
                BotIdBox.Text.Trim(), AppState.Current.Token!);
            BotList.ItemsSource = skills.Select(sk => new Row(
                $"{sk.Title} · {sk.PackTitle}")).ToList();
        });

    private async void OnBotDials(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.RobotSteeringOf(
                BotIdBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = s.BehaviorProfile ?? "";
        });

    private async void OnBotUnbind(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.UnbindRobot(
            BotIdBox.Text.Trim(), AppState.Current.Token!));

    private async void OnBotSteer(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.SteerRobot(BotIdBox.Text.Trim(),
                int.TryParse(BotPaceBox.Text, out var v) ? v : 50,
                AppState.Current.Token!);
            StatusText.Text = s.BehaviorProfile ?? "";
        });

    private async void OnReferMatch(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var found = await ApiClient.Shared.MatchClinicians(
                ReferAreaBox.Text.Trim());
            ClinicianList.ItemsSource = found.Select(c => new Row(
                $"{c.Id} · {c.Name} · {c.Expertise}")).ToList();
        });

    private async void OnReferPrepare(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var pkg = await ApiClient.Shared.PrepareReferral(
                AppState.Current.Pid!, AppState.Current.Pid!,
                ReferProviderBox.Text.Trim(), AppState.Current.Token!);
            ReferIdBox.Text = pkg.Id ?? pkg.ReferralId ?? "";
        });

    private async void OnReferRelease(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.ReleaseReferral(
            ReferIdBox.Text.Trim(), ReferSignatureBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnReferOpen(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var pkg = await ApiClient.Shared.OpenReferral(
                ReferIdBox.Text.Trim(), ReferTokenBox.Text.Trim());
            StatusText.Text = pkg.Status ?? "";
        });

    private async void OnReferReply(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.ReplyToReferral(
            ReferIdBox.Text.Trim(), ReferTokenBox.Text.Trim(),
            ReferWordsBox.Text.Trim()));

    private async void OnObjectShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.ObjectionOf(
                ObjectIdBox.Text.Trim());
            StatusText.Text = o.Status ?? "";
        });

    private async void OnObjectAudit(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var a = await ApiClient.Shared.ObjectionAuditOf(
                ObjectIdBox.Text.Trim(), AppState.Current.Token!);
            ObjectList.ItemsSource = (a.Events
                ?? Array.Empty<ObjectionEvent>()).Select(ev => new Row(
                    ev.Event + (ev.Sealed == true ? " ◆" : ""))).ToList();
        });

    private async void OnObjectWithdraw(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.WithdrawObjectionConsent(
                ObjectIdBox.Text.Trim());
            StatusText.Text = o.Status ?? "";
        });

    private async void OnObjectRevoke(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.RevokeObjectionBasis(
                ObjectIdBox.Text.Trim());
            StatusText.Text = o.Status ?? "";
        });

    private async void OnObjectResolve(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.ResolveObjection(
                ObjectIdBox.Text.Trim(), "dismiss",
                AppState.Current.Token!);
            StatusText.Text = o.Status ?? "";
        });

    private async void OnLobbyRules(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.LobbyVocabulary();
            LobbyList.ItemsSource = (v.Rules ?? Array.Empty<string>())
                .Select(r => new Row($"· {r}")).ToList();
        });

    private async void OnLobbySeat(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.SeatInLobby(
            LobbySessionBox.Text.Trim(), LobbyKindBox.Text.Trim(),
            LobbyMemberBox.Text.Trim(), LobbyRoleBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnLobbyRoster(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var roster = await ApiClient.Shared.LobbyRosterOf(
                LobbySessionBox.Text.Trim(), AppState.Current.Token!);
            LobbyList.ItemsSource = (roster.Members
                ?? Array.Empty<LobbySeatRow>()).Select(m => new Row(
                    $"{m.Callsign ?? m.MemberId} · {m.MemberKind} · {m.Role}"))
                .ToList();
        });

    private async void OnLobbyLeave(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.LeaveLobby(
            LobbySessionBox.Text.Trim(), LobbyMemberBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnLobbyContext(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var ctx = await ApiClient.Shared.LobbyContextOf(
                LobbySessionBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = ctx.Note ?? "";
        });

    private async void OnDockFaces(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var box = await ApiClient.Shared.DockFaces();
            DockList.ItemsSource = (box.Faces ?? Array.Empty<string>())
                .Select(f => new Row(f)).ToList();
        });

    private async void OnDockMine(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.DockSettingsOf(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = $"{s.Corner} · {s.State}";
        });

    private async void OnDockWhere(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var w = await ApiClient.Shared.DockWhereOf(
                DockFaceBox.Text.Trim());
            StatusText.Text = $"{w.Screen} · {w.Tab}";
        });

    private async void OnDockFace(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var f = await ApiClient.Shared.DockFaceOf(
                AppState.Current.Pid!, DockFaceBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = f.Line ?? f.Face ?? "";
        });

    private async void OnDockSet(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.ConfigureDock(
            AppState.Current.Pid!, DockCornerBox.Text.Trim(),
            DockStateBox.Text.Trim(), AppState.Current.Token!));

    // -- the signature, the mail, the rooms, the screen, the plan, the
    // handoff and the campaign --------------------------------------------

    private async void OnSigCert(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.SignatureCertificateOf(
                SigIdBox.Text.Trim());
            StatusText.Text = $"{c.PrintedName} · {c.Meaning} · {c.SignedAt}";
        });

    private async void OnSigVerify(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.VerifySignaturePackage();
            StatusText.Text = $"{v.Valid ?? v.Verified}";
        });

    private void OnSigCeremony(object sender, RoutedEventArgs e) =>
        StatusText.Text = ApiClient.Shared.SignatureCeremonyUrl();

    private async void OnSigProof(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.ReproofCredential(
            SigCredBox.Text.Trim(), "verified", AppState.Current.Pid!,
            AppState.Current.Token!));

    private async void OnMailShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var m = await ApiClient.Shared.MailSettings();
            StatusText.Text = $"{m.Transport} · {m.Host}";
        });

    private async void OnMailSave(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.SaveMailSettings(
            MailHostBox.Text.Trim(),
            int.TryParse(MailPortBox.Text, out var mp) ? mp : 587,
            MailSenderBox.Text.Trim(), AppState.Current.Token!));

    private async void OnMailForget(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.ForgetMailSettings(
            AppState.Current.Token!));

    private async void OnMailTest(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.TestMailSettings(
            MailToBox.Text.Trim(), AppState.Current.Token!));

    private async void OnRoomsList(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var rooms = await ApiClient.Shared.Rooms();
            RoomList.ItemsSource = rooms.Select(r => new Row(
                $"{r.Id} · {r.Topic} · {r.Channel} · {r.Participants}"))
                .ToList();
        });

    private async void OnRoomMicLend(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.LendRoomMic(
            RoomIdBox.Text.Trim(), AppState.Current.Pid!,
            AppState.Current.Token!));

    private async void OnRoomMicBack(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.TakeBackRoomMic(
            RoomIdBox.Text.Trim(), AppState.Current.Pid!,
            AppState.Current.Token!));

    private async void OnRoomMicWho(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var d = await ApiClient.Shared.RoomMicDisclosure(
                RoomIdBox.Text.Trim(), AppState.Current.Token!);
            RoomList.ItemsSource = (d.Lent ?? Array.Empty<LentRow>())
                .Select(m => new Row($"{m.InteractorId} · {m.Device}"))
                .ToList();
        });

    private async void OnDispRules(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.DisplayVocabulary();
            DispList.ItemsSource = (v.Never
                ?? new System.Collections.Generic.Dictionary<string, string>())
                .Values.OrderBy(x => x).Select(r => new Row($"· {r}"))
                .ToList();
        });

    private async void OnDispShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var d = await ApiClient.Shared.DisplayOf(DispIdBox.Text.Trim());
            StatusText.Text =
                $"{d.Kind} · {string.Join(", ", d.Faces ?? Array.Empty<string>())}";
        });

    private async void OnDispFaces(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.SetDisplayFaces(
            DispIdBox.Text.Trim(),
            DispFacesBox.Text.Split(',').Select(f => f.Trim())
                .Where(f => f.Length > 0).ToArray(),
            AppState.Current.Token!));

    private async void OnDispDown(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.TakeDownDisplay(
            DispIdBox.Text.Trim(), AppState.Current.Token!));

    private async void OnMemberShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var m = await ApiClient.Shared.MembershipOf(
                MemberAccountBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = $"{m.Plan} · {m.Status}";
        });

    private async void OnMemberJoin(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.JoinPlan(
            MemberAccountBox.Text.Trim(), MemberPlanBox.Text.Trim(),
            AppState.Current.Token!));

    private async void OnMemberCancel(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.CancelMembership(
            MemberAccountBox.Text.Trim(), AppState.Current.Token!));

    private async void OnHandCreate(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var h = await ApiClient.Shared.CreateHandoff(
                AppState.Current.Pid!, AppState.Current.Pid!,
                HandProviderBox.Text.Trim(), AppState.Current.Token!);
            HandIdBox.Text = h.Id ?? "";
            HandTokenBox.Text = h.Token ?? "";
        });

    private async void OnHandOpen(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var h = await ApiClient.Shared.OpenHandoff(
                HandIdBox.Text.Trim(), HandTokenBox.Text.Trim());
            StatusText.Text = $"{h.Provider} · {h.Sealed}";
        });

    private async void OnHandRevoke(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.RevokeHandoff(
            HandIdBox.Text.Trim(), AppState.Current.Token!));

    private async void OnCampShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.CampaignOf(CampIdBox.Text.Trim());
            StatusText.Text = $"{c.Title} · {c.Raised} / {c.Goal} · {c.Status}";
        });

    private async void OnCampGive(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.Donate(
            CampIdBox.Text.Trim(),
            double.TryParse(CampAmountBox.Text, out var amt) ? amt : 0,
            CampWordsBox.Text.Trim()));

    private async void OnCampClose(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.CloseCampaign(
            CampIdBox.Text.Trim(), AppState.Current.Token!));
}
