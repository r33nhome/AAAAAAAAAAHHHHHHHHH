# C# Dependencies for Vedal-Inspired System

## Core C# Project Structure
```
services/csharp/
├── TwitchProcessor/           # Main Twitch integration service
│   ├── TwitchProcessor.csproj
│   ├── Program.cs
│   └── Services/
├── SystemController/          # System-level integration
│   ├── SystemController.csproj  
│   └── Controllers/
└── UnityBridge/              # Future Unity SDK integration
    └── UnityBridge.csproj
```

## TwitchProcessor.csproj Dependencies
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <!-- Twitch Integration (Vedal-Confirmed) -->
    <PackageReference Include="TwitchLib" Version="3.5.3" />
    <PackageReference Include="TwitchLib.Client" Version="3.3.0" />
    <PackageReference Include="TwitchLib.Api" Version="3.8.0" />
    
    <!-- Real-time Communication -->
    <PackageReference Include="Microsoft.AspNetCore.SignalR" Version="8.0.0" />
    <PackageReference Include="Microsoft.AspNetCore.SignalR.Client" Version="8.0.0" />
    
    <!-- WebSocket Communication with Python -->
    <PackageReference Include="System.Net.WebSockets.Client" Version="8.0.0" />
    <PackageReference Include="Websocket.Client" Version="5.0.0" />
    
    <!-- JSON Processing -->
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageReference Include="System.Text.Json" Version="8.0.0" />
    
    <!-- HTTP Client -->
    <PackageReference Include="Microsoft.Extensions.Http" Version="8.0.0" />
    
    <!-- Configuration & Logging -->
    <PackageReference Include="Microsoft.Extensions.Configuration" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.0" />
    <PackageReference Include="Serilog.AspNetCore" Version="7.0.0" />
    
    <!-- Rate Limiting -->
    <PackageReference Include="AspNetCoreRateLimit" Version="5.0.0" />
    
    <!-- Content Filtering -->
    <PackageReference Include="Microsoft.ML" Version="3.0.1" />
  </ItemGroup>

</Project>
```

## SystemController.csproj Dependencies
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <!-- Windows API Integration -->
    <PackageReference Include="Microsoft.Win32.Registry" Version="5.0.0" />
    <PackageReference Include="System.Management" Version="8.0.0" />
    
    <!-- Audio System Integration -->
    <PackageReference Include="NAudio" Version="2.2.1" />
    <PackageReference Include="System.Speech" Version="8.0.0" />
    
    <!-- Configuration -->
    <PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.0" />
    
    <!-- Performance Monitoring -->
    <PackageReference Include="System.Diagnostics.PerformanceCounter" Version="8.0.0" />
  </ItemGroup>

</Project>
```

## UnityBridge.csproj Dependencies (Future)
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <!-- Unity Engine References (when available) -->
    <!-- <PackageReference Include="Unity.Netcode.GameObjects" Version="1.5.2" /> -->
    <!-- <PackageReference Include="Unity.Collections" Version="2.1.4" /> -->
    
    <!-- Game State Communication -->
    <PackageReference Include="MessagePack" Version="2.5.124" />
    <PackageReference Include="System.Memory" Version="4.5.5" />
    
    <!-- Computer Vision Integration -->
    <PackageReference Include="OpenCvSharp4" Version="4.8.0.20230708" />
    <PackageReference Include="OpenCvSharp4.runtime.win" Version="4.8.0.20230708" />
  </ItemGroup>

</Project>
```

## Global C# Configuration (Directory.Build.props)
```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>12.0</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>

  <ItemGroup>
    <!-- Common packages for all C# projects -->
    <PackageReference Include="Microsoft.Extensions.Hosting" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.Configuration" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.0" />
    
    <!-- Security -->
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.0" />
    
    <!-- Testing -->
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.7.2" />
    <PackageReference Include="xunit" Version="2.4.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.4.5" />
    <PackageReference Include="Moq" Version="4.20.69" />
  </ItemGroup>
</Project>
```

## Development Tools
```xml
<!-- Directory.Packages.props for centralized package management -->
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <!-- Development Tools -->
    <PackageVersion Include="Microsoft.CodeAnalysis.Analyzers" Version="3.3.4" />
    <PackageVersion Include="StyleCop.Analyzers" Version="1.2.0-beta.507" />
    <PackageVersion Include="SonarAnalyzer.CSharp" Version="9.10.0.77988" />
  </ItemGroup>
</Project>
```

## Build and Deployment Commands
```bash
# Install .NET 8.0 SDK
# Download from: https://dotnet.microsoft.com/download/dotnet/8.0

# Build all C# services
dotnet build services/csharp/ --configuration Release

# Run Twitch Processor
dotnet run --project services/csharp/TwitchProcessor

# Run System Controller
dotnet run --project services/csharp/SystemController

# Testing
dotnet test services/csharp/ --logger "console;verbosity=detailed"

# Publish for deployment
dotnet publish services/csharp/TwitchProcessor -c Release -o ./publish/twitch
dotnet publish services/csharp/SystemController -c Release -o ./publish/system
```

## Integration with Python Services
```csharp
// WebSocket communication to Python AI Engine
public class PythonAIClient
{
    private readonly ClientWebSocket _webSocket;
    private readonly string _pythonAIUrl = "ws://localhost:8001/chat";
    
    public async Task<string> SendChatMessage(ChatMessage message)
    {
        var request = new
        {
            user_id = message.UserId,
            username = message.DisplayName,
            message = message.Message,
            timestamp = DateTime.UtcNow.ToString("O")
        };
        
        var json = JsonConvert.SerializeObject(request);
        await _webSocket.SendAsync(
            Encoding.UTF8.GetBytes(json),
            WebSocketMessageType.Text,
            true,
            CancellationToken.None
        );
        
        // Receive Python AI response
        var buffer = new byte[4096];
        var result = await _webSocket.ReceiveAsync(
            new ArraySegment<byte>(buffer),
            CancellationToken.None
        );
        
        return Encoding.UTF8.GetString(buffer, 0, result.Count);
    }
}
```