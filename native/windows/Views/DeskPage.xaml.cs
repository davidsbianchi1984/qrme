using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;

namespace QrmeStudio.Views;

/// <summary>
/// A live desk: an actual person offering a service, waiting behind a camera
/// view of their own counter.
///
/// Deliberately the mirror image of a profile card. A synthetic profile always
/// carries the AI mark; this carries none, because stamping "AI" on a real
/// person tells the visitor the human they are waiting for does not exist.
/// Absence alone would be ambiguous, so the claim is made positively and the
/// attestation behind it is shown next to it.
///
/// And when the chair is empty there is a bell — the sign taped to the chair
/// says to ring it, so the button is here on the screen they are looking at.
/// </summary>
public sealed partial class DeskPage : Page
{
    private DeskCard? _desk;

    public DeskPage()
    {
        InitializeComponent();
        CounterHead.Text = L10n.T("desk.counter");
        CallerIdBox.Header = L10n.T("desk.counter.staff.caller");
        CallerTokenBox.Header = L10n.T("desk.counter.your_token");
        ShowSessionsButton.Content = L10n.T("desk.counter.show");
        StaffHead.Text = L10n.T("desk.counter.staff");
        DeskTokenBox.Header = L10n.T("desk.counter.staff.token");
        SessionCallerBox.Header = L10n.T("desk.counter.staff.caller");
        OpenSessionButton.Content = L10n.T("desk.counter.staff.open");
        OfferTargetBox.Header = L10n.T("desk.counter.staff.target");
        OfferScopeBox.Header = L10n.T("desk.counter.staff.scope");
        OfferButton.Content = L10n.T("desk.counter.staff.offer");
    }

    private async void OnOpen(object sender, RoutedEventArgs e)
    {
        var id = DeskIdBox.Text.Trim();
        if (id.Length == 0) return;
        try
        {
            _desk = await ApiClient.Shared.GetDesk(id);
            Render(_desk);
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { Fail(ex); }
    }

    private void Render(DeskCard d)
    {
        DeskImage.Source = new BitmapImage(new Uri(ApiClient.Shared.DeskViewUrl(d.DeskId)));
        LiveBadge.Text = d.Feed.Live ? "● LIVE" : "SAMPLE VIEW";
        FeedNote.Text = d.Feed.Live ? "" : d.Feed.Note;

        NameText.Text = d.DisplayName;
        TradeText.Text = d.Location is null ? d.Trade : $"{d.Trade} · {d.Location}";
        DesignationText.Text = $"✓ {d.Designation}";
        PresenceText.Text = d.Presence switch
        {
            "attended" => "At the desk",
            "closed" => "Closed — not taking callers",
            _ => "Away from the desk",
        };

        AttestorText.Text = $"Attested by {d.Attestation.Attestor}"
            + (d.Attestation.Signed ? " · signed" : "");
        BasisText.Text = d.Attestation.Basis;
        // Shipped with the claim, always: "recorded" and "proven" are
        // different words and the difference is the whole point.
        AttestNote.Text = d.Attestation.Note;

        ViewPanel.Visibility = Visibility.Visible;
        WhoPanel.Visibility = Visibility.Visible;
        AttestPanel.Visibility = Visibility.Visible;
        BellPanel.Visibility = d.Bell.Available ? Visibility.Visible : Visibility.Collapsed;
        RingResult.Visibility = Visibility.Collapsed;
    }

    private async void OnRing(object sender, RoutedEventArgs e)
    {
        if (_desk is null) return;
        RingButton.IsEnabled = false;
        try
        {
            var note = NoteBox.Text.Trim();
            var receipt = await ApiClient.Shared.RingBell(
                _desk.DeskId, note.Length == 0 ? null : note);
            RingResult.Text = receipt.Note;
            RingResult.Visibility = Visibility.Visible;
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { Fail(ex); }
        finally { RingButton.IsEnabled = true; }
    }


    private string? _openSessionId;

    /// <summary>The caller's own sessions: offers to answer, links to end.
    /// The link token appears only here — it is the caller's machine the
    /// link opens, so the secret is theirs to hand to their own tooling.</summary>
    private async void OnShowSessions(object sender, RoutedEventArgs e)
    {
        try
        {
            var sessions = await ApiClient.Shared.MyDeskSessions(
                CallerIdBox.Text.Trim(), CallerTokenBox.Text.Trim());
            SessionsPanel.Children.Clear();
            foreach (var session in sessions)
            {
                var line = new TextBlock
                {
                    Text = $"{session.DeskName ?? session.DeskId} · {session.Status}",
                    FontSize = 12,
                };
                SessionsPanel.Children.Add(line);
                foreach (var link in session.Connections)
                {
                    var row = new TextBlock
                    {
                        Text = $"  {link.Kind} · {link.Target} · {link.Status}"
                               + (link.Means is null ? "" : $" — {link.Means}")
                               + (link.Token is null ? "" : $" · {link.Token}"),
                        FontSize = 11,
                        TextWrapping = TextWrapping.Wrap,
                    };
                    SessionsPanel.Children.Add(row);
                    if (link.Status == "offered")
                    {
                        var yes = new Button { Content = L10n.T("desk.counter.connect"), FontSize = 11 };
                        var sid = session.Id; var cid = link.Id;
                        yes.Click += async (_, _) =>
                        {
                            try
                            {
                                var made = await ApiClient.Shared.AnswerDeskConnection(
                                    sid, cid, true, CallerTokenBox.Text.Trim());
                                CounterResult.Text = made.Token is null
                                    ? made.Status
                                    : $"Connected — link token (yours alone): {made.Token}";
                                CounterResult.Visibility = Visibility.Visible;
                                var refreshed = await ApiClient.Shared.DeskSession(
                                    sid, CallerTokenBox.Text.Trim());
                                _ = refreshed;
                            }
                            catch (Exception ex) { Fail(ex); }
                        };
                        SessionsPanel.Children.Add(yes);
                        var no = new Button { Content = L10n.T("desk.counter.decline"), FontSize = 11 };
                        no.Click += async (_, _) =>
                        {
                            try
                            {
                                await ApiClient.Shared.AnswerDeskConnection(
                                    sid, cid, false, CallerTokenBox.Text.Trim());
                            }
                            catch (Exception ex) { Fail(ex); }
                        };
                        SessionsPanel.Children.Add(no);
                    }
                    if (link.Status == "active")
                    {
                        var end = new Button { Content = L10n.T("desk.counter.end"), FontSize = 11 };
                        var sid = session.Id; var cid = link.Id;
                        end.Click += async (_, _) =>
                        {
                            try
                            {
                                await ApiClient.Shared.EndDeskConnection(
                                    sid, cid, CallerTokenBox.Text.Trim());
                            }
                            catch (Exception ex) { Fail(ex); }
                        };
                        SessionsPanel.Children.Add(end);
                    }
                }
                if (session.Status == "open")
                {
                    var close = new Button { Content = L10n.T("desk.counter.close_all"), FontSize = 11 };
                    var sid = session.Id;
                    close.Click += async (_, _) =>
                    {
                        try
                        {
                            await ApiClient.Shared.CloseDeskSession(
                                sid, CallerTokenBox.Text.Trim());
                        }
                        catch (Exception ex) { Fail(ex); }
                    };
                    SessionsPanel.Children.Add(close);
                }
            }
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { Fail(ex); }
    }

    /// <summary>The staffer's half: holding the desk token is what makes
    /// this caller the desk. The offer grants nothing; the accept does.</summary>
    private async void OnOpenSession(object sender, RoutedEventArgs e)
    {
        if (_desk is null) return;
        try
        {
            var session = await ApiClient.Shared.OpenDeskSession(
                _desk.DeskId, SessionCallerBox.Text.Trim(), DeskTokenBox.Text.Trim());
            _openSessionId = session.Id;
            var all = await ApiClient.Shared.DeskSessions(
                _desk.DeskId, DeskTokenBox.Text.Trim());
            CounterResult.Text = $"Session open · {all.Length} on this desk";
            CounterResult.Visibility = Visibility.Visible;
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { Fail(ex); }
    }

    private async void OnOffer(object sender, RoutedEventArgs e)
    {
        if (_openSessionId is null) return;
        try
        {
            var scope = OfferScopeBox.Text.Trim();
            var made = await ApiClient.Shared.OfferDeskConnection(
                _openSessionId, "screen_share", OfferTargetBox.Text.Trim(),
                scope.Length == 0 ? null : scope, DeskTokenBox.Text.Trim());
            CounterResult.Text = $"Offered ({made.Status}) — their yes is what opens it.";
            CounterResult.Visibility = Visibility.Visible;
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { Fail(ex); }
    }

    private void Fail(Exception ex)
    {
        ErrorText.Text = ex.Message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
