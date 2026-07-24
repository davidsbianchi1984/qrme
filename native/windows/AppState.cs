using System;
using System.IO;
using System.Text.Json;

namespace QrmeStudio;

/// <summary>
/// The created profile id + owner token, persisted to a small JSON file under
/// LocalApplicationData so the app resumes signed-in (unpackaged-safe).
/// </summary>
public sealed class AppState
{
    public static AppState Current { get; } = Load();

    public string? Pid { get; set; }
    public string? Token { get; set; }
    public string DisplayName { get; set; } = "";
    // The device owner's interactor identity for Chat, minted lazily.
    // InteractorVerified is true when the identity was minted with an 18+
    // birthdate — the key that opens the rated stranger tier.
    public string? InteractorId { get; set; }
    public bool InteractorVerified { get; set; }

    public void RememberInteractor(string id, bool adult = false)
    {
        InteractorId = id;
        InteractorVerified = adult;
        Save();
    }

    public bool IsSignedIn => !string.IsNullOrEmpty(Pid) && !string.IsNullOrEmpty(Token);

    private static string PathOnDisk =>
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                     "QrmeStudio", "session.json");

    public void SignIn(ProfileCreated r)
    {
        Pid = r.Id; Token = r.OwnerToken; DisplayName = r.DisplayName;
        Save();
    }

    public void SignOut()
    {
        Pid = null; Token = null; DisplayName = ""; InteractorId = null;
        InteractorVerified = false;
        try { File.Delete(PathOnDisk); } catch { /* ignore */ }
    }

    private void Save()
    {
        Directory.CreateDirectory(Path.GetDirectoryName(PathOnDisk)!);
        File.WriteAllText(PathOnDisk, JsonSerializer.Serialize(this));
    }

    private static AppState Load()
    {
        try
        {
            if (File.Exists(PathOnDisk))
                return JsonSerializer.Deserialize<AppState>(File.ReadAllText(PathOnDisk)) ?? new AppState();
        }
        catch { /* fall through to fresh state */ }
        return new AppState();
    }
}
