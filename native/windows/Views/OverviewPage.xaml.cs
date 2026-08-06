using System.Collections.Generic;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class OverviewPage : Page
{
    public record CardRow(string Label, string Value);

    public OverviewPage()
    {
        InitializeComponent();
        Localize();
    }

    private void Localize()
    {
        var lang = AppState.Current.Language;
        Sub.Text = L10n.T("nov.sub", lang);
        LiveText.Text = L10n.T("nov.live", lang);
        RefreshButton.Content = L10n.T("nov.refresh", lang);
        CardHead.Text = L10n.T("nov", lang);
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        RefreshButton.Content = L10n.T("action.refresh");
        await Load();
    }

    private async void OnRefresh(object sender, RoutedEventArgs e) => await Load();

    private async System.Threading.Tasks.Task Load()
    {
        var s = AppState.Current;
        Greeting.Text = s.DisplayName;
        try
        {
            var c = await ApiClient.Shared.Profile(s.Pid!);
            CardList.ItemsSource = new List<CardRow>
            {
                new("Kind", c.Kind.Replace('_', ' ')),
                new("Status", c.Status ?? "active"),
                new("ID", c.Id),
            };
        }
        catch
        {
            Empty.Text = "Couldn't load the card — is the backend running?";
            Empty.Visibility = Visibility.Visible;
        }
        finally
        {
            Loading.IsActive = false;
            Loading.Visibility = Visibility.Collapsed;
        }
    }
}
