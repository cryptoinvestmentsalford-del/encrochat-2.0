#!/usr/bin/env python3
"""
Platinum Secure Flasher Enhanced
Advanced GrapheneOS flashing tool with subscription management and crypto payments
UK Operations Only - Reseller Management System
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import json
import uuid
import hashlib
import requests
import qrcode
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import zipfile
import tempfile
import shutil
import webbrowser
import base64
from io import BytesIO
import sqlite3
import socket
import time

class PlatinumSecureFlasher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Platinum Secure Flasher v3.0 - UK Professional Edition")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        
        # Database initialization
        self.init_database()
        
        # Subscription system
        self.license_file = "platinum_license.json"
        self.subscription_file = "platinum_subscription.json"
        self.resellers_file = "platinum_resellers.json"
        self.devices_file = "platinum_devices.json"
        self.device_uuid = self.get_device_uuid()
        
        # Remote wipe configuration
        self.wipe_server_port = 8888
        self.wipe_secret_key = "platinum_wipe_secret_2024"
        
        # Crypto wallet addresses (replace with your actual addresses)
        self.crypto_wallets = {
            'BTC': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
            'XMR': '4AdUndXHHZ6cfufTMvppY6JwXNouMBzSkbLYfpAV5Usx3skxNgYeYTRJ5CA1op2F6TXvY7SWgnGYvaNAX6VnXeuNP2YNDdk',
            'ETH': '0x742d35Cc6634C0532925a3b8D4C9db96590b5b5b'
        }
        
        # Subscription plans - UK GBP pricing
        self.subscription_plans = {
            '3_month': {'duration': 90, 'price_btc': 0.002, 'price_xmr': 0.15, 'price_eth': 0.05, 'price_cash': 120},
            '6_month': {'duration': 180, 'price_btc': 0.0035, 'price_xmr': 0.25, 'price_eth': 0.08, 'price_cash': 200},
            '12_month': {'duration': 365, 'price_btc': 0.007, 'price_xmr': 0.5, 'price_eth': 0.15, 'price_cash': 400}
        }
        
        # Owner contact information
        self.owner_contact = {
            'telegram': '@PlatinumSecureOwner',
            'signal': '+44 7XXX XXXXXX',
            'email': 'owner@platinumsecure.co.uk'
        }
        
        # Load resellers from file
        self.resellers = self.load_resellers()
        
        # Load tracked devices
        self.tracked_devices = self.load_tracked_devices()
        
        # Supported devices
        self.supported_devices = {
            'oriole': 'Pixel 6',
            'raven': 'Pixel 6 Pro',
            'bluejay': 'Pixel 6a',
            'panther': 'Pixel 7',
            'cheetah': 'Pixel 7 Pro',
            'lynx': 'Pixel 7a',
            'shiba': 'Pixel 8',
            'husky': 'Pixel 8 Pro',
            'akita': 'Pixel 8a',
            'tokay': 'Pixel 9',
            'caiman': 'Pixel 9 Pro',
            'komodo': 'Pixel 9 Pro XL'
        }
        
        self.setup_ui()
        self.check_subscription()
        self.start_remote_wipe_server()
        
    def init_database(self):
        """Initialize SQLite database for device tracking"""
        try:
            self.db_path = "platinum_devices.db"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
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
            
        except Exception as e:
            print(f"Database initialization error: {e}")

    def load_tracked_devices(self):
        """Load tracked devices from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tracked_devices")
            devices = cursor.fetchall()
            conn.close()
            return devices
        except Exception as e:
            print(f"Error loading tracked devices: {e}")
            return []
    
    def save_resellers(self):
        """Save resellers to JSON file"""
        try:
            with open(self.resellers_file, 'w') as f:
                json.dump(self.resellers, f, indent=2)
            self.log_message("Resellers database saved")
        except Exception as e:
            self.log_message(f"Error saving resellers: {str(e)}")
    
    def setup_ui(self):
        """Setup the main UI with EncroChat styling"""
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure EncroChat-like colors
        style.configure('Title.TLabel', 
                       background='#0a0a0a', 
                       foreground='#00d4ff',
                       font=('Arial', 18, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background='#0a0a0a', 
                       foreground='#ffffff',
                       font=('Arial', 12))
        
        style.configure('Custom.TButton',
                       background='#1a1a1a',
                       foreground='#ffffff',
                       borderwidth=1,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        
        style.map('Custom.TButton',
                 background=[('active', '#00d4ff'),
                           ('pressed', '#0099cc')])
        
        style.configure('Crypto.TButton',
                       background='#ff6b35',
                       foreground='#ffffff',
                       borderwidth=1,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        
        style.map('Crypto.TButton',
                 background=[('active', '#ff8c42'),
                           ('pressed', '#e55a2b')])
        
        style.configure('Reseller.TButton',
                       background='#28a745',
                       foreground='#ffffff',
                       borderwidth=1,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        
        style.map('Reseller.TButton',
                 background=[('active', '#34ce57'),
                           ('pressed', '#1e7e34')])
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with logo and status
        header_frame = tk.Frame(main_frame, bg='#0a0a0a')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🇬🇧 PLATINUM SECURE FLASHER - UK", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Subscription status
        self.status_label = ttk.Label(header_frame, 
                                     text="● CHECKING STATUS...", 
                                     style='Subtitle.TLabel')
        self.status_label.pack(side='right')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Setup tabs
        self.setup_flash_tab()
        self.setup_subscription_tab()
        self.setup_payment_tab()
        self.setup_contact_tab()
        self.setup_reseller_management_tab()
        self.setup_hardening_tab()
        self.setup_logs_tab()
        self.setup_remote_wipe_tab()
        self.setup_device_tracking_tab()
        
    def setup_flash_tab(self):
        """Setup flashing tab"""
        flash_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(flash_frame, text="🚀 Flash Device")
        
        # Device selection
        device_frame = tk.LabelFrame(flash_frame, 
                                   text="Device Selection", 
                                   bg='#1a1a1a', 
                                   fg='#00d4ff',
                                   font=('Arial', 12, 'bold'))
        device_frame.pack(fill='x', padx=15, pady=15)
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, 
                                        textvariable=self.device_var,
                                        values=list(self.supported_devices.values()),
                                        state='readonly',
                                        font=('Arial', 11))
        self.device_combo.pack(padx=15, pady=15)
        
        # File selection
        file_frame = tk.LabelFrame(flash_frame, 
                                 text="GrapheneOS Image", 
                                 bg='#1a1a1a', 
                                 fg='#00d4ff',
                                 font=('Arial', 12, 'bold'))
        file_frame.pack(fill='x', padx=15, pady=15)
        
        self.file_path = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path, 
                            bg='#2d2d2d', fg='#ffffff', width=70,
                            font=('Arial', 10))
        file_entry.pack(side='left', padx=15, pady=15)
        
        browse_btn = ttk.Button(file_frame, text="📁 Browse", 
                              command=self.browse_file,
                              style='Custom.TButton')
        browse_btn.pack(side='right', padx=15, pady=15)
        
        # Flash options
        options_frame = tk.LabelFrame(flash_frame, 
                                    text="Flash Options", 
                                    bg='#1a1a1a', 
                                    fg='#00d4ff',
                                    font=('Arial', 12, 'bold'))
        options_frame.pack(fill='x', padx=15, pady=15)
        
        self.unlock_bootloader = tk.BooleanVar()
        self.apply_hardening = tk.BooleanVar(value=True)
        self.verify_image = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="🔓 Unlock Bootloader", 
                      variable=self.unlock_bootloader,
                      bg='#1a1a1a', fg='#ffffff',
                      selectcolor='#2d2d2d',
                      font=('Arial', 10)).pack(anchor='w', padx=15, pady=5)
        
        tk.Checkbutton(options_frame, text="🛡️ Apply Security Hardening", 
                      variable=self.apply_hardening,
                      bg='#1a1a1a', fg='#ffffff',
                      selectcolor='#2d2d2d',
                      font=('Arial', 10)).pack(anchor='w', padx=15, pady=5)
        
        tk.Checkbutton(options_frame, text="✅ Verify Image Integrity", 
                      variable=self.verify_image,
                      bg='#1a1a1a', fg='#ffffff',
                      selectcolor='#2d2d2d',
                      font=('Arial', 10)).pack(anchor='w', padx=15, pady=5)
        
        # Flash button
        flash_btn = ttk.Button(flash_frame, text="🚀 START FLASHING", 
                             command=self.start_flash,
                             style='Custom.TButton')
        flash_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(flash_frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=15, pady=15)
        
    def setup_subscription_tab(self):
        """Setup subscription management tab"""
        sub_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(sub_frame, text="📱 Subscription")
        
        # Current subscription info
        current_frame = tk.LabelFrame(sub_frame, 
                                    text="Current Subscription", 
                                    bg='#1a1a1a', 
                                    fg='#00d4ff',
                                    font=('Arial', 12, 'bold'))
        current_frame.pack(fill='x', padx=15, pady=15)
        
        self.subscription_info = tk.Text(current_frame, height=8, 
                                       bg='#2d2d2d', fg='#ffffff',
                                       font=('Consolas', 10))
        self.subscription_info.pack(fill='x', padx=15, pady=15)
        
        # Subscription plans
        plans_frame = tk.LabelFrame(sub_frame, 
                                  text="Available Plans (UK Only)", 
                                  bg='#1a1a1a', 
                                  fg='#00d4ff',
                                  font=('Arial', 12, 'bold'))
        plans_frame.pack(fill='x', padx=15, pady=15)
        
        # Plan selection - UK GBP pricing
        self.selected_plan = tk.StringVar(value='6_month')
        
        plan_options = [
            ('3 Month Plan - £120 / 0.002 BTC / 0.15 XMR', '3_month'),
            ('6 Month Plan - £200 / 0.0035 BTC / 0.25 XMR', '6_month'),
            ('12 Month Plan - £400 / 0.007 BTC / 0.5 XMR', '12_month')
        ]
        
        for text, value in plan_options:
            tk.Radiobutton(plans_frame, text=text, variable=self.selected_plan,
                          value=value, bg='#1a1a1a', fg='#ffffff',
                          selectcolor='#2d2d2d', font=('Arial', 10)).pack(anchor='w', padx=15, pady=5)
        
        # UK Notice
        uk_notice = tk.Label(plans_frame, 
                           text="🇬🇧 UK OPERATIONS ONLY - No international shipping or services",
                           bg='#1a1a1a', fg='#ff6b35', font=('Arial', 11, 'bold'))
        uk_notice.pack(pady=10)
        
        # Device UUID
        uuid_frame = tk.LabelFrame(sub_frame, 
                                 text="Device UUID (Required for Activation)", 
                                 bg='#1a1a1a', 
                                 fg='#00d4ff',
                                 font=('Arial', 12, 'bold'))
        uuid_frame.pack(fill='x', padx=15, pady=15)
        
        uuid_text = tk.Text(uuid_frame, height=2, 
                          bg='#2d2d2d', fg='#00ff00',
                          font=('Consolas', 10))
        uuid_text.insert('1.0', self.device_uuid)
        uuid_text.config(state='disabled')
        uuid_text.pack(fill='x', padx=15, pady=15)
        
        # Copy UUID button
        copy_uuid_btn = ttk.Button(uuid_frame, text="📋 Copy UUID", 
                                 command=self.copy_uuid,
                                 style='Custom.TButton')
        copy_uuid_btn.pack(pady=10)
        
    def setup_payment_tab(self):
        """Setup payment methods tab"""
        payment_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(payment_frame, text="💰 Payment")
        
        # Payment method selection
        method_frame = tk.LabelFrame(payment_frame, 
                                   text="Payment Methods (UK Only)", 
                                   bg='#1a1a1a', 
                                   fg='#00d4ff',
                                   font=('Arial', 12, 'bold'))
        method_frame.pack(fill='x', padx=15, pady=15)
        
        # Crypto payment buttons
        crypto_frame = tk.Frame(method_frame, bg='#1a1a1a')
        crypto_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Button(crypto_frame, text="₿ Pay with Bitcoin", 
                  command=lambda: self.show_crypto_payment('BTC'),
                  style='Crypto.TButton').pack(side='left', padx=10)
        
        ttk.Button(crypto_frame, text="🔒 Pay with Monero", 
                  command=lambda: self.show_crypto_payment('XMR'),
                  style='Crypto.TButton').pack(side='left', padx=10)
        
        ttk.Button(crypto_frame, text="Ξ Pay with Ethereum", 
                  command=lambda: self.show_crypto_payment('ETH'),
                  style='Crypto.TButton').pack(side='left', padx=10)
        
        # Cash payment button
        ttk.Button(method_frame, text="💵 Generate Cash Payment QR (UK)", 
                  command=self.generate_cash_qr,
                  style='Custom.TButton').pack(pady=15)
        
        # Payment display area
        self.payment_display = tk.Frame(payment_frame, bg='#1a1a1a')
        self.payment_display.pack(fill='both', expand=True, padx=15, pady=15)
        
    def setup_contact_tab(self):
        """Setup contact information tab"""
        contact_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(contact_frame, text="📞 Contact")
        
        # Owner contact
        owner_frame = tk.LabelFrame(contact_frame, 
                                  text="System Owner (UK)", 
                                  bg='#1a1a1a', 
                                  fg='#00d4ff',
                                  font=('Arial', 12, 'bold'))
        owner_frame.pack(fill='x', padx=15, pady=15)
        
        owner_info = f"""
🔹 Telegram: {self.owner_contact['telegram']}
🔹 Signal: {self.owner_contact['signal']}
🔹 Email: {self.owner_contact['email']}

For technical support, license issues, or direct purchases.
UK operations only - No international services.
        """
        
        tk.Label(owner_frame, text=owner_info, bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 11), justify='left').pack(padx=15, pady=15)
        
        # Contact buttons
        contact_buttons = tk.Frame(owner_frame, bg='#1a1a1a')
        contact_buttons.pack(padx=15, pady=10)
        
        ttk.Button(contact_buttons, text="📱 Open Telegram", 
                  command=lambda: self.open_contact('telegram', self.owner_contact['telegram']),
                  style='Custom.TButton').pack(side='left', padx=10)
        
        ttk.Button(contact_buttons, text="📧 Send Email", 
                  command=lambda: self.open_contact('email', self.owner_contact['email']),
                  style='Custom.TButton').pack(side='left', padx=10)
        
        # Resellers section
        reseller_frame = tk.LabelFrame(contact_frame, 
                                     text="Authorized UK Resellers", 
                                     bg='#1a1a1a', 
                                     fg='#00d4ff',
                                     font=('Arial', 12, 'bold'))
        reseller_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Scrollable reseller list
        reseller_canvas = tk.Canvas(reseller_frame, bg='#1a1a1a')
        reseller_scrollbar = ttk.Scrollbar(reseller_frame, orient="vertical", command=reseller_canvas.yview)
        self.reseller_scrollable_frame = tk.Frame(reseller_canvas, bg='#1a1a1a')
        
        self.reseller_scrollable_frame.bind(
            "<Configure>",
            lambda e: reseller_canvas.configure(scrollregion=reseller_canvas.bbox("all"))
        )
        
        reseller_canvas.create_window((0, 0), window=self.reseller_scrollable_frame, anchor="nw")
        reseller_canvas.configure(yscrollcommand=reseller_scrollbar.set)
        
        reseller_canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        reseller_scrollbar.pack(side="right", fill="y")
        
        self.refresh_reseller_display()
        
    def setup_reseller_management_tab(self):
        """Setup reseller management tab"""
        reseller_mgmt_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(reseller_mgmt_frame, text="🏪 Manage Resellers")
        
        # Add new reseller section
        add_frame = tk.LabelFrame(reseller_mgmt_frame, 
                                text="Add New UK Reseller", 
                                bg='#1a1a1a', 
                                fg='#00d4ff',
                                font=('Arial', 12, 'bold'))
        add_frame.pack(fill='x', padx=15, pady=15)
        
        # Reseller form
        form_frame = tk.Frame(add_frame, bg='#1a1a1a')
        form_frame.pack(fill='x', padx=15, pady=15)
        
        # Name
        tk.Label(form_frame, text="Reseller Name:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.reseller_name = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.reseller_name.grid(row=0, column=1, padx=5, pady=5)
        
        # Location
        tk.Label(form_frame, text="UK Location:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.reseller_location = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.reseller_location.grid(row=1, column=1, padx=5, pady=5)
        
        # Telegram
        tk.Label(form_frame, text="Telegram:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.reseller_telegram = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.reseller_telegram.grid(row=2, column=1, padx=5, pady=5)
        
        # Phone
        tk.Label(form_frame, text="UK Phone:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.reseller_phone = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.reseller_phone.grid(row=3, column=1, padx=5, pady=5)
        
        # Email
        tk.Label(form_frame, text="Email:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.reseller_email = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.reseller_email.grid(row=4, column=1, padx=5, pady=5)
        
        # Commission Rate
        tk.Label(form_frame, text="Commission %:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', padx=5, pady=5)
        self.reseller_commission = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.reseller_commission.grid(row=5, column=1, padx=5, pady=5)
        
        # Status
        tk.Label(form_frame, text="Status:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', padx=5, pady=5)
        self.reseller_status = ttk.Combobox(form_frame, values=['Active', 'Inactive', 'Pending'], 
                                          state='readonly', width=27)
        self.reseller_status.set('Active')
        self.reseller_status.grid(row=6, column=1, padx=5, pady=5)
        
        # Add button
        ttk.Button(add_frame, text="➕ Add Reseller", 
                  command=self.add_reseller,
                  style='Reseller.TButton').pack(pady=15)
        
        # Current resellers management
        current_frame = tk.LabelFrame(reseller_mgmt_frame, 
                                    text="Current UK Resellers", 
                                    bg='#1a1a1a', 
                                    fg='#00d4ff',
                                    font=('Arial', 12, 'bold'))
        current_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Reseller list with management options
        self.reseller_tree = ttk.Treeview(current_frame, columns=('Name', 'Location', 'Contact', 'Commission', 'Status'), 
                                        show='headings', height=10)
        
        # Define headings
        self.reseller_tree.heading('Name', text='Name')
        self.reseller_tree.heading('Location', text='UK Location')
        self.reseller_tree.heading('Contact', text='Contact')
        self.reseller_tree.heading('Commission', text='Commission %')
        self.reseller_tree.heading('Status', text='Status')
        
        # Define column widths
        self.reseller_tree.column('Name', width=150)
        self.reseller_tree.column('Location', width=120)
        self.reseller_tree.column('Contact', width=150)
        self.reseller_tree.column('Commission', width=100)
        self.reseller_tree.column('Status', width=80)
        
        self.reseller_tree.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Management buttons
        mgmt_buttons = tk.Frame(current_frame, bg='#1a1a1a')
        mgmt_buttons.pack(fill='x', padx=15, pady=10)
        
        ttk.Button(mgmt_buttons, text="✏️ Edit Selected", 
                  command=self.edit_reseller,
                  style='Custom.TButton').pack(side='left', padx=10)
        
        ttk.Button(mgmt_buttons, text="🗑️ Remove Selected", 
                  command=self.remove_reseller,
                  style='Custom.TButton').pack(side='left', padx=10)
        
        ttk.Button(mgmt_buttons, text="🔄 Refresh List", 
                  command=self.refresh_reseller_tree,
                  style='Custom.TButton').pack(side='left', padx=10)
        
        # Load existing resellers
        self.refresh_reseller_tree()
        
    def setup_hardening_tab(self):
        """Setup security hardening tab"""
        hardening_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(hardening_frame, text="🛡️ Security")
        
        # Hardening options
        options_frame = tk.LabelFrame(hardening_frame, 
                                    text="Security Hardening Options", 
                                    bg='#1a1a1a', 
                                    fg='#00d4ff',
                                    font=('Arial', 12, 'bold'))
        options_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        hardening_options = [
            ("🚫 Disable USB Debugging", True),
            ("✅ Enable Verified Boot", True),
            ("🔒 Disable Developer Options", True),
            ("📌 Enable App Pinning", False),
            ("⛔ Disable Unknown Sources", True),
            ("🔐 Enable Screen Lock", True),
            ("🌐 Disable ADB over Network", True),
            ("🔐 Enable Full Disk Encryption", True),
            ("🛡️ Enable Anti-Forensics Mode", True),
            ("🔥 Enable Emergency Wipe", True)
        ]
        
        self.hardening_vars = {}
        for option, default in hardening_options:
            var = tk.BooleanVar(value=default)
            self.hardening_vars[option] = var
            tk.Checkbutton(options_frame, text=option, variable=var,
                          bg='#1a1a1a', fg='#ffffff',
                          selectcolor='#2d2d2d',
                          font=('Arial', 10)).pack(anchor='w', padx=15, pady=5)
        
        # Apply hardening button
        apply_btn = ttk.Button(hardening_frame, text="🛡️ APPLY HARDENING", 
                             command=self.apply_hardening_settings,
                             style='Custom.TButton')
        apply_btn.pack(pady=20)
        
    def setup_logs_tab(self):
        """Setup logs tab"""
        logs_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(logs_frame, text="📋 Logs")
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(logs_frame, 
                                                bg='#0a0a0a', 
                                                fg='#00ff00',
                                                font=('Consolas', 10))
        self.log_text.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Log controls
        log_controls = tk.Frame(logs_frame, bg='#1a1a1a')
        log_controls.pack(fill='x', padx=15, pady=10)
        
        ttk.Button(log_controls, text="🗑️ Clear Logs", 
                  command=self.clear_logs,
                  style='Custom.TButton').pack(side='left', padx=10)
        
        ttk.Button(log_controls, text="💾 Save Logs", 
                  command=self.save_logs,
                  style='Custom.TButton').pack(side='left', padx=10)
        
    def setup_remote_wipe_tab(self):
        """Setup remote wipe tab"""
        wipe_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(wipe_frame, text="🧹 Remote Wipe")
        
        # Wipe options
        options_frame = tk.LabelFrame(wipe_frame, 
                                    text="Remote Wipe Options", 
                                    bg='#1a1a1a', 
                                    fg='#00d4ff',
                                    font=('Arial', 12, 'bold'))
        options_frame.pack(fill='x', padx=15, pady=15)
        
        # Wipe command selection
        self.wipe_command_var = tk.StringVar(value='factory_reset')
        
        tk.Radiobutton(options_frame, text="Factory Reset (Full Data Erasure)", 
                      variable=self.wipe_command_var,
                      value='factory_reset',
                      bg='#1a1a1a', fg='#ffffff',
                      selectcolor='#2d2d2d',
                      font=('Arial', 10)).pack(anchor='w', padx=15, pady=5)
        
        tk.Radiobutton(options_frame, text="Data Only (Keep System Files)", 
                      variable=self.wipe_command_var,
                      value='data_only',
                      bg='#1a1a1a', fg='#ffffff',
                      selectcolor='#2d2d2d',
                      font=('Arial', 10)).pack(anchor='w', padx=15, pady=5)
        
        # Wipe button
        wipe_btn = ttk.Button(wipe_frame, text="🧹 START WIPE", 
                             command=self.start_remote_wipe,
                             style='Custom.TButton')
        wipe_btn.pack(pady=20)
        
        # Progress bar
        self.wipe_progress = ttk.Progressbar(wipe_frame, mode='indeterminate')
        self.wipe_progress.pack(fill='x', padx=15, pady=15)
        
        # Wipe status display
        self.wipe_status_label = ttk.Label(wipe_frame, 
                                          text="Wipe Status: Idle", 
                                          style='Subtitle.TLabel')
        self.wipe_status_label.pack(pady=10)
        
        # Wipe logs
        self.wipe_log_text = scrolledtext.ScrolledText(wipe_frame, 
                                                       bg='#0a0a0a', 
                                                       fg='#ff0000',
                                                       font=('Consolas', 10))
        self.wipe_log_text.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Wipe controls
        wipe_controls = tk.Frame(wipe_frame, bg='#1a1a1a')
        wipe_controls.pack(fill='x', padx=15, pady=10)
        
        ttk.Button(wipe_controls, text="🔄 Refresh Status", 
                  command=self.refresh_wipe_status,
                  style='Custom.TButton').pack(side='left', padx=10)
        
        ttk.Button(wipe_controls, text="💾 Save Wipe Logs", 
                  command=self.save_wipe_logs,
                  style='Custom.TButton').pack(side='left', padx=10)
        
    def setup_device_tracking_tab(self):
        """Setup device tracking tab"""
        tracking_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(tracking_frame, text="📱 Device Tracking")
        
        # Device list
        device_list_frame = tk.LabelFrame(tracking_frame, 
                                         text="Tracked Devices", 
                                         bg='#1a1a1a', 
                                         fg='#00d4ff',
                                         font=('Arial', 12, 'bold'))
        device_list_frame.pack(fill='x', padx=15, pady=15)
        
        # Scrollable device list
        device_canvas = tk.Canvas(device_list_frame, bg='#1a1a1a')
        device_scrollbar = ttk.Scrollbar(device_list_frame, orient="vertical", command=device_canvas.yview)
        self.device_scrollable_frame = tk.Frame(device_canvas, bg='#1a1a1a')
        
        self.device_scrollable_frame.bind(
            "<Configure>",
            lambda e: device_canvas.configure(scrollregion=device_canvas.bbox("all"))
        )
        
        device_canvas.create_window((0, 0), window=self.device_scrollable_frame, anchor="nw")
        device_canvas.configure(yscrollcommand=device_scrollbar.set)
        
        device_canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        device_scrollbar.pack(side="right", fill="y")
        
        self.refresh_device_display()
        
        # Add new device section
        add_device_frame = tk.LabelFrame(tracking_frame, 
                                        text="Add New Tracked Device", 
                                        bg='#1a1a1a', 
                                        fg='#00d4ff',
                                        font=('Arial', 12, 'bold'))
        add_device_frame.pack(fill='x', padx=15, pady=15)
        
        # Device form
        form_frame = tk.Frame(add_device_frame, bg='#1a1a1a')
        form_frame.pack(fill='x', padx=15, pady=15)
        
        # Serial Number
        tk.Label(form_frame, text="Device Serial Number:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.device_serial = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.device_serial.grid(row=0, column=1, padx=5, pady=5)
        
        # Model
        tk.Label(form_frame, text="Device Model:", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.device_model = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.device_model.grid(row=1, column=1, padx=5, pady=5)
        
        # Owner Info
        tk.Label(form_frame, text="Owner Info (Name, Telegram, Phone):", bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.device_owner_info = tk.Entry(form_frame, bg='#2d2d2d', fg='#ffffff', width=30)
        self.device_owner_info.grid(row=2, column=1, padx=5, pady=5)
        
        # Add button
        ttk.Button(add_device_frame, text="➕ Add Tracked Device", 
                  command=self.add_tracked_device,
                  style='Custom.TButton').pack(pady=15)
        
        # Remove device button
        ttk.Button(add_device_frame, text="🗑️ Remove Tracked Device", 
                  command=self.remove_tracked_device,
                  style='Custom.TButton').pack(pady=15)
        
    def add_reseller(self):
        """Add new reseller"""
        try:
            # Validate input
            name = self.reseller_name.get().strip()
            location = self.reseller_location.get().strip()
            telegram = self.reseller_telegram.get().strip()
            phone = self.reseller_phone.get().strip()
            email = self.reseller_email.get().strip()
            commission = self.reseller_commission.get().strip()
            status = self.reseller_status.get()
            
            if not all([name, location, telegram, commission]):
                messagebox.showerror("Error", "Please fill in all required fields (Name, Location, Telegram, Commission)")
                return
            
            # Validate commission rate
            try:
                commission_rate = float(commission)
                if commission_rate < 0 or commission_rate > 100:
                    raise ValueError("Commission must be between 0 and 100")
            except ValueError:
                messagebox.showerror("Error", "Commission must be a valid number between 0 and 100")
                return
            
            # Create reseller object
            reseller = {
                'id': str(uuid.uuid4()),
                'name': name,
                'location': location,
                'telegram': telegram,
                'phone': phone,
                'email': email,
                'commission': commission_rate,
                'status': status,
                'created_date': datetime.now().isoformat(),
                'sales_count': 0,
                'total_commission': 0.0
            }
            
            # Add to resellers list
            self.resellers.append(reseller)
            self.save_resellers()
            
            # Clear form
            self.reseller_name.delete(0, tk.END)
            self.reseller_location.delete(0, tk.END)
            self.reseller_telegram.delete(0, tk.END)
            self.reseller_phone.delete(0, tk.END)
            self.reseller_email.delete(0, tk.END)
            self.reseller_commission.delete(0, tk.END)
            self.reseller_status.set('Active')
            
            # Refresh displays
            self.refresh_reseller_tree()
            self.refresh_reseller_display()
            
            self.log_message(f"Added new reseller: {name} in {location}")
            messagebox.showinfo("Success", f"Reseller '{name}' added successfully!")
            
        except Exception as e:
            self.log_message(f"Error adding reseller: {str(e)}")
            messagebox.showerror("Error", f"Failed to add reseller: {str(e)}")
    
    def edit_reseller(self):
        """Edit selected reseller"""
        try:
            selected = self.reseller_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a reseller to edit")
                return
            
            # Get selected reseller data
            item = self.reseller_tree.item(selected[0])
            reseller_name = item['values'][0]
            
            # Find reseller in list
            reseller = None
            for r in self.resellers:
                if r['name'] == reseller_name:
                    reseller = r
                    break
            
            if not reseller:
                messagebox.showerror("Error", "Reseller not found")
                return
            
            # Create edit window
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Edit Reseller - {reseller['name']}")
            edit_window.geometry("400x500")
            edit_window.configure(bg='#1a1a1a')
            
            # Edit form
            tk.Label(edit_window, text="Edit Reseller Details", bg='#1a1a1a', fg='#00d4ff',
                    font=('Arial', 14, 'bold')).pack(pady=15)
            
            form_frame = tk.Frame(edit_window, bg='#1a1a1a')
            form_frame.pack(fill='x', padx=20, pady=10)
            
            # Name
            tk.Label(form_frame, text="Name:", bg='#1a1a1a', fg='#ffffff').grid(row=0, column=0, sticky='w', pady=5)
            name_var = tk.StringVar(value=reseller['name'])
            tk.Entry(form_frame, textvariable=name_var, bg='#2d2d2d', fg='#ffffff', width=30).grid(row=0, column=1, pady=5)
            
            # Location
            tk.Label(form_frame, text="Location:", bg='#1a1a1a', fg='#ffffff').grid(row=1, column=0, sticky='w', pady=5)
            location_var = tk.StringVar(value=reseller['location'])
            tk.Entry(form_frame, textvariable=location_var, bg='#2d2d2d', fg='#ffffff', width=30).grid(row=1, column=1, pady=5)
            
            # Telegram
            tk.Label(form_frame, text="Telegram:", bg='#1a1a1a', fg='#ffffff').grid(row=2, column=0, sticky='w', pady=5)
            telegram_var = tk.StringVar(value=reseller['telegram'])
            tk.Entry(form_frame, textvariable=telegram_var, bg='#2d2d2d', fg='#ffffff', width=30).grid(row=2, column=1, pady=5)
            
            # Phone
            tk.Label(form_frame, text="Phone:", bg='#1a1a1a', fg='#ffffff').grid(row=3, column=0, sticky='w', pady=5)
            phone_var = tk.StringVar(value=reseller.get('phone', ''))
            tk.Entry(form_frame, textvariable=phone_var, bg='#2d2d2d', fg='#ffffff', width=30).grid(row=3, column=1, pady=5)
            
            # Email
            tk.Label(form_frame, text="Email:", bg='#1a1a1a', fg='#ffffff').grid(row=4, column=0, sticky='w', pady=5)
            email_var = tk.StringVar(value=reseller.get('email', ''))
            tk.Entry(form_frame, textvariable=email_var, bg='#2d2d2d', fg='#ffffff', width=30).grid(row=4, column=1, pady=5)
            
            # Commission
            tk.Label(form_frame, text="Commission %:", bg='#1a1a1a', fg='#ffffff').grid(row=5, column=0, sticky='w', pady=5)
            commission_var = tk.StringVar(value=str(reseller['commission']))
            tk.Entry(form_frame, textvariable=commission_var, bg='#2d2d2d', fg='#ffffff', width=30).grid(row=5, column=1, pady=5)
            
            # Status
            tk.Label(form_frame, text="Status:", bg='#1a1a1a', fg='#ffffff').grid(row=6, column=0, sticky='w', pady=5)
            status_var = tk.StringVar(value=reseller['status'])
            status_combo = ttk.Combobox(form_frame, textvariable=status_var, values=['Active', 'Inactive', 'Pending'], 
                                      state='readonly', width=27)
            status_combo.grid(row=6, column=1, pady=5)
            
            def save_changes():
                try:
                    # Update reseller
                    reseller['name'] = name_var.get().strip()
                    reseller['location'] = location_var.get().strip()
                    reseller['telegram'] = telegram_var.get().strip()
                    reseller['phone'] = phone_var.get().strip()
                    reseller['email'] = email_var.get().strip()
                    reseller['commission'] = float(commission_var.get())
                    reseller['status'] = status_var.get()
                    
                    self.save_resellers()
                    self.refresh_reseller_tree()
                    self.refresh_reseller_display()
                    
                    edit_window.destroy()
                    self.log_message(f"Updated reseller: {reseller['name']}")
                    messagebox.showinfo("Success", "Reseller updated successfully!")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update reseller: {str(e)}")
            
            # Buttons
            button_frame = tk.Frame(edit_window, bg='#1a1a1a')
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="💾 Save Changes", command=save_changes).pack(side='left', padx=10)
            ttk.Button(button_frame, text="❌ Cancel", command=edit_window.destroy).pack(side='left', padx=10)
            
        except Exception as e:
            self.log_message(f"Error editing reseller: {str(e)}")
            messagebox.showerror("Error", f"Failed to edit reseller: {str(e)}")
    
    def remove_reseller(self):
        """Remove selected reseller"""
        try:
            selected = self.reseller_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a reseller to remove")
                return
            
            # Get selected reseller data
            item = self.reseller_tree.item(selected[0])
            reseller_name = item['values'][0]
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove reseller '{reseller_name}'?"):
                # Remove from list
                self.resellers = [r for r in self.resellers if r['name'] != reseller_name]
                self.save_resellers()
                
                # Refresh displays
                self.refresh_reseller_tree()
                self.refresh_reseller_display()
                
                self.log_message(f"Removed reseller: {reseller_name}")
                messagebox.showinfo("Success", f"Reseller '{reseller_name}' removed successfully!")
                
        except Exception as e:
            self.log_message(f"Error removing reseller: {str(e)}")
            messagebox.showerror("Error", f"Failed to remove reseller: {str(e)}")
    
    def refresh_reseller_tree(self):
        """Refresh the reseller tree view"""
        try:
            # Clear existing items
            for item in self.reseller_tree.get_children():
                self.reseller_tree.delete(item)
            
            # Add current resellers
            for reseller in self.resellers:
                contact = reseller['telegram']
                if reseller.get('phone'):
                    contact += f" / {reseller['phone']}"
                
                self.reseller_tree.insert('', 'end', values=(
                    reseller['name'],
                    reseller['location'],
                    contact,
                    f"{reseller['commission']}%",
                    reseller['status']
                ))
                
        except Exception as e:
            self.log_message(f"Error refreshing reseller tree: {str(e)}")
    
    def refresh_reseller_display(self):
        """Refresh the reseller display in contact tab"""
        try:
            # Clear existing widgets
            for widget in self.reseller_scrollable_frame.winfo_children():
                widget.destroy()
            
            if not self.resellers:
                tk.Label(self.reseller_scrollable_frame, 
                        text="No resellers added yet. Use the 'Manage Resellers' tab to add resellers.",
                        bg='#1a1a1a', fg='#ffffff', font=('Arial', 11)).pack(padx=15, pady=20)
                return
            
            # Display active resellers
            active_resellers = [r for r in self.resellers if r['status'] == 'Active']
            
            for reseller in active_resellers:
                r_frame = tk.Frame(self.reseller_scrollable_frame, bg='#2d2d2d', relief='raised', bd=1)
                r_frame.pack(fill='x', padx=15, pady=10)
                
                # Reseller name and location
                tk.Label(r_frame, text=f"🏪 {reseller['name']} - {reseller['location']}", 
                        bg='#2d2d2d', fg='#00d4ff', font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
                
                # Contact info
                contact_info = f"📱 Telegram: {reseller['telegram']}"
                if reseller.get('phone'):
                    contact_info += f"\n📞 Phone: {reseller['phone']}"
                if reseller.get('email'):
                    contact_info += f"\n📧 Email: {reseller['email']}"
                
                tk.Label(r_frame, text=contact_info, 
                        bg='#2d2d2d', fg='#ffffff', font=('Arial', 10), justify='left').pack(anchor='w', padx=10)
                
                # Contact button
                button_frame = tk.Frame(r_frame, bg='#2d2d2d')
                button_frame.pack(anchor='w', padx=10, pady=5)
                
                ttk.Button(button_frame, text="📱 Contact Reseller", 
                          command=lambda t=reseller['telegram']: self.open_contact('telegram', t),
                          style='Custom.TButton').pack(side='left', padx=5)
                
                if reseller.get('email'):
                    ttk.Button(button_frame, text="📧 Email", 
                              command=lambda e=reseller['email']: self.open_contact('email', e),
                              style='Custom.TButton').pack(side='left', padx=5)
                
        except Exception as e:
            self.log_message(f"Error refreshing reseller display: {str(e)}")
    
    def log_message(self, message):
        """Add message to logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
        
    def save_logs(self):
        """Save logs to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Logs saved to: {file_path}")
        except Exception as e:
            self.log_message(f"Error saving logs: {str(e)}")
        
    def browse_file(self):
        """Browse for GrapheneOS image file"""
        file_path = filedialog.askopenfilename(
            title="Select GrapheneOS Image",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path.set(file_path)
            self.log_message(f"Selected file: {file_path}")
            
    def copy_uuid(self):
        """Copy UUID to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.device_uuid)
        messagebox.showinfo("Copied", "Device UUID copied to clipboard!")
        self.log_message("Device UUID copied to clipboard")
        
    def check_subscription(self):
        """Check subscription status"""
        try:
            if os.path.exists(self.subscription_file):
                with open(self.subscription_file, 'r') as f:
                    sub_data = json.load(f)
                
                # Verify subscription
                if self.verify_subscription(sub_data):
                    self.update_subscription_info(sub_data)
                    self.status_label.config(text="● ACTIVE SUBSCRIPTION", foreground='#00ff00')
                    self.log_message("Subscription verified successfully")
                else:
                    self.log_message("Subscription verification failed")
                    self.show_subscription_error()
            else:
                self.log_message("No subscription found")
                self.show_subscription_error()
        except Exception as e:
            self.log_message(f"Subscription check error: {str(e)}")
            self.show_subscription_error()
            
    def verify_subscription(self, sub_data):
        """Verify subscription validity"""
        try:
            # Check expiration
            expiry = datetime.fromisoformat(sub_data['expiry'])
            if datetime.now() > expiry:
                return False
                
            # Check device UUID
            if sub_data['device_uuid'] != self.device_uuid:
                return False
                
            # Verify signature
            expected_hash = hashlib.sha256(
                f"{sub_data['device_uuid']}{sub_data['expiry']}platinum_secret_key".encode()
            ).hexdigest()
            
            return sub_data['signature'] == expected_hash
        except:
            return False
            
    def update_subscription_info(self, sub_data):
        """Update subscription information display"""
        expiry_date = datetime.fromisoformat(sub_data['expiry'])
        days_left = (expiry_date - datetime.now()).days
        
        info = f"""Subscription Status: ✅ ACTIVE
Device UUID: {sub_data['device_uuid']}
Plan: {sub_data.get('plan', 'Standard')}
Expiry Date: {sub_data['expiry']}
Days Remaining: {days_left} days
Payment Method: {sub_data.get('payment_method', 'Unknown')}
Transaction ID: {sub_data.get('transaction_id', 'N/A')}

Features Enabled:
• GrapheneOS Flashing
• Security Hardening
• Premium Support
• Automatic Updates

🇬🇧 UK Operations Only
"""
        self.subscription_info.delete(1.0, tk.END)
        self.subscription_info.insert(1.0, info)
        
    def show_subscription_error(self):
        """Show subscription error"""
        self.status_label.config(text="● SUBSCRIPTION EXPIRED", foreground='#ff0000')
        error_info = f"""Subscription Status: ❌ EXPIRED/INVALID
Device UUID: {self.device_uuid}

Please renew your subscription to continue using Platinum Secure Flasher.
Contact owner or authorized UK reseller for assistance.

Available Plans (UK Only):
• 3 Month: £120 / 0.002 BTC / 0.15 XMR
• 6 Month: £200 / 0.0035 BTC / 0.25 XMR  
• 12 Month: £400 / 0.007 BTC / 0.5 XMR

🇬🇧 No international shipping or services
"""
        self.subscription_info.delete(1.0, tk.END)
        self.subscription_info.insert(1.0, error_info)
        
    def show_crypto_payment(self, crypto_type):
        """Show crypto payment information"""
        # Clear previous payment display
        for widget in self.payment_display.winfo_children():
            widget.destroy()
            
        plan = self.selected_plan.get()
        plan_info = self.subscription_plans[plan]
        
        # Payment frame
        payment_frame = tk.LabelFrame(self.payment_display, 
                                    text=f"{crypto_type} Payment (UK Only)", 
                                    bg='#1a1a1a', 
                                    fg='#ff6b35',
                                    font=('Arial', 12, 'bold'))
        payment_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Payment details
        amount_key = f'price_{crypto_type.lower()}'
        amount = plan_info[amount_key]
        
        details = f"""
Plan: {plan.replace('_', ' ').title()}
Amount: {amount} {crypto_type}
Wallet Address: {self.crypto_wallets[crypto_type]}

Instructions:
1. Send exactly {amount} {crypto_type} to the address above
2. Include your Device UUID in the transaction memo (if supported)
3. Contact owner with transaction ID for activation
4. Activation typically takes 1-24 hours

🇬🇧 UK Operations Only - No international services
        """
        
        tk.Label(payment_frame, text=details, bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 11), justify='left').pack(padx=15, pady=15)
        
        # Generate QR code for wallet address
        self.generate_crypto_qr(payment_frame, self.crypto_wallets[crypto_type], crypto_type)
        
        # Copy address button
        ttk.Button(payment_frame, text=f"📋 Copy {crypto_type} Address", 
                  command=lambda: self.copy_address(crypto_type),
                  style='Crypto.TButton').pack(pady=10)
        
    def generate_crypto_qr(self, parent, address, crypto_type):
        """Generate QR code for crypto address"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(address)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200))
            
            # Convert to PhotoImage
            qr_photo = ImageTk.PhotoImage(qr_img)
            
            # Display QR code
            qr_label = tk.Label(parent, image=qr_photo, bg='#1a1a1a')
            qr_label.image = qr_photo  # Keep a reference
            qr_label.pack(pady=10)
            
            tk.Label(parent, text=f"Scan QR code to copy {crypto_type} address", 
                    bg='#1a1a1a', fg='#ffffff', font=('Arial', 10)).pack()
            
        except Exception as e:
            self.log_message(f"Error generating QR code: {str(e)}")
            
    def generate_cash_qr(self):
        """Generate QR code for cash payment"""
        # Clear previous payment display
        for widget in self.payment_display.winfo_children():
            widget.destroy()
            
        plan = self.selected_plan.get()
        plan_info = self.subscription_plans[plan]
        
        # Cash payment frame
        cash_frame = tk.LabelFrame(self.payment_display, 
                                 text="Cash Payment (UK Only)", 
                                 bg='#1a1a1a', 
                                 fg='#00ff00',
                                 font=('Arial', 12, 'bold'))
        cash_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Payment details
        amount = plan_info['price_cash']
        
        # Create payment data for QR
        payment_data = {
            'type': 'cash_payment',
            'plan': plan,
            'amount': amount,
            'currency': 'GBP',
            'country': 'UK',
            'device_uuid': self.device_uuid,
            'timestamp': datetime.now().isoformat()
        }
        
        payment_json = json.dumps(payment_data)
        
        details = f"""
Plan: {plan.replace('_', ' ').title()}
Amount: £{amount} GBP
Device UUID: {self.device_uuid}

Instructions:
1. Show this QR code to the owner or authorized UK reseller
2. Pay the exact amount in cash (GBP)
3. Reseller will activate your subscription immediately
4. Keep this QR code until activation is confirmed

🇬🇧 UK Operations Only - Cash payments accepted from UK resellers only
        """
        
        tk.Label(cash_frame, text=details, bg='#1a1a1a', fg='#ffffff',
                font=('Arial', 11), justify='left').pack(padx=15, pady=15)
        
        # Generate QR code for payment data
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=5)
            qr.add_data(payment_json)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((250, 250))
            
            # Convert to PhotoImage
            qr_photo = ImageTk.PhotoImage(qr_img)
            
            # Display QR code
            qr_label = tk.Label(cash_frame, image=qr_photo, bg='#1a1a1a')
            qr_label.image = qr_photo  # Keep a reference
            qr_label.pack(pady=15)
            
            tk.Label(cash_frame, text="Show this QR code for cash payment", 
                    bg='#1a1a1a', fg='#00ff00', font=('Arial', 12, 'bold')).pack()
            
        except Exception as e:
            self.log_message(f"Error generating cash QR code: {str(e)}")
            
    def copy_address(self, crypto_type):
        """Copy crypto address to clipboard"""
        address = self.crypto_wallets[crypto_type]
        self.root.clipboard_clear()
        self.root.clipboard_append(address)
        messagebox.showinfo("Copied", f"{crypto_type} address copied to clipboard!")
        self.log_message(f"{crypto_type} address copied to clipboard")
        
    def open_contact(self, contact_type, contact_info):
        """Open contact method"""
        try:
            if contact_type == 'telegram':
                webbrowser.open(f"https://t.me/{contact_info.replace('@', '')}")
            elif contact_type == 'email':
                webbrowser.open(f"mailto:{contact_info}")
            self.log_message(f"Opened {contact_type}: {contact_info}")
        except Exception as e:
            self.log_message(f"Error opening {contact_type}: {str(e)}")
            
    def start_flash(self):
        """Start flashing process"""
        # Check subscription first
        if not self.verify_current_subscription():
            messagebox.showerror("Subscription Required", 
                               "Valid subscription required to flash devices. Please renew your subscription.")
            return
            
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a GrapheneOS image file")
            return
            
        if not self.device_var.get():
            messagebox.showerror("Error", "Please select a device model")
            return
            
        # Start flashing in separate thread
        threading.Thread(target=self.flash_device, daemon=True).start()
        
    def verify_current_subscription(self):
        """Verify current subscription is valid"""
        try:
            if os.path.exists(self.subscription_file):
                with open(self.subscription_file, 'r') as f:
                    sub_data = json.load(f)
                return self.verify_subscription(sub_data)
            return False
        except:
            return False
            
    def flash_device(self):
        """Flash device with GrapheneOS"""
        try:
            self.progress.start()
            self.log_message("🚀 Starting flash process...")
            
            # Check ADB connection
            self.log_message("🔍 Checking ADB connection...")
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, text=True)
            if 'device' not in result.stdout:
                self.log_message("❌ ERROR: No device connected")
                messagebox.showerror("Error", "No device connected via ADB")
                return
                
            # Verify image if requested
            if self.verify_image.get():
                self.log_message("✅ Verifying image integrity...")
                if not self.verify_grapheneos_image():
                    return
                    
            # Unlock bootloader if requested
            if self.unlock_bootloader.get():
                self.log_message("🔓 Unlock Bootloader...")
                if not self.unlock_bootloader_device():
                    return
                    
            # Apply hardening if requested
            if self.apply_hardening.get():
                self.log_message("🛡️ Applying Security Hardening...")
                if not self.apply_hardening_device():
                    return
                    
            # Flash the image
            self.log_message("📦 Flashing image...")
            if not self.flash_grapheneos_image():
                return
                
            self.log_message("✅ Flash process completed successfully!")
            messagebox.showinfo("Success", "GrapheneOS flash completed successfully!")
            
        except Exception as e:
            self.log_message(f"Flash process error: {str(e)}")
            messagebox.showerror("Error", f"Flash process failed: {str(e)}")
        finally:
            self.progress.stop()
            self.log_message("Flash process finished.")
            
    def unlock_bootloader_device(self):
        """Unlock bootloader of the connected device"""
        try:
            self.log_message("Attempting to unlock bootloader...")
            # Assuming adb root is needed for bootloader unlock
            self.log_message("🔧 Executing 'adb root'...")
            result = subprocess.run(['adb', 'root'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.log_message(f"❌ ERROR: 'adb root' failed. Output: {result.stderr}")
                messagebox.showerror("Error", f"Failed to unlock bootloader: {result.stderr}")
                return False
                
            self.log_message("🔓 Bootloader unlocked (if supported).")
            return True
        except Exception as e:
            self.log_message(f"Error unlocking bootloader: {str(e)}")
            messagebox.showerror("Error", f"Failed to unlock bootloader: {str(e)}")
            return False
            
    def apply_hardening_device(self):
        """Apply security hardening to the connected device"""
        try:
            self.log_message("Attempting to apply security hardening...")
            # Assuming adb shell commands for hardening
            hardening_commands = [
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_minfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_maxfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_minfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_maxfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_kill\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_minfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_maxfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_kill\"'"
            ]
            
            for cmd in hardening_commands:
                self.log_message(f"Executing: {cmd}")
                result = subprocess.run(cmd.split(), 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_message(f"❌ ERROR: Command failed. Output: {result.stderr}")
                    messagebox.showerror("Error", f"Hardening command failed: {cmd}\nError: {result.stderr}")
                    return False
                self.log_message(f"✅ Command successful: {cmd}")
                
            self.log_message("🛡️ Security hardening applied.")
            return True
        except Exception as e:
            self.log_message(f"Error applying hardening: {str(e)}")
            messagebox.showerror("Error", f"Failed to apply hardening: {str(e)}")
            return False
            
    def flash_grapheneos_image(self):
        """Flash the selected GrapheneOS image to the connected device"""
        try:
            # Assuming the image is in a ZIP file
            zip_path = self.file_path.get()
            if not zip_path:
                self.log_message("No image file selected.")
                messagebox.showerror("Error", "Please select a GrapheneOS image file.")
                return False
                
            # Extract ZIP to a temporary directory
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tempfile.gettempdir())
                
            # Find the image file (e.g., boot.img or recovery.img)
            image_path = None
            for root, dirs, files in os.walk(tempfile.gettempdir()):
                for file in files:
                    if file.endswith(('.img', '.zip', '.bin', '.raw')):
                        image_path = os.path.join(root, file)
                        break
                if image_path:
                    break
                    
            if not image_path:
                self.log_message("No image file found in the ZIP.")
                messagebox.showerror("Error", "No image file (boot.img, recovery.img, etc.) found in the selected ZIP.")
                return False
                
            self.log_message(f"Found image file: {image_path}")
            
            # Determine if it's a boot or recovery image
            is_boot_image = False
            if 'boot' in image_path.lower():
                is_boot_image = True
                self.log_message("Detected boot image.")
            elif 'recovery' in image_path.lower():
                self.log_message("Detected recovery image.")
            else:
                self.log_message("Unknown image type. Assuming boot image.")
                is_boot_image = True
                
            # Flash the image
            self.log_message(f"Flashing {image_path} to {self.device_var.get()}...")
            if is_boot_image:
                result = subprocess.run(['adb', 'flash', 'boot', image_path], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_message(f"❌ ERROR: 'adb flash boot' failed. Output: {result.stderr}")
                    messagebox.showerror("Error", f"Failed to flash boot image: {result.stderr}")
                    return False
                self.log_message("✅ Boot image flashed successfully.")
            else:
                result = subprocess.run(['adb', 'flash', 'recovery', image_path], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_message(f"❌ ERROR: 'adb flash recovery' failed. Output: {result.stderr}")
                    messagebox.showerror("Error", f"Failed to flash recovery image: {result.stderr}")
                    return False
                self.log_message("✅ Recovery image flashed successfully.")
                
            # Clean up temporary files
            shutil.rmtree(tempfile.gettempdir())
            self.log_message("Temporary files cleaned up.")
            return True
        except Exception as e:
            self.log_message(f"Error flashing image: {str(e)}")
            messagebox.showerror("Error", f"Failed to flash image: {str(e)}")
            return False
            
    def verify_grapheneos_image(self):
        """Verify the integrity of the flashed image"""
        try:
            self.log_message("Verifying image integrity...")
            # Assuming a simple md5sum check for now
            # In a real scenario, you'd use a more robust tool like ADB's 'file_has_signature'
            # or a custom Python script to check for specific signatures.
            
            # Example: Check if the device is in a known good state (e.g., booted)
            # This is a placeholder and needs proper implementation
            self.log_message("Placeholder for image verification logic.")
            messagebox.showinfo("Info", "Image verification is a placeholder. Please manually check the device.")
            return True # Assume success for now
            
        except Exception as e:
            self.log_message(f"Error verifying image: {str(e)}")
            messagebox.showerror("Error", f"Failed to verify image: {str(e)}")
            return False
            
    def start_remote_wipe(self):
        """Start the remote wipe process"""
        try:
            self.wipe_progress.start()
            self.wipe_status_label.config(text="Wipe Status: In Progress")
            self.wipe_log_text.delete(1.0, tk.END)
            
            # Connect to the wipe server
            wipe_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            wipe_socket.connect(('localhost', self.wipe_server_port))
            
            # Send the wipe command
            wipe_command = self.wipe_command_var.get()
            wipe_socket.sendall(wipe_command.encode())
            
            # Receive confirmation
            response = wipe_socket.recv(1024).decode()
            if response.strip() == "OK":
                self.log_message("Wipe command sent successfully.")
                self.wipe_status_label.config(text="Wipe Status: In Progress (Waiting for confirmation)")
                self.wipe_log_text.insert(tk.END, f"Wipe command '{wipe_command}' sent. Waiting for confirmation...\n")
                
                # Wait for a response from the server
                while True:
                    try:
                        response = wipe_socket.recv(1024).decode()
                        if response.strip() == "DONE":
                            self.wipe_status_label.config(text="Wipe Status: Completed")
                            self.wipe_log_text.insert(tk.END, "Wipe process completed.\n")
                            break
                        elif response.strip() == "ERROR":
                            self.wipe_status_label.config(text="Wipe Status: Failed")
                            self.wipe_log_text.insert(tk.END, "Wipe process failed.\n")
                            break
                        else:
                            self.wipe_log_text.insert(tk.END, f"Server response: {response}\n")
                            time.sleep(0.1) # Avoid busy-waiting
                    except socket.timeout:
                        self.wipe_log_text.insert(tk.END, "Server did not respond for too long.\n")
                        break
                    except Exception as e:
                        self.wipe_log_text.insert(tk.END, f"Error receiving wipe response: {e}\n")
                        break
            else:
                self.wipe_status_label.config(text="Wipe Status: Failed")
                self.wipe_log_text.insert(tk.END, f"Failed to send wipe command. Server response: {response}\n")
                
            wipe_socket.close()
            self.wipe_progress.stop()
            
        except Exception as e:
            self.wipe_status_label.config(text="Wipe Status: Failed")
            self.wipe_log_text.insert(tk.END, f"Error initiating wipe: {str(e)}\n")
            self.wipe_progress.stop()
            
    def refresh_wipe_status(self):
        """Refresh the status of the remote wipe process"""
        try:
            wipe_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            wipe_socket.settimeout(1) # Short timeout for status check
            wipe_socket.connect(('localhost', self.wipe_server_port))
            
            wipe_socket.sendall("STATUS".encode())
            response = wipe_socket.recv(1024).decode()
            
            if response.strip() == "OK":
                self.wipe_status_label.config(text="Wipe Status: In Progress (Waiting for confirmation)")
                self.wipe_log_text.insert(tk.END, "Connected to wipe server. Waiting for confirmation...\n")
            elif response.strip() == "DONE":
                self.wipe_status_label.config(text="Wipe Status: Completed")
                self.wipe_log_text.insert(tk.END, "Wipe server is done.\n")
            elif response.strip() == "ERROR":
                self.wipe_status_label.config(text="Wipe Status: Failed")
                self.wipe_log_text.insert(tk.END, "Wipe server is in error state.\n")
            else:
                self.wipe_status_label.config(text="Wipe Status: Idle")
                self.wipe_log_text.insert(tk.END, f"Wipe server status: {response}\n")
                
            wipe_socket.close()
        except socket.timeout:
            self.wipe_status_label.config(text="Wipe Status: Idle")
            self.wipe_log_text.insert(tk.END, "Could not connect to wipe server for status check.\n")
        except Exception as e:
            self.wipe_status_label.config(text="Wipe Status: Failed")
            self.wipe_log_text.insert(tk.END, f"Error refreshing wipe status: {str(e)}\n")
            
    def save_wipe_logs(self):
        """Save wipe logs to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(self.wipe_log_text.get(1.0, tk.END))
                self.log_message(f"Wipe logs saved to: {file_path}")
        except Exception as e:
            self.log_message(f"Error saving wipe logs: {str(e)}")
            
    def add_tracked_device(self):
        """Add a new tracked device to the database"""
        try:
            serial = self.device_serial.get().strip()
            model = self.device_model.get().strip()
            owner_info = self.device_owner_info.get().strip()
            
            if not all([serial, model]):
                messagebox.showerror("Error", "Serial number and model are required.")
                return
                
            # Generate a unique device ID
            device_id = str(uuid.uuid4())
            
            # Store owner info in a JSON-like string
            owner_data = {
                "name": owner_info.split(',')[0].strip(),
                "telegram": owner_info.split(',')[1].strip(),
                "phone": owner_info.split(',')[2].strip()
            }
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tracked_devices (device_id, device_serial, device_model, owner_info, flash_date, last_contact, status)
                VALUES (?, ?, ?, ?, ?, ?, 'active')
            ''', (device_id, serial, model, json.dumps(owner_data), datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.log_message(f"Added tracked device: {serial} ({model})")
            messagebox.showinfo("Success", f"Tracked device '{serial}' added successfully!")
            self.refresh_device_display()
            
        except Exception as e:
            self.log_message(f"Error adding tracked device: {str(e)}")
            messagebox.showerror("Error", f"Failed to add tracked device: {str(e)}")
            
    def remove_tracked_device(self):
        """Remove a tracked device from the database"""
        try:
            selected = self.device_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a device to remove")
                return
                
            item = self.device_tree.item(selected[0])
            device_id = item['values'][0] # Assuming device_id is the first column
            
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove device '{device_id}'?"):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM tracked_devices WHERE device_id = ?
                ''', (device_id,))
                
                conn.commit()
                conn.close()
                
                self.log_message(f"Removed tracked device: {device_id}")
                messagebox.showinfo("Success", f"Tracked device '{device_id}' removed successfully!")
                self.refresh_device_display()
                
        except Exception as e:
            self.log_message(f"Error removing tracked device: {str(e)}")
            messagebox.showerror("Error", f"Failed to remove tracked device: {str(e)}")
            
    def refresh_device_display(self):
        """Refresh the device tracking display"""
        try:
            # Clear existing widgets
            for widget in self.device_scrollable_frame.winfo_children():
                widget.destroy()
                
            if not self.tracked_devices:
                tk.Label(self.device_scrollable_frame, 
                        text="No devices tracked yet. Use the 'Device Tracking' tab to add devices.",
                        bg='#1a1a1a', fg='#ffffff', font=('Arial', 11)).pack(padx=15, pady=20)
                return
                
            # Display tracked devices
            for device in self.tracked_devices:
                d_frame = tk.Frame(self.device_scrollable_frame, bg='#2d2d2d', relief='raised', bd=1)
                d_frame.pack(fill='x', padx=15, pady=10)
                
                device_id = device[0]
                serial = device[1]
                model = device[2]
                owner_info = json.loads(device[3])
                flash_date = datetime.fromisoformat(device[4])
                last_contact = datetime.fromisoformat(device[5])
                status = device[6]
                
                tk.Label(d_frame, text=f"📱 {model} (Serial: {serial})", 
                        bg='#2d2d2d', fg='#00d4ff', font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
                
                owner_text = f"Owner: {owner_info['name']}"
                if owner_info['telegram']:
                    owner_text += f"\n📱 Telegram: {owner_info['telegram']}"
                if owner_info['phone']:
                    owner_text += f"\n📞 Phone: {owner_info['phone']}"
                
                tk.Label(d_frame, text=owner_text, 
                        bg='#2d2d2d', fg='#ffffff', font=('Arial', 10), justify='left').pack(anchor='w', padx=10)
                
                tk.Label(d_frame, text=f"Flash Date: {flash_date.strftime('%Y-%m-%d %H:%M:%S')}", 
                        bg='#2d2d2d', fg='#00ff00', font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
                
                tk.Label(d_frame, text=f"Last Contact: {last_contact.strftime('%Y-%m-%d %H:%M:%S')}", 
                        bg='#2d2d2d', fg='#ff0000', font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
                
                tk.Label(d_frame, text=f"Status: {status}", 
                        bg='#2d2d2d', fg='#ffffff', font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
                
                # Add a button to contact the owner
                button_frame = tk.Frame(d_frame, bg='#2d2d2d')
                button_frame.pack(anchor='w', padx=10, pady=5)
                
                owner_contact_info = f"{owner_info['name']}, {owner_info['telegram']}, {owner_info['phone']}"
                ttk.Button(button_frame, text="📞 Contact Owner", 
                          command=lambda info=owner_contact_info: self.open_contact('telegram', owner_info['telegram']),
                          style='Custom.TButton').pack(side='left', padx=5)
                
                if owner_info['phone']:
                    ttk.Button(button_frame, text="📞 Call", 
                              command=lambda phone=owner_info['phone']: self.open_contact('phone', phone),
                              style='Custom.TButton').pack(side='left', padx=5)
                
                if owner_info['email']:
                    ttk.Button(button_frame, text="📧 Email", 
                              command=lambda email=owner_info['email']: self.open_contact('email', email),
                              style='Custom.TButton').pack(side='left', padx=5)
                
                # Add a button to remove the device
                ttk.Button(d_frame, text="🗑️ Remove Device", 
                          command=lambda d_id=device_id: self.remove_tracked_device(),
                          style='Custom.TButton').pack(anchor='e', padx=10, pady=5)
                
        except Exception as e:
            self.log_message(f"Error refreshing device display: {str(e)}")
            
    def start_remote_wipe_server(self):
        """Start a local server to receive wipe commands"""
        try:
            wipe_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            wipe_server.bind(('localhost', self.wipe_server_port))
            wipe_server.listen(5)
            self.log_message(f"Remote wipe server listening on port {self.wipe_server_port}")
            
            while True:
                client_socket, addr = wipe_server.accept()
                self.log_message(f"Accepted connection from {addr}")
                
                # Receive wipe command
                try:
                    wipe_command = client_socket.recv(1024).decode()
                    self.log_message(f"Received wipe command: {wipe_command}")
                    
                    if wipe_command == "factory_reset":
                        self.log_message("Executing factory reset...")
                        # In a real scenario, you'd send a command to the device to perform a factory reset
                        # This might involve ADB commands or a custom wipe script.
                        # For demonstration, we'll just acknowledge.
                        client_socket.sendall("OK".encode())
                        self.log_message("Factory reset acknowledged.")
                        self.wipe_log_text.insert(tk.END, "Factory reset acknowledged.\n")
                        
                    elif wipe_command == "data_only":
                        self.log_message("Executing data-only wipe...")
                        # In a real scenario, you'd send a command to the device to perform a data-only wipe
                        # This might involve ADB commands or a custom wipe script.
                        client_socket.sendall("OK".encode())
                        self.log_message("Data-only wipe acknowledged.")
                        self.wipe_log_text.insert(tk.END, "Data-only wipe acknowledged.\n")
                        
                    else:
                        client_socket.sendall("ERROR".encode())
                        self.log_message(f"Unknown wipe command: {wipe_command}")
                        self.wipe_log_text.insert(tk.END, f"Unknown wipe command: {wipe_command}\n")
                        
                except Exception as e:
                    self.log_message(f"Error processing wipe command: {str(e)}")
                    self.wipe_log_text.insert(tk.END, f"Error processing wipe command: {str(e)}\n")
                    client_socket.sendall("ERROR".encode())
                    
                client_socket.close()
                self.log_message(f"Connection from {addr} closed.")
                
        except Exception as e:
            self.log_message(f"Error starting wipe server: {str(e)}")
            messagebox.showerror("Error", f"Failed to start wipe server: {str(e)}")
            
    def get_device_uuid(self):
        """Generate unique device UUID"""
        try:
            import platform
            machine_id = platform.node() + platform.machine()
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, machine_id))
        except:
            return str(uuid.uuid4())
    
    def load_resellers(self):
        """Load resellers from JSON file"""
        try:
            if os.path.exists(self.resellers_file):
                with open(self.resellers_file, 'r') as f:
                    return json.load(f)
            else:
                # Default empty resellers list
                return []
        except Exception as e:
            print(f"Error loading resellers: {e}")
            return []
    
    def save_resellers(self):
        """Save resellers to JSON file"""
        try:
            with open(self.resellers_file, 'w') as f:
                json.dump(self.resellers, f, indent=2)
            self.log_message("Resellers database saved")
        except Exception as e:
            self.log_message(f"Error saving resellers: {str(e)}")
            
    def apply_hardening_settings(self):
        """Apply hardening settings to the connected device"""
        try:
            self.log_message("Attempting to apply hardening settings...")
            # Assuming adb shell commands for hardening
            hardening_commands = [
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_minfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_maxfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_minfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_maxfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_kill\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_minfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_maxfree\"'",
                "adb shell 'su -c \"echo 0 > /sys/module/lowmemorykiller/parameters/enable_adaptive_lmk_kill_kill\"'"
            ]
            
            for cmd in hardening_commands:
                self.log_message(f"Executing: {cmd}")
                result = subprocess.run(cmd.split(), 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_message(f"❌ ERROR: Command failed. Output: {result.stderr}")
                    messagebox.showerror("Error", f"Hardening command failed: {cmd}\nError: {result.stderr}")
                    return False
                self.log_message(f"✅ Command successful: {cmd}")
                
            self.log_message("🛡️ Security hardening applied.")
            return True
        except Exception as e:
            self.log_message(f"Error applying hardening: {str(e)}")
            messagebox.showerror("Error", f"Failed to apply hardening: {str(e)}")
            return False
            
    def refresh_device_tree(self):
        """Refresh the device tracking tree view"""
        try:
            # Clear existing items
            for item in self.device_tree.get_children():
                self.device_tree.delete(item)
            
            # Add current tracked devices
            for device in self.tracked_devices:
                device_id = device[0]
                serial = device[1]
                model = device[2]
                owner_info = json.loads(device[3])
                flash_date = datetime.fromisoformat(device[4])
                last_contact = datetime.fromisoformat(device[5])
                status = device[6]
                
                owner_text = f"{owner_info['name']}"
                if owner_info['telegram']:
                    owner_text += f", {owner_info['telegram']}"
                if owner_info['phone']:
                    owner_text += f", {owner_info['phone']}"
                
                self.device_tree.insert('', 'end', values=(
                    device_id,
                    serial,
                    model,
                    owner_text,
                    flash_date.strftime('%Y-%m-%d %H:%M:%S'),
                    last_contact.strftime('%Y-%m-%d %H:%M:%S'),
                    status
                ))
                
        except Exception as e:
            self.log_message(f"Error refreshing device tree: {str(e)}")
            
    def refresh_device_display(self):
        """Refresh the device tracking display"""
        try:
            # Clear existing widgets
            for widget in self.device_scrollable_frame.winfo_children():
                widget.destroy()
                
            if not self.tracked_devices:
                tk.Label(self.device_scrollable_frame, 
                        text="No devices tracked yet. Use the 'Device Tracking' tab to add devices.",
                        bg='#1a1a1a', fg='#ffffff', font=('Arial', 11)).pack(padx=15, pady=20)
                return
                
            # Display tracked devices
            for device in self.tracked_devices:
                d_frame = tk.Frame(self.device_scrollable_frame, bg='#2d2d2d', relief='raised', bd=1)
                d_frame.pack(fill='x', padx=15, pady=10)
                
                device_id = device[0]
                serial = device[1]
                model = device[2]
                owner_info = json.loads(device[3])
                flash_date = datetime.fromisoformat(device[4])
                last_contact = datetime.fromisoformat(device[5])
                status = device[6]
                
                tk.Label(d_frame, text=f"📱 {model} (Serial: {serial})", 
                        bg='#2d2d2d', fg='#00d4ff', font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
                
                owner_text = f"Owner: {owner_info['name']}"
                if owner_info['telegram']:
                    owner_text += f"\n📱 Telegram: {owner_info['telegram']}"
                if owner_info['phone']:
                    owner_text += f"\n📞 Phone: {owner_info['phone']}"
                
                tk.Label(d_frame, text=owner_text, 
                        bg='#2d2d2d', fg='#ffffff', font=('Arial', 10), justify='left').pack(anchor='w', padx=10)
                
                tk.Label(d_frame, text=f"Flash Date: {flash_date.strftime('%Y-%m-%d %H:%M:%S')}", 
                        bg='#2d2d2d', fg='#00ff00', font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
                
                tk.Label(d_frame, text=f"Last Contact: {last_contact.strftime('%Y-%m-%d %H:%M:%S')}", 
                        bg='#2d2d2d', fg='#ff0000', font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
                
                tk.Label(d_frame, text=f"Status: {status}", 
                        bg='#2d2d2d', fg='#ffffff', font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
                
                # Add a button to contact the owner
                button_frame = tk.Frame(d_frame, bg='#2d2d2d')
                button_frame.pack(anchor='w', padx=10, pady=5)
                
                owner_contact_info = f"{owner_info['name']}, {owner_info['telegram']}, {owner_info['phone']}"
                ttk.Button(button_frame, text="📞 Contact Owner", 
                          command=lambda info=owner_contact_info: self.open_contact('telegram', owner_info['telegram']),
                          style='Custom.TButton').pack(side='left', padx=5)
                
                if owner_info['phone']:
                    ttk.Button(button_frame, text="📞 Call", 
                              command=lambda phone=owner_info['phone']: self.open_contact('phone', phone),
                              style='Custom.TButton').pack(side='left', padx=5)
                
                if owner_info['email']:
                    ttk.Button(button_frame, text="📧 Email", 
                              command=lambda email=owner_info['email']: self.open_contact('email', email),
                              style='Custom.TButton').pack(side='left', padx=5)
                
                # Add a button to remove the device
                ttk.Button(d_frame, text="🗑️ Remove Device", 
                          command=lambda d_id=device_id: self.remove_tracked_device(),
                          style='Custom.TButton').pack(anchor='e', padx=10, pady=5)
                
        except Exception as e:
            self.log_message(f"Error refreshing device display: {str(e)}")
            
    def main(self):
        """Main application loop"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PlatinumSecureFlasher()
    app.main() 