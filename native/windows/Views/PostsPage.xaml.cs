using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class PostsPage : Page
{
    public record PostRow(string Status, string Content, string Mark);

    public PostsPage()
    {
        InitializeComponent();
        Localize();
    }

    private void Localize()
    {
        var lang = AppState.Current.Language;
        Title.Text = L10n.T("tab.posts", lang);
        Sub.Text = L10n.T("npst.sub", lang);
        Empty.Text = L10n.T("npst.none", lang);
    }

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        var s = AppState.Current;
        try
        {
            var posts = await ApiClient.Shared.Posts(s.Pid!);
            PostsList.ItemsSource = posts.Select(p => new PostRow(
                Cap(p.Status ?? "draft"), p.Content,
                p.Watermark?.Display?.Line ?? "✦ AI")).ToList();
            Empty.Visibility = posts.Length == 0 ? Visibility.Visible : Visibility.Collapsed;
        }
        catch
        {
            Empty.Text = L10n.T("npst.error");
            Empty.Visibility = Visibility.Visible;
        }
        finally
        {
            Loading.IsActive = false;
            Loading.Visibility = Visibility.Collapsed;
        }
        LoadStream();
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];

    // -- the public stream --
    //
    // `Plays` is read from the server and never recomputed here. Only footage
    // this deployment holds comes back true, so paging past an off-site card
    // makes no request to another company's server — the promise
    // `qrme/db.py` makes about `post_videos`, kept on this shell too.

    private List<FeedCard> _stream = new();
    private string? _streamCursor;
    private int _at;
    private readonly HashSet<string> _opened = new();

    private async void LoadStream()
    {
        var lang = AppState.Current.Language;
        StreamTitle.Text = L10n.T("feed.title", lang);
        StreamSub.Text = L10n.T("feed.sub", lang);
        StreamBack.Content = L10n.T("feed.back", lang);
        StreamNext.Content = L10n.T("feed.next", lang);
        StreamOpen.Content = L10n.T("feed.play", lang);
        try
        {
            var page = await ApiClient.Shared.PublicFeed();
            _stream = page.Items ?? new List<FeedCard>();
            _streamCursor = page.Cursor;
        }
        catch
        {
            // A stream that cannot load is a quiet shelf, not an error page.
            _stream = new List<FeedCard>();
        }
        ShowCard();
    }

    private void ShowCard()
    {
        var lang = AppState.Current.Language;
        if (_stream.Count == 0)
        {
            StreamTitleLine.Text = L10n.T("feed.empty", lang);
            StreamKind.Text = "";
            StreamReason.Text = "";
            StreamSays.Text = "";
            StreamAct.Content = "";
            return;
        }
        var c = _stream[System.Math.Clamp(_at, 0, _stream.Count - 1)];
        // Spelled out: a key built at runtime is invisible to the guard
        // that checks every asked-for key exists.
        StreamKind.Text = c.Kind switch
        {
            "offsite" => L10n.T("feed.kind.offsite", lang),
            "room" => L10n.T("feed.kind.room", lang),
            "desk" => L10n.T("feed.kind.desk", lang),
            _ => L10n.T("feed.kind.video", lang),
        };
        StreamReason.Text = c.Reason ?? "";
        StreamTitleLine.Text = c.Kind switch
        {
            "room" => c.Topic ?? L10n.T("feed.room.untitled", lang),
            "desk" => (c.DisplayName ?? "—") + " · " + (c.Trade ?? ""),
            _ => c.Title ?? "—",
        };
        StreamSays.Text = c.Kind switch
        {
            "room" => c.Entering ?? "",
            "desk" => c.Ringing ?? "",
            _ => c.Note ?? "",
        };
        StreamAct.Content = c.Kind switch
        {
            "room" => L10n.T("feed.enter", lang),
            "desk" => L10n.T("feed.ring", lang),
            "offsite" => _opened.Contains(c.Id ?? "") ? "" : L10n.T("feed.play", lang),
            _ => "",
        };
    }

    private void OnStreamBack(object sender, RoutedEventArgs e)
    {
        _at = System.Math.Max(0, _at - 1);
        ShowCard();
    }

    private async void OnStreamNext(object sender, RoutedEventArgs e)
    {
        _at = System.Math.Min(_stream.Count - 1, _at + 1);
        // One page ahead of the end, so the next press never waits.
        if (_streamCursor != null && _at >= _stream.Count - 2)
        {
            try
            {
                var page = await ApiClient.Shared.PublicFeed(_streamCursor);
                _stream.AddRange(page.Items ?? new List<FeedCard>());
                _streamCursor = page.Cursor;
            }
            catch { }
        }
        ShowCard();
    }

    private void OnStreamAct(object sender, RoutedEventArgs e)
    {
        if (_stream.Count == 0) return;
        var c = _stream[System.Math.Clamp(_at, 0, _stream.Count - 1)];
        // The first request an off-site card ever makes is this one.
        if (c.Kind == "offsite" && c.Id != null) _opened.Add(c.Id);
        StreamLine.Text = c.Kind switch
        {
            "room" => c.Entering ?? "",
            "desk" => c.Ringing ?? "",
            _ => c.Facade?.Url ?? "",
        };
        ShowCard();
    }

    private async void OnStreamOpen(object sender, RoutedEventArgs e)
    {
        try
        {
            var c = await ApiClient.Shared.FeedItem(StreamItemId.Text);
            StreamLine.Text = (c.Title ?? c.DisplayName ?? c.Id ?? "—")
                + " · " + ((c.Plays ?? false) ? "▶" : "—");
        }
        catch
        {
            // 404 for a rated item this reader is not verified for.
            StreamLine.Text = "";
        }
    }
}
