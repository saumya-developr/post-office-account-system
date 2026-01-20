USE post_office;

-- ===============================
-- CUSTOMERS (15)
-- ===============================
INSERT IGNORE INTO customers (customer_id, aadhaar, name, address, mobile) VALUES
('1000000001','111122223333','Saumya Mishra','Katia, Shahjahanpur','9621049512'),
('1000000002','111122223334','Anubhav Mishra','Cantt, Shahjahanpur','9456789012'),
('1000000003','111122223335','Neelam Devi','Jalalabad, Shahjahanpur','9876543210'),
('1000000004','111122223336','Rohit Kumar','Bareilly','9123456780'),
('1000000005','111122223337','Priya Verma','Lucknow','9988776655'),
('1000000006','111122223338','Amit Singh','Delhi','8899776655'),
('1000000007','111122223339','Saniya Khan','Kanpur','9012345678'),
('1000000008','111122223340','Vikas Gupta','Agra','9345678901'),
('1000000009','111122223341','Shivam Yadav','Hardoi','9567890123'),
('1000000010','111122223342','Anjali Sharma','Sitapur','9876501234'),
('1000000011','111122223343','Pooja Patel','Varanasi','9300123456'),
('1000000012','111122223344','Rakesh Kumar','Prayagraj','8899001122'),
('1000000013','111122223345','Nitin Tiwari','Gorakhpur','7788990011'),
('1000000014','111122223346','Kajal Gupta','Badaun','9900112233'),
('1000000015','111122223347','Rahul Jain','Meerut','9811112233');

-- ===============================
-- ACCOUNTS (SB + RD + TD mix)
-- Account no 12 digits:
-- SB: 010xxxxxxxxx
-- RD: 020xxxxxxxxx
-- TD: 030xxxxxxxxx
-- ===============================
INSERT IGNORE INTO accounts (acc_no, name, address, mobile, acc_type, balance, customer_id, status) VALUES

-- SB accounts (one per customer)
('010100000001','Saumya Mishra','Katia, Shahjahanpur','9621049512','SB',8000,'1000000001','Active'),
('010100000002','Anubhav Mishra','Cantt, Shahjahanpur','9456789012','SB',12000,'1000000002','Active'),
('010100000003','Neelam Devi','Jalalabad, Shahjahanpur','9876543210','SB',6000,'1000000003','Active'),
('010100000004','Rohit Kumar','Bareilly','9123456780','SB',15000,'1000000004','Active'),
('010100000005','Priya Verma','Lucknow','9988776655','SB',9500,'1000000005','Active'),

-- RD accounts
('020200000001','Saumya Mishra','Katia, Shahjahanpur','9621049512','RD',5000,'1000000001','Active'),
('020200000002','Anubhav Mishra','Cantt, Shahjahanpur','9456789012','RD',10000,'1000000002','Active'),
('020200000003','Neelam Devi','Jalalabad, Shahjahanpur','9876543210','RD',3000,'1000000003','Active'),
('020200000004','Rohit Kumar','Bareilly','9123456780','RD',2000,'1000000004','Active'),
('020200000005','Priya Verma','Lucknow','9988776655','RD',4000,'1000000005','Active'),

-- TD accounts (1 year)
('030300000001','Amit Singh','Delhi','8899776655','TD',20000,'1000000006','Active'),
('030300000002','Saniya Khan','Kanpur','9012345678','TD',30000,'1000000007','Active'),
('030300000003','Vikas Gupta','Agra','9345678901','TD',15000,'1000000008','Active'),
('030300000004','Shivam Yadav','Hardoi','9567890123','TD',25000,'1000000009','Active'),
('030300000005','Anjali Sharma','Sitapur','9876501234','TD',18000,'1000000010','Active');

-- ===============================
-- RD DETAILS (for all RD accounts)
-- ===============================
INSERT IGNORE INTO rd_details (acc_no, monthly_amount, months_completed) VALUES
('020200000001',1000,5),
('020200000002',2000,10),
('020200000003',500,6),
('020200000004',1000,2),
('020200000005',800,4);

-- ===============================
-- TRANSACTIONS (some sample)
-- ===============================
INSERT INTO transactions (acc_no, txn_type, amount) VALUES
('010100000001','DEPOSIT',2000),
('010100000001','WITHDRAW',500),
('010100000002','DEPOSIT',1000),
('010100000003','WITHDRAW',300),
('010100000004','DEPOSIT',2500),
('010100000005','DEPOSIT',700),

('020200000001','RD_INSTALLMENT',1000),
('020200000001','RD_INSTALLMENT',1000),
('020200000002','RD_INSTALLMENT',2000),
('020200000003','RD_INSTALLMENT',500),

('030300000001','TD_OPEN',20000),
('030300000002','TD_OPEN',30000),
('030300000003','TD_OPEN',15000);
