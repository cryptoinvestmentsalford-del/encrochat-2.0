#!/usr/bin/env python3
"""
Platinum Secure Flasher - Android Management App
Reseller and Subscription Management Mobile Application
UK Operations Only
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
import json
import uuid
from datetime import datetime, timedelta
import hashlib
import base64

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = Label(
            text='🇬🇧 PLATINUM SECURE FLASHER\nAndroid Management App',
            size_hint=(1, 0.3),
            font_size='24sp',
            halign='center',
            color=(0, 0.83, 1, 1)  # Blue color
        )
        main_layout.add_widget(title)
        
        # Login form
        form_layout = GridLayout(cols=1, spacing=15, size_hint=(1, 0.5))
        
        # Username field
        self.username_input = TextInput(
            hint_text='Username',
            multiline=False,
            size_hint=(1, None),
            height='48dp',
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1)
        )
        form_layout.add_widget(self.username_input)
        
        # Password field
        self.password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint=(1, None),
            height='48dp',
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1)
        )
        form_layout.add_widget(self.password_input)
        
        # Login button
        login_btn = Button(
            text='🔑 LOGIN',
            size_hint=(1, None),
            height='50dp',
            background_color=(0, 0.83, 1, 1),
            color=(1, 1, 1, 1)
        )
        login_btn.bind(on_press=self.login)
        form_layout.add_widget(login_btn)
        
        main_layout.add_widget(form_layout)
        
        # Footer
        footer = Label(
            text='UK Operations Only - Authorized Resellers',
            size_hint=(1, 0.2),
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        main_layout.add_widget(footer)
        
        self.add_widget(main_layout)
        
    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if not username or not password:
            self.show_popup('Error', 'Please enter username and password')
            return
            
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Send login request
        login_data = {
            'username': username,
            'password_hash': password_hash,
            'device_id': self.get_device_id()
        }
        
        # In a real app, this would be your API endpoint
        # For demo purposes, we'll simulate success
        self.authenticate_user(login_data)
        
    def get_device_id(self):
        """Generate unique device ID"""
        try:
            # In a real Android app, you'd use proper device ID methods
            return str(uuid.uuid4())
        except:
            return str(uuid.uuid4())
            
    def authenticate_user(self, login_data):
        """Authenticate user with backend"""
        # Simulate successful authentication
        # In real implementation, this would connect to your API server
        if login_data['username'] in ['admin', 'reseller1', 'reseller2']:
            # Store user session
            self.manager.current_user = {
                'username': login_data['username'],
                'role': 'admin' if login_data['username'] == 'admin' else 'reseller',
                'device_id': login_data['device_id'],
                'login_time': datetime.now().isoformat()
            }
            
            # Navigate to main screen
            self.manager.current = 'main'
        else:
            self.show_popup('Error', 'Invalid credentials')
            
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(
            text='PLATINUM SECURE MANAGEMENT',
            size_hint=(1, 0.15),
            font_size='20sp',
            color=(0, 0.83, 1, 1)
        )
        main_layout.add_widget(header)
        
        # Menu buttons
        menu_layout = GridLayout(cols=2, spacing=10, size_hint=(1, 0.7))
        
        # Subscription Management
        sub_btn = Button(
            text='📱 Subscription\nManagement',
            background_color=(0, 0.83, 1, 1),
            color=(1, 1, 1, 1)
        )
        sub_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'subscriptions'))
        menu_layout.add_widget(sub_btn)
        
        # Reseller Management
        reseller_btn = Button(
            text='🏪 Reseller\nManagement',
            background_color=(0.16, 0.66, 0.27, 1),
            color=(1, 1, 1, 1)
        )
        reseller_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'resellers'))
        menu_layout.add_widget(reseller_btn)
        
        # Device Tracking
        device_btn = Button(
            text='📱 Device\nTracking',
            background_color=(1, 0.42, 0.21, 1),
            color=(1, 1, 1, 1)
        )
        device_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'devices'))
        menu_layout.add_widget(device_btn)
        
        # Remote Wipe
        wipe_btn = Button(
            text='🧹 Remote\nWipe',
            background_color=(0.86, 0.2, 0.27, 1),
            color=(1, 1, 1, 1)
        )
        wipe_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'wipe'))
        menu_layout.add_widget(wipe_btn)
        
        # Analytics
        analytics_btn = Button(
            text='📊 Analytics\n& Reports',
            background_color=(0.61, 0.15, 0.69, 1),
            color=(1, 1, 1, 1)
        )
        analytics_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'analytics'))
        menu_layout.add_widget(analytics_btn)
        
        # Settings
        settings_btn = Button(
            text='⚙️ Settings\n& Logout',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        settings_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        menu_layout.add_widget(settings_btn)
        
        main_layout.add_widget(menu_layout)
        
        # Status bar
        self.status_label = Label(
            text='Status: Connected to Platinum Secure API',
            size_hint=(1, 0.15),
            font_size='14sp',
            color=(0, 1, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)

class SubscriptionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subscriptions = []
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        back_btn = Button(
            text='← Back',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='📱 Subscription Management',
            size_hint=(0.6, 1),
            font_size='18sp',
            color=(0, 0.83, 1, 1)
        )
        header_layout.add_widget(title)
        
        refresh_btn = Button(
            text='🔄 Refresh',
            size_hint=(0.2, 1),
            background_color=(0, 0.83, 1, 1)
        )
        refresh_btn.bind(on_press=self.refresh_subscriptions)
        header_layout.add_widget(refresh_btn)
        
        main_layout.add_widget(header_layout)
        
        # Subscription list
        scroll = ScrollView()
        self.subscription_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.subscription_layout.bind(minimum_height=self.subscription_layout.setter('height'))
        scroll.add_widget(self.subscription_layout)
        main_layout.add_widget(scroll)
        
        # Add subscription button
        add_btn = Button(
            text='➕ Add New Subscription',
            size_hint=(1, 0.1),
            background_color=(0, 0.83, 1, 1)
        )
        add_btn.bind(on_press=self.show_add_subscription)
        main_layout.add_widget(add_btn)
        
        self.add_widget(main_layout)
        
    def refresh_subscriptions(self, instance):
        """Refresh subscription list"""
        # Clear existing subscriptions
        self.subscription_layout.clear_widgets()
        
        # Sample subscription data
        sample_subscriptions = [
            {
                'uuid': str(uuid.uuid4()),
                'plan': '3 Month',
                'expiry': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
                'status': 'Active',
                'payment': 'BTC',
                'amount': '0.002'
            },
            {
                'uuid': str(uuid.uuid4()),
                'plan': '6 Month',
                'expiry': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
                'status': 'Active',
                'payment': 'Cash',
                'amount': '£200'
            }
        ]
        
        for sub in sample_subscriptions:
            self.add_subscription_widget(sub)
            
    def add_subscription_widget(self, subscription):
        """Add a subscription widget to the list"""
        sub_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='120dp',
            padding=10
        )
        
        # Background
        sub_layout.canvas.before.clear()
        with sub_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.1, 0.1, 0.1, 1)
            rect = Rectangle(size=sub_layout.size, pos=sub_layout.pos)
            sub_layout.bind(size=rect.setter('size'), pos=rect.setter('pos'))
        
        # Subscription info
        info_text = f"Plan: {subscription['plan']}\nExpiry: {subscription['expiry']}\nStatus: {subscription['status']}\nPayment: {subscription['payment']} ({subscription['amount']})"
        
        info_label = Label(
            text=info_text,
            size_hint_y=0.8,
            text_size=(None, None),
            halign='left',
            color=(1, 1, 1, 1)
        )
        sub_layout.add_widget(info_label)
        
        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        
        edit_btn = Button(
            text='✏️ Edit',
            size_hint_x=0.33,
            background_color=(0, 0.83, 1, 1)
        )
        button_layout.add_widget(edit_btn)
        
        extend_btn = Button(
            text='⏱️ Extend',
            size_hint_x=0.33,
            background_color=(0.16, 0.66, 0.27, 1)
        )
        button_layout.add_widget(extend_btn)
        
        delete_btn = Button(
            text='🗑️ Delete',
            size_hint_x=0.33,
            background_color=(0.86, 0.2, 0.27, 1)
        )
        button_layout.add_widget(delete_btn)
        
        sub_layout.add_widget(button_layout)
        self.subscription_layout.add_widget(sub_layout)
        
    def show_add_subscription(self, instance):
        """Show add subscription dialog"""
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Plan selection
        popup_layout.add_widget(Label(text='Select Plan:', color=(1, 1, 1, 1)))
        
        plan_layout = BoxLayout(orientation='horizontal')
        
        plan_3m = Button(text='3 Month\n£120', background_color=(0, 0.83, 1, 1))
        plan_6m = Button(text='6 Month\n£200', background_color=(0, 0.83, 1, 1))
        plan_12m = Button(text='12 Month\n£400', background_color=(0, 0.83, 1, 1))
        
        plan_layout.add_widget(plan_3m)
        plan_layout.add_widget(plan_6m)
        plan_layout.add_widget(plan_12m)
        
        popup_layout.add_widget(plan_layout)
        
        # Customer info
        customer_input = TextInput(
            hint_text='Customer Name',
            size_hint_y=None,
            height='40dp'
        )
        popup_layout.add_widget(customer_input)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal')
        
        cancel_btn = Button(text='Cancel', background_color=(0.5, 0.5, 0.5, 1))
        create_btn = Button(text='Create', background_color=(0.16, 0.66, 0.27, 1))
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(create_btn)
        
        popup_layout.add_widget(button_layout)
        
        popup = Popup(
            title='Add New Subscription',
            content=popup_layout,
            size_hint=(0.9, 0.7)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        create_btn.bind(on_press=lambda x: self.create_subscription(popup, customer_input.text))
        
        popup.open()
        
    def create_subscription(self, popup, customer_name):
        """Create new subscription"""
        if not customer_name:
            return
            
        # Generate new subscription
        new_sub = {
            'uuid': str(uuid.uuid4()),
            'customer': customer_name,
            'plan': '3 Month',  # Default
            'expiry': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
            'status': 'Pending',
            'payment': 'Pending',
            'amount': '£120'
        }
        
        self.add_subscription_widget(new_sub)
        popup.dismiss()

class ResellerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        back_btn = Button(
            text='← Back',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='🏪 Reseller Management',
            size_hint=(0.6, 1),
            font_size='18sp',
            color=(0.16, 0.66, 0.27, 1)
        )
        header_layout.add_widget(title)
        
        refresh_btn = Button(
            text='🔄 Refresh',
            size_hint=(0.2, 1),
            background_color=(0.16, 0.66, 0.27, 1)
        )
        refresh_btn.bind(on_press=self.refresh_resellers)
        header_layout.add_widget(refresh_btn)
        
        main_layout.add_widget(header_layout)
        
        # Reseller list
        scroll = ScrollView()
        self.reseller_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.reseller_layout.bind(minimum_height=self.reseller_layout.setter('height'))
        scroll.add_widget(self.reseller_layout)
        main_layout.add_widget(scroll)
        
        # Add reseller button
        add_btn = Button(
            text='➕ Add New Reseller',
            size_hint=(1, 0.1),
            background_color=(0.16, 0.66, 0.27, 1)
        )
        add_btn.bind(on_press=self.show_add_reseller)
        main_layout.add_widget(add_btn)
        
        self.add_widget(main_layout)
        
    def refresh_resellers(self, instance):
        """Refresh reseller list"""
        self.reseller_layout.clear_widgets()
        
        # Sample reseller data
        sample_resellers = [
            {
                'name': 'London Tech Solutions',
                'location': 'London, UK',
                'contact': '@LondonTech',
                'commission': '15%',
                'status': 'Active',
                'sales': 25
            },
            {
                'name': 'Manchester Mobile',
                'location': 'Manchester, UK',
                'contact': '@ManchesterMob',
                'commission': '12%',
                'status': 'Active',
                'sales': 18
            }
        ]
        
        for reseller in sample_resellers:
            self.add_reseller_widget(reseller)
            
    def add_reseller_widget(self, reseller):
        """Add a reseller widget to the list"""
        reseller_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='140dp',
            padding=10
        )
        
        # Background
        with reseller_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.05, 0.2, 0.1, 1)
            rect = Rectangle(size=reseller_layout.size, pos=reseller_layout.pos)
            reseller_layout.bind(size=rect.setter('size'), pos=rect.setter('pos'))
        
        # Reseller info
        info_text = f"Name: {reseller['name']}\nLocation: {reseller['location']}\nContact: {reseller['contact']}\nCommission: {reseller['commission']} | Sales: {reseller['sales']}\nStatus: {reseller['status']}"
        
        info_label = Label(
            text=info_text,
            size_hint_y=0.7,
            text_size=(None, None),
            halign='left',
            color=(1, 1, 1, 1)
        )
        reseller_layout.add_widget(info_label)
        
        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        contact_btn = Button(
            text='📱 Contact',
            size_hint_x=0.25,
            background_color=(0, 0.83, 1, 1)
        )
        button_layout.add_widget(contact_btn)
        
        edit_btn = Button(
            text='✏️ Edit',
            size_hint_x=0.25,
            background_color=(0.16, 0.66, 0.27, 1)
        )
        button_layout.add_widget(edit_btn)
        
        pay_btn = Button(
            text='💰 Pay',
            size_hint_x=0.25,
            background_color=(1, 0.65, 0, 1)
        )
        button_layout.add_widget(pay_btn)
        
        disable_btn = Button(
            text='⏸️ Disable',
            size_hint_x=0.25,
            background_color=(0.86, 0.2, 0.27, 1)
        )
        button_layout.add_widget(disable_btn)
        
        reseller_layout.add_widget(button_layout)
        self.reseller_layout.add_widget(reseller_layout)
        
    def show_add_reseller(self, instance):
        """Show add reseller dialog"""
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Form fields
        name_input = TextInput(hint_text='Reseller Name', size_hint_y=None, height='40dp')
        location_input = TextInput(hint_text='Location (UK only)', size_hint_y=None, height='40dp')
        contact_input = TextInput(hint_text='Telegram Contact', size_hint_y=None, height='40dp')
        commission_input = TextInput(hint_text='Commission %', size_hint_y=None, height='40dp')
        
        popup_layout.add_widget(name_input)
        popup_layout.add_widget(location_input)
        popup_layout.add_widget(contact_input)
        popup_layout.add_widget(commission_input)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal')
        
        cancel_btn = Button(text='Cancel', background_color=(0.5, 0.5, 0.5, 1))
        create_btn = Button(text='Add Reseller', background_color=(0.16, 0.66, 0.27, 1))
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(create_btn)
        
        popup_layout.add_widget(button_layout)
        
        popup = Popup(
            title='Add New Reseller',
            content=popup_layout,
            size_hint=(0.9, 0.8)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        create_btn.bind(on_press=lambda x: self.create_reseller(popup, name_input.text, location_input.text, contact_input.text, commission_input.text))
        
        popup.open()
        
    def create_reseller(self, popup, name, location, contact, commission):
        """Create new reseller"""
        if not all([name, location, contact, commission]):
            return
            
        new_reseller = {
            'name': name,
            'location': location,
            'contact': contact,
            'commission': commission + '%',
            'status': 'Active',
            'sales': 0
        }
        
        self.add_reseller_widget(new_reseller)
        popup.dismiss()

class DeviceTrackingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        back_btn = Button(
            text='← Back',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='📱 Device Tracking',
            size_hint=(0.6, 1),
            font_size='18sp',
            color=(1, 0.42, 0.21, 1)
        )
        header_layout.add_widget(title)
        
        refresh_btn = Button(
            text='🔄 Refresh',
            size_hint=(0.2, 1),
            background_color=(1, 0.42, 0.21, 1)
        )
        refresh_btn.bind(on_press=self.refresh_devices)
        header_layout.add_widget(refresh_btn)
        
        main_layout.add_widget(header_layout)
        
        # Device statistics
        stats_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        
        total_label = Label(text='Total Devices\n45', halign='center', color=(0, 1, 0, 1))
        active_label = Label(text='Active\n42', halign='center', color=(0, 1, 0, 1))
        offline_label = Label(text='Offline\n3', halign='center', color=(1, 0, 0, 1))
        
        stats_layout.add_widget(total_label)
        stats_layout.add_widget(active_label)
        stats_layout.add_widget(offline_label)
        
        main_layout.add_widget(stats_layout)
        
        # Device list
        scroll = ScrollView()
        self.device_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.device_layout.bind(minimum_height=self.device_layout.setter('height'))
        scroll.add_widget(self.device_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
    def refresh_devices(self, instance):
        """Refresh device list"""
        self.device_layout.clear_widgets()
        
        # Sample device data
        sample_devices = [
            {
                'serial': 'PX6A001234',
                'model': 'Pixel 6a',
                'owner': 'John Smith',
                'status': 'Online',
                'last_seen': '2024-01-15 14:30',
                'location': 'London, UK'
            },
            {
                'serial': 'PX7P005678',
                'model': 'Pixel 7 Pro',
                'owner': 'Sarah Johnson',
                'status': 'Online',
                'last_seen': '2024-01-15 14:25',
                'location': 'Manchester, UK'
            },
            {
                'serial': 'PX8001999',
                'model': 'Pixel 8',
                'owner': 'Mike Wilson',
                'status': 'Offline',
                'last_seen': '2024-01-14 10:15',
                'location': 'Birmingham, UK'
            }
        ]
        
        for device in sample_devices:
            self.add_device_widget(device)
            
    def add_device_widget(self, device):
        """Add a device widget to the list"""
        device_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='120dp',
            padding=10
        )
        
        # Background color based on status
        bg_color = (0.05, 0.2, 0.05, 1) if device['status'] == 'Online' else (0.2, 0.05, 0.05, 1)
        
        with device_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*bg_color)
            rect = Rectangle(size=device_layout.size, pos=device_layout.pos)
            device_layout.bind(size=rect.setter('size'), pos=rect.setter('pos'))
        
        # Device info
        info_text = f"Serial: {device['serial']} | Model: {device['model']}\nOwner: {device['owner']} | Location: {device['location']}\nStatus: {device['status']} | Last Seen: {device['last_seen']}"
        
        info_label = Label(
            text=info_text,
            size_hint_y=0.7,
            text_size=(None, None),
            halign='left',
            color=(1, 1, 1, 1)
        )
        device_layout.add_widget(info_label)
        
        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        ping_btn = Button(
            text='📡 Ping',
            size_hint_x=0.25,
            background_color=(0, 0.83, 1, 1)
        )
        button_layout.add_widget(ping_btn)
        
        locate_btn = Button(
            text='📍 Locate',
            size_hint_x=0.25,
            background_color=(1, 0.65, 0, 1)
        )
        button_layout.add_widget(locate_btn)
        
        wipe_btn = Button(
            text='🧹 Wipe',
            size_hint_x=0.25,
            background_color=(0.86, 0.2, 0.27, 1)
        )
        button_layout.add_widget(wipe_btn)
        
        details_btn = Button(
            text='📋 Details',
            size_hint_x=0.25,
            background_color=(0.61, 0.15, 0.69, 1)
        )
        button_layout.add_widget(details_btn)
        
        device_layout.add_widget(button_layout)
        self.device_layout.add_widget(device_layout)

class RemoteWipeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        back_btn = Button(
            text='← Back',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='🧹 Remote Wipe Control',
            size_hint=(0.8, 1),
            font_size='18sp',
            color=(0.86, 0.2, 0.27, 1)
        )
        header_layout.add_widget(title)
        
        main_layout.add_widget(header_layout)
        
        # Warning
        warning = Label(
            text='⚠️ WARNING: Remote wipe operations are IRREVERSIBLE\nOnly use in authorized situations',
            size_hint=(1, 0.1),
            color=(1, 0.65, 0, 1),
            halign='center'
        )
        main_layout.add_widget(warning)
        
        # Device selection
        device_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        device_layout.add_widget(Label(text='Select Device:', color=(1, 1, 1, 1), size_hint_y=0.3))
        
        self.device_input = TextInput(
            hint_text='Enter device serial number',
            size_hint_y=0.7,
            multiline=False
        )
        device_layout.add_widget(self.device_input)
        
        main_layout.add_widget(device_layout)
        
        # Wipe options
        options_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        options_layout.add_widget(Label(text='Wipe Options:', color=(1, 1, 1, 1), size_hint_y=0.2))
        
        wipe_buttons = BoxLayout(orientation='horizontal', size_hint_y=0.8)
        
        factory_btn = Button(
            text='🔥 Factory Reset\n(Full Wipe)',
            background_color=(0.86, 0.2, 0.27, 1)
        )
        factory_btn.bind(on_press=lambda x: self.initiate_wipe('factory_reset'))
        wipe_buttons.add_widget(factory_btn)
        
        data_btn = Button(
            text='📁 Data Only\n(Keep System)',
            background_color=(1, 0.42, 0.21, 1)
        )
        data_btn.bind(on_press=lambda x: self.initiate_wipe('data_only'))
        wipe_buttons.add_widget(data_btn)
        
        options_layout.add_widget(wipe_buttons)
        main_layout.add_widget(options_layout)
        
        # Status
        self.status_label = Label(
            text='Status: Ready',
            size_hint=(1, 0.1),
            color=(0, 1, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # Log area
        scroll = ScrollView(size_hint=(1, 0.2))
        self.log_label = Label(
            text='Remote Wipe Log:\n- System ready\n- Waiting for commands...',
            text_size=(None, None),
            halign='left',
            valign='top',
            color=(0.7, 0.7, 0.7, 1)
        )
        scroll.add_widget(self.log_label)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
    def initiate_wipe(self, wipe_type):
        """Initiate remote wipe"""
        device_serial = self.device_input.text.strip()
        
        if not device_serial:
            self.show_popup('Error', 'Please enter a device serial number')
            return
            
        # Confirmation popup
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        warning_label = Label(
            text=f'⚠️ FINAL WARNING ⚠️\n\nThis will PERMANENTLY {wipe_type.replace("_", " ").upper()} device:\n{device_serial}\n\nThis action CANNOT be undone!',
            color=(1, 0, 0, 1),
            halign='center'
        )
        popup_layout.add_widget(warning_label)
        
        # Confirmation buttons
        button_layout = BoxLayout(orientation='horizontal')
        
        cancel_btn = Button(
            text='❌ CANCEL',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        
        confirm_btn = Button(
            text='💥 CONFIRM WIPE',
            background_color=(0.86, 0.2, 0.27, 1)
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(confirm_btn)
        
        popup_layout.add_widget(button_layout)
        
        popup = Popup(
            title='CONFIRM REMOTE WIPE',
            content=popup_layout,
            size_hint=(0.9, 0.6)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.execute_wipe(popup, device_serial, wipe_type))
        
        popup.open()
        
    def execute_wipe(self, popup, device_serial, wipe_type):
        """Execute the remote wipe"""
        popup.dismiss()
        
        self.status_label.text = f'Status: Executing {wipe_type} on {device_serial}...'
        self.status_label.color = (1, 0.65, 0, 1)
        
        # Log the action
        log_entry = f'- {datetime.now().strftime("%H:%M:%S")}: Initiating {wipe_type} on {device_serial}\n'
        self.log_label.text += log_entry
        
        # Simulate wipe process
        Clock.schedule_once(lambda dt: self.wipe_complete(device_serial, wipe_type), 3)
        
    def wipe_complete(self, device_serial, wipe_type):
        """Handle wipe completion"""
        self.status_label.text = f'Status: {wipe_type.replace("_", " ").title()} completed on {device_serial}'
        self.status_label.color = (0, 1, 0, 1)
        
        log_entry = f'- {datetime.now().strftime("%H:%M:%S")}: {wipe_type.replace("_", " ").title()} completed successfully\n'
        self.log_label.text += log_entry
        
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class AnalyticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        back_btn = Button(
            text='← Back',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='📊 Analytics & Reports',
            size_hint=(0.8, 1),
            font_size='18sp',
            color=(0.61, 0.15, 0.69, 1)
        )
        header_layout.add_widget(title)
        
        main_layout.add_widget(header_layout)
        
        # Statistics grid
        stats_grid = GridLayout(cols=2, spacing=10, size_hint=(1, 0.4))
        
        # Revenue stats
        revenue_layout = BoxLayout(orientation='vertical')
        revenue_layout.add_widget(Label(text='💰 Total Revenue', color=(0, 1, 0, 1), font_size='16sp'))
        revenue_layout.add_widget(Label(text='£15,750', color=(0, 1, 0, 1), font_size='24sp'))
        revenue_layout.add_widget(Label(text='This Month: £3,200', color=(0.7, 0.7, 0.7, 1)))
        stats_grid.add_widget(revenue_layout)
        
        # Subscription stats
        sub_layout = BoxLayout(orientation='vertical')
        sub_layout.add_widget(Label(text='📱 Active Subscriptions', color=(0, 0.83, 1, 1), font_size='16sp'))
        sub_layout.add_widget(Label(text='127', color=(0, 0.83, 1, 1), font_size='24sp'))
        sub_layout.add_widget(Label(text='New this month: 23', color=(0.7, 0.7, 0.7, 1)))
        stats_grid.add_widget(sub_layout)
        
        # Device stats
        device_layout = BoxLayout(orientation='vertical')
        device_layout.add_widget(Label(text='📱 Devices Flashed', color=(1, 0.42, 0.21, 1), font_size='16sp'))
        device_layout.add_widget(Label(text='89', color=(1, 0.42, 0.21, 1), font_size='24sp'))
        device_layout.add_widget(Label(text='This month: 15', color=(0.7, 0.7, 0.7, 1)))
        stats_grid.add_widget(device_layout)
        
        # Reseller stats
        reseller_layout = BoxLayout(orientation='vertical')
        reseller_layout.add_widget(Label(text='🏪 Active Resellers', color=(0.16, 0.66, 0.27, 1), font_size='16sp'))
        reseller_layout.add_widget(Label(text='12', color=(0.16, 0.66, 0.27, 1), font_size='24sp'))
        reseller_layout.add_widget(Label(text='Commissions owed: £1,250', color=(0.7, 0.7, 0.7, 1)))
        stats_grid.add_widget(reseller_layout)
        
        main_layout.add_widget(stats_grid)
        
        # Recent activity
        activity_label = Label(
            text='Recent Activity:',
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        main_layout.add_widget(activity_label)
        
        # Activity list
        scroll = ScrollView()
        activity_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        activity_layout.bind(minimum_height=activity_layout.setter('height'))
        
        activities = [
            "15:30 - New subscription: 6-month plan (£200) - London Tech Solutions",
            "14:45 - Device flashed: Pixel 8 Pro - PX8P002341",
            "13:20 - Commission paid: Manchester Mobile - £180",
            "12:15 - Remote wipe executed: PX6A001789 (Factory Reset)",
            "11:30 - New reseller added: Birmingham Secure Tech",
            "10:45 - Subscription renewed: 12-month plan (BTC) - Sarah J.",
            "09:20 - Device tracking updated: 45 devices online",
            "08:15 - System backup completed successfully"
        ]
        
        for activity in activities:
            activity_label = Label(
                text=f"• {activity}",
                size_hint_y=None,
                height='30dp',
                text_size=(None, None),
                halign='left',
                color=(0.8, 0.8, 0.8, 1)
            )
            activity_layout.add_widget(activity_label)
        
        scroll.add_widget(activity_layout)
        main_layout.add_widget(scroll)
        
        # Export button
        export_btn = Button(
            text='📄 Export Monthly Report',
            size_hint=(1, 0.1),
            background_color=(0.61, 0.15, 0.69, 1)
        )
        export_btn.bind(on_press=self.export_report)
        main_layout.add_widget(export_btn)
        
        self.add_widget(main_layout)
        
    def export_report(self, instance):
        """Export monthly report"""
        popup = Popup(
            title='Report Exported',
            content=Label(text='Monthly report has been exported\nand sent to your email.'),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        back_btn = Button(
            text='← Back',
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='⚙️ Settings',
            size_hint=(0.8, 1),
            font_size='18sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        header_layout.add_widget(title)
        
        main_layout.add_widget(header_layout)
        
        # Settings options
        settings_layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 0.7))
        
        # API Settings
        api_btn = Button(
            text='🔗 API Configuration',
            size_hint=(1, None),
            height='50dp',
            background_color=(0, 0.83, 1, 1)
        )
        settings_layout.add_widget(api_btn)
        
        # Notification Settings
        notif_btn = Button(
            text='🔔 Notification Settings',
            size_hint=(1, None),
            height='50dp',
            background_color=(0.16, 0.66, 0.27, 1)
        )
        settings_layout.add_widget(notif_btn)
        
        # Security Settings
        security_btn = Button(
            text='🔒 Security Settings',
            size_hint=(1, None),
            height='50dp',
            background_color=(1, 0.42, 0.21, 1)
        )
        settings_layout.add_widget(security_btn)
        
        # About
        about_btn = Button(
            text='ℹ️ About',
            size_hint=(1, None),
            height='50dp',
            background_color=(0.61, 0.15, 0.69, 1)
        )
        about_btn.bind(on_press=self.show_about)
        settings_layout.add_widget(about_btn)
        
        main_layout.add_widget(settings_layout)
        
        # User info
        if hasattr(self.manager, 'current_user'):
            user_info = f"Logged in as: {self.manager.current_user.get('username', 'Unknown')}\nRole: {self.manager.current_user.get('role', 'Unknown')}"
        else:
            user_info = "No user logged in"
            
        user_label = Label(
            text=user_info,
            size_hint=(1, 0.1),
            color=(0.7, 0.7, 0.7, 1)
        )
        main_layout.add_widget(user_label)
        
        # Logout button
        logout_btn = Button(
            text='🚪 Logout',
            size_hint=(1, 0.1),
            background_color=(0.86, 0.2, 0.27, 1)
        )
        logout_btn.bind(on_press=self.logout)
        main_layout.add_widget(logout_btn)
        
        self.add_widget(main_layout)
        
    def show_about(self, instance):
        """Show about dialog"""
        about_text = """Platinum Secure Flasher
Android Management App v1.0

🇬🇧 UK Operations Only

Features:
• Subscription Management
• Reseller Management  
• Device Tracking
• Remote Wipe Control
• Analytics & Reports

© 2024 Platinum Secure
All rights reserved."""
        
        popup = Popup(
            title='About Platinum Secure',
            content=Label(text=about_text, halign='center'),
            size_hint=(0.8, 0.7)
        )
        popup.open()
        
    def logout(self, instance):
        """Logout user"""
        if hasattr(self.manager, 'current_user'):
            delattr(self.manager, 'current_user')
        self.manager.current = 'login'

class PlatinumSecureApp(App):
    def build(self):
        # Screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SubscriptionScreen(name='subscriptions'))
        sm.add_widget(ResellerScreen(name='resellers'))
        sm.add_widget(DeviceTrackingScreen(name='devices'))
        sm.add_widget(RemoteWipeScreen(name='wipe'))
        sm.add_widget(AnalyticsScreen(name='analytics'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        # Set initial screen
        sm.current = 'login'
        
        return sm

if __name__ == '__main__':
    PlatinumSecureApp().run()