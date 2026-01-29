DROP DATABASE IF EXISTS post_office;
CREATE DATABASE post_office;
USE post_office;

-- ==========================
-- 1) USERS TABLE (LOGIN)
-- ==========================
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password_hash VARCHAR(64) NOT NULL,
    role ENUM('POSTMASTER','CLERK') NOT NULL DEFAULT 'CLERK',
    status ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE'
);

-- Default login: username = postmaster, password = 1234
-- SHA256("1234") = 03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4
INSERT INTO users(username, password_hash, role, status)
VALUES ('postmaster','03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4','POSTMASTER','ACTIVE');

-- ==========================
-- 2) CUSTOMERS TABLE (CIF)
-- ==========================
CREATE TABLE customers (
    customer_id VARCHAR(9) PRIMARY KEY,   -- ✅ CIF 9 digits
    aadhaar VARCHAR(12) UNIQUE NOT NULL,   -- ✅ 1 Aadhaar = 1 Customer
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    mobile VARCHAR(10) NOT NULL
);

CREATE INDEX idx_customers_mobile ON customers(mobile);

-- ==========================
-- 3) ACCOUNTS TABLE
-- ==========================
CREATE TABLE accounts (
    acc_no VARCHAR(12) PRIMARY KEY,       -- ✅ 12 digits
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    mobile VARCHAR(10) NOT NULL,
    acc_type ENUM('SB','RD','TD') NOT NULL,
    balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    customer_id VARCHAR(9) NOT NULL,
    status ENUM('Active','Closed') NOT NULL DEFAULT 'Active',
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_accounts_mobile ON accounts(mobile);
CREATE INDEX idx_accounts_type ON accounts(acc_type);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_customer_id ON accounts(customer_id);

-- ✅ RULE: One SB account per customer_id only
-- (RD/TD multiple allowed)
CREATE UNIQUE INDEX unique_one_sb_per_customer
ON accounts(customer_id, acc_type);

-- BUT above will also restrict RD and TD (wrong) ❌
-- ✅ Fix with trigger-based unique SB-only enforcement ✅

-- Step 1: Create helper column
ALTER TABLE accounts ADD COLUMN sb_unique_key VARCHAR(20) DEFAULT NULL;

DELIMITER $$

-- Insert trigger
CREATE TRIGGER trg_sb_unique_insert
BEFORE INSERT ON accounts
FOR EACH ROW
BEGIN
    IF NEW.acc_type = 'SB' THEN
        SET NEW.sb_unique_key = NEW.customer_id;
    ELSE
        SET NEW.sb_unique_key = NULL;
    END IF;
END$$

-- Update trigger
CREATE TRIGGER trg_sb_unique_update
BEFORE UPDATE ON accounts
FOR EACH ROW
BEGIN
    IF NEW.acc_type = 'SB' THEN
        SET NEW.sb_unique_key = NEW.customer_id;
    ELSE
        SET NEW.sb_unique_key = NULL;
    END IF;
END$$

DELIMITER ;

-- ✅ Drop wrong unique constraint
DROP INDEX unique_one_sb_per_customer ON accounts;

-- ✅ Create SB-only unique constraint
CREATE UNIQUE INDEX unique_only_sb ON accounts(sb_unique_key);

-- ==========================
-- 4) RD DETAILS TABLE
-- ==========================
CREATE TABLE rd_details (
    acc_no VARCHAR(12) PRIMARY KEY,
    monthly_amount DECIMAL(10,2) NOT NULL,
    months_completed INT NOT NULL DEFAULT 0,

    CONSTRAINT fk_rd_acc
        FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);

-- ==========================
-- 5) TRANSACTIONS TABLE
-- ==========================
CREATE TABLE transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_no VARCHAR(12) NOT NULL,
    txn_type VARCHAR(30) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    txn_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_txn_acc
        FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);

CREATE INDEX idx_txn_acc ON transactions(acc_no);
CREATE INDEX idx_txn_type ON transactions(txn_type);
CREATE INDEX idx_txn_date ON transactions(txn_date);

SELECT "✅ post_office database created successfully (Python compatible)" AS STATUS;
