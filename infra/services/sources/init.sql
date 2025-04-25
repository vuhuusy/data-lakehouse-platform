CREATE DATABASE financial_ops;

\connect financial_ops;

CREATE SCHEMA core;

-- 1. mcc table
CREATE TABLE core.mcc (
    code VARCHAR(10) PRIMARY KEY,
    descriptions TEXT NOT NULL
);

-- 2. user table
CREATE TABLE core.user_account (
    id BIGINT PRIMARY KEY,
    retirement_age INT NOT NULL,
    birth_year INT NOT NULL,
    birth_month INT NOT NULL,
    gender VARCHAR(10),
    address TEXT,
    latitude FLOAT,
    longitude FLOAT,
    per_capita_income VARCHAR(50),
    yearly_income VARCHAR(50),
    total_debt VARCHAR(50),
    credit_score INT,
    num_credit_cards INT
);

-- 3. card table
CREATE TABLE core.card (
    id BIGINT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    card_brand VARCHAR(50),
    card_type VARCHAR(50),
    card_number BIGINT,
    expires VARCHAR(10),
    cvv INT,
    has_chip BOOLEAN,
    num_cards_issued INT,
    credit_limit VARCHAR(50),
    acct_open_date VARCHAR(20),
    year_pin_last_changed INT,
    card_on_dark_web BOOLEAN,
    FOREIGN KEY (client_id) REFERENCES core.user_account(id)
);

-- 4. merchant table
CREATE TABLE core.merchant (
    key VARCHAR(10) PRIMARY KEY,    
    id BIGINT,
    city VARCHAR(100),
    state VARCHAR(100),
    zip VARCHAR(20),
    mcc_code VARCHAR(10),
    FOREIGN KEY (mcc_code) REFERENCES core.mcc(code)
);

-- 5. transaction table
CREATE TABLE core.transaction (
    id BIGINT PRIMARY KEY,
    date TIMESTAMP,
    card_id BIGINT,
    amount NUMERIC,
    use_chip BOOLEAN,
    merchant_key VARCHAR(10),
    errors TEXT,
    FOREIGN KEY (card_id) REFERENCES core.card(id),
    FOREIGN KEY (merchant_key) REFERENCES core.merchant(key)
);

-- insert data into tables --
COPY core.mcc FROM '/workdir/mcc.csv' DELIMITER ',' CSV HEADER;
COPY core.merchant FROM '/workdir/merchant.csv' DELIMITER ',' CSV HEADER;
COPY core.user_account FROM '/workdir/user.csv' DELIMITER ',' CSV HEADER;
COPY core.card FROM '/workdir/card.csv' DELIMITER ',' CSV HEADER;