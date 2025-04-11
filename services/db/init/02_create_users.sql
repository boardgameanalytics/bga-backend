\c boardgameanalytics_db

-- Create users
CREATE USER bga_user WITH LOGIN;
CREATE USER bga_pipeline WITH LOGIN;

-- Grant basic privileges to both users
GRANT CONNECT ON DATABASE boardgameanalytics_db TO bga_user, bga_pipeline;
GRANT USAGE ON SCHEMA public TO bga_user, bga_pipeline;

-- Grant specific privileges for each user
-- Read-only user: SELECT only
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bga_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bga_user;

-- Read-write user: ALL PRIVILEGES on tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bga_pipeline;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO bga_pipeline;

-- Allow read-write user to create objects in the schema
GRANT CREATE ON SCHEMA public TO bga_pipeline;
