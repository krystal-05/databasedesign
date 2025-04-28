from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from decimal import Decimal



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

@app.route('/loan_payments/<int:loan_id>')
def display_loan_payments(loan_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # confirm loan belongs to user
    cursor.execute("""
        SELECT 1
        FROM loans
        WHERE loan_id = %s AND user_id = %s
    """, (loan_id, user_id))
    if not cursor.fetchone():
        cursor.close()
        abort(404, "Loan not found.")

    # fetch payments
    cursor.execute("""
        SELECT payment_id, amount_paid, payment_date
        FROM loan_payments
        WHERE loan_id = %s
        ORDER BY payment_date DESC
    """, (loan_id,))
    payments = cursor.fetchall()
    cursor.close()

    return render_template(
        'loan_payments.html',
        loan_id=loan_id,
        payments=payments
    )

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
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch current remaining balance (we've been decrementing loan_amount as balance)
    cursor.execute("""
        SELECT
          loan_id,
          loan_amount   AS remaining_balance
        FROM loans
        WHERE loan_id = %s
          AND user_id = %s
    """, (loan_id, user_id))
    loan = cursor.fetchone()
    if not loan:
        cursor.close()
        abort(404, "Loan not found.")

    # Load all checking/savings for dropdown
    cursor.execute("""
        SELECT account_no, account_type, balance
        FROM accounts
        WHERE user_id = %s
          AND account_type IN ('checking','savings')
    """, (user_id,))
    accounts = cursor.fetchall()

    error = None
    error_field = None
    form_data = {}

    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            acct_no = int(form_data.get('account_no', 0))
            # Parse as Decimal, not float
            amt     = Decimal(form_data.get('amount', '0.00'))
        except (ValueError, ArithmeticError):
            error = "Please select an account and enter a valid amount."
            error_field = 'amount'
        else:
            # Validation: positive, not over loan, account has funds
            if amt <= 0:
                error = "Payment must be positive."
                error_field = 'amount'
            elif amt > loan['remaining_balance']:
                error = "Cannot pay more than remaining balance."
                error_field = 'amount'
            else:
                # check source account balance
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
                    # 1) withdraw from account
                    cursor.execute("""
                        UPDATE accounts
                           SET balance = balance - %s
                         WHERE account_no = %s
                    """, (amt, acct_no))
                    # 2) log transaction
                    cursor.execute("""
                        INSERT INTO transactions
                          (account_no, amount, transaction_type, transaction_date)
                        VALUES (%s, %s, %s, NOW())
                    """, (acct_no, -amt, 'loan_payment'))
                    # 3) log loan payment
                    cursor.execute("""
                        INSERT INTO loan_payments (loan_id, amount_paid)
                        VALUES (%s, %s)
                    """, (loan_id, amt))
                    # 4) update loan balance + status
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

@app.route('/open_account', methods=['GET', 'POST'])
def open_new_account():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Initialize, so template always has these variables
    form_data   = {}
    error       = None
    error_field = None

    if request.method == 'POST':
        # grab everything they sent
        form_data = request.form.to_dict()

        account_type = form_data.get('account_type')
        cursor = mysql.connection.cursor()

        if account_type == 'checking':
            try:
                initial_deposit = float(form_data.get('initial_deposit', 0.00))
            except ValueError:
                error       = "Please enter a valid deposit amount."
                error_field = 'initial_deposit'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)

            cursor.execute("""
                INSERT INTO accounts
                  (user_id, account_type, balance, interest_rate, date_created)
                VALUES (%s, %s, %s, %s, NOW())
            """, (user_id, 'checking', initial_deposit, 0.00))
            account_no = cursor.lastrowid

            if initial_deposit > 0:
                cursor.execute("""
                    INSERT INTO transactions
                      (account_no, amount, transaction_type, transaction_date)
                    VALUES (%s, %s, 'deposit', NOW())
                """, (account_no, initial_deposit))

        elif account_type == 'savings':
            # validate deposit
            try:
                initial_deposit = float(form_data.get('initial_deposit', 0.00))
            except ValueError:
                error       = "Please enter a valid deposit amount."
                error_field = 'initial_deposit'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)

            savings_plan = form_data.get('savings_plan')
            if savings_plan == 'fixed_0.03':
                interest_rate = 0.03
            elif savings_plan == 'fixed_0.05':
                if initial_deposit < 15000:
                    error       = "Minimum deposit for 5% plan is $15,000."
                    error_field = 'initial_deposit'
                    cursor.close()
                    return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)
                interest_rate = 0.05
            elif savings_plan == 'variable':
                import random
                interest_rate = round(random.uniform(0.02, 0.06), 4)
            else:
                error       = "Please select a valid savings plan."
                error_field = 'savings_plan'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)

            cursor.execute("""
                INSERT INTO accounts
                  (user_id, account_type, balance, interest_rate, date_created)
                VALUES (%s, %s, %s, %s, NOW())
            """, (user_id, 'savings', initial_deposit, interest_rate))
            account_no = cursor.lastrowid

            if initial_deposit > 0:
                cursor.execute("""
                    INSERT INTO transactions
                      (account_no, amount, transaction_type, transaction_date)
                    VALUES (%s, %s, 'deposit', NOW())
                """, (account_no, initial_deposit))

        elif account_type == 'loan':
            try:
                loan_amount = float(form_data.get('loan_amount', 0.00))
                loan_term = int(form_data.get('loan_term', 0))
            except ValueError:
                error = "Please enter valid loan amount and term."
                error_field = 'loan_amount'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)

            if loan_amount < 1000:
                error = "Minimum loan amount is $1,000."
                error_field = 'loan_amount'
                cursor.close()
                return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)

            # Fixed 7% interest
            loan_interest = 7.0
            monthly_rate = (loan_interest / 100) / 12
            monthly_payment = round(loan_amount * monthly_rate / (1 - (1 + monthly_rate)**(-loan_term)), 2)

            cursor.execute("""
                INSERT INTO loans
                (user_id, loan_amount, interest_rate, loan_term, monthly_payment, status, date_created)
                VALUES (%s, %s, %s, %s, %s, 'active', NOW())
            """, (user_id, loan_amount, loan_interest, loan_term, monthly_payment))


        else:
            error       = "Please select an account type."
            error_field = 'account_type'
            cursor.close()
            return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)

        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('display_account_index'))

    # GET request or initial load
    return render_template('open_account.html', form_data=form_data, error=error, error_field=error_field)



@app.route('/close_account/<int:account_no>', methods=['GET'])
def close_account(account_no):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Check if account belongs to user and has zero balance
    cursor.execute("""
        SELECT balance FROM accounts WHERE account_no = %s AND user_id = %s
    """, (account_no, user_id))
    account = cursor.fetchone()

    if account and account['balance'] == 0:
        # Safe to delete the account
        cursor.execute("""
            DELETE FROM accounts WHERE account_no = %s
        """, (account_no,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('display_account_index'))
    else:
        cursor.close()
        return "Cannot close account. Either it does not exist, does not belong to you, or balance is not zero.", 400


if __name__ == '__main__':
    app.run(debug=True)
