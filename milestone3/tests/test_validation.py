"""
Unit Tests for Form Validation, Localhost Startup Guard, and SQL Injection Sanitization
Does not require network access; validates client and server-side security rules.
"""
import unittest
from datetime import date, timedelta
from milestone3.app.services.user_service import validate_user_input
from milestone3.app.db import verify_remote_host, FORBIDDEN_LOCAL_HOSTS

class TestValidationAndSecurity(unittest.TestCase):

    def test_localhost_guard_rejects_local_hosts(self):
        """Verifies that the startup guard strictly refuses localhost and loopback interfaces."""
        for local_host in FORBIDDEN_LOCAL_HOSTS:
            import os
            os.environ["DB_HOST"] = local_host
            os.environ["ALLOW_LOCAL_DEV"] = "false"
            with self.assertRaises(ConnectionRefusedError):
                verify_remote_host(allow_local=False)

    def test_localhost_guard_accepts_remote_hosts(self):
        """Verifies that valid remote host addresses pass the startup guard."""
        import os
        os.environ["DB_HOST"] = "db4free.net"
        os.environ["ALLOW_LOCAL_DEV"] = "false"
        host = verify_remote_host(allow_local=False)
        self.assertEqual(host, "db4free.net")

    def test_registration_validation_invalid_email(self):
        """Rejects malformed emails."""
        errors, _, _, _, _ = validate_user_input("valid_user", "not-an-email", "male", "1995-05-15", [1])
        self.assertTrue(any("valid email" in e for e in errors))

    def test_registration_validation_future_birthdate(self):
        """Rejects birthdates occurring in the future."""
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        errors, _, _, _, _ = validate_user_input("valid_user", "user@example.com", "female", tomorrow, [1])
        self.assertTrue(any("past date" in e for e in errors))

    def test_registration_validation_no_focus_areas(self):
        """Rejects registration without at least one focus area."""
        errors, _, _, _, _ = validate_user_input("valid_user", "user@example.com", "other", "1990-01-01", [])
        self.assertTrue(any("area of focus" in e for e in errors))

    def test_registration_validation_short_username(self):
        """Rejects usernames shorter than 3 characters."""
        errors, _, _, _, _ = validate_user_input("ab", "user@example.com", "male", "1990-01-01", [1])
        self.assertTrue(any("Username must be between" in e for e in errors))

    def test_sql_injection_treated_as_plain_text(self):
        """Verifies that malicious SQL injection inputs are kept as literals and do not break validation."""
        sql_injection_payload = "' OR 1=1 --; DROP TABLE property; --"
        errors, clean_username, _, _, _ = validate_user_input(
            sql_injection_payload, "test@example.com", "male", "1992-04-10", [1]
        )
        self.assertEqual(errors, [])
        self.assertEqual(clean_username, sql_injection_payload)

if __name__ == "__main__":
    unittest.main()
