using Microsoft.UI.Xaml;

namespace QrmeStudio;

public partial class App : Application
{
    private Window? _window;

    /// <summary>
    /// The shell's window, for the WinRT pickers that need a handle.
    ///
    /// A file chooser on WinUI 3 has no implicit owner — <c>PickSingleFileAsync</c>
    /// throws rather than opening anything until <c>InitializeWithWindow</c>
    /// has been handed one. The window was private, so a page that wanted to
    /// let somebody choose a file had nothing to pass.
    /// </summary>
    public static Window? Window => (Current as App)?._window;

    public App()
    {
        InitializeComponent();
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        _window = new MainWindow();
        _window.Activate();
        // What the buffer is for. Not awaited: a diagnostic must never be the
        // reason a window is slow to appear, and Send returns an outcome
        // rather than throwing, so there is nothing here to handle. It answers
        // AwaitingNotice until somebody has been told and chosen.
        _ = Problems.Send();
    }
}
