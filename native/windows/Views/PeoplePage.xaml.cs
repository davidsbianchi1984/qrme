using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using System.Collections.Generic;

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
    /// <summary>A public party row: the label, the button's word, and the
    /// id the join carries — never shown, only carried.</summary>
    public record PubRow(string Line, string Action, string Id);

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
        PartyPublicButton.Content = L10n.T("party.pub");
        PartyPublishButton.Content = L10n.T("party.pub.make");
        PartyUnpublishButton.Content = L10n.T("party.pub.unmake");
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
        LeaseButton.Content = L10n.T("org.lease");
        GoalBox.Header = L10n.T("org.goal");
        FromDeptBox.Header = L10n.T("org.department");
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
        RoomJoinButton.Content = L10n.T("room.join");
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
        WorkTitle.Text = L10n.T("work.title");
        WorkGoalBox.Header = L10n.T("work.goal");
        WorkStartButton.Content = L10n.T("work.start");
        WorkIdBox.Header = L10n.T("work.id");
        WorkShowButton.Content = L10n.T("work.show");
        WorkAdvanceButton.Content = L10n.T("work.advance");
        WorkCancelButton.Content = L10n.T("work.cancel");
        WorkInputBox.Header = L10n.T("work.input");
        WorkResumeButton.Content = L10n.T("work.resume");
        DeleTitle.Text = L10n.T("dele.title");
        DelePhasesBox.Header = L10n.T("dele.phases");
        DelePhasesBox.Text = "draft,review";
        DeleAllowButton.Content = L10n.T("dele.allow");
        DeleVisitorBox.Header = L10n.T("people.add");
        DeleGoalBox.Header = L10n.T("dele.goal");
        DeleStartButton.Content = L10n.T("dele.start");
        DeleIdBox.Header = L10n.T("dele.id");
        DeleShowButton.Content = L10n.T("dele.show");
        DeleAdvanceButton.Content = L10n.T("dele.advance");
        DeleInputBox.Header = L10n.T("work.input");
        DeleResumeButton.Content = L10n.T("dele.resume");
        AsstTitle.Text = L10n.T("asst.title");
        AsstMomentBox.Header = L10n.T("asst.moment");
        AsstComposeButton.Content = L10n.T("asst.compose");
        AsstTextBox.Header = L10n.T("asst.text");
        AsstProofButton.Content = L10n.T("asst.proof");
        AsstItemsBox.Header = L10n.T("asst.items");
        AsstCriteriaBox.Header = L10n.T("asst.criteria");
        AsstTriageButton.Content = L10n.T("asst.triage");
        TaskTitle.Text = L10n.T("task.title");
        TaskGrantButton.Content = L10n.T("task.grant");
        TaskRevokeButton.Content = L10n.T("task.revoke");
        TaskTopicBox.Header = L10n.T("task.topic");
        TaskRunButton.Content = L10n.T("task.run");
        PlcTitle.Text = L10n.T("plc.title");
        PlcVenueBox.Header = L10n.T("plc.venue");
        PlcLabelBox.Header = L10n.T("plc.label");
        PlcPlaceButton.Content = L10n.T("plc.place");
        PlcStatsButton.Content = L10n.T("plc.stats");
        PlcCustodyButton.Content = L10n.T("plc.custody");
        PlcIdBox.Header = L10n.T("plc.id");
        PlcRemoveButton.Content = L10n.T("plc.remove");
        SpecTitle.Text = L10n.T("spec.title");
        SpecDomainBox.Header = L10n.T("spec.domain");
        SpecIdBox.Header = L10n.T("spec.id");
        SpecSetButton.Content = L10n.T("spec.set");
        MemTitle.Text = L10n.T("mem.title");
        MemIdBox.Header = L10n.T("mem.id");
        MemShowButton.Content = L10n.T("mem.show");
        MemEraseButton.Content = L10n.T("mem.erase");
        MemAccountButton.Content = L10n.T("mem.account");
        MemForgetBox.PlaceholderText = L10n.T("mem.forget.ph");
        MemForgetButton.Content = L10n.T("mem.forget");
        MemTurnIdBox.PlaceholderText = L10n.T("mem.turnid");
        MemStrikeButton.Content = L10n.T("mem.strike");
        MemNewWordsBox.PlaceholderText = L10n.T("mem.newwords");
        MemSaveWordsButton.Content = L10n.T("action.save");
        PairTitle.Text = L10n.T("who.title");
        PairIdBox.Header = L10n.T("mem.id");
        PairThreadButton.Content = L10n.T("who.thread");
        PairEngagementButton.Content = L10n.T("who.engagement");
        PairNotesButton.Content = L10n.T("who.notes");
        PairEmbeddingButton.Content = L10n.T("who.embedding");
        SrcTitle.Text = L10n.T("src.title");
        SrcKindBox.Header = L10n.T("src.kind");
        SrcKindBox.Text = "life_event";
        SrcNameBox.Header = L10n.T("src.name");
        SrcWordsBox.Header = L10n.T("src.words");
        SrcAddButton.Content = L10n.T("src.add");
        RecTitle.Text = L10n.T("rec.title");
        RecTransparencyButton.Content = L10n.T("rec.transparency");
        RecStatsButton.Content = L10n.T("rec.stats");
        RecExportButton.Content = L10n.T("rec.export");
        RecFeedButton.Content = L10n.T("rec.feed");
        VeilTitle.Text = L10n.T("veil.title");
        VeilShowButton.Content = L10n.T("veil.show");
        VeilOnButton.Content = L10n.T("veil.on");
        VeilOffButton.Content = L10n.T("veil.off");
        VerTitle.Text = L10n.T("ver.title");
        VerShowButton.Content = L10n.T("ver.show");
        VerAbleButton.Content = L10n.T("ver.able");
        VerLevelBox.Header = L10n.T("ver.level");
        VerLevelBox.Text = "document";
        VerAttestorBox.Header = L10n.T("ver.attestor");
        VerClaimButton.Content = L10n.T("ver.claim");
        VerMoveButton.Content = L10n.T("ver.move");
        ExitTitle.Text = L10n.T("exit.title");
        ExitNameBox.Header = L10n.T("exit.rename");
        ExitPersonaBox.Header = L10n.T("exit.persona");
        ExitSaveButton.Content = L10n.T("exit.save");
        ExitSiblingsButton.Content = L10n.T("exit.siblings");
        ExitMemorialButton.Content = L10n.T("exit.memorial");
        ExitRefBox.Header = L10n.T("exit.ref");
        ExitSucceedButton.Content = L10n.T("exit.succeed");
        ExitSunsetButton.Content = L10n.T("exit.sunset");
        ExitDeleteButton.Content = L10n.T("exit.delete");
        AvaTitle.Text = L10n.T("ava.title");
        AvaShowButton.Content = L10n.T("ava.show");
        AvaBriefsButton.Content = L10n.T("ava.briefs");
        AvaAssetBox.Header = L10n.T("ava.asset");
        AvaSetButton.Content = L10n.T("ava.set");
        AvaHandleBox.Header = L10n.T("people.add");
        AvaBriefButton.Content = L10n.T("ava.brief");
        AvaMarketTitle.Text = L10n.T("ava.market");
        AvaImportBox.Header = L10n.T("ava.url.ph");
        AvaImportButton.Content = L10n.T("ava.import");
        EmblTitle.Text = L10n.T("embl.title");
        EmblListButton.Content = L10n.T("embl.list");
        EmblRulesButton.Content = L10n.T("embl.rules");
        EmblBadgeButton.Content = L10n.T("embl.badge");
        EmblPickBox.Header = L10n.T("embl.pick");
        EmblSetButton.Content = L10n.T("embl.set");
        PgTitle.Text = L10n.T("pg.title");
        PgShowButton.Content = L10n.T("pg.show");
        PgThemesButton.Content = L10n.T("pg.themes");
        FrontShowButton.Content = L10n.T("front.show");
        PgThemeBox.Header = L10n.T("pg.theme");
        PgTaglineBox.Header = L10n.T("pg.tagline");
        PgAboutBox.Header = L10n.T("pg.about");
        PgSaveButton.Content = L10n.T("pg.save");
        SurfTitle.Text = L10n.T("surf.title");
        SurfListButton.Content = L10n.T("surf.list");
        CompShowButton.Content = L10n.T("comp.show");
        SurfSetBox.Header = L10n.T("surf.title");
        SurfSetButton.Content = L10n.T("surf.set");
        FormTitle.Text = L10n.T("form.title");
        FormNameBox.Header = L10n.T("form.name");
        FormKindBox.Header = L10n.T("form.kind");
        FormKindBox.Text = "speaker";
        FormAddButton.Content = L10n.T("form.add");
        FormSameButton.Content = L10n.T("form.same");
        FormScreenBox.Header = L10n.T("plc.label");
        FormScreensButton.Content = L10n.T("disp.title");
        FormScreenAddButton.Content = L10n.T("src.add");
        SteerTitle.Text = L10n.T("steer.title");
        SteerShowButton.Content = L10n.T("steer.show");
        SteerPaceBox.Header = L10n.T("steer.pace");
        SteerAutonomyBox.Header = L10n.T("steer.autonomy");
        SteerSetButton.Content = L10n.T("steer.set");
        WristTitle.Text = L10n.T("wrist.title");
        WristShowButton.Content = L10n.T("wrist.show");
        WristTargetBox.Header = L10n.T("wrist.target");
        WristTargetBox.Text = "workflow";
        WristIdBox.Header = L10n.T("wrist.id");
        WristActionBox.Header = L10n.T("wrist.action");
        WristActionBox.Text = "advance";
        WristInputBox.Header = L10n.T("wrist.input");
        WristActButton.Content = L10n.T("wrist.act");
        AcctTitle.Text = L10n.T("acct.title");
        AcctEmailBox.Header = L10n.T("acct.email");
        AcctNameBox.Header = L10n.T("acct.name");
        AcctSignupButton.Content = L10n.T("acct.signup");
        AcctSigninButton.Content = L10n.T("acct.signin");
        AcctCodeBox.Header = L10n.T("acct.code");
        AcctVerifyButton.Content = L10n.T("acct.verify");
        AcctResendButton.Content = L10n.T("acct.resend");
        AcctResetRequestButton.Content = L10n.T("acct.reset.request");
        AcctResetButton.Content = L10n.T("acct.reset.do");
        AcctOauthButton.Content = L10n.T("acct.oauth");
        AcctOauthClaimButton.Content = "\u21bb";
        TillTitle.Text = L10n.T("till.title");
        TillPlansButton.Content = L10n.T("till.plans");
        TillSubsButton.Content = L10n.T("till.subs");
        TillOrdersButton.Content = L10n.T("till.orders");
        TillSubIdBox.Header = L10n.T("wrist.id");
        TillBeneficiaryBox.Header = L10n.T("till.beneficiary");
        TillRenewButton.Content = L10n.T("till.renew");
        TillProceedsButton.Content = L10n.T("till.proceeds");
        TillCampaignsButton.Content = L10n.T("till.campaigns");
        TillDesigneeBox.Header = L10n.T("till.designees");
        TillSetButton.Content = L10n.T("till.set");
        TillCampTitleBox.Header = L10n.T("till.camp.title");
        TillCampGoalBox.Header = L10n.T("till.camp.goal");
        TillCampAddButton.Content = L10n.T("till.camp.add");
        LifeTitle.Text = L10n.T("life.title");
        LifeCloudButton.Content = L10n.T("life.cloud");
        LifeOfflineButton.Content = L10n.T("life.offline");
        LifeLightsButton.Content = L10n.T("life.lights");
        LifeTopicsButton.Content = L10n.T("life.help.topics");
        LifeQuestionBox.Header = L10n.T("life.help");
        LifeAskButton.Content = L10n.T("life.help.ask");
        LifeProvidersButton.Content = L10n.T("life.providers");
        LifeProvNameBox.Header = L10n.T("life.prov.name");
        LifeProvAreaBox.Header = L10n.T("life.prov.area");
        LifeProvAddButton.Content = L10n.T("life.prov.add");
        BcnTitle.Text = L10n.T("bcn.title");
        BcnIdBox.Header = L10n.T("bcn.id");
        BcnCardButton.Content = L10n.T("bcn.card");
        BcnDeskButton.Content = L10n.T("bcn.desk");
        BcnQrButton.Content = L10n.T("bcn.qr");
        BcnCidBox.Header = L10n.T("people.add");
        BcnSocialButton.Content = L10n.T("bcn.social");
        BcnPairButton.Content = L10n.T("bcn.pair");
        ModqTitle.Text = L10n.T("modq.title");
        ModqShowButton.Content = L10n.T("modq.show");
        ModqMsgBox.Header = L10n.T("modq.msg");
        ModqApproveButton.Content = L10n.T("modq.approve");
        ModqRejectButton.Content = L10n.T("modq.reject");
        ModqInteractorBox.Header = L10n.T("people.add");
        ModqContentBox.Header = L10n.T("modq.edit");
        ModqEditButton.Content = L10n.T("modq.edit");
        ModqRetractButton.Content = L10n.T("modq.retract");
        RevwTitle.Text = L10n.T("revw.title");
        RevwShowButton.Content = L10n.T("revw.show");
        RevwInteractorBox.Header = L10n.T("people.add");
        RevwRatingBox.Header = L10n.T("revw.rating");
        RevwBodyBox.Header = L10n.T("revw.body");
        RevwLeaveButton.Content = L10n.T("revw.leave");
        WmTitle.Text = L10n.T("wm.title");
        WmIdBox.Header = L10n.T("wm.id");
        WmResolveButton.Content = L10n.T("wm.resolve");
        WmContentBox.Header = L10n.T("wm.content");
        WmVerifyButton.Content = L10n.T("wm.verify");
        MedTitle.Text = L10n.T("med.title");
        MedLimitsButton.Content = L10n.T("med.limits");
        MedPlatformsButton.Content = L10n.T("med.platforms");
        MedFilenameBox.Header = L10n.T("wear.name");
        MedUploadButton.Content = L10n.T("med.upload");
        WearTitle.Text = L10n.T("wear.title");
        WearListButton.Content = L10n.T("wear.list");
        WearNameBox.Header = L10n.T("wear.name");
        WearKindBox.Header = L10n.T("wear.kind");
        WearPairButton.Content = L10n.T("wear.pair");
        WearUnpairButton.Content = L10n.T("wear.unpair");
        BornTitle.Text = L10n.T("born.title");
        BornOwnerBox.Header = L10n.T("born.owner");
        BornNameBox.Header = L10n.T("born.name");
        BornSocialBox.Header = L10n.T("born.social");
        BornHumorBox.Header = L10n.T("born.humor");
        BornMattersBox.Header = L10n.T("born.matters");
        BornComfortBox.Header = L10n.T("born.comfort");
        BornMakeButton.Content = L10n.T("born.make");
        BornSourcesBox.Header = L10n.T("born.sources");
        BornBlendButton.Content = L10n.T("born.blend");
        BornPackIndustryBox.Header = L10n.T("born.pack.industry");
        BornPackTitleBox.Header = L10n.T("born.pack.title");
        BornPackPublishButton.Content = L10n.T("born.pack.publish");
        BornPackSeedButton.Content = L10n.T("born.pack.seed");
        MindTitle.Text = L10n.T("mind.title");
        MindScenarioBox.Header = L10n.T("mind.scenario");
        MindSimulateButton.Content = L10n.T("mind.simulate");
        MindRunsButton.Content = L10n.T("mind.runs");
        MindTuneButton.Content = L10n.T("mind.tune");
        MindCloudButton.Content = L10n.T("mind.cloud");
        MindRevokeButton.Content = L10n.T("mind.revoke");
        MindCidBox.Header = L10n.T("people.add");
        MindExcursionButton.Content = L10n.T("mind.excursion");
        ReachTitle.Text = L10n.T("reach.title");
        ReachCheckinButton.Content = L10n.T("reach.checkin");
        ReachRateUpButton.Content = L10n.T("reach.rate.up");
        ReachRateDownButton.Content = L10n.T("reach.rate.down");
        ReachQuietStartBox.Header = L10n.T("reach.quiet.start");
        ReachQuietEndBox.Header = L10n.T("reach.quiet.end");
        ReachQuietSetButton.Content = L10n.T("reach.quiet.set");
        ReachReferralsButton.Content = L10n.T("reach.referrals");
        LicTitle.Text = L10n.T("lic.title");
        LicAcquireButton.Content = L10n.T("lic.acquire");
        LicGrantBox.Header = L10n.T("lic.grant");
        LicDeriveButton.Content = L10n.T("lic.derive");
        SensTitle.Text = L10n.T("sens.title");
        SensSceneBox.Header = L10n.T("sens.scene");
        SensGoalBox.Header = L10n.T("wrist.input");
        SensPerceiveButton.Content = L10n.T("sens.perceive");
        SensMicsButton.Content = L10n.T("sens.mics");
        SensVocabButton.Content = L10n.T("sens.vocab");
        SensOverlaysButton.Content = L10n.T("sens.overlays");
        SensHealthButton.Content = L10n.T("life.status");
        SensExpBox.Header = L10n.T("sens.exp");
        SensExpSetButton.Content = L10n.T("sens.exp.set");
        SensCredBox.Header = L10n.T("lic.grant");
        SensCredRemoveButton.Content = L10n.T("exit.delete");
        SensDeskJoinButton.Content = L10n.T("bcn.desk");
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

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        await Load();
        await LoadWorkshop();
    }

    /// <summary>What the workshop shows before any button: the delegation
    /// offer this profile advertises, and the venues a rated placement
    /// could go to — the same two reads the other shells do on appear.</summary>
    private async Task LoadWorkshop()
    {
        var s = AppState.Current;
        if (s.Pid is null) return;
        try
        {
            var offer = await ApiClient.Shared.DelegationOfferOf(s.Pid);
            DeleOfferText.Text = offer.Delegation == true
                ? string.Join(", ", offer.Phases ?? []) : "—";
            var venues = await ApiClient.Shared.RatedVenues();
            PlcVenuesText.Text = string.Join(", ",
                venues.Select(v => v.Key));
            var memories = await ApiClient.Shared.Memories(
                s.Pid, s.Token!);
            MemList.ItemsSource = memories.Select(m => new Row(
                $"{m.InteractorName} · {m.Turns}")).ToList();
            var sources = await ApiClient.Shared.Sources(s.Pid, s.Token!);
            SrcList.ItemsSource = sources.Select(r => new Row(
                $"{r.Kind} · {r.Title}")).ToList();
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

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

    // The browse door. The id box stays the private one — these rows join
    // without ever showing an id.
    private async void OnPartyPublicList(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var box = await ApiClient.Shared.PublicParties();
            PartyPublicList.ItemsSource = box.Parties.Select(c => new PubRow(
                $"{c.Title} · {c.People}", L10n.T("party.join"), c.Id))
                .ToList();
        });

    private async void OnPartyPublicJoin(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var id = (string)((Button)sender).Tag;
            PartyIdBox.Text = id;
            ShowParty(await ApiClient.Shared.JoinParty(
                id, AppState.Current.Pid!, AppState.Current.Token!));
        });

    // Host only, both directions; the id keeps working either way.
    private async void OnPartyPublish(object sender, RoutedEventArgs e) =>
        await Try(async () => ShowParty(await ApiClient.Shared.PublishParty(
            PartyIdBox.Text.Trim(), AppState.Current.Token!)));

    private async void OnPartyUnpublish(object sender, RoutedEventArgs e) =>
        await Try(async () => ShowParty(await ApiClient.Shared.UnpublishParty(
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
            PlaceList.ItemsSource = (d.Overlays ?? Array.Empty<WornRow>())
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

    // AI for lease: the same three fields, but the profile id names somebody
    // else's licensed specialist; the fee goes to its owner, who can revoke.
    private async void OnLease(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var lease = await ApiClient.Shared.LeaseSpecialist(
                OrgIdBox.Text.Trim(), DeptProfileBox.Text.Trim(),
                DeptNameBox.Text.Trim(), DeptRoleBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = lease.LeaseId;
        });

    private async void OnCoordinate(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.Coordinate(
            OrgIdBox.Text.Trim(), GoalBox.Text.Trim(),
            FromDeptBox.Text.Trim(), AppState.Current.Token!));

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
            TourList.ItemsSource = (o.Chapters ?? Array.Empty<TutorialChapter>())
                .Select(c => new Row(
                    $"{c.Chapter} · {(c.Steps?.Length ?? 0)}")).ToList();
        });

    private async void OnTourStart(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.StartTutorial(
                AppState.Current.Pid ?? "walk-in");
            TourText.Text = s.Step?.Title ?? s.Step?.Key ?? "";
        });

    private async void OnTourProgress(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.TutorialProgress(
                AppState.Current.Pid ?? "walk-in");
            TourText.Text = s.Step is null ? ""
                : $"{s.Step.Chapter} · {s.Step.Title} — {s.Step.TryIt}";
        });

    private async void OnTourStep(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.TutorialStepOf(
                TourStepBox.Text.Trim());
            TourText.Text = s.What ?? s.Title ?? "";
        });

    private async void OnTourDone(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.MarkTutorialDone(
                AppState.Current.Pid ?? "walk-in", TourStepBox.Text.Trim());
            TourText.Text = s.Step?.Title ?? "";
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
            DockList.ItemsSource = (box.Faces ?? [])
                .Select(f => new Row($"{f.Key} · {f.Value}")).ToList();
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
            StatusText.Text = $"{w.Title} · {w.Path} · #{w.Screen}";
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

    // The list used to show rooms nobody could enter — the door in was
    // frozen at creation. Joining takes the interactor token; a room id
    // alone is not being here.
    private async void OnRoomJoin(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.JoinRoom(
            RoomIdBox.Text.Trim(), AppState.Current.InteractorToken!));

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
            DispList.ItemsSource = (v.Never ?? [])
                .Select(r => new Row($"{r.Thing} · {r.Why}")).ToList();
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

    // -- the owner's workshop ---------------------------------------------

    private string _grantId = "";
    private string _grantToken = "";

    private async void OnWorkStart(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var made = await ApiClient.Shared.StartWorkflow(
                AppState.Current.Pid!, WorkGoalBox.Text.Trim(),
                AppState.Current.Token!);
            WorkIdBox.Text = made.Id;
            WorkGoalBox.Text = "";
            await ReloadWorkflows();
        });

    private async Task ReloadWorkflows()
    {
        var rows = await ApiClient.Shared.Workflows(
            AppState.Current.Pid!, AppState.Current.Token!);
        WorkList.ItemsSource = rows.Select(w => new Row(
            $"{w.Goal} \u00b7 {w.Status} \u00b7 {w.NextPhase ?? "\u2014"}"))
            .ToList();
    }

    private async void OnWorkShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var w = await ApiClient.Shared.WorkflowOf(
                AppState.Current.Pid!, WorkIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = $"{w.Status} \u00b7 {w.NextPhase ?? "\u2014"}";
        });

    private async void OnWorkAdvance(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var w = await ApiClient.Shared.AdvanceWorkflow(
                AppState.Current.Pid!, WorkIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = $"{w.Status} \u00b7 {w.NextPhase ?? "\u2014"}";
            await ReloadWorkflows();
        });

    private async void OnWorkCancel(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.CancelWorkflow(
                AppState.Current.Pid!, WorkIdBox.Text.Trim(),
                AppState.Current.Token!);
            await ReloadWorkflows();
        });

    private async void OnWorkResume(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var w = await ApiClient.Shared.ResumeWorkflow(
                AppState.Current.Pid!, WorkIdBox.Text.Trim(),
                WorkInputBox.Text.Trim(), AppState.Current.Token!);
            WorkInputBox.Text = "";
            StatusText.Text = w.Status ?? "";
            await ReloadWorkflows();
        });

    private async void OnDeleAllow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var phases = DelePhasesBox.Text.Split(',')
                .Select(x => x.Trim()).Where(x => x.Length > 0).ToArray();
            var offer = await ApiClient.Shared.SetDelegation(
                AppState.Current.Pid!, phases, AppState.Current.Token!);
            DeleOfferText.Text = string.Join(", ", offer.Phases ?? []);
        });

    private async void OnDeleStart(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var made = await ApiClient.Shared.StartDelegatedWorkflow(
                AppState.Current.Pid!, DeleVisitorBox.Text.Trim(),
                DeleGoalBox.Text.Trim(), AppState.Current.Token!);
            DeleIdBox.Text = made.Id;
            DeleGoalBox.Text = "";
        });

    private async void OnDeleShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var w = await ApiClient.Shared.DelegatedWorkflowOf(
                AppState.Current.Pid!, DeleIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = $"{w.Status} \u00b7 {w.DelegatedTo}";
        });

    private async void OnDeleAdvance(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var w = await ApiClient.Shared.AdvanceDelegatedWorkflow(
                AppState.Current.Pid!, DeleIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = w.Status ?? "";
        });

    private async void OnDeleResume(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var w = await ApiClient.Shared.ResumeDelegatedWorkflow(
                AppState.Current.Pid!, DeleIdBox.Text.Trim(),
                DeleInputBox.Text.Trim(), AppState.Current.Token!);
            DeleInputBox.Text = "";
            StatusText.Text = w.Status ?? "";
        });

    private async void OnAsstCompose(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var made = await ApiClient.Shared.ComposeNote(
                AppState.Current.Pid!, AsstMomentBox.Text.Trim(),
                AppState.Current.Token!);
            AsstMomentBox.Text = "";
            StatusText.Text = made.Content ?? "";
            await ReloadWorks();
        });

    private async Task ReloadWorks()
    {
        var rows = await ApiClient.Shared.ComposedWorks(
            AppState.Current.Pid!, AppState.Current.Token!);
        AsstWorksList.ItemsSource = rows.Select(w => new Row(
            $"{w.Kind} \u00b7 {w.Moment}")).ToList();
    }

    private async void OnAsstProof(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Proofread(
                AppState.Current.Pid!, AsstTextBox.Text,
                AppState.Current.Token!);
            StatusText.Text = outp.Edited
                ?? string.Join(" \u00b7 ", outp.Suggestions ?? []);
        });

    private async void OnAsstTriage(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var items = AsstItemsBox.Text.Split(';')
                .Select(x => x.Trim()).Where(x => x.Length > 0)
                .Select((t, i) => (object)new { id = $"i{i}", text = t })
                .ToArray();
            var outp = await ApiClient.Shared.Triage(
                AppState.Current.Pid!, items, 1,
                AsstCriteriaBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = string.Join(" \u00b7 ",
                outp.Kept.Select(k => k.Reason));
        });

    private async void OnTaskGrant(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var g = await ApiClient.Shared.MintTaskGrant(
                AppState.Current.Pid!, AppState.Current.Token!);
            _grantId = g.Id ?? "";
            _grantToken = g.Token ?? "";
            StatusText.Text = string.Join(",", g.Scope ?? []);
        });

    private async void OnTaskRevoke(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.RevokeTaskGrant(
                _grantId, AppState.Current.Token!);
            _grantId = ""; _grantToken = "";
        });

    private async void OnTaskRun(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.RunTask(
                AppState.Current.Pid!, TaskTopicBox.Text.Trim(),
                _grantToken, AppState.Current.Token!);
            TaskTopicBox.Text = "";
            StatusText.Text = outp.Reason ?? outp.Status ?? "";
            var rows = await ApiClient.Shared.TasksRun(
                AppState.Current.Pid!, AppState.Current.Token!);
            TaskList.ItemsSource = rows.Select(t => new Row(
                $"{t.Topic} \u00b7 {t.Status}")).ToList();
        });

    private async void OnPlcPlace(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var made = await ApiClient.Shared.PlaceRated(
                AppState.Current.Pid!, PlcVenueBox.Text.Trim(),
                PlcLabelBox.Text.Trim(), AppState.Current.Token!);
            PlcIdBox.Text = made.PlacementId ?? "";
            StatusText.Text = made.ScanUrl ?? "";
            await ReloadPlacements();
        });

    private async Task ReloadPlacements()
    {
        var rows = await ApiClient.Shared.Placements(
            AppState.Current.Pid!, AppState.Current.Token!);
        PlcList.ItemsSource = rows.Select(r => new Row(
            $"{r.Label ?? r.VenueName} \u00b7 {r.Scans}")).ToList();
    }

    private async void OnPlcStats(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.PlacementAnalytics(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = $"{s.Funnel.Resolutions} \u2192 "
                + $"{s.Funnel.VerifiedViews} \u2192 "
                + $"{s.Funnel.UniqueChatters}";
        });

    private async void OnPlcCustody(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.PlacementCustodyOf(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = $"{c.Count} \u00b7 {c.ChainIntact}";
        });

    private async void OnPlcRemove(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.RemovePlacement(
                PlcIdBox.Text.Trim(), AppState.Current.Token!);
            PlcIdBox.Text = "";
            await ReloadPlacements();
        });

    private async void OnSpecSet(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.SetSpecialist(
                AppState.Current.Pid!, SpecDomainBox.Text.Trim(),
                SpecIdBox.Text.Trim(), AppState.Current.Token!);
            SpecDomainBox.Text = ""; SpecIdBox.Text = "";
            var rows = await ApiClient.Shared.Specialists(
                AppState.Current.Pid!, AppState.Current.Token!);
            SpecList.ItemsSource = rows.Select(r => new Row(
                $"{r.Domain} \u00b7 {r.SpecialistProfileId}")).ToList();
        });

    // -- the record, the veil and the exit --------------------------------

    private async void OnMemShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            // The remembrance leads: what the profile still carries of this
            // person past the recent window, then the last turns.
            var kept = await ApiClient.Shared.Remembrance(
                AppState.Current.Pid!, MemIdBox.Text.Trim(),
                AppState.Current.Token!);
            var turns = await ApiClient.Shared.Memory(
                AppState.Current.Pid!, MemIdBox.Text.Trim(),
                AppState.Current.Token!);
            // Ids ride along so the strike/rewrite doors below have
            // something to be given; a rewritten turn wears its mark.
            var parts = turns.TakeLast(3)
                .Select(t => t.Id + " \u2014 " + t.Content
                    + (t.Edited ? " \u270e" : "")).ToList();
            if (kept.Content is not null) parts.Insert(0, kept.Content);
            StatusText.Text = string.Join(" \u00b7 ", parts);
        });

    private async void OnMemErase(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.EraseMemory(
                AppState.Current.Pid!, MemIdBox.Text.Trim(),
                AppState.Current.Token!);
            MemIdBox.Text = "";
            var rows = await ApiClient.Shared.Memories(
                AppState.Current.Pid!, AppState.Current.Token!);
            MemList.ItemsSource = rows.Select(m => new Row(
                $"{m.InteractorName} \u00b7 {m.Turns}")).ToList();
        });

    private async void OnMemAccount(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            // The account: the kept paragraph and the honest counts.
            var a = await ApiClient.Shared.MemoryAccount(
                AppState.Current.Pid!, MemIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = (a.Remembers ?? "—") + " · "
                + a.FoldedTurns + "+" + a.RecentTurns;
        });

    private async void OnMemForget(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            // Forget that one thing; the kept memory re-folds from what
            // remains, never from what was struck.
            var outp = await ApiClient.Shared.ForgetMemory(
                AppState.Current.Pid!, MemIdBox.Text.Trim(),
                MemForgetBox.Text.Trim(), AppState.Current.Token!);
            MemForgetBox.Text = "";
            StatusText.Text = outp.ForgottenTurns.ToString();
        });

    private async void OnMemStrike(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            // Strike the selected turn; the kept memory re-folds from
            // what remains — never from what was struck.
            var outp = await ApiClient.Shared.StrikeTurns(
                AppState.Current.Pid!, MemIdBox.Text.Trim(),
                new[] { MemTurnIdBox.Text.Trim() }, AppState.Current.Token!);
            MemTurnIdBox.Text = "";
            StatusText.Text = outp.StruckTurns.ToString();
        });

    private async void OnMemSaveWords(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            // Rewrite one remembered turn; a profile turn loses its
            // synthetic-media credential with the rewrite.
            var outp = await ApiClient.Shared.EditTurn(
                AppState.Current.Pid!, MemIdBox.Text.Trim(),
                MemTurnIdBox.Text.Trim(), MemNewWordsBox.Text.Trim(),
                AppState.Current.Token!);
            MemNewWordsBox.Text = "";
            StatusText.Text = outp.Turn?.Content ?? "";
        });

    private async void OnPairThread(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var t = await ApiClient.Shared.ThreadOf(
                AppState.Current.Pid!, PairIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = t.Messages.Length.ToString();
        });

    private async void OnPairEngagement(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var g = await ApiClient.Shared.EngagementOf(
                AppState.Current.Pid!, PairIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = (g.Sessions ?? 0).ToString();
        });

    private async void OnPairNotes(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var notes = await ApiClient.Shared.ClinicalNotes(
                AppState.Current.Pid!, PairIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = string.Join(" \u00b7 ",
                notes.Select(n => n.Note));
        });

    private async void OnPairEmbedding(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.EmbeddingOf(
                AppState.Current.Pid!, PairIdBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = "\u2713";
        });

    private async void OnSrcAdd(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.AddSource(
                AppState.Current.Pid!, SrcKindBox.Text.Trim(),
                SrcNameBox.Text.Trim(), SrcWordsBox.Text,
                AppState.Current.Token!);
            SrcNameBox.Text = ""; SrcWordsBox.Text = "";
            var rows = await ApiClient.Shared.Sources(
                AppState.Current.Pid!, AppState.Current.Token!);
            SrcList.ItemsSource = rows.Select(r => new Row(
                $"{r.Kind} \u00b7 {r.Title}")).ToList();
        });

    private async void OnRecTransparency(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var t = await ApiClient.Shared.TransparencyOf(
                AppState.Current.Pid!);
            StatusText.Text =
                $"{t.ActiveRelationships} \u00b7 {t.ModelEffective}";
        });

    private async void OnRecStats(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var s = await ApiClient.Shared.ProfileStats(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = $"{s.Sessions} \u00b7 {s.MemoryEntries} "
                + $"\u00b7 {s.Interactors} \u00b7 {s.Sources}";
        });

    private async void OnRecExport(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.ExportProfile(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = $"{o.Messages.Length} \u00b7 "
                + $"{o.Posts.Length} \u00b7 {o.Sources.Length}";
        });

    private async void OnRecFeed(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var f = await ApiClient.Shared.FeedOf(AppState.Current.Pid!);
            StatusText.Text = $"{f.Posts.Length} \u00b7 "
                + string.Join(", ", f.RankedOn);
        });

    private async void OnVeilShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.AnonymityOf(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = string.Join(" \u00b7 ",
                v.NotWithheld ?? []);
        });

    private async void OnVeilOn(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.SetAnonymity(
            AppState.Current.Pid!, true, AppState.Current.Token!));

    private async void OnVeilOff(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.SetAnonymity(
            AppState.Current.Pid!, false, AppState.Current.Token!));

    private async void OnVerShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.VerificationOf(
                AppState.Current.Pid!);
            StatusText.Text =
                $"{v.Level ?? "\u2014"} \u00b7 {v.Attestor ?? "\u2014"}";
        });

    private async void OnVerAble(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.VerifiableOf(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = v.Reason ?? v.CanVerify.ToString();
        });

    private async void OnVerClaim(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.ClaimVerification(
            AppState.Current.Pid!, VerLevelBox.Text.Trim(),
            VerAttestorBox.Text.Trim(), AppState.Current.Token!));

    private async void OnVerMove(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.MoveBadgeHere(
            AppState.Current.Pid!, AppState.Current.Token!));

    private async void OnExitSave(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.EditProfile(
                AppState.Current.Pid!, ExitNameBox.Text.Trim(),
                ExitPersonaBox.Text.Trim(), AppState.Current.Token!);
            ExitNameBox.Text = ""; ExitPersonaBox.Text = "";
        });

    private async void OnExitSiblings(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var r = await ApiClient.Shared.Siblings(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = string.Join(" \u00b7 ",
                (r.Profiles ?? []).Select(x => x.DisplayName ?? x.ProfileId));
        });

    private async void OnExitMemorial(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var m = await ApiClient.Shared.MemorialOf(
                AppState.Current.Pid!);
            StatusText.Text = $"{m.DisplayName} \u00b7 "
                + $"{m.RelationshipsTouched ?? 0}";
        });

    private async void OnExitSucceed(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.Succeed(
                AppState.Current.Pid!, ExitRefBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = (o.Succeeded ?? false).ToString();
        });

    private async void OnExitSunset(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var o = await ApiClient.Shared.Sunset(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = (o.Farewells ?? 0).ToString();
        });

    private async void OnExitDelete(object sender, RoutedEventArgs e) =>
        await Try(async () => await ApiClient.Shared.DeleteProfile(
            AppState.Current.Pid!, AppState.Current.Token!));

    // -- the face it shows the world --------------------------------------

    private async void OnAvaShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var a = await ApiClient.Shared.AvatarOf(AppState.Current.Pid!);
            StatusText.Text = ((a.AssetMarked ?? false) ? "AI" : "\u2014")
                + " \u00b7 " + (a.Likeness?.Note ?? "\u2014");
        });

    private async void OnAvaBriefs(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.AvatarBriefs();
            StatusText.Text = (c.Briefs?.Length ?? 0).ToString();
        });

    private async void OnAvaSet(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.SetAvatar(AppState.Current.Pid!,
                AvaAssetBox.Text.Trim(), AppState.Current.Token!);
            AvaAssetBox.Text = "";
        });

    private async void OnAvaBrief(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var b = await ApiClient.Shared.AvatarBrief(
                AvaHandleBox.Text.Trim());
            StatusText.Text = b.Brief ?? "";
        });

    private async void OnAvaImport(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var shelf = await ApiClient.Shared.AvatarMarket();
            await ApiClient.Shared.ImportAvatar(AppState.Current.Pid!,
                "other", AvaImportBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = $"{shelf.Sources.Length} · imported";
            AvaImportBox.Text = "";
        });

    private async void OnEmblList(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.IdentityEmblems();
            StatusText.Text = string.Join(" \u00b7 ",
                (c.Emblems ?? []).Select(x => x.Emblem));
        });

    private async void OnEmblRules(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var v = await ApiClient.Shared.IdentityVocabularyOf();
            StatusText.Text = string.Join(" \u00b7 ",
                v.WithheldWhenAnonymous);
        });

    private async void OnEmblBadge(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var b = await ApiClient.Shared.BadgeOf(AppState.Current.Pid!);
            StatusText.Text =
                $"{b.Level ?? "\u2014"} \u00b7 {b.Attestor ?? "\u2014"}";
        });

    private async void OnEmblSet(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.SetEmblem(AppState.Current.Pid!,
                EmblPickBox.Text.Trim(), AppState.Current.Token!);
            EmblPickBox.Text = "";
        });

    private async void OnPgShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var pg = await ApiClient.Shared.PageOf(AppState.Current.Pid!);
            StatusText.Text =
                $"{pg.Theme?.Label ?? "\u2014"} \u00b7 {pg.Tagline ?? "\u2014"}";
        });

    private async void OnPgThemes(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.PageThemes();
            StatusText.Text = string.Join(" \u00b7 ",
                (c.Themes ?? []).Select(t => t.Id));
        });

    private async void OnFrontShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var f = await ApiClient.Shared.FrontPage(AppState.Current.Pid!);
            StatusText.Text = $"{f.DisplayName ?? "\u2014"} \u00b7 "
                + (f.Headline ?? "\u2014") + " \u00b7 " + (f.AiDisclosure ?? "\u2014");
        });

    private async void OnPgSave(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.EditPage(AppState.Current.Pid!,
                PgThemeBox.Text.Trim(), PgTaglineBox.Text.Trim(),
                PgAboutBox.Text.Trim(), AppState.Current.Token!);
            PgThemeBox.Text = ""; PgTaglineBox.Text = "";
            PgAboutBox.Text = "";
        });

    private async void OnSurfList(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var su = await ApiClient.Shared.SurfacesOf(
                AppState.Current.Pid!);
            StatusText.Text = string.Join(" \u00b7 ", su.Surfaces);
        });

    private async void OnCompShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.CompositionOf(
                AppState.Current.Pid!);
            StatusText.Text = string.Join(" \u00b7 ",
                (c.Sources ?? []).Select(x =>
                    $"{x.DisplayName} {(int)Math.Round((x.Weight ?? 0) * 100)}%"
                    + (x.Aspect is null ? "" : $" ({x.Aspect})")));
        });

    private async void OnSurfSet(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var parts = SurfSetBox.Text.Split(',')
                .Select(x => x.Trim()).Where(x => x.Length > 0).ToArray();
            await ApiClient.Shared.SetSurfaces(AppState.Current.Pid!,
                parts, AppState.Current.Token!);
            SurfSetBox.Text = "";
        });

    private async void OnFormAdd(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.AddEmbodiment(AppState.Current.Pid!,
                FormNameBox.Text.Trim(), FormKindBox.Text.Trim(),
                AppState.Current.Token!);
            FormNameBox.Text = "";
            var rows = await ApiClient.Shared.Embodiments(
                AppState.Current.Pid!, AppState.Current.Token!);
            FormList.ItemsSource = rows.Select(r => new Row(
                $"{r.Name} \u00b7 {r.Kind}")).ToList();
        });

    private async void OnFormSame(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var c = await ApiClient.Shared.EmbodimentConsistency(
                AppState.Current.Pid!);
            StatusText.Text = string.Join(" \u00b7 ",
                (c.Embodiments ?? []).Select(x => x.Name));
        });

    private async void OnFormScreens(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var rows = await ApiClient.Shared.ProfileDisplays(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = string.Join(" \u00b7 ",
                rows.Displays.Select(r => r.Label));
        });

    private async void OnFormScreenAdd(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.AddProfileDisplay(AppState.Current.Pid!,
                "wall_panel", FormScreenBox.Text.Trim(),
                AppState.Current.Token!);
            FormScreenBox.Text = "";
        });

    private async void OnSteerShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var st = await ApiClient.Shared.SteeringOf(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = string.Join(" \u00b7 ", st.Values
                .OrderBy(kv => kv.Key)
                .Select(kv => $"{kv.Key} {kv.Value}"));
        });

    private async void OnSteerSet(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var values =
                new System.Collections.Generic.Dictionary<string, int>();
            if (int.TryParse(SteerPaceBox.Text.Trim(), out var pace))
                values["pace"] = pace;
            if (int.TryParse(SteerAutonomyBox.Text.Trim(), out var auto))
                values["autonomy"] = auto;
            await ApiClient.Shared.SetSteering(AppState.Current.Pid!,
                values, AppState.Current.Token!);
            SteerPaceBox.Text = ""; SteerAutonomyBox.Text = "";
        });

    private async void OnWristShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var f = await ApiClient.Shared.WatchFace(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = $"{f.Profile.Light} \u00b7 "
                + $"{f.Summary.Working} \u00b7 "
                + $"{f.Summary.NeedingAssistance} \u00b7 "
                + $"{f.Summary.Stopped}";
        });

    private async void OnWristAct(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.WatchAct(
                AppState.Current.Pid!, WristTargetBox.Text.Trim(),
                WristIdBox.Text.Trim(), WristActionBox.Text.Trim(),
                WristInputBox.Text.Trim(), AppState.Current.Token!);
            WristInputBox.Text = "";
            StatusText.Text = outp.Status ?? "";
        });

    private string _oauthState = "";

    private async void OnAcctSignup(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Signup(
                AcctEmailBox.Text.Trim(), AcctPasswordBox.Password,
                AcctNameBox.Text.Trim());
            StatusText.Text = outp.CodeDelivery ?? "";
        });

    private async void OnAcctSignin(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Signin(
                AcctEmailBox.Text.Trim(), AcctPasswordBox.Password);
            StatusText.Text = outp.DisplayName ?? outp.Email ?? "";
        });

    private async void OnAcctVerify(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.VerifyEmail(
                AcctEmailBox.Text.Trim(), AcctCodeBox.Text.Trim());
            StatusText.Text = outp.Email ?? "";
        });

    private async void OnAcctResend(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.ResendCode(
                AcctEmailBox.Text.Trim());
            StatusText.Text = outp.CodeDelivery ?? "";
        });

    private async void OnAcctResetRequest(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.RequestPasswordReset(
                AcctEmailBox.Text.Trim());
            StatusText.Text = outp.CodeDelivery ?? "";
        });

    private async void OnAcctReset(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.ResetPassword(
                AcctEmailBox.Text.Trim(), AcctCodeBox.Text.Trim(),
                AcctNewPasswordBox.Password);
            AcctNewPasswordBox.Password = "";
            StatusText.Text = outp.Reset == true ? "\u2713" : "";
        });

    private async void OnAcctOauth(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var doors = await ApiClient.Shared.OAuthProviders();
            if (doors.Providers.Length == 0) { StatusText.Text = "\u2014"; return; }
            var start = await ApiClient.Shared.OAuthStart(
                doors.Providers[0].Provider);
            _oauthState = start.State ?? "";
            StatusText.Text = doors.Providers[0].Provider + " \u00b7 "
                + (start.Url ?? "");
        });

    private async void OnAcctOauthClaim(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.OAuthClaim(_oauthState);
            StatusText.Text = outp.Ready == true
                ? (outp.Email ?? "\u2713") : "\u2026";
        });

    private async void OnTillPlans(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Plans();
            StatusText.Text = string.Join(" \u00b7 ",
                outp.Plans.Select(pl => pl.Plan));
        });

    private async void OnTillSubs(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.MySubscriptions(
                AppState.Current.Token!);
            StatusText.Text = outp.Subscriptions.Length.ToString();
        });

    private async void OnTillOrders(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.MyOrders(
                AppState.Current.Token!);
            StatusText.Text = outp.Orders.Length.ToString();
        });

    private async void OnTillRenew(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.RenewSubscription(
                TillSubIdBox.Text.Trim(), TillBeneficiaryBox.Text.Trim(),
                AppState.Current.Token!);
            StatusText.Text = (outp.Periods ?? 0).ToString();
        });

    private async void OnTillProceeds(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.ProceedsOf(
                AppState.Current.Pid!);
            StatusText.Text = string.Join(" \u00b7 ",
                outp.ProceedsTo.Select(d => d.Name));
        });

    private async void OnTillSet(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            await ApiClient.Shared.SetProceeds(AppState.Current.Pid!,
                TillDesigneeBox.Text.Trim(), AppState.Current.Token!);
            TillDesigneeBox.Text = "";
            StatusText.Text = "\u2713";
        });

    private async void OnTillCampaigns(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.CampaignsOf(
                AppState.Current.Pid!);
            StatusText.Text = outp.Length.ToString();
        });

    private async void OnTillCampAdd(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            double.TryParse(TillCampGoalBox.Text.Trim(), out var goal);
            var outp = await ApiClient.Shared.AddCampaign(
                AppState.Current.Pid!, TillCampTitleBox.Text.Trim(), goal,
                AppState.Current.Token!);
            TillCampTitleBox.Text = ""; TillCampGoalBox.Text = "";
            StatusText.Text = outp.Title ?? outp.Id;
        });

    private async void OnLifeCloud(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.CloudStatus();
            StatusText.Text = (outp.Cloud ? "\u2601" : "\u2014")
                + " \u00b7 " + (outp.Fallback ?? "");
        });

    private async void OnLifeOffline(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.OfflineStatus();
            StatusText.Text = outp.Provider ?? "";
        });

    private async void OnLifeLights(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.AgentLights();
            StatusText.Text = string.Join(" \u00b7 ", outp.Order);
        });

    private async void OnLifeTopics(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.HelpTopics();
            StatusText.Text = outp.Topics.Length.ToString();
        });

    private async void OnLifeAsk(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.AskHelp(
                LifeQuestionBox.Text.Trim());
            LifeQuestionBox.Text = "";
            StatusText.Text = outp.Answer;
        });

    private async void OnLifeProviders(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.LocalProviders();
            StatusText.Text = outp.Length.ToString();
        });

    private async void OnLifeProvAdd(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.AddLocalProvider(
                LifeProvNameBox.Text.Trim(), LifeProvAreaBox.Text.Trim());
            LifeProvNameBox.Text = ""; LifeProvAreaBox.Text = "";
            StatusText.Text = outp.Name ?? outp.Id;
        });

    private async void OnBcnCard(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.BeaconCard(
                BcnIdBox.Text.Trim());
            StatusText.Text = outp.AgeWall == true
                ? (outp.Note ?? "18+")
                : (outp.DisplayName ?? "\u2014") + " \u00b7 "
                  + (outp.Watermark ?? "");
        });

    private async void OnBcnDesk(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.DeskScanCard(
                BcnIdBox.Text.Trim());
            StatusText.Text = outp.DisplayName ?? outp.DeskId ?? "";
        });

    private void OnBcnQr(object sender, RoutedEventArgs e) =>
        StatusText.Text =
            ApiClient.Shared.BeaconQrUrl(BcnIdBox.Text.Trim()) + " \u00b7 "
            + ApiClient.Shared.BeaconScanUrl(BcnIdBox.Text.Trim())
            + " \u00b7 " + ApiClient.Shared.DeskScanUrl(
                BcnIdBox.Text.Trim());

    private async void OnBcnSocial(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.SocialBeacon(
                BcnCidBox.Text.Trim());
            StatusText.Text = (outp.Platform ?? "\u2014") + " \u00b7 "
                + (outp.Handle ?? "") + " \u00b7 "
                + ApiClient.Shared.SocialQrUrl(BcnCidBox.Text.Trim());
        });

    private async void OnBcnPair(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Pairing();
            StatusText.Text = (outp.ConsoleUrl ?? "\u2014") + " \u00b7 "
                + ApiClient.Shared.PairQrUrl();
        });

    private async void OnModqShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.ModerationQueue(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = outp.Length.ToString();
        });

    private async void OnModqApprove(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.ApproveMessage(
                ModqMsgBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = outp.Status ?? "";
        });

    private async void OnModqReject(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.RejectMessage(
                ModqMsgBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = outp.Status ?? "";
        });

    private async void OnModqEdit(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.EditMessage(
                AppState.Current.Pid!, ModqMsgBox.Text.Trim(),
                ModqInteractorBox.Text.Trim(), ModqContentBox.Text.Trim(),
                AppState.Current.Token!);
            ModqContentBox.Text = "";
            StatusText.Text = outp.Status ?? "";
        });

    private async void OnModqRetract(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.RetractMessage(
                AppState.Current.Pid!, ModqMsgBox.Text.Trim(),
                ModqInteractorBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = outp.Status ?? "";
        });

    private async void OnRevwShow(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.ReviewsOf(
                AppState.Current.Pid!);
            StatusText.Text = outp.Reviews.Length + " \u00b7 "
                + (outp.Rating?.Average ?? 0);
        });

    private async void OnRevwLeave(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            int.TryParse(RevwRatingBox.Text.Trim(), out var rating);
            var outp = await ApiClient.Shared.LeaveReview(
                AppState.Current.Pid!, RevwInteractorBox.Text.Trim(),
                rating, RevwBodyBox.Text.Trim(), AppState.Current.Token!);
            RevwBodyBox.Text = "";
            StatusText.Text = (outp.Rating ?? 0).ToString();
        });

    private async void OnWmResolve(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.WatermarkCredentialOf(
                WmIdBox.Text.Trim());
            StatusText.Text = (outp.ProfileId ?? "\u2014") + " \u00b7 "
                + (outp.Kind ?? "");
        });

    private async void OnWmVerify(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.VerifyWatermark(
                WmIdBox.Text.Trim(), WmContentBox.Text.Trim());
            StatusText.Text = (outp.Valid == true ? "\u2713" : "\u2717")
                + " \u00b7 " + (outp.ContentMatches is null ? "\u2014"
                    : (outp.ContentMatches == true ? "\u2713" : "\u2717"));
        });

    private async void OnMedLimits(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.MediaLimits();
            StatusText.Text = string.Join(" \u00b7 ", new[] {
                ("image", outp.Image), ("video", outp.Video),
                ("file", outp.File),
            }.Where(p => p.Item2 is not null).Select(p =>
                $"{p.Item1} {(p.Item2!.MaxBytes ?? 0) / (1024 * 1024)}MB"));
        });

    private async void OnMedPlatforms(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.VideoPlatforms();
            StatusText.Text = string.Join(" \u00b7 ",
                outp.Platforms ?? Array.Empty<string>());
        });

    private async void OnMedUpload(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.UploadMedia(
                AppState.Current.Pid!, MedFilenameBox.Text.Trim(),
                System.Text.Encoding.UTF8.GetBytes("QRME"),
                AppState.Current.Token!);
            MedFilenameBox.Text = "";
            StatusText.Text = outp.Kind ?? outp.Id ?? "";
        });

    private async void OnWearList(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Wearables(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = outp.Wearables.Length + " \u00b7 "
                + string.Join(" \u00b7 ", (outp.KindsWorn ?? [])
                    .Select(k => $"{k.Key} {k.Value}"));
        });

    private async void OnWearPair(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.PairWearable(
                AppState.Current.Pid!, WearNameBox.Text.Trim(),
                WearKindBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = (outp.Name ?? "\u2014") + " \u00b7 "
                + (outp.Kind ?? "");
        });

    private async void OnWearUnpair(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.UnpairWearable(
                AppState.Current.Pid!, WearNameBox.Text.Trim(),
                AppState.Current.Token!);
            WearNameBox.Text = "";
            StatusText.Text = outp.Revoked == true ? "\u2713" : "\u2014";
        });

    private async void OnBornMake(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Genesis(
                BornOwnerBox.Text.Trim(), BornNameBox.Text.Trim(),
                BornSocialBox.Text.Trim(), BornHumorBox.Text.Trim(),
                BornMattersBox.Text.Trim(), BornComfortBox.Text.Trim());
            StatusText.Text = outp.DisplayName ?? outp.Id ?? "";
        });

    private async void OnBornBlend(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var sources = BornSourcesBox.Text.Split(',')
                .Select(x => x.Trim()).Where(x => x.Length > 0).ToArray();
            var outp = await ApiClient.Shared.Composite(
                BornOwnerBox.Text.Trim(), BornNameBox.Text.Trim(), sources);
            StatusText.Text = outp.DisplayName ?? outp.Id ?? "";
        });

    private async void OnBornPackPublish(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.PublishPack(
                BornPackIndustryBox.Text.Trim(),
                BornPackTitleBox.Text.Trim(), AppState.Current.Token!);
            BornPackTitleBox.Text = "";
            StatusText.Text = outp.Title ?? outp.Id ?? "";
        });

    private async void OnBornPackSeed(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.SeedPacks();
            StatusText.Text = (outp.Created ?? outp.Packs ?? 0).ToString();
        });

    private async void OnMindSimulate(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Simulate(
                AppState.Current.Pid!, MindScenarioBox.Text.Trim(),
                AppState.Current.Token!);
            MindScenarioBox.Text = "";
            StatusText.Text = outp.Narrative ?? outp.Id ?? "";
        });

    private async void OnMindRuns(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Simulations(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = outp.Length.ToString();
        });

    private async void OnMindTune(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Finetune(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = $"{outp.Interactors ?? 0} · "
                + $"{outp.MessagesProcessed ?? 0} · {outp.Computed}";
        });

    private async void OnMindCloud(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.CloudContribution(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = (outp.Enabled == true ? "on" : "off")
                + " \u00b7 " + (outp.Contributed?.Length ?? 0);
        });

    private async void OnMindRevoke(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.RevokeContributions(
                AppState.Current.Pid!, AppState.Current.Token!);
            StatusText.Text = (outp.RevokedCount ?? 0).ToString();
        });

    private async void OnMindExcursion(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Excursion(
                MindCidBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = (outp.Status ?? "\u2014") + " \u00b7 "
                + (outp.Findings ?? "");
        });

    private async void OnReachCheckin(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.ProactiveCheckin(
                AppState.Current.Pid!, AppState.Current.InteractorId!,
                AppState.Current.Token!);
            StatusText.Text = outp.Message ?? outp.Reason ?? "";
        });

    private async void OnReachRateUp(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.GiveFeedback(
                AppState.Current.Pid!, AppState.Current.InteractorId!,
                "up", AppState.Current.InteractorToken!);
            StatusText.Text = outp.Rating ?? "";
        });

    private async void OnReachRateDown(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.GiveFeedback(
                AppState.Current.Pid!, AppState.Current.InteractorId!,
                "down", AppState.Current.InteractorToken!);
            StatusText.Text = outp.Rating ?? "";
        });

    private async void OnReachQuietSet(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            int? start = int.TryParse(ReachQuietStartBox.Text.Trim(),
                out var a) ? a : null;
            int? end = int.TryParse(ReachQuietEndBox.Text.Trim(),
                out var b) ? b : null;
            var outp = await ApiClient.Shared.SetQuietHours(
                AppState.Current.InteractorId!, start, end,
                AppState.Current.InteractorToken!);
            StatusText.Text = (outp.QuietStart ?? -1) + "\u2013"
                + (outp.QuietEnd ?? -1);
        });

    private async void OnReachReferrals(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.MyReferrals(
                AppState.Current.InteractorId!,
                AppState.Current.InteractorToken!);
            StatusText.Text = outp.Length.ToString();
        });

    private async void OnLicAcquire(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.AcquireLicense(
                AppState.Current.Pid!, AppState.Current.InteractorToken!);
            LicGrantBox.Text = outp.Id ?? "";
            StatusText.Text = outp.Id ?? "";
        });

    private async void OnLicDerive(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.DeriveAgent(
                AppState.Current.Pid!, LicGrantBox.Text.Trim(),
                AppState.Current.InteractorToken!);
            StatusText.Text = outp.DisplayName ?? outp.Id ?? "";
        });

    private async void OnSensPerceive(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var objects = SensSceneBox.Text.Split(',')
                .Select(x => x.Trim()).Where(x => x.Length > 0).ToArray();
            var outp = await ApiClient.Shared.Perceive(
                AppState.Current.Pid!, objects, SensGoalBox.Text.Trim(),
                AppState.Current.Token!);
            SensSceneBox.Text = ""; SensGoalBox.Text = "";
            StatusText.Text = outp.Guidance ?? "";
        });

    private async void OnSensMics(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.MicrophonePlaces();
            StatusText.Text = string.Join(" \u00b7 ",
                (outp.Places ?? []).Select(x => x.Surface));
        });

    private async void OnSensVocab(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.MicrophoneVocabulary();
            StatusText.Text = string.Join(" · ",
                outp.Personal ?? Array.Empty<string>());
        });

    private async void OnSensOverlays(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.OverlaysCatalogue();
            StatusText.Text = (outp.Kinds?.Length ?? 0) + " \u00b7 "
                + (outp.Refusals?.Length ?? 0);
        });

    private async void OnSensHealth(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.Health();
            StatusText.Text = outp.Status ?? "ok";
        });

    private async void OnSensExpSet(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.SetExperience(
                AppState.Current.Pid!, SensExpBox.Text.Trim(),
                AppState.Current.Token!);
            SensExpBox.Text = "";
            StatusText.Text = outp.Experience.Length.ToString();
        });

    private async void OnSensCredRemove(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.RemoveSigningCredential(
                SensCredBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = outp.Removed == true ? "\u2713" : "\u2014";
        });

    private async void OnSensDeskJoin(object sender, RoutedEventArgs e) =>
        await Try(async () =>
        {
            var outp = await ApiClient.Shared.JoinDeskStream(
                SensCredBox.Text.Trim(), AppState.Current.Token!);
            StatusText.Text = outp.Mode ?? outp.Status ?? "";
        });
}
