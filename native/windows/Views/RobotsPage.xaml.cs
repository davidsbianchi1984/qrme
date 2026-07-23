using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class RobotsPage : Page
{
    public sealed class RobotRow
    {
        public string Id { get; init; } = "";
        public string Name { get; init; } = "";
        public string Status { get; init; } = "";
        public string[] Commands { get; init; } = Array.Empty<string>();
        public Visibility SayVisibility =>
            Commands.Contains("say") ? Visibility.Visible : Visibility.Collapsed;
        public Visibility CleanVisibility =>
            Commands.Contains("clean") ? Visibility.Visible : Visibility.Collapsed;
    }

    private RobotSpec[] _catalog = Array.Empty<RobotSpec>();

    public RobotsPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        try
        {
            _catalog = (await ApiClient.Shared.Robotics()).Robots;
            ModelBox.ItemsSource = _catalog
                .Select(r => $"{r.Label} · {r.Maker}").ToList();
            if (_catalog.Length > 0) ModelBox.SelectedIndex = 0;
        }
        catch (Exception ex) { ShowError(ex.Message); }
        await Reload();
    }

    private async System.Threading.Tasks.Task Reload()
    {
        var s = AppState.Current;
        try
        {
            var robots = await ApiClient.Shared.Robots(s.Pid!, s.Token!);
            RobotsList.ItemsSource = robots.Select(r => new RobotRow
            {
                Id = r.Id, Name = r.Name,
                Status = Cap(r.Status ?? "docked"),
                Commands = r.Commands ?? Array.Empty<string>(),
            }).ToList();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnBind(object sender, RoutedEventArgs e)
    {
        if (ModelBox.SelectedIndex < 0 || ModelBox.SelectedIndex >= _catalog.Length) return;
        var s = AppState.Current;
        BindButton.IsEnabled = false;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            await ApiClient.Shared.BindRobot(s.Pid!, s.Token!,
                _catalog[ModelBox.SelectedIndex].Model);
            await Reload();
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { BindButton.IsEnabled = true; }
    }

    private void OnSay(object sender, RoutedEventArgs e) =>
        Command(sender, "say", TopicBox.Text.Trim());

    private void OnClean(object sender, RoutedEventArgs e) => Command(sender, "clean", null);

    private void OnPatrol(object sender, RoutedEventArgs e) => Command(sender, "patrol", null);

    private void OnDock(object sender, RoutedEventArgs e) => Command(sender, "dock", null);

    private async void Command(object sender, string command, string? arg)
    {
        if ((sender as Button)?.Tag is not string rid) return;
        var s = AppState.Current;
        ErrorText.Visibility = Visibility.Collapsed;
        try
        {
            var r = await ApiClient.Shared.CommandRobot(rid, s.Token!, command, arg);
            ResultText.Text = r.Spoken ?? $"{r.Command}: {r.Status}";
            ResultCard.Visibility = Visibility.Visible;
            await Reload();
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private void ShowError(string message)
    {
        ErrorText.Text = message;
        ErrorText.Visibility = Visibility.Visible;
    }

    private static string Cap(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..];
}
