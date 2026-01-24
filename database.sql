-- ================================
-- POST OFFICE ACCOUNT SYSTEM DB
-- CIF = 9 digits
-- ================================

DROP DATABASE IF EXISTS post_office;
CREATE DATABASE post_office;
USE post_office;

-- ================================
-- 1) USERS TABLE (LOGIN)
-- ================================
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password_hash VARCHAR(64) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'CLERK',
    status VARCHAR(10) NOT NULL DEFAULT 'ACTIVE'
);

-- Default admin user:
-- Username: postmaster
-- Password: 1234
INSERT INTO users(username, password_hash, role, status)
VALUES ('postmaster', SHA2('1234',256), 'POSTMASTER', 'ACTIVE');


-- ================================
-- 2) CUSTOMERS TABLE (CIF SYSTEM)
-- CIF = 9 digits (VARCHAR(9))
-- Aadhaar unique
-- ================================
CREATE TABLE customers (
    customer_id VARCHAR(9) PRIMARY KEY,
    aadhaar VARCHAR(12) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    mobile VARCHAR(10) NOT NULL
);

-- Index for faster searching
CREATE INDEX idx_customer_name ON customers(name);
CREATE INDEX idx_customer_mobile ON customers(mobile);


-- ================================
-- 3) ACCOUNTS TABLE
-- Account number = 12 digits
-- SB = 010xxxxxxxxx
-- RD = 020xxxxxxxxx
-- TD = 030xxxxxxxxx
-- ================================
CREATE TABLE accounts (
    acc_no VARCHAR(12) PRIMARY KEY,
    customer_id VARCHAR(9) NOT NULL,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    mobile VARCHAR(10) NOT NULL,
    acc_type ENUM('SB','RD','TD') NOT NULL,
    balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status ENUM('Active','Closed') DEFAULT 'Active',

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE CASCADE
);

-- ✅ One active SB account per customer rule
-- (One customer cannot have multiple SB accounts)
CREATE UNIQUE INDEX unique_sb_per_customer
ON accounts(customer_id, acc_type);

-- Index for faster lookup
CREATE INDEX idx_accounts_mobile ON accounts(mobile);
CREATE INDEX idx_accounts_type ON accounts(acc_type);
CREATE INDEX idx_accounts_status ON accounts(status);


-- ================================
-- 4) RD DETAILS TABLE
-- Only for RD accounts
-- ================================
CREATE TABLE rd_details (
    acc_no VARCHAR(12) PRIMARY KEY,
    monthly_amount DECIMAL(10,2) NOT NULL,
    months_completed INT DEFAULT 0,

    CONSTRAINT fk_rd_acc
        FOREIGN KEY (acc_no)
        REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);

-- ================================
-- 5) TRANSACTIONS TABLE
-- Tracks deposit/withdraw/rd installments/interest etc.
-- ================================
CREATE TABLE transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_no VARCHAR(12) NOT NULL,
    txn_type VARCHAR(30) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    txn_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_txn_acc
        FOREIGN KEY (acc_no)
        REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);

CREATE INDEX idx_txn_acc ON transactions(acc_no);
CREATE INDEX idx_txn_type ON transactions(txn_type);
CREATE INDEX idx_txn_date ON transactions(txn_date);

-- ================================
-- ✅ END OF DATABASE SCRIPT
-- ================================
