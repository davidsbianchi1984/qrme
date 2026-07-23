using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace QrmeStudio.Views;

public sealed partial class ComposePage : Page
{
    public ComposePage() => InitializeComponent();

    private async void OnCompose(object sender, RoutedEventArgs e)
    {
        var topic = TopicBox.Text.Trim();
        if (topic.Length == 0) { ShowError("Enter a topic to compose about."); return; }

        var s = AppState.Current;
        SendButton.IsEnabled = false;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            var post = await ApiClient.Shared.Compose(s.Pid!, s.Token!, topic);
            StatusText.Text = Cap(post.Status ?? "draft");
            ContentText.Text = post.Content;
            ResultCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ShowError(ex.Message);
        }
        finally
        {
            SendButton.IsEnabled = true;
        }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];
}
