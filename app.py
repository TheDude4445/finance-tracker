from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    limit = db.Column(db.Float, nullable=False)

# -------------------- API Endpoints -------------------- #

# API Home
@app.route('/api/')
def api_home():
    return jsonify(message="Welcome to the Personal Finance Tracker API")

# API - Add a new transaction
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

# API - Get all transactions
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

# API - Add a new budget
@app.route('/api/budgets', methods=['POST'])
def api_add_budget():
    data = request.get_json()
    if not data.get('category') or not data.get('limit'):
        return jsonify(message="Invalid input, 'category' and 'limit' are required fields"), 400
    
    if not isinstance(data['limit'], (int, float)) or data['limit'] <= 0:
        return jsonify(message="'limit' should be a positive number"), 400
    
    new_budget = Budget(category=data['category'], limit=data['limit'])
    db.session.add(new_budget)
    db.session.commit()
    
    return jsonify(message="Budget added successfully"), 201

# API - Get all budgets
@app.route('/api/budgets', methods=['GET'])
def api_get_budgets():
    budgets = Budget.query.all()
    output = []
    for budget in budgets:
        budget_data = {
            'category': budget.category,
            'limit': budget.limit
        }
        output.append(budget_data)
    return jsonify(budgets=output)

# -------------------- Front-End Routes -------------------- #

# Home Route (Front-end)
@app.route('/')
def home():
    return render_template('index.html')

# Route to display the transaction form
@app.route('/add_transaction', methods=['GET'])
def add_transaction_form():
    return render_template('add_transaction.html')

# Route to handle form submission for adding a transaction
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    description = request.form['description']
    amount = float(request.form['amount'])
    category = request.form['category']
    date = request.form['date']  # Get the date from the form

    # Convert string date to datetime object
    transaction_date = datetime.strptime(date, '%Y-%m-%d')

    new_transaction = Transaction(description=description, amount=amount, category=category, date=transaction_date)
    db.session.add(new_transaction)
    db.session.commit()

    return redirect(url_for('get_transactions'))

# Route to display all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

# Route to display the budget form
@app.route('/add_budget', methods=['GET'])
def add_budget_form():
    return render_template('add_budget.html')

# Route to handle form submission for adding a budget
@app.route('/add_budget', methods=['POST'])
def add_budget():
    category = request.form['category']
    limit = float(request.form['limit'])

    new_budget = Budget(category=category, limit=limit)
    db.session.add(new_budget)
    db.session.commit()

    return redirect(url_for('get_budgets'))

# Route to display all budgets
@app.route('/budgets', methods=['GET'])
def get_budgets():
    budgets = Budget.query.all()
    return render_template('budgets.html', budgets=budgets)

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created before the app runs
    app.run(debug=True, host="0.0.0.0")