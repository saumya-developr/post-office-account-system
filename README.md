# 🏤 Post Office Account Management System  
### (Python + MySQL | SB, RD, TD Schemes)

A **complete Post Office Account Management System** developed using **Python** and **MySQL**, implementing real-world banking rules for **Savings Bank (SB)**, **Recurring Deposit (RD)**, and **Time Deposit (TD)** accounts.

This project supports **compound interest calculation**, **installment tracking**, **maturity handling**, **transaction history**, and **data integrity using foreign keys**.

---

## 📌 Features

### 🔹 Account Management
- Open SB / RD / TD accounts
- Auto-generated **10-digit account numbers**
  - SB → `010xxxxxxxx`
  - RD → `020xxxxxxxx`
  - TD → `030xxxxxxxx`
- Mobile number validation (10 digits)
- Account status: **Active / Closed**

---

### 🔹 Savings Bank (SB)
- Deposit (SB only)
- Withdrawal with **minimum balance ₹500**
- Compound interest calculation @ **4%**
- Account closure
- RD & TD maturity amount credit support

---

### 🔹 Recurring Deposit (RD)
- Monthly RD deposits
- Multiple installments can be deposited at once
- Installments tracked using `months_completed`
- RD schedule (month-wise deposit + interest)
- Interest rules:
  - ❌ No interest before **36 months**
  - ⚠️ Premature closure after 36 months
  - ✅ Full maturity after **60 installments**
- Compound interest @ **6.7%**
- RD maturity transfer to SB account

---

### 🔹 Time Deposit (TD)
- Lump-sum deposit
- Fixed tenure: **1 year**
- Compound interest @ **6.9%**
- TD maturity transfer to SB account
- Automatic TD account closure after maturity

---

### 🔹 Transactions
- Separate `transactions` table
- Records:
  - Deposits
  - Withdrawals
  - RD installments
  - Interest credits
  - Maturity transfers
- Enforced **foreign key constraint** (`acc_no`)

---

### 🔹 Search & Enquiry
- Search account by:
  - Name
  - Account Number
  - Mobile Number
- Balance enquiry
- Account status check

---

## 🛠️ Technologies Used

- **Python 3.10+**
- **MySQL Server**
- MySQL Port: **3307**
- `mysql-connector-python`
- `decimal` module for accurate financial calculations

---

## 🗂️ Database Structure

### 📘 accounts
| Column | Description |
|------|------------|
| acc_no | Account Number (Primary Key) |
| name | Account Holder Name |
| address | Address |
| mobile | Mobile Number |
| acc_type | SB / RD / TD |
| balance | Current Balance |
| status | Active / Closed |

---

### 📘 rd_details
| Column | Description |
|------|------------|
| acc_no | RD Account Number (Foreign Key) |
| monthly_amount | Monthly Installment |
| months_completed | Installments Completed |

---

### 📘 transactions
| Column | Description |
|------|------------|
| txn_id | Auto Increment ID |
| acc_no | Account Number (Foreign Key) |
| txn_type | Transaction Type |
| amount | Transaction Amount |
| txn_date | Timestamp |

---

## ▶️ How to Run the Project (Beginner Friendly)

### 🔹 Step 1: Install Requirements
```bash
pip install mysql-connector-python

Step 2: Start MySQL Server

Port: 3307

User: root

Password: 1234

🔹 Step 3: Create Database
CREATE DATABASE post_office;
USE post_office;

🔹 Step 4: Import Database Tables

Assuming database.sql contains table structure:

"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -P 3307 post_office < database.sql

🔹 Step 5: Import Test Data (Accounts / Transactions)
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -P 3307 post_office < test_data.sql


✔ This imports:

Sample accounts

RD details

100+ transaction records

🔹 Step 6: Verify Database Data
USE post_office;

SHOW TABLES;
SELECT COUNT(*) FROM accounts;
SELECT COUNT(*) FROM transactions;
SELECT * FROM rd_details;

🔹 Step 7: Run Python Program
python post_office.py

🧪 Useful SQL Queries
-- View all accounts
SELECT * FROM accounts;

-- Active accounts
SELECT * FROM accounts WHERE status='Active';

-- View all transactions
SELECT * FROM transactions;

-- Account-wise transactions
SELECT * FROM transactions WHERE acc_no='010xxxxxxxx';

-- RD installments
SELECT * FROM rd_details;

📦 Database Backup & Transfer (Important)
🔹 Export Database
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u root -p -P 3307 post_office > post_office_backup.sql

🔹 Import on Another PC
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -P 3307 post_office < post_office_backup.sql


✔ All tables and data will be restored.

⚠️ Common Errors & Fixes
Error	Reason	Fix
mysql not recognized	PATH not set	Use full path
Foreign key constraint fails	Account not found	Insert valid acc_no
Access denied	Wrong password	Check credentials
Wrong port	MySQL on 3306	Update port to 3307
🧠 Learning Outcomes

Python–MySQL integration

Real-world banking logic

Foreign key constraints

Compound interest calculations

Menu-driven system design

Data validation & integrity

🚀 Future Enhancements

GUI using Tkinter

User login system (Clerk / Admin)

PDF account statements

Audit logs

Role-based access control

Email / SMS alerts

👤 Author

Saumya Mishra
Class XII
Kendriya Vidyalaya No.1 Cantt, Shahjahanpur

📄 License

This project is created for educational and learning purposes only.
