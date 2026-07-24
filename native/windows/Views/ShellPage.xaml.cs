using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace QrmeStudio.Views;

public sealed partial class ShellPage : Page
{
    public ShellPage()
    {
        InitializeComponent();
        LocalizeNav();
        ContentFrame.Navigate(typeof(OverviewPage));
    }

    /// Nav labels follow the profile's chosen language (chrome localization);
    /// re-applied on every pane selection so a language change in Settings
    /// takes effect immediately.
    private void LocalizeNav()
    {
        foreach (var entry in Nav.MenuItems)
            if (entry is NavigationViewItem nvi && nvi.Tag is string tag)
                nvi.Content = L10n.T($"tab.{tag}");
    }

    private void OnSelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
    {
        LocalizeNav();
        if (args.SelectedItem is not NavigationViewItem item) return;
        switch (item.Tag as string)
        {
            case "overview": ContentFrame.Navigate(typeof(OverviewPage)); break;
            case "chat": ContentFrame.Navigate(typeof(ChatPage)); break;
            case "community": ContentFrame.Navigate(typeof(CommunityPage)); break;
            case "compose": ContentFrame.Navigate(typeof(ComposePage)); break;
            case "posts": ContentFrame.Navigate(typeof(PostsPage)); break;
            case "study": ContentFrame.Navigate(typeof(StudyPage)); break;
            case "connect": ContentFrame.Navigate(typeof(ConnectPage)); break;
            case "gaming": ContentFrame.Navigate(typeof(GamingPage)); break;
            case "robots": ContentFrame.Navigate(typeof(RobotsPage)); break;
            case "reach": ContentFrame.Navigate(typeof(ReachPage)); break;
            case "settings": ContentFrame.Navigate(typeof(SettingsPage)); break;
        }
    }

    private void OnSignOut(object sender, RoutedEventArgs e)
    {
        AppState.Current.SignOut();
        Frame.Navigate(typeof(WelcomePage));
    }
}
