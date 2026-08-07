using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class ReachPage : Page
{
    public sealed class BeaconVm
    {
        public string Id { get; init; } = "";
        public string Label { get; init; } = "";
        public string Detail { get; init; } = "";
        public bool Active { get; init; }
        public Visibility ActiveVisibility =>
            Active ? Visibility.Visible : Visibility.Collapsed;
        public string PickUpLabel => L10n.T("nmg.beacon.pickup");
    }

    public sealed class CardVm
    {
        public string DisplayName { get; init; } = "";
        public string Meta { get; init; } = "";
    }

    public sealed class ListingVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Kind { get; init; } = "";
        public string Blurb { get; init; } = "";
        public string TagLine { get; init; } = "";
        public bool Mine { get; init; }
        public Visibility MineVisibility =>
            Mine ? Visibility.Visible : Visibility.Collapsed;
        public string RemoveLabel => L10n.T("nmg.remove");
    }

    public sealed class PackVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Blurb { get; init; } = "";
        public string Meta { get; init; } = "";
        public string PriceLabel { get; init; } = "";
        public string ActionLabel { get; init; } = "";
        public bool Installed { get; init; }
        public Visibility InstalledVisibility =>
            Installed ? Visibility.Visible : Visibility.Collapsed;
        public Visibility AvailableVisibility =>
            Installed ? Visibility.Collapsed : Visibility.Visible;
        public string InstalledLabel => L10n.T("nmg.packs.installed");
        public string RemoveLabel => L10n.T("nmg.remove");
    }

    public sealed class RegistryVm
    {
        public string Key { get; init; } = "";
        public string Name { get; init; } = "";
        public string Tagline { get; init; } = "";
        public string SyncState { get; init; } = "";
        public bool CanSync { get; init; }
        public string ActionLabel =>
            L10n.T(CanSync ? "nmg.packs.sync" : "nmg.packs.synced");
    }

    public sealed class GrantVm
    {
        public string Id { get; init; } = "";
        public string Title { get; init; } = "";
        public string Derived { get; init; } = "";
        public bool Revoked { get; init; }
        public Visibility RevokedVisibility =>
            Revoked ? Visibility.Visible : Visibility.Collapsed;
        public Visibility ActiveVisibility =>
            Revoked ? Visibility.Collapsed : Visibility.Visible;
        public string RevokedLabel => L10n.T("nmg.revoked");
        public string RevokeLabel => L10n.T("nmg.revoke");
    }

    private static readonly string[] Kinds = { "consult", "finetune", "clone" };

    // Quick-browse tags: the wellbeing starters first, then popular areas.
    private static readonly string[] QuickBrowseTags =
        { "mental-health", "mood", "relationships",
          "healthcare", "finance", "fitness", "food" };

    public ReachPage()
    {
        InitializeComponent();
        Localize();
    }

    /// Every visible word on this page, from the table. The same surface is
    /// called Manage on the phones and Reach here, and until this round the
    /// two of them disagreed about the packs paragraph as well as the name:
    /// Windows told a reader that provenance names the pack, that a robot task
    /// pack teaches a body new commandable tasks, and that free packs download
    /// while priced ones are bought — three facts the phones left out. One row
    /// now, the longer wording, on all three shells.
    private void Localize()
    {
        var lang = AppState.Current.Language;
        SummonPivot.Header = L10n.T("nmg.t.summon", lang);
        MarketPivot.Header = L10n.T("nmg.t.market", lang);
        PacksPivot.Header = L10n.T("nmg.t.packs", lang);
        LicensePivot.Header = L10n.T("nmg.t.license", lang);
        EarnPivot.Header = L10n.T("nmg.t.earn", lang);

        HandleHead.Text = L10n.T("nmg.handle", lang);
        HandleSub.Text = L10n.T("nmg.handle.sub", lang);
        HandleBox.PlaceholderText = L10n.T("nmg.handle.example", lang);
        ClaimButton.Content = L10n.T("nmg.claim", lang);
        BeaconsHead.Text = L10n.T("nmg.beacons", lang);
        BeaconsSub.Text = L10n.T("nmg.beacons.sub", lang);
        BeaconLabelBox.Header = L10n.T("nmg.h.label", lang);
        BeaconLabelBox.PlaceholderText = L10n.T("nmg.beacon.label.example", lang);
        BeaconLocationBox.Header = L10n.T("nmg.h.location", lang);
        PlaceBeaconButton.Content = L10n.T("nmg.beacon.place", lang);
        TrySummonHead.Text = L10n.T("nmg.trysummon", lang);
        RefBox.PlaceholderText = L10n.T("nmg.summon.ph", lang);
        SummonButton.Content = L10n.T("nmg.t.summon", lang);

        ListHead.Text = L10n.T("nmg.list", lang);
        ListSub.Text = L10n.T("nmg.list.sub", lang);
        TitleBox.Header = L10n.T("nmg.h.title", lang);
        BlurbBox.Header = L10n.T("nmg.h.blurb", lang);
        TagsBox.Header = L10n.T("nmg.h.tags", lang);
        CreateListingButton.Content = L10n.T("nmg.create", lang);
        WellbeingHead.Text = L10n.T("nmg.wellbeing.head", lang);
        WellbeingNote.Text = L10n.T("nmg.wellbeing", lang);
        FilterTagBox.PlaceholderText = L10n.T("nmg.filter.tag", lang);
        BrowseButton.Content = L10n.T("nmg.browse", lang);

        PacksHead.Text = L10n.T("nmg.packs", lang);
        PacksSub.Text = L10n.T("nmg.packs.sub", lang);
        PackIndustryBox.PlaceholderText = L10n.T("nmg.filter.industry", lang);
        BrowsePacksButton.Content = L10n.T("nmg.browse", lang);
        PackSourcesHead.Text = L10n.T("nmg.packs.sources", lang);
        PackSourcesSub.Text = L10n.T("nmg.packs.sources.sub", lang);

        LicenseHead.Text = L10n.T("nmg.license", lang);
        LicenseSub.Text = L10n.T("nmg.license.sub", lang);
        KindBox.Header = L10n.T("nmg.license.kind", lang);
        PriceBox.Header = L10n.T("nmg.h.price", lang);
        TermsBox.Header = L10n.T("nmg.h.terms", lang);
        SetOfferButton.Content = L10n.T("nmg.setoffer", lang);
        UnlistButton.Content = L10n.T("nmg.unlist", lang);

        EarningsHead.Text = L10n.T("nmg.earnings", lang);
        EarningsSub.Text = L10n.T("nmg.earnings.sub", lang);
        AccruedLabel.Text = L10n.T("nmg.accrued", lang);
        PaidLabel.Text = L10n.T("nmg.paid", lang);
        LifetimeLabel.Text = L10n.T("nmg.lifetime", lang);
        PayoutButton.Content = L10n.T("nmg.payout.request", lang);
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        KindBox.ItemsSource = Kinds.ToList();
        KindBox.SelectedIndex = 0;
        QuickTags.ItemsSource = QuickBrowseTags.Select(tag =>
        {
            var chip = new Button { Content = $"#{tag}", Tag = tag, FontSize = 12 };
            chip.Click += OnQuickTag;
            return chip;
        }).ToList();
        await ReloadBeacons();
        await ReloadListings();
        await ReloadPacks();
        await ReloadLicense();
        await ReloadEarnings();
    }

    // -- Earnings: the creator's statement over the ledger --

    public sealed class LedgerVm
    {
        public string Kind { get; init; } = "";
        public string Memo { get; init; } = "";
        public string Amount { get; init; } = "";
        public string Status { get; init; } = "";
    }

    private static string Money(double v, string c) =>
        (c == "USD" ? "$" : c + " ") + v.ToString("0.00");

    private async System.Threading.Tasks.Task ReloadEarnings()
    {
        var s = AppState.Current;
        try
        {
            var st = await ApiClient.Shared.Earnings(s.Pid!, s.Token!);
            AccruedText.Text = Money(st.Totals.Accrued, st.Currency);
            PaidText.Text = Money(st.Totals.Paid, st.Currency);
            LifetimeText.Text = Money(st.Totals.Lifetime, st.Currency);
            PayoutButton.IsEnabled = st.Totals.Accrued > 0;
            if (st.Totals.ByKind.Count > 0)
            {
                ByKindText.Text = string.Join(" · ", st.Totals.ByKind
                    .OrderBy(kv => kv.Key)
                    .Select(kv => $"{kv.Key.Replace('_', ' ')}: {Money(kv.Value, st.Currency)}"));
                ByKindText.Visibility = Visibility.Visible;
            }
            LedgerList.ItemsSource = st.Entries.Take(20).Select(e2 => new LedgerVm
            {
                Kind = e2.Kind.Replace('_', ' '),
                Memo = e2.Memo ?? "",
                Amount = Money(e2.Amount, st.Currency),
                Status = e2.Status,
            }).ToList();
        }
        catch (Exception ex)
        {
            EarningsError.Text = ex.Message;
            EarningsError.Visibility = Visibility.Visible;
        }
    }

    private async void OnRequestPayout(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var r = await ApiClient.Shared.RequestPayout(s.Pid!, s.Token!);
            PayoutText.Text = $"Payout {r.PayoutId}: {Money(r.Total, "USD")} across " +
                              $"{r.Entries} entries (simulated transfer).";
            PayoutText.Visibility = Visibility.Visible;
            await ReloadEarnings();
        }
        catch (Exception ex)
        {
            EarningsError.Text = ex.Message;
            EarningsError.Visibility = Visibility.Visible;
        }
    }

    // -- Knowledge packs --

    private System.Collections.Generic.Dictionary<string, Pack> _packsById = new();
    // pack id -> robot id ("" when installed on the profile itself)
    private System.Collections.Generic.Dictionary<string, string> _installedOn = new();

    private async System.Threading.Tasks.Task ReloadPacks()
    {
        var s = AppState.Current;
        try
        {
            RegistryList.ItemsSource = (await ApiClient.Shared.PackRegistries())
                .Select(r => new RegistryVm
                {
                    Key = r.Key,
                    Name = r.Name,
                    Tagline = r.Tagline,
                    SyncState = $"{r.Synced}/{r.Available} packs synced",
                    CanSync = r.Synced < r.Available,
                }).ToList();
            var catalog = await ApiClient.Shared.Packs(PackIndustryBox.Text.Trim());
            _installedOn = (await ApiClient.Shared.InstalledPacks(s.Pid!, s.Token!))
                .ToDictionary(p => p.Id, p => p.RobotId ?? "");
            _packsById = catalog.ToDictionary(p => p.Id);
            PackList.ItemsSource = catalog.Select(p => new PackVm
            {
                Id = p.Id,
                Title = p.Title,
                Blurb = p.Blurb ?? "",
                Meta = $"#{p.Industry} · {p.Items} items · {p.Installs} installs · {p.Publisher}"
                       + (p.OriginUrl is { } u ? $" · from {u}" : ""),
                // `nmg.pack.robot.tasks` rather than `nmg.pack.robot`: both
                // rows existed on both shells with different words — "ROBOT"
                // here, "ROBOT TASKS" on the iPhone — for the same badge on
                // the same kind of pack. One badge, one word, one key; the
                // short row is deleted rather than left translated ten ways
                // for nobody.
                PriceLabel = (p.Audience == "robot"
                              ? L10n.T("nmg.pack.robot.tasks") + " · " : "")
                             + (p.Free ? "FREE" : $"{p.Price:F2} {p.Currency}"),
                ActionLabel = p.Free
                    ? L10n.T("nmg.packs.download")
                    : L10n.Fill("nmg.packs.buy", AppState.Current.Language,
                                ("price", p.Price.ToString("F2")),
                                ("currency", p.Currency)),
                Installed = _installedOn.ContainsKey(p.Id),
            }).ToList();
            PackError.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            PackError.Text = ex.Message;
            PackError.Visibility = Visibility.Visible;
        }
    }

    private async void OnBrowsePacks(object sender, RoutedEventArgs e) =>
        await ReloadPacks();

    private async void OnSyncRegistry(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string key) return;
        try
        {
            await ApiClient.Shared.SyncRegistry(key);
            PackStatus.Text = L10n.T("nrch.src.synced");
            PackStatus.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            PackError.Text = ex.Message;
            PackError.Visibility = Visibility.Visible;
        }
        await ReloadPacks();
    }

    private async void OnInstallPack(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string packId) return;
        if (!_packsById.TryGetValue(packId, out var pack)) return;
        var s = AppState.Current;
        PackStatus.Visibility = Visibility.Collapsed;
        try
        {
            // Robot task packs install onto the profile's bound body.
            string? robotId = null;
            if (pack.Audience == "robot")
            {
                var robots = await ApiClient.Shared.Robots(s.Pid!, s.Token!);
                if (robots.Length == 0)
                {
                    PackError.Text = L10n.T("nrch.needbody");
                    PackError.Visibility = Visibility.Visible;
                    return;
                }
                robotId = robots[0].Id;
            }
            // Clicking the priced button is the accept_price consent.
            var r = await ApiClient.Shared.InstallPack(
                packId, s.Pid!, s.Token!, acceptPrice: !pack.Free, robotId: robotId);
            var what = pack.Audience == "robot"
                ? L10n.T("nmg.pack.commandable")
                : L10n.T("nmg.pack.grounding");
            PackStatus.Text = pack.Free
                ? $"downloaded — {r.Count} {what}"
                : $"bought for {r.PricePaid:F2} — {r.Count} {what}";
            PackStatus.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            PackError.Text = ex.Message;
            PackError.Visibility = Visibility.Visible;
        }
        await ReloadPacks();
    }

    private async void OnUninstallPack(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string packId) return;
        var s = AppState.Current;
        try
        {
            var robotId = _installedOn.GetValueOrDefault(packId, "");
            if (robotId.Length > 0)
            {
                await ApiClient.Shared.UninstallRobotPack(packId, robotId, s.Token!);
                PackStatus.Text = L10n.T("nrch.body.removed");
            }
            else
            {
                await ApiClient.Shared.UninstallPack(packId, s.Pid!, s.Token!);
                PackStatus.Text = L10n.T("nrch.kb.removed");
            }
            PackStatus.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            PackError.Text = ex.Message;
            PackError.Visibility = Visibility.Visible;
        }
        await ReloadPacks();
    }

    private async void OnQuickTag(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string tag) return;
        FilterTagBox.Text = tag;
        await ReloadListings();
    }

    // -- Summon --

    private async void OnClaim(object sender, RoutedEventArgs e)
    {
        var handle = HandleBox.Text.Trim();
        if (handle.Length == 0) return;
        var s = AppState.Current;
        SummonError.Visibility = Visibility.Collapsed;
        try
        {
            var r = await ApiClient.Shared.ClaimHandle(s.Pid!, handle,
                s.Token ?? "");
            ClaimedText.Text = $"claimed {r.Handle}";
            ClaimedText.Visibility = Visibility.Visible;
            HandleBox.Text = "";
        }
        catch (Exception ex) { ShowSummonError(ex.Message); }
    }

    private async System.Threading.Tasks.Task ReloadBeacons()
    {
        var s = AppState.Current;
        try
        {
            var beacons = await ApiClient.Shared.Beacons(s.Pid!);
            BeaconList.ItemsSource = beacons.Select(b => new BeaconVm
            {
                Id = b.Id,
                Label = b.Label,
                // "scan(s)" and "picked up" were English string literals
                // here while `nmg.beacon.scans` and `nmg.beacon.pickedup` sat
                // translated into ten languages in this shell's own table,
                // asked for by nothing. An owner reading the app in German
                // was shown "Garten · 3 scan(s) · picked up" — translated
                // chrome around the two words carrying the meaning.
                Detail = $"{b.Location ?? "—"} · "
                         + L10n.Fill("nmg.beacon.scans", s.Language,
                                     ("n", b.Scans.ToString()))
                         + (b.Active ? "" : " · " + L10n.T("nmg.beacon.pickedup")),
                Active = b.Active,
            }).ToList();
        }
        catch (Exception ex) { ShowSummonError(ex.Message); }
    }

    private async void OnPlaceBeacon(object sender, RoutedEventArgs e)
    {
        var label = BeaconLabelBox.Text.Trim();
        if (label.Length == 0) return;
        var s = AppState.Current;
        SummonError.Visibility = Visibility.Collapsed;
        try
        {
            var placed = await ApiClient.Shared.PlaceBeacon(
                s.Pid!, label, BeaconLocationBox.Text.Trim());
            QrText.Text = $"QR: {placed.QrSvg} · {placed.SummonUrl}";
            QrText.Visibility = Visibility.Visible;
            BeaconLabelBox.Text = "";
            BeaconLocationBox.Text = "";
            await ReloadBeacons();
        }
        catch (Exception ex) { ShowSummonError(ex.Message); }
    }

    private async void OnPickUp(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string bid) return;
        try
        {
            await ApiClient.Shared.PickUpBeacon(bid);
            await ReloadBeacons();
        }
        catch (Exception ex) { ShowSummonError(ex.Message); }
    }

    private async void OnSummon(object sender, RoutedEventArgs e)
    {
        var reference = RefBox.Text.Trim();
        if (reference.Length == 0) return;
        SummonError.Visibility = Visibility.Collapsed;
        BeaconMeta.Visibility = Visibility.Collapsed;
        try
        {
            var r = await ApiClient.Shared.Summon(reference);
            var cards = r.Profile is not null
                ? new[] { r.Profile }
                : r.Profiles ?? Array.Empty<SummonCard>();
            SummonList.ItemsSource = cards.Select(c => new CardVm
            {
                DisplayName = c.DisplayName,
                Meta = string.Join(" · ", new[] { c.Handle, c.Status, c.Note }
                    .Where(x => !string.IsNullOrEmpty(x))!),
            }).ToList();
            if (r.Type == "beacon")
            {
                BeaconMeta.Text = $"beacon \"{r.Label}\" · {r.Scans ?? 0} scan(s)";
                BeaconMeta.Visibility = Visibility.Visible;
            }
        }
        catch (Exception ex) { ShowSummonError(ex.Message); }
    }

    // -- Market --

    private async System.Threading.Tasks.Task ReloadListings()
    {
        var s = AppState.Current;
        try
        {
            var listings = await ApiClient.Shared.Listings(FilterTagBox.Text.Trim());
            ListingList.ItemsSource = listings.Select(l => new ListingVm
            {
                Id = l.Id,
                Title = l.Title,
                Kind = l.Kind,
                Blurb = l.Blurb ?? "",
                TagLine = string.Join(" ", l.Tags.Select(t => $"#{t}")),
                Mine = l.ProfileId == s.Pid,
            }).ToList();
        }
        catch (Exception ex) { ShowMarketError(ex.Message); }
    }

    private async void OnCreateListing(object sender, RoutedEventArgs e)
    {
        var title = TitleBox.Text.Trim();
        if (title.Length == 0) return;
        var s = AppState.Current;
        MarketError.Visibility = Visibility.Collapsed;
        try
        {
            var tags = TagsBox.Text.Split(',', StringSplitOptions.RemoveEmptyEntries)
                .Select(t => t.Trim()).Where(t => t.Length > 0).ToArray();
            await ApiClient.Shared.CreateListing(
                title, BlurbBox.Text.Trim(), tags, s.DisplayName, s.Pid!);
            MarketStatus.Text = L10n.T("nrch.listed");
            MarketStatus.Visibility = Visibility.Visible;
            TitleBox.Text = ""; BlurbBox.Text = ""; TagsBox.Text = "";
            await ReloadListings();
        }
        catch (Exception ex) { ShowMarketError(ex.Message); }
    }

    private async void OnBrowse(object sender, RoutedEventArgs e) =>
        await ReloadListings();

    private async void OnRemoveListing(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string lid) return;
        try
        {
            await ApiClient.Shared.RemoveListing(lid);
            await ReloadListings();
        }
        catch (Exception ex) { ShowMarketError(ex.Message); }
    }

    // -- License --

    private async System.Threading.Tasks.Task ReloadLicense()
    {
        var s = AppState.Current;
        try
        {
            var offer = await ApiClient.Shared.License(s.Pid!);
            ShowOffer(offer);
        }
        catch { OfferText.Visibility = Visibility.Collapsed; UnlistButton.Visibility = Visibility.Collapsed; }
        try
        {
            var grants = await ApiClient.Shared.LicenseGrants(s.Pid!, s.Token!);
            GrantList.ItemsSource = grants.Select(g => new GrantVm
            {
                Id = g.Id,
                Title = $"{g.Kind} → {g.BuyerId}",
                Derived = g.DerivedProfileId is { } d ? $"derived agent: {d}" : "",
                Revoked = g.Revoked,
            }).ToList();
        }
        catch (Exception ex) { ShowLicenseError(ex.Message); }
    }

    private void ShowOffer(LicenseOffer offer)
    {
        OfferText.Text = $"offered: {offer.Kind} · {offer.Currency} {offer.Price:0.00}" +
                         (offer.AllowDerivatives ? " · derivatives allowed" : "");
        OfferText.Visibility = Visibility.Visible;
        UnlistButton.Visibility = Visibility.Visible;
    }

    private async void OnSetLicense(object sender, RoutedEventArgs e)
    {
        if (KindBox.SelectedItem is not string kind) return;
        var s = AppState.Current;
        LicenseError.Visibility = Visibility.Collapsed;
        try
        {
            double.TryParse(PriceBox.Text.Trim(), out var price);
            var offer = await ApiClient.Shared.SetLicense(
                s.Pid!, s.Token!, kind, price, TermsBox.Text.Trim());
            ShowOffer(offer);
        }
        catch (Exception ex) { ShowLicenseError(ex.Message); }
    }

    private async void OnUnlist(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.UnlistLicense(s.Pid!, s.Token!);
            OfferText.Visibility = Visibility.Collapsed;
            UnlistButton.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { ShowLicenseError(ex.Message); }
    }

    private async void OnRevokeGrant(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string gid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.RevokeLicense(gid, s.Token!);
            await ReloadLicense();
        }
        catch (Exception ex) { ShowLicenseError(ex.Message); }
    }

    // -- helpers --

    private void ShowSummonError(string message)
    {
        SummonError.Text = message;
        SummonError.Visibility = Visibility.Visible;
    }

    private void ShowMarketError(string message)
    {
        MarketError.Text = message;
        MarketError.Visibility = Visibility.Visible;
    }

    private void ShowLicenseError(string message)
    {
        LicenseError.Text = message;
        LicenseError.Visibility = Visibility.Visible;
    }
}
