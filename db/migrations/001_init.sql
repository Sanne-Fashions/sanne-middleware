-- Initial schema for sanne-middleware. Run against sanne_staging first, then sanne_prod.

CREATE TABLE IF NOT EXISTS products (
  product_id   text PRIMARY KEY,
  name         text NOT NULL,
  shopify_id   text UNIQUE,
  odoo_id      text UNIQUE,
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS size_charts (
  id            bigserial PRIMARY KEY,
  product_id    text NOT NULL REFERENCES products(product_id),
  size          text NOT NULL,
  measure       text NOT NULL,
  target_cm     numeric(6,2) NOT NULL,
  tolerance_cm  numeric(6,2) NOT NULL,
  UNIQUE (product_id, size, measure)
);

CREATE TABLE IF NOT EXISTS orders (
  shopify_order_id  text PRIMARY KEY,
  status            text NOT NULL DEFAULT 'received',
  odoo_order_id     text UNIQUE,
  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS measurements (
  id                 bigserial PRIMARY KEY,
  shopify_order_id   text NOT NULL REFERENCES orders(shopify_order_id),
  product_id         text NOT NULL REFERENCES products(product_id),
  values_cm          jsonb NOT NULL,
  captured_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sizing_results (
  id                 bigserial PRIMARY KEY,
  shopify_order_id   text NOT NULL REFERENCES orders(shopify_order_id),
  base_size          text NOT NULL,
  decision           text NOT NULL CHECK (decision IN ('standard', 'alteration', 'custom')),
  alterations_cm     jsonb NOT NULL DEFAULT '{}'::jsonb,
  notes              text[] NOT NULL DEFAULT '{}',
  created_at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dxf_files (
  id                 bigserial PRIMARY KEY,
  shopify_order_id   text REFERENCES orders(shopify_order_id),
  blob_name          text NOT NULL UNIQUE,
  sha256             text NOT NULL,
  kind               text NOT NULL CHECK (kind IN ('base', 'generated')),
  created_at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approvals (
  id                 bigserial PRIMARY KEY,
  shopify_order_id   text NOT NULL REFERENCES orders(shopify_order_id),
  checker            text NOT NULL,
  decision           text NOT NULL CHECK (decision IN ('approved', 'rejected')),
  reason             text,
  decided_at         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS size_charts_product_idx ON size_charts(product_id);
