from flask import Flask, render_template, request, session 
from flask_mysqldb import MySQL
import pymysql

# db = pymysql.connect(host="dbdev.cs.kent.edu", user="", password="YES", database="banting_barter_bankclear")
# app = Flask(__name__)

# # app.config['MYSQL_HOST'] = 'localhost'
# # app.config['MYSQL_USER'] = 'root' # Flashline username
# # app.config['MYSQL_PASSWORD'] = '' #phpMyAdmin password
# # app.config['MYSQL_DB'] = 'ksu' # Flashline Username

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Database Configuration
app.config['MYSQL_HOST'] = 'dbdev.cs.kent.edu'
app.config['MYSQL_USER'] = 'your_username'  # Replace with actual username
app.config['MYSQL_PASSWORD'] = 'your_password'  # Replace with actual password
app.config['MYSQL_DB'] = 'banting_barter_bankclear'

mysql = MySQL(app) 

@app.route('/')
def main():
    return render_template('main.html')

#login table needs created for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        submitted_user_id = request.form['user_id']
        submitted_password = request.form['password']
        #checks for correct credentials 
        sql = "SELECT * FROM login WHERE user_id = %s AND password = %s"
        cursor.execute(sql, (submitted_user_id, submitted_password))
        #fetchone because we are only checking one user
        user = cursor.fetchone() 
        cursor.close()

        #if credentials are correct, store user_id in session and take user to account_index 
        if user:
            sql = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(sql, (submitted_user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            #storing user_id in session instead of passing it as an int
            #if this doesnt work we will need to pass it as an int
            session['user_id'] = submitted_user_id
            return render_template('account.html',data=user)

        #if incorrect id or password
        else:
            return render_template('login.html',  message="incorrect id or password")
        
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/account_index', methods= ['GET', 'POST'])
def display_account_index():
    if request.method == 'POST':
        #get user_id from current session 
        user_id = session.get('user_id')
        account_type = request.form['account_type']

        if account_type == 'checking':
            sql = "SELECT * FROM accounts WHERE user_id = %s AND account_type = %s"
            cursor.execute(sql, (user_id, account_type))
            results = cursor.fetchall()
            cursor.close()
            return render_template('checking.html', data=results)

        elif account_type == 'savings':
            sql = "SELECT * FROM accounts WHERE user_id = %s AND account_type = %s"
            cursor.execute(sql, (user_id, account_type))
            results = cursor.fetchall()
            cursor.close()
            return render_template('savings.html', data=results)

        elif account_type == 'loans':
            sql = "SELECT * FROM accounts WHERE user_id = %s AND account_type = %s"
            cursor.execute(sql, (user_id, account_type))
            results = cursor.fetchall()
            cursor.close()
            return render_template('checking.html', data=results)
        

    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM user WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        results = cursor.fetchall()
        cursor.close()
        print(results)

        return render_template('login.html', data=results)
        

@app.route('/checking')
def display_checking_account():
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM accounts WHERE user_id = %s AND account_type = 'checking'"
    cursor.execute(sql,(user_id,))
    results = cursor.fetchall()
    cursor.close()
    print(results)

    return render_template('account_index.html', data=results)

@app.route('/savings')
def display_savings_account():
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM accounts WHERE user_id = %s AND account_type = 'savings'"
    cursor.execute(sql, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    print(results)

    return render_template('account_index.html', data=results)

@app.route('/loans')
def display_loans_account():
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM loans WHERE user_id = %s"
    cursor.execute(sql, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    print(results)

    return render_template('account_index.html', data=results)

#transactions might be able to be condensed into one template. 
@app.route('/savings_transactions')
def display_savings_transations():
    #idk if this needs stored somewhere else first???
    account_no = session.get('account_no')
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM transactions WHERE account_no = %s"
    cursor.execute(sql, (account_no,))
    results = cursor.fetchall()
    cursor.close()
    print(results)
    
    return render_template('savings.html', data=results)

@app.route('/checking_transactions')
def display_checking_transations():
    #idk if this needs stored somewhere else first???
    account_no = session.get('account_no')
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM transactions WHERE account_no = %s"
    cursor.execute(sql, (account_no,))
    results = cursor.fetchall()
    cursor.close()
    print(results)
    
    return render_template('checking.html', data=results)

@app.route('/loan_payments')
def display_loan_payments():
    #idk if this needs stored somewhere else first???
    loan_id = session.get('loan_id')
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM transactions WHERE loan_id = %s"
    cursor.execute(sql, (loan_id,))
    results = cursor.fetchall()
    cursor.close()
    print(results)
    
    return render_template('loans.html', data=results)

app.run()

