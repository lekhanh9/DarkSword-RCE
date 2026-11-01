#!/usr/bin/env python3
"""
DarkSword Exploit Chain Deep Dissector
Phân tích toàn diện kiến trúc 4 tầng của DarkSword-RCE:
1. Stage 0: Delivery Vector & Frame Initialization
2. Stage 1: WebKit RCE & Worker Thread Management (OffscreenCanvas / ImageBitmap)
3. Stage 2: WebKit-to-GPU IPC Sandbox Escape (RemoteGraphicsContextGL / RemoteDisplayListRecorder)
4. Stage 3: Post-Exploitation & Privilege Escalation (Keychain dumping, native symbol resolution)
"""

import os
import re
import json

REPO_DIR = "/home/kle475569/hello/DarkSword-RCE"

def dissect_darksword():
    print("=" * 70)
    print("     DARKSWORD FULL-CHAIN REVERSE ENGINEERING & ARCHITECTURE REPORT")
    print("=" * 70)

    # 1. Inspect Files & Sizes
    files = os.listdir(REPO_DIR)
    print(f"\n[*] Đã nạp repository: {len(files)} tệp tin.")
    for f in sorted(files):
        if not f.startswith("."):
            sz = os.path.getsize(os.path.join(REPO_DIR, f))
            print(f"    - {f:<25} ({sz:>8,} bytes)")

    # 2. Stage 1 Analysis: rce_loader.js
    rce_loader_path = os.path.join(REPO_DIR, "rce_loader.js")
    with open(rce_loader_path, "r", errors="ignore") as f:
        rce_loader = f.read()

    print("\n--- [STAGE 1] WebKit RCE & Worker Orchestration (rce_loader.js) ---")
    targets = re.findall(r"ios_version\s*==\s*'([^']+)'", rce_loader)
    print(f"  * Phiên bản iOS được nhắm tới: {', '.join(targets)}")
    has_offscreen = "OffscreenCanvas" in rce_loader
    has_bitmap = "createImageBitmap" in rce_loader
    print(f"  * Thành phần kích hoạt: OffscreenCanvas={has_offscreen}, ImageBitmap={has_bitmap}")
    print("  * Kỹ thuật: Spawns dlopen workers và chuẩn bị SharedArrayBuffer/MessagePort.")

    # 3. Stage 2 Analysis: sbx0_main_18.4.js (GPU Process Sandbox Escape)
    sbx_path = os.path.join(REPO_DIR, "sbx0_main_18.4.js")
    with open(sbx_path, "r", errors="ignore") as f:
        sbx_data = f.read()

    print("\n--- [STAGE 2] GPU Process Sandbox Escape (sbx0_main_18.4.js) ---")
    gpu_selectors = re.findall(r"(RemoteGraphicsContextGL_\w+|RemoteDisplayListRecorder_\w+|GPUConnectionToWebProcess_\w+):\s*(0x[0-9a-fA-F]+|\d+)", sbx_data)
    print(f"  * Trích xuất {len(gpu_selectors)} IPC message selectors tới com.apple.WebKit.GPU:")
    for sel, code in gpu_selectors[:12]:
        print(f"    - {sel:<45} = {code}")

    # 4. Stage 3 Analysis: pe_main.js (Privilege Escalation & Exfiltration)
    pe_path = os.path.join(REPO_DIR, "pe_main.js")
    with open(pe_path, "r", errors="ignore") as f:
        pe_data = f.read()

    print("\n--- [STAGE 3] Native Infiltration & Post-Exploitation (pe_main.js) ---")
    native_funcs = set(re.findall(r'func_resolve\("([^"]+)"\)', pe_data))
    print(f"  * Phân giải hàm hệ thống native qua dlsym ({len(native_funcs)} hàm):")
    for nf in sorted(list(native_funcs))[:14]:
        print(f"    - {nf}")

    # Exfiltration targets
    exfil_wifi = "extractWiFiPasswords" in pe_data
    exfil_keychain = "kSecClass" in pe_data
    print(f"  * Mục tiêu khai thác dữ liệu:")
    print(f"    - Chiết xuất Keychain: {exfil_keychain}")
    print(f"    - Trích xuất mật khẩu Wi-Fi: {exfil_wifi}")
    print(f"    - Các đường dẫn đích: /var/wireless/, /var/root/, /var/mobile/Library/Preferences/")

    print("\n" + "=" * 70)
    print("               KẾT LUẬN KIỂM SOÁT PHÒNG THỦ")
    print("=" * 70)
    print("  1. DarkSword hoàn toàn khác biệt với Coruna (Coruna dùng DiskImages & IOKit).")
    print("  2. DarkSword nhắm vào WebKit GPU Process IPC (iOS 18.4 - 18.6.2).")
    print("  3. Toàn bộ các selector GPU và memory layout này KHÔNG tương thích với iOS 16.7.16.")

if __name__ == "__main__":
    dissect_darksword()
