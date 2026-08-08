using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

/// <summary>
/// Signing, and the read half of docs/signatures.md.
///
/// The ceremony runs in an embedded WebView2 rather than through
/// <c>webauthn.dll</c>. That interop is several hundred lines of
/// version-sensitive struct marshalling which a compile cannot meaningfully
/// check; Edge already speaks WebAuthn and already talks to Windows Hello, so
/// nothing here marshals anything by hand. The page it loads is served from
/// the deployment's own origin — WebAuthn refuses a mismatched relying party,
/// and an opaque origin has none to match.
///
/// The web page never sees a token. It posts the raw assertion back over the
/// WebView2 message channel and this class makes the authenticated call; a
/// bearer token in a query string ends up in logs and history.
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

    private string _pendingEnvelope = "";
    // Kept rather than parsed back out of the navigated URL: the enrol call
    // has to echo the exact challenge, and re-deriving it from a query string
    // is a decode bug waiting to happen.
    private string _pendingChallenge = "";
    private bool _wired;

    public SignaturesPage()
    {
        InitializeComponent();
        var lang = AppState.Current.Language;
        HelloHead.Text = L10n.T("nsig.hello", lang);
        CeremonyNote.Text = L10n.T("nsig.ceremony.win", lang);
        DocumentBox.Header = L10n.T("nsig.signing", lang);
        MeaningBox.Header = L10n.T("nsig.means", lang);
        // The default was the attestation itself, in English, sitting in the
        // box a person is agreeing with.
        MeaningBox.Text = L10n.T("nsig.attest", lang);
        EnrollButton.Content = L10n.T("nsig.register", lang);
        SignButton.Content = L10n.T("nsig.sign", lang);
        CredsHead.Text = L10n.T("nsig.creds.yours", lang);
        NoCredsNote.Text = L10n.T("nsig.none", lang);
        LookupHead.Text = L10n.T("nsig.lookup", lang);
        SignatureIdBox.Header = L10n.T("nsig.sigid", lang);
        FetchButton.Content = L10n.T("nsig.fetch", lang);
        VerifyHead.Text = L10n.T("nsig.verify.other", lang);
        EvidenceNote.Text = L10n.T("nsig.evidence.sub", lang);
        PackageBox.Header = L10n.T("nsig.evidence", lang);
        VerifyButton.Content = L10n.T("nsig.verify", lang);
    }

    /// <summary>
    /// Start one ceremony in the embedded browser and hand the result to
    /// <see cref="OnCeremonyMessage"/>.
    /// </summary>
    private async Task RunCeremony(string url)
    {
        await Ceremony.EnsureCoreWebView2Async();
        if (!_wired)
        {
            Ceremony.CoreWebView2.WebMessageReceived += OnCeremonyMessage;
            _wired = true;
        }
        Ceremony.Visibility = Visibility.Visible;
        Ceremony.CoreWebView2.Navigate(url);
    }

    private async void OnEnroll(object sender, RoutedEventArgs e)
    {
        var token = AppState.Current.Token;
        if (token is null) { Fail(new Exception("Create a profile first.")); return; }
        try
        {
            var options = await ApiClient.Shared.EnrollOptions("QRME owner", token);
            _pendingEnvelope = "";
            _pendingChallenge = options.Challenge;
            CeremonyStatus.Text = L10n.T("nsig.hello.prompt");
            await RunCeremony(ApiClient.Shared.CeremonyUrl(
                "enroll", options.Challenge, userId: options.User.Id,
                userName: options.User.Name,
                displayName: options.User.DisplayName));
        }
        catch (Exception ex) { Fail(ex); }
    }

    private async void OnSign(object sender, RoutedEventArgs e)
    {
        var token = AppState.Current.Token;
        if (token is null) { Fail(new Exception("Create a profile first.")); return; }
        var document = DocumentBox.Text.Trim();
        if (document.Length == 0) return;
        try
        {
            // `basic` is what a self-asserted credential can sign, and
            // self-asserted is all this page can enrol.
            var env = await ApiClient.Shared.RequestSignature(
                document, MeaningBox.Text.Trim(), "basic", token);
            _pendingEnvelope = env.EnvelopeId;
            CeremonyStatus.Text = L10n.T("nsig.hello.prompt");
            await RunCeremony(ApiClient.Shared.CeremonyUrl(
                "sign", env.Challenge, displayText: env.DisplayText,
                meaning: env.Meaning));
        }
        catch (Exception ex) { Fail(ex); }
    }

    private async void OnCeremonyMessage(object? sender,
        Microsoft.Web.WebView2.Core.CoreWebView2WebMessageReceivedEventArgs args)
    {
        var token = AppState.Current.Token;
        if (token is null) return;
        try
        {
            using var doc = JsonDocument.Parse(args.TryGetWebMessageAsString());
            var root = doc.RootElement;
            if (!root.GetProperty("ok").GetBoolean())
            {
                Fail(new Exception(root.GetProperty("error").GetString() ?? "refused"));
                return;
            }
            string S(string k) => root.GetProperty(k).GetString() ?? "";

            if (root.GetProperty("mode").GetString() == "enroll")
            {
                var cred = await ApiClient.Shared.EnrollCredential(
                    S("credential_id"), S("attestation_object"),
                    S("client_data_json"), _pendingChallenge,
                    "QRME owner", token);
                CeremonyStatus.Text = L10n.T("nsig.registered")
                    + " " + L10n.Fill("nsig.cansign", AppState.Current.Language,
                        ("levels", string.Join(", ", cred.CanSign.Select(
                            l => L10n.T($"nsig.level.{l}")))));
            }
            else
            {
                var pkg = await ApiClient.Shared.SubmitSignature(
                    _pendingEnvelope, S("credential_id"), S("signature"),
                    S("authenticator_data"), S("client_data_json"), token);
                CeremonyStatus.Text = pkg.Verification.Valid
                    ? $"Signed — {pkg.SignatureId} verifies."
                    : "Signed, but the package does not verify.";
            }
            Ceremony.Visibility = Visibility.Collapsed;
            ErrorText.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex) { Fail(ex); }
    }

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
            NoCredsNote.Visibility =
                creds.Count == 0 ? Visibility.Visible : Visibility.Collapsed;
            CredentialList.ItemsSource = creds.Select(c => new CredentialVm
            {
                Title = c.DisplayName ?? c.CredentialId,
                Proofing = L10n.Fill("nsig.proofing", AppState.Current.Language,
                    ("level", L10n.T($"nsig.level.{c.ProofingLevel}"))),
                // Surfaced rather than buried: a syncable passkey exists on
                // every device in the owner's cloud account, which is a weaker
                // claim that only they could have signed.
                Custody = c.DeviceBound
                    ? L10n.T("nsig.devicebound")
                    : L10n.T("nsig.syncable"),
                Tiers = L10n.Fill("nsig.cansign", AppState.Current.Language,
                    ("levels", string.Join(", ", c.CanSign.Select(
                        l => L10n.T($"nsig.level.{l}"))))),
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
        target.Text = L10n.T(valid ? "nsig.verifies" : "nsig.noverify");
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
