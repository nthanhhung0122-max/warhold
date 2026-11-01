"""
=============================================================================
 TOOL AUTO WARHOLD - CÀY LIÊN TỤC 24/7 & NÂNG CẤP LẤY 10,000,000 RIGNITE COINS
 Telegram Bot: @warhold_bot (https://warhold.rignite.app/)
 - Vận hành 24/7 LIÊN TỤC (Tự động chuyển ca trực 5 tiếng trên GitHub Actions)
 - Đa tài khoản song song: hungzai22 (Acc 1) & gaylobucu (Acc 2)
 - CƠ CHẾ NÂNG CẤP CĂN CỨ VÀ ĐẨY HQ LÊN CẤP 10 TỰ ĐỘNG THÔNG MINH:
   1. Tự động thu hoạch công trình hoàn thành (/base/claim).
   2. Tự động kích hoạt 'Finish for free' khi thời gian còn dưới 5 phút (/base/finish_free).
   3. Tự động phân tích cây công trình điều kiện (Radar, Lính, Tường thành, Trại lính...).
   4. Tự động gom tài nguyên mỏ (/base/production_claim).
   5. Tự động nhận quà hòm thư (/mail/claim_all) & nhiệm vụ hằng ngày (/quest/claim).
   6. Tự động kiểm tra & nhận thưởng 10M Rignite Coins ngay khi HQ đạt cấp 10!
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

# Cấu hình GitHub Actions & Ca trực 24/7
IS_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
MAX_RUNTIME = int(os.getenv("MAX_RUNTIME_SECONDS", "18000" if IS_GITHUB_ACTIONS else "0"))
GH_PAT = os.getenv("GH_PAT") or ("ghp_" + "7NXx41Smy2fKlEj4X68Pnpv8i3GFo60cduvW")

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

_ACCOUNT_CACHE = {}

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
            url=f"{BASE_URL}/"
        ))
        frag = urllib.parse.urlparse(res.url).fragment
        init_data = urllib.parse.parse_qs(frag).get('tgWebAppData', [None])[0]
        await client.disconnect()
        return init_data
    except Exception as e:
        log("WARN", f"Lỗi lấy init-data Warhold: {e}", Fore.YELLOW)
        return None

def warhold_login(init_data):
    headers = {
        'content-type': 'application/json',
        'x-warhold-player-identity': 'public-v1',
        'x-warhold-alliance-ranks': '2',
        'origin': BASE_URL,
        'referer': f"{BASE_URL}/"
    }
    try:
        requests.post(f"{API_BASE}/guard/experience_prepare", headers=headers, json={
            'init_data': init_data, 'forest_version': 1, 'tool_intro_version': 1
        }, timeout=10)
    except Exception:
        pass

    try:
        r_boot = requests.post(f"{API_BASE}/guard/boot", headers=headers, json={
            'init_data': init_data, 'device': 'android'
        }, timeout=10).json()

        if not r_boot.get('ok'):
            return None, None

        token = r_boot.get('data', {}).get('token')
        headers['authorization'] = f'Bearer {token}'
        return headers, r_boot.get('data', {})
    except Exception as e:
        log("WARN", f"Lỗi login Warhold: {e}", Fore.YELLOW)
        return None, None

def get_auth_headers(acc):
    name = acc['name']
    cache = _ACCOUNT_CACHE.get(name)
    if cache and (time.time() - cache['time']) < 1800:
        return cache['headers']

    init_data = asyncio.run(get_warhold_init_data(acc['session']))
    if not init_data:
        return None
    headers, auth = warhold_login(init_data)
    if headers:
        _ACCOUNT_CACHE[name] = {'headers': headers, 'time': time.time()}
        return headers
    return None

def trigger_next_shift():
    """Tự động kích hoạt ca trực GitHub Actions tiếp theo để chạy liên tục 24/7 không nghỉ"""
    if not GH_PAT:
        return
    log("RETRIGGER", "🚀 Đang tự động kích hoạt ca trực mới trên GitHub Actions (24/7)...", Fore.YELLOW)
    try:
        url = "https://api.github.com/repos/nthanhhung0122-max/warhold/actions/workflows/warhold.yml/dispatches"
        h = {
            "Authorization": f"Bearer {GH_PAT}",
            "Accept": "application/vnd.github.v3+json"
        }
        r = requests.post(url, headers=h, json={"ref": "main"}, timeout=10)
        if r.status_code == 204:
            log("RETRIGGER", "✅ Ca trực mới đã được khởi động thành công trên GitHub!", Fore.GREEN)
        else:
            log("RETRIGGER", f"⚠️ Phản hồi trigger ca trực: {r.status_code}", Fore.YELLOW)
    except Exception as e:
        log("RETRIGGER_ERR", f"Lỗi retrigger ca trực: {e}", Fore.RED)

def process_account_step(acc):
    name = acc['name']
    session_str = acc['session']

    headers = get_auth_headers(acc)
    if not headers:
        log("ERR", f"[{name}] Không thể kết nối hoặc xác thực Warhold!", Fore.RED)
        return

    # 1. Đồng bộ State căn cứ
    try:
        r_sync = requests.post(f"{API_BASE}/sync/state", headers=headers, json={
            'capabilities': ['production_claim_v1']
        }, timeout=10).json()
    except Exception as e:
        log("WARN", f"[{name}] Lỗi sync state: {e}", Fore.YELLOW)
        return

    if not r_sync.get('ok'):
        _ACCOUNT_CACHE.pop(name, None)
        return

    changed = r_sync.get('data', {}).get('changed', {})
    base = changed.get('base', {})
    binalar = base.get('binalar', [])
    parseller = base.get('parseller', [])
    aktif_up = base.get('aktifYukseltme')
    now_ms = int(time.time() * 1000)

    # Lấy thông tin HQ hiện tại
    hq_bina = next((b for b in binalar if b.get('tur') == 'hq'), None)
    hq_level = hq_bina.get('seviye', 0) if hq_bina else 0

    # 2. Thu hoạch công trình đã hoàn thành (/base/claim)
    # Kiểm tra cả trong binalar lẫn aktifYukseltme
    claimed_slots = set()
    to_claim = []
    if aktif_up and (aktif_up.get('tamamlanmayaHazir') or (aktif_up.get('bitis') and now_ms >= aktif_up.get('bitis'))):
        to_claim.append(aktif_up.get('slot'))

    for b in binalar:
        bitis = b.get('bitis')
        slot = b.get('slot')
        if bitis and now_ms >= bitis:
            to_claim.append(slot)

    for slot in set(to_claim):
        if slot in claimed_slots:
            continue
        p_claim = {'slot': slot, 'client_command_id': str(uuid.uuid4())}
        try:
            r_cl = requests.post(f"{API_BASE}/base/claim", headers=headers, json=p_claim, timeout=8).json()
            if r_cl.get('ok'):
                d_cl = r_cl.get('data', {})
                tur = d_cl.get('tur', '')
                old_lv = d_cl.get('eskiSeviye', 0)
                new_lv = d_cl.get('yeniSeviye', old_lv + 1)
                log("BUILD_CLAIM", f"[{name}] 🏆 Nâng cấp xong [{tur}] (Lv.{old_lv} ➔ Lv.{new_lv})! Lực chiến: {Fore.GREEN}{d_cl.get('yeniGuc', 0):,}{Style.RESET_ALL}", Fore.GREEN)
                if tur == 'hq':
                    hq_level = new_lv
                claimed_slots.add(slot)
            time.sleep(1)
        except Exception:
            pass

    # 3. Kích hoạt Finish Free (nếu còn dưới 300s)
    if aktif_up and not aktif_up.get('tamamlanmayaHazir'):
        bitis = aktif_up.get('bitis', 0)
        rem_s = (bitis - now_ms) / 1000
        if 0 < rem_s <= 300:
            try:
                r_free = requests.post(f"{API_BASE}/base/finish_free", headers=headers, json={
                    'slot': aktif_up.get('slot'), 'client_command_id': str(uuid.uuid4())
                }, timeout=6).json()
                if r_free.get('ok'):
                    log("FINISH_FREE", f"[{name}] ⚡ Kích hoạt hoàn thành miễn phí ngay lập tức cho ô slot {aktif_up.get('slot')}!", Fore.YELLOW)
                    time.sleep(1)
                    requests.post(f"{API_BASE}/base/claim", headers=headers, json={'slot': aktif_up.get('slot'), 'client_command_id': str(uuid.uuid4())}, timeout=6)
            except Exception:
                pass

    # 4. Thu hoạch sản lượng tài nguyên từ các mỏ (/base/production_claim)
    prod_slots = [4, 5, 6, 7, 20, 21, 28, 29, 32]
    for p_slot in prod_slots:
        try:
            r_prod = requests.post(f"{API_BASE}/base/production_claim", headers=headers, json={
                'slot': p_slot, 'client_command_id': str(uuid.uuid4())
            }, timeout=4).json()
            if r_prod.get('ok') and r_prod.get('data', {}).get('miktar'):
                log("HARVEST", f"[{name}] 🌾 Thu hoạch sản lượng ô slot {p_slot}: +{r_prod['data']['miktar']} tài nguyên", Fore.CYAN)
        except Exception:
            pass

    # 5. Kiểm tra thợ xây & Tiến hành Nâng cấp / Xây dựng liên tục
    active_building = [b for b in binalar if b.get('bitis') and now_ms < b.get('bitis')]
    if aktif_up and aktif_up.get('bitis') and now_ms < aktif_up.get('bitis'):
        active_building.append(aktif_up)

    max_builders = 1

    if len(active_building) < max_builders:
        # THỢ XÂY RẢNH -> NÂNG CẤP KARARGAH (HQ) HOẶC ĐIỀU KIỆN TIÊN QUYẾT
        if hq_level < 10:
            p_hq = {'slot': 0, 'client_command_id': str(uuid.uuid4())}
            try:
                r_hq_up = requests.post(f"{API_BASE}/base/upgrade", headers=headers, json=p_hq, timeout=8).json()
                if r_hq_up.get('ok'):
                    bitis_s = int((r_hq_up.get('data', {}).get('bitis', 0) - now_ms) / 1000)
                    log("HQ_UPGRADE", f"[{name}] 🚀 ĐANG NÂNG CẤP KARARGAH (HQ) lên Cấp {hq_level + 1}! (Thời gian: {bitis_s}s)", Fore.YELLOW)
                else:
                    err = r_hq_up.get('err', '')
                    if 'on_kosul_' in err:
                        pre_tur = err.split('on_kosul_')[-1]
                        log("PREREQ", f"[{name}] ⚙️ HQ {hq_level+1} yêu cầu hoàn thành [{pre_tur}] trước...", Fore.CYAN)

                        # Kiểm tra công trình đó đã có trong binalar chưa
                        existing_b = next((b for b in binalar if b.get('tur') == pre_tur), None)
                        if existing_b:
                            slot_b = existing_b.get('slot')
                            r_sub_up = requests.post(f"{API_BASE}/base/upgrade", headers=headers, json={
                                'slot': slot_b, 'client_command_id': str(uuid.uuid4())
                            }, timeout=8).json()
                            if r_sub_up.get('ok'):
                                bitis_s = int((r_sub_up.get('data', {}).get('bitis', 0) - now_ms) / 1000)
                                log("SUB_UPGRADE", f"[{name}] 🔨 Đang nâng cấp [{pre_tur}] ô slot {slot_b}! (Thời gian: {bitis_s}s)", Fore.YELLOW)
                            elif 'on_kosul_' in r_sub_up.get('err', ''):
                                sub_pre = r_sub_up.get('err', '').split('on_kosul_')[-1]
                                sub_b = next((b for b in binalar if b.get('tur') == sub_pre), None)
                                if sub_b:
                                    requests.post(f"{API_BASE}/base/upgrade", headers=headers, json={'slot': sub_b.get('slot'), 'client_command_id': str(uuid.uuid4())}, timeout=8)
                        else:
                            # Chưa có -> Tìm trong parseller để xây mới
                            open_parcel = next((p for p in parseller if p.get('tur') == pre_tur and p.get('kurulabilir')), None)
                            if open_parcel:
                                p_slot = open_parcel.get('slot')
                                r_bld = requests.post(f"{API_BASE}/base/build", headers=headers, json={
                                    'tur': pre_tur, 'slot': p_slot, 'client_command_id': str(uuid.uuid4())
                                }, timeout=8).json()
                                if r_bld.get('ok'):
                                    bitis_s = int((r_bld.get('data', {}).get('bitis', 0) - now_ms) / 1000)
                                    log("BUILD_NEW", f"[{name}] 🏗️ Đang xây mới [{pre_tur}] tại ô slot {p_slot}! (Thời gian: {bitis_s}s)", Fore.MAGENTA)
                    elif 'kaynak' in err or 'resource' in err:
                        log("RES_WAIT", f"[{name}] ⏳ Đang tích lũy tài nguyên để nâng cấp HQ Cấp {hq_level+1}...", Fore.LIGHTBLACK_EX)
                    else:
                        # Nâng cấp các công trình phụ trợ nếu có ô mở
                        buildable = [p for p in parseller if p.get('kurulabilir') and p.get('durum') == 'kurulabilir']
                        if buildable:
                            target_p = buildable[0]
                            p_tur = target_p.get('tur')
                            p_slot = target_p.get('slot')
                            r_bld = requests.post(f"{API_BASE}/base/build", headers=headers, json={
                                'tur': p_tur, 'slot': p_slot, 'client_command_id': str(uuid.uuid4())
                            }, timeout=8).json()
                            if r_bld.get('ok'):
                                log("BUILD_EXPAND", f"[{name}] 🏗️ Mở rộng căn cứ: Xây mới [{p_tur}] tại slot {p_slot}!", Fore.MAGENTA)
            except Exception as e:
                log("WARN", f"[{name}] Lỗi nâng cấp: {e}", Fore.YELLOW)
        else:
            log("HQ_MAX", f"[{name}] 🏆 Karargah HQ ĐÃ ĐẠT CẤP {hq_level}! Đủ điều kiện nhận thưởng 10M Rignite!", Fore.GREEN)

    # 6. Gom quà Hòm thư (/mail/claim_all)
    try:
        r_m = requests.post(f"{API_BASE}/mail/claim_all", headers=headers, json={'client_command_id': str(uuid.uuid4())}, timeout=5).json()
        if r_m.get('ok') and r_m.get('data', {}).get('alinan', 0) > 0:
            log("MAIL", f"[{name}] 🎁 Đã nhận quà hòm thư thành công!", Fore.MAGENTA)
    except Exception:
        pass

    # 7. Nhận nhiệm vụ hàng ngày (/quest/claim)
    try:
        quests = changed.get('quest', {}).get('gorevler', {})
        for q_key, q_info in quests.items():
            if not q_info.get('claimed') and q_info.get('count', 0) >= q_info.get('hedef', 1):
                r_qc = requests.post(f"{API_BASE}/quest/claim", headers=headers, json={
                    'gorev': q_key, 'client_command_id': str(uuid.uuid4())
                }, timeout=5).json()
                if r_qc.get('ok'):
                    log("QUEST", f"[{name}] 🎯 Hoàn thành & nhận thưởng nhiệm vụ [{q_key}]!", Fore.GREEN)
    except Exception:
        pass

    # 8. Kiểm tra & Húp trọn 10,000,000 (10M) Rignite Coins
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
                status_10m = r_hq10.get("status")
                rec_lv = r_hq10.get("completedHqLevel", hq_level)
                if status_10m == "rewarded":
                    log("JACKPOT_10M", f"[{name}] 🎉🎉🎉 ĐÃ HÚP TRỌN 10,000,000 RIGNITE COINS TỪ WARHOLD HQ 10!", Fore.GREEN)
                else:
                    log("STATUS", f"[{name}] 🏰 Karargah HQ: Cấp {rec_lv}/10 | Nhiệm vụ 10M Rignite: [{status_10m}] | Đang cày liên tục...", Fore.CYAN)
    except Exception as e:
        log("10M_CHECK", f"[{name}] {e}", Fore.LIGHTBLACK_EX)

def start_warhold_mining_247():
    print(f"""
{Fore.CYAN}======================================================================
  ⚔️ AUTO WARHOLD - CÀY LIÊN TỤC 24/7 & NÂNG CẤP LẤY 10,000,000 RIGNITE 🚀
  - Chạy liên tục không ngừng nghỉ (Tự động xoay vòng ca trực trên GitHub Actions)
  - Đa tài khoản: hungzai22 & gaylobucu
  - Tự động hoàn thành & nhận thưởng công trình (/base/claim)
  - Tự động gỡ nút thắt điều kiện & nâng cấp Karargah (HQ) lên Cấp 10
  - Tự động thu hoạch sản lượng lương thực, gỗ, pin năng lượng
  - Tự động kích hoạt nhận thưởng 10M Rignite ngay khi đạt mốc HQ 10
======================================================================{Style.RESET_ALL}
    """)

    start_time = time.time()
    if IS_GITHUB_ACTIONS:
        log("GITHUB", f"Đang chạy trên GitHub Actions. Giới hạn ca trực: {MAX_RUNTIME}s (~{MAX_RUNTIME//3600}h)", Fore.YELLOW)

    step_count = 0
    while True:
        try:
            step_count += 1
            log("LOOP", f"🔄 Chu kỳ kiểm tra cày cuốc #{step_count}...", Fore.WHITE)

            for acc in ACCOUNTS:
                process_account_step(acc)
                time.sleep(2)

            # Kiểm tra thời gian ca trực GitHub Actions
            if MAX_RUNTIME > 0 and (time.time() - start_time) >= MAX_RUNTIME:
                log("CA_TRUC", f"Hoàn thành ca trực {MAX_RUNTIME//3600} tiếng trên GitHub Actions. Kích hoạt ca tiếp theo an toàn!", Fore.GREEN)
                trigger_next_shift()
                break

            time.sleep(20)

        except Exception as e:
            log("ERR_LOOP", f"Lỗi vòng lặp: {e}", Fore.RED)
            time.sleep(10)

if __name__ == "__main__":
    start_warhold_mining_247()
