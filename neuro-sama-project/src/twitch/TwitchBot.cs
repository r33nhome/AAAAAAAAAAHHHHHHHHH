using System;
using System.Threading.Tasks;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using TwitchLib.Client;
using TwitchLib.Client.Events;
using TwitchLib.Client.Models;
using TwitchLib.Communication.Clients;
using TwitchLib.Communication.Models;
using Microsoft.Extensions.Logging;

namespace NeuroSama.Twitch
{
    /// <summary>
    /// C# Twitch-Client basierend auf Vedal-Architecture
    /// Koordiniert mit Python AI-Engine über WebSocket
    /// </summary>
    public class TwitchBot
    {
        private readonly ILogger<TwitchBot> _logger;
        private readonly TwitchClient _twitchClient;
        private readonly ClientWebSocket _pythonAISocket;
        private readonly RateLimiter _rateLimiter;
        private readonly ContentFilter _contentFilter;
        
        private readonly string _channel;
        private readonly string _pythonAIUrl = "ws://localhost:8001/chat";
        
        public TwitchBot(ILogger<TwitchBot> logger, string username, string oauth, string channel)
        {
            _logger = logger;
            _channel = channel;
            
            // Rate Limiting - Vedal's 20-Sekunden-Regel
            _rateLimiter = new RateLimiter(TimeSpan.FromSeconds(20));
            
            // Content-Filtering für deutsche Community
            _contentFilter = new ContentFilter();
            
            // Twitch Client Setup
            var credentials = new ConnectionCredentials(username, oauth);
            var clientOptions = new ClientOptions
            {
                MessagesAllowedInPeriod = 750,
                ThrottlingPeriod = TimeSpan.FromSeconds(30)
            };
            
            var customClient = new WebSocketClient(clientOptions);
            _twitchClient = new TwitchClient(customClient);
            _twitchClient.Initialize(credentials, _channel);
            
            // Event-Handler registrieren
            _twitchClient.OnMessageReceived += OnMessageReceived;
            _twitchClient.OnConnected += OnConnected;
            _twitchClient.OnJoinedChannel += OnJoinedChannel;
            _twitchClient.OnError += OnError;
            
            // WebSocket für Python AI
            _pythonAISocket = new ClientWebSocket();
        }
        
        public async Task StartAsync()
        {
            try
            {
                _logger.LogInformation("Starte deutschen Neuro-sama Twitch Bot...");
                
                // Verbindung zu Python AI-Engine
                await _pythonAISocket.ConnectAsync(new Uri(_pythonAIUrl), CancellationToken.None);
                _logger.LogInformation("Verbunden mit Python AI-Engine auf {Url}", _pythonAIUrl);
                
                // Twitch-Verbindung starten
                _twitchClient.Connect();
                
                _logger.LogInformation("Twitch Bot erfolgreich gestartet für Channel: {Channel}", _channel);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Fehler beim Starten des Twitch Bots");
                throw;
            }
        }
        
        private async void OnMessageReceived(object? sender, OnMessageReceivedArgs e)
        {
            var message = e.ChatMessage;
            
            try
            {
                _logger.LogDebug("Nachricht empfangen von {User}: {Message}", 
                    message.DisplayName, message.Message);
                
                // Content-Filtering
                if (!_contentFilter.IsAppropriate(message.Message))
                {
                    _logger.LogWarning("Nachricht von {User} durch Content-Filter blockiert", 
                        message.DisplayName);
                    return;
                }
                
                // Rate-Limiting (Vedal's 20-Sekunden-Regel)
                if (!_rateLimiter.AllowMessage(message.UserId))
                {
                    _logger.LogDebug("Rate-Limit erreicht für User {User}", message.DisplayName);
                    return;
                }
                
                // Deutsche Chat-Commands prüfen
                if (await HandleGermanChatCommands(message))
                {
                    return; // Command wurde behandelt
                }
                
                // An Python AI weiterleiten
                await SendMessageToPythonAI(message);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Fehler bei Message-Processing für User {User}", 
                    message.DisplayName);
            }
        }
        
        private async Task<bool> HandleGermanChatCommands(ChatMessage message)
        {
            var text = message.Message.ToLower();
            
            // Deutsche Chat-Commands
            if (text.StartsWith("!hallo"))
            {
                await SendTwitchMessage($"Hallo {message.DisplayName}! Ich bin Neuro-sama, eure deutsche AI VTuber! 😊");
                return true;
            }
            
            if (text.StartsWith("!hilfe") || text.StartsWith("!commands"))
            {
                await SendTwitchMessage("Deutsche Commands: !hallo, !wetter, !news, !joke, !time - Oder einfach mit mir chatten! 🤖");
                return true;
            }
            
            if (text.StartsWith("!time") || text.StartsWith("!zeit"))
            {
                var germanTime = DateTime.Now.ToString("HH:mm:ss dd.MM.yyyy");
                await SendTwitchMessage($"Aktuelle deutsche Zeit: {germanTime} 🕐");
                return true;
            }
            
            if (text.StartsWith("!wetter") || text.StartsWith("!weather"))
            {
                // Trigger für Search-Integration-Agent (Google Search)
                var searchQuery = text.Replace("!wetter", "").Replace("!weather", "").Trim();
                if (string.IsNullOrEmpty(searchQuery))
                {
                    searchQuery = "Wetter Deutschland heute";
                }
                
                var weatherRequest = new
                {
                    type = "search_command",
                    command = "weather",
                    query = searchQuery,
                    user = message.DisplayName,
                    user_id = message.UserId
                };
                
                await SendToPythonAI(weatherRequest);
                return true;
            }
            
            return false; // Kein Command erkannt
        }
        
        private async Task SendMessageToPythonAI(ChatMessage message)
        {
            var aiRequest = new
            {
                type = "chat_message",
                user_id = message.UserId,
                username = message.DisplayName,
                message = message.Message,
                badges = message.Badges?.Select(b => b.Key).ToArray() ?? Array.Empty<string>(),
                is_subscriber = message.IsSubscriber,
                is_moderator = message.IsModerator,
                timestamp = DateTime.UtcNow.ToString("O"),
                platform = "twitch",
                channel = _channel
            };
            
            await SendToPythonAI(aiRequest);
        }
        
        private async Task SendToPythonAI(object request)
        {
            try
            {
                var jsonData = JsonSerializer.Serialize(request);
                var buffer = Encoding.UTF8.GetBytes(jsonData);
                
                await _pythonAISocket.SendAsync(
                    new ArraySegment<byte>(buffer),
                    WebSocketMessageType.Text,
                    true,
                    CancellationToken.None);
                
                _logger.LogDebug("Nachricht an Python AI gesendet: {JsonData}", jsonData);
                
                // Response von Python AI empfangen
                await ReceiveAIResponse();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Fehler beim Senden an Python AI");
                
                // Fallback-Response bei AI-Fehler
                await SendTwitchMessage("Hm, da ist wohl was schiefgegangen... Aber ich bin trotzdem da! 🤖");
            }
        }
        
        private async Task ReceiveAIResponse()
        {
            try
            {
                var buffer = new byte[4096];
                var result = await _pythonAISocket.ReceiveAsync(
                    new ArraySegment<byte>(buffer),
                    CancellationToken.None);
                
                var responseJson = Encoding.UTF8.GetString(buffer, 0, result.Count);
                var response = JsonSerializer.Deserialize<AIResponse>(responseJson);
                
                if (response?.Response != null)
                {
                    await SendTwitchMessage(response.Response);
                    
                    // Optional: TTS triggern
                    if (response.NeedsTTS)
                    {
                        await TriggerTTSResponse(response.Response, response.Emotion);
                    }
                }
                
                _logger.LogDebug("AI Response empfangen und versendet: {Response}", response?.Response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Fehler beim Empfangen der AI Response");
            }
        }
        
        private async Task SendTwitchMessage(string message)
        {
            try
            {
                _twitchClient.SendMessage(_channel, message);
                _logger.LogInformation("Twitch-Message gesendet: {Message}", message);
                
                // Rate-Limiting für eigene Messages
                await Task.Delay(1000); // 1 Sekunde zwischen eigenen Nachrichten
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Fehler beim Senden der Twitch-Message: {Message}", message);
            }
        }
        
        private async Task TriggerTTSResponse(string text, string emotion = "neutral")
        {
            try
            {
                var ttsRequest = new
                {
                    type = "tts_request",
                    text = text,
                    emotion = emotion,
                    language = "de",
                    voice_characteristics = "german_female_enthusiastic"
                };
                
                // An Audio-Agent senden (separate WebSocket oder Message-Queue)
                // Implementation abhängig von System-Architecture
                _logger.LogDebug("TTS-Request getriggert: {Text}", text);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Fehler beim TTS-Trigger");
            }
        }
        
        private void OnConnected(object? sender, OnConnectedArgs e)
        {
            _logger.LogInformation("✅ Twitch Bot verbunden: {AutoJoinChannel}", e.AutoJoinChannel);
        }
        
        private void OnJoinedChannel(object? sender, OnJoinedChannelArgs e)
        {
            _logger.LogInformation("✅ Channel beigetreten: {Channel}", e.Channel);
            
            // Begrüßungsnachricht (optional)
            Task.Run(async () =>
            {
                await Task.Delay(2000); // 2 Sekunden warten
                await SendTwitchMessage("Hallo Chat! Neuro-sama ist online! 🤖✨");
            });
        }
        
        private void OnError(object? sender, OnErrorEventArgs e)
        {
            _logger.LogError("Twitch Client Fehler: {Exception}", e.Exception);
        }
        
        public async Task StopAsync()
        {
            try
            {
                _logger.LogInformation("Stoppe Twitch Bot...");
                
                _twitchClient?.Disconnect();
                
                if (_pythonAISocket?.State == WebSocketState.Open)
                {
                    await _pythonAISocket.CloseAsync(WebSocketCloseStatus.NormalClosure,
                        "Bot shutdown", CancellationToken.None);
                }
                
                _pythonAISocket?.Dispose();
                
                _logger.LogInformation("✅ Twitch Bot erfolgreich gestoppt");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Fehler beim Stoppen des Twitch Bots");
            }
        }
    }
    
    /// <summary>
    /// Rate-Limiter basierend auf Vedal's 20-Sekunden-Regel
    /// </summary>
    public class RateLimiter
    {
        private readonly TimeSpan _interval;
        private readonly Dictionary<string, DateTime> _lastMessageTimes = new();
        
        public RateLimiter(TimeSpan interval)
        {
            _interval = interval;
        }
        
        public bool AllowMessage(string userId)
        {
            var now = DateTime.UtcNow;
            
            if (_lastMessageTimes.TryGetValue(userId, out var lastTime))
            {
                if (now - lastTime < _interval)
                {
                    return false; // Rate-Limit aktiv
                }
            }
            
            _lastMessageTimes[userId] = now;
            return true;
        }
    }
    
    /// <summary>
    /// Content-Filter für deutsche Community
    /// </summary>
    public class ContentFilter
    {
        private readonly HashSet<string> _blockedWords = new(StringComparer.OrdinalIgnoreCase)
        {
            // Deutsche Schimpfwörter und problematische Begriffe
            // (Hier würde eine echte Implementierung stehen)
        };
        
        public bool IsAppropriate(string message)
        {
            if (string.IsNullOrWhiteSpace(message))
                return false;
                
            // Basis-Filterung
            var words = message.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            
            foreach (var word in words)
            {
                if (_blockedWords.Contains(word.Trim()))
                {
                    return false;
                }
            }
            
            // Weitere Filterlogik...
            // - Spam-Detection
            // - Link-Validation
            // - Caps-Lock-Filter
            // - etc.
            
            return true;
        }
    }
    
    /// <summary>
    /// Response-Struktur von Python AI-Engine
    /// </summary>
    public class AIResponse
    {
        public string? Response { get; set; }
        public string? Emotion { get; set; }
        public bool NeedsTTS { get; set; }
        public string? UserId { get; set; }
        public DateTime Timestamp { get; set; }
    }
}