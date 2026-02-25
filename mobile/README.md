# HealthGuard Mobile App

Cross-platform mobile app for restaurant staff to monitor compliance, receive alerts, and log manual checks.

## Features

- **Offline-First Architecture**: Works completely without internet
- **Real-Time Sensor Monitoring**: Connects to local gateway via WiFi
- **Critical Alerts**: Push notifications for temperature violations
- **Manual Logging**: Quick temperature and compliance logging
- **Historical Data**: View 7-30 days of sensor history
- **Multi-Restaurant Support**: Switch between locations

## Architecture

```
┌─────────────────────────────────────────┐
│         Flutter Mobile App              │
├─────────────────────────────────────────┤
│  MQTT Manager (Offline-First)           │
│  ├─ Local Gateway Connection            │
│  ├─ Cloud Fallback                      │
│  └─ Offline Buffering                   │
├─────────────────────────────────────────┤
│  Local SQLite Database                  │
│  └─ 7-30 day buffer                     │
├─────────────────────────────────────────┤
│  Riverpod State Management              │
│  └─ Reactive UI                         │
└─────────────────────────────────────────┘
```

## Getting Started

```bash
# Install dependencies
flutter pub get

# Run on device
flutter run

# Build APK
flutter build apk --release
```

## Configuration

Create `lib/core/config/env.dart`:

```dart
class Env {
  static const String apiBaseUrl = 'https://api.healthguard.com';
  static const String cloudMqttHost = 'mqtt.healthguard.com';
}
```

## Screens

- **Login**: Authenticate user
- **Dashboard**: Overview of all sensors and alerts
- **Sensors**: Detailed sensor readings and history
- **Alerts**: Active and historical alerts
- **Logs**: Manual compliance logging
- **Settings**: App configuration
