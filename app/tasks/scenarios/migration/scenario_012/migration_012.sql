-- Migration: optimize the notification feed query
-- Common query: SELECT id, title, created_at FROM notifications
--               WHERE user_id = ? AND is_read = false
--               ORDER BY created_at DESC LIMIT 50;
-- Ticket: NOTIF-981

CREATE INDEX idx_notif_feed ON notifications(created_at DESC, user_id, is_read);

DROP INDEX idx_notif_user;
