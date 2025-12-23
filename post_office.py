import mysql.connector
import random

# Database connection
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",  # 
    database="post_office",
    port=3307
)

cur = con.cursor()

# -------------------------------
# Generate 10-digit Account Number
# -------------------------------
def generate_account_number(acc_type):
    if acc_type == "SB":
        prefix = "010"
    elif acc_type == "RD":
        prefix = "020"
    elif acc_type == "TD":
        prefix = "030"
    else:
        return None

    number = prefix + str(random.randint(1000000, 9999999))
    return number


# -------------------------------
# Create Account
# -------------------------------
def create_account():
    name = input("Enter Name: ")
    address = input("Enter Address: ")
    mobile = input("Enter Mobile Number: ")
    acc_type = input("Account Type (SB/RD/TD): ").upper()
    balance = float(input("Opening Balance: "))

    acc_no = generate_account_number(acc_type)

    if acc_no is None:
        print("Invalid Account Type")
        return

    cur.execute(
        "INSERT INTO accounts (acc_no,name,address,mobile,acc_type,balance) VALUES (%s,%s,%s,%s,%s,%s)",
        (acc_no, name, address, mobile, acc_type, balance)
    )
    con.commit()

    print("\n✅ Account Created Successfully")
    print("📌 Your Account Number is:", acc_no)


# -------------------------------
# Deposit
# -------------------------------
def deposit():
    acc = input("Enter Account Number: ")
    amt = float(input("Enter Amount: "))

    cur.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc,))
    data = cur.fetchone()

    if data is None:
        print("❌ Account Not Found")
        return

    cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no=%s", (amt, acc))
    cur.execute(
        "INSERT INTO transactions (acc_no,txn_type,amount,txn_date) VALUES (%s,'Deposit',%s,NOW())",
        (acc, amt)
    )
    con.commit()
    print("✅ Amount Deposited Successfully")


# -------------------------------
# Withdraw
# -------------------------------
def withdraw():
    acc = input("Enter Account Number: ")
    amt = float(input("Enter Amount: "))

    cur.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc,))
    data = cur.fetchone()

    if data is None:
        print("❌ Account Not Found")
    elif data[0] < amt:
        print("❌ Insufficient Balance")
    else:
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no=%s", (amt, acc))
        cur.execute(
            "INSERT INTO transactions (acc_no,txn_type,amount,txn_date) VALUES (%s,'Withdraw',%s,NOW())",
            (acc, amt)
        )
        con.commit()
        print("✅ Amount Withdrawn Successfully")


# -------------------------------
# Balance Enquiry
# -------------------------------
def balance_enquiry():
    acc = input("Enter Account Number: ")
    cur.execute("SELECT name, balance FROM accounts WHERE acc_no=%s", (acc,))
    data = cur.fetchone()

    if data:
        print("Name:", data[0])
        print("Balance:", data[1])
    else:
        print("❌ Account Not Found")


# -------------------------------
# Interest Calculation
# -------------------------------
def calculate_interest():
    acc = input("Enter Account Number: ")
    rate = 5     # 5% interest
    time = 1     # 1 year

    cur.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc,))
    data = cur.fetchone()

    if data:
        interest = (data[0] * rate * time) / 100
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no=%s", (interest, acc))
        con.commit()
        print("✅ Interest Added:", interest)
    else:
        print("❌ Account Not Found")


# -------------------------------
# Main Menu
# -------------------------------
while True:
    print("\n--- POST OFFICE ACCOUNT SYSTEM ---")
    print("1. Create Account")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Balance Enquiry")
    print("5. Interest Calculation")
    print("6. Exit")

    ch = input("Enter Choice: ")

    if ch == '1':
        create_account()
    elif ch == '2':
        deposit()
    elif ch == '3':
        withdraw()
    elif ch == '4':
        balance_enquiry()
    elif ch == '5':
        calculate_interest()
    elif ch == '6':
        print("Thank You")
        break
    else:
        print("❌ Invalid Choice")
