-- ================================
-- POST OFFICE ACCOUNT SYSTEM
-- SQL DATABASE CODE
-- ================================

-- Delete old database if exists
DROP DATABASE IF EXISTS post_office;

-- Create new database
CREATE DATABASE post_office;

-- Use database
USE post_office;

-- ================================
-- Accounts Table
-- ================================
CREATE TABLE accounts (
    acc_no VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50),
    address VARCHAR(100),
    mobile VARCHAR(15),
    acc_type VARCHAR(5),
    balance DECIMAL(10,2)
);

-- ================================
-- Transactions Table
-- ================================
CREATE TABLE transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_no VARCHAR(10),
    txn_type VARCHAR(20),
    amount DECIMAL(10,2),
    txn_date DATETIME,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
);
