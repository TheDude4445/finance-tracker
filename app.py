from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pymysql

# Install pymysql as MySQLdb
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# Database configuration using environment variables
mysql_user = os.getenv('MYSQL_USER', 'default_user')
mysql_password = os.getenv('MYSQL_PASSWORD', 'default_password')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_db = os.getenv('MYSQL_DB', 'finance_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# -------------------- Models -------------------- #
class Transaction(db.Model):
    __tablename__ = 'transaction'  # Specify the existing table name
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Budget(db.Model):
    __tablename__ = 'budget'  # Specify the existing table name
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    budget_limit = db.Column(db.Float, nullable=False)  # Adjusted to match manual creation

# -------------------- API Endpoints -------------------- #
@app.route('/api/')
def api_home():
    return jsonify(message="Welcome to the Personal Finance Tracker API")

@app.route('/api/transactions', methods=['POST'])
def api_add_transaction():
    data = request.get_json()
    if not data.get('description') or not data.get('amount') or not data.get('category'):
        return jsonify(message="Invalid input, all fields are required"), 400
    
    new_transaction = Transaction(
        description=data['description'], 
        amount=data['amount'], 
        category=data['category']
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify(message="Transaction added successfully"), 201

@app.route('/api/transactions', methods=['GET'])
def api_get_transactions():
    transactions = Transaction.query.all()
    output = []
    for transaction in transactions:
        transaction_data = {
            'description': transaction.description,
            'amount': transaction.amount,
            'category': transaction.category,
            'date': transaction.date
        }
        output.append(transaction_data)
    return jsonify(transactions=output)

@app.route('/api/budgets', methods=['POST'])
def api_add_budget():
    data = request.get_json()
    if not data.get('category') or not data.get('budget_limit'):
        return jsonify(message="Invalid input, 'category' and 'budget_limit' are required fields"), 400
    
    if not isinstance(data['budget_limit'], (int, float)) or data['budget_limit'] <= 0:
        return jsonify(message="'budget_limit' should be a positive number"), 400
    
    new_budget = Budget(category=data['category'], budget_limit=data['budget_limit'])
    db.session.add(new_budget)
    db.session.commit()
    
    return jsonify(message="Budget added successfully"), 201

@app.route('/api/budgets', methods=['GET'])
def api_get_budgets():
    budgets = Budget.query.all()
    output = []
    for budget in budgets:
        budget_data = {
            'category': budget.category,
            'budget_limit': budget.budget_limit
        }
        output.append(budget_data)
    return jsonify(budgets=output)

# -------------------- Front-End Routes -------------------- #
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_transaction', methods=['GET'])
def add_transaction_form():
    return render_template('add_transaction.html')

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    description = request.form['description']
    amount = float(request.form['amount'])
    category = request.form['category']
    date = request.form['date']

    transaction_date = datetime.strptime(date, '%Y-%m-%d')

    new_transaction = Transaction(description=description, amount=amount, category=category, date=transaction_date)
    db.session.add(new_transaction)
    db.session.commit()

    return redirect(url_for('get_transactions'))

@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

@app.route('/add_budget', methods=['GET'])
def add_budget_form():
    return render_template('add_budget.html')

@app.route('/add_budget', methods=['POST'])
def add_budget():
    category = request.form['category']
    budget_limit = float(request.form['budget_limit'])

    new_budget = Budget(category=category, budget_limit=budget_limit)
    db.session.add(new_budget)
    db.session.commit()

    return redirect(url_for('get_budgets'))

@app.route('/budgets', methods=['GET'])
def get_budgets():
    budgets = Budget.query.all()
    return render_template('budgets.html', budgets=budgets)

@app.route('/delete_transaction/<int:id>', methods=['POST'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('get_transactions'))

@app.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if request.method == 'POST':
        transaction.description = request.form['description']
        transaction.amount = float(request.form['amount'])
        transaction.category = request.form['category']
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        db.session.commit()
        return redirect(url_for('get_transactions'))
    return render_template('edit_transaction.html', transaction=transaction)

@app.route('/delete_budget/<int:id>', methods=['POST'])
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    db.session.delete(budget)
    db.session.commit()
    return redirect(url_for('get_budgets'))

@app.route('/edit_budget/<int:id>', methods=['GET', 'POST'])
def edit_budget(id):
    budget = Budget.query.get_or_404(id)
    if request.method == 'POST':
        budget.category = request.form['category']
        budget.budget_limit = float(request.form['budget_limit'])
        db.session.commit()
        return redirect(url_for('get_budgets'))
    return render_template('edit_budget.html', budget=budget)

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")