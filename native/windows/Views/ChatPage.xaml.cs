using System;
using System.Collections.ObjectModel;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class ChatPage : Page
{
    public record BubbleRow(string Text, HorizontalAlignment Align);

    private readonly ObservableCollection<BubbleRow> _messages = new();

    // Index 0 is the empty default: "let it read my prompt". The label is a
    // key now — this shell and the console said what each role does while the
    // phones said only "Advisor" and "Operator", on the control that decides
    // whether a synthetic profile recommends something or goes and does it.
    private static readonly (string Value, string Key)[] Roles =
    {
        ("", "nchat.role.read"),
        ("advisor", "nchat.role.advisor"),
        ("collaborator", "nchat.role.collaborator"),
        ("operator", "nchat.role.operator"),
    };

    public ChatPage()
    {
        InitializeComponent();
        var lang = AppState.Current.Language;
        Title.Text = L10n.T("tab.chat", lang);
        RoleBox.Header = L10n.T("nchat.rolepick", lang);
        RoleBox.ItemsSource = Roles.Select(r => L10n.T(r.Key, lang)).ToList();
        RoleBox.SelectedIndex = 0;
        DraftBox.PlaceholderText = L10n.T("nchat.type.ph", lang);
        SendButton.Content = L10n.T("nchat.send", lang);
    }

    private string? SelectedRole()
    {
        var i = RoleBox.SelectedIndex;
        return i > 0 && i < Roles.Length ? Roles[i].Value : null;
    }

    protected override void OnNavigatedTo(NavigationEventArgs e)
    {
        Subtitle.Text = L10n.Fill("nchat.sub", AppState.Current.Language,
                                  ("name", AppState.Current.DisplayName));
        RehearsalBox.PlaceholderText = L10n.T("cht.rh.scenario.ph");
        RehearsalButton.Content = L10n.T("cht.rh.open");
        MessagesList.ItemsSource = _messages;
    }

    private string? _rehearsalId;
    private string _rehearsalScenario = "";

    // Rehearsal: open a room whose transcript lives only until it closes;
    // while it stands, sends go there and nothing is remembered.
    private async void OnRehearsal(object sender, RoutedEventArgs e)
    {
        var s = AppState.Current;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            if (_rehearsalId is { } roomId)
            {
                await ApiClient.Shared.CloseRehearsal(s.Pid!, roomId);
                _rehearsalId = null;
                RehearsalButton.Content = L10n.T("cht.rh.open");
                RehearsalLine.Visibility = Visibility.Collapsed;
                RehearsalBox.Visibility = Visibility.Visible;
                return;
            }
            var scenario = RehearsalBox.Text.Trim();
            if (scenario.Length == 0) return;
            if (string.IsNullOrEmpty(s.InteractorId))
            {
                var created = await ApiClient.Shared.CreateInteractor("You");
                s.RememberInteractor(created.Id, token: created.Token);
            }
            var room = await ApiClient.Shared.OpenRehearsal(
                s.Pid!, s.InteractorId!, scenario);
            _rehearsalId = room.Id;
            _rehearsalScenario = room.Scenario;
            RehearsalBox.Text = ""; RehearsalBox.Visibility = Visibility.Collapsed;
            RehearsalButton.Content = L10n.T("cht.rh.close");
            RehearsalLine.Text = "🎭 " + room.Scenario;
            RehearsalLine.Visibility = Visibility.Visible;
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
    }

    private async void OnSend(object sender, RoutedEventArgs e)
    {
        var text = DraftBox.Text.Trim();
        if (text.Length == 0) return;
        DraftBox.Text = "";
        _messages.Add(new BubbleRow(text, HorizontalAlignment.Right));

        var s = AppState.Current;
        SendButton.IsEnabled = false;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            // An open rehearsal room takes the turn: nothing lands in the
            // remembered conversation, and the bubble says so.
            if (_rehearsalId is { } openRoom)
            {
                var turn = await ApiClient.Shared.Rehearse(
                    s.Pid!, openRoom, text);
                _messages.Add(new BubbleRow(turn.Reply, HorizontalAlignment.Left));
                _messages.Add(new BubbleRow("🎭 " + _rehearsalScenario,
                                            HorizontalAlignment.Left));
                return;
            }
            // Lazily mint the device owner's interactor identity once.
            if (string.IsNullOrEmpty(s.InteractorId))
            {
                var created = await ApiClient.Shared.CreateInteractor("You");
                s.RememberInteractor(created.Id, token: created.Token);
            }
            var reply = await ApiClient.Shared.Chat(s.Pid!, s.Token!,
                                                    s.InteractorId!, text,
                                                    SelectedRole());
            var p = reply.ProfileMessage;
            _messages.Add(new BubbleRow(
                p.Content is { } c && p.Status == "approved"
                    ? c
                    : "⏳ Held for review"
                      + (p.FlagReason is { } fr ? $" — {fr}" : ""),
                HorizontalAlignment.Left));
            if (p.Status == "approved")
                // The watermark rides on every AI render, always visible.
                _messages.Add(new BubbleRow(
                    p.Watermark?.Display?.Line ?? "✦ AI",
                    HorizontalAlignment.Left));
            if (p.Status == "approved" && reply.RoleContext is { } rc)
                _messages.Add(new BubbleRow(
                    $"◈ worked as {rc.Role} ({rc.How})",
                    HorizontalAlignment.Left));
            if (p.Status == "approved" && reply.Provenance is { } prov)
            {
                var lang = AppState.Current.Language;
                var trail = "ⓘ " + L10n.Fill(
                    "nprv.generated", lang,
                    ("model", prov.GeneratedBy),
                    ("n", $"{prov.GroundedInInfo.SourceItems}"),
                    ("status", prov.Moderation.Status));
                if (prov.LicensedFrom is { } lf)
                    trail += " · " + L10n.Fill("nprv.licensed", lang, ("source", lf));
                _messages.Add(new BubbleRow(trail, HorizontalAlignment.Left));
            }
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
        finally { SendButton.IsEnabled = true; }
    }
}
