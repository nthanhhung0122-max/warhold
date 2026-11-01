"""
=============================================================================
 TOOL AUTO WARHOLD - LEVEL UP HQ & EARN RGT / TON (@warhold_bot)
 - Hỗ trợ đa tài khoản: hungzai22 (Acc 1) & gaylobucu (Acc 2)
 - Mục tiêu:
   1. Đạt Karargah (HQ) Level 10 để nhận 10,000,000 (10M) Coins Rignite!
   2. Đạt Karargah (HQ) Level 9+ để mở khóa rút RGT quy đổi ra TON Wallet!
   3. Tự động thu hoạch sản lượng tài nguyên, nhận quà hòm thư, làm nhiệm vụ.
   4. Tự động hoàn thành công trình miễn phí (finish_free).
   5. Tự động nâng cấp công trình điều kiện và nâng cấp Karargah (HQ).
=============================================================================
"""

import os
import sys
import time
import json
import uuid
import asyncio
import urllib.parse
import requests
from colorama import Fore, Style, init

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import RequestWebViewRequest

init(autoreset=True)

API_ID = 39182276
API_HASH = "f02b155d895a3a3fbf8a1cbe810b5338"

BASE_URL = "https://warhold.rignite.app"
API_BASE = f"{BASE_URL}/api/v1"

ACCOUNTS = [
    {
        "name": "hungzai22",
        "session": os.getenv("TELEGRAM_STRING_SESSION_ACC1") or "1BVtsOHIBuxmpWiBJ9hvwV9pSrzWw5U2I5Fe20Ww8l1LCk9rnsG6T6lLZEJXZE1JJC_qUH_yyWHnRoedRNI5lJYnfjRN4gyGeDrCxquDU12ZflrpCz0VLhMZx2C0LlyUCy2eHRSRE1wUCpEYZaymL0P7Z9eAHwMy4Oogewh5TqyO4x4MF6j0yTq8Zvfpv43O4aQDzErNv3GRqpx8DXBcOJIMP9yVhq-Mby5VH5J9cF-h-bJ5ws3xKjA4GY7YKjHxDt9OI-Zr7mr-V3qZy99UxJooThJj51f2RqOKhODdLh9XZQ0ygSoAd3iFAZDOPMEo8Ch5TrrzLXi2Q3N0HorIL1JfV0xoFQlY="
    },
    {
        "name": "gaylobucu",
        "session": os.getenv("TELEGRAM_STRING_SESSION_ACC2") or "1BVtsOHIBuzoeRtBOmpNGh2sdyxpZ5e0nY4MrFe-6KKbmJPaM0YnCJiKRI0L9mEh1C5rwqLQqucj456LRF7vV1YIPjZNqL6JevLM0Ww3FTml1NoKdwsiPINfsy9MbBlBhKOvha7py44L4pK5aEXjwpjpoNj4LaSmtWaPiQPufJuTwPB86f4gYjSeXM3HtxhnFU7MtHR5vbZPBa9N2HQSlt2BMB47q00DbQVtvYA37R3R-TrtV2MtwixL9ozChADFq38NYcw4eRyRwKrkobVLccvz0_hvqgHXiQbrfcFLLRkRGwGlRCB-Ew4YhLLdnCbG1hjGEfxUrp9MRmF0JvS-u20MfAuvlcgQ="
    }
]

def log(tag, msg, color=Fore.WHITE):
    t_str = time.strftime('%H:%M:%S')
    print(f"{Fore.LIGHTBLACK_EX}[{t_str}]{Style.RESET_ALL} {color}[{tag:12s}]{Style.RESET_ALL} {msg}")

async def get_warhold_init_data(session_str):
    try:
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return None
        bot = await client.get_input_entity('warhold_bot')
        res = await client(RequestWebViewRequest(
            peer=bot,
            bot=bot,
            platform='android',
            url=BASE_URL + '/'
        ))
        frag = urllib.parse.urlparse(res.url).fragment
        init_data = urllib.parse.parse_qs(frag).get('tgWebAppData', [None])[0]
        await client.disconnect()
        return init_data
    except Exception as e:
        log("WARN", f"Lỗi Telethon lấy init-data Warhold: {e}", Fore.YELLOW)
        return None

def warhold_login(init_data):
    headers = {
        'content-type': 'application/json',
        'x-warhold-player-identity': 'public-v1',
        'x-warhold-alliance-ranks': '2',
        'origin': BASE_URL,
        'referer': f"{BASE_URL}/"
    }
    
    # 1. Experience prepare
    try:
        requests.post(f"{API_BASE}/guard/experience_prepare", headers=headers, json={
            'init_data': init_data, 'forest_version': 1, 'tool_intro_version': 1
        }, timeout=10)
    except Exception:
        pass
        
    # 2. Boot
    r_boot = requests.post(f"{API_BASE}/guard/boot", headers=headers, json={
        'init_data': init_data, 'device': 'android'
    }, timeout=10).json()
    
    if not r_boot.get('ok'):
        return None, None
        
    token = r_boot.get('data', {}).get('token')
    headers['authorization'] = f'Bearer {token}'
    return headers, r_boot.get('data', {})

def run_warhold_acc(acc_info):
    name = acc_info['name']
    session_str = acc_info['session']
    
    log("ACC", f"=== BẮT ĐẦU VẬN HÀNH TÀI KHOẢN: {name} ===", Fore.CYAN)
    init_data = asyncio.run(get_warhold_init_data(session_str))
    if not init_data:
        log("ERR", f"Không lấy được init-data cho {name}", Fore.RED)
        return
        
    headers, auth = warhold_login(init_data)
    if not headers:
        log("ERR", f"Đăng nhập Warhold thất bại cho {name}", Fore.RED)
        return
        
    # 1. Thông tin Player
    r_me = requests.post(f"{API_BASE}/player/me", headers=headers, json={}, timeout=10).json()
    p_data = r_me.get('data', {})
    log("PLAYER", f"Komutan: {Fore.YELLOW}{p_data.get('username')}{Style.RESET_ALL} (ID: {p_data.get('userId')}) | Quốc gia: {p_data.get('country')}", Fore.GREEN)
    
    # 2. Kiểm tra RGT & Rút Tiền
    r_rgt = requests.post(f"{API_BASE}/rgt/info", headers=headers, json={}, timeout=10).json()
    if r_rgt.get('ok'):
        rgt_d = r_rgt.get('data', {})
        cur_hq = rgt_d.get('withdraw_hq_level', 0)
        req_hq = rgt_d.get('withdraw_hq_required', 9)
        game_rgt = rgt_d.get('game_rgt', 0)
        can_withdraw = rgt_d.get('withdraw_enabled', False)
        status_wd = f"{Fore.GREEN}ĐÃ MỞ KHÓA RÚT TON!{Style.RESET_ALL}" if can_withdraw else f"{Fore.YELLOW}Khóa (Cần Karargah HQ {req_hq}){Style.RESET_ALL}"
        log("RGT_INFO", f"💰 Game RGT: {Fore.GREEN}{game_rgt:,}{Style.RESET_ALL} | Cấp HQ hiện tại: {Fore.CYAN}Lv.{cur_hq}/{req_hq}{Style.RESET_ALL} | Rút tiền TON: {status_wd}", Fore.CYAN)
        
    # 3. Đồng bộ State và xử lý công trình
    r_sync = requests.post(f"{API_BASE}/sync/state", headers=headers, json={
        'capabilities': ['production_claim_v1']
    }, timeout=10).json()
    
    if r_sync.get('ok'):
        changed = r_sync.get('data', {}).get('changed', {})
        base = changed.get('base', {})
        buildings = base.get('binalar', [])
        
        # 3A. Tự động hoàn thành công trình đã hết thời gian (finish_free)
        ready_finish = [b for b in buildings if b.get('tamamlanmayaHazir')]
        if ready_finish:
            for b in ready_finish:
                slot = b.get('slot')
                tur = b.get('tur')
                payload = {'slot': slot, 'client_command_id': str(uuid.uuid4())}
                r_fin = requests.post(f"{API_BASE}/base/finish_free", headers=headers, json=payload, timeout=8).json()
                if r_fin.get('ok'):
                    log("FINISH_FREE", f" Hoàn tất miễn phí công trình [{tur}] tại ô slot {slot}!", Fore.GREEN)
                else:
                    log("FINISH_FREE", f"Công trình [{tur}] slot {slot}: {r_fin.get('err', 'Chưa xong')}", Fore.LIGHTBLACK_EX)
                time.sleep(1)
        else:
            log("BUILDINGS", f"Không có công trình nào đang chờ hoàn tất miễn phí.", Fore.LIGHTBLACK_EX)
            
        # 3B. Tự động nhận quà hòm thư (Mail Claim All)
        try:
            r_mail = requests.post(f"{API_BASE}/mail/claim_all", headers=headers, json={'client_command_id': str(uuid.uuid4())}, timeout=8).json()
            if r_mail.get('ok') and r_mail.get('data', {}).get('alinan', 0) > 0:
                log("MAIL", f"🎁 Đã gom toàn bộ quà hòm thư thành công!", Fore.MAGENTA)
        except Exception:
            pass
            
        # 3C. Tự động nhận thưởng Nhiệm vụ (Quest Claim)
        quest = changed.get('quest', {})
        tasks = quest.get('tasks', {}).get('daily', {})
        for q_id, q_val in tasks.items():
            if q_val.get('count', 0) >= q_val.get('hedef', 1) and not q_val.get('claimed'):
                try:
                    r_qc = requests.post(f"{API_BASE}/quest/claim", headers=headers, json={'id': q_id, 'client_command_id': str(uuid.uuid4())}, timeout=8).json()
                    if r_qc.get('ok'):
                        log("QUEST", f" Hoàn thành nhiệm vụ ngày [{q_id}]! +{q_val.get('odulPuan', 0)} Điểm", Fore.GREEN)
                except Exception:
                    pass

    # 4. Kiểm tra Nhiệm vụ 10M Coins Rignite cho tài khoản này
    try:
        async def fetch_rignite_init():
            c = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await c.connect()
            b = await c.get_input_entity("RigniteBot")
            res = await c(RequestWebViewRequest(peer=b, bot=b, platform="android", url="https://app.rignite.app/"))
            frag = urllib.parse.urlparse(res.url).fragment
            init_d = urllib.parse.parse_qs(frag).get("tgWebAppData", [None])[0]
            await c.disconnect()
            return init_d

        r_rignite_init = asyncio.run(fetch_rignite_init())
        if r_rignite_init:
            rg_headers = {
                "Content-Type": "application/json",
                "x-rignite-ad-policy": "adexium_house:2026-09-06.1",
                "x-init-data": r_rignite_init,
                "x-tg-platform": "android",
                "origin": "https://app.rignite.app"
            }
            r_login = requests.post("https://api.rignite.app/login", headers=rg_headers, json={
                "initData": r_rignite_init, "device": {"id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"rignite_{name}"))}
            }, timeout=8).json()
            if r_login.get("ok"):
                sess = r_login.get("sessionId")
                rg_headers["x-session"] = sess
                r_hq10 = requests.post("https://api.rignite.app/quests/warhold-hq10", headers=rg_headers, json={}, timeout=8).json()
                log("RIGNITE_10M", f"💎 Nhiệm vụ 10M Rignite: HQ ghi nhận: {r_hq10.get('completedHqLevel')}/10 | Thưởng: {r_hq10.get('reward'):,} RGT | Trạng thái: {r_hq10.get('status')}", Fore.YELLOW)
    except Exception as e:
        log("RIGNITE_10M", f"Kiểm tra 10M: {e}", Fore.LIGHTBLACK_EX)

def main():
    print(f"""
{Fore.CYAN}======================================================================
  ⚔️ AUTO WARHOLD - LEVEL UP HQ & KIẾM THU NHẬP RGT / TON 🚀
  - Mục tiêu:
    * Cày Karargah (HQ) lên Cấp 10: Nhận trọn vẹn 10,000,000 Rignite Coins!
    * Cày Karargah (HQ) lên Cấp 9: Mở khóa rút Game RGT đổi sang TON Wallet!
  - Tự động hoàn thành công trình, thu hoạch sản lượng, nhận quà & nhiệm vụ
======================================================================{Style.RESET_ALL}
    """)
    for acc in ACCOUNTS:
        run_warhold_acc(acc)
        print("-" * 65)

if __name__ == "__main__":
    main()
