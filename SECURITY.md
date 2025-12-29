# Security Policy

## Overview

Dōsatsu takes security seriously. This document outlines our security practices and how to report vulnerabilities.

---

## 🔐 Handling API Credentials

### Never Commit Credentials

**DO NOT** commit the following to git:
- API keys
- Client IDs
- Client secrets
- Access tokens
- `.env` files
- `.streamlit/secrets.toml`

### How Dōsatsu Handles Credentials

Dōsatsu uses environment variables for all sensitive data:

#### For Command-Line Scripts:
```bash
# Set environment variables
export SPOTIFY_CLIENT_ID='your_client_id_here'
export SPOTIFY_CLIENT_SECRET='your_client_secret_here'

# Or use a .env file (gitignored)
cp .env.example .env
# Edit .env with your credentials
```

#### For Streamlit Dashboard:
```toml
# .streamlit/secrets.toml (gitignored)
SPOTIFY_CLIENT_ID = "your_client_id_here"
SPOTIFY_CLIENT_SECRET = "your_client_secret_here"
```

---

## 🛡️ Current Security Measures

### 1. Gitignore Protection
Our `.gitignore` file excludes:
- `.env` and all `.env.*` files
- `.streamlit/secrets.toml`
- API key files
- Credential caches

### 2. Environment Variables
All API credentials are loaded from environment variables:
```python
import os
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
```

### 3. No Hardcoded Credentials
Code is designed to **fail fast** if credentials are missing:
```python
if not client_id or not client_secret:
    print("❌ ERROR: Spotify credentials not found!")
    sys.exit(1)
```

### 4. Secure Dependencies
- All dependencies from PyPI (trusted sources)
- Regular dependency updates recommended
- No executable downloads from untrusted sources

---

## 🚨 What to Do If You Accidentally Commit Credentials

### Immediate Actions:

1. **Revoke the exposed credentials immediately**
   - For Spotify: https://developer.spotify.com/dashboard
   - Click your app → Settings → Revoke Secret

2. **Remove from git history**
   ```bash
   # Remove file from all commits
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/secrets/file" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push
   git push --force --all
   ```

3. **Generate new credentials**
   - Create new API keys
   - Update your local `.env` file
   - Test that everything still works

4. **Notify maintainers**
   - Open an issue (do NOT include the exposed credentials)
   - Mention that credentials were accidentally exposed

---

## 🔍 Security Checklist for Contributors

Before committing code:

- [ ] No hardcoded API keys, passwords, or tokens
- [ ] No `.env` or `secrets.toml` files staged
- [ ] All new credential usage follows environment variable pattern
- [ ] Added new sensitive files to `.gitignore` if needed
- [ ] Tested code with environment variables (not hardcoded values)
- [ ] Reviewed `git diff` for accidental credential inclusion

---

## 📊 API Credential Scope

### Spotify API
- **Scope**: Read-only access to artist data
- **Risk Level**: Low (no write access, no user data)
- **Rate Limits**:
  - Free tier: ~180 requests/minute
  - Sufficient for Dōsatsu usage
- **What it CAN'T do**:
  - Access your Spotify account
  - Modify playlists
  - Access listening history
  - Charge you money

### MusicBrainz API
- **Authentication**: None required (public API)
- **Scope**: Read-only access to music metadata
- **Rate Limits**: 1 request/second (respected by our code)
- **Risk Level**: None (no credentials needed)

---

## 🐛 Reporting Security Vulnerabilities

### If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. **DO** email the maintainer privately
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

### What qualifies as a security issue:

- ✅ Exposed credentials in code
- ✅ Insecure credential storage
- ✅ Dependency vulnerabilities (CVEs)
- ✅ Code injection vulnerabilities
- ✅ Unauthorized data access

### What doesn't qualify:

- ❌ Feature requests
- ❌ Performance issues
- ❌ Documentation errors
- ❌ Rate limiting (API quotas)

---

## 🔄 Dependency Security

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all packages (test carefully)
pip install --upgrade -r requirements.txt
```

### Known Safe Dependencies

Dōsatsu uses well-maintained packages:
- `streamlit` - Official Streamlit package
- `pandas` - NumFOCUS project
- `plotly` - Plotly Technologies
- `requests` - Python Software Foundation

---

## 📚 Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Spotify API Security Best Practices](https://developer.spotify.com/documentation/web-api/concepts/api-calls)

---

## ✅ Security Best Practices Summary

1. **Never commit credentials** - Use environment variables
2. **Use `.gitignore`** - Exclude all sensitive files
3. **Fail fast** - Exit if credentials are missing
4. **Rotate credentials** - Change them if exposed
5. **Minimal scope** - Use read-only API access when possible
6. **Regular updates** - Keep dependencies current
7. **Report responsibly** - Contact maintainers privately

---

**Questions about security?** Open an issue (without sensitive data) or contact the maintainer.

**Found a vulnerability?** Report it privately to protect users.

---

**Last updated:** December 28, 2025
