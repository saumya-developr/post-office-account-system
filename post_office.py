import mysql.connector
import random
import math

# ================= DATABASE CONNECTION =================
print("Program started")

try:
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",   # <-- change this
        database="post_office",
        port=3307,
        connection_timeout=5
    )
    cur = con.cursor()
    print("Database connected")
except:
    print("ERROR: Database not connected")
    input("Press Enter to exit")
    exit()

# ================= UTILITY FUNCTIONS =================

def generate_account_number(acc_type):
    prefix = {"SB": "010", "RD": "020", "TD": "030"}
    return prefix[acc_type] + str(random.randint(1000000, 9999999))

def is_valid_mobile(mobile):
    return mobile.isdigit() and len(mobile) == 10

# ================= BASIC OPERATIONS =================

def create_account():
    name = input("Name: ")
    address = input("Address: ")

    mobile = input("Mobile Number: ")
    if not is_valid_mobile(mobile):
        print("Invalid phone number")
        return

    acc_type = input("Account Type (SB/RD/TD): ").upper()
    acc_no = generate_account_number(acc_type)

    if acc_type == "SB":
        balance = float(input("Opening Balance (Min 500): "))
        if balance < 500:
            print("Minimum opening balance for SB is 500")
            return

    elif acc_type == "RD":
        monthly = float(input("Monthly RD Amount: "))
        balance = monthly        # first installment
        months = 1

    elif acc_type == "TD":
        balance = float(input("TD Lump Sum Amount: "))

    else:
        print("Invalid account type")
        return

    cur.execute(
        "INSERT INTO accounts VALUES (%s,%s,%s,%s,%s,%s,'Active')",
        (acc_no, name, address, mobile, acc_type, balance)
    )

    if acc_type == "RD":
        cur.execute(
            "INSERT INTO rd_details VALUES (%s,%s,%s)",
            (acc_no, monthly, months)
        )

    con.commit()
    print("Account Created Successfully")
    print("Account Number:", acc_no)

# ----------------------------------------------------

def deposit():
    acc = input("Account Number: ")
    amt = float(input("Amount: "))

    cur.execute("SELECT status FROM accounts WHERE acc_no=%s", (acc,))
    d = cur.fetchone()

    if not d or d[0] == "Closed":
        print("Invalid / Closed Account")
        return

    cur.execute("UPDATE accounts SET balance=balance+%s WHERE acc_no=%s", (amt, acc))
    con.commit()
    print("Deposit Successful")

# ----------------------------------------------------

def withdraw():
    acc = input("Account Number: ")
    amt = float(input("Amount: "))

    cur.execute("SELECT balance,acc_type,status FROM accounts WHERE acc_no=%s", (acc,))
    d = cur.fetchone()

    if not d or d[2] == "Closed":
        print("Invalid / Closed Account")
        return

    balance = float(d[0])
    acc_type = d[1]
    min_bal = 500 if acc_type == "SB" else 0

    if balance - amt < min_bal:
        print("Minimum balance rule violated")
        return

    cur.execute("UPDATE accounts SET balance=balance-%s WHERE acc_no=%s", (amt, acc))
    con.commit()
    print("Withdrawal Successful")

# ----------------------------------------------------

def balance_enquiry():
    acc = input("Account Number: ")
    cur.execute("SELECT name,balance,status FROM accounts WHERE acc_no=%s", (acc,))
    d = cur.fetchone()

    if d:
        print("Name:", d[0])
        print("Balance:", d[1])
        print("Status:", d[2])
    else:
        print("Account not found")

# ----------------------------------------------------

def calculate_interest():
    acc = input("Account Number: ")
    rate = 5

    cur.execute("SELECT balance,status FROM accounts WHERE acc_no=%s", (acc,))
    d = cur.fetchone()

    if not d or d[1] == "Closed":
        print("Invalid / Closed Account")
        return

    interest = (float(d[0]) * rate) / 100
    cur.execute("UPDATE accounts SET balance=balance+%s WHERE acc_no=%s", (interest, acc))
    con.commit()
    print("Interest Added:", interest)

# ----------------------------------------------------

def search_account():
    mobile = input("Mobile Number: ")
    cur.execute("SELECT acc_no,name,acc_type,balance FROM accounts WHERE mobile=%s", (mobile,))
    rows = cur.fetchall()

    if not rows:
        print("No accounts found")
        return

    for r in rows:
        print(r)

# ----------------------------------------------------

def close_account():
    acc = input("Account Number: ")
    cur.execute("UPDATE accounts SET status='Closed' WHERE acc_no=%s", (acc,))
    con.commit()
    print("Account Closed")

# ================= RD SCHEME =================

def rd_monthly_deposit():
    acc = input("RD Account Number: ")

    cur.execute("""
        SELECT r.monthly_amount,a.status
        FROM rd_details r JOIN accounts a ON r.acc_no=a.acc_no
        WHERE r.acc_no=%s
    """, (acc,))
    d = cur.fetchone()

    if not d or d[1] == "Closed":
        print("Invalid / Closed RD Account")
        return

    cur.execute("UPDATE accounts SET balance=balance+%s WHERE acc_no=%s", (d[0], acc))
    cur.execute("UPDATE rd_details SET months_completed=months_completed+1 WHERE acc_no=%s", (acc,))
    con.commit()
    print("RD Monthly Deposit Successful")

# ----------------------------------------------------

def rd_compound_interest():
    acc = input("RD Account Number: ")
    rate = 5.8

    cur.execute("""
        SELECT a.balance,r.months_completed,a.status
        FROM accounts a JOIN rd_details r ON a.acc_no=r.acc_no
        WHERE a.acc_no=%s
    """, (acc,))
    d = cur.fetchone()

    if not d or d[2] == "Closed":
        print("Invalid / Closed RD Account")
        return

    balance = float(d[0])
    months = d[1]
    t = months / 12

    maturity = balance * ((1 + rate/100) ** t)
    cur.execute("UPDATE accounts SET balance=%s WHERE acc_no=%s", (maturity, acc))
    con.commit()

    print("RD Compound Interest Applied")
    print("Maturity Amount:", round(maturity,2))

# ----------------------------------------------------

def rd_schedule():
    acc = input("RD Account Number: ")
    rate = 5.8

    cur.execute("""
        SELECT a.balance,r.months_completed,r.monthly_amount,a.status
        FROM accounts a JOIN rd_details r ON a.acc_no=r.acc_no
        WHERE a.acc_no=%s
    """, (acc,))
    d = cur.fetchone()

    if not d or d[3] == "Closed":
        print("Invalid / Closed RD Account")
        return

    balance = float(d[0])
    months = d[1]
    monthly = float(d[2])

    print("\nMONTH | DEPOSIT | INTEREST | BALANCE")
    print("------------------------------------")

    for m in range(1, months + 1):
        interest = (balance * rate) / (12 * 100)
        balance = balance + interest + monthly
        print(m, "|", monthly, "|", round(interest,2), "|", round(balance,2))

# ----------------------------------------------------

def rd_to_sb_transfer():
    rd = input("RD Account Number: ")
    sb = input("SB Account Number: ")

    cur.execute("SELECT balance,status FROM accounts WHERE acc_no=%s AND acc_type='RD'", (rd,))
    r = cur.fetchone()

    if not r or r[1] == "Closed":
        print("Invalid RD Account")
        return

    cur.execute("UPDATE accounts SET balance=balance+%s WHERE acc_no=%s", (r[0], sb))
    cur.execute("UPDATE accounts SET balance=0,status='Closed' WHERE acc_no=%s", (rd,))
    con.commit()
    print("RD Maturity Amount Transferred to SB")

# ================= SCHEME MENUS =================

def rd_menu():
    while True:
        print("""
--- RD SCHEME ---
1. Monthly RD Deposit
2. RD Compound Interest
3. RD Schedule
4. RD Maturity Transfer
0. Back
""")
        ch = input("Choice: ")
        if ch == '1': rd_monthly_deposit()
        elif ch == '2': rd_compound_interest()
        elif ch == '3': rd_schedule()
        elif ch == '4': rd_to_sb_transfer()
        elif ch == '0': break

def sb_menu():
    while True:
        print("""
--- SB SCHEME ---
1. Deposit
2. Withdraw
3. Interest
4. Account Closure
0. Back
""")
        ch = input("Choice: ")
        if ch == '1': deposit()
        elif ch == '2': withdraw()
        elif ch == '3': calculate_interest()
        elif ch == '4': close_account()
        elif ch == '0': break

def td_menu():
    while True:
        print("""
--- TD SCHEME ---
1. Interest Calculation
2. Maturity Closure
0. Back
""")
        ch = input("Choice: ")
        if ch == '1': calculate_interest()
        elif ch == '2': close_account()
        elif ch == '0': break

def schemes_menu():
    while True:
        print("""
--- SCHEMES ---
1. RD Scheme
2. SB Scheme
3. TD Scheme
0. Back
""")
        ch = input("Choice: ")
        if ch == '1': rd_menu()
        elif ch == '2': sb_menu()
        elif ch == '3': td_menu()
        elif ch == '0': break

# ================= MAIN MENU =================

while True:
    print("""
=== POST OFFICE ACCOUNT SYSTEM ===
1. Open Account
2. Deposit
3. Withdraw
4. Balance Enquiry
5. Interest Calculation
6. Search Account
7. Close Account
8. Schemes Menu
0. Exit
""")

    ch = input("Enter Choice: ")

    if ch == '1': create_account()
    elif ch == '2': deposit()
    elif ch == '3': withdraw()
    elif ch == '4': balance_enquiry()
    elif ch == '5': calculate_interest()
    elif ch == '6': search_account()
    elif ch == '7': close_account()
    elif ch == '8': schemes_menu()
    elif ch == '0':
        print("Thank You")
        break
    else:
        print("Invalid Choice")
