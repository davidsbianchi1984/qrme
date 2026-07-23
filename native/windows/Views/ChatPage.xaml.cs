using System;
using System.Collections.ObjectModel;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class ChatPage : Page
{
    public record BubbleRow(string Text, HorizontalAlignment Align);

    private readonly ObservableCollection<BubbleRow> _messages = new();

    public ChatPage() => InitializeComponent();

    protected override void OnNavigatedTo(NavigationEventArgs e)
    {
        Subtitle.Text = $"Talk with {AppState.Current.DisplayName} — replies are in character and moderated.";
        MessagesList.ItemsSource = _messages;
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
            // Lazily mint the device owner's interactor identity once.
            if (string.IsNullOrEmpty(s.InteractorId))
            {
                var created = await ApiClient.Shared.CreateInteractor("You");
                s.RememberInteractor(created.Id);
            }
            var reply = await ApiClient.Shared.Chat(s.Pid!, s.Token!,
                                                    s.InteractorId!, text);
            var p = reply.ProfileMessage;
            _messages.Add(new BubbleRow(
                p.Content is { } c && p.Status == "approved"
                    ? c
                    : "⏳ Held for review"
                      + (p.FlagReason is { } fr ? $" — {fr}" : ""),
                HorizontalAlignment.Left));
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            ErrorText.Visibility = Visibility.Visible;
        }
        finally { SendButton.IsEnabled = true; }
    }
}
