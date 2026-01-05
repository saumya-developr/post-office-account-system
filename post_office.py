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

    cur.execute(
        "SELECT status, acc_type FROM accounts WHERE acc_no=%s",
        (acc,)
    )
    d = cur.fetchone()

    if not d:
        print("Account not found")
        return

    status, acc_type = d

    if status == "Closed":
        print("Account is closed")
        return

    # 🔒 SCHEME VALIDATION FIRST
    if acc_type != "SB":
        print("Deposit allowed only in SB accounts")
        return

    # ✅ AMOUNT TAB HI POOCHO
    try:
        amt = float(input("Amount: "))
    except:
        print("Invalid amount")
        return

    cur.execute(
        "UPDATE accounts SET balance = balance + %s WHERE acc_no=%s",
        (amt, acc)
    )
    con.commit()
    print("SB Deposit Successful")


# ----------------------------------------------------

def withdraw():
    acc = input("Account Number: ")

    cur.execute(
        "SELECT balance, acc_type, status FROM accounts WHERE acc_no=%s",
        (acc,)
    )
    d = cur.fetchone()

    if not d:
        print("Account not found")
        return

    balance, acc_type, status = d

    if status == "Closed":
        print("Account is closed")
        return

    # 🔒 Withdraw only from SB
    if acc_type != "SB":
        print("Withdrawal allowed only from SB accounts")
        return

    # ✅ Amount tab hi poochho
    try:
        amt = float(input("Amount: "))
        if amt <= 0:
            print("Invalid amount")
            return
    except:
        print("Invalid amount")
        return

    if balance - amt < 500:
        print("Minimum balance of 500 must be maintained")
        return

    cur.execute(
        "UPDATE accounts SET balance = balance - %s WHERE acc_no=%s",
        (amt, acc)
    )
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

    cur.execute(
        "SELECT balance, status, acc_type FROM accounts WHERE acc_no=%s",
        (acc,)
    )
    d = cur.fetchone()

    if not d or d[1] == "Closed":
        print("Invalid / Closed Account")
        return

    balance = float(d[0])
    acc_type = d[2]

    # Interest rates as per 1 Oct 2025 – 31 Dec 2025
    if acc_type == "SB":
        rate = 4.0
        months = int(input("Enter number of months balance was maintained: "))

    elif acc_type == "TD":
        rate = 6.9
        months = int(input("Enter deposit period in months: "))

    else:
        print("Interest calculation not applicable here")
        return

    time_years = months / 12

    amount = balance * ((1 + rate / 100) ** time_years)
    interest = amount - balance

    cur.execute(
        "UPDATE accounts SET balance=%s WHERE acc_no=%s",
        (amount, acc)
    )
    con.commit()

    print("Compound Interest Applied")
    print("Interest:", round(interest, 2))
    print("Updated Balance:", round(amount, 2))


# ----------------------------------------------------

def search_account():
    while True:
        print("""
--- SEARCH ACCOUNT ---
1. Search by Name
2. Search by Account Number
3. Search by Mobile Number
0. Back
""")
        ch = input("Enter Choice: ")

        if ch == '1':
            name = input("Enter Name: ")
            cur.execute(
                "SELECT acc_no,name,acc_type,balance,status FROM accounts WHERE name LIKE %s",
                ('%' + name + '%',)
            )
            rows = cur.fetchall()

        elif ch == '2':
            acc = input("Enter Account Number: ")
            cur.execute(
                "SELECT acc_no,name,acc_type,balance,status FROM accounts WHERE acc_no=%s",
                (acc,)
            )
            rows = cur.fetchall()

        elif ch == '3':
            mobile = input("Enter Mobile Number: ")
            cur.execute(
                "SELECT acc_no,name,acc_type,balance,status FROM accounts WHERE mobile=%s",
                (mobile,)
            )
            rows = cur.fetchall()

        elif ch == '0':
            break

        else:
            print("Invalid Choice")
            continue

        if not rows:
            print("No account found")
        else:
            print("\nACC NO | NAME | TYPE | BALANCE | STATUS")
            print("----------------------------------------")
            for r in rows:
                print(r)


# ----------------------------------------------------

def close_account():
    acc = input("Account Number: ")

    # 🔍 Check account existence
    cur.execute(
        "SELECT status FROM accounts WHERE acc_no=%s",
        (acc,)
    )
    d = cur.fetchone()

    if not d:
        print("Invalid Account Number")
        return

    if d[0] == "Closed":
        print("Account is already closed")
        return

    # ✅ Close account
    cur.execute(
        "UPDATE accounts SET status='Closed' WHERE acc_no=%s",
        (acc,)
    )
    con.commit()

    print("Account Closed Successfully")


# ================= RD SCHEME =================
def rd_monthly_deposit():
    acc = input("RD Account Number: ")

    cur.execute("""
        SELECT r.monthly_amount, r.months_completed, a.status
        FROM rd_details r
        JOIN accounts a ON r.acc_no = a.acc_no
        WHERE r.acc_no=%s
    """, (acc,))
    d = cur.fetchone()

    if not d or d[2] == "Closed":
        print("Invalid / Closed RD Account")
        return

    monthly_amount = float(d[0])

    try:
        installments = int(input("Enter number of installments to deposit: "))
        if installments <= 0:
            print("Invalid number of installments")
            return
    except:
        print("Invalid input")
        return

    total_deposit = monthly_amount * installments

    # Update balance
    cur.execute(
        "UPDATE accounts SET balance = balance + %s WHERE acc_no = %s",
        (total_deposit, acc)
    )

    # Update installments
    cur.execute(
        "UPDATE rd_details SET months_completed = months_completed + %s WHERE acc_no = %s",
        (installments, acc)
    )

    con.commit()

    print("RD Deposit Successful")
    print("Installments Deposited:", installments)
    print("Amount Deposited:", total_deposit)


# ----------------------------------------------------

def rd_compound_interest():
    acc = input("RD Account Number: ")
    rate = 6.7

    cur.execute("""
        SELECT r.monthly_amount, r.months_completed, a.status
        FROM rd_details r
        JOIN accounts a ON r.acc_no = a.acc_no
        WHERE r.acc_no=%s
    """, (acc,))
    d = cur.fetchone()

    if not d or d[2] == "Closed":
        print("Invalid / Closed RD Account")
        return

    monthly = float(d[0])
    months_completed = d[1]

    # ❌ Less than 36 months → no interest
    if months_completed < 36:
        print("RD interest is not applicable before 36 months")
        return

    # ⚠️ Premature closure
    if months_completed < 60:
        print("Premature RD Closure")
        print("Full RD interest rate is applicable only after 60 installments")
        return

    # ✅ RD MATURITY (60 months)
    total_deposit = monthly * 60
    time_years = 5

    maturity_amount = total_deposit * ((1 + rate / 100) ** time_years)
    interest = maturity_amount - total_deposit

    cur.execute(
        "UPDATE accounts SET balance=%s WHERE acc_no=%s",
        (maturity_amount, acc)
    )
    con.commit()

    print("RD Maturity Completed (60 Installments)")
    print("Total Deposits:", total_deposit)
    print("Interest @ 6.7%:", round(interest, 2))
    print("Maturity Amount:", round(maturity_amount, 2))


# ----------------------------------------------------

def rd_schedule():
    acc = input("RD Account Number: ")
    rate = 5.8

    cur.execute("""
        SELECT r.months_completed, r.monthly_amount, a.status
        FROM rd_details r
        JOIN accounts a ON r.acc_no = a.acc_no
        WHERE r.acc_no=%s
    """, (acc,))
    data = cur.fetchone()

    if not data or data[2] == "Closed":
        print("Invalid / Closed RD Account")
        return

    months, monthly, _ = data
    monthly = float(monthly)

    balance = 0.0

    print("\nMONTH | DEPOSIT | INTEREST | BALANCE")
    print("------------------------------------")

    for m in range(1, months + 1):
        balance += monthly                  # deposit once per month
        interest = (balance * rate) / (12 * 100)
        balance += interest

        print(
            m,
            "|",
            monthly,
            "|",
            round(interest, 2),
            "|",
            round(balance, 2)
        )


# ----------------------------------------------------

def rd_to_sb_transfer():
    rd = input("RD Account Number: ")
    sb = input("SB Account Number: ")

    # 🔍 Validate RD account
    cur.execute(
        "SELECT balance, status FROM accounts WHERE acc_no=%s AND acc_type='RD'",
        (rd,)
    )
    rd_data = cur.fetchone()

    if not rd_data or rd_data[1] == "Closed":
        print("Invalid / Closed RD Account")
        return

    rd_balance = float(rd_data[0])

    # 🔍 Validate SB account
    cur.execute(
        "SELECT status FROM accounts WHERE acc_no=%s AND acc_type='SB'",
        (sb,)
    )
    sb_data = cur.fetchone()

    if not sb_data:
        print("Invalid SB Account Number")
        return

    if sb_data[0] == "Closed":
        print("SB Account is closed")
        return

    # ✅ Perform transfer
    cur.execute(
        "UPDATE accounts SET balance = balance + %s WHERE acc_no = %s",
        (rd_balance, sb)
    )
    cur.execute(
        "UPDATE accounts SET balance = 0, status = 'Closed' WHERE acc_no = %s",
        (rd,)
    )

    con.commit()

    print("RD Maturity Amount Transferred to SB Successfully")


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
