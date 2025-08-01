#!/bin/bash

echo "[🛡️] Starting PlatinumOS MDM Lockdown..."

# --- BASIC HARDENING ---
adb shell settings put global adb_enabled 0
adb shell settings put secure development_settings_enabled 0
adb shell settings put global usb_mass_storage_enabled 0
adb shell settings put global oem_unlock_allowed 0
adb shell settings put global auto_time_zone 0

# --- LOCATION + TELEMETRY BLOCKING ---
adb shell settings put secure location_mode 0
adb shell settings put global wifi_scan_always_enabled 0
adb shell settings put global ble_scan_always_enabled 0
adb shell settings put global assisted_gps_enabled 0

# --- UI & RESET PROTECTION ---
adb shell pm disable-user --user 0 com.android.settings/.Settings\$FactoryResetActivity
adb shell settings put global add_users_when_locked 0
adb shell settings put secure multi_user_enabled 0
adb shell settings put global user_switcher_enabled 0

# --- INSTALL/SECURITY ENFORCEMENT ---
adb shell settings put secure install_non_market_apps 1
adb shell settings put secure allow_parent_profile_app_linking 0
adb shell settings put global package_verifier_enable 1
adb shell settings put global package_verifier_user_consent 1

# --- SCREEN SECURITY ---
adb shell settings put secure lock_screen_allow_remote_input 0
adb shell settings put secure lock_screen_show_notifications 0
adb shell settings put secure show_password 0
adb shell settings put secure screenshot_disabled 1

# --- BACKUP/DATA LEAK BLOCKS ---
adb shell settings put global backup_enabled 0
adb shell settings put global send_action_app_error 0
adb shell settings put secure automatic_storage_manager_enabled 0

# --- BLUETOOTH ---
adb shell settings put secure bluetooth_on 0
adb shell settings put secure bluetooth_discoverability 0

# --- AIRPLANE MODE ON BOOT ---
adb shell settings put global airplane_mode_on 1
adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true

# --- VPN LOCKDOWN (PREP — ACTIVE WHEN CONFIGURED) ---
adb shell settings put global always_on_vpn_app com.wireguard.android
adb shell settings put global always_on_vpn_lockdown 1

echo "[✅] MDM lockdown complete. Device is now Platinum-grade secure."
