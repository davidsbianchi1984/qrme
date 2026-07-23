using Microsoft.UI.Xaml;
using QrmeStudio.Views;

namespace QrmeStudio;

public sealed partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        Title = "QRME";
        RootFrame.Navigate(AppState.Current.IsSignedIn ? typeof(ShellPage) : typeof(WelcomePage));
    }
}
