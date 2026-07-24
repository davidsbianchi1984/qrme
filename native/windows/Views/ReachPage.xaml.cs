using System;
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
    }

    private static readonly string[] Kinds = { "consult", "finetune", "clone" };

    // Quick-browse tags: the wellbeing starters first, then popular areas.
    private static readonly string[] QuickBrowseTags =
        { "mental-health", "mood", "relationships",
          "healthcare", "finance", "fitness", "food" };

    public ReachPage() => InitializeComponent();

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
            var catalog = await ApiClient.Shared.Packs(PackIndustryBox.Text.Trim());
            _installedOn = (await ApiClient.Shared.InstalledPacks(s.Pid!, s.Token!))
                .ToDictionary(p => p.Id, p => p.RobotId ?? "");
            _packsById = catalog.ToDictionary(p => p.Id);
            PackList.ItemsSource = catalog.Select(p => new PackVm
            {
                Id = p.Id,
                Title = p.Title,
                Blurb = p.Blurb ?? "",
                Meta = $"#{p.Industry} · {p.Items} items · {p.Installs} installs · {p.Publisher}",
                PriceLabel = (p.Audience == "robot" ? "🤖 ROBOT · " : "")
                             + (p.Free ? "FREE" : $"{p.Price:F2} {p.Currency}"),
                ActionLabel = p.Free ? "Download" : $"Buy {p.Price:F2} {p.Currency}",
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
                    PackError.Text = "bind a robot first (Robots page) — task packs install onto a body";
                    PackError.Visibility = Visibility.Visible;
                    return;
                }
                robotId = robots[0].Id;
            }
            // Clicking the priced button is the accept_price consent.
            var r = await ApiClient.Shared.InstallPack(
                packId, s.Pid!, s.Token!, acceptPrice: !pack.Free, robotId: robotId);
            var what = pack.Audience == "robot"
                ? "tasks the body can now be commanded with"
                : "items now grounding this profile";
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
                PackStatus.Text = "removed — the body's tasks were revoked";
            }
            else
            {
                await ApiClient.Shared.UninstallPack(packId, s.Pid!, s.Token!);
                PackStatus.Text = "removed — the knowledge base shrank back";
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
            var r = await ApiClient.Shared.ClaimHandle(s.Pid!, handle);
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
                Detail = $"{b.Location ?? "—"} · {b.Scans} scan(s)" +
                         (b.Active ? "" : " · picked up"),
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
            MarketStatus.Text = "listed — summonable by tag";
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
