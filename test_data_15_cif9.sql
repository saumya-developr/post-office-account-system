USE post_office;

-- ================================
-- CUSTOMERS (15)  | CIF = 9 digits
-- ================================
INSERT IGNORE INTO customers (customer_id, aadhaar, name, address, mobile) VALUES
('100000001','111122223333','Saumya Mishra','Katia, Shahjahanpur','9621049512'),
('100000002','111122223334','Anubhav Mishra','Cantt, Shahjahanpur','9456789012'),
('100000003','111122223335','Neelam Devi','Jalalabad, Shahjahanpur','9876543210'),
('100000004','111122223336','Rohit Kumar','Bareilly','9123456780'),
('100000005','111122223337','Priya Verma','Lucknow','9988776655'),
('100000006','111122223338','Amit Singh','Delhi','8899776655'),
('100000007','111122223339','Saniya Khan','Kanpur','9012345678'),
('100000008','111122223340','Vikas Gupta','Agra','9345678901'),
('100000009','111122223341','Shivam Yadav','Hardoi','9567890123'),
('100000010','111122223342','Anjali Sharma','Sitapur','9876501234'),
('100000011','111122223343','Pooja Patel','Varanasi','9300123456'),
('100000012','111122223344','Rakesh Kumar','Prayagraj','8899001122'),
('100000013','111122223345','Nitin Tiwari','Gorakhpur','7788990011'),
('100000014','111122223346','Kajal Gupta','Badaun','9900112233'),
('100000015','111122223347','Rahul Jain','Meerut','9811112233');

-- ================================
-- ACCOUNTS (15)
-- SB(5) + RD(5) + TD(5)
-- acc_no = 12 digits
-- ================================
INSERT IGNORE INTO accounts (acc_no, customer_id, name, address, mobile, acc_type, balance, status) VALUES

-- SB accounts (5)
('010100000001','100000001','Saumya Mishra','Katia, Shahjahanpur','9621049512','SB',8000,'Active'),
('010100000002','100000002','Anubhav Mishra','Cantt, Shahjahanpur','9456789012','SB',12000,'Active'),
('010100000003','100000003','Neelam Devi','Jalalabad, Shahjahanpur','9876543210','SB',6000,'Active'),
('010100000004','100000004','Rohit Kumar','Bareilly','9123456780','SB',15000,'Active'),
('010100000005','100000005','Priya Verma','Lucknow','9988776655','SB',9500,'Active'),

-- RD accounts (5)
('020200000001','100000001','Saumya Mishra','Katia, Shahjahanpur','9621049512','RD',5000,'Active'),
('020200000002','100000002','Anubhav Mishra','Cantt, Shahjahanpur','9456789012','RD',10000,'Active'),
('020200000003','100000003','Neelam Devi','Jalalabad, Shahjahanpur','9876543210','RD',3000,'Active'),
('020200000004','100000004','Rohit Kumar','Bareilly','9123456780','RD',2000,'Active'),
('020200000005','100000005','Priya Verma','Lucknow','9988776655','RD',4000,'Active'),

-- TD accounts (5)
('030300000001','100000006','Amit Singh','Delhi','8899776655','TD',20000,'Active'),
('030300000002','100000007','Saniya Khan','Kanpur','9012345678','TD',30000,'Active'),
('030300000003','100000008','Vikas Gupta','Agra','9345678901','TD',15000,'Active'),
('030300000004','100000009','Shivam Yadav','Hardoi','9567890123','TD',25000,'Active'),
('030300000005','100000010','Anjali Sharma','Sitapur','9876501234','TD',18000,'Active');

-- ================================
-- RD DETAILS (for all RD accounts)
-- ================================
INSERT IGNORE INTO rd_details (acc_no, monthly_amount, months_completed) VALUES
('020200000001',1000,5),
('020200000002',2000,10),
('020200000003',500,6),
('020200000004',1000,2),
('020200000005',800,4);

-- ================================
-- TRANSACTIONS (sample)
-- ================================
INSERT INTO transactions (acc_no, txn_type, amount) VALUES
('010100000001','DEPOSIT',2000),
('010100000001','WITHDRAW',500),
('010100000002','DEPOSIT',1000),
('010100000003','WITHDRAW',300),
('010100000004','DEP0SIT',2500),
('010100000005','DEPOSIT',700),

('020200000001','RD_INSTALLMENT',1000),
('020200000001','RD_INSTALLMENT',1000),
('020200000002','RD_INSTALLMENT',2000),
('020200000003','RD_INSTALLMENT',500),

('030300000001','TD_OPEN',20000),
('030300000002','TD_OPEN',30000),
('030300000003','TD_OPEN',15000);
