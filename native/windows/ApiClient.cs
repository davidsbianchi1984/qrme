using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace QrmeStudio;

// MARK: wire models (mirror qrme/models.py + routers)

public record ProfileCreated(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("owner_token")] string OwnerToken);

public record ProfileCard(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("status")] string? Status);

public record Post(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("status")] string? Status);

/// <summary>
/// Async client for the QRME backend. Windows reaches the local dev server
/// directly on 127.0.0.1.
/// </summary>
public sealed class ApiClient
{
    public static ApiClient Shared { get; } = new();

    private readonly HttpClient _http = new() { BaseAddress = new Uri("http://127.0.0.1:8000") };

    public void SetBase(string url) => _http.BaseAddress = new Uri(url.TrimEnd('/'));

    private async Task<T> Send<T>(HttpRequestMessage req)
    {
        var res = await _http.SendAsync(req);
        var body = await res.Content.ReadAsStringAsync();
        if (!res.IsSuccessStatusCode)
        {
            string? detail = null;
            try { detail = JsonDocument.Parse(body).RootElement.GetProperty("detail").GetString(); }
            catch { /* non-JSON error body */ }
            throw new HttpRequestException(detail ?? $"HTTP {(int)res.StatusCode}");
        }
        return JsonSerializer.Deserialize<T>(body)!;
    }

    private static HttpRequestMessage Post(string path, object body, string? token = null)
    {
        var req = new HttpRequestMessage(HttpMethod.Post, path) { Content = JsonContent.Create(body) };
        if (token is not null) req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    public Task<ProfileCreated> CreateProfile(string name, string persona, string kind, string birthdate) =>
        Send<ProfileCreated>(Post("/profiles", new
        {
            owner_id = "owner-1",
            kind,
            display_name = name,
            persona,
            demographics = new { language = "en" },
            verification = new { birthdate },
        }));

    public Task<ProfileCard> Profile(string id) =>
        Send<ProfileCard>(new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}"));

    public Task<Post> Compose(string id, string token, string topic) =>
        Send<Post>(Post($"/profiles/{id}/compose", new { topic }, token));

    public Task<Post[]> Posts(string id) =>
        Send<Post[]>(new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/posts"));
}
