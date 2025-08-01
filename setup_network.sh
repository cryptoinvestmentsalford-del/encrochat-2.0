#!/bin/bash
# setup_network.sh – Full network bootstrap for Platinum Secure
# Run via Termux or ADB (after device flash)

LOGFILE="/sdcard/logs/first_boot.txt"
mkdir -p "$(dirname "$LOGFILE")"
echo ">>> Starting setup: $(date)" > "$LOGFILE"

## --- STEP 1: Provision eSIM ---
echo "[*] Step 1: Provision eSIM" | tee -a "$LOGFILE"
read -p "Paste eSIM QR (e.g. LPA:...): " QR
adb shell am start -a android.intent.action.VIEW -d "$QR"
echo "[✔] eSIM triggered." | tee -a "$LOGFILE"

## --- STEP 2: Set APN ---
echo "[*] Step 2: Set APN" | tee -a "$LOGFILE"
APN_FILE="apn_profiles/silentlink.json"
APN=$(jq -r .apn < "$APN_FILE")
adb shell settings put global preferred_apn_name "$APN"
adb shell svc data disable && sleep 1 && adb shell svc data enable
echo "[✔] APN applied: $APN" | tee -a "$LOGFILE"

## --- STEP 3: Enable VPN (WireGuard only) ---
echo "[*] Step 3: Enable VPN" | tee -a "$LOGFILE"
WG_CONF="vpn_profiles/wg0.conf"
adb shell am start -n com.wireguard.android/com.wireguard.android.activity.MainActivity
sleep 2
adb shell am broadcast -a com.wireguard.android.action.IMPORT_TUNNEL -e config "$(cat $WG_CONF)"
echo "[✔] VPN config pushed." | tee -a "$LOGFILE"

## --- STEP 4: Sync Time ---
echo "[*] Step 4: Syncing time…" | tee -a "$LOGFILE"
adb shell settings put global auto_time 1
adb shell settings put global auto_time_zone 1
echo "[✔] Time sync enabled." | tee -a "$LOGFILE"

echo ">>> Setup complete." | tee -a "$LOGFILE"
