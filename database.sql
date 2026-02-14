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
    status ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default login: username = postmaster, password = 1234
INSERT INTO users(username, password_hash, role, status)
VALUES ('postmaster','03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4','POSTMASTER','ACTIVE');

-- ==========================
-- 2) CUSTOMERS TABLE (CIF)
-- ==========================
CREATE TABLE customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    aadhaar VARCHAR(12) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    mobile VARCHAR(10) NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_mobile ON customers(mobile);
CREATE INDEX idx_customers_aadhaar ON customers(aadhaar);

-- ==========================
-- 3) ACCOUNTS TABLE
-- ==========================
CREATE TABLE accounts (
    acc_no VARCHAR(12) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    mobile VARCHAR(10) NOT NULL,
    acc_type ENUM('SB','RD','TD','NSC','KVP') NOT NULL,
    balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    customer_id VARCHAR(10) NOT NULL,
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
-- 5) TD DETAILS TABLE
-- ==========================
CREATE TABLE td_details (
    acc_no VARCHAR(12) PRIMARY KEY,
    tenure_months INT NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    maturity_date DATE,

    CONSTRAINT fk_td_acc
        FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);

-- ==========================
-- 6) NSC DETAILS TABLE
-- ==========================
CREATE TABLE nsc_details (
    acc_no VARCHAR(12) PRIMARY KEY,
    tenure_months INT NOT NULL DEFAULT 60,
    interest_rate DECIMAL(5,2) NOT NULL DEFAULT 7.7,
    maturity_date DATE,

    CONSTRAINT fk_nsc_acc
        FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);

-- ==========================
-- 7) KVP DETAILS TABLE
-- ==========================
CREATE TABLE kvp_details (
    acc_no VARCHAR(12) PRIMARY KEY,
    maturity_period_months INT NOT NULL DEFAULT 115,
    interest_rate DECIMAL(5,2) NOT NULL DEFAULT 7.5,
    maturity_date DATE,

    CONSTRAINT fk_kvp_acc
        FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);

-- ==========================
-- 8) TRANSACTIONS TABLE
-- ==========================
CREATE TABLE transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_no VARCHAR(12) NOT NULL,
    txn_type VARCHAR(50) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    txn_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performed_by VARCHAR(50),
    remarks TEXT,

    CONSTRAINT fk_txn_acc
        FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);

CREATE INDEX idx_txn_acc ON transactions(acc_no);
CREATE INDEX idx_txn_type ON transactions(txn_type);
CREATE INDEX idx_txn_date ON transactions(txn_date);

-- ==========================
-- 9) SYSTEM LOGS TABLE
-- ==========================
CREATE TABLE system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    log_level ENUM('DEBUG','INFO','WARNING','ERROR','CRITICAL') NOT NULL,
    module VARCHAR(100),
    function_name VARCHAR(100),
    message TEXT NOT NULL,
    username VARCHAR(50),
    acc_no VARCHAR(12),
    customer_id VARCHAR(10),
    error_details TEXT,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_level ON system_logs(log_level);
CREATE INDEX idx_logs_date ON system_logs(created_on);
CREATE INDEX idx_logs_username ON system_logs(username);

SELECT "✅ Post Office database created successfully with logging support" AS STATUS;
