from flask import Flask, render_template, request, session, redirect, url_for, abort
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure random key in production

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '...'
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
    return render_template('login.html', message="Invalid email or password.")

@app.route('/account_index')
def display_account_index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Fetch user info
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT user_id, first_name, last_name
        FROM users
        WHERE user_id = %s
    """, (user_id,))
    user = cursor.fetchone()
    cursor.close()

    # Fetch checking accounts
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT account_no, balance
        FROM accounts
        WHERE user_id = %s AND account_type = 'checking'
    """, (user_id,))
    checking_accounts = cursor.fetchall()
    cursor.close()

    # Fetch savings accounts
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT account_no, balance
        FROM accounts
        WHERE user_id = %s AND account_type = 'savings'
    """, (user_id,))
    savings_accounts = cursor.fetchall()
    cursor.close()

    # Fetch loans
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT loan_id     AS account_no,
               loan_amount AS balance
        FROM loans
        WHERE user_id = %s
    """, (user_id,))
    loan_accounts = cursor.fetchall()
    cursor.close()

    return render_template(
        'account_index.html',
        user=user,
        checking_accounts=checking_accounts,
        savings_accounts=savings_accounts,
        loan_accounts=loan_accounts
    )

@app.route('/register', methods=['GET', 'POST'])
def registerUsers():
    if request.method == 'POST':
        fName = request.form['first_name']
        lName = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_types = request.form.getlist('account_type')
        if password != confirm_password:
            return render_template('register.html', message="Passwords do not match.")
        hashed_password = generate_password_hash(password)
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, phone, address, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (fName, lName, email, phone, address, hashed_password))
        mysql.connection.commit()
        new_user_id = cursor.lastrowid
        for acct in account_types:
            cursor.execute("""
                INSERT INTO accounts (user_id, account_type, balance, interest_rate, date_created)
                VALUES (%s, %s, 0.00, 0.00, NOW())
            """, (new_user_id, acct))
        mysql.connection.commit()
        cursor.close()
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
    cursor.execute("""
        SELECT * FROM accounts
        WHERE user_id = %s AND account_type = %s
    """, (user_id, account_type))
    results = cursor.fetchall()
    cursor.close()
    return render_template(f'{account_type}.html', data=results)

@app.route('/transactions')
def display_account_transactions():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    account_no = request.args.get('account_no', type=int)
    if not account_no:
        return redirect(url_for('display_account_index'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM transactions
        WHERE account_no = %s
        ORDER BY transaction_date DESC
    """, (account_no,))
    transactions = cursor.fetchall()
    cursor.close()
    return render_template('transactions.html', transactions=transactions)

@app.route('/make_loan_payment/<int:loan_id>', methods=['GET', 'POST'])
def make_loan_payment(loan_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT
          loan_id,
          loan_amount   AS remaining_balance
        FROM loans
        WHERE loan_id = %s AND user_id = %s
    """, (loan_id, user_id))
    loan = cursor.fetchone()
    if not loan:
        cursor.close()
        abort(404, "Loan not found.")

    cursor.execute("""
        SELECT account_no, account_type, balance
        FROM accounts
        WHERE user_id = %s AND account_type IN ('checking','savings')
    """, (user_id,))
    accounts = cursor.fetchall()

    error = None
    error_field = None
    form_data = {}

    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            acct_no = int(form_data.get('account_no', 0))
            amt     = Decimal(form_data.get('amount', '0.00'))
        except (ValueError, ArithmeticError):
            error = "Please select an account and enter a valid amount."
            error_field = 'amount'
        else:
            if amt <= 0:
                error = "Payment must be positive."
                error_field = 'amount'
            elif amt > loan['remaining_balance']:
                error = "Cannot pay more than remaining balance."
                error_field = 'amount'
            else:
                cursor.execute("""
                    SELECT balance
                    FROM accounts
                    WHERE account_no = %s AND user_id = %s
                """, (acct_no, user_id))
                acct = cursor.fetchone()
                if not acct:
                    error = "Selected account not found."
                    error_field = 'account_no'
                elif amt > acct['balance']:
                    error = "Insufficient funds in source account."
                    error_field = 'account_no'
                else:
                    # Withdraw from account
                    cursor.execute("""
                        UPDATE accounts
                           SET balance = balance - %s
                         WHERE account_no = %s
                    """, (amt, acct_no))
                    # Log transaction
                    cursor.execute("""
                        INSERT INTO transactions
                          (account_no, amount, transaction_type, transaction_date)
                        VALUES (%s, %s, %s, NOW())
                    """, (acct_no, -amt, 'loan_payment'))
                    # Log loan payment
                    cursor.execute("""
                        INSERT INTO loan_payments (loan_id, amount_paid)
                        VALUES (%s, %s)
                    """, (loan_id, amt))
                    # Update loan balance + status
                    new_bal: Decimal = loan['remaining_balance'] - amt
                    if new_bal <= 0:
                        cursor.execute("""
                            UPDATE loans
                               SET loan_amount = 0, status = 'paid'
                             WHERE loan_id = %s
                        """, (loan_id,))
                    else:
                        cursor.execute("""
                            UPDATE loans
                               SET loan_amount = %s
                             WHERE loan_id = %s
                        """, (new_bal, loan_id))
                    mysql.connection.commit()
                    cursor.close()
                    return redirect(url_for('display_loan_payments', loan_id=loan_id))

    cursor.close()
    return render_template(
        'make_loan_payment.html',
        loan=loan,
        accounts=accounts,
        form_data=form_data,
        error=error,
        error_field=error_field
    )

@app.route('/loan_payments/<int:loan_id>')
def display_loan_payments(loan_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT 1
        FROM loans
        WHERE loan_id = %s AND user_id = %s
    """, (loan_id, user_id))
    if not cursor.fetchone():
        cursor.close()
        abort(404, "Loan not found.")

    cursor.execute("""
        SELECT payment_id, amount_paid, payment_date
        FROM loan_payments
        WHERE loan_id = %s
        ORDER BY payment_date DESC
    """, (loan_id,))
    payments = cursor.fetchall()
    cursor.close()
    return render_template('loan_payments.html', loan_id=loan_id, payments=payments)

@app.route('/add_money/<int:account_no>', methods=['GET', 'POST'])
def add_money(account_no):
    if request.method == 'POST':
        amount = float(request.form['amount'])
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE accounts
               SET balance = balance + %s
             WHERE account_no = %s
        """, (amount, account_no))
        cursor.execute("""
            INSERT INTO transactions (account_no, amount, transaction_type, transaction_date)
            VALUES (%s, %s, %s, NOW())
        """, (account_no, amount, 'deposit'))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('display_account_index'))
    return render_template('add_money.html', account_no=account_no)

@app.route('/remove_money/<int:account_no>', methods=['GET', 'POST'])
def remove_money(account_no):
    if request.method == 'POST':
        amount = float(request.form['amount'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT balance FROM accounts WHERE account_no = %s", (account_no,))
        account = cursor.fetchone()
        if not account or amount > account['balance']:
            cursor.close()
            return render_template('remove_money.html', account_no=account_no, error="Insufficient funds.")
        cursor.execute("""
            UPDATE accounts
               SET balance = balance - %s
             WHERE account_no = %s
        """, (amount, account_no))
        cursor.execute("""
            INSERT INTO transactions (account_no, amount, transaction_type, transaction_date)
            VALUES (%s, %s, %s, NOW())
        """, (account_no, -amount, 'withdrawal'))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('display_account_index'))
    return render_template('remove_money.html', account_no=account_no)

@app.route('/open_account', methods=['GET', 'POST'])
def open_new_account():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    form_data = {}
    error = None
    error_field = None

    if request.method == 'POST':
        form_data = request.form.to_dict()
        account_type = form_data.get('account_type')
        cursor = mysql.connection.cursor()

        if account_type == 'checking':
            try:
                initial_deposit = float(form_data.get('initial_deposit', '0.00'))
            except ValueError:
                error, error_field = "Please enter a valid deposit amount.", 'initial_deposit'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)
            cursor.execute("""
                INSERT INTO accounts (user_id, account_type, balance, interest_rate, date_created)
                VALUES (%s, %s, %s, 0.00, NOW())
            """, (user_id, 'checking', initial_deposit))
            acct_no = cursor.lastrowid
            if initial_deposit > 0:
                cursor.execute("""
                    INSERT INTO transactions (account_no, amount, transaction_type, transaction_date)
                    VALUES (%s, %s, 'deposit', NOW())
                """, (acct_no, initial_deposit))

        elif account_type == 'savings':
            try:
                initial_deposit = float(form_data.get('initial_deposit', '0.00'))
            except ValueError:
                error, error_field = "Please enter a valid deposit amount.", 'initial_deposit'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)
            plan = form_data.get('savings_plan')
            if plan == 'fixed_0.03':
                rate = 0.03
            elif plan == 'fixed_0.05':
                if initial_deposit < 15000:
                    error, error_field = "Minimum deposit for 5% plan is $15,000.", 'initial_deposit'
                    cursor.close()
                    return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)
                rate = 0.05
            elif plan == 'variable':
                import random
                rate = round(random.uniform(0.02, 0.06), 4)
            else:
                error, error_field = "Please select a valid savings plan.", 'savings_plan'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)
            cursor.execute("""
                INSERT INTO accounts (user_id, account_type, balance, interest_rate, date_created)
                VALUES (%s, %s, %s, %s, NOW())
            """, (user_id, 'savings', initial_deposit, rate))
            acct_no = cursor.lastrowid
            if initial_deposit > 0:
                cursor.execute("""
                    INSERT INTO transactions (account_no, amount, transaction_type, transaction_date)
                    VALUES (%s, %s, 'deposit', NOW())
                """, (acct_no, initial_deposit))

        elif account_type == 'loan':
            try:
                loan_amount = float(form_data.get('loan_amount', '0.00'))
                loan_term   = int(form_data.get('loan_term', '0'))
            except ValueError:
                error, error_field = "Please enter valid loan amount and term.", 'loan_amount'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)
            if loan_amount < 1000:
                error, error_field = "Minimum loan amount is $1,000.", 'loan_amount'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)
            rate = 7.0
            r = (rate/100)/12
            M = round(loan_amount * r / (1 - (1+r)**(-loan_term)), 2)
            cursor.execute("""
                INSERT INTO loans (user_id, loan_amount, interest_rate, loan_term, monthly_payment, status, date_created)
                VALUES (%s, %s, %s, %s, %s, 'active', NOW())
            """, (user_id, loan_amount, rate, loan_term, M))

        else:
            error, error_field = "Please select an account type.", 'account_type'
            cursor.close()
            return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)

        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('display_account_index'))

    return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)

@app.route('/close_account/<int:account_no>')
def close_account(account_no):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT balance FROM accounts WHERE account_no = %s AND user_id = %s", (account_no, user_id))
    acct = cursor.fetchone()
    if acct and acct['balance'] == 0:
        cursor.execute("DELETE FROM accounts WHERE account_no = %s", (account_no,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('display_account_index'))
    cursor.close()
    return "Cannot close account (non-zero balance or not found).", 400

if __name__ == '__main__':
    app.run(debug=True)
