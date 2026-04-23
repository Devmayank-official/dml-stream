# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.5.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of DML Stream seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Email**: devmayank.inbox@gmail.com
- **Subject**: [Security] DML Stream Vulnerability Report

### What to Include

Please include the following information in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)
- Your contact information for follow-up

### Response Time

We will acknowledge receipt of your report within **48 hours** and will send you a more detailed response within **5 business days** indicating the next steps in handling your report.

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version of DML Stream
2. **FFmpeg Security**: Only download FFmpeg from official sources
3. **Configuration**: Never commit configuration files with sensitive data
4. **Network**: Use trusted networks when downloading content

### For Contributors

1. **Dependencies**: Keep dependencies up to date
2. **Secrets**: Never commit secrets or API keys
3. **Input Validation**: Always validate user input
4. **Error Handling**: Don't expose sensitive information in error messages

## Security Features

### Implemented Security Measures

- **No Hardcoded Secrets**: All credentials must come from environment or config
- **Input Validation**: URLs and paths are validated before use
- **Secure Defaults**: Conservative security settings by default
- **Dependency Scanning**: Automated vulnerability scanning via Dependabot
- **Code Analysis**: Static analysis via Bandit and CodeQL

### Security Scanning

We perform regular security scans:

- **Weekly**: Dependabot dependency checks
- **Weekly**: Bandit security linter
- **Weekly**: Safety vulnerability scanner
- **On PR**: CodeQL static analysis

## Known Limitations

1. **YouTube API**: DML Stream relies on YouTube's public interface. Changes to YouTube's API or Terms of Service may affect functionality.

2. **Age-Restricted Content**: Age-restricted videos require authentication, which is not currently supported.

3. **Region-Locked Content**: Some content may not be available in certain regions.

## Security Updates

Security updates are released as patch versions (e.g., 2.5.1, 2.5.2) and are announced via:

- GitHub Releases
- PyPI changelog
- Security advisory (for significant issues)

## Responsible Disclosure

We follow a responsible disclosure policy:

1. Reporter submits vulnerability
2. We investigate and develop fix
3. Fix is released
4. Vulnerability is publicly disclosed (with credit if desired)

## Contact

For security-related questions:
- **Email**: devmayank.inbox@gmail.com

---

**Thank you for helping keep DML Stream and our users safe!**
