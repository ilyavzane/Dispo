CREATE TABLE users(id BIGSERIAL PRIMARY KEY, 
name TEXT NOT NULL,
email VARCHAR(254) NOT NULL UNIQUE,
password_hash TEXT NOT NULL,
role VARCHAR(12) NOT NULL CHECK (role IN ('admin', 'driver', 'dispatcher')),
status VARCHAR(12) NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
created_at TIMESTAMPTZ NOT NULL DEFAULT now());