DROP DATABASE IF EXISTS post_office;
CREATE DATABASE post_office;
USE post_office;


CREATE TABLE accounts (
    acc_no VARCHAR(15) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    mobile VARCHAR(10) NOT NULL,
    acc_type ENUM('SB','RD','TD') NOT NULL,
    balance DECIMAL(12,2) NOT NULL,
    status ENUM('Active','Closed') DEFAULT 'Active'
);



CREATE TABLE rd_details (
    acc_no VARCHAR(15) PRIMARY KEY,
    monthly_amount DECIMAL(10,2) NOT NULL,
    months_completed INT DEFAULT 0,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
        ON DELETE CASCADE
);


CREATE TABLE transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_no VARCHAR(15),
    txn_type VARCHAR(20),
    amount DECIMAL(10,2),
    txn_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
);
