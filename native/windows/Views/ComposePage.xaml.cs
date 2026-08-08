using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace QrmeStudio.Views;

public sealed partial class ComposePage : Page
{
    public ComposePage()
    {
        InitializeComponent();
        Localize();
    }

    private void Localize()
    {
        var lang = AppState.Current.Language;
        Title.Text = L10n.T("tab.compose", lang);
        Sub.Text = L10n.T("ncmp.sub", lang);
        TopicBox.Header = L10n.T("ncmp.topic", lang);
        TopicBox.PlaceholderText = L10n.T("ncmp.topic.ph", lang);
        SendButton.Content = L10n.T("ncmp", lang);
    }

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
            ContentText.Text = post.Content ?? "· held for review ·";
            if (post.Provenance is { } prov)
            {
                var lang = AppState.Current.Language;
                ContentText.Text += "\n\nⓘ " + L10n.Fill(
                    "nprv.generated", lang,
                    ("model", prov.GeneratedBy),
                    ("n", $"{prov.GroundedInInfo.SourceItems}"),
                    ("status", prov.Moderation.Status));
                if (prov.LicensedFrom is { } lf)
                    ContentText.Text += " · " + L10n.Fill("nprv.licensed", lang,
                                                          ("source", lf));
                ContentText.Text += "\n" + prov.Disclaimer;
            }
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
