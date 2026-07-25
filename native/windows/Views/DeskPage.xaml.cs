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

    public DeskPage() => InitializeComponent();

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

    private void Fail(Exception ex)
    {
        ErrorText.Text = ex.Message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
