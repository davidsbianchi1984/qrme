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
    public WithoutAnAccountPage()
    {
        InitializeComponent();
        // The one screen in this shell whose reader has no profile, so the
        // language comes from the machine rather than from a stored setting.
        var lang = L10n.DeviceLanguage();
        TimelineTitle.Text = L10n.T("obj.timeline.title", lang);
        TimelineButton.Content = L10n.T("obj.timeline.go", lang);

        // Every one of these used to be a XAML attribute, which is why this
        // shell's count was the largest of the nine: an attribute is written
        // once at parse time and cannot be re-read in another language. The
        // wording is the console's `pub.*` rows, ported rather than
        // translated a second time.
        TitleText.Text = L10n.T("pub.sub", lang);
        BackButton.Content = L10n.T("pub.back.short", lang);
        LeadText.Text = L10n.T("pub.invite", lang) + " "
                      + L10n.T("pub.invite.none", lang);
        ObjectHeading.Text = L10n.T("pub.object.title", lang);
        ObjectRestricts.Text = L10n.T("pub.object.restricts", lang);
        ProfileBox.Header = L10n.T("pub.object.profileId", lang);
        RefBox.Header = L10n.T("pub.object.ref", lang);
        RefBox.PlaceholderText = L10n.T("pub.object.ref.ph", lang);
        ReasonBox.Header = L10n.T("pub.object.reason", lang);
        RefNote.Text = L10n.T("pub.object.ref.note", lang);
        ObjectButton.Content = L10n.T("pub.object.open", lang);
        WriteItDown.Text = L10n.T("pub.object.writeitdown", lang);
        MarkHeading.Text = L10n.T("pub.mark.title", lang);
        MarkExplain.Text = L10n.T("pub.mark.explain", lang);
        ContentBox.PlaceholderText = L10n.T("pub.mark.paste", lang);
        RecoverButton.Content = L10n.T("pub.mark.ask", lang);
        CountHeading.Text = L10n.T("pub.count.title", lang);
        CountIdBox.PlaceholderText = L10n.T("pub.count.id", lang);
        CountButton.Content = L10n.T("pub.count.ask", lang);
        NoTokenText.Text = L10n.T("pub.notoken", lang);
    }

    /// <summary>This page's reader has no profile, so there is no profile
    /// language to read. Resolved on every use rather than cached, because
    /// the machine's language can change while the app is open.</summary>
    private static string Lang => L10n.DeviceLanguage();

    private void OnBack(object sender, RoutedEventArgs e) =>
        Frame.Navigate(typeof(WelcomePage));

    private async void OnObject(object sender, RoutedEventArgs e)
    {
        var pid = ProfileBox.Text.Trim();
        var reference = RefBox.Text.Trim();
        if (pid.Length == 0 || reference.Length == 0)
        {
            ShowError(L10n.T("pub.object.needid", Lang));
            return;
        }
        ErrorText.Visibility = Visibility.Collapsed;
        ObjectButton.IsEnabled = false;
        try
        {
            var o = await ApiClient.Shared.OpenObjection(
                pid, reference, ReasonBox.Text.Trim());
            OpenedTitle.Text = L10n.Fill("pub.object.opened", Lang, ("id", o.Id));
            OpenedNote.Text = (o.Note ?? "")
                + (o.ProfileStatus is null ? "" : " " + L10n.Fill(
                    "pub.object.opened.status", Lang,
                    ("now", L10n.T($"pub.state.{o.ProfileStatus}", Lang)),
                    ("before", L10n.T(
                        $"pub.state.{o.PriorStatus ?? "active"}", Lang))));
            OpenedCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { ObjectButton.IsEnabled = true; }
    }

    /// <summary>Read the record of a case you raised.
    ///
    /// <para>The objector could already end the profile from this page's
    /// sibling routes and could not read what had been done about it: the full
    /// audit is owner- or reviewer-gated because it quotes free text. This
    /// carries the shape of what happened and none of the words — including
    /// the objector's own, which is why the gate on the other view stands.</para></summary>
    private async void OnTimeline(object sender, RoutedEventArgs e)
    {
        var lang = L10n.DeviceLanguage();
        var id = TimelineIdBox.Text.Trim();
        if (id.Length == 0)
        {
            ShowError(L10n.T("obj.timeline.need_id", lang));
            return;
        }
        ErrorText.Visibility = Visibility.Collapsed;
        TimelineButton.IsEnabled = false;
        try
        {
            var t = await ApiClient.Shared.ObjectionTimeline(id);
            TimelineList.Children.Clear();
            if (t.Events.Length == 0)
            {
                TimelineList.Children.Add(new TextBlock
                {
                    Text = L10n.T("obj.timeline.empty", lang),
                    FontSize = 12,
                    TextWrapping = TextWrapping.Wrap,
                });
            }
            foreach (var ev in t.Events)
            {
                var line = L10n.T($"obj.event.{ev.Event}", lang)
                    + " · " + L10n.T($"obj.actor.{ev.Actor}", lang)
                    + " · " + ev.At
                    + (ev.Sealed ? " · " + L10n.T("obj.timeline.sealed", lang) : "");
                TimelineList.Children.Add(new TextBlock
                {
                    Text = line,
                    FontSize = 12,
                    TextWrapping = TextWrapping.Wrap,
                });
            }
            TimelineList.Visibility = Visibility.Visible;
            // The backend's own sentence, already in the reader's language:
            // it says the reasons are not repeated here and why.
            TimelineNote.Text = t.Note;
            TimelineNote.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { TimelineButton.IsEnabled = true; }
    }

    private async void OnRecover(object sender, RoutedEventArgs e)
    {
        var content = ContentBox.Text.Trim();
        if (content.Length == 0) { ShowError(L10n.T("pub.mark.needtext", Lang)); return; }
        ErrorText.Visibility = Visibility.Collapsed;
        RecoverButton.IsEnabled = false;
        try
        {
            var f = await ApiClient.Shared.RecoverWatermark(content);
            if (f.Recovered)
            {
                FoundTitle.Text = L10n.Fill("pub.mark.producedby", Lang,
                    ("state", f.State ?? ""));
                FoundBody.Text = L10n.Fill("pub.mark.windows", Lang,
                    ("matched", f.MatchedWindows.ToString()),
                    ("stored", f.StoredWindows.ToString()),
                    ("examined", f.ExaminedWindows.ToString()),
                    ("similarity", f.Similarity.ToString("0.00")));
                FoundDetail.Text = f.Verbatim
                    ? "" : L10n.T("pub.mark.altered", Lang);
            }
            else
            {
                FoundTitle.Text = L10n.T("pub.mark.unknown", Lang);
                FoundBody.Text = f.Reason ?? "";
                FoundDetail.Text = L10n.Fill("pub.mark.unknown.explain", Lang,
                    ("here", L10n.T("pub.mark.here", Lang)));
            }
            FoundCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { RecoverButton.IsEnabled = true; }
    }

    /// <summary>How many people is this thing talking to.
    ///
    /// Here rather than behind sign-in: making somebody get an account before
    /// they may learn the number is the same withholding with a form in front
    /// of it, and the withholding is the whole harm.</summary>
    private async void OnCount(object sender, RoutedEventArgs e)
    {
        var pid = CountIdBox.Text.Trim();
        if (pid.Length == 0) { ShowError(L10n.T("pub.count.id", Lang)); return; }
        ErrorText.Visibility = Visibility.Collapsed;
        CountButton.IsEnabled = false;
        try
        {
            var c = await ApiClient.Shared.ProfileAttention(pid);
            CountNumbers.Text = c.PeopleThisWeek + " \u00b7 "
                + L10n.T("pub.count.week", Lang) + "    " + c.PeopleEver
                + " \u00b7 " + L10n.T("pub.count.ever", Lang);
            CountSays.Text = c.Says;
            CountNote.Text = c.Note;
            CountCard.Visibility = Visibility.Visible;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { CountButton.IsEnabled = true; }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
