-- VOID AI Assistant — PostgreSQL Setup Script
-- Run this in the target database as a superuser or database owner.

-- Connect to the application database first.
-- Example in psql: \c void

GRANT USAGE, CREATE ON SCHEMA public TO void_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO void_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO void_user;

-- Optional, but useful when the schema was created by another role.
ALTER SCHEMA public OWNER TO postgres;

-- If the user should fully manage existing objects too, keep these grants.
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO void_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO void_user;