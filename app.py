from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL

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
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not user_id:
            return render_template('login.html', message="Please enter a user ID.")
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user_id
            return redirect(url_for('display_account_index'))
        else:
            return render_template('login.html', message="Incorrect ID.")
    return render_template('login.html')

@app.route('/account_index', methods=['GET', 'POST'])
def display_account_index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        account_type = request.form.get('account_type')
        cursor = mysql.connection.cursor()

        if account_type in ['checking', 'savings']:
            cursor.execute("SELECT * FROM accounts WHERE user_id = %s AND account_type = %s", (user_id, account_type))
            results = cursor.fetchall()
            cursor.close()
            return render_template(f'{account_type}.html', data=results)

        elif account_type == 'loans':
            cursor.execute("SELECT * FROM loans WHERE user_id = %s", (user_id,))
            results = cursor.fetchall()
            cursor.close()
            return render_template('loans.html', data=results)

    # For GET request
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    results = cursor.fetchall()
    cursor.close()
    return render_template('account_index.html', data=results)

#Register for an account
@app.route('/register', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def registerUsers():
    if request.method == 'POST':
        userID = request.form['user_id']
        fName = request.form['first_name']
        lName = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        account_types = request.form.getlist('account_type')  # Fix for multiple selections

        cursor = mysql.connection.cursor()

        # Insert user details
        sql_users = "INSERT INTO users (user_id, first_name, last_name, email, phone, address) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_users, (userID, fName, lName, email, phone, address))

        # Insert multiple accounts separately
        for account_type in account_types:
            sql_accounts = "INSERT INTO accounts (user_id, account_type, balance, interest_rate, date_created) VALUES (%s, %s, %s, %s, NOW())"
            cursor.execute(sql_accounts, (userID, account_type, 0.00, 0.00))

        mysql.connection.commit()

        # Fetch accounts only if checking/savings was selected
        if "checking" in account_types or "savings" in account_types:
            cursor.execute("SELECT * FROM accounts WHERE user_id = %s AND account_type IN (%s, %s)", (userID, "checking", "savings"))
            results = cursor.fetchall()
            cursor.close()
            return render_template('account_index.html', data=results)

        cursor.close()
        print("Account created successfully! Please log in.")
        return redirect('/login')

    return render_template('register.html')
    
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

        # UPDATE balance by adding amount
        cursor.execute(""" UPDATE accounts SET balance = balance + %s WHERE account_no = %s """, (amount, account_no))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('display_account_index'))

    # Show form to enter amount
    return render_template('add_money.html', account_no=account_no)

@app.route('/remove_money/<int:account_no>', methods=['GET', 'POST'])
def remove_money(account_no):
    if request.method == 'POST':
        amount = float(request.form['amount'])
        cursor = mysql.connection.cursor()

        # Check current balance
        cursor.execute(" SELECT balance FROM accounts WHERE account_no = %s", (account_no,))
        current_balance = cursor.fetchone()[0]

        if current_balance is not None and current_balance >= amount:
            # UPDATE balance by subtracting amount
            cursor.execute(""" UPDATE accounts SET balance = balance - %s WHERE account_no = %s """, (amount, account_no))
            mysql.connection.commit()
        else:
            # Optionally handle if not enough money
            cursor.close()
            return "Error: Insufficient balance."

        cursor.close()
        return redirect(url_for('display_account_index'))

    # Show form to enter amount
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


if __name__ == '__main__':
    app.run(debug=True)
