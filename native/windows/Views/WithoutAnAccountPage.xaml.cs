using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace QrmeStudio.Views;

/// <summary>The two things this app lets a stranger do, on a page a stranger
/// can reach.
///
/// <para><c>MainWindow</c> navigates to <c>WelcomePage</c> unless
/// <c>AppState.Current.IsSignedIn</c>, and everything else lives inside
/// <c>ShellPage</c> behind it. So <c>OpenObjection</c> — added to
/// <c>SettingsPage</c> one release ago precisely because a person contesting
/// a profile has no console — sat inside the signed-in shell, past a profile
/// the objector does not have and should not have to make.</para>
///
/// <para>Its own summary in <c>ApiClient.cs</c> says as much: "This route
/// belongs to somebody who has found a synthetic profile of themselves, has
/// no QRME account, and therefore has no console." That was written beside a
/// call site requiring one.</para>
///
/// <para>Nothing here passes a token, and nothing here is the owner's half:
/// listing objections against your own profile and attesting to them stays in
/// Settings, where the credential is.</para></summary>
public sealed partial class WithoutAnAccountPage : Page
{
    public WithoutAnAccountPage() => InitializeComponent();

    private void OnBack(object sender, RoutedEventArgs e) =>
        Frame.Navigate(typeof(WelcomePage));

    private async void OnObject(object sender, RoutedEventArgs e)
    {
        var pid = ProfileBox.Text.Trim();
        var reference = RefBox.Text.Trim();
        if (pid.Length == 0 || reference.Length == 0)
        {
            ShowError("Enter the profile's id and your proof reference.");
            return;
        }
        ErrorText.Visibility = Visibility.Collapsed;
        ObjectButton.IsEnabled = false;
        try
        {
            var o = await ApiClient.Shared.OpenObjection(
                pid, reference, ReasonBox.Text.Trim());
            OpenedTitle.Text = $"Opened — {o.Id}";
            OpenedNote.Text = (o.Note ?? "")
                + (o.ProfileStatus is null
                    ? "" : $" The profile is {o.ProfileStatus} from this moment.");
            OpenedCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { ObjectButton.IsEnabled = true; }
    }

    private async void OnRecover(object sender, RoutedEventArgs e)
    {
        var content = ContentBox.Text.Trim();
        if (content.Length == 0) { ShowError("Paste the text first."); return; }
        ErrorText.Visibility = Visibility.Collapsed;
        RecoverButton.IsEnabled = false;
        try
        {
            var f = await ApiClient.Shared.RecoverWatermark(content);
            if (f.Recovered)
            {
                FoundTitle.Text = f.State ?? "recovered";
                FoundBody.Text = "Produced by a QRME synthetic profile.";
                FoundDetail.Text =
                    $"{f.MatchedWindows} of {f.StoredWindows} stored windows matched."
                    + (f.Verbatim ? "" : " The wording has changed since it was "
                        + "stamped — that does not make it less traceable, it is "
                        + "what the score is measuring.");
            }
            else
            {
                FoundTitle.Text = "Not recognised";
                FoundBody.Text = f.Reason ?? "";
                FoundDetail.Text = "This says nothing about whether a person wrote "
                    + "it. It says no profile on this deployment has stamped work "
                    + "sharing enough wording with it.";
            }
            FoundCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { RecoverButton.IsEnabled = true; }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
