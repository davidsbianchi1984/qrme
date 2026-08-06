using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace QrmeStudio.Views;

public sealed partial class WelcomePage : Page
{
    private LanguageInfo[] _languages = System.Array.Empty<LanguageInfo>();

    /// The API's members, in the order the picker shows them. The picker used
    /// to carry these as its visible text and `OnStart` read that text back —
    /// so a translated label would have been posted as the kind.
    private static readonly string[] _kinds = { "self", "other_person", "fictional" };

    /// This screen renders before a profile exists, so `AppState.Language` is
    /// the default rather than a setting anybody chose — and the picker below
    /// is where the profile's language gets chosen in the first place.
    /// `DeviceLanguage()` was added for `WithoutAnAccountPage`, whose reader is
    /// in exactly this position.
    private readonly string _lang = L10n.DeviceLanguage();

    public WelcomePage()
    {
        InitializeComponent();
        TitleText.Text = L10n.T("nw.title", _lang);
        SubText.Text = L10n.T("nw.sub", _lang);
        NameBox.Header = L10n.T("nw.name", _lang);
        NameBox.PlaceholderText = L10n.T("nw.name.ph", _lang);
        PersonaBox.Header = L10n.T("nw.persona", _lang);
        PersonaBox.PlaceholderText = L10n.T("nw.persona.ph", _lang);
        KindBox.Header = L10n.T("nw.kind", _lang);
        // The sentence is prose; the command is typed verbatim and is the
        // same in every language, so it goes in as a value.
        BackendHint.Text = L10n.Fill("nov.backend", _lang,
            ("command", "QRME_CORS_ORIGINS=* uvicorn qrme.api:app"));
        foreach (var kind in _kinds)
        {
            KindBox.Items.Add(new ComboBoxItem {
                Content = L10n.T(kind == "other_person" ? "nw.kind.other"
                                                        : $"nw.kind.{kind}", _lang) });
        }
        KindBox.SelectedIndex = 0;
        LanguageBox.Header = L10n.T("nw.language", _lang);
        BirthBox.Header = L10n.T("nw.birthdate", _lang);
        TermsText.Text = L10n.T("nw.terms", _lang);
        StartButton.Content = L10n.T("nw.create", _lang);
        InviteText.Text = L10n.T("pub.invite", _lang);
        DoorButton.Content = L10n.T("nw.door", _lang);
        NoAccountText.Text = L10n.T("pub.invite.none", _lang);
    }

    protected override async void OnNavigatedTo(Microsoft.UI.Xaml.Navigation.NavigationEventArgs e)
    {
        try
        {
            _languages = (await ApiClient.Shared.Languages()).Languages;
            LanguageBox.ItemsSource = System.Linq.Enumerable.ToList(
                System.Linq.Enumerable.Select(_languages, l => l.Label));
            LanguageBox.SelectedIndex = 0;   // English
        }
        catch { /* backend offline — create will surface the error */ }
    }

    private async void OnStart(object sender, RoutedEventArgs e)
    {
        var name = NameBox.Text.Trim();
        var persona = PersonaBox.Text.Trim();
        if (name.Length == 0 || persona.Length == 0)
        {
            ShowError("Enter a display name and a persona to continue.");
            return;
        }
        var kind = KindBox.SelectedIndex >= 0 && KindBox.SelectedIndex < _kinds.Length
            ? _kinds[KindBox.SelectedIndex] : "self";
        StartButton.IsEnabled = false;
        try
        {
            var language = LanguageBox.SelectedIndex >= 0
                           && LanguageBox.SelectedIndex < _languages.Length
                ? _languages[LanguageBox.SelectedIndex].Code
                : null;
            var result = await ApiClient.Shared.CreateProfile(
                name, persona, kind, BirthBox.Text.Trim(), language);
            AppState.Current.SignIn(result);
            Frame.Navigate(typeof(ShellPage));
        }
        catch (Exception ex)
        {
            ShowError(L10n.Fill("nw.unreachable", _lang, ("detail", ex.Message)));
            StartButton.IsEnabled = true;
        }
    }

    private void OnPublicDoor(object sender, RoutedEventArgs e) =>
        Frame.Navigate(typeof(WithoutAnAccountPage));

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
