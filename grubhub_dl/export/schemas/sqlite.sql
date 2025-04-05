--
-- TABLES
--

CREATE TABLE IF NOT EXISTS emails
(
    email_id    TEXT,
    subject     TEXT,
    sent_by     TEXT,
    sent_at     TEXT, -- ISO8601 timestamp
    body        TEXT,
    category    TEXT
);

CREATE TABLE IF NOT EXISTS credits
(
    email_id    TEXT,
    amount      TEXT, -- USD in cents
    code        TEXT,
    expires     TEXT, -- ISO8601 timestamp
    category    TEXT
);

CREATE TABLE IF NOT EXISTS orders
(
    email_id                TEXT,
    ordered_at              TEXT, -- ISO8601 timestamp
    restaurant_name         TEXT,
    restaurant_phone        TEXT,
    order_number            TEXT,
    order_subtotal          TEXT, -- USD in cents
    order_service_fee       TEXT, -- USD in cents
    order_delivery_fee      TEXT, -- USD in cents
    order_sales_tax         TEXT, -- USD in cents
    order_delivery_tip      TEXT, -- USD in cents
    order_total             TEXT, -- USD in cents
    order_payment_method    TEXT
);

CREATE TABLE IF NOT EXISTS order_updates
(
    email_id            TEXT,
    order_number        TEXT,
    refund_amount       TEXT, -- USD in cents
    refund_item         TEXT,
    refund_reason       TEXT,
    refund_item_amount  TEXT, -- USD in cents
    refund_fees_amount  TEXT, -- USD in cents
    tip_adjusted_amount TEXT
);

CREATE TABLE IF NOT EXISTS order_cancellations
(
    email_id        TEXT,
    order_number    TEXT,
    amount          TEXT, -- USD in cents
    reason          TEXT
);


CREATE TABLE IF NOT EXISTS order_items
(

);

--
-- VIEWS
--

CREATE VIEW IF NOT EXISTS vw_orders
(

);

CREATE VIEW IF NOT EXISTS vw_credits
(

);

CREATE VIEW IF NOT EXISTS vw_emails_not_processed
(

);

CREATE VIEW IF NOT EXISTS vw_order_cancellations_no_order_number
(

);

CREATE VIEW IF NOT EXISTS vw_order_updates_no_order_number
(

);

CREATE VIEW IF NOT EXISTS vw_order_items_no_order_number
(

);
