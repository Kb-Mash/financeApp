from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import app, db, jwt, bcrypt
from models import User, Category, Expense

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Finance Tracker API'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/categories', methods=['GET'])
@jwt_required
def get_categories():
    categories = Category.query.all()
    return jsonify([category.name for category in categories])

@app.route('/expenses', methods=['GET'])
@jwt_required
def get_expenses():
    user_id = get_jwt_identity()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    return jsonify([expense.amount for expense in expenses]), 200

@app.route('/expenses', methods=['POST'])
@jwt_required
def add_expense():
    user_id = get_jwt_identity()
    data = request.get_json()
    expense = Expense(user_id=user_id, amount=data['amount'], description=data['description'], date=data['date'], category_id=data['category_id'])
    db.session.add(expense)
    db.session.commit()
    return jsonify({'message': 'Expense added successfully'}), 201

@app.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required
def update_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if expense:
        data = request.get_json()
        expense.amount = data['amount']
        expense.description = data['description']
        expense.date = data['date']
        expense.category_id = data['category_id']
        db.session.commit()
        return jsonify({'message': 'Expense updated successfully'}), 200
    else:
        return jsonify({'message': 'Expense not found'}), 404

@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required
def delete_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if expense:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted successfully'}), 200
    else:
        return jsonify({'message': 'Expense not found'}), 404

@app.route('/expenses/category/<string:category_name>', methods=['GET'])
@jwt_required
def get_expenses_by_category(category_name):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(name=category_name).first()
    if category:
        expenses = Expense.query.filter_by(user_id=user_id, category_id=category.id).all()
        return jsonify([expense.amount for expense in expenses]), 200
    else:
        return jsonify({'message': 'Category not found'}), 404

@app.route('/report', methods=['GET'])
@jwt_required
def generate_report():
    user_id = get_jwt_identity()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    total_expenses = sum([expense.amount for expense in expenses])
    return jsonify({
        'total_expenses': total_expenses,
        'total_count': len(expenses),
        'by_category': {category: sum(exp.amount for exp in expenses if exp.category == category) for category in set(exp.category for exp in expenses)}
    }), 200
