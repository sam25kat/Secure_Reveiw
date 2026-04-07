-- Migration: Add email verification to users table
-- Ticket: AUTH-1234
-- Author: dev@company.com

ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL;

CREATE INDEX idx_users_email_verified ON users(email_verified);

ALTER TABLE users DROP COLUMN legacy_auth_token;
