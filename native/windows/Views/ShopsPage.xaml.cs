using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

/// <summary>
/// Shops: storefronts, not desks. No bell, no sessions, no connection
/// offers — that absence is the design. Buying signs with the interactor
/// identity this shell already holds; the till signs with the owner token.
/// Every visible string is set here from L10n so the English count behind
/// this shell's tabs does not grow.
/// </summary>
public sealed partial class ShopsPage : Page
{
    public record Row(string Line);

    public ShopsPage()
    {
        InitializeComponent();
        TitleText.Text = L10n.T("shop.title");
        LeadText.Text = L10n.T("shop.sub");
        BrowseShopId.Header = L10n.T("shop.browse_id");
        BrowseButton.Content = L10n.T("shop.browse");
        OrderOfferingId.Header = L10n.T("shop.offer_title");
        OrderButton.Content = L10n.T("shop.order");
        TillTitle.Text = L10n.T("shop.till");
        TillNote.Text = L10n.T("shop.till_note");
        ShopName.Header = L10n.T("shop.name");
        OpenButton.Content = L10n.T("shop.open");
        OfferTitle.Header = L10n.T("shop.offer_title");
        OfferPrice.Header = L10n.T("shop.price");
        AddButton.Content = L10n.T("shop.add");
        RetireOfferingId.Header = L10n.T("shop.offer_title");
        RetireButton.Content = L10n.T("shop.retire");
        AdvanceOrderId.Header = L10n.T("shop.book");
        AcceptButton.Content = L10n.T("shop.accept");
        FulfilButton.Content = L10n.T("shop.fulfil");
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        await LoadShops();
    }

    private string? _openShopId;
    private string? _myShopId;

    private async System.Threading.Tasks.Task LoadShops()
    {
        try
        {
            var shops = await ApiClient.Shared.ListShops();
            ShopList.ItemsSource = shops.Select(s => new Row(
                $"{s.Id} · {s.Name} · {s.Seller}" +
                (s.Tag is null ? "" : $" · {s.Tag}"))).ToList();
        }
        catch { /* leave as-is */ }
    }

    private async void OnBrowse(object sender, RoutedEventArgs e)
    {
        var id = BrowseShopId.Text.Trim();
        if (id.Length == 0) return;
        try
        {
            var shop = await ApiClient.Shared.ShopCard(id);
            _openShopId = shop.Id;
            OfferingList.ItemsSource = shop.Offerings.Select(o => new Row(
                $"{o.Id} · {o.Title} · {o.Kind} · {o.Price:F2} {o.Currency} · {o.Availability}"))
                .ToList();
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnOrder(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var offering = OrderOfferingId.Text.Trim();
        if (_openShopId is null || offering.Length == 0 ||
            s.InteractorId is null || s.InteractorToken is null) return;
        try
        {
            await ApiClient.Shared.PlaceShopOrder(_openShopId, offering,
                s.InteractorId, 1, s.InteractorToken);
            var mine = await ApiClient.Shared.MyShopOrders(s.InteractorId,
                                                           s.InteractorToken);
            MineText.Text = string.Join("\n", mine.Select(o =>
                $"{o.Title} · {o.Amount:F2} {o.Currency} · {o.Status}"));
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnOpenShop(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var name = ShopName.Text.Trim();
        if (name.Length == 0 || s.Pid is null || s.Token is null) return;
        try
        {
            var shop = await ApiClient.Shared.OpenShop(s.Pid, name, s.Token);
            _myShopId = shop.Id;
            await LoadBook();
            await LoadShops();
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async System.Threading.Tasks.Task LoadBook()
    {
        var s = AppState.Current;
        if (_myShopId is null || s.Token is null) return;
        var book = await ApiClient.Shared.ShopOrderBook(_myShopId, s.Token);
        BookList.ItemsSource = book.Select(o => new Row(
            $"{o.Id} · {o.Title} ×{o.Quantity} · {o.Amount:F2} {o.Currency} · {o.Status}"))
            .ToList();
    }

    private async void OnAddOffering(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var title = OfferTitle.Text.Trim();
        if (_myShopId is null || title.Length == 0 || s.Token is null) return;
        if (!double.TryParse(OfferPrice.Text.Trim(), out var price)) return;
        try
        {
            await ApiClient.Shared.AddShopOffering(_myShopId, "goods", title,
                                                   price, s.Token);
            OfferTitle.Text = ""; OfferPrice.Text = "";
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnRetire(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var offering = RetireOfferingId.Text.Trim();
        if (_myShopId is null || offering.Length == 0 || s.Token is null) return;
        try
        {
            await ApiClient.Shared.RetireShopOffering(_myShopId, offering,
                                                      s.Token);
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }

    private async void OnAccept(object sender, RoutedEventArgs e) =>
        await Advance("accepted");

    private async void OnFulfil(object sender, RoutedEventArgs e) =>
        await Advance("fulfilled");

    private async System.Threading.Tasks.Task Advance(string to)
    {
        var s = AppState.Current;
        var order = AdvanceOrderId.Text.Trim();
        if (_myShopId is null || order.Length == 0 || s.Token is null) return;
        try
        {
            await ApiClient.Shared.AdvanceShopOrder(_myShopId, order,
                                                    "seller", to, s.Token);
            await LoadBook();
            StatusText.Text = "";
        }
        catch (Exception ex) { StatusText.Text = ex.Message; }
    }
}
