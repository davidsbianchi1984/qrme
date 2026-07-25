using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

/// <summary>
/// The read half of docs/signatures.md: what has been signed, whether it still
/// verifies, and what the scheme does not claim.
///
/// This page does not sign. A signature has to come from a platform
/// authenticator, and reaching Windows Hello as one means webauthn.dll interop
/// — a large block of struct marshalling that cannot be exercised here. A
/// button that looks like it signs and does not is worse than no button, so
/// the page says where signing happens instead of pretending to offer it.
///
/// Verification is a different matter and belongs on a desktop: it needs no
/// authenticator, and reading someone else's evidence package is exactly the
/// thing a person does at a keyboard.
/// </summary>
public sealed partial class SignaturesPage : Page
{
    public sealed class CredentialVm
    {
        public string Title { get; init; } = "";
        public string Proofing { get; init; } = "";
        public string Custody { get; init; } = "";
        public string Tiers { get; init; } = "";
    }

    public SignaturesPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        try
        {
            var policy = await ApiClient.Shared.GetSignaturePolicy();
            StandardText.Text = policy.Standard;
        }
        catch (Exception ex) { Fail(ex); }

        var token = AppState.Current.Token;
        if (token is null) return;
        try
        {
            var creds = await ApiClient.Shared.ListSigningCredentials(token);
            CredentialsEmpty.Visibility =
                creds.Count == 0 ? Visibility.Visible : Visibility.Collapsed;
            CredentialList.ItemsSource = creds.Select(c => new CredentialVm
            {
                Title = c.DisplayName ?? c.CredentialId,
                Proofing = $"verified at enrolment: {c.ProofingLevel}",
                // Surfaced rather than buried: a syncable passkey exists on
                // every device in the owner's cloud account, which is a weaker
                // claim that only they could have signed.
                Custody = c.DeviceBound
                    ? "device-bound — cannot sync"
                    : "syncable — exists on their other devices",
                Tiers = $"can sign: {string.Join(", ", c.CanSign)}",
            }).ToList();
        }
        catch (Exception ex) { Fail(ex); }
    }

    private async void OnFetch(object sender, RoutedEventArgs e)
    {
        var id = SignatureIdBox.Text.Trim();
        if (id.Length == 0) return;
        try
        {
            var pkg = await ApiClient.Shared.GetSignature(id);
            Verdict(VerdictText, pkg.Verification.Valid);
            MeaningText.Text = pkg.Meaning is null ? "" : $"Meaning: {pkg.Meaning}";
            // What the signer was shown, verbatim. WebAuthn cannot attest to
            // it, so the recorded text is the closest thing to reproducing the
            // screen — which is the point of storing it at all.
            ShownText.Text = pkg.DisplayText is null
                ? "" : $"What was shown: {pkg.DisplayText}";
            var where = pkg.Platform is null ? "" : $" on {pkg.Platform}";
            var how = pkg.Transport is null ? "" : $" ({pkg.Transport})";
            DetailText.Text = string.Join("\n", new List<string>
            {
                $"{pkg.Signer.Name ?? "unnamed"} · {pkg.Signer.ProofingLevel} · {pkg.Tier} tier",
                $"signed {pkg.SignedAt}{where}{how}",
                $"document sha256 {pkg.DocumentSha256}",
            }.Concat(pkg.Verification.Notes.Select(n => $"note: {n}"))
             .Concat(pkg.Limits.Select(l => $"• {l}")));
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { Fail(ex); }
    }

    private async void OnVerifyPackage(object sender, RoutedEventArgs e)
    {
        var raw = PackageBox.Text.Trim();
        if (raw.Length == 0) return;
        try
        {
            using var doc = JsonDocument.Parse(raw);
            var result = await ApiClient.Shared.VerifySignature(doc.RootElement.Clone());
            Verdict(PackageVerdict, result.Valid);
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (JsonException)
        {
            Fail(new Exception("That is not valid JSON — paste the whole package."));
        }
        catch (Exception ex) { Fail(ex); }
    }

    private void Verdict(TextBlock target, bool valid)
    {
        target.Text = valid ? "Verifies" : "Does not verify";
        target.Foreground = (SolidColorBrush)Application.Current.Resources[
            valid ? "QrmeGreenBrush" : "QrmeRedBrush"];
        target.Visibility = Visibility.Visible;
    }

    private void Fail(Exception ex)
    {
        ErrorText.Text = ex.Message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
