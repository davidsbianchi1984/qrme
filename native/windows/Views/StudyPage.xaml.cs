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
    }

    public StudyPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e) => await Reload();

    private async System.Threading.Tasks.Task Reload()
    {
        var s = AppState.Current;
        try
        {
            var excursions = await ApiClient.Shared.Excursions(s.Pid!, s.Token!);
            ExcursionsList.ItemsSource = excursions.Reverse().Select(x => new ExcursionRow
            {
                Id = x.Id,
                Topic = x.Topic,
                Badge = x.LeftHost ? "left host" : "stayed local",
                Redacted = x.Redactions > 0
                    ? $"{x.Redactions} private term(s) redacted from the outbound brief" : "",
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
