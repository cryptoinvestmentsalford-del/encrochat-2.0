#!/usr/bin/env python3
"""
Platinum Secure Flasher - System Setup Script
Comprehensive setup for all components
UK Operations Only
"""

import os
import sys
import subprocess
import sqlite3
from datetime import datetime
import json
import uuid

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🇬🇧 PLATINUM SECURE FLASHER - SYSTEM SETUP")
    print("UK Operations Only - Professional Edition")
    print("=" * 60)
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ ERROR: Python 3.8+ required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "logs",
        "backups",
        "images",
        "exports",
        "temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def initialize_databases():
    """Initialize all databases"""
    print("\n🗄️ Initializing databases...")
    
    # Main flasher database
    conn = sqlite3.connect('platinum_devices.db')
    cursor = conn.cursor()
    
    # Tracked devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_devices (
            device_id TEXT PRIMARY KEY,
            device_serial TEXT UNIQUE,
            device_model TEXT,
            owner_info TEXT,
            flash_date TEXT,
            last_contact TEXT,
            status TEXT DEFAULT 'active',
            wipe_key TEXT,
            reseller TEXT,
            notes TEXT
        )
    ''')
    
    # Wipe commands table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wipe_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            command_type TEXT,
            timestamp TEXT,
            status TEXT DEFAULT 'pending',
            result TEXT,
            FOREIGN KEY (device_id) REFERENCES tracked_devices (device_id)
        )
    ''')
    
    # Reseller commissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reseller_commissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reseller_name TEXT,
            device_id TEXT,
            commission_amount REAL,
            currency TEXT,
            date_earned TEXT,
            paid_status TEXT DEFAULT 'unpaid'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Main database initialized")
    
    # API database is initialized by the API server itself
    print("✅ API database schema ready")

def create_config_files():
    """Create configuration files"""
    print("\n⚙️ Creating configuration files...")
    
    # Main config
    config = {
        "version": "3.0",
        "uk_operations_only": True,
        "subscription_plans": {
            "3_month": {"duration": 90, "price_gbp": 120, "price_btc": 0.002, "price_xmr": 0.15, "price_eth": 0.05},
            "6_month": {"duration": 180, "price_gbp": 200, "price_btc": 0.0035, "price_xmr": 0.25, "price_eth": 0.08},
            "12_month": {"duration": 365, "price_gbp": 400, "price_btc": 0.007, "price_xmr": 0.5, "price_eth": 0.15}
        },
        "crypto_wallets": {
            "BTC": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "XMR": "4AdUndXHHZ6cfufTMvppY6JwXNouMBzSkbLYfpAV5Usx3skxNgYeYTRJ5CA1op2F6TXvY7SWgnGYvaNAX6VnXeuNP2YNDdk",
            "ETH": "0x742d35Cc6634C0532925a3b8D4C9db96590b5b5b"
        },
        "owner_contact": {
            "telegram": "@PlatinumSecureOwner",
            "signal": "+44 7XXX XXXXXX",
            "email": "owner@platinumsecure.co.uk"
        },
        "wipe_server_port": 8888,
        "api_server_port": 5000,
        "wipe_server_alt_port": 9999
    }
    
    with open('platinum_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print("✅ Main configuration created")
    
    # Default resellers file
    resellers = [
        {
            "name": "London Tech Solutions",
            "location": "London, UK",
            "telegram": "@LondonTech",
            "phone": "+44 20 XXXX XXXX",
            "email": "contact@londontech.co.uk",
            "commission": 15,
            "status": "Active",
            "joined_date": datetime.now().isoformat()
        }
    ]
    
    with open('platinum_resellers.json', 'w') as f:
        json.dump(resellers, f, indent=2)
    print("✅ Resellers configuration created")

def create_startup_scripts():
    """Create startup scripts"""
    print("\n🚀 Creating startup scripts...")
    
    # Windows batch file
    with open('start_platinum_system.bat', 'w') as f:
        f.write('''@echo off
echo 🇬🇧 Starting Platinum Secure Flasher System...
echo UK Operations Only
echo.

echo Starting API Server...
start "Platinum API Server" python platinum_api_server.py

timeout /t 3

echo Starting Main Flasher Application...
python "Platinum Secure Flasher Enhanced.py"

echo.
echo System started successfully!
pause
''')
    
    # Linux shell script
    with open('start_platinum_system.sh', 'w') as f:
        f.write('''#!/bin/bash
echo "🇬🇧 Starting Platinum Secure Flasher System..."
echo "UK Operations Only"
echo

echo "Starting API Server..."
python3 platinum_api_server.py &
API_PID=$!

sleep 3

echo "Starting Main Flasher Application..."
python3 "Platinum Secure Flasher Enhanced.py"

echo
echo "System started successfully!"
''')
    
    os.chmod('start_platinum_system.sh', 0o755)
    
    # Android app startup
    with open('start_android_app.py', 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Start Platinum Secure Android Management App
"""
import subprocess
import sys

def main():
    print("🇬🇧 Starting Platinum Secure Android App...")
    print("UK Operations Only")
    
    try:
        subprocess.run([sys.executable, "android_management_app.py"])
    except KeyboardInterrupt:
        print("\\nAndroid app stopped by user")
    except Exception as e:
        print(f"Error starting Android app: {e}")

if __name__ == "__main__":
    main()
''')
    
    print("✅ Startup scripts created")

def create_documentation():
    """Create system documentation"""
    print("\n📚 Creating documentation...")
    
    readme_content = """# Platinum Secure Flasher System v3.0
🇬🇧 **UK Operations Only** - Professional Edition

## 🚀 Quick Start

### 1. System Setup
```bash
python setup_platinum_system.py
```

### 2. Start Full System
**Windows:**
```cmd
start_platinum_system.bat
```

**Linux/Mac:**
```bash
./start_platinum_system.sh
```

### 3. Start Android Management App
```bash
python start_android_app.py
```

## 📱 Components

### Main Flasher Application
- GrapheneOS flashing for Pixel 6+ devices
- Subscription management (3/6/12 month plans)
- Reseller management with commission tracking
- Remote wipe functionality
- Device tracking and management

### Android Management App
- Mobile interface for resellers
- Subscription creation and management
- Device tracking and remote control
- Analytics and reporting
- Commission tracking

### API Server
- RESTful API backend
- JWT authentication
- Real-time device communication
- Secure remote wipe commands
- Analytics and reporting endpoints

## 💰 Subscription Plans (UK Only)

| Plan | Duration | Cash (GBP) | BTC | XMR | ETH |
|------|----------|------------|-----|-----|-----|
| 3 Month | 90 days | £120 | 0.002 | 0.15 | 0.05 |
| 6 Month | 180 days | £200 | 0.0035 | 0.25 | 0.08 |
| 12 Month | 365 days | £400 | 0.007 | 0.5 | 0.15 |

## 🏪 Reseller System

### Features
- Commission-based sales (10-20%)
- Real-time tracking
- Payment management
- Performance analytics
- UK-wide network

### Default Login
- **Admin:** admin / admin123
- **Reseller:** reseller1 / reseller123

## 🧹 Remote Wipe System

### Capabilities
- Factory reset (complete wipe)
- Data-only wipe (preserve system)
- Real-time status tracking
- Secure command authentication
- Audit logging

## 📊 Analytics & Reporting

### Dashboard Metrics
- Total revenue tracking
- Active subscriptions
- Device fleet status
- Reseller performance
- Commission calculations

## 🔒 Security Features

### Authentication
- JWT token-based API security
- Password hashing (Werkzeug)
- Role-based access control
- Session management

### Encryption
- AES-256 for sensitive data
- HTTPS API communication
- Secure key exchange
- Device authentication

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Token verification

### Subscriptions
- `GET /api/subscriptions` - List subscriptions
- `POST /api/subscriptions` - Create subscription
- `PUT /api/subscriptions/{id}` - Update subscription
- `DELETE /api/subscriptions/{id}` - Cancel subscription

### Resellers
- `GET /api/resellers` - List resellers
- `POST /api/resellers` - Create reseller
- `PUT /api/resellers/{id}` - Update reseller

### Devices
- `GET /api/devices` - List tracked devices
- `POST /api/devices` - Add device
- `GET /api/devices/{id}` - Device details

### Remote Wipe
- `POST /api/wipe/initiate` - Initiate wipe
- `GET /api/wipe/status/{id}` - Check wipe status

### Analytics
- `GET /api/analytics/dashboard` - Dashboard data
- `GET /api/analytics/revenue` - Revenue reports
- `GET /api/analytics/devices` - Device statistics

## 📁 File Structure

```
platinum-secure-flasher/
├── Platinum Secure Flasher Enhanced.py  # Main application
├── android_management_app.py             # Android app
├── platinum_api_server.py                # API backend
├── setup_platinum_system.py              # Setup script
├── requirements.txt                      # Dependencies
├── platinum_config.json                  # Configuration
├── platinum_resellers.json               # Resellers data
├── platinum_devices.db                   # Device database
├── platinum_api.db                       # API database
├── logs/                                 # System logs
├── backups/                              # Database backups
├── images/                               # GrapheneOS images
└── exports/                              # Report exports
```

## 🛠️ Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Reset databases
rm *.db
python setup_platinum_system.py
```

**2. API Server Not Starting**
```bash
# Check port availability
netstat -an | grep :5000
```

**3. Android App Dependencies**
```bash
# Install Kivy dependencies
pip install kivy kivymd
```

### Support Contacts

- **Owner:** @PlatinumSecureOwner (Telegram)
- **Email:** owner@platinumsecure.co.uk
- **Signal:** +44 7XXX XXXXXX

## 📄 License

Proprietary software. UK operations only. Unauthorized distribution prohibited.

---

© 2024 Platinum Secure - All Rights Reserved
🇬🇧 United Kingdom Operations Only
"""
    
    with open('README_SYSTEM.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Documentation created")

def setup_logging():
    """Setup logging configuration"""
    print("\n📝 Setting up logging...")
    
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": "logs/platinum_system.log",
                "formatter": "standard"
            },
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "standard"
            }
        },
        "loggers": {
            "": {
                "handlers": ["file", "console"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    
    with open('logging_config.json', 'w') as f:
        json.dump(log_config, f, indent=2)
    
    print("✅ Logging configuration created")

def verify_setup():
    """Verify system setup"""
    print("\n🔍 Verifying setup...")
    
    required_files = [
        "Platinum Secure Flasher Enhanced.py",
        "android_management_app.py",
        "platinum_api_server.py",
        "requirements.txt",
        "platinum_config.json",
        "README_SYSTEM.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing files:", missing_files)
        return False
    
    print("✅ All required files present")
    
    # Test database connections
    try:
        conn = sqlite3.connect('platinum_devices.db')
        conn.close()
        print("✅ Main database accessible")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print_banner()
    
    print("Starting Platinum Secure Flasher system setup...")
    print("This will configure all components for UK operations.")
    print()
    
    # Setup steps
    check_python_version()
    install_dependencies()
    setup_directories()
    initialize_databases()
    create_config_files()
    create_startup_scripts()
    create_documentation()
    setup_logging()
    
    # Verification
    if verify_setup():
        print("\n" + "=" * 60)
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("🇬🇧 Platinum Secure Flasher System Ready")
        print("=" * 60)
        print()
        print("📋 Next Steps:")
        print("1. Review configuration in platinum_config.json")
        print("2. Add your crypto wallet addresses")
        print("3. Update owner contact information")
        print("4. Run: start_platinum_system.bat (Windows) or ./start_platinum_system.sh (Linux)")
        print("5. Access Android app: python start_android_app.py")
        print()
        print("📚 Documentation: README_SYSTEM.md")
        print("🏪 Default admin login: admin / admin123")
        print()
        print("⚠️  Remember: UK Operations Only")
    else:
        print("\n❌ Setup failed. Please check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()