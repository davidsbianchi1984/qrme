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
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) => await Load();

    // MARK: state

    private async Task Load()
    {
        var pid = AppState.Current.Pid;
        var token = AppState.Current.Token;
        if (pid is null || token is null) return;
        try { Render(await ApiClient.Shared.Voiceprint(pid, token)); }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private void Render(VoiceprintStatus s)
    {
        var consented = s.Consent.Granted;
        GrantButton.Visibility = consented ? Visibility.Collapsed : Visibility.Visible;
        RevokeButton.Visibility = consented ? Visibility.Visible : Visibility.Collapsed;
        EnrollmentCard.Visibility = consented ? Visibility.Visible : Visibility.Collapsed;
        VoiceprintCard.Visibility = consented ? Visibility.Visible : Visibility.Collapsed;

        ConsentText.Text = consented
            ? $"Granted for {string.Join(", ", s.Consent.Sources ?? Array.Empty<string>())}"
              + (s.Consent.GrantedAt is { Length: >= 10 } at ? $" · {at[..10]}" : "")
            : "Nothing is recorded until you say so. QRME will only learn your own "
              + "voice — there is no path here for anybody else's.";

        if (s.Enrollment is { } en)
        {
            CountsText.Text = $"{en.Samples} sample(s) · {en.Seconds:F1}s — "
                            + (en.Ready ? "ready" : "not yet");
            var turnLine = en.MeanTurnSeconds is { } mean
                ? $"about {mean:F1}s a turn"
                : "no turns counted yet";
            ThresholdText.Text = $"{turnLine} · needs {en.Threshold.Samples} samples "
                               + $"and {en.Threshold.Seconds:F0}s";
            NeedsText.Text = en.Needs.Length > 0
                ? $"Still wants: {string.Join(", ", en.Needs)}." : "";
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
                $"Built {(p.BuiltAt is { Length: >= 10 } b ? b[..10] : "—")} · {p.Id}",
            { Active: false } =>
                "A previous voiceprint was retired when consent was withdrawn. "
                + "That record stays.",
            _ => s.Enrollment?.Ready == true
                ? "Enough of your voice is on record — mint the voiceprint."
                : "Record a few more samples first.",
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
            RevokedText.Text = $"{r.SamplesDeleted} sample(s) deleted. {r.Note}";
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
            RecordButton.Content = "Stop";
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
        RecordButton.Content = "Record a sample";
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
