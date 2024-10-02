from flask import Flask, request, jsonify
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

# API Endpoints

# 1. Home Route
@app.route('/')
def home():
    return jsonify(message="Welcome to the Personal Finance Tracker API")

# 2. Add a new transaction
@app.route('/transactions', methods=['POST'])
def add_transaction():
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

# 3. Get all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
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

# 4. Add a new budget
@app.route('/budgets', methods=['POST'])
def add_budget():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('category') or not data.get('limit'):
        return jsonify(message="Invalid input, 'category' and 'limit' are required fields"), 400
    
    # Validate that 'limit' is a positive number
    if not isinstance(data['limit'], (int, float)) or data['limit'] <= 0:
        return jsonify(message="'limit' should be a positive number"), 400
    
    new_budget = Budget(category=data['category'], limit=data['limit'])
    db.session.add(new_budget)
    db.session.commit()
    
    return jsonify(message="Budget added successfully"), 201

# 5. Get all budgets
@app.route('/budgets', methods=['GET'])
def get_budgets():
    budgets = Budget.query.all()
    output = []
    for budget in budgets:
        budget_data = {
            'category': budget.category,
            'limit': budget.limit
        }
        output.append(budget_data)
    return jsonify(budgets=output)

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # This ensures tables are created before the app runs
    app.run(debug=True, host="0.0.0.0")