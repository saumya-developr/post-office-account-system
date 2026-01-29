USE post_office;

-- ==========================
-- INSERT 15 CUSTOMERS
-- ==========================
INSERT INTO customers (customer_id, aadhaar, name, address, mobile) VALUES
('935942240','228683700716','Anubhav Mishra','Katia Tola, Shahjahanpur','9119621379'),
('935942241','111122223333','Saumya Mishra','Cantt Area, Shahjahanpur','9621049512'),
('935942242','444455556666','Neelam Devi','Tilhar Road, Shahjahanpur','9839012345'),
('935942243','777788889999','Rahul Verma','Powayan, Shahjahanpur','9305123456'),
('935942244','123412341234','Aman Singh','Khutar, Shahjahanpur','9456123789'),
('935942245','999988887777','Pooja Gupta','Katra, Shahjahanpur','9145123678'),
('935942246','555566667777','Rakesh Kumar','Jalalabad, Shahjahanpur','9876501234'),
('935942247','222233334444','Shivani Sharma','Mirzapur, Shahjahanpur','9800012345'),
('935942248','888877776666','Karan Yadav','Nigohi, Shahjahanpur','9123456780'),
('935942249','666655554444','Mohit Jain','Sadar Bazar, Shahjahanpur','9012345678'),
('935942250','121212121212','Sakshi Patel','Banda Road, Shahjahanpur','9898989898'),
('935942251','343434343434','Vikas Tiwari','Civil Lines, Shahjahanpur','9797979797'),
('935942252','565656565656','Riya Singh','Shahjahanpur City','9696969696'),
('935942253','787878787878','Arjun Saxena','Khari Baoli, Shahjahanpur','9595959595'),
('935942254','909090909090','Sneha Gupta','Clock Tower, Shahjahanpur','9494949494');

-- ==========================
-- INSERT ACCOUNTS (SB/RD/TD)
-- acc_no = 12 digits: 010... / 020... / 030...
-- ==========================

-- ✅ SB accounts (only 1 per customer)
INSERT INTO accounts (acc_no, name, address, mobile, acc_type, balance, customer_id, status)
VALUES
('010100000001','Anubhav Mishra','Katia Tola, Shahjahanpur','9119621379','SB',5000.00,'935942240','Active'),
('010100000002','Saumya Mishra','Cantt Area, Shahjahanpur','9621049512','SB',2500.00,'935942241','Active'),
('010100000003','Neelam Devi','Tilhar Road, Shahjahanpur','9839012345','SB',1200.00,'935942242','Active'),
('010100000004','Rahul Verma','Powayan, Shahjahanpur','9305123456','SB',7000.00,'935942243','Active'),
('010100000005','Aman Singh','Khutar, Shahjahanpur','9456123789','SB',1500.00,'935942244','Active'),
('010100000006','Pooja Gupta','Katra, Shahjahanpur','9145123678','SB',3200.00,'935942245','Active'),
('010100000007','Rakesh Kumar','Jalalabad, Shahjahanpur','9876501234','SB',1800.00,'935942246','Active'),
('010100000008','Shivani Sharma','Mirzapur, Shahjahanpur','9800012345','SB',5100.00,'935942247','Active'),
('010100000009','Karan Yadav','Nigohi, Shahjahanpur','9123456780','SB',2400.00,'935942248','Active'),
('010100000010','Mohit Jain','Sadar Bazar, Shahjahanpur','9012345678','SB',6000.00,'935942249','Active'),
('010100000011','Sakshi Patel','Banda Road, Shahjahanpur','9898989898','SB',800.00,'935942250','Active'),
('010100000012','Vikas Tiwari','Civil Lines, Shahjahanpur','9797979797','SB',900.00,'935942251','Active'),
('010100000013','Riya Singh','Shahjahanpur City','9696969696','SB',500.00,'935942252','Active'),
('010100000014','Arjun Saxena','Khari Baoli, Shahjahanpur','9595959595','SB',4500.00,'935942253','Active'),
('010100000015','Sneha Gupta','Clock Tower, Shahjahanpur','9494949494','SB',2000.00,'935942254','Active');

-- ✅ RD accounts (multiple allowed)
INSERT INTO accounts (acc_no, name, address, mobile, acc_type, balance, customer_id, status)
VALUES
('020200000001','Anubhav Mishra','Katia Tola, Shahjahanpur','9119621379','RD',1000.00,'935942240','Active'),
('020200000002','Saumya Mishra','Cantt Area, Shahjahanpur','9621049512','RD',500.00,'935942241','Active'),
('020200000003','Rahul Verma','Powayan, Shahjahanpur','9305123456','RD',2000.00,'935942243','Active'),
('020200000004','Rahul Verma','Powayan, Shahjahanpur','9305123456','RD',1500.00,'935942243','Active'); -- second RD

-- ✅ TD accounts (multiple allowed)
INSERT INTO accounts (acc_no, name, address, mobile, acc_type, balance, customer_id, status)
VALUES
('030300000001','Anubhav Mishra','Katia Tola, Shahjahanpur','9119621379','TD',10000.00,'935942240','Active'),
('030300000002','Saumya Mishra','Cantt Area, Shahjahanpur','9621049512','TD',5000.00,'935942241','Active'),
('030300000003','Sneha Gupta','Clock Tower, Shahjahanpur','9494949494','TD',8000.00,'935942254','Active');

-- ==========================
-- RD DETAILS (For each RD acc)
-- ==========================
INSERT INTO rd_details (acc_no, monthly_amount, months_completed) VALUES
('020200000001',1000.00,12),
('020200000002',500.00,6),
('020200000003',2000.00,24),
('020200000004',1500.00,36);

-- ==========================
-- TRANSACTIONS (Sample 50 entries)
-- ==========================
INSERT INTO transactions (acc_no, txn_type, amount) VALUES
('010100000001','OPENING',5000.00),
('010100000002','OPENING',2500.00),
('010100000003','OPENING',1200.00),
('010100000004','OPENING',7000.00),
('010100000005','OPENING',1500.00),

('010100000001','DEPOSIT',1000.00),
('010100000001','WITHDRAW',500.00),
('010100000002','DEPOSIT',200.00),
('010100000003','WITHDRAW',100.00),
('010100000004','DEPOSIT',1500.00),

('020200000001','RD_OPEN',1000.00),
('020200000002','RD_OPEN',500.00),
('020200000003','RD_OPEN',2000.00),
('020200000004','RD_OPEN',1500.00),

('020200000001','RD_DEPOSIT',1000.00),
('020200000001','RD_DEPOSIT',1000.00),
('020200000001','RD_DEPOSIT',1000.00),
('020200000002','RD_DEPOSIT',500.00),
('020200000003','RD_DEPOSIT',2000.00),

('030300000001','TD_OPEN',10000.00),
('030300000002','TD_OPEN',5000.00),
('030300000003','TD_OPEN',8000.00),

('010100000006','DEPOSIT',1000.00),
('010100000007','WITHDRAW',200.00),
('010100000008','DEPOSIT',700.00),
('010100000009','DEPOSIT',900.00),
('010100000010','WITHDRAW',300.00),

('010100000011','DEPOSIT',500.00),
('010100000012','DEPOSIT',700.00),
('010100000013','WITHDRAW',100.00),
('010100000014','DEPOSIT',1200.00),
('010100000015','DEPOSIT',2000.00),

('010100000001','INTEREST',120.00),
('010100000002','INTEREST',60.00),
('010100000003','INTEREST',45.00),
('010100000004','INTEREST',150.00),

('020200000004','RD_PREMATURE',5000.00),
('020200000003','RD_DEPOSIT',2000.00),
('020200000003','RD_DEPOSIT',2000.00),
('020200000003','RD_DEPOSIT',2000.00),

('030300000001','TD_INTEREST',690.00),
('030300000002','TD_INTEREST',345.00),
('030300000003','TD_INTEREST',552.00);

SELECT "✅ Test data inserted successfully!" AS STATUS;
