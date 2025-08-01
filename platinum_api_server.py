#!/usr/bin/env python3
"""
Platinum Secure Flasher - API Server
Backend API for Android Management App
UK Operations Only
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import jwt
import hashlib
import uuid
import json
from datetime import datetime, timedelta
import os
import threading
import socket
import time
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = 'platinum_secure_secret_key_2024_uk_operations'
CORS(app)

# Configuration
DB_PATH = 'platinum_api.db'
JWT_SECRET = 'platinum_jwt_secret_2024'
WIPE_SERVER_PORT = 9999

class PlatinumAPIServer:
    def __init__(self):
        self.init_database()
        self.wipe_commands = {}
        self.start_wipe_server()
        
    def init_database(self):
        """Initialize API database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'reseller',
                email TEXT,
                telegram TEXT,
                phone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                customer_contact TEXT,
                plan_type TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                payment_amount REAL NOT NULL,
                payment_currency TEXT NOT NULL,
                transaction_id TEXT,
                status TEXT DEFAULT 'pending',
                reseller_id INTEGER,
                device_uuid TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reseller_id) REFERENCES users (id)
            )
        ''')
        
        # Resellers table (enhanced)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                business_name TEXT NOT NULL,
                location TEXT NOT NULL,
                commission_rate REAL DEFAULT 10.0,
                total_sales INTEGER DEFAULT 0,
                total_commission REAL DEFAULT 0.0,
                commission_paid REAL DEFAULT 0.0,
                commission_pending REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                joined_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_sale TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tracked devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracked_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                model TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                owner_contact TEXT,
                subscription_id INTEGER,
                reseller_id INTEGER,
                flash_date TEXT NOT NULL,
                last_contact TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                location TEXT,
                wipe_key TEXT,
                notes TEXT,
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (id),
                FOREIGN KEY (reseller_id) REFERENCES resellers (id)
            )
        ''')
        
        # Wipe commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wipe_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                command_type TEXT NOT NULL,
                initiated_by INTEGER NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                result TEXT,
                confirmation_required BOOLEAN DEFAULT 1,
                confirmed_at TEXT,
                executed_at TEXT,
                FOREIGN KEY (device_id) REFERENCES tracked_devices (device_id),
                FOREIGN KEY (initiated_by) REFERENCES users (id)
            )
        ''')
        
        # Commission tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commission_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reseller_id INTEGER NOT NULL,
                subscription_id INTEGER NOT NULL,
                commission_amount REAL NOT NULL,
                currency TEXT NOT NULL,
                date_earned TEXT DEFAULT CURRENT_TIMESTAMP,
                payment_status TEXT DEFAULT 'unpaid',
                payment_date TEXT,
                payment_method TEXT,
                notes TEXT,
                FOREIGN KEY (reseller_id) REFERENCES resellers (id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
            )
        ''')
        
        # System logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        
        # Create default admin user if not exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            admin_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, email) 
                VALUES (?, ?, 'admin', 'admin@platinumsecure.co.uk')
            ''', ('admin', admin_hash))
            conn.commit()
            
        conn.close()
        
    def start_wipe_server(self):
        """Start the remote wipe command server"""
        def wipe_server():
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind(('localhost', WIPE_SERVER_PORT))
                server_socket.listen(5)
                print(f"Wipe server listening on port {WIPE_SERVER_PORT}")
                
                while True:
                    client_socket, addr = server_socket.accept()
                    threading.Thread(target=self.handle_wipe_client, args=(client_socket, addr)).start()
                    
            except Exception as e:
                print(f"Wipe server error: {e}")
                
        threading.Thread(target=wipe_server, daemon=True).start()
        
    def handle_wipe_client(self, client_socket, addr):
        """Handle wipe client connections"""
        try:
            data = client_socket.recv(1024).decode()
            command_data = json.loads(data)
            
            device_id = command_data.get('device_id')
            command_type = command_data.get('command_type')
            auth_token = command_data.get('auth_token')
            
            # Verify command in database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, status FROM wipe_commands 
                WHERE device_id = ? AND command_type = ? AND status = 'pending'
                ORDER BY timestamp DESC LIMIT 1
            ''', (device_id, command_type))
            
            wipe_command = cursor.fetchone()
            
            if wipe_command:
                # Execute wipe command
                cursor.execute('''
                    UPDATE wipe_commands 
                    SET status = 'executing', executed_at = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), wipe_command[0]))
                
                conn.commit()
                
                # Simulate wipe execution
                time.sleep(2)
                
                # Update status to completed
                cursor.execute('''
                    UPDATE wipe_commands 
                    SET status = 'completed', result = 'Wipe executed successfully'
                    WHERE id = ?
                ''', (wipe_command[0],))
                
                conn.commit()
                
                client_socket.sendall(b"WIPE_COMPLETED")
            else:
                client_socket.sendall(b"NO_COMMAND")
                
            conn.close()
            
        except Exception as e:
            print(f"Wipe client error: {e}")
            client_socket.sendall(b"ERROR")
        finally:
            client_socket.close()

# Initialize API server
api_server = PlatinumAPIServer()

def token_required(f):
    """JWT token authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
            
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'error': 'Token invalid'}), 401
            
        return f(current_user_id, *args, **kwargs)
    return decorated

def log_action(user_id, action, details=None, ip_address=None):
    """Log user actions"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO system_logs (user_id, action, details, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (user_id, action, details, ip_address))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, role, email, status 
            FROM users WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        
        if user and check_password_hash(user[2], password) and user[5] == 'active':
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now().isoformat(), user[0]))
            conn.commit()
            
            # Generate JWT token
            token = jwt.encode({
                'user_id': user[0],
                'username': user[1],
                'role': user[3],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            
            log_action(user[0], 'login', f'User {username} logged in', request.remote_addr)
            
            conn.close()
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'email': user[4]
                }
            })
        else:
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subscriptions', methods=['GET'])
@token_required
def get_subscriptions(current_user_id):
    """Get all subscriptions"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, u.username as reseller_name 
            FROM subscriptions s
            LEFT JOIN resellers r ON s.reseller_id = r.id
            LEFT JOIN users u ON r.user_id = u.id
            ORDER BY s.created_at DESC
        ''')
        
        subscriptions = cursor.fetchall()
        conn.close()
        
        result = []
        for sub in subscriptions:
            result.append({
                'id': sub[0],
                'uuid': sub[1],
                'customer_name': sub[2],
                'customer_contact': sub[3],
                'plan_type': sub[4],
                'duration_days': sub[5],
                'start_date': sub[6],
                'expiry_date': sub[7],
                'payment_method': sub[8],
                'payment_amount': sub[9],
                'payment_currency': sub[10],
                'transaction_id': sub[11],
                'status': sub[12],
                'reseller_name': sub[17] if len(sub) > 17 else None,
                'created_at': sub[15]
            })
            
        log_action(current_user_id, 'view_subscriptions', f'Viewed {len(result)} subscriptions')
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subscriptions', methods=['POST'])
@token_required
def create_subscription(current_user_id):
    """Create new subscription"""
    try:
        data = request.get_json()
        
        required_fields = ['customer_name', 'plan_type', 'payment_method', 'payment_amount', 'payment_currency']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
                
        # Calculate dates based on plan
        plan_durations = {'3_month': 90, '6_month': 180, '12_month': 365}
        duration = plan_durations.get(data['plan_type'], 90)
        
        start_date = datetime.now()
        expiry_date = start_date + timedelta(days=duration)
        
        subscription_uuid = str(uuid.uuid4())
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get reseller ID if user is reseller
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user_role = cursor.fetchone()[0]
        
        reseller_id = None
        if user_role == 'reseller':
            cursor.execute('SELECT id FROM resellers WHERE user_id = ?', (current_user_id,))
            reseller_result = cursor.fetchone()
            if reseller_result:
                reseller_id = reseller_result[0]
        
        cursor.execute('''
            INSERT INTO subscriptions (
                uuid, customer_name, customer_contact, plan_type, duration_days,
                start_date, expiry_date, payment_method, payment_amount, payment_currency,
                transaction_id, status, reseller_id, device_uuid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            subscription_uuid, data['customer_name'], data.get('customer_contact'),
            data['plan_type'], duration, start_date.isoformat(), expiry_date.isoformat(),
            data['payment_method'], data['payment_amount'], data['payment_currency'],
            data.get('transaction_id'), data.get('status', 'pending'), reseller_id,
            data.get('device_uuid')
        ))
        
        subscription_id = cursor.lastrowid
        
        # Calculate and record commission if reseller
        if reseller_id:
            cursor.execute('SELECT commission_rate FROM resellers WHERE id = ?', (reseller_id,))
            commission_rate = cursor.fetchone()[0]
            commission_amount = data['payment_amount'] * (commission_rate / 100)
            
            cursor.execute('''
                INSERT INTO commission_transactions (
                    reseller_id, subscription_id, commission_amount, currency
                ) VALUES (?, ?, ?, ?)
            ''', (reseller_id, subscription_id, commission_amount, data['payment_currency']))
            
            # Update reseller stats
            cursor.execute('''
                UPDATE resellers 
                SET total_sales = total_sales + 1,
                    total_commission = total_commission + ?,
                    commission_pending = commission_pending + ?,
                    last_sale = ?
                WHERE id = ?
            ''', (commission_amount, commission_amount, datetime.now().isoformat(), reseller_id))
        
        conn.commit()
        conn.close()
        
        log_action(current_user_id, 'create_subscription', f'Created subscription {subscription_uuid}')
        
        return jsonify({
            'id': subscription_id,
            'uuid': subscription_uuid,
            'message': 'Subscription created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/resellers', methods=['GET'])
@token_required
def get_resellers(current_user_id):
    """Get all resellers"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.*, u.username, u.email, u.telegram, u.phone, u.status as user_status
            FROM resellers r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.joined_date DESC
        ''')
        
        resellers = cursor.fetchall()
        conn.close()
        
        result = []
        for reseller in resellers:
            result.append({
                'id': reseller[0],
                'business_name': reseller[2],
                'location': reseller[3],
                'commission_rate': reseller[4],
                'total_sales': reseller[5],
                'total_commission': reseller[6],
                'commission_paid': reseller[7],
                'commission_pending': reseller[8],
                'status': reseller[9],
                'joined_date': reseller[10],
                'last_sale': reseller[11],
                'username': reseller[13],
                'email': reseller[14],
                'telegram': reseller[15],
                'phone': reseller[16],
                'user_status': reseller[17]
            })
            
        log_action(current_user_id, 'view_resellers', f'Viewed {len(result)} resellers')
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/resellers', methods=['POST'])
@token_required
def create_reseller(current_user_id):
    """Create new reseller"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'password', 'business_name', 'location']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
                
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (data['username'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Username already exists'}), 400
            
        # Create user account
        password_hash = generate_password_hash(data['password'])
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email, telegram, phone)
            VALUES (?, ?, 'reseller', ?, ?, ?)
        ''', (data['username'], password_hash, data.get('email'), 
              data.get('telegram'), data.get('phone')))
        
        user_id = cursor.lastrowid
        
        # Create reseller profile
        cursor.execute('''
            INSERT INTO resellers (
                user_id, business_name, location, commission_rate, notes
            ) VALUES (?, ?, ?, ?, ?)
        ''', (user_id, data['business_name'], data['location'], 
              data.get('commission_rate', 10.0), data.get('notes')))
        
        reseller_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        log_action(current_user_id, 'create_reseller', f'Created reseller {data["business_name"]}')
        
        return jsonify({
            'id': reseller_id,
            'user_id': user_id,
            'message': 'Reseller created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['GET'])
@token_required
def get_tracked_devices(current_user_id):
    """Get all tracked devices"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, s.customer_name as subscription_customer, r.business_name as reseller_name
            FROM tracked_devices d
            LEFT JOIN subscriptions s ON d.subscription_id = s.id
            LEFT JOIN resellers r ON d.reseller_id = r.id
            ORDER BY d.last_contact DESC
        ''')
        
        devices = cursor.fetchall()
        conn.close()
        
        result = []
        for device in devices:
            result.append({
                'id': device[0],
                'device_id': device[1],
                'serial_number': device[2],
                'model': device[3],
                'owner_name': device[4],
                'owner_contact': device[5],
                'flash_date': device[8],
                'last_contact': device[9],
                'status': device[10],
                'location': device[11],
                'subscription_customer': device[15],
                'reseller_name': device[16]
            })
            
        log_action(current_user_id, 'view_devices', f'Viewed {len(result)} tracked devices')
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['POST'])
@token_required
def add_tracked_device(current_user_id):
    """Add new tracked device"""
    try:
        data = request.get_json()
        
        required_fields = ['serial_number', 'model', 'owner_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
                
        device_id = str(uuid.uuid4())
        wipe_key = str(uuid.uuid4())
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tracked_devices (
                device_id, serial_number, model, owner_name, owner_contact,
                subscription_id, reseller_id, flash_date, location, wipe_key, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device_id, data['serial_number'], data['model'], data['owner_name'],
            data.get('owner_contact'), data.get('subscription_id'), data.get('reseller_id'),
            datetime.now().isoformat(), data.get('location'), wipe_key, data.get('notes')
        ))
        
        device_db_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        log_action(current_user_id, 'add_device', f'Added device {data["serial_number"]}')
        
        return jsonify({
            'id': device_db_id,
            'device_id': device_id,
            'wipe_key': wipe_key,
            'message': 'Device added successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wipe/initiate', methods=['POST'])
@token_required
def initiate_remote_wipe(current_user_id):
    """Initiate remote wipe command"""
    try:
        data = request.get_json()
        
        device_id = data.get('device_id')
        command_type = data.get('command_type', 'factory_reset')
        
        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400
            
        # Verify device exists
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM tracked_devices WHERE device_id = ?', (device_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Device not found'}), 404
            
        # Check user permissions
        cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
        user_role = cursor.fetchone()[0]
        
        if user_role not in ['admin', 'reseller']:
            conn.close()
            return jsonify({'error': 'Insufficient permissions'}), 403
            
        # Create wipe command
        cursor.execute('''
            INSERT INTO wipe_commands (device_id, command_type, initiated_by)
            VALUES (?, ?, ?)
        ''', (device_id, command_type, current_user_id))
        
        command_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        log_action(current_user_id, 'initiate_wipe', f'Initiated {command_type} for device {device_id}')
        
        return jsonify({
            'command_id': command_id,
            'message': f'Remote wipe ({command_type}) initiated for device {device_id}',
            'status': 'pending'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wipe/status/<int:command_id>', methods=['GET'])
@token_required
def get_wipe_status(current_user_id, command_id):
    """Get wipe command status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT w.*, d.serial_number 
            FROM wipe_commands w
            JOIN tracked_devices d ON w.device_id = d.device_id
            WHERE w.id = ?
        ''', (command_id,))
        
        command = cursor.fetchone()
        conn.close()
        
        if not command:
            return jsonify({'error': 'Command not found'}), 404
            
        return jsonify({
            'id': command[0],
            'device_id': command[1],
            'command_type': command[2],
            'timestamp': command[4],
            'status': command[5],
            'result': command[6],
            'executed_at': command[9],
            'device_serial': command[10]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/dashboard', methods=['GET'])
@token_required
def get_dashboard_analytics(current_user_id):
    """Get dashboard analytics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total revenue
        cursor.execute('SELECT SUM(payment_amount) FROM subscriptions WHERE status = "active"')
        total_revenue = cursor.fetchone()[0] or 0
        
        # Active subscriptions
        cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE status = "active"')
        active_subscriptions = cursor.fetchone()[0]
        
        # Total devices
        cursor.execute('SELECT COUNT(*) FROM tracked_devices')
        total_devices = cursor.fetchone()[0]
        
        # Active resellers
        cursor.execute('SELECT COUNT(*) FROM resellers WHERE status = "active"')
        active_resellers = cursor.fetchone()[0]
        
        # Recent activity
        cursor.execute('''
            SELECT action, details, timestamp 
            FROM system_logs 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_activity = cursor.fetchall()
        
        # Monthly stats
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute('''
            SELECT COUNT(*), SUM(payment_amount) 
            FROM subscriptions 
            WHERE created_at LIKE ?
        ''', (f'{current_month}%',))
        monthly_stats = cursor.fetchone()
        
        conn.close()
        
        log_action(current_user_id, 'view_analytics', 'Viewed dashboard analytics')
        
        return jsonify({
            'total_revenue': total_revenue,
            'active_subscriptions': active_subscriptions,
            'total_devices': total_devices,
            'active_resellers': active_resellers,
            'monthly_subscriptions': monthly_stats[0] or 0,
            'monthly_revenue': monthly_stats[1] or 0,
            'recent_activity': [
                {
                    'action': activity[0],
                    'details': activity[1],
                    'timestamp': activity[2]
                } for activity in recent_activity
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🇬🇧 Platinum Secure API Server Starting...")
    print("UK Operations Only")
    print(f"Database: {DB_PATH}")
    print(f"Wipe Server Port: {WIPE_SERVER_PORT}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)