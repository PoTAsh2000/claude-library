---
description: Security standards that apply to all code. Covers secrets management, input validation, SQL injection prevention, data exposure, and transport security.
alwaysApply: true
---

# Security Standards

- Never hardcode secrets, API keys, passwords, or tokens in source code. Use environment variables, config files excluded from version control, or a secrets manager.
- Validate and sanitize all user input at the system boundary (controller/handler layer). Never trust client-side validation alone.
- Use parameterized queries or ORM methods for all database operations. Never concatenate user input into SQL, JPQL, HQL, or any query string.
- Never concatenate user input into shell commands, system calls, or file paths. Use framework-provided APIs for process execution and file operations.
- Apply the principle of least privilege: request minimum permissions, expose minimum data. API responses should return only the fields the consumer needs.
- Never log PII (names, emails, addresses, phone numbers), credentials, session tokens, or payment data. Mask or redact sensitive fields in logs.
- Enforce HTTPS for all external communication. Validate TLS certificates. Do not disable certificate verification, even in development.
- Set security headers on HTTP responses: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`.
- Hash passwords with a strong algorithm (bcrypt, scrypt, Argon2). Never store passwords in plaintext or use weak hashing (MD5, SHA-1).
- Audit dependencies for known CVEs before adding them. Run dependency audit checks (`npm audit`, `mvn dependency:tree`, `cargo audit`) regularly.
- Sanitize and escape output to prevent XSS. Use the framework's built-in escaping mechanisms — do not write manual HTML escaping.
- Implement CSRF protection for state-changing operations in web applications that use cookies for authentication.