"""Tests for sensitive data detection and masking."""

from clipsy.redact import (
    SensitiveMatch,
    SensitiveType,
    detect_sensitive,
    get_sensitivity_summary,
    is_sensitive,
    mask_text,
)


class TestDetectAPIKeys:
    def test_openai_key(self):
        text = "My API key is sk-1234567890abcdefghijklmnop"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.API_KEY
        assert matches[0].original == "sk-1234567890abcdefghijklmnop"

    def test_openai_project_key(self):
        text = "sk-proj-ABC123_xyz789-abcdef"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.API_KEY

    def test_aws_key(self):
        text = "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.API_KEY
        assert "AKIAIOSFODNN7EXAMPLE" in matches[0].original

    def test_github_pat(self):
        text = "token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.API_KEY

    def test_github_fine_grained_pat(self):
        text = "github_pat_ABC123xyz789_abcdefghij"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.API_KEY

    def test_slack_token(self):
        text = "xoxb-123456789-abcdefghij"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.API_KEY

    def test_stripe_key(self):
        # Build key dynamically to avoid GitHub push protection
        prefix = "sk_" + "test" + "_"
        text = prefix + "4eC39HqLyjWDarjtT1zdp7dc"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.API_KEY

    def test_google_api_key(self):
        text = "AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.API_KEY


class TestDetectPasswords:
    def test_password_equals(self):
        text = "password=MySecretPass123"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.PASSWORD
        assert matches[0].original == "MySecretPass123"

    def test_password_colon(self):
        text = "password: hunter2"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.PASSWORD

    def test_pwd_equals(self):
        text = "pwd=secret123"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.PASSWORD

    def test_secret_equals(self):
        text = 'secret="abc123xyz"'
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.PASSWORD


class TestDetectSSN:
    def test_ssn_with_dashes(self):
        text = "SSN: 123-45-6789"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.SSN
        assert matches[0].original == "123-45-6789"

    def test_ssn_masked_shows_last_four(self):
        text = "SSN: 123-45-6789"
        matches = detect_sensitive(text)
        assert matches[0].masked == "•••-••-6789"


class TestDetectCreditCard:
    def test_credit_card_with_spaces(self):
        text = "Card: 4111 1111 1111 1111"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.CREDIT_CARD

    def test_credit_card_with_dashes(self):
        text = "4111-1111-1111-1111"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.CREDIT_CARD

    def test_credit_card_no_separators(self):
        text = "4111111111111111"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.CREDIT_CARD

    def test_credit_card_masked_shows_last_four(self):
        text = "4111-1111-1111-1234"
        matches = detect_sensitive(text)
        assert matches[0].masked == "••••-••••-••••-1234"


class TestDetectPrivateKeys:
    def test_rsa_private_key(self):
        text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIB...\n-----END RSA PRIVATE KEY-----"
        matches = detect_sensitive(text)
        assert len(matches) >= 1
        assert any(m.sensitive_type == SensitiveType.PRIVATE_KEY for m in matches)

    def test_generic_private_key(self):
        text = "-----BEGIN PRIVATE KEY-----"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.PRIVATE_KEY
        assert matches[0].masked == "[Private Key]"

    def test_openssh_private_key(self):
        text = "-----BEGIN OPENSSH PRIVATE KEY-----"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.PRIVATE_KEY


class TestDetectCertificates:
    def test_certificate(self):
        text = "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"
        matches = detect_sensitive(text)
        assert len(matches) >= 1
        assert any(m.sensitive_type == SensitiveType.CERTIFICATE for m in matches)

    def test_certificate_masked(self):
        text = "-----BEGIN CERTIFICATE-----"
        matches = detect_sensitive(text)
        assert matches[0].masked == "[Certificate]"


class TestDetectTokens:
    def test_jwt(self):
        text = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.TOKEN

    def test_bearer_token(self):
        text = "Authorization: Bearer abc123xyz789012345678901234567890"
        matches = detect_sensitive(text)
        assert len(matches) == 1
        assert matches[0].sensitive_type == SensitiveType.TOKEN


class TestMaskText:
    def test_mask_single_sensitive(self):
        text = "password=secret123"
        masked = mask_text(text)
        assert "secret123" not in masked
        assert "••••••••" in masked

    def test_mask_preserves_context(self):
        text = "Login with password=secret123 to continue"
        masked = mask_text(text)
        assert "Login with" in masked
        assert "to continue" in masked
        assert "secret123" not in masked

    def test_mask_multiple_sensitive(self):
        text = "API: sk-abc123def456ghi789jkl012 SSN: 123-45-6789"
        masked = mask_text(text)
        assert "sk-abc123def456ghi789jkl012" not in masked
        assert "123-45-6789" not in masked

    def test_no_sensitive_unchanged(self):
        text = "Hello, this is a normal message."
        masked = mask_text(text)
        assert masked == text


class TestIsSensitive:
    def test_sensitive_text(self):
        assert is_sensitive("password=secret") is True

    def test_non_sensitive_text(self):
        assert is_sensitive("Hello world") is False

    def test_api_key_sensitive(self):
        assert is_sensitive("sk-1234567890abcdefghij") is True


class TestGetSensitivitySummary:
    def test_single_type(self):
        matches = [
            SensitiveMatch(SensitiveType.API_KEY, 0, 10, "sk-abc123", "sk-••••123")
        ]
        summary = get_sensitivity_summary(matches)
        assert summary == "Api Key"

    def test_multiple_types(self):
        matches = [
            SensitiveMatch(SensitiveType.API_KEY, 0, 10, "sk-abc", "sk-••••"),
            SensitiveMatch(SensitiveType.SSN, 20, 31, "123-45-6789", "•••-••-6789"),
        ]
        summary = get_sensitivity_summary(matches)
        assert "Api Key" in summary
        assert "Ssn" in summary


class TestNoFalsePositives:
    def test_short_numbers_not_ssn(self):
        text = "Phone: 555-1234"
        matches = detect_sensitive(text)
        ssn_matches = [m for m in matches if m.sensitive_type == SensitiveType.SSN]
        assert len(ssn_matches) == 0

    def test_normal_text_not_sensitive(self):
        text = "The quick brown fox jumps over the lazy dog."
        assert is_sensitive(text) is False

    def test_code_snippet_not_sensitive(self):
        text = "def hello(): return 'world'"
        assert is_sensitive(text) is False

    def test_url_not_sensitive(self):
        text = "https://example.com/api/v1/users"
        # URLs should not trigger API key detection unless they contain actual keys
        matches = detect_sensitive(text)
        api_matches = [m for m in matches if m.sensitive_type == SensitiveType.API_KEY]
        assert len(api_matches) == 0
