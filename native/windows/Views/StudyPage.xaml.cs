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

    /// <summary>One of the owner's own questions. <c>Brief</c> is what went on
    /// the board — the typed question is deliberately not shown here, because
    /// the line worth checking is the line that left.</summary>
    public sealed class AskRow
    {
        public string Id { get; init; } = "";
        public string Brief { get; init; } = "";
        public string Count { get; init; } = "";
        public string AnswersText { get; init; } = "";
        public string FoldTag { get; init; } = "";
        public bool Closed { get; init; }
        public Visibility AnswersVisibility =>
            AnswersText.Length > 0 ? Visibility.Visible : Visibility.Collapsed;
        public Visibility CloseVisibility =>
            Closed ? Visibility.Collapsed : Visibility.Visible;
        public Visibility FoldVisibility =>
            FoldTag.Length > 0 ? Visibility.Visible : Visibility.Collapsed;
        public string ReadLabel => L10n.T("nask.read");
        public string CloseLabel => L10n.T("nask.close");
        public string FoldLabel => L10n.T("nstu.fold");
    }

    /// <summary>A question on the open board. No owner, no redaction count —
    /// see <c>OpenQuestion</c>.</summary>
    public sealed class BoardRow
    {
        public string Id { get; init; } = "";
        public string Brief { get; init; } = "";
        public string AnswersText { get; init; } = "";
        public Visibility AnswersVisibility =>
            AnswersText.Length > 0 ? Visibility.Visible : Visibility.Collapsed;
        public string ReadLabel => L10n.T("nask.send");
    }

    /// <summary>One far host this profile keeps returning to. The count is
    /// the answer; a list of individual visits would be the movement log this
    /// card exists to warn about.</summary>
    public sealed class BeenRow
    {
        public string Host { get; init; } = "";
        public string Times { get; init; } = "";
        public string Note { get; init; } = "";
        public bool StoodDown { get; init; }
        public Visibility NoteVisibility =>
            Note.Length > 0 ? Visibility.Visible : Visibility.Collapsed;
        public string ActionLabel =>
            StoodDown ? L10n.T("rem.been.resume") : L10n.T("rem.been.stop");
    }

    private string _openedAsk = "";
    private string _answeringId = "";

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
        WebHead.Text = L10n.T("nws.title");
        WebQBox.PlaceholderText = L10n.T("nws.ph");
        WebGoButton.Content = L10n.T("nws.title");
        AskTitle.Text = L10n.T("nask", lang);
        AskSub.Text = L10n.T("nask.sub", lang);
        AskTopicBox.Header = L10n.T("ncmp.topic", lang);
        AskTopicBox.PlaceholderText = L10n.T("nstu.topic.ph", lang);
        AskQuestionBox.Header = L10n.T("nstu.question", lang);
        AskQuestionBox.PlaceholderText = L10n.T("nask.q.ph", lang);
        AskButton.Content = L10n.T("nask.go", lang);
        BoardTitle.Text = L10n.T("nask.board", lang);
        BoardSub.Text = L10n.T("nask.board.sub", lang);
        AnswerText.Header = L10n.T("nask.your", lang);
        AnswerText.PlaceholderText = L10n.T("nask.your.ph", lang);
        AliasBox.Header = L10n.T("nask.alias", lang);
        AliasBox.PlaceholderText = L10n.T("nask.alias.ph", lang);
        PointsBox.Header = L10n.T("nask.points", lang);
        PointsBox.PlaceholderText = L10n.T("nask.points.ph", lang);
        SendAnswerButton.Content = L10n.T("nask.send", lang);
        BeenTitle.Text = L10n.T("rem.been", lang);
        BeenSub.Text = L10n.T("rem.been.pitch", lang);
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e) => await Reload();

    public sealed class WebRow
    {
        public string Title { get; init; } = "";
        public string Note { get; init; } = "";
        public Uri? Uri { get; init; }
    }

    private async void OnWebSearch(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        var q = WebQBox.Text.Trim();
        if (s.Pid is null || s.Token is null || q.Length == 0) return;
        try
        {
            var found = await ApiClient.Shared.WebSearch(s.Pid, s.Token, q);
            WebNoneText.Text = L10n.T("nws.none");
            WebNoneText.Visibility = found.Pages.Length == 0
                ? Visibility.Visible : Visibility.Collapsed;
            WebList.ItemsSource = found.Pages.Select(r => new WebRow
            {
                Title = r.Title.Length > 0 ? r.Title : r.Url,
                Note = r.Note,
                Uri = Uri.TryCreate(r.Url, UriKind.Absolute, out var u) ? u : null,
            }).ToList();
            if (Uri.TryCreate(found.MoreUrl, UriKind.Absolute, out var more))
            {
                WebMoreLink.Content = L10n.T("nws.more");
                WebMoreLink.NavigateUri = more;
                WebMoreLink.Visibility = Visibility.Visible;
            }
        }
        catch (Exception ex)
        {
            WebNoneText.Text = ex.Message;
            WebNoneText.Visibility = Visibility.Visible;
        }
    }

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
        await ReloadAsks();
        await ReloadBoard();
        await ReloadBeen();
    }

    private async System.Threading.Tasks.Task ReloadBeen()
    {
        var s = AppState.Current;
        try
        {
            var been = await ApiClient.Shared.Visits(s.Pid!, s.Token!);
            BeenList.ItemsSource = been.Select(v => new BeenRow
            {
                Host = v.Host,
                Times = L10n.Fill("rem.been.times", AppState.Current.Language,
                                  ("n", v.Times.ToString())),
                Note = (v.StoodDown ?? false) ? L10n.T("rem.been.stopped")
                       : v.Persistent ? L10n.T("rem.been.persistent") : "",
                StoodDown = v.StoodDown ?? false,
            }).ToList();
            if (been.Length == 0) BeenSub.Text = L10n.T("rem.been.none");
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    /// <summary>Stop visiting a host, or start again. The refusal itself
    /// lives where the socket opens, so pressing this binds every path that
    /// fetches — not only the one that listed it.</summary>
    private async void OnToggleHost(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string host) return;
        var s = AppState.Current;
        var row = (BeenList.ItemsSource as System.Collections.Generic.List<BeenRow>)
            ?.FirstOrDefault(r => r.Host == host);
        try
        {
            if (row?.StoodDown == true)
                await ApiClient.Shared.VisitHostAgain(s.Pid!, host, s.Token!);
            else
                await ApiClient.Shared.StandDownFromHost(s.Pid!, host, s.Token!);
            await ReloadBeen();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async System.Threading.Tasks.Task ReloadAsks()
    {
        var s = AppState.Current;
        try
        {
            var asks = await ApiClient.Shared.Inquiries(s.Pid!, s.Token!);
            AsksList.ItemsSource = Enumerable.Reverse(asks).Select(a => new AskRow
            {
                Id = a.Id,
                Brief = a.Brief,
                Count = L10n.Fill("nask.count", AppState.Current.Language,
                                  ("n", a.AnswerCount.ToString())),
                AnswersText = a.Id == _openedAsk ? AnswersOf(a) : "",
                FoldTag = a.Id == _openedAsk ? FoldableAnswer(a) : "",
                Closed = a.Closed,
            }).ToList();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private static string AnswersOf(Inquiry a)
    {
        if (a.Answers is null || a.Answers.Length == 0)
            return L10n.T("nask.anon");
        return string.Join("\n", a.Answers.Select(x =>
        {
            var who = x.Alias.Length > 0 ? x.Alias : L10n.T("nask.anon");
            var held = x.Blocked ? " — " + L10n.T("nask.held") : "";
            var points = x.PointsTo.Length > 0 ? " (" + x.PointsTo + ")" : "";
            return who + ": " + x.Body + points + held;
        }));
    }

    /// <summary>The first answer that could still be folded in, as
    /// "inquiry/answer". Empty when there is none, which collapses the
    /// button — a control that would refuse is not offered.</summary>
    private static string FoldableAnswer(Inquiry a)
    {
        var first = a.Answers?.FirstOrDefault(x => !x.Blocked && !x.Folded);
        return first is null ? "" : a.Id + "/" + first.Id;
    }

    /// <summary>The board. No token: this loads for a signed-out window too.
    /// </summary>
    private async System.Threading.Tasks.Task ReloadBoard()
    {
        try
        {
            var board = await ApiClient.Shared.OpenQuestions();
            BoardList.ItemsSource = board.Select(q => new BoardRow
            {
                Id = q.Id,
                Brief = q.Brief,
                AnswersText = q.Id == _answeringId && q.Replies is not null
                    ? string.Join("\n", q.Replies.Select(x => x.Body)) : "",
            }).ToList();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnAsk(object sender, RoutedEventArgs e)
    {
        var topic = AskTopicBox.Text.Trim();
        var question = AskQuestionBox.Text.Trim();
        if (topic.Length == 0 || question.Length == 0) return;
        var s = AppState.Current;
        AskButton.IsEnabled = false;
        try
        {
            await ApiClient.Shared.OpenInquiry(s.Pid!, s.Token!, topic, question);
            AskTopicBox.Text = ""; AskQuestionBox.Text = "";
            await ReloadAsks();
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { AskButton.IsEnabled = true; }
    }

    private async void OnReadAnswers(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string iid) return;
        try
        {
            // The single-question route is the one that carries the answers.
            await ApiClient.Shared.Inquiry(iid, AppState.Current.Token!);
            _openedAsk = iid;
            await ReloadAsks();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnCloseAsk(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string iid) return;
        try
        {
            await ApiClient.Shared.CloseInquiry(iid, AppState.Current.Token!);
            await ReloadAsks();
            await ReloadBoard();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnFoldAnswer(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string tag) return;
        var parts = tag.Split('/');
        if (parts.Length != 2) return;
        try
        {
            await ApiClient.Shared.LearnFromAnswer(parts[0], parts[1],
                                                  AppState.Current.Token!);
            await ReloadAsks();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnPickQuestion(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string iid) return;
        try
        {
            await ApiClient.Shared.OpenQuestion(iid);
            _answeringId = iid;
            ReceiptText.Text = "";
            AnswerBox.Visibility = Visibility.Visible;
            await ReloadBoard();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnSendAnswer(object sender, RoutedEventArgs e)
    {
        if (_answeringId.Length == 0 || AnswerText.Text.Trim().Length == 0) return;
        try
        {
            // No token, deliberately — see ApiClient.AnswerOpenQuestion.
            var receipt = await ApiClient.Shared.AnswerOpenQuestion(
                _answeringId, AnswerText.Text.Trim(), AliasBox.Text.Trim(),
                PointsBox.Text.Trim());
            // Held or not, the server's own note says which.
            ReceiptText.Text = receipt.Note;
            AnswerText.Text = ""; AliasBox.Text = ""; PointsBox.Text = "";
            await ReloadBoard();
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
