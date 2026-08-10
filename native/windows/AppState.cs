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
    // Kept from the mint response. Without it this shell could hold an
    // identity and never act as it — which is why the room routes had to be
    // callable with no credential for the Community page to work at all.
    public string? InteractorToken { get; set; }
    public bool InteractorVerified { get; set; }
    // The profile's chosen language also drives the app chrome via L10n.
    public string Language { get; set; } = "en";

    /// <summary>The person's own model key, held on this machine only and
    /// sent per request as <c>x-llm-api-key</c>.
    ///
    /// <para>The console has offered this since 0.4.3 and the shells never
    /// did — so a key set in the console was used there and the deployment's
    /// key used here, on the same profile, with nothing saying so.</para>
    /// </summary>
    public string LlmKey { get; set; } = "";

    /// <summary>Store or clear it. Empty is the clear: no key means the
    /// deployment's, and there is no flag to leave switched on by
    /// mistake.</summary>
    public void RememberLlmKey(string key)
    {
        LlmKey = (key ?? "").Trim();
        Save();
    }

    /// <summary>The deployment invite key, sent per request as
    /// <c>x-signup-key</c>. A published deployment gates account creation
    /// behind one; empty means none, which is what every ungated
    /// deployment wants.</summary>
    public string SignupKey { get; set; } = "";

    public void RememberSignupKey(string key)
    {
        SignupKey = (key ?? "").Trim();
        Save();
    }

    public void RememberLanguage(string code)
    {
        Language = code;
        Save();
    }

    public void RememberInteractor(string id, bool adult = false,
                                   string? token = null)
    {
        InteractorId = id;
        InteractorVerified = adult;
        if (token is { Length: > 0 }) InteractorToken = token;
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
        InteractorToken = null;
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
