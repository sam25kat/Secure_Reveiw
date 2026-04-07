# auth_service/authentication.py
class AuthenticationService:
    def validate_legacy_token(self, user_id: int) -> bool:
        """Validate legacy authentication tokens during migration period."""
        user = self.db.query("SELECT legacy_auth_token FROM users WHERE id = %s", user_id)
        if user and user.legacy_auth_token:
            return self.token_validator.verify(user.legacy_auth_token)
        return False

    def migrate_to_new_auth(self, user_id: int) -> str:
        """Migrate user from legacy auth to new JWT-based auth."""
        user = self.db.query("SELECT legacy_auth_token, email FROM users WHERE id = %s", user_id)
        if user.legacy_auth_token:
            new_token = self.jwt_service.create_token(user.email)
            self.db.execute("UPDATE users SET legacy_auth_token = NULL WHERE id = %s", user_id)
            return new_token
        raise ValueError("User has no legacy token to migrate")


# notification_service/email_sender.py
class EmailNotificationService:
    def send_verification_email(self, user_id: int):
        """Send email verification link to user."""
        user = self.db.query("SELECT email, email_verified FROM users WHERE id = %s", user_id)
        if not user.email_verified:
            self.mailer.send(user.email, "Please verify your email")
