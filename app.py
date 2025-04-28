from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure random key in production

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = '!tMifKb7V_Qf)I8i'
app.config['MYSQL_DB'] = 'bankdata'

mysql = MySQL(app)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session.pop('user_id', None)
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return render_template('login.html', message="Please enter both email and password.")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['user_id']
            return redirect(url_for('display_account_index'))
        else:
            return render_template('login.html', message="Invalid email or password.")

@app.route('/account_index')
def display_account_index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # 1) Fetch basic user info
    dict_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    dict_cursor.execute("""
        SELECT user_id, first_name, last_name
        FROM users
        WHERE user_id = %s
    """, (user_id,))
    user = dict_cursor.fetchone()   # e.g. {'user_id': 'alice', 'first_name': 'Alice', 'last_name': 'Smith'}
    dict_cursor.close()

    # 2) Fetch checking accounts (if any)
    dict_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    dict_cursor.execute("""
        SELECT account_no, balance
        FROM accounts
        WHERE user_id = %s AND account_type = 'checking'
    """, (user_id,))
    checking_accounts = dict_cursor.fetchall()   # list of dicts
    dict_cursor.close()

    # 3) Fetch savings accounts
    dict_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    dict_cursor.execute("""
        SELECT account_no, balance
        FROM accounts
        WHERE user_id = %s AND account_type = 'savings'
    """, (user_id,))
    savings_accounts = dict_cursor.fetchall()
    dict_cursor.close()

    # 4) Fetch loans
    dict_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    dict_cursor.execute("""
        SELECT loan_id     AS account_no,   -- normalize key naming
               loan_amount AS balance
        FROM loans
        WHERE user_id = %s
    """, (user_id,))
    loan_accounts = dict_cursor.fetchall()
    dict_cursor.close()

    # 5) Render the dashboard template you provided
    return render_template(
        'account_index.html',
        user=user,
        checking_accounts=checking_accounts,
        savings_accounts=savings_accounts,
        loan_accounts=loan_accounts
    )

#Register for an account
@app.route('/register', methods=['GET', 'POST'])
def registerUsers():
    if request.method == 'POST':
        # Gather user input
        fName = request.form['first_name']
        lName = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_types = request.form.getlist('account_type')

        # Check password confirmation
        if password != confirm_password:
            return render_template('register.html', message="Passwords do not match.")

        # Hash password securely
        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()

        # Insert user into USERS table
        sql_users = """
            INSERT INTO users (first_name, last_name, email, phone, address, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_users, (fName, lName, email, phone, address, hashed_password))
        mysql.connection.commit()

        # Get newly created user_id
        new_user_id = cursor.lastrowid

        # Insert into ACCOUNTS if needed
        for account_type in account_types:
            sql_accounts = """
                INSERT INTO accounts (user_id, account_type, balance, interest_rate, date_created)
                VALUES (%s, %s, 0.00, 0.00, NOW())
            """
            cursor.execute(sql_accounts, (new_user_id, account_type))
        mysql.connection.commit()
        cursor.close()

        # Login user immediately after register
        session.clear()
        session['user_id'] = new_user_id
        return redirect(url_for('display_account_index'))

    return render_template('register.html')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route('/checking')
def display_checking_account():
    return display_account_type_page('checking')

@app.route('/savings')
def display_savings_account():
    return display_account_type_page('savings')

@app.route('/loans')
def display_loans_account():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM loans WHERE user_id = %s", (user_id,))
    results = cursor.fetchall()
    cursor.close()
    return render_template('loans.html', data=results)

def display_account_type_page(account_type):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM accounts WHERE user_id = %s AND account_type = %s", (user_id, account_type))
    results = cursor.fetchall()
    cursor.close()
    return render_template(f'{account_type}.html', data=results)

@app.route('/savings_transactions')
@app.route('/checking_transactions')
def display_account_transactions():
    account_no = session.get('account_no')
    if not account_no:
        return redirect(url_for('display_account_index'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transactions WHERE account_no = %s", (account_no,))
    results = cursor.fetchall()
    cursor.close()

    template = 'checking.html' if 'checking' in request.path else 'savings.html'
    return render_template(template, data=results)

@app.route('/loan_payments')
def display_loan_payments():
    loan_id = session.get('loan_id')
    if not loan_id:
        return redirect(url_for('display_loans_account'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM loan_payments WHERE loan_id = %s", (loan_id,))
    results = cursor.fetchall()
    cursor.close()

    return render_template('loans.html', data=results)

@app.route('/add_money/<int:account_no>', methods=['GET', 'POST'])
def add_money(account_no):
    if request.method == 'POST':
        amount = float(request.form['amount'])
        cursor = mysql.connection.cursor()

        # 1. Update the account balance
        cursor.execute("""
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_no = %s
        """, (amount, account_no))

        # 2. Insert a transaction record
        cursor.execute("""
            INSERT INTO transactions (account_no, amount, transaction_type, transaction_date)
            VALUES (%s, %s, %s, NOW())
        """, (account_no, amount, 'deposit'))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('display_account_index'))

    # Show the form
    return render_template('add_money.html', account_no=account_no)

@app.route('/remove_money/<int:account_no>', methods=['GET', 'POST'])
def remove_money(account_no):
    if request.method == 'POST':
        amount = float(request.form['amount'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # 1. Get current balance
        cursor.execute("""
            SELECT balance FROM accounts WHERE account_no = %s
        """, (account_no,))
        account = cursor.fetchone()

        if not account:
            cursor.close()
            return redirect(url_for('display_account_index'))

        current_balance = account['balance']

        # 2. Check for overdraft
        if amount > current_balance:
            cursor.close()
            return render_template('remove_money.html', account_no=account_no, error="Insufficient funds.")

        # 3. Update balance
        cursor.execute("""
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_no = %s
        """, (amount, account_no))

        # 4. Insert a transaction
        cursor.execute("""
            INSERT INTO transactions (account_no, amount, transaction_type, transaction_date)
            VALUES (%s, %s, %s, NOW())
        """, (account_no, -amount, 'withdrawal'))  # negative amount recorded

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('display_account_index'))

    # GET request, just render the form
    return render_template('remove_money.html', account_no=account_no)

@app.route('/make_loan_payment/<int:loan_id>', methods=['GET', 'POST'])
def make_loan_payment(loan_id):
    if request.method == 'POST':
        amount = float(request.form['amount'])
        cursor = mysql.connection.cursor()

        # Insert the payment
        cursor.execute(""" INSERT INTO loan_payments (loan_id, amount_paid) VALUES (%s, %s) """, (loan_id, amount))

        # Calculate total payments for the loan
        cursor.execute(""" SELECT SUM(amount_paid) FROM loan_payments WHERE loan_id = %s """, (loan_id,))
        total_paid = cursor.fetchone()[0] or 0

        # Get the original loan amount
        cursor.execute(""" SELECT loan_amount FROM loans WHERE loan_id = %s """, (loan_id,))
        loan_amount = cursor.fetchone()[0]

        # If fully paid, update the status
        if total_paid >= loan_amount:        
            cursor.execute(""" UPDATE loans SET status = 'paid' WHERE loan_id = %s """, (loan_id,))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('display_loans_account'))

    return render_template('make_loan_payment.html', loan_id=loan_id)

@app.route('/transactions')
def view_transactions():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    account_filter = request.args.get('account_no')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if account_filter:
        cursor.execute("""
            SELECT * FROM transactions
            WHERE account_no = %s
            ORDER BY transaction_date DESC
        """, (account_filter,))
    else:
        cursor.execute("""
            SELECT t.*
            FROM transactions t
            JOIN accounts a ON t.account_no = a.account_no
            WHERE a.user_id = %s
            ORDER BY transaction_date DESC
        """, (user_id,))

    transactions = cursor.fetchall()
    cursor.close()

    return render_template('transactions.html', transactions=transactions)

@app.route('/open_account', methods=['GET', 'POST'])
def open_new_account():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        account_type = request.form.get('account_type')

        cursor = mysql.connection.cursor()

        if account_type == 'checking':
            initial_deposit = float(request.form.get('initial_deposit', 0.00))
            cursor.execute("""
                INSERT INTO accounts (user_id, account_type, balance, interest_rate, date_created)
                VALUES (%s, 'checking', %s, 0.00, NOW())
            """, (user_id, initial_deposit))

        elif account_type == 'savings':
            initial_deposit = float(request.form.get('initial_deposit', 0.00))
            interest_rate = float(request.form.get('interest_rate', 0.00))
            cursor.execute("""
                INSERT INTO accounts (user_id, account_type, balance, interest_rate, date_created)
                VALUES (%s, 'savings', %s, %s, NOW())
            """, (user_id, initial_deposit, interest_rate))

        elif account_type == 'loan':
            loan_amount = float(request.form.get('loan_amount', 0.00))
            loan_term = int(request.form.get('loan_term', 12))
            monthly_payment = 0.00  # You could calculate based on loan amount/term if you want
            cursor.execute("""
                INSERT INTO loans (user_id, loan_amount, interest_rate, loan_term, monthly_payment, status, date_created)
                VALUES (%s, %s, 0.00, %s, %s, 'active', NOW())
            """, (user_id, loan_amount, loan_term, monthly_payment))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('display_account_index'))

    return render_template('open_account.html')


if __name__ == '__main__':
    app.run(debug=True)
