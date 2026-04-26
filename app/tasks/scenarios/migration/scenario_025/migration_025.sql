-- Migration: address connection storms by increasing max_connections
-- Ticket: PLATFORM-9912
-- (This is a config migration applied via ALTER SYSTEM)

ALTER SYSTEM SET max_connections = 12000;

ALTER SYSTEM SET shared_buffers = '32GB';

ALTER SYSTEM SET work_mem = '256MB';

SELECT pg_reload_conf();
