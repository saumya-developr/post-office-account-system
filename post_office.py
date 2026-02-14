import mysql.connector
import random
import hashlib
import webbrowser
import os
from decimal import Decimal
from datetime import datetime, timedelta
import logging
import traceback

# ================= LOGGING SETUP =================
class DatabaseLogger:
    """Custom logger that writes to both console and database"""
    
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection
        self.current_user = None
        
        # Setup console logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('post_office.log'),
                logging.StreamHandler()
            ]
        )
        self.console_logger = logging.getLogger('PostOffice')
    
    def set_user(self, username):
        """Set current logged-in user"""
        self.current_user = username
    
    def log(self, level, module, function_name, message, acc_no=None, customer_id=None, error_details=None):
        """Log to both console and database"""
        # Console log
        log_method = getattr(self.console_logger, level.lower(), self.console_logger.info)
        log_method(f"[{module}.{function_name}] {message}")
        
        # Database log
        try:
            self.cursor.execute("""
                INSERT INTO system_logs 
                (log_level, module, function_name, message, username, acc_no, customer_id, error_details)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (level, module, function_name, message, self.current_user, acc_no, customer_id, error_details))
            self.connection.commit()
        except Exception as e:
            self.console_logger.error(f"Failed to write to database log: {e}")
    
    def debug(self, module, function, message, **kwargs):
        self.log('DEBUG', module, function, message, **kwargs)
    
    def info(self, module, function, message, **kwargs):
        self.log('INFO', module, function, message, **kwargs)
    
    def warning(self, module, function, message, **kwargs):
        self.log('WARNING', module, function, message, **kwargs)
    
    def error(self, module, function, message, **kwargs):
        self.log('ERROR', module, function, message, **kwargs)
    
    def critical(self, module, function, message, **kwargs):
        self.log('CRITICAL', module, function, message, **kwargs)


# ================= DATABASE CONNECTION =================
print("Program started ...")

try:
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="post_office",
        port=3307,
        connection_timeout=5
    )
    cur = con.cursor()
    logger = DatabaseLogger(cur, con)
    logger.info('System', 'startup', 'Database connected successfully')
    print("✅ Database connected")
except Exception as e:
    print(f"❌ ERROR: Database not connected - {e}")
    input("Press Enter to exit")
    exit()

# Global session variable
session = None

# ================= UTILITY FUNCTIONS =================

FORMS_LOCAL = {
    "SB-3 (Savings Account Opening Form)": "forms/sb3.pdf",
    "RD Account Opening Form": "forms/sb3.pdf",
    "TD Account Opening Form": "forms/sb3.pdf",
    "NSC Account Opening Form": "forms/nsc.pdf",
    "KVP Account Opening Form": "forms/kvp.pdf",
    "Deposit Slip (SB/RD/TD)": "forms/sb103.pdf",
    "Withdrawal Form (SB/RD/TD)": "forms/sb7.pdf",
    "Account Closure Form": "forms/sb7a.pdf"
}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_aadhaar(aadhaar):
    return aadhaar.isdigit() and len(aadhaar) == 12

def is_valid_mobile(mobile):
    return mobile.isdigit() and len(mobile) == 10

def generate_customer_id():
    return str(random.randint(1000000000, 9999999999))

def generate_account_number(acc_type):
    """Generate 12-digit account number with proper prefix"""
    prefix = {"SB": "010", "RD": "020", "TD": "030", "NSC": "040", "KVP": "050"}
    
    # Validate account type
    if acc_type not in prefix:
        raise ValueError(f"Invalid account type: {acc_type}. Must be one of: {list(prefix.keys())}")
    
    # 3 digit prefix + 9 digit random = 12 digits total
    random_part = str(random.randint(100000000, 999999999))
    account_number = prefix[acc_type] + random_part
    
    # Validate length
    if len(account_number) != 12:
        raise ValueError(f"Generated account number has wrong length: {len(account_number)}")
    
    return account_number

# ================= SCHEME INFO FUNCTIONS =================

def sb_info():
    print("\n=== SB SCHEME INFORMATION ===")
    print("Scheme Name      : Savings Bank (SB)")
    print("Account Prefix   : 010xxxxxxxxx (12 digits)")
    print("Interest Rate    : 4% (Compound) [1 Oct 2025 – 31 Dec 2025]")
    print("Minimum Balance  : ₹500")
    print("Deposit/Withdraw : Allowed anytime")
    print("Main Operations  : Deposit, Withdraw, Interest, Closure")

def rd_info():
    print("\n=== RD SCHEME INFORMATION ===")
    print("Scheme Name      : Recurring Deposit (RD)")
    print("Account Prefix   : 020xxxxxxxxx (12 digits)")
    print("Interest Rate    : 6.7% (Compound) [1 Oct 2025 – 31 Dec 2025]")
    print("Tenure           : 60 months (5 years)")
    print("Maturity Rule    : Full maturity after 60 installments")
    print("Premature Closure: Allowed after 36 months (reduced benefit)")
    print("Deposit Type     : Monthly fixed installment")

def td_info():
    print("\n=== TD SCHEME INFORMATION ===")
    print("Scheme Name      : Time Deposit (TD)")
    print("Account Prefix   : 030xxxxxxxxx (12 digits)")
    print("Interest Rates   : 2Y: 7.3%, 3Y: 7.5%, 5Y: 7.7%")
    print("Tenure Options   : 2, 3, or 5 years")
    print("Deposit Type     : One-time lump sum")
    print("Maturity         : Amount transfers to SB")

def nsc_info():
    print("\n=== NSC SCHEME INFORMATION ===")
    print("Scheme Name      : National Savings Certificate (NSC)")
    print("Account Prefix   : 040xxxxxxxxx (12 digits)")
    print("Interest Rate    : 7.7% (Compound)")
    print("Tenure           : 5 years (60 months)")
    print("Minimum Deposit  : ₹1,000")
    print("Maturity         : After 5 years")
    print("Tax Benefit      : Eligible under Section 80C")

def kvp_info():
    print("\n=== KVP SCHEME INFORMATION ===")
    print("Scheme Name      : Kisan Vikas Patra (KVP)")
    print("Account Prefix   : 050xxxxxxxxx (12 digits)")
    print("Interest Rate    : 7.5% (doubles in 115 months)")
    print("Maturity Period  : 115 months (~9.6 years)")
    print("Minimum Deposit  : ₹1,000")
    print("Feature          : Amount doubles at maturity")

# ================= LOGIN FUNCTION =================

def login():
    print("\n=== POST OFFICE LOGIN ===")
    logger.info('Authentication', 'login', 'Login attempt started')
    
    try:
        for attempt in range(1, 4):
            username = input("Username: ").strip()
            
            if username == "":
                print("❌ Username cannot be empty")
                continue
            
            password = input("Password: ").strip()
            
            if password == "":
                print("❌ Password cannot be empty")
                continue
            
            password_hash = hash_password(password)
            
            cur.execute("""
                SELECT role, status
                FROM users
                WHERE username=%s AND password_hash=%s
            """, (username, password_hash))
            
            user = cur.fetchone()
            
            if user:
                role, status = user
                if status != "ACTIVE":
                    logger.warning('Authentication', 'login', 
                                 f'Inactive account login attempt: {username}')
                    print("❌ Your account is inactive. Contact admin.")
                    return None
                
                logger.info('Authentication', 'login', 
                          f'Successful login: {username} (Role: {role})')
                print(f"\n✅ Login Successful! Role: {role}")
                return {"username": username, "role": role}
            
            logger.warning('Authentication', 'login', 
                         f'Failed login attempt {attempt}/3 for username: {username}')
            print(f"❌ Invalid credentials (Attempt {attempt}/3)")
        
        logger.error('Authentication', 'login', 'Max login attempts exceeded')
        print("\n🚫 Too many failed attempts. Exiting program.")
        return None
    
    except KeyboardInterrupt:
        logger.info('Authentication', 'login', 'Login cancelled by user')
        print("\n✅ Exiting program...")
        return None
    except Exception as e:
        logger.error('Authentication', 'login', f'Login error: {str(e)}', 
                    error_details=traceback.format_exc())
        print(f"❌ Login error: {e}")
        return None

# ================= CUSTOMER MANAGEMENT =================

def get_or_create_customer():
    print("\n=== CUSTOMER IDENTIFICATION ===")
    logger.info('Customer', 'get_or_create', 'Customer identification started')
    
    customer_id = input("Enter Customer ID (10 digits) OR press Enter for NEW customer: ").strip()
    
    try:
        # CASE 1: Existing customer
        if customer_id != "":
            if not (customer_id.isdigit() and len(customer_id) == 10):
                logger.warning('Customer', 'get_or_create', 
                             f'Invalid customer ID format: {customer_id}')
                print("❌ Invalid Customer ID (must be 10 digits)")
                return None
            
            cur.execute(
                "SELECT customer_id, aadhaar, name, address, mobile FROM customers WHERE customer_id=%s",
                (customer_id,)
            )
            data = cur.fetchone()
            
            if not data:
                logger.warning('Customer', 'get_or_create', 
                             f'Customer ID not found: {customer_id}')
                print("❌ Customer ID not found")
                return None
            
            logger.info('Customer', 'get_or_create', 
                       f'Customer found: {customer_id}', customer_id=customer_id)
            print("\n✅ CUSTOMER FOUND")
            print("Customer ID (CIF):", data[0])
            print("Name:", data[2])
            print("Mobile:", data[4])
            
            return data[0]
        
        # CASE 2: New customer
        print("\n🆕 New Customer Registration")
        
        name = input("Customer Name: ").strip()
        address = input("Customer Address: ").strip()
        mobile = input("Customer Mobile (10 digits): ").strip()
        aadhaar = input("Customer Aadhaar (12 digits): ").strip()
        
        if not name or not address:
            logger.warning('Customer', 'get_or_create', 'Empty name or address')
            print("❌ Name/Address cannot be empty")
            return None
        
        if not is_valid_mobile(mobile):
            logger.warning('Customer', 'get_or_create', f'Invalid mobile: {mobile}')
            print("❌ Invalid mobile number")
            return None
        
        if not is_valid_aadhaar(aadhaar):
            logger.warning('Customer', 'get_or_create', f'Invalid Aadhaar: {aadhaar}')
            print("❌ Invalid Aadhaar number")
            return None
        
        # Check if Aadhaar exists
        cur.execute("SELECT customer_id, name FROM customers WHERE aadhaar=%s", (aadhaar,))
        existing = cur.fetchone()
        
        if existing:
            logger.info('Customer', 'get_or_create', 
                       f'Aadhaar already exists: {existing[0]}', customer_id=existing[0])
            print("\n⚠️ Aadhaar already exists!")
            print("Existing Customer:", existing[1])
            print("Customer ID (CIF):", existing[0])
            return existing[0]
        
        # Generate unique customer ID
        while True:
            new_cif = generate_customer_id()
            cur.execute("SELECT customer_id FROM customers WHERE customer_id=%s", (new_cif,))
            if not cur.fetchone():
                break
        
        # Insert new customer
        cur.execute(
            "INSERT INTO customers (customer_id, aadhaar, name, address, mobile) VALUES (%s,%s,%s,%s,%s)",
            (new_cif, aadhaar, name, address, mobile)
        )
        con.commit()
        
        logger.info('Customer', 'get_or_create', 
                   f'New customer created: {new_cif}', customer_id=new_cif)
        print("\n✅ New Customer Created Successfully!")
        print("Customer ID (CIF):", new_cif)
        
        return new_cif
    
    except Exception as e:
        con.rollback()
        logger.error('Customer', 'get_or_create', f'Error: {str(e)}', 
                    error_details=traceback.format_exc())
        print(f"❌ Error: {e}")
        return None

# ================= ACCOUNT CREATION =================

def create_account():
    print("\n=== CREATE NEW ACCOUNT ===")
    logger.info('Account', 'create', 'Account creation started')
    
    try:
        customer_id = get_or_create_customer()
        if not customer_id:
            return
        
        # Scheme selection with validation
        print("\nAvailable Account Types:")
        print("1. SB  - Savings Bank")
        print("2. RD  - Recurring Deposit")
        print("3. TD  - Time Deposit")
        print("4. NSC - National Savings Certificate")
        print("5. KVP - Kisan Vikas Patra")
        
        valid_types = {"SB", "RD", "TD", "NSC", "KVP"}
        
        while True:
            acc_type = input("Account Type (SB / RD / TD / NSC / KVP): ").strip().upper()
            if acc_type in valid_types:
                break
            print("❌ Invalid account type. Please choose from: SB, RD, TD, NSC, KVP")
        
        # ONE SB ACCOUNT ONLY per customer
        if acc_type == "SB":
            cur.execute("""
                SELECT acc_no FROM accounts
                WHERE customer_id=%s AND acc_type='SB' AND status='Active'
            """, (customer_id,))
            
            sb_exists = cur.fetchone()
            if sb_exists:
                logger.warning('Account', 'create', 
                             f'Customer {customer_id} already has SB account: {sb_exists[0]}',
                             customer_id=customer_id, acc_no=sb_exists[0])
                print("❌ This customer already has an ACTIVE SB account!")
                print("Existing SB Account No:", sb_exists[0])
                return
        
        # Generate unique account number
        while True:
            acc_no = generate_account_number(acc_type)
            cur.execute("SELECT acc_no FROM accounts WHERE acc_no=%s", (acc_no,))
            if not cur.fetchone():
                break
        
        # Fetch customer info
        cur.execute("SELECT name, address, mobile FROM customers WHERE customer_id=%s", (customer_id,))
        name, address, mobile = cur.fetchone()
        
        balance = 0
        
        # ================= SCHEME-SPECIFIC LOGIC =================
        
        if acc_type == "SB":
            balance = float(input("Opening Balance (Min 500): "))
            if balance < 500:
                logger.warning('Account', 'create', 
                             f'SB balance too low: {balance}', customer_id=customer_id)
                print("❌ Minimum opening balance for SB is 500")
                return
        
        elif acc_type == "RD":
            monthly = float(input("Monthly RD Amount (Min 100, Multiple of 100): "))
            if monthly < 100:
                logger.warning('Account', 'create', 
                             f'RD amount too low: {monthly}', customer_id=customer_id)
                print("❌ RD minimum amount is 100")
                return
            if monthly % 100 != 0:
                logger.warning('Account', 'create', 
                             f'RD amount not multiple of 100: {monthly}', customer_id=customer_id)
                print("❌ RD amount must be in multiples of 100")
                return
            balance = monthly
        
        elif acc_type == "TD":
            print("1. 2 Years (7.3%)")
            print("2. 3 Years (7.5%)")
            print("3. 5 Years (7.7%)")
            t = input("Choice: ")
            
            if t == '1':
                tenure = 24
                rate = 7.3
            elif t == '2':
                tenure = 36
                rate = 7.5
            else:
                tenure = 60
                rate = 7.7
            
            balance = float(input("TD Amount (Min 1000): "))
            if balance < 1000:
                logger.warning('Account', 'create', 
                             f'TD amount too low: {balance}', customer_id=customer_id)
                print("❌ TD minimum amount is 1000")
                return
            
            maturity_date = datetime.now() + timedelta(days=tenure*30)
        
        elif acc_type == "NSC":
            balance = float(input("NSC Amount (Min 1000): "))
            if balance < 1000:
                logger.warning('Account', 'create', 
                             f'NSC amount too low: {balance}', customer_id=customer_id)
                print("❌ NSC minimum amount is 1000")
                return
            tenure = 60
            rate = 7.7
            maturity_date = datetime.now() + timedelta(days=tenure*30)
        
        elif acc_type == "KVP":
            balance = float(input("KVP Amount (Min 1000): "))
            if balance < 1000:
                logger.warning('Account', 'create', 
                             f'KVP amount too low: {balance}', customer_id=customer_id)
                print("❌ KVP minimum amount is 1000")
                return
            maturity_period = 115
            rate = 7.5
            maturity_date = datetime.now() + timedelta(days=maturity_period*30)
        
        # ================= INSERT INTO DATABASE =================
        
        cur.execute("""
            INSERT INTO accounts
            (acc_no, name, address, mobile, acc_type, balance, customer_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
        """, (acc_no, name, address, mobile, acc_type, balance, customer_id))
        
        # Insert scheme-specific details
        if acc_type == "RD":
            cur.execute(
                "INSERT INTO rd_details (acc_no, monthly_amount, months_completed) VALUES (%s,%s,%s)",
                (acc_no, monthly, 1)
            )
        
        elif acc_type == "TD":
            cur.execute(
                "INSERT INTO td_details (acc_no, tenure_months, interest_rate, maturity_date) VALUES (%s,%s,%s,%s)",
                (acc_no, tenure, rate, maturity_date)
            )
        
        elif acc_type == "NSC":
            cur.execute(
                "INSERT INTO nsc_details (acc_no, tenure_months, interest_rate, maturity_date) VALUES (%s,%s,%s,%s)",
                (acc_no, tenure, rate, maturity_date)
            )
        
        elif acc_type == "KVP":
            cur.execute(
                "INSERT INTO kvp_details (acc_no, maturity_period_months, interest_rate, maturity_date) VALUES (%s,%s,%s,%s)",
                (acc_no, maturity_period, rate, maturity_date)
            )
        
        # Log transaction
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """, (acc_no, f'{acc_type}_OPEN', balance, session['username'], 'Account opened'))
        
        con.commit()
        
        logger.info('Account', 'create', 
                   f'{acc_type} account created: {acc_no}', 
                   customer_id=customer_id, acc_no=acc_no)
        
        print("\n✅ Account Created Successfully!")
        print("Customer ID (CIF):", customer_id)
        print("Account Number:", acc_no)
        print("Account Type:", acc_type)
        print("Opening Balance:", balance)
    
    except Exception as e:
        con.rollback()
        logger.error('Account', 'create', f'Account creation failed: {str(e)}', 
                    customer_id=customer_id if 'customer_id' in locals() else None,
                    error_details=traceback.format_exc())
        print(f"❌ Error creating account: {e}")

# ================= BASIC OPERATIONS =================

def deposit():
    logger.info('Transaction', 'deposit', 'Deposit operation started')
    acc = input("Account Number: ")
    
    try:
        cur.execute("SELECT status, acc_type, balance FROM accounts WHERE acc_no=%s", (acc,))
        d = cur.fetchone()
        
        if not d:
            logger.warning('Transaction', 'deposit', f'Account not found: {acc}', acc_no=acc)
            print("❌ Account not found")
            return
        
        status, acc_type, current_balance = d
        
        if status == "Closed":
            logger.warning('Transaction', 'deposit', f'Closed account: {acc}', acc_no=acc)
            print("❌ Account is closed")
            return
        
        if acc_type != "SB":
            logger.warning('Transaction', 'deposit', 
                         f'Deposit attempted on {acc_type} account: {acc}', acc_no=acc)
            print("❌ Deposit allowed only in SB accounts")
            return
        
        amt = float(input("Amount: "))
        if amt <= 0:
            logger.warning('Transaction', 'deposit', f'Invalid amount: {amt}', acc_no=acc)
            print("❌ Invalid amount")
            return
        
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no=%s", (amt, acc))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by)
            VALUES (%s, %s, %s, %s)
        """, (acc, 'DEPOSIT', amt, session['username']))
        
        con.commit()
        
        logger.info('Transaction', 'deposit', 
                   f'Deposit successful: {amt} to {acc}', acc_no=acc)
        print(f"✅ Deposit Successful! New Balance: {current_balance + amt}")
    
    except Exception as e:
        con.rollback()
        logger.error('Transaction', 'deposit', f'Deposit failed: {str(e)}', 
                    acc_no=acc, error_details=traceback.format_exc())
        print(f"❌ Deposit failed: {e}")

def withdraw():
    logger.info('Transaction', 'withdraw', 'Withdrawal operation started')
    acc = input("Account Number: ")
    
    try:
        cur.execute("SELECT balance, acc_type, status FROM accounts WHERE acc_no=%s", (acc,))
        d = cur.fetchone()
        
        if not d:
            logger.warning('Transaction', 'withdraw', f'Account not found: {acc}', acc_no=acc)
            print("❌ Account not found")
            return
        
        balance, acc_type, status = d
        
        if status == "Closed":
            logger.warning('Transaction', 'withdraw', f'Closed account: {acc}', acc_no=acc)
            print("❌ Account is closed")
            return
        
        if acc_type != "SB":
            logger.warning('Transaction', 'withdraw', 
                         f'Withdrawal attempted on {acc_type} account: {acc}', acc_no=acc)
            print("❌ Withdrawal allowed only from SB accounts")
            return
        
        amt = Decimal(input("Amount: "))
        if amt <= 0:
            logger.warning('Transaction', 'withdraw', f'Invalid amount: {amt}', acc_no=acc)
            print("❌ Invalid amount")
            return
        
        balance = Decimal(balance)
        
        if balance < amt:
            logger.warning('Transaction', 'withdraw', 
                         f'Insufficient balance: {balance} < {amt}', acc_no=acc)
            print("❌ Insufficient balance")
            return
        
        if balance - amt < Decimal("500"):
            logger.warning('Transaction', 'withdraw', 
                         f'Min balance violation: {balance - amt}', acc_no=acc)
            print("❌ Minimum balance of 500 must be maintained")
            return
        
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no=%s", (amt, acc))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by)
            VALUES (%s, %s, %s, %s)
        """, (acc, 'WITHDRAWAL', amt, session['username']))
        
        con.commit()
        
        logger.info('Transaction', 'withdraw', 
                   f'Withdrawal successful: {amt} from {acc}', acc_no=acc)
        print(f"✅ Withdrawal Successful! New Balance: {balance - amt}")
    
    except Exception as e:
        con.rollback()
        logger.error('Transaction', 'withdraw', f'Withdrawal failed: {str(e)}', 
                    acc_no=acc, error_details=traceback.format_exc())
        print(f"❌ Withdrawal failed: {e}")

def balance_enquiry():
    logger.info('Account', 'balance_enquiry', 'Balance enquiry started')
    acc = input("Account Number: ")
    
    try:
        cur.execute("SELECT name, balance, status, acc_type FROM accounts WHERE acc_no=%s", (acc,))
        d = cur.fetchone()
        
        if d:
            logger.info('Account', 'balance_enquiry', f'Balance checked: {acc}', acc_no=acc)
            print("\n✅ ACCOUNT DETAILS")
            print("Name:", d[0])
            print("Account Type:", d[3])
            print("Balance:", d[1])
            print("Status:", d[2])
        else:
            logger.warning('Account', 'balance_enquiry', f'Account not found: {acc}', acc_no=acc)
            print("❌ Account not found")
    
    except Exception as e:
        logger.error('Account', 'balance_enquiry', f'Balance enquiry failed: {str(e)}', 
                    acc_no=acc, error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

def search_account():
    logger.info('Account', 'search', 'Search operation started')
    
    while True:
        print("""
=== SEARCH ACCOUNT ===
1. Search by Name
2. Search by Account Number
3. Search by Mobile Number
4. Search by Aadhaar Number
0. Back
""")
        ch = input("Enter Choice: ").strip()
        
        try:
            if ch == '1':
                name = input("Enter Name: ").strip()
                cur.execute(
                    "SELECT acc_no, name, acc_type, balance, status FROM accounts WHERE name LIKE %s",
                    ('%' + name + '%',)
                )
                rows = cur.fetchall()
                
                if not rows:
                    print("❌ No account found")
                else:
                    print("\nACC NO | NAME | TYPE | BALANCE | STATUS")
                    print("------------------------------------------")
                    for r in rows:
                        print(r)
                logger.info('Account', 'search', f'Name search: {name}')
            
            elif ch == '2':
                acc = input("Enter Account Number: ").strip()
                cur.execute(
                    "SELECT acc_no, name, acc_type, balance, status FROM accounts WHERE acc_no=%s",
                    (acc,)
                )
                rows = cur.fetchall()
                
                if not rows:
                    print("❌ No account found")
                else:
                    print("\nACC NO | NAME | TYPE | BALANCE | STATUS")
                    print("------------------------------------------")
                    for r in rows:
                        print(r)
                logger.info('Account', 'search', f'Account search: {acc}')
            
            elif ch == '3':
                mobile = input("Enter Mobile Number: ").strip()
                if not is_valid_mobile(mobile):
                    print("❌ Invalid mobile number")
                    continue
                
                cur.execute(
                    "SELECT acc_no, name, acc_type, balance, status FROM accounts WHERE mobile=%s",
                    (mobile,)
                )
                rows = cur.fetchall()
                
                if not rows:
                    print("❌ No account found")
                else:
                    print("\nACC NO | NAME | TYPE | BALANCE | STATUS")
                    print("------------------------------------------")
                    for r in rows:
                        print(r)
                logger.info('Account', 'search', f'Mobile search: {mobile}')
            
            elif ch == '4':
                aadhaar = input("Enter Aadhaar Number: ").strip()
                if not is_valid_aadhaar(aadhaar):
                    print("❌ Invalid Aadhaar number")
                    continue
                
                cur.execute(
                    "SELECT customer_id, name, address, mobile FROM customers WHERE aadhaar=%s",
                    (aadhaar,)
                )
                customer = cur.fetchone()
                
                if not customer:
                    print("❌ No customer found")
                    continue
                
                customer_id, cname, caddress, cmobile = customer
                
                print("\n✅ CUSTOMER DETAILS")
                print("Customer ID:", customer_id)
                print("Name:", cname)
                print("Address:", caddress)
                print("Mobile:", cmobile)
                
                cur.execute(
                    "SELECT acc_no, acc_type, balance, status FROM accounts WHERE customer_id=%s",
                    (customer_id,)
                )
                accounts = cur.fetchall()
                
                if accounts:
                    print("\n✅ LINKED ACCOUNTS")
                    print("ACC NO | TYPE | BALANCE | STATUS")
                    print("------------------------------------")
                    for a in accounts:
                        print(a)
                
                logger.info('Account', 'search', f'Aadhaar search: {aadhaar}')
            
            elif ch == '0':
                break
            
            else:
                print("❌ Invalid Choice")
        
        except Exception as e:
            logger.error('Account', 'search', f'Search failed: {str(e)}', 
                        error_details=traceback.format_exc())
            print(f"❌ Error: {e}")

def close_account():
    logger.info('Account', 'close', 'Account closure started')
    acc = input("Account Number: ")
    
    try:
        cur.execute("SELECT status, balance FROM accounts WHERE acc_no=%s", (acc,))
        d = cur.fetchone()
        
        if not d:
            logger.warning('Account', 'close', f'Account not found: {acc}', acc_no=acc)
            print("❌ Invalid Account Number")
            return
        
        if d[0] == "Closed":
            logger.warning('Account', 'close', f'Already closed: {acc}', acc_no=acc)
            print("❌ Account is already closed")
            return
        
        confirm = input(f"Close account {acc} with balance {d[1]}? (yes/no): ").lower()
        if confirm != 'yes':
            print("❌ Account closure cancelled")
            return
        
        cur.execute("UPDATE accounts SET status='Closed' WHERE acc_no=%s", (acc,))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """, (acc, 'CLOSURE', 0, session['username'], 'Account closed'))
        
        con.commit()
        
        logger.info('Account', 'close', f'Account closed: {acc}', acc_no=acc)
        print("✅ Account Closed Successfully")
    
    except Exception as e:
        con.rollback()
        logger.error('Account', 'close', f'Closure failed: {str(e)}', 
                    acc_no=acc, error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

# ================= RD OPERATIONS =================

def rd_monthly_deposit():
    logger.info('RD', 'monthly_deposit', 'RD deposit started')
    acc = input("RD Account Number: ").strip()
    
    try:
        cur.execute("""
            SELECT r.monthly_amount, r.months_completed, a.status
            FROM rd_details r
            JOIN accounts a ON r.acc_no = a.acc_no
            WHERE r.acc_no=%s
        """, (acc,))
        d = cur.fetchone()
        
        if not d:
            logger.warning('RD', 'monthly_deposit', f'RD account not found: {acc}', acc_no=acc)
            print("❌ RD account not found")
            return
        
        monthly_amount, months_completed, status = d
        
        if status == "Closed":
            logger.warning('RD', 'monthly_deposit', f'Closed RD account: {acc}', acc_no=acc)
            print("❌ RD account is closed")
            return
        
        monthly_amount = float(monthly_amount)
        months_completed = int(months_completed)
        
        if months_completed >= 60:
            logger.warning('RD', 'monthly_deposit', f'RD already matured: {acc}', acc_no=acc)
            print("✅ RD account already completed 60 installments (Matured)")
            return
        
        installments = int(input("Enter number of installments to deposit: "))
        if installments <= 0:
            print("❌ Invalid number of installments")
            return
        
        remaining = 60 - months_completed
        
        if installments > remaining:
            logger.warning('RD', 'monthly_deposit', 
                         f'Excess installments: {installments} > {remaining}', acc_no=acc)
            print(f"❌ Only {remaining} installment(s) remaining")
            return
        
        total_deposit = monthly_amount * installments
        
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no = %s", 
                   (total_deposit, acc))
        cur.execute("UPDATE rd_details SET months_completed = months_completed + %s WHERE acc_no = %s", 
                   (installments, acc))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """, (acc, 'RD_DEPOSIT', total_deposit, session['username'], 
              f'{installments} installments deposited'))
        
        con.commit()
        
        logger.info('RD', 'monthly_deposit', 
                   f'RD deposit successful: {installments} installments for {acc}', acc_no=acc)
        print(f"\n✅ RD Deposit Successful!")
        print(f"Installments Deposited: {installments}")
        print(f"Amount Deposited: {total_deposit}")
        print(f"Total Installments Completed: {months_completed + installments}")
    
    except Exception as e:
        con.rollback()
        logger.error('RD', 'monthly_deposit', f'RD deposit failed: {str(e)}', 
                    acc_no=acc, error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

def rd_compound_interest():
    logger.info('RD', 'interest', 'RD interest calculation started')
    acc = input("RD Account Number: ")
    rate = Decimal("6.7")
    
    try:
        cur.execute("""
            SELECT r.monthly_amount, r.months_completed, a.status
            FROM rd_details r
            JOIN accounts a ON r.acc_no = a.acc_no
            WHERE r.acc_no=%s
        """, (acc,))
        d = cur.fetchone()
        
        if not d or d[2] == "Closed":
            logger.warning('RD', 'interest', f'Invalid/Closed RD: {acc}', acc_no=acc)
            print("❌ Invalid / Closed RD Account")
            return
        
        monthly = Decimal(d[0])
        months = d[1]
        
        if months < 36:
            logger.warning('RD', 'interest', 
                         f'RD interest not applicable before 36 months: {acc}', acc_no=acc)
            print("❌ RD interest not applicable before 36 months")
            return
        
        balance = Decimal("0")
        
        for m in range(1, months + 1):
            balance += monthly
            interest = (balance * rate) / Decimal("1200")
            balance += interest
        
        interest_earned = balance - (monthly * months)
        
        cur.execute("UPDATE accounts SET balance=%s WHERE acc_no=%s", (balance, acc))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """, (acc, 'RD_INTEREST', interest_earned, session['username'], 
              f'Interest calculated for {months} months'))
        
        con.commit()
        
        logger.info('RD', 'interest', 
                   f'RD interest applied: {interest_earned} for {acc}', acc_no=acc)
        print("\n✅ RD Interest Applied Successfully")
        print(f"Total Installments: {months}")
        print(f"Total Deposits: {monthly * months}")
        print(f"Interest Earned: {round(interest_earned, 2)}")
        print(f"Maturity Amount: {round(balance, 2)}")
    
    except Exception as e:
        con.rollback()
        logger.error('RD', 'interest', f'RD interest failed: {str(e)}', 
                    acc_no=acc, error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

def rd_to_sb_transfer():
    logger.info('RD', 'maturity_transfer', 'RD maturity transfer started')
    rd = input("RD Account Number: ")
    sb = input("SB Account Number: ")
    rate = Decimal("6.7")
    
    try:
        cur.execute("""
            SELECT r.monthly_amount, r.months_completed, a.balance, a.status
            FROM rd_details r
            JOIN accounts a ON r.acc_no = a.acc_no
            WHERE r.acc_no=%s AND a.acc_type='RD'
        """, (rd,))
        rd_data = cur.fetchone()
        
        if not rd_data or rd_data[3] == "Closed":
            logger.warning('RD', 'maturity_transfer', f'Invalid/Closed RD: {rd}', acc_no=rd)
            print("❌ Invalid / Closed RD Account")
            return
        
        monthly = Decimal(rd_data[0])
        months = rd_data[1]
        
        if months < 36:
            logger.warning('RD', 'maturity_transfer', 
                         f'RD cannot be closed before 36 months: {rd}', acc_no=rd)
            print("❌ RD cannot be closed before 36 months")
            return
        
        balance = Decimal("0")
        for m in range(1, months + 1):
            balance += monthly
            interest = (balance * rate) / Decimal("1200")
            balance += interest
        
        cur.execute("SELECT status FROM accounts WHERE acc_no=%s AND acc_type='SB'", (sb,))
        sb_data = cur.fetchone()
        
        if not sb_data or sb_data[0] == "Closed":
            logger.warning('RD', 'maturity_transfer', f'Invalid/Closed SB: {sb}', acc_no=sb)
            print("❌ Invalid / Closed SB Account")
            return
        
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no=%s", (balance, sb))
        cur.execute("UPDATE accounts SET balance = 0, status='Closed' WHERE acc_no=%s", (rd,))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """, (rd, 'RD_MATURITY_TRANSFER', balance, session['username'], 
              f'Transferred to SB: {sb}'))
        
        con.commit()
        
        logger.info('RD', 'maturity_transfer', 
                   f'RD maturity transferred: {rd} -> {sb}, Amount: {balance}', acc_no=rd)
        print("\n✅ RD Maturity Transfer Successful")
        print(f"Installments: {months}")
        print(f"Total Deposits: {monthly * months}")
        print(f"Maturity Amount: {round(balance, 2)}")
    
    except Exception as e:
        con.rollback()
        logger.error('RD', 'maturity_transfer', f'Transfer failed: {str(e)}', 
                    acc_no=rd if 'rd' in locals() else None, 
                    error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

# ================= TD OPERATIONS =================

def nsc_maturity_transfer():
    logger.info('NSC', 'maturity_transfer', 'NSC maturity transfer started')
    print("\n=== NSC MATURITY TRANSFER ===")
    
    nsc = input("NSC Account Number: ").strip()
    sb = input("SB Account Number to credit maturity amount: ").strip()
    
    try:
        # Fetch NSC details
        cur.execute("""
            SELECT n.tenure_months, n.interest_rate, n.maturity_date, a.balance, a.status
            FROM nsc_details n
            JOIN accounts a ON n.acc_no = a.acc_no
            WHERE n.acc_no=%s AND a.acc_type='NSC'
        """, (nsc,))
        nsc_data = cur.fetchone()
        
        if not nsc_data:
            logger.warning('NSC', 'maturity_transfer', f'NSC not found: {nsc}', acc_no=nsc)
            print("❌ NSC Account not found")
            return
        
        tenure_months, rate, maturity_date, principal, status = nsc_data
        
        if status == "Closed":
            logger.warning('NSC', 'maturity_transfer', f'NSC already closed: {nsc}', acc_no=nsc)
            print("❌ NSC Account already closed")
            return
        
        # Check maturity
        current_date = datetime.now().date()  # Convert to date only
        maturity_date_only = maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date
        
        if current_date < maturity_date_only:
            days_left = (maturity_date_only - current_date).days
            logger.warning('NSC', 'maturity_transfer', 
                         f'NSC not yet matured: {nsc}, Maturity: {maturity_date_only}, Days left: {days_left}', acc_no=nsc)
            print(f"⚠️  NSC not yet matured!")
            print(f"Maturity Date: {maturity_date_only}")
            print(f"Current Date: {current_date}")
            print(f"Days remaining: {days_left}")
            
            # Allow override for testing/special cases
            override = input("\n⚠️  Proceed with premature transfer anyway? (yes/no): ").lower().strip()
            if override != 'yes':
                print("❌ Transfer cancelled")
                return
            print("⚠️  Proceeding with premature transfer...")
        
        principal = Decimal(principal)
        rate = Decimal(rate)
        years = Decimal(tenure_months) / Decimal(12)
        
        # Fetch SB account
        cur.execute("SELECT status FROM accounts WHERE acc_no=%s AND acc_type='SB'", (sb,))
        sb_data = cur.fetchone()
        
        if not sb_data:
            logger.warning('NSC', 'maturity_transfer', f'SB not found: {sb}', acc_no=sb)
            print("❌ SB Account not found")
            return
        
        if sb_data[0] == "Closed":
            logger.warning('NSC', 'maturity_transfer', f'SB closed: {sb}', acc_no=sb)
            print("❌ SB Account is closed")
            return
        
        # Calculate maturity amount with compound interest
        maturity_amount = principal * ((1 + rate/100) ** years)
        interest = maturity_amount - principal
        
        # Transfer to SB
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no=%s", 
                   (maturity_amount, sb))
        cur.execute("UPDATE accounts SET balance = 0, status='Closed' WHERE acc_no=%s", (nsc,))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """, (nsc, 'NSC_MATURITY_TRANSFER', maturity_amount, session['username'], 
              f'Transferred to SB: {sb}'))
        
        con.commit()
        
        logger.info('NSC', 'maturity_transfer', 
                   f'NSC maturity transferred: {nsc} -> {sb}, Amount: {maturity_amount}', acc_no=nsc)
        print("\n✅ NSC Maturity Transfer Successful")
        print(f"Principal: ₹{round(principal, 2)}")
        print(f"Interest @ {rate}%: ₹{round(interest, 2)}")
        print(f"Total Credited to SB: ₹{round(maturity_amount, 2)}")
    
    except Exception as e:
        con.rollback()
        logger.error('NSC', 'maturity_transfer', f'NSC transfer failed: {str(e)}', 
                    acc_no=nsc if 'nsc' in locals() else None, 
                    error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

def kvp_maturity_transfer():
    logger.info('KVP', 'maturity_transfer', 'KVP maturity transfer started')
    print("\n=== KVP MATURITY TRANSFER ===")
    
    kvp = input("KVP Account Number: ").strip()
    sb = input("SB Account Number to credit maturity amount: ").strip()
    
    try:
        # Fetch KVP details
        cur.execute("""
            SELECT k.maturity_period_months, k.interest_rate, k.maturity_date, a.balance, a.status
            FROM kvp_details k
            JOIN accounts a ON k.acc_no = a.acc_no
            WHERE k.acc_no=%s AND a.acc_type='KVP'
        """, (kvp,))
        kvp_data = cur.fetchone()
        
        if not kvp_data:
            logger.warning('KVP', 'maturity_transfer', f'KVP not found: {kvp}', acc_no=kvp)
            print("❌ KVP Account not found")
            return
        
        maturity_period, rate, maturity_date, principal, status = kvp_data
        
        if status == "Closed":
            logger.warning('KVP', 'maturity_transfer', f'KVP already closed: {kvp}', acc_no=kvp)
            print("❌ KVP Account already closed")
            return
        
        # Check maturity
        current_date = datetime.now().date()  # Convert to date only
        maturity_date_only = maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date
        
        if current_date < maturity_date_only:
            days_left = (maturity_date_only - current_date).days
            logger.warning('KVP', 'maturity_transfer', 
                         f'KVP not yet matured: {kvp}, Maturity: {maturity_date_only}, Days left: {days_left}', acc_no=kvp)
            print(f"⚠️  KVP not yet matured!")
            print(f"Maturity Date: {maturity_date_only}")
            print(f"Current Date: {current_date}")
            print(f"Days remaining: {days_left}")
            
            # Allow override for testing/special cases
            override = input("\n⚠️  Proceed with premature transfer anyway? (yes/no): ").lower().strip()
            if override != 'yes':
                print("❌ Transfer cancelled")
                return
            print("⚠️  Proceeding with premature transfer...")
        
        principal = Decimal(principal)
        
        # KVP doubles the amount
        maturity_amount = principal * 2
        interest = maturity_amount - principal
        
        # Fetch SB account
        cur.execute("SELECT status FROM accounts WHERE acc_no=%s AND acc_type='SB'", (sb,))
        sb_data = cur.fetchone()
        
        if not sb_data:
            logger.warning('KVP', 'maturity_transfer', f'SB not found: {sb}', acc_no=sb)
            print("❌ SB Account not found")
            return
        
        if sb_data[0] == "Closed":
            logger.warning('KVP', 'maturity_transfer', f'SB closed: {sb}', acc_no=sb)
            print("❌ SB Account is closed")
            return
        
        # Transfer to SB
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no=%s", 
                   (maturity_amount, sb))
        cur.execute("UPDATE accounts SET balance = 0, status='Closed' WHERE acc_no=%s", (kvp,))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """, (kvp, 'KVP_MATURITY_TRANSFER', maturity_amount, session['username'], 
              f'Transferred to SB: {sb}'))
        
        con.commit()
        
        logger.info('KVP', 'maturity_transfer', 
                   f'KVP maturity transferred: {kvp} -> {sb}, Amount: {maturity_amount}', acc_no=kvp)
        print("\n✅ KVP Maturity Transfer Successful")
        print(f"Principal: ₹{round(principal, 2)}")
        print(f"Interest (Doubled): ₹{round(interest, 2)}")
        print(f"Total Credited to SB: ₹{round(maturity_amount, 2)}")
        print(f"Maturity Period: {maturity_period} months (~{round(maturity_period/12, 1)} years)")
    
    except Exception as e:
        con.rollback()
        logger.error('KVP', 'maturity_transfer', f'KVP transfer failed: {str(e)}', 
                    acc_no=kvp if 'kvp' in locals() else None, 
                    error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

# ================= TD OPERATIONS =================

def td_maturity_transfer():
    logger.info('TD', 'maturity_transfer', 'TD maturity transfer started')
    print("\n=== TD MATURITY TRANSFER ===")
    
    td = input("TD Account Number: ").strip()
    sb = input("SB Account Number: ").strip()
    
    try:
        cur.execute("""
            SELECT t.tenure_months, t.interest_rate, t.maturity_date, a.balance, a.status
            FROM td_details t
            JOIN accounts a ON t.acc_no = a.acc_no
            WHERE t.acc_no=%s AND a.acc_type='TD'
        """, (td,))
        td_data = cur.fetchone()
        
        if not td_data:
            logger.warning('TD', 'maturity_transfer', f'TD not found: {td}', acc_no=td)
            print("❌ TD Account not found")
            return
        
        tenure_months, rate, maturity_date, principal, status = td_data
        
        if status == "Closed":
            logger.warning('TD', 'maturity_transfer', f'TD already closed: {td}', acc_no=td)
            print("❌ TD Account already closed")
            return
        
        # Check if matured
        current_date = datetime.now().date()  # Convert to date only
        maturity_date_only = maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date
        
        if current_date < maturity_date_only:
            days_left = (maturity_date_only - current_date).days
            logger.warning('TD', 'maturity_transfer', 
                         f'TD not yet matured: {td}, Maturity: {maturity_date_only}, Days left: {days_left}', acc_no=td)
            print(f"⚠️  TD not yet matured!")
            print(f"Maturity Date: {maturity_date_only}")
            print(f"Current Date: {current_date}")
            print(f"Days remaining: {days_left}")
            
            # Allow override for testing/special cases
            override = input("\n⚠️  Proceed with premature transfer anyway? (yes/no): ").lower().strip()
            if override != 'yes':
                print("❌ Transfer cancelled")
                return
            print("⚠️  Proceeding with premature transfer...")
        
        principal = Decimal(principal)
        rate = Decimal(rate)
        years = Decimal(tenure_months) / Decimal(12)
        
        cur.execute("SELECT status FROM accounts WHERE acc_no=%s AND acc_type='SB'", (sb,))
        sb_data = cur.fetchone()
        
        if not sb_data:
            logger.warning('TD', 'maturity_transfer', f'SB not found: {sb}', acc_no=sb)
            print("❌ SB Account not found")
            return
        
        if sb_data[0] == "Closed":
            logger.warning('TD', 'maturity_transfer', f'SB closed: {sb}', acc_no=sb)
            print("❌ SB Account is closed")
            return
        
        maturity_amount = principal * ((1 + rate/100) ** years)
        interest = maturity_amount - principal
        
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no=%s", 
                   (maturity_amount, sb))
        cur.execute("UPDATE accounts SET balance = 0, status='Closed' WHERE acc_no=%s", (td,))
        
        cur.execute("""
            INSERT INTO transactions (acc_no, txn_type, amount, performed_by, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """, (td, 'TD_MATURITY_TRANSFER', maturity_amount, session['username'], 
              f'Transferred to SB: {sb}'))
        
        con.commit()
        
        logger.info('TD', 'maturity_transfer', 
                   f'TD maturity transferred: {td} -> {sb}, Amount: {maturity_amount}', acc_no=td)
        print("\n✅ TD Maturity Transfer Successful")
        print(f"Principal: {round(principal, 2)}")
        print(f"Interest @ {rate}%: {round(interest, 2)}")
        print(f"Total Credited to SB: {round(maturity_amount, 2)}")
    
    except Exception as e:
        con.rollback()
        logger.error('TD', 'maturity_transfer', f'TD transfer failed: {str(e)}', 
                    acc_no=td if 'td' in locals() else None, 
                    error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

# ================= SCHEME MENUS =================

def view_matured_accounts():
    """View all accounts that have matured and can be transferred to SB"""
    logger.info('Account', 'view_matured', 'Viewing matured accounts')
    print("\n=== MATURED ACCOUNTS ===")
    
    try:
        current_date = datetime.now().date()  # Convert to date only
        
        # TD Matured Accounts
        cur.execute("""
            SELECT a.acc_no, a.name, t.tenure_months, t.interest_rate, t.maturity_date, a.balance
            FROM td_details t
            JOIN accounts a ON t.acc_no = a.acc_no
            WHERE a.status = 'Active' AND t.maturity_date <= %s
            ORDER BY t.maturity_date
        """, (current_date,))
        td_matured = cur.fetchall()
        
        # NSC Matured Accounts
        cur.execute("""
            SELECT a.acc_no, a.name, n.tenure_months, n.interest_rate, n.maturity_date, a.balance
            FROM nsc_details n
            JOIN accounts a ON n.acc_no = a.acc_no
            WHERE a.status = 'Active' AND n.maturity_date <= %s
            ORDER BY n.maturity_date
        """, (current_date,))
        nsc_matured = cur.fetchall()
        
        # KVP Matured Accounts
        cur.execute("""
            SELECT a.acc_no, a.name, k.maturity_period_months, k.interest_rate, k.maturity_date, a.balance
            FROM kvp_details k
            JOIN accounts a ON k.acc_no = a.acc_no
            WHERE a.status = 'Active' AND k.maturity_date <= %s
            ORDER BY k.maturity_date
        """, (current_date,))
        kvp_matured = cur.fetchall()
        
        total_matured = len(td_matured) + len(nsc_matured) + len(kvp_matured)
        
        if total_matured == 0:
            print("\n✅ No matured accounts found")
            return
        
        print(f"\n🎉 Total Matured Accounts: {total_matured}")
        print("=" * 80)
        
        if td_matured:
            print("\n📊 TIME DEPOSIT (TD) - MATURED")
            print("-" * 80)
            print(f"{'Acc No':<15} {'Name':<20} {'Tenure':<10} {'Rate':<8} {'Maturity Date':<15} {'Amount':<12}")
            print("-" * 80)
            for acc in td_matured:
                acc_no, name, tenure, rate, mat_date, balance = acc
                principal = Decimal(balance)
                years = Decimal(tenure) / Decimal(12)
                maturity_amt = principal * ((1 + Decimal(rate)/100) ** years)
                print(f"{acc_no:<15} {name:<20} {tenure}M {rate}% {str(mat_date.date()):<15} ₹{round(maturity_amt, 2):<12}")
        
        if nsc_matured:
            print("\n📊 NATIONAL SAVINGS CERTIFICATE (NSC) - MATURED")
            print("-" * 80)
            print(f"{'Acc No':<15} {'Name':<20} {'Tenure':<10} {'Rate':<8} {'Maturity Date':<15} {'Amount':<12}")
            print("-" * 80)
            for acc in nsc_matured:
                acc_no, name, tenure, rate, mat_date, balance = acc
                principal = Decimal(balance)
                years = Decimal(tenure) / Decimal(12)
                maturity_amt = principal * ((1 + Decimal(rate)/100) ** years)
                print(f"{acc_no:<15} {name:<20} {tenure}M {rate}% {str(mat_date.date()):<15} ₹{round(maturity_amt, 2):<12}")
        
        if kvp_matured:
            print("\n📊 KISAN VIKAS PATRA (KVP) - MATURED")
            print("-" * 80)
            print(f"{'Acc No':<15} {'Name':<20} {'Period':<10} {'Rate':<8} {'Maturity Date':<15} {'Amount':<12}")
            print("-" * 80)
            for acc in kvp_matured:
                acc_no, name, period, rate, mat_date, balance = acc
                principal = Decimal(balance)
                maturity_amt = principal * 2  # KVP doubles
                print(f"{acc_no:<15} {name:<20} {period}M {rate}% {str(mat_date.date()):<15} ₹{round(maturity_amt, 2):<12}")
        
        print("\n" + "=" * 80)
        print("💡 Tip: Use Schemes Menu to transfer matured amounts to SB account")
    
    except Exception as e:
        logger.error('Account', 'view_matured', f'Error viewing matured accounts: {str(e)}', 
                    error_details=traceback.format_exc())
        print(f"❌ Error: {e}")

# ================= SCHEME MENUS =================

def rd_menu():
    while True:
        print("""
=== RD SCHEME ===
1. Monthly RD Deposit
2. RD Compound Interest
3. RD Maturity Transfer
4. RD Scheme Info
0. Back
""")
        ch = input("Choice: ").strip()
        
        if ch == '1':
            rd_monthly_deposit()
        elif ch == '2':
            rd_compound_interest()
        elif ch == '3':
            rd_to_sb_transfer()
        elif ch == '4':
            rd_info()
        elif ch == '0':
            break

def sb_menu():
    while True:
        print("""
=== SB SCHEME ===
1. Deposit
2. Withdraw
3. Account Closure
4. SB Scheme Info
0. Back
""")
        ch = input("Choice: ").strip()
        
        if ch == '1':
            deposit()
        elif ch == '2':
            withdraw()
        elif ch == '3':
            close_account()
        elif ch == '4':
            sb_info()
        elif ch == '0':
            break

def td_menu():
    while True:
        print("""
=== TD SCHEME ===
1. TD Maturity Transfer to SB
2. View TD Details
3. TD Scheme Info
0. Back
""")
        ch = input("Choice: ").strip()
        
        if ch == '1':
            td_maturity_transfer()
        elif ch == '2':
            acc = input("TD Account Number: ")
            try:
                cur.execute("""
                    SELECT t.tenure_months, t.interest_rate, t.maturity_date, a.balance, a.status, a.created_on
                    FROM td_details t
                    JOIN accounts a ON t.acc_no = a.acc_no
                    WHERE t.acc_no=%s
                """, (acc,))
                data = cur.fetchone()
                if data:
                    tenure, rate, maturity_date, balance, status, created = data
                    principal = Decimal(balance)
                    years = Decimal(tenure) / Decimal(12)
                    maturity_amount = principal * ((1 + Decimal(rate)/100) ** years)
                    
                    print("\n✅ TD ACCOUNT DETAILS")
                    print("═" * 50)
                    print(f"Account Number  : {acc}")
                    print(f"Status          : {status}")
                    print(f"Opened On       : {created}")
                    print(f"Principal Amount: ₹{round(principal, 2)}")
                    print(f"Tenure          : {tenure} months ({tenure//12} years)")
                    print(f"Interest Rate   : {rate}%")
                    print(f"Maturity Date   : {maturity_date.date()}")
                    print(f"Maturity Amount : ₹{round(maturity_amount, 2)}")
                    print(f"Interest Earned : ₹{round(maturity_amount - principal, 2)}")
                    
                    if datetime.now().date() >= (maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date):
                        print("\n🎉 TD HAS MATURED! You can transfer to SB.")
                    else:
                        maturity_date_only = maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date
                        days_left = (maturity_date_only - datetime.now().date()).days
                        print(f"\n⏰ Days until maturity: {days_left}")
                else:
                    print("❌ TD account not found")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif ch == '3':
            td_info()
        elif ch == '0':
            break
        else:
            print("❌ Invalid choice")

def nsc_menu():
    while True:
        print("""
=== NSC SCHEME ===
1. NSC Maturity Transfer to SB
2. View NSC Details
3. NSC Scheme Info
0. Back
""")
        ch = input("Choice: ").strip()
        
        if ch == '1':
            nsc_maturity_transfer()
        elif ch == '2':
            acc = input("NSC Account Number: ")
            try:
                cur.execute("""
                    SELECT n.tenure_months, n.interest_rate, n.maturity_date, a.balance, a.status, a.created_on
                    FROM nsc_details n
                    JOIN accounts a ON n.acc_no = a.acc_no
                    WHERE n.acc_no=%s
                """, (acc,))
                data = cur.fetchone()
                if data:
                    tenure, rate, maturity_date, balance, status, created = data
                    principal = Decimal(balance)
                    years = Decimal(tenure) / Decimal(12)
                    maturity_amount = principal * ((1 + Decimal(rate)/100) ** years)
                    
                    print("\n✅ NSC ACCOUNT DETAILS")
                    print("═" * 50)
                    print(f"Account Number  : {acc}")
                    print(f"Status          : {status}")
                    print(f"Opened On       : {created}")
                    print(f"Principal Amount: ₹{round(principal, 2)}")
                    print(f"Tenure          : {tenure} months ({tenure//12} years)")
                    print(f"Interest Rate   : {rate}%")
                    print(f"Maturity Date   : {maturity_date.date()}")
                    print(f"Maturity Amount : ₹{round(maturity_amount, 2)}")
                    print(f"Interest Earned : ₹{round(maturity_amount - principal, 2)}")
                    
                    if datetime.now().date() >= (maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date):
                        print("\n🎉 NSC HAS MATURED! You can transfer to SB.")
                    else:
                        maturity_date_only = maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date
                        days_left = (maturity_date_only - datetime.now().date()).days
                        print(f"\n⏰ Days until maturity: {days_left}")
                else:
                    print("❌ NSC account not found")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif ch == '3':
            nsc_info()
        elif ch == '0':
            break
        else:
            print("❌ Invalid choice")

def kvp_menu():
    while True:
        print("""
=== KVP SCHEME ===
1. KVP Maturity Transfer to SB
2. View KVP Details
3. KVP Scheme Info
0. Back
""")
        ch = input("Choice: ").strip()
        
        if ch == '1':
            kvp_maturity_transfer()
        elif ch == '2':
            acc = input("KVP Account Number: ")
            try:
                cur.execute("""
                    SELECT k.maturity_period_months, k.interest_rate, k.maturity_date, a.balance, a.status, a.created_on
                    FROM kvp_details k
                    JOIN accounts a ON k.acc_no = a.acc_no
                    WHERE k.acc_no=%s
                """, (acc,))
                data = cur.fetchone()
                if data:
                    period, rate, maturity_date, balance, status, created = data
                    principal = Decimal(balance)
                    maturity_amount = principal * 2  # KVP doubles the amount
                    
                    print("\n✅ KVP ACCOUNT DETAILS")
                    print("═" * 50)
                    print(f"Account Number    : {acc}")
                    print(f"Status            : {status}")
                    print(f"Opened On         : {created}")
                    print(f"Principal Amount  : ₹{round(principal, 2)}")
                    print(f"Maturity Period   : {period} months (~{round(period/12, 1)} years)")
                    print(f"Interest Rate     : {rate}%")
                    print(f"Maturity Date     : {maturity_date.date()}")
                    print(f"Maturity Amount   : ₹{round(maturity_amount, 2)} (Doubled)")
                    print(f"Interest Earned   : ₹{round(maturity_amount - principal, 2)}")
                    
                    if datetime.now().date() >= (maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date):
                        print("\n🎉 KVP HAS MATURED! You can transfer to SB.")
                    else:
                        maturity_date_only = maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date
                        days_left = (maturity_date_only - datetime.now().date()).days
                        print(f"\n⏰ Days until maturity: {days_left}")
                else:
                    print("❌ KVP account not found")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif ch == '3':
            kvp_info()
        elif ch == '0':
            break
        else:
            print("❌ Invalid choice")

def schemes_menu():
    while True:
        print("""
=== SCHEMES ===
1. RD Scheme
2. SB Scheme
3. TD Scheme
4. NSC Scheme
5. KVP Scheme
0. Back
""")
        ch = input("Choice: ")
        
        if ch == '1':
            rd_menu()
        elif ch == '2':
            sb_menu()
        elif ch == '3':
            td_menu()
        elif ch == '4':
            nsc_menu()
        elif ch == '5':
            kvp_menu()
        elif ch == '0':
            break

def forms_menu():
    while True:
        print("\n=== POST OFFICE FORMS ===")
        
        form_names = list(FORMS_LOCAL.keys())
        
        for i, form_name in enumerate(form_names, start=1):
            print(f"{i}. {form_name}")
        
        print("0. Back")
        
        choice = input("Enter choice: ").strip()
        
        if choice == "0":
            break
        
        if not choice.isdigit():
            print("❌ Invalid input")
            continue
        
        idx = int(choice)
        
        if idx < 1 or idx > len(form_names):
            print("❌ Invalid choice")
            continue
        
        selected_form = form_names[idx - 1]
        relative_path = FORMS_LOCAL[selected_form]
        abs_path = os.path.abspath(relative_path)
        
        if not os.path.exists(abs_path):
            print("❌ Form file not found!")
            continue
        
        print(f"\n✅ Opening Form: {selected_form}")
        webbrowser.open("file://" + abs_path)

# ================= MAIN MENU =================

def main_menu():
    global session
    
    try:
        while True:
            print("""
=== POST OFFICE ACCOUNT SYSTEM ===
1. Open Account
2. Deposit
3. Withdraw
4. Balance Enquiry
5. Search Account
6. Close Account
7. Schemes Menu
8. View Matured Accounts 🎉
9. Post Office Forms
10. Logout
0. Exit
""")
            
            ch = input("Enter Choice: ").strip()
            
            if ch == '1':
                create_account()
            elif ch == '2':
                deposit()
            elif ch == '3':
                withdraw()
            elif ch == '4':
                balance_enquiry()
            elif ch == '5':
                search_account()
            elif ch == '6':
                close_account()
            elif ch == '7':
                schemes_menu()
            elif ch == '8':
                view_matured_accounts()
            elif ch == '9':
                forms_menu()
            elif ch == '10':
                logger.info('System', 'main_menu', f'User logged out: {session["username"]}')
                print("\n✅ Logged out successfully!\n")
                session = login()
                if not session:
                    break
                logger.set_user(session['username'])
            elif ch == '0':
                logger.info('System', 'main_menu', 'Program exited normally')
                print("✅ Exiting program...")
                break
            else:
                print("❌ Invalid Choice")
    
    except KeyboardInterrupt:
        logger.info('System', 'main_menu', 'Program interrupted by user')
        print("\n✅ Exiting program...")
    
    finally:
        try:
            cur.close()
            con.close()
            logger.info('System', 'shutdown', 'Database connection closed')
        except:
            pass

# ================= PROGRAM START =================

session = login()
if not session:
    print("✅ Exiting program...")
    exit()

logger.set_user(session['username'])
main_menu()
