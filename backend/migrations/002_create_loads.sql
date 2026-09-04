CREATE TABLE loads(id BIGSERIAL PRIMARY KEY,
origin TEXT NOT NULL,
destination TEXT NOT NULL,
pickup_date TIMESTAMPTZ NOT NULL,
weight NUMERIC(8, 2) NOT NULL,
assigned_driver_id BIGINT REFERENCES users(id),
rate numeric(8, 2) NOT NULL,
status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new', 'assigned', 'in_transit', 'delivered')),
updated_at TIMESTAMPTZ,
created_by BIGINT NOT NULL REFERENCES users(id),
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
assigned_by BIGINT REFERENCES users(id) 
);