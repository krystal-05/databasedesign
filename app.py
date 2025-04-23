from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure random key in production

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'bankUser'
app.config['MYSQL_PASSWORD'] = '!tMifKb7V_Qf)I8i'
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

if __name__ == '__main__':
    app.run(debug=True)
