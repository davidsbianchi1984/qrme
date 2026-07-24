using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace QrmeStudio.Views;

public sealed partial class WelcomePage : Page
{
    private LanguageInfo[] _languages = System.Array.Empty<LanguageInfo>();

    public WelcomePage() => InitializeComponent();

    protected override async void OnNavigatedTo(Microsoft.UI.Xaml.Navigation.NavigationEventArgs e)
    {
        try
        {
            _languages = (await ApiClient.Shared.Languages()).Languages;
            LanguageBox.ItemsSource = System.Linq.Enumerable.ToList(
                System.Linq.Enumerable.Select(_languages, l => l.Label));
            LanguageBox.SelectedIndex = 0;   // English
        }
        catch { /* backend offline — create will surface the error */ }
    }

    private async void OnStart(object sender, RoutedEventArgs e)
    {
        var name = NameBox.Text.Trim();
        var persona = PersonaBox.Text.Trim();
        if (name.Length == 0 || persona.Length == 0)
        {
            ShowError("Enter a display name and a persona to continue.");
            return;
        }
        var kind = (KindBox.SelectedItem as ComboBoxItem)?.Content as string ?? "self";
        StartButton.IsEnabled = false;
        try
        {
            var language = LanguageBox.SelectedIndex >= 0
                           && LanguageBox.SelectedIndex < _languages.Length
                ? _languages[LanguageBox.SelectedIndex].Code
                : null;
            var result = await ApiClient.Shared.CreateProfile(
                name, persona, kind, BirthBox.Text.Trim(), language);
            AppState.Current.SignIn(result);
            Frame.Navigate(typeof(ShellPage));
        }
        catch (Exception ex)
        {
            ShowError($"Couldn't reach QRME — is the backend running? ({ex.Message})");
            StartButton.IsEnabled = true;
        }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
