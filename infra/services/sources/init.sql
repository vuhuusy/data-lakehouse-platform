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
-- May: from day 1 to day 31
COPY core.transaction FROM '/workdir/transactions_2024-05-01.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-02.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-03.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-04.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-05.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-06.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-07.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-08.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-09.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-10.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-11.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-12.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-13.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-14.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-15.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-16.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-17.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-18.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-19.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-20.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-21.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-22.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-23.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-24.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-25.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-26.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-27.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-28.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-29.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-30.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-05-31.csv' DELIMITER '|' CSV HEADER;

-- Tháng 6: từ ngày 1 đến 12
COPY core.transaction FROM '/workdir/transactions_2024-06-01.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-02.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-03.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-04.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-05.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-06.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-07.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-08.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-09.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-10.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-11.csv' DELIMITER '|' CSV HEADER;
COPY core.transaction FROM '/workdir/transactions_2024-06-12.csv' DELIMITER '|' CSV HEADER;
