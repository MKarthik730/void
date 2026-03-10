-- ═══════════════════════════════════════════════
--   VOID AI Assistant — PostgreSQL Setup Script
--   Run this once before starting the backend
-- ═══════════════════════════════════════════════

-- Step 1: Connect as postgres superuser
-- psql -U postgres

-- Step 2: Create user and database
CREATE USER void_user WITH PASSWORD 'void_password';
CREATE DATABASE void_db OWNER void_user;

-- Step 3: Connect to void_db
-- \c void_db

-- Step 4: Grant privileges
GRANT ALL PRIVILEGES ON DATABASE void_db TO void_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO void_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO void_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO void_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO void_user;

-- Tables are auto-created by SQLAlchemy when backend starts
-- To verify after first run:
-- \dt

-- Expected tables:
-- action_logs   — every VOID action logged
-- screenshots   — saved screenshot metadata
-- voice_logs    — voice transcription history
-- meeting_logs  — meeting summaries and action items
