from flask import Flask, request, jsonify,render_template
import hashlib
import json
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('blockchain.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS blockchain (
        id INTEGER PRIMARY KEY,
        sender TEXT,
        receiver TEXT,
        amount INTEGER
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS balances (
        user TEXT PRIMARY KEY,
        balance INTEGER
    )
''')


# Save blockchain and balances to JSON files
# Save blockchain and balances to database
def save_data(blockchain, balances):
    cursor.execute('DELETE FROM blockchain')
    for transaction in blockchain:
        print(transaction)
        #cursor.execute('INSERT INTO blockchain VALUES (NULL, ?, ?, ?)', transaction)
        cursor.execute('INSERT INTO blockchain VALUES (NULL, :index,:sender, :receiver, :amount)', transaction)
    cursor.execute('DELETE FROM balances')
    for user, balance in balances.items():
        #cursor.execute('INSERT INTO balances VALUES (?, ?)', (user, balance))
        cursor.execute('INSERT INTO balances VALUES (:user, :balance)', {'user': user, 'balance': balance})
    conn.commit()

# Load blockchain and balances from database
def load_data():
    cursor.execute('SELECT * FROM blockchain')
    blockchain = cursor.fetchall()
    cursor.execute('SELECT * FROM balances')
    balances = dict(cursor.fetchall())
    return blockchain, balances

app = Flask(__name__)
blockchain, balances = load_data()
# Save blockchain and balances data on shutdown
import atexit
# Load blockchain and balances data
# Initialize blockchain and balances
#blockchain = []
#balances = {"Alice": 100, "Bob": 100, "Charlie": 100}

# Function to add transaction to blockchain
def add_transaction(sender, receiver, amount):
    transaction = {"sender": sender, "receiver": receiver, "amount": amount}
    blockchain.append(transaction)
    update_balances(sender, receiver, amount)

# Function to update balances
def update_balances(sender, receiver, amount):
    global balances
    try:
        balances[sender] -= int(amount)
    except KeyError:
        balances.update({sender:1000})
        balances[sender] -= int(amount)
    try:
        balances[receiver] += int(amount)
    except KeyError:
        balances.update({receiver:1000})
        balances[receiver] += int(amount)

# Function to calculate hash
def calculate_hash(block):
    return hashlib.sha256(str(block).encode()).hexdigest()
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
@app.route('/')
def index():
    return render_template('index.html')
# Route to add transaction
@app.route('/transaction', methods=['POST'])
def add_transaction_route():
    data = request.get_json()
    sender = data['sender']
    receiver = data['receiver']
    amount = data['amount']
    add_transaction(sender, receiver, amount)
    atexit.register(save_data, blockchain, balances)
    return jsonify({'message': 'Transaction added'}), 200

# Route to get blockchain
@app.route('/blockchain', methods=['GET'])
def get_blockchain_route():
    return jsonify(blockchain), 200

# Route to get balances
@app.route('/balances', methods=['GET'])
def get_balances_route():
    return jsonify(balances), 200


if __name__ == '__main__':
    app.run(debug=True)

