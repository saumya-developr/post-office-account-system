USE post_office;

-- ===============================
-- CLEAN OLD DATA (OPTIONAL)
-- ===============================
DELETE FROM rd_details;
DELETE FROM accounts;

-- ===============================
-- 20 SB ACCOUNTS
-- ===============================
INSERT INTO accounts VALUES
('0101000001','Anubhav Mishra','Shahjahanpur','9876543210','SB',25000,'Active'),
('0101000002','Saumya Mishra','Lucknow','9123456789','SB',18000,'Active'),
('0101000003','Neelam Devi','Bareilly','9988776655','SB',12000,'Active'),
('0101000004','Ramesh Kumar','Delhi','9012345678','SB',32000,'Active'),
('0101000005','Sita Devi','Kanpur','8899776655','SB',15000,'Active'),
('0101000006','Amit Verma','Noida','9876501234','SB',27000,'Active'),
('0101000007','Pooja Singh','Agra','9123498765','SB',11000,'Active'),
('0101000008','Rahul Sharma','Meerut','9001122334','SB',50000,'Active'),
('0101000009','Sunita Gupta','Aligarh','9988001122','SB',16000,'Active'),
('0101000010','Manoj Yadav','Etawah','8877665544','SB',19000,'Active'),
('0101000011','Kiran Patel','Ahmedabad','9900112233','SB',35000,'Active'),
('0101000012','Deepak Jain','Indore','9786543210','SB',22000,'Active'),
('0101000013','Nidhi Saxena','Bhopal','9111222333','SB',14000,'Active'),
('0101000014','Vikas Malhotra','Gurgaon','9898989898','SB',42000,'Active'),
('0101000015','Ritu Arora','Faridabad','9812312312','SB',17000,'Active'),
('0101000016','Sanjay Mehta','Jaipur','9123987654','SB',28000,'Active'),
('0101000017','Anita Roy','Kolkata','9900990099','SB',26000,'Active'),
('0101000018','Mohit Bansal','Panipat','9812121212','SB',15500,'Active'),
('0101000019','Pankaj Tripathi','Gonda','9009009001','SB',21000,'Active'),
('0101000020','Rekha Devi','Sitapur','9897123456','SB',13000,'Active');

-- ===============================
-- 12 RD ACCOUNTS
-- ===============================
INSERT INTO accounts VALUES
('0202000001','Anubhav Mishra','Shahjahanpur','9876543210','RD',60000,'Active'),
('0202000002','Saumya Mishra','Lucknow','9123456789','RD',36000,'Active'),
('0202000003','Ramesh Kumar','Delhi','9012345678','RD',24000,'Active'),
('0202000004','Sita Devi','Kanpur','8899776655','RD',48000,'Active'),
('0202000005','Amit Verma','Noida','9876501234','RD',60000,'Active'),
('0202000006','Pooja Singh','Agra','9123498765','RD',12000,'Active'),
('0202000007','Rahul Sharma','Meerut','9001122334','RD',72000,'Active'),
('0202000008','Sunita Gupta','Aligarh','9988001122','RD',36000,'Active'),
('0202000009','Manoj Yadav','Etawah','8877665544','RD',24000,'Active'),
('0202000010','Kiran Patel','Ahmedabad','9900112233','RD',60000,'Active'),
('0202000011','Deepak Jain','Indore','9786543210','RD',36000,'Active'),
('0202000012','Nidhi Saxena','Bhopal','9111222333','RD',18000,'Active');

-- ===============================
-- RD DETAILS (Installments)
-- ===============================
INSERT INTO rd_details VALUES
('0202000001',1000,60),
('0202000002',1000,36),
('0202000003',1000,24),
('0202000004',2000,24),
('0202000005',1000,60),
('0202000006',1000,12),
('0202000007',1200,60),
('0202000008',1000,36),
('0202000009',1000,24),
('0202000010',1000,60),
('0202000011',1000,36),
('0202000012',500,36);

-- ===============================
-- 8 TD ACCOUNTS
-- ===============================
INSERT INTO accounts VALUES
('0303000001','Ramesh Kumar','Delhi','9012345678','TD',50000,'Active'),
('0303000002','Sita Devi','Kanpur','8899776655','TD',75000,'Active'),
('0303000003','Amit Verma','Noida','9876501234','TD',100000,'Active'),
('0303000004','Rahul Sharma','Meerut','9001122334','TD',60000,'Active'),
('0303000005','Sunita Gupta','Aligarh','9988001122','TD',80000,'Active'),
('0303000006','Manoj Yadav','Etawah','8877665544','TD',55000,'Active'),
('0303000007','Kiran Patel','Ahmedabad','9900112233','TD',90000,'Active'),
('0303000008','Deepak Jain','Indore','9786543210','TD',65000,'Active');

-- ===============================
-- VERIFY TOTAL RECORDS
-- ===============================
SELECT acc_type, COUNT(*) FROM accounts GROUP BY acc_type;
SELECT COUNT(*) AS total_rd FROM rd_details;
