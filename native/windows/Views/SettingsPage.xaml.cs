using System;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace QrmeStudio.Views;

public sealed partial class SettingsPage : Page
{
    public sealed class ObjectionRow
    {
        public string Id { get; init; } = "";
        public string Status { get; init; } = "";
        public string Reason { get; init; } = "";
        public bool CanAttest { get; init; }
        public Visibility AttestVisibility =>
            CanAttest ? Visibility.Visible : Visibility.Collapsed;
    }

    private ProviderInfo[] _providers = Array.Empty<ProviderInfo>();
    private bool _loading;   // suppress SelectionChanged while populating

    public SettingsPage() => InitializeComponent();

    protected override async void OnNavigatedTo(NavigationEventArgs e) => await Reload();

    private async System.Threading.Tasks.Task Reload()
    {
        var s = AppState.Current;
        _loading = true;
        try
        {
            _providers = (await ApiClient.Shared.Models()).Providers;
            ProviderBox.ItemsSource = _providers.Select(p =>
                $"{p.Label}  ({(p.Configured ? "ready" : "no key")})").ToList();
            var current = await ApiClient.Shared.ProfileModel(s.Pid!);
            var idx = Array.FindIndex(_providers, p => p.Name == current.Provider);
            ProviderBox.SelectedIndex = idx >= 0 ? idx : 0;
            EffectiveText.Text = $"Effective now: {current.Effective}";
        }
        catch (Exception ex) { ShowError(ex.Message); }
        finally { _loading = false; }

        try
        {
            var objections = await ApiClient.Shared.Objections(s.Pid!, s.Token!);
            ObjectionsList.ItemsSource = objections.Select(o => new ObjectionRow
            {
                Id = o.Id,
                Status = o.Status.ToUpper()
                         + (o.Reattested == 1 ? " · basis re-attested" : ""),
                Reason = o.Reason ?? "",
                CanAttest = o.Status == "open" && o.Reattested == 0,
            }).ToList();
            NoObjections.Visibility =
                objections.Length == 0 ? Visibility.Visible : Visibility.Collapsed;
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnProviderPicked(object sender, SelectionChangedEventArgs e)
    {
        if (_loading) return;
        var idx = ProviderBox.SelectedIndex;
        if (idx < 0 || idx >= _providers.Length) return;
        var s = AppState.Current;
        try
        {
            var m = await ApiClient.Shared.SetModel(s.Pid!, s.Token!,
                                                    _providers[idx].Name);
            EffectiveText.Text = $"Effective now: {m.Effective}";
        }
        catch (Exception ex) { ShowError(ex.Message); }
    }

    private async void OnAttest(object sender, RoutedEventArgs e)
    {
        if ((sender as Button)?.Tag is not string oid) return;
        var s = AppState.Current;
        try
        {
            await ApiClient.Shared.Attest(s.Pid!, oid, s.Token!);
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
