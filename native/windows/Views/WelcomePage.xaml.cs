using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace QrmeStudio.Views;

public sealed partial class WelcomePage : Page
{
    public WelcomePage() => InitializeComponent();

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
            var result = await ApiClient.Shared.CreateProfile(name, persona, kind, BirthBox.Text.Trim());
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
