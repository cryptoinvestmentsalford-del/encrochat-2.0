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

class PlatinumSecureFlasher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Platinum Secure Flasher v3.0 - UK Professional Edition")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        
        # Subscription system
        self.license_file = "platinum_license.json"
        self.subscription_file = "platinum_subscription.json"
        self.resellers_file = "platinum_resellers.json"
        self.device_uuid = self.get_device_uuid()
        
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
                self.log_message("🔓 