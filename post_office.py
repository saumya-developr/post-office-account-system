import mysql.connector
import random
import math

# ================= DATABASE =================
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="post_office",
    port=3307
)
cur = con.cursor()

# ================= UTIL =================
def generate_account_number(acc_type):
    prefix = {"SB": "010", "RD": "020", "TD": "030"}
    return prefix[acc_type] + str(random.randint(1000000, 9999999))

# ================= BASIC OPERATIONS =================

def create_account():
    name = input("Name: ")
    address = input("Address: ")
    mobile = input("Mobile: ")
    acc_type = input("Account Type (SB/RD/TD): ").upper()

    acc_no = generate_account_number(acc_type)
    balance = 0

    cur.execute(
        "INSERT INTO accounts VALUES (%s,%s,%s,%s,%s,%s,'Active')",
        (acc_no, name, address, mobile, acc_type, balance)
    )

    if acc_type == "RD":
        monthly = float(input("Monthly RD Amount: "))
        cur.execute("INSERT INTO rd_details VALUES (%s,%s,0)", (acc_no, monthly))

    con.commit()
    print("Account Created | Account No:", acc_no)

# ----------------------------------------------------

def deposit():
    acc = input("Account Number: ")
    amt = float(input("Amount: "))

    cur.execute("SELECT status FROM accounts WHERE acc_no=%s", (acc,))
    s = cur.fetchone()

    if s is None or s[0] == "Closed":
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

    if d is None or d[2] == "Closed":
        print("Invalid / Closed Account")
        return

    balance, acc_type, _ = d
    min_bal = 500 if acc_type == "SB" else 0

    if balance - amt < min_bal:
        print("Minimum Balance Rule Violated")
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
        print("Account Not Found")

# ----------------------------------------------------

def calculate_interest():
    acc = input("Account Number: ")
    rate = 5
    time = 1

    cur.execute("SELECT balance,status FROM accounts WHERE acc_no=%s", (acc,))
    d = cur.fetchone()

    if d is None or d[1] == "Closed":
        print("Invalid / Closed Account")
        return

    interest = (d[0] * rate * time) / 100
    cur.execute("UPDATE accounts SET balance=balance+%s WHERE acc_no=%s", (interest, acc))
    con.commit()
    print("Interest Added:", interest)

# ----------------------------------------------------

def search_account():
    print("1. By Mobile")
    print("2. By Name")
    ch = input("Choice: ")

    if ch == '1':
        mobile = input("Mobile: ")
        cur.execute("SELECT acc_no,name,acc_type,balance FROM accounts WHERE mobile=%s", (mobile,))
    elif ch == '2':
        name = input("Name: ")
        cur.execute("SELECT acc_no,name,acc_type,balance FROM accounts WHERE name LIKE %s", ('%'+name+'%',))
    else:
        return

    for r in cur.fetchall():
        print(r)

# ----------------------------------------------------

def close_account():
    acc = input("Account Number: ")
    cur.execute("UPDATE accounts SET status='Closed' WHERE acc_no=%s", (acc,))
    con.commit()
    print("Account Closed")

# ================= RD OPERATIONS =================

def rd_monthly_deposit():
    acc = input("RD Account Number: ")

    cur.execute("""
        SELECT r.monthly_amount, a.status
        FROM rd_details r JOIN accounts a ON r.acc_no=a.acc_no
        WHERE r.acc_no=%s
    """, (acc,))
    d = cur.fetchone()

    if d is None or d[1] == "Closed":
        print("Invalid / Closed RD")
        return

    cur.execute("UPDATE accounts SET balance=balance+%s WHERE acc_no=%s", (d[0], acc))
    cur.execute("UPDATE rd_details SET months_completed=months_completed+1 WHERE acc_no=%s", (acc,))
    con.commit()
    print("RD Monthly Deposit Done")

# ----------------------------------------------------

def rd_compound_interest():
    acc = input("RD Account Number: ")
    rate = 5.8

    cur.execute("""
        SELECT a.balance,r.months_completed
        FROM accounts a JOIN rd_details r ON a.acc_no=r.acc_no
        WHERE a.acc_no=%s
    """, (acc,))
    d = cur.fetchone()

    if d is None:
        print("RD Account Not Found")
        return

    bal, months = d
    t = months / 12
    maturity = bal * ((1 + rate/100) ** t)
    cur.execute("UPDATE accounts SET balance=%s WHERE acc_no=%s", (maturity, acc))
    con.commit()

    print("RD Interest Applied | Maturity:", round(maturity,2))

# ----------------------------------------------------

def rd_schedule():
    acc = input("RD Account Number: ")
    rate = 5.8

    cur.execute("""
        SELECT a.balance,r.months_completed,r.monthly_amount
        FROM accounts a JOIN rd_details r ON a.acc_no=r.acc_no
        WHERE a.acc_no=%s
    """, (acc,))
    d = cur.fetchone()

    if d is None:
        print("RD Account Not Found")
        return

    balance, months, monthly = d

    print("\nMONTH | DEPOSIT | INTEREST | BALANCE")
    for m in range(1, months+1):
        interest = (balance * rate) / (12 * 100)
        balance = balance + interest + monthly
        print(m, "|", monthly, "|", round(interest,2), "|", round(balance,2))

# ----------------------------------------------------

def rd_to_sb_transfer():
    rd = input("RD Account Number: ")
    sb = input("SB Account Number: ")

    cur.execute("SELECT balance FROM accounts WHERE acc_no=%s AND acc_type='RD'", (rd,))
    r = cur.fetchone()
    cur.execute("SELECT balance FROM accounts WHERE acc_no=%s AND acc_type='SB'", (sb,))
    s = cur.fetchone()

    if r is None or s is None:
        print("Invalid Accounts")
        return

    cur.execute("UPDATE accounts SET balance=balance+%s WHERE acc_no=%s", (r[0], sb))
    cur.execute("UPDATE accounts SET balance=0,status='Closed' WHERE acc_no=%s", (rd,))
    con.commit()
    print("RD Amount Transferred to SB")

# ================= RD SUB MENU =================

def rd_menu():
    while True:
        print("""
--- RD OPERATIONS ---
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

# ================= MAIN MENU =================

while True:
    print("""
=== POST OFFICE SYSTEM ===
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
    elif ch == '8': rd_menu()
    elif ch == '0':
        print("Thank You")
        break
    else:
        print("Invalid Choice")
