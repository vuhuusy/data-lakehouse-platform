CREATE DATABASE financial_ops;

\connect financial_ops;

CREATE SCHEMA core;

-- 1. Customer table
CREATE TABLE core.customer (
    id VARCHAR(50) PRIMARY KEY,
    ssn VARCHAR(50),
    cc_num VARCHAR(50),
    first VARCHAR(50),
    last VARCHAR(50),
    gender VARCHAR(10),
    street TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip VARCHAR(10),
    lat FLOAT,
    lon FLOAT,
    job VARCHAR(100),
    dob VARCHAR(10),
    acct_num VARCHAR(50),
    area_type VARCHAR(50)
);

-- 2. Merchant table
CREATE TABLE core.merchant (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(100)
);

-- 3. Transaction table
CREATE TABLE core.transaction (
    id VARCHAR(50) PRIMARY KEY,
    date VARCHAR(10),
    time VARCHAR(8),
    amt FLOAT,
    lat FLOAT,
    lon FLOAT,
    customer_id VARCHAR(50),
    merchant_id VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES core.customer(id),
    FOREIGN KEY (merchant_id) REFERENCES core.merchant(id)
);

-- insert data into tables --
COPY core.customer FROM '/workdir/customers.csv' DELIMITER '|' CSV HEADER;
COPY core.merchant FROM '/workdir/merchants.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions.csv' DELIMITER '|' CSV HEADER;