using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class StudyPage : Page
{
    public sealed class ExcursionRow
    {
        public string Id { get; init; } = "";
        public string Topic { get; init; } = "";
        public string Badge { get; init; } = "";
        public string Redacted { get; init; } = "";
        public string Findings { get; init; } = "";
        public bool Learned { get; init; }
        public Visibility RedactedVisibility =>
            Redacted.Length > 0 ? Visibility.Visible : Visibility.Collapsed;
        public Visibility LearnedVisibility =>
            Learned ? Visibility.Visible : Visibility.Collapsed;
        public Visibility LearnVisibility =>
            Learned ? Visibility.Collapsed : Visibility.Visible;
        public string FoldedLabel => L10n.T("nstu.folded");
        public string FoldLabel => L10n.T("nstu.fold");
    }

    public StudyPage()
    {
        InitializeComponent();
        Localize();
    }

    private void Localize()
    {
        var lang = AppState.Current.Language;
        Title.Text = L10n.T("nstu", lang);
        Sub.Text = L10n.T("nstu.sub", lang);
        TopicBox.Header = L10n.T("ncmp.topic", lang);
        TopicBox.PlaceholderText = L10n.T("nstu.topic.ph", lang);
        QuestionBox.Header = L10n.T("nstu.question", lang);
        QuestionBox.PlaceholderText = L10n.T("nstu.question.ph", lang);
        StudyButton.Content = L10n.T("nstu.go", lang);
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) => await Reload();

    private async System.Threading.Tasks.Task Reload()
    {
        var s = AppState.Current;
        try
        {
            var excursions = await ApiClient.Shared.Excursions(s.Pid!, s.Token!);
            // Enumerable.Reverse by name: an array converts to Span<T>, so plain
            // .Reverse() binds to MemoryExtensions' in-place void overload.
            ExcursionsList.ItemsSource = Enumerable.Reverse(excursions)
                .Select(x => new ExcursionRow
            {
                Id = x.Id,
                Topic = x.Topic,
                Badge = L10n.T(x.LeftHost ? "nstu.lefthost" : "nstu.stayedlocal"),
                Redacted = x.Redactions > 0
                    ? L10n.Fill("nstu.redacted", AppState.Current.Language,
                                ("n", x.Redactions.ToString())) : "",
                Findings = x.Findings,
                Learned = x.Learned,
            }).ToList();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnStudy(object sender, RoutedEventArgs e)
    {
        var topic = TopicBox.Text.Trim();
        var question = QuestionBox.Text.Trim();
        if (topic.Length == 0 || question.Length == 0)
        {
            ShowError("Fill both a topic and a question.");
            return;
        }
        var s = AppState.Current;
        StudyButton.IsEnabled = false;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.StartExcursion(s.Pid!, s.Token!, topic, question);
            TopicBox.Text = ""; QuestionBox.Text = "";
            await Reload();
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { StudyButton.IsEnabled = true; }
    }

    private async void OnLearn(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string cid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.Learn(cid, s.Token!);
            await Reload();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }
}
