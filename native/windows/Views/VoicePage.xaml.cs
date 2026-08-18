using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using Windows.Media.Capture;
using Windows.Media.MediaProperties;
using Windows.Storage;

namespace QrmeStudio.Views;

/// <summary>
/// Voice enrollment, walked in the order FIG. 800 gates it: permission (802),
/// then collection (806/808), then the characteristics (810), then the print
/// (812) and what speaking with it always carries.
///
/// The desktop has a microphone too, so this page records the sample and
/// measures it rather than asking the owner to type how many seconds they
/// gathered. What crosses the wire is still only the measurement: the audio is
/// written to this app's temporary folder and the profile database is told its
/// name, never its bytes.
///
/// Turns are reported as one per recording. Unlike the phone shells, which read
/// the platform's level meter and count stretches of speech, nothing here
/// meters the input — and inventing a turn count from the duration would be a
/// number the app cannot stand behind. Several short recordings therefore
/// describe a conversation better than one long one, which the page says.
/// </summary>
public sealed partial class VoicePage : Page
{
    private MediaCapture? _capture;
    private LowLagMediaRecording? _recording;
    private StorageFile? _file;
    private readonly Stopwatch _clock = new();
    private readonly DispatcherTimer _ticker = new() { Interval = TimeSpan.FromMilliseconds(250) };
    private bool _busy;

    public VoicePage()
    {
        InitializeComponent();
        _ticker.Tick += (_, _) =>
            ElapsedText.Text = $"{_clock.Elapsed.TotalSeconds:F0}s";
        Localize();
    }

    /// Every visible string on this page, from the table. The consent copy
    /// said "stays on this machine" where the phones said "stays on this
    /// device" — the same promise about where a recording lives, worded twice.
    /// One row now, and this page says what they say.
    private void Localize()
    {
        var lang = AppState.Current.Language;
        Step1.Text = L10n.T("nvoi.step1", lang);
        Step2.Text = L10n.T("nvoi.step2", lang);
        Step3.Text = L10n.T("nvoi.step3", lang);
        GrantButton.Content = L10n.T("nvoi.attest", lang);
        TapNote.Text = L10n.T("nvoi.tap", lang);
        RecordButton.Content = L10n.T("nvoi.sample", lang);
        StaysNote.Text = L10n.T("nvoi.stays", lang);
        BuildButton.Content = L10n.T("nvoi.build", lang);
        SayBox.Header = L10n.T("nvoi.say", lang);
        SpeakButton.Content = L10n.T("nvoi.speak", lang);
        WithdrawButton.Content = L10n.T("nvoi.withdraw", lang);
        HoldsHead.Text = L10n.T("nvoi.holds", lang);
        HoldsOwn.Text = L10n.T("nvoi.holds.own", lang);
        HoldsMark.Text = L10n.T("nvoi.holds.mark", lang);
        HoldsWithdraw.Text = L10n.T("nvoi.holds.withdraw", lang);
        SpokenHead.Text = L10n.T("nsv.title", lang);
        SpokenLead.Text = L10n.T("nsv.lead", lang);
        BindIdBox.PlaceholderText = L10n.T("nsv.id.ph", lang);
        BindLabelBox.PlaceholderText = L10n.T("nsv.label.ph", lang);
        BindButton.Content = L10n.T("nsv.save", lang);
        SayButton.Content = L10n.T("nsv.test", lang);
        UnbindButton.Content = L10n.T("nsv.unbind", lang);
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) => await Load();

    // MARK: state

    private async Task Load()
    {
        var pid = AppState.Current.Pid;
        var token = AppState.Current.Token;
        // Returning here left the page as furniture: three cards of headings
        // over buttons that answered nothing, and no word about why. The
        // sentence for this state was in the table already, translated ten
        // ways, asked for by nobody.
        if (pid is null || token is null)
        {
            ShowError(L10n.T("nvoi.needprofile", AppState.Current.Language));
            GrantButton.IsEnabled = false;
            RecordButton.IsEnabled = false;
            BuildButton.IsEnabled = false;
            return;
        }
        try { Render(await ApiClient.Shared.Voiceprint(pid, token)); }
        catch (Exception ex) { ShowError(ex.Message); }
        // The spoken voice — a different thing from the voiceprint above,
        // which is why it does not sit behind the enrollment consent.
        try { RenderSpoken(await ApiClient.Shared.SpokenVoice(pid)); }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private void RenderSpoken(SpokenBinding b)
    {
        var lang = AppState.Current.Language;
        BindPanel.Visibility = b.Speaks ? Visibility.Collapsed : Visibility.Visible;
        BoundPanel.Visibility = b.Speaks ? Visibility.Visible : Visibility.Collapsed;
        if (b.Speaks)
            BoundText.Text = L10n.T("nsv.bound", lang) + " "
                + (b.Label is { Length: > 0 } ? b.Label : b.VoiceId);
    }

    private void Render(VoiceprintStatus s)
    {
        var consented = s.Consent.Granted;
        var lang = AppState.Current.Language;
        GrantButton.Visibility = consented ? Visibility.Collapsed : Visibility.Visible;
        WithdrawButton.Visibility = consented ? Visibility.Visible : Visibility.Collapsed;
        EnrollmentCard.Visibility = consented ? Visibility.Visible : Visibility.Collapsed;
        VoiceprintCard.Visibility = consented ? Visibility.Visible : Visibility.Collapsed;

        ConsentText.Text = consented
            ? L10n.Fill("nvoi.granted", lang,
                        ("sources", string.Join(", ", s.Consent.Sources ?? Array.Empty<string>())))
              + (s.Consent.GrantedAt is { Length: >= 10 } at ? $" · {at[..10]}" : "")
            : L10n.T("nvoi.nothing", lang);

        if (s.Enrollment is { } en)
        {
            CountsText.Text = L10n.Fill("nvoi.samples", lang,
                                        ("n", $"{en.Samples}"),
                                        ("secs", $"{en.Seconds:F1}s"))
                            + " — " + L10n.T(en.Ready ? "nvoi.ready" : "nvoi.notyet", lang);
            var turnLine = en.MeanTurnSeconds is { } mean
                ? $"about {mean:F1}s a turn"
                : "no turns counted yet";
            ThresholdText.Text = $"{turnLine} · needs {en.ReadyWhen.Samples} samples "
                               + $"and {en.ReadyWhen.Seconds:F0}s";
            NeedsText.Text = en.Needs.Length > 0
                ? L10n.Fill("nvoi.needs", lang,
                            ("needs", string.Join(", ", en.Needs))) : "";
            NeedsText.Visibility = !en.Ready && en.Needs.Length > 0
                ? Visibility.Visible : Visibility.Collapsed;
            MethodText.Text = en.Method;
            BuildButton.IsEnabled = en.Ready;
        }

        var active = s.Voiceprint is { Active: true };
        SpeakPanel.Visibility = active ? Visibility.Visible : Visibility.Collapsed;
        BuildButton.Visibility = active ? Visibility.Collapsed : Visibility.Visible;
        PrintText.Text = s.Voiceprint switch
        {
            { Active: true } p =>
                L10n.Fill("nvoi.built", lang,
                          ("date", p.BuiltAt is { Length: >= 10 } b ? b[..10] : "—"))
                + $" · {p.Id}",
            { Active: false } => L10n.T("nvoi.retired", lang),
            _ => s.Enrollment?.Ready == true
                ? L10n.T("nvoi.enough", lang)
                : L10n.T("nvoi.more", lang),
        };
        DisclosureText.Text = s.Disclosure;
    }

    // MARK: 802 — permission

    private async void OnGrant(object sender, RoutedEventArgs e) =>
        await Call(async (pid, token) => Render(await ApiClient.Shared.GrantVoiceConsent(
            pid, token, new[] { "call", "voice_note", "direct" })));

    private async void OnRevoke(object sender, RoutedEventArgs e) =>
        await Call(async (pid, token) =>
        {
            var r = await ApiClient.Shared.RevokeVoiceprint(pid, token);
            RevokedText.Text = L10n.Fill("nvoi.deleted", AppState.Current.Language,
                                         ("n", $"{r.SamplesDeleted}"),
                                         ("note", r.Note));
            RevokedText.Visibility = Visibility.Visible;
            await Load();
        });

    // MARK: 806/808 — a sample arrives

    private async void OnRecord(object sender, RoutedEventArgs e)
    {
        if (_recording is not null) { await StopRecording(); return; }
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            _capture = new MediaCapture();
            await _capture.InitializeAsync(new MediaCaptureInitializationSettings
            {
                StreamingCaptureMode = StreamingCaptureMode.Audio,
            });
            // Not ApplicationData.Current: this app is unpackaged, where that
            // property throws. Same LocalApplicationData root AppState uses.
            var dir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "QrmeStudio", "voice");
            Directory.CreateDirectory(dir);
            var folder = await StorageFolder.GetFolderFromPathAsync(dir);
            _file = await folder.CreateFileAsync(
                $"voice-{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}.m4a",
                CreationCollisionOption.GenerateUniqueName);
            _recording = await _capture.PrepareLowLagRecordToStorageFileAsync(
                MediaEncodingProfile.CreateM4a(AudioEncodingQuality.Medium), _file);
            await _recording.StartAsync();
            _clock.Restart();
            _ticker.Start();
            ElapsedText.Visibility = Visibility.Visible;
            RecordButton.Content = L10n.T("nvoi.stop");
        }
        catch (UnauthorizedAccessException)
        {
            await ReleaseCapture();
            ShowError("Microphone access is off for QRME — turn it on in "
                    + "Settings › Privacy & security › Microphone.");
        }
        catch (Exception ex)
        {
            await ReleaseCapture();
            ShowError($"Could not open the microphone: {ex.Message}");
        }
    }

    private async Task StopRecording()
    {
        _ticker.Stop();
        _clock.Stop();
        var seconds = Math.Round(_clock.Elapsed.TotalSeconds, 1);
        var reference = _file?.Name;
        await ReleaseCapture();
        RecordButton.Content = L10n.T("nvoi.sample");
        ElapsedText.Visibility = Visibility.Collapsed;
        if (seconds <= 0) return;
        await Call(async (pid, token) =>
        {
            await ApiClient.Shared.AddVoiceSample(pid, token, "direct", seconds,
                                                  turns: 1, reference: reference);
            await Load();
        });
    }

    /// Always let go of the device, even on the failure paths — a microphone
    /// left open is a worse outcome than a lost sample.
    private async Task ReleaseCapture()
    {
        try { if (_recording is not null) { await _recording.StopAsync(); await _recording.FinishAsync(); } }
        catch (Exception) { /* never started */ }
        _recording = null;
        _capture?.Dispose();
        _capture = null;
    }

    // MARK: 812 — the print

    private async void OnBuild(object sender, RoutedEventArgs e) =>
        await Call(async (pid, token) =>
            Render(await ApiClient.Shared.BuildVoiceprint(pid, token)));

    private async void OnSpeak(object sender, RoutedEventArgs e)
    {
        var text = SayBox.Text.Trim();
        if (text.Length == 0) return;
        await Call(async (pid, token) =>
        {
            var spoken = await ApiClient.Shared.SpeakInVoice(pid, token, text);
            BasisText.Text = spoken.Basis;
            SpokenDisclosure.Text = spoken.Disclosure;
        });
    }

    // MARK: plumbing

    // MARK: the spoken voice — the binding, and a line said aloud

    private async void OnBind(object sender, RoutedEventArgs e) =>
        await Call(async (pid, token) => RenderSpoken(
            await ApiClient.Shared.BindSpokenVoice(
                pid, token, BindIdBox.Text.Trim(), BindLabelBox.Text.Trim())));

    private async void OnUnbind(object sender, RoutedEventArgs e) =>
        await Call(async (pid, token) => RenderSpoken(
            await ApiClient.Shared.BindSpokenVoice(pid, token, "", "")));

    private async void OnSay(object sender, RoutedEventArgs e) =>
        await Call(async (pid, token) =>
        {
            var audio = await ApiClient.Shared.SaySpoken(
                pid, token, SayLineBox.Text);
            // Played from this app's temporary folder: the media player
            // reads files, and the utterance is not something to keep.
            var dir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "QrmeStudio", "voice");
            Directory.CreateDirectory(dir);
            var path = Path.Combine(dir,
                $"say-{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}.mp3");
            await File.WriteAllBytesAsync(path, audio);
            var player = new Windows.Media.Playback.MediaPlayer
            {
                Source = Windows.Media.Core.MediaSource.CreateFromUri(
                    new Uri(path)),
            };
            player.MediaEnded += (_, _) =>
            {
                player.Dispose();
                try { File.Delete(path); } catch { /* already gone */ }
            };
            player.Play();
        });

    private async Task Call(Func<string, string, Task> work)
    {
        var pid = AppState.Current.Pid;
        var token = AppState.Current.Token;
        if (pid is null || token is null || _busy) return;
        _busy = true;
        ErrorText.Visibility = Visibility.Collapsed;
        try { await work(pid, token); }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { _busy = false; }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
