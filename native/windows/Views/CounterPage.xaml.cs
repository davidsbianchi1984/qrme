using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

/// <summary>
/// Standing behind the counter — the half of trade no shell had.
///
/// The caller's side shipped long ago: ring a bell, join a stream, open a
/// session. What never reached a phone or a desktop was the other side of
/// the same counter — open a desk, staff it, decide who comes through,
/// print its sticker. The market could be listed on and not searched,
/// priced, sold or bought in. Exchanges — two parties, one manifest —
/// existed on no client but the console.
///
/// Every visible string comes from L10n; the server's refusals arrive
/// already in the reader's language and are shown verbatim.
/// </summary>
public sealed partial class CounterPage : Page
{
    public record Row(string Line);

    private bool _loading;

    /// The three presences the backend accepts, offered as the closed set
    /// it is — a free field would earn the refusal on every typo.
    private static readonly string[] Presences =
        { "attended", "away", "closed" };

    public CounterPage()
    {
        InitializeComponent();
        TitleText.Text = L10n.T("counter.open");
        AttestedText.Text = L10n.T("counter.attested");
        DeskNameBox.Header = L10n.T("counter.name");
        TradeBox.Header = L10n.T("counter.trade");
        AttestorBox.Header = L10n.T("counter.attestor");
        BasisBox.Header = L10n.T("counter.basis");
        WhereBox.Header = L10n.T("counter.where");
        DeskBlurbBox.Header = L10n.T("counter.blurb");
        OpenDeskButton.Content = L10n.T("counter.open.go");
        DeskIdBox.Header = L10n.T("counter.desk_id");
        DeskTokenBox.Header = L10n.T("counter.desk_token");
        PresencePicker.Header = L10n.T("counter.mine");
        PresencePicker.ItemsSource = Presences
            .Select(PresenceLabel).ToList();
        PresencePicker.SelectedIndex = 0;
        PresenceButton.Content = L10n.T("counter.mine");
        CameraButton.Content = L10n.T("counter.camera");
        PortraitButton.Content = L10n.T("counter.portrait");
        ViewButton.Content = L10n.T("counter.bell");
        RingIdBox.Header = L10n.T("counter.bell");
        AckButton.Content = L10n.T("counter.ack");
        GuestIdBox.Header = L10n.T("counter.guests");
        AcceptGuestButton.Content = L10n.T("counter.accept");
        DeclineGuestButton.Content = L10n.T("counter.decline");
        StickerTitle.Text = L10n.T("counter.sticker");
        StickerNote.Text = L10n.T("counter.sticker.note");
        StickerLabelBox.Header = L10n.T("counter.sticker.label");
        MakeStickerButton.Content = L10n.T("counter.sticker.make");
        BeaconIdBox.Header = L10n.T("counter.sticker");
        ShowQrButton.Content = L10n.T("counter.sticker");
        DropStickerButton.Content = L10n.T("counter.sticker.drop");
        WalkupTitle.Text = L10n.T("counter.walkup");
        KnockNoteBox.Header = L10n.T("counter.knock.note");
        KnockButton.Content = L10n.T("counter.knock");
        LeaveButton.Content = L10n.T("counter.leave");
        FindTitle.Text = L10n.T("trade.find");
        QueryBox.Header = L10n.T("trade.query");
        SearchButton.Content = L10n.T("trade.search");
        NeedBox.Header = L10n.T("trade.need");
        AssistButton.Content = L10n.T("trade.assist");
        SeedButton.Content = L10n.T("trade.seed");
        StandTitle.Text = L10n.T("trade.stand");
        StandBlurbBox.Header = L10n.T("trade.blurb");
        LocalityBox.Header = L10n.T("trade.locality");
        TagsBox.Header = L10n.T("trade.tags");
        ListMeButton.Content = L10n.T("trade.list");
        UnlistMeButton.Content = L10n.T("trade.unlist");
        PriceTitle.Text = L10n.T("trade.price");
        ListingIdBox.Header = L10n.T("trade.listing");
        AmountBox.Header = L10n.T("trade.amount");
        AcceptBox.Header = L10n.T("trade.accept");
        SetOfferButton.Content = L10n.T("trade.set");
        ShowOfferButton.Content = L10n.T("trade.show");
        ClearOfferButton.Content = L10n.T("trade.clear");
        VenueBox.Header = L10n.T("trade.venue");
        PlaceButton.Content = L10n.T("trade.place");
        UnplaceButton.Content = L10n.T("trade.unplace");
        PullButton.Content = L10n.T("trade.pull");
        BuyButton.Content = L10n.T("trade.buy");
        ShowOffersSwitch.Header = L10n.T("trade.show_offers");
        DealsTitle.Text = L10n.T("deals.propose");
        GuestPartyBox.Header = L10n.T("deals.guest");
        WorkBox.Header = L10n.T("deals.work");
        FeeBox.Header = L10n.T("deals.fee");
        ProposeButton.Content = L10n.T("deals.propose.go");
        ExchangeIdBox.Header = L10n.T("deals.id");
        ItemNameBox.Header = L10n.T("deals.item");
        AddItemButton.Content = L10n.T("deals.add");
        ItemIdBox.Header = L10n.T("deals.manifest");
        TakeItemButton.Content = L10n.T("deals.take");
        DropItemButton.Content = L10n.T("deals.drop");
        SignButton.Content = L10n.T("deals.sign.go");
        ReopenButton.Content = L10n.T("deals.reopen");
        WithdrawButton.Content = L10n.T("deals.withdraw");
        ChannelButton.Content = L10n.T("deals.channel");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) =>
        await Load();

    private async System.Threading.Tasks.Task Load()
    {
        var s = AppState.Current;
        _loading = true;
        try
        {
            DeskList.ItemsSource = (await ApiClient.Shared.Desks())
                .Select(d => new Row($"{d.Id} · {d.DisplayName} · {d.Presence}"))
                .ToList();
            MarketList.ItemsSource = (await ApiClient.Shared.Marketplace())
                .Select(m => new Row($"{m.ProfileId} · {m.DisplayName}"))
                .ToList();
            LocalitiesText.Text = string.Join(" · ",
                await ApiClient.Shared.MarketLocalities());
            var vocab = await ApiClient.Shared.ExchangeVocabulary();
            RulesText.Text = string.Join(" · ", vocab.Rules);
        }
        catch { /* leave as-is */ }

        var deskId = DeskIdBox.Text.Trim();
        var deskToken = DeskTokenBox.Text.Trim();
        if (deskId.Length > 0)
        {
            try
            {
                var overlay = await ApiClient.Shared.DeskOverlay(deskId);
                var live = await ApiClient.Shared.DeskLivePerson(deskId);
                WaitingText.Text = $"{L10n.T("counter.waiting")} {overlay.Waiting}"
                    + (live.OwnerId is null ? "" : $" · {live.OwnerId}");
            }
            catch { /* leave as-is */ }
        }
        if (deskId.Length > 0 && deskToken.Length > 0)
        {
            try
            {
                RingList.ItemsSource = (await ApiClient.Shared
                    .DeskRings(deskId, deskToken))
                    .Select(r => new Row($"{r.Id} · {r.Note ?? ""}")).ToList();
                GuestList.ItemsSource = (await ApiClient.Shared
                    .DeskGuests(deskId, deskToken))
                    .Select(g => new Row(
                        $"{g.Id} · {g.DisplayName ?? g.GuestId} · {g.Status}"))
                    .ToList();
                BeaconList.ItemsSource = (await ApiClient.Shared
                    .DeskBeacons(deskId, deskToken))
                    .Select(b => new Row($"{b.Id} · {b.Label ?? ""}")).ToList();
            }
            catch { /* leave as-is */ }
        }
        if (s.Token is not null)
        {
            try
            {
                SalesList.ItemsSource = (await ApiClient.Shared
                    .MarketSales(s.Token))
                    .Select(x => new Row($"{x.Id} · {x.Status ?? ""}")).ToList();
                if (s.InteractorId is not null)
                {
                    var settings = await ApiClient.Shared.MarketSettings(
                        s.InteractorId, s.Token);
                    ShowOffersSwitch.IsOn = settings.ShowOffers ?? true;
                }
                if (s.Pid is not null)
                {
                    DealList.ItemsSource = (await ApiClient.Shared
                        .MyExchanges(s.Pid, s.Token))
                        .Select(d => new Row(
                            $"{d.Id} · {d.Work ?? ""} · {d.State}")).ToList();
                }
            }
            catch { /* leave as-is */ }
        }
        _loading = false;
    }

    private async System.Threading.Tasks.Task Act(
        Func<System.Threading.Tasks.Task> op)
    {
        try { await op(); StatusText.Text = ""; await Load(); }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private string Desk => DeskIdBox.Text.Trim();
    private string DeskToken => DeskTokenBox.Text.Trim();
    private string Listing => ListingIdBox.Text.Trim();
    private string Deal => ExchangeIdBox.Text.Trim();

    // -- the counter --

    /// Literal keys rather than the prefix plus the API value: a key
    /// built at runtime is a key the dead-key guard cannot see being
    /// asked for.
    private static string PresenceLabel(string state) => state switch
    {
        "attended" => L10n.T("counter.presence.attended"),
        "away" => L10n.T("counter.presence.away"),
        _ => L10n.T("counter.presence.closed"),
    };

    private async void OnOpenDesk(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        await Act(async () =>
        {
            var made = await ApiClient.Shared.OpenDesk(s.Pid!,
                DeskNameBox.Text.Trim(), TradeBox.Text.Trim(),
                AttestorBox.Text.Trim(), BasisBox.Text.Trim(),
                WhereBox.Text.Trim(), DeskBlurbBox.Text.Trim(), s.Token!);
            DeskIdBox.Text = made.DeskId;
            DeskTokenBox.Text = made.DeskToken ?? "";
        });
    }

    private async void OnSetPresence(object sender, RoutedEventArgs e)
    {
        var presence = Presences[Math.Max(0, PresencePicker.SelectedIndex)];
        await Act(() => ApiClient.Shared.SetDeskPresence(Desk, presence,
                                                         DeskToken));
    }

    private async void OnCamera(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.SetDeskCamera(Desk, true, DeskToken));

    private async void OnPortrait(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.SetDeskPortrait(Desk, DeskToken));

    private async void OnDeskView(object sender, RoutedEventArgs e)
    {
        try
        {
            var bytes = await ApiClient.Shared.DeskView(Desk);
            StatusText.Text = $"{bytes.Length}";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnAck(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.AckDeskRing(Desk,
            RingIdBox.Text.Trim(), DeskToken));

    private async void OnAcceptGuest(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.AcceptDeskGuest(Desk,
            GuestIdBox.Text.Trim(), DeskToken));

    private async void OnDeclineGuest(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.DeclineDeskGuest(Desk,
            GuestIdBox.Text.Trim(), DeskToken));

    private async void OnMakeSticker(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.AddDeskBeacon(Desk,
            StickerLabelBox.Text.Trim(), DeskToken));

    private async void OnShowQr(object sender, RoutedEventArgs e)
    {
        try
        {
            var bytes = await ApiClient.Shared.DeskBeaconQr(
                BeaconIdBox.Text.Trim());
            StatusText.Text = $"{bytes.Length}";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnDropSticker(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.RemoveDeskBeacon(
            BeaconIdBox.Text.Trim(), DeskToken));

    private async void OnKnock(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.AskToJoinDesk(Desk,
            KnockNoteBox.Text.Trim(), AppState.Current.InteractorToken ?? ""));

    private async void OnLeave(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.LeaveDesk(Desk,
            AppState.Current.InteractorToken ?? ""));

    // -- the market --

    private async void OnSearch(object sender, RoutedEventArgs e)
    {
        try
        {
            var box = await ApiClient.Shared.MarketSearch(
                QueryBox.Text.Trim());
            MarketList.ItemsSource = box.Results
                .Select(h => new Row($"{h.Id} · {h.Title}")).ToList();
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnAssist(object sender, RoutedEventArgs e)
    {
        try
        {
            var box = await ApiClient.Shared.MarketAssist(NeedBox.Text.Trim());
            StatusText.Text = string.Join(" · ", box.Suggestions);
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnSeed(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.SeedMarketplace());

    private async void OnListMe(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        await Act(() => ApiClient.Shared.ListInMarketplace(s.Pid!,
            StandBlurbBox.Text.Trim(), LocalityBox.Text.Trim(),
            TagsBox.Text.Split(',').Select(t => t.Trim())
                .Where(t => t.Length > 0).ToArray(), s.Token!));
    }

    private async void OnUnlistMe(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.UnlistFromMarketplace(
            AppState.Current.Pid!, AppState.Current.Token!));

    private async void OnSetOffer(object sender, RoutedEventArgs e)
    {
        double.TryParse(AmountBox.Text, out var amount);
        double? accept = double.TryParse(AcceptBox.Text, out var a)
            ? a : null;
        await Act(() => ApiClient.Shared.SetListingOffer(Listing, amount,
            accept, AppState.Current.Token!));
    }

    private async void OnShowOffer(object sender, RoutedEventArgs e)
    {
        try
        {
            var offer = await ApiClient.Shared.ListingOffer(Listing);
            StatusText.Text = $"{L10n.T("trade.asking")} {offer.Amount}";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnClearOffer(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.ClearListingOffer(Listing,
            AppState.Current.Token!));

    private async void OnPlace(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.PlaceListing(Listing,
            VenueBox.Text.Trim(), AppState.Current.Token!));

    private async void OnUnplace(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.UnplaceListing(Listing,
            AppState.Current.Token!));

    private async void OnPull(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.RemoveMarketListing(Listing,
            AppState.Current.Token!));

    private async void OnBuy(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.PurchaseListing(Listing,
            AppState.Current.InteractorToken ?? ""));

    private async void OnShowOffersToggled(object sender, RoutedEventArgs e)
    {
        if (_loading) return;
        var s = AppState.Current;
        await Act(() => ApiClient.Shared.SetMarketSettings(
            s.InteractorId ?? "", ShowOffersSwitch.IsOn, s.Token!));
    }

    // -- the deals --

    private async void OnPropose(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        double.TryParse(FeeBox.Text, out var fee);
        await Act(async () =>
        {
            var made = await ApiClient.Shared.ProposeExchange(s.Pid!,
                GuestPartyBox.Text.Trim(), WorkBox.Text.Trim(), "software",
                fee, s.Token!);
            ExchangeIdBox.Text = made.Id;
        });
    }

    private async void OnAddItem(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.AddExchangeItem(Deal,
            "host_to_guest", ItemNameBox.Text.Trim(), "source",
            AppState.Current.Token!));

    private async void OnTakeItem(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.AcceptExchangeItem(Deal,
            ItemIdBox.Text.Trim(), AppState.Current.Token!));

    private async void OnDropItem(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.RemoveExchangeItem(Deal,
            ItemIdBox.Text.Trim(), AppState.Current.Token!));

    private async void OnSign(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.SignExchange(Deal,
            AppState.Current.Pid!, AppState.Current.Token!));

    private async void OnReopen(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.ReopenExchange(Deal,
            AppState.Current.Pid!, AppState.Current.Token!));

    private async void OnWithdraw(object sender, RoutedEventArgs e) =>
        await Act(() => ApiClient.Shared.WithdrawFromExchange(Deal,
            AppState.Current.Pid!, AppState.Current.Token!));

    private async void OnChannel(object sender, RoutedEventArgs e)
    {
        try
        {
            var channel = await ApiClient.Shared.ExchangeChannel(Deal,
                AppState.Current.Token!);
            StatusText.Text = channel.RoomId ?? "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnExchangeLoad(object sender, RoutedEventArgs e) =>
        await Act(async () =>
        {
            var deal = await ApiClient.Shared.Exchange(Deal,
                AppState.Current.Token!);
            DealList.ItemsSource = (deal.Items ?? Array.Empty<ExchangeItemRow>())
                .Select(i => new Row($"{i.Id} · {i.Name} · {i.Kind}"))
                .ToList();
        });
}
