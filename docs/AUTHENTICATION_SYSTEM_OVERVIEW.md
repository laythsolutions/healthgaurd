# Authentication System - Complete Overview

## System Status: ✅ 100% Complete

The HealthGuard authentication system provides multiple authentication methods including JWT, OAuth2, MFA, and API keys for programmatic access.

---

## Features Implemented

### 1. JWT Authentication ✅
- Access tokens (1 hour expiry)
- Refresh tokens (7 day expiry)
- Token rotation
- Custom token claims

### 2. OAuth2 Authentication ✅
- Google OAuth2
- Microsoft Azure AD OAuth2
- Automatic user creation
- Profile picture import

### 3. Password Reset ✅
- Email-based password reset
- Secure token generation
- Token expiration (24 hours)
- Single-use tokens

### 4. Multi-Factor Authentication (MFA) ✅
- TOTP (Time-based One-Time Password)
- QR code setup
- Backup codes (10 codes)
- Trusted device support

### 5. API Key Authentication ✅
- Personal access tokens
- Service accounts
- Scope-based permissions
- IP whitelisting
- Rate limiting support

### 6. Session Management ✅
- Active session tracking
- Session revocation
- Device information
- IP and user agent logging

---

## API Endpoints

### Authentication

```bash
# Login (JWT)
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "password"
}

# Register
POST /api/v1/auth/register/
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "MANAGER",
  "organization": 1
}

# Get current user
GET /api/v1/auth/me/

# Change password (authenticated)
POST /api/v1/auth/change_password/
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

### OAuth2

```bash
# Get OAuth2 authorization URL
GET /api/v1/auth/oauth_url/?provider=google&redirect_uri=http://localhost:3000/auth/callback

# OAuth2 callback
POST /api/v1/auth/oauth_callback/
{
  "provider": "google",
  "code": "authorization_code_from_provider",
  "redirect_uri": "http://localhost:3000/auth/callback"
}
```

### Password Reset

```bash
# Request password reset
POST /api/v1/auth/forgot_password/
{
  "email": "user@example.com"
}

# Verify reset token
POST /api/v1/auth/verify_reset_token/
{
  "token": "reset_token_here"
}

# Reset password
POST /api/v1/auth/reset_password/
{
  "token": "reset_token_here",
  "new_password": "newpassword"
}
```

### Multi-Factor Authentication

```bash
# Get MFA status
GET /api/v1/auth/mfa_status/

# Set up MFA (generate secret and QR code)
POST /api/v1/auth/mfa_setup/

# Verify MFA setup (enroll)
POST /api/v1/auth/mfa_verify_setup/
{
  "token": "123456"  # 6-digit code from authenticator app
}

# Verify MFA during login
POST /api/v1/auth/mfa_verify/
{
  "token": "123456",
  "trust_device": true  # Optional: create trusted device
}

# Disable MFA
POST /api/v1/auth/mfa_disable/
```

### API Keys

```bash
# List API keys
GET /api/v1/auth/api_keys/
Authorization: Bearer YOUR_JWT_TOKEN

# Create API key
POST /api/v1/auth/create_api_key/
{
  "name": "Production API Key",
  "key_type": "PERSONAL",
  "scopes": ["read:restaurants", "read:devices", "read:alerts"],
  "expires_days": 365
}

# Delete API key
DELETE /api/v1/auth/delete_api_key/{id}/
```

### Sessions

```bash
# List active sessions
GET /api/v1/auth/sessions/

# Revoke session
DELETE /api/v1/auth/revoke_session/{id}/
```

---

## Configuration

### Environment Variables

```bash
# OAuth2 - Google
GOOGLE_OAUTH2_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH2_CLIENT_SECRET=your_google_client_secret

# OAuth2 - Microsoft
MICROSOFT_OAUTH2_CLIENT_ID=your_microsoft_client_id
MICROSOFT_OAUTH2_CLIENT_SECRET=your_microsoft_client_secret

# MFA
MFA_ISSUER_NAME=HealthGuard
MFA_REQUIRED_FOR_ADMINS=True

# Password Reset
PASSWORD_RESET_TOKEN_EXPIRY_HOURS=24
SUPPORT_EMAIL=support@healthguard.com
```

### Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `https://your-frontend.com/auth/callback`
5. Copy Client ID and Client Secret

### Microsoft OAuth2 Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new app in Azure AD
3. Add redirect URI: `https://your-frontend.com/auth/callback`
4. Copy Application (client) ID
5. Generate client secret

---

## Models

### User
```python
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+15551234567",
  "role": "MANAGER",
  "organization": 1,
  "profile_image": "https://...",
  "created_at": "2025-02-06T10:00:00Z"
}
```

### MFASettings
```python
{
  "user": 1,
  "is_enabled": true,
  "totp_secret": "JBSWY3DPEHPK3PXP",  # Only during setup
  "verified_at": "2025-02-06T10:00:00Z",
  "last_verified_at": "2025-02-06T11:30:00Z"
}
```

### APIKey
```python
{
  "id": 1,
  "name": "Production Key",
  "key_type": "PERSONAL",
  "key_prefix": "hg_live_abc123...",
  "scopes": ["read:restaurants", "write:alerts"],
  "is_active": true,
  "last_used_at": "2025-02-06T12:00:00Z",
  "expires_at": "2026-02-06T00:00:00Z"
}
```

### BackupCode
```python
{
  "user": 1,
  "code_hash": "sha256_hash_here",  # Not plain text
  "is_used": false,
  "used_at": null
}
```

---

## Authentication Flow

### Standard Login (with MFA)

```
1. POST /auth/login/ (email + password)
   ↓
2. Return JWT tokens + requires_mfa flag
   ↓
3. If requires_mfa:
   POST /auth/mfa_verify/ (totp token)
   ↓
4. Return authenticated session
```

### OAuth2 Login

```
1. GET /auth/oauth_url/ (provider)
   ↓
2. Redirect user to provider (Google/Microsoft)
   ↓
3. User authorizes
   ↓
4. Provider redirects back with code
   ↓
5. POST /auth/oauth_callback/ (code)
   ↓
6. Return JWT tokens
```

### Password Reset Flow

```
1. POST /auth/forgot_password/ (email)
   ↓
2. Send email with reset link
   ↓
3. User clicks link (token in URL)
   ↓
4. POST /auth/reset_password/ (token + new_password)
   ↓
5. Password updated
```

### API Key Authentication

```
Request:
Authorization: Bearer hg_live_abc123...

1. Extract key from header
2. Hash key
3. Lookup in database
4. Check active, not expired, IP whitelist
5. Return user context
```

---

## API Key Scopes

| Scope | Description |
|-------|-------------|
| `read:restaurants` | View restaurant information |
| `write:restaurants` | Create and edit restaurants |
| `read:devices` | View device information |
| `write:devices` | Register and configure devices |
| `read:sensors` | View sensor readings |
| `write:sensors` | Submit sensor readings |
| `read:alerts` | View alerts |
| `write:alerts` | Create and acknowledge alerts |
| `read:reports` | View reports |
| `write:reports` | Generate reports |
| `read:analytics` | View analytics data |
| `read:organization` | View organization details |
| `write:organization` | Edit organization settings |
| `read:users` | View user information |
| `write:users` | Create and edit users |
| `webhook:receive` | Receive webhooks |
| `webhook:send` | Send webhooks |

---

## MFA Setup Process

### User Side

1. Enable MFA via UI
2. Scan QR code with authenticator app
   - Google Authenticator
   - Authy
   - Microsoft Authenticator
   - 1Password
   - LastPass
3. Enter 6-digit code to verify
4. Save backup codes (10 codes)

### Server Side

1. Generate TOTP secret (Base32)
2. Create provisioning URI
3. Generate QR code
4. Verify TOTP token
5. Generate backup codes
6. Enable MFA for user

---

## Security Features

### Password Requirements
- Minimum 8 characters
- No common passwords
- Django validation

### JWT Tokens
- Access token: 1 hour
- Refresh token: 7 days
- Automatic rotation
- Blacklist after rotation

### MFA
- TOTP: 30-second window
- Backup codes: One-time use
- Trusted devices: 30 days

### API Keys
- SHA256 hashed storage
- Only shown during creation
- Configurable expiration
- IP whitelisting
- Scope-based permissions

### Rate Limiting
- Per API key: 60/min, 1000/hour
- Per IP: Configurable
- Failed login tracking

---

## Best Practices

### For Users
1. Enable MFA on all accounts
2. Use a password manager
3. Store backup codes securely
4. Use trusted devices on personal devices only
5. Revoke unused API keys

### For Developers
1. Always use HTTPS
2. Implement rate limiting
3. Log all authentication events
4. Monitor for suspicious activity
5. Use API keys with minimal scopes
6. Rotate API keys regularly

---

## Troubleshooting

### MFA Issues

**Problem:** Can't scan QR code
- **Solution:** Use manual entry with secret key

**Problem:** Lost authenticator device
- **Solution:** Use backup codes or contact admin

**Problem:** Backup codes lost
- **Solution:** Admin can disable MFA temporarily

### OAuth2 Issues

**Problem:** Redirect URI mismatch
- **Solution:** Ensure exact match in provider console

**Problem:** Invalid client credentials
- **Solution:** Regenerate client secret

### API Key Issues

**Problem:** 401 Unauthorized
- **Solution:** Check key is active and not expired

**Problem:** 403 Forbidden
- **Solution:** Check API key has required scopes

---

## Dependencies

```bash
# Install requirements
pip install -r apps/accounts/requirements.txt

# Requirements:
requests==2.31.0          # OAuth2
pyotp==2.9.0             # MFA TOTP
qrcode==7.4.2            # MFA QR codes
```

---

## Database Schema

### Users Table
- Email-based authentication
- Role-based access (ADMIN, MANAGER, STAFF, INSPECTOR)
- Organization membership

### MFA Settings Table
- TOTP secret
- Verification tracking
- Enable/disable flag

### Backup Codes Table
- SHA256 hashed codes
- One-time use tracking

### Trusted Devices Table
- Device tokens
- Expiration tracking

### API Keys Table
- SHA256 hashed keys
- Scope permissions
- Rate limiting config

### Sessions Table
- Session tracking
- Device information
- IP and user agent

### Password Reset Tokens Table
- Secure tokens
- Expiration tracking

---

**Status: Production Ready** ✅

All authentication features implemented and tested. Ready for deployment.
