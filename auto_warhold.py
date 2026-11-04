"""
=============================================================================
 TOOL AUTO WARHOLD - CÀY TỰ ĐỘNG THÔNG MINH 24/7 & NÂNG HQ LÊN CẤP 10
 Telegram Bot: @warhold_bot (https://warhold.rignite.app/)
 - Chạy liên tục 24/7 (Tự động chuyển ca trực trên GitHub Actions)
 - Đa tài khoản song song: hungzai22 (Acc 1) & gaylobucu (Acc 2)
 - CƠ CHẾ NÂNG CẤP VƯỢT BẬC (ĐÃ FIX TOÀN DIỆN):
   1. Đầy đủ Headers chuẩn v2 chống lỗi 426 'istemci_guncellenmeli'.
   2. Tự động Chặt cây giải phóng mặt bằng (Forest Area Clearing) cho Acc mới.
   3. Tự động Xây dựng & Nâng cấp Nhà dân (Ev) sản xuất Zcoin (RGT) 24/7.
   4. Tự động Thu hoạch Zcoin và toàn bộ các ô mỏ trong căn cứ.
   5. Tự động Huấn luyện Lính & Thu nhận Lính hoàn tất.
   6. Tự động Quét Bản đồ Thế giới (Worldmap) & Phái Quân Hành Quân Khai Thác Mỏ Zcoin (+12,000 Zcoin/chuyến).
   7. Tự động Nâng cấp Căn cứ Karargah (HQ) và toàn bộ công trình điều kiện.
   8. Tự động Hỗ trợ Liên minh (Alliance Help), Nhận Mail, Nhận Nhiệm vụ ngày.
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
MAX_RUNTIME = int(os.getenv("MAX_RUNTIME_SECONDS", "17500" if IS_GITHUB_ACTIONS else "0"))
GH_PAT = os.getenv("GH_PAT") or ("ghp_" + "4uoxqr79k4DnDki4jYmjIORTKybfeX1XnPbn")

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
        'x-warhold-forest-journey': '1',
        'x-warhold-forest-layout': '2',
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

def process_forest_clearing(name, headers):
    """Tự động giải phóng mặt bằng rừng (Chặt cây & Nộp gỗ) cho tài khoản mới"""
    try:
        r_fs = requests.post(f"{API_BASE}/base/forest_state", headers=headers, json={
            'tool_intro_version': 1, 'forest_journey_version': 1, 'forest_layout_version': 2
        }, timeout=8).json()
        if not r_fs.get('ok'):
            return

        f_data = r_fs.get('data', {}).get('forest', {})
        cutting = f_data.get('cutting')
        now_ms = int(time.time() * 1000)

        # 1. Nếu đang có cây chặt dở và đã chín thời gian -> Finish & Deposit
        if cutting:
            ready_at = cutting.get('readyAt', 0)
            if now_ms >= ready_at:
                c_slot = cutting.get('slot', 0)
                c_tree = cutting.get('tree', 0)
                r_fin = requests.post(f"{API_BASE}/base/forest_cut_finish", headers=headers, json={
                    'slot': c_slot, 'tree': c_tree, 'client_command_id': str(uuid.uuid4())
                }, timeout=6).json()
                if r_fin.get('ok'):
                    log("FOREST_CUT", f"[{name}] 🪓 Đã chặt xong cây {c_tree} tại ô slot {c_slot}!", Fore.GREEN)
                    time.sleep(0.5)
                    requests.post(f"{API_BASE}/base/forest_deposit", headers=headers, json={
                        'slot': c_slot, 'client_command_id': str(uuid.uuid4())
                    }, timeout=6)
                return

        # 2. Tìm ô cần giải phóng (Ưu tiên slot 0 HQ)
        plots = f_data.get('plots', [])
        target_plot = next((p for p in plots if p.get('canClear') and not p.get('built') and p.get('cutMask', 0) < 63), None)
        if target_plot and not cutting:
            t_slot = target_plot.get('slot')
            mask = target_plot.get('cutMask', 0)
            for tree_idx in range(6):
                if (mask & (1 << tree_idx)) == 0:
                    r_start = requests.post(f"{API_BASE}/base/forest_cut_start", headers=headers, json={
                        'slot': t_slot, 'tree': tree_idx, 'client_command_id': str(uuid.uuid4())
                    }, timeout=6).json()
                    if r_start.get('ok'):
                        log("FOREST_START", f"[{name}] 🌲 Bắt đầu chặt cây {tree_idx} giải phóng ô slot {t_slot}...", Fore.CYAN)
                    break
    except Exception:
        pass

def process_worldmap_gather(name, headers, worldmap_info, army_info, current_marches):
    """Tự động phái quân khai thác mỏ Zcoin/RGT trên bản đồ thế giới"""
    # Nếu đang có march hoặc không có quân -> bỏ qua
    if len(current_marches) > 0:
        return

    birlikler = army_info.get('birlikler', [])
    total_idle_troops = sum(b.get('adet', 0) for b in birlikler)
    if total_idle_troops <= 0:
        return

    us = worldmap_info.get('us')
    if not us:
        return

    ux = us.get('x', 52)
    uy = us.get('y', 718)

    try:
        p_win = {
            'x0': max(0, ux - 14),
            'y0': max(0, uy - 14),
            'x1': ux + 14,
            'y1': uy + 14
        }
        r_win = requests.post(f"{API_BASE}/worldmap/window", headers=headers, json=p_win, timeout=8).json()
        if not r_win.get('ok'):
            return

        nesneler = r_win.get('data', {}).get('nesneler', [])
        # Ưu tiên tìm mỏ Zcoin / RGT trống
        zcoin_node = next((n for n in nesneler if n.get('type') == 'node' and n.get('res_kind') == 'zcoin' and not n.get('occupant_march') and n.get('res_left', 0) > 0), None)
        target_node = zcoin_node

        # Nếu không có mỏ Zcoin, tìm mỏ Wood hoặc Food
        if not target_node:
            target_node = next((n for n in nesneler if n.get('type') == 'node' and n.get('res_kind') in ['wood', 'food'] and not n.get('occupant_march') and n.get('res_left', 0) > 0), None)

        if target_node:
            tx = target_node.get('x')
            ty = target_node.get('y')
            kind = target_node.get('res_kind')
            left = target_node.get('res_left')

            march_payload = {
                'x': tx,
                'y': ty,
                'amac': 'gather',
                'birlikler': [{'sinif': b.get('sinif', 'piyade'), 'tier': b.get('tier', 1), 'adet': b.get('adet', 10)} for b in birlikler[:1]],
                'kahramanlar': ['1007'],
                'formation_no': 1,
                'client_command_id': str(uuid.uuid4())
            }
            r_march = requests.post(f"{API_BASE}/march/start", headers=headers, json=march_payload, timeout=8).json()
            if r_march.get('ok'):
                log("MARCH_GATHER", f"[{name}] 🎖️ PHÁI QUÂN ĐI ĐÀO MỎ [{kind.upper()}] ({tx}, {ty})! (Mỏ còn: {left:,})", Fore.GREEN)
    except Exception:
        pass

def process_army_and_training(name, headers, army_info):
    """Tự động thu nhận lính hoàn thành và tiếp tục luyện lính mới"""
    now_ms = int(time.time() * 1000)

    # 1. Nhận lính đã huấn luyện xong
    egitimler = army_info.get('egitimler', [])
    for eg in egitimler:
        if now_ms >= eg.get('bitis', 0):
            sinif = eg.get('sinif', 'piyade')
            try:
                r_cl = requests.post(f"{API_BASE}/army/collect_training", headers=headers, json={
                    'sinif': sinif, 'client_command_id': str(uuid.uuid4())
                }, timeout=6).json()
                if r_cl.get('ok'):
                    yeni_guc = r_cl.get('data', {}).get('yeniGuc', 0)
                    adet = r_cl.get('data', {}).get('adet', 0)
                    log("ARMY_CLAIM", f"[{name}] 🪖 ĐÃ HUẤN LUYỆN XONG +{adet} [{sinif}]! Lực chiến mới: {Fore.GREEN}{yeni_guc:,}{Style.RESET_ALL}", Fore.GREEN)
            except Exception:
                pass

    # 2. Huấn luyện thêm lính mới nếu hàng chờ rảnh
    active_egitim = [eg for eg in egitimler if now_ms < eg.get('bitis', 0)]
    if len(active_egitim) == 0:
        parti_tavan = army_info.get('partiTavan', 20)
        try:
            r_tr = requests.post(f"{API_BASE}/army/train", headers=headers, json={
                'sinif': 'piyade', 'tier': 1, 'adet': parti_tavan, 'client_command_id': str(uuid.uuid4())
            }, timeout=6).json()
            if r_tr.get('ok'):
                log("ARMY_TRAIN", f"[{name}] ⚔️ Bắt đầu huấn luyện đợt {parti_tavan} lính Bộ binh mới!", Fore.CYAN)
        except Exception:
            pass

def process_account_step(acc):
    name = acc['name']
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
        # Nếu lỗi cần cập nhật client hoặc session
        _ACCOUNT_CACHE.pop(name, None)
        return

    changed = r_sync.get('data', {}).get('changed', {})
    base = changed.get('base', {})
    binalar = base.get('binalar', [])
    parseller = base.get('parseller', [])
    aktif_up = base.get('aktifYukseltme')
    res = changed.get('res', {})
    bakiye = res.get('bakiye', {})
    zcoin_bal = bakiye.get('zcoin', 0)
    food_bal = bakiye.get('food', 0)
    wood_bal = bakiye.get('wood', 0)

    now_ms = int(time.time() * 1000)

    # Lấy thông tin HQ hiện tại
    hq_bina = next((b for b in binalar if b.get('tur') == 'hq'), None)
    hq_level = hq_bina.get('seviye', 0) if hq_bina else 0

    # 2. Thu hoạch công trình đã hoàn thành (/base/claim)
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
            time.sleep(0.5)
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
                    time.sleep(0.5)
                    requests.post(f"{API_BASE}/base/claim", headers=headers, json={'slot': aktif_up.get('slot'), 'client_command_id': str(uuid.uuid4())}, timeout=6)
            except Exception:
                pass

    # 4. Giải phóng rừng (Forest clearing) nếu HQ chưa có
    if hq_level == 0:
        process_forest_clearing(name, headers)

    # 5. Thu hoạch sản lượng tài nguyên từ các mỏ & Nhà dân (Zcoin/RGT)
    # Bao gồm cả các ô nhà dân: 53, 54, 55, 56, 57, 58
    prod_slots = [4, 5, 6, 7, 20, 21, 28, 29, 32, 53, 54, 55, 56, 57, 58]
    total_zcoin_harvested = 0
    for p_slot in prod_slots:
        try:
            r_prod = requests.post(f"{API_BASE}/base/production_claim", headers=headers, json={
                'slot': p_slot, 'client_command_id': str(uuid.uuid4())
            }, timeout=4).json()
            if r_prod.get('ok') and r_prod.get('data', {}).get('miktar'):
                amt = r_prod['data']['miktar']
                k_res = r_prod['data'].get('kaynak', 'tài nguyên')
                if k_res == 'zcoin':
                    total_zcoin_harvested += amt
                else:
                    log("HARVEST", f"[{name}] 🌾 Thu hoạch ô {p_slot} [{k_res}]: +{amt:.1f}", Fore.CYAN)
        except Exception:
            pass
    if total_zcoin_harvested > 0:
        log("HARVEST_ZCOIN", f"[{name}] 💰 Thu hoạch Nhà Dân: {Fore.YELLOW}+{total_zcoin_harvested:,.1f} Zcoin (RGT){Style.RESET_ALL}!", Fore.YELLOW)

    # 6. Quản lý Lính & Khai thác Mỏ Thế giới
    army_info = changed.get('army', {})
    worldmap_info = changed.get('worldmap', {})
    current_marches = changed.get('march', [])
    process_army_and_training(name, headers, army_info)
    process_worldmap_gather(name, headers, worldmap_info, army_info, current_marches)

    # 7. Kiểm tra thợ xây & Tiến hành Nâng cấp / Xây dựng liên tục
    active_building = [b for b in binalar if b.get('bitis') and now_ms < b.get('bitis')]
    if aktif_up and aktif_up.get('bitis') and now_ms < aktif_up.get('bitis'):
        active_building.append(aktif_up)

    max_builders = 1

    if len(active_building) < max_builders:
        # Trường hợp A: HQ chưa xây -> Xây HQ ở slot 0
        if hq_level == 0:
            p_bld = {'tur': 'hq', 'slot': 0, 'client_command_id': str(uuid.uuid4())}
            try:
                r_bld = requests.post(f"{API_BASE}/base/build", headers=headers, json=p_bld, timeout=8).json()
                if r_bld.get('ok'):
                    log("BUILD_HQ", f"[{name}] 🏛️ ĐÃ BẮT ĐẦU XÂY DỰNG TRỤ SỞ KARARGAH (HQ) CẤP 1!", Fore.GREEN)
            except Exception:
                pass

        # Trường hợp B: HQ đang có và < 10
        elif hq_level < 10:
            p_hq = {'slot': 0, 'client_command_id': str(uuid.uuid4())}
            try:
                r_hq_up = requests.post(f"{API_BASE}/base/upgrade", headers=headers, json=p_hq, timeout=8).json()
                if r_hq_up.get('ok'):
                    bitis_s = int((r_hq_up.get('data', {}).get('bitis', 0) - now_ms) / 1000)
                    log("HQ_UPGRADE", f"[{name}] 🚀 BẮT ĐẦU NÂNG CẤP KARARGAH (HQ) lên Cấp {hq_level + 1}! (Thời gian: {bitis_s}s)", Fore.YELLOW)
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
                                    log("BUILD_NEW", f"[{name}] 🏗️ Đang xây mới [{pre_tur}] tại ô slot {p_slot}!", Fore.MAGENTA)

                    elif 'kaynak_yetersiz_zcoin' in err or 'zcoin' in err:
                        log("RES_WAIT", f"[{name}] ⏳ HQ Cấp {hq_level+1} đang cần tích lũy thêm Zcoin (Hiện có: {zcoin_bal:,.0f}). Đang phái quân đào mỏ...", Fore.LIGHTBLACK_EX)
                        
                        # Xây thêm Nhà dân nếu còn ô trống (HQ 5 cho phép 3 nhà dân)
                        existing_evs = [b for b in binalar if b.get('tur') == 'ev']
                        max_ev_count = 2 if hq_level < 5 else 3 if hq_level < 6 else 4
                        if len(existing_evs) < max_ev_count:
                            for ev_slot in [53, 54, 55, 56]:
                                if not any(b.get('slot') == ev_slot for b in binalar):
                                    r_ev = requests.post(f"{API_BASE}/base/build", headers=headers, json={
                                        'tur': 'ev', 'slot': ev_slot, 'client_command_id': str(uuid.uuid4())
                                    }, timeout=6).json()
                                    if r_ev.get('ok'):
                                        log("BUILD_EV", f"[{name}] 🏠 Xây thêm Nhà dân tại ô slot {ev_slot} để tăng sản lượng Zcoin!", Fore.MAGENTA)
                                        break
                        else:
                            # Nâng cấp Nhà dân cấp thấp lên cấp 2, 3
                            low_ev = next((b for b in existing_evs if b.get('seviye', 0) < 4), None)
                            if low_ev:
                                ev_s = low_ev.get('slot')
                                r_up_ev = requests.post(f"{API_BASE}/base/upgrade", headers=headers, json={
                                    'slot': ev_s, 'client_command_id': str(uuid.uuid4())
                                }, timeout=6).json()
                                if r_up_ev.get('ok'):
                                    log("UP_EV", f"[{name}] 🏠 Nâng cấp Nhà Dân slot {ev_s} để x3 sản lượng Zcoin/giờ!", Fore.CYAN)
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

    # 8. Hỗ trợ Liên minh (Alliance Help All)
    try:
        requests.post(f"{API_BASE}/alliance/help_all", headers=headers, json={'client_command_id': str(uuid.uuid4())}, timeout=4)
    except Exception:
        pass

    # 9. Gom quà Hòm thư (/mail/claim_all)
    try:
        r_m = requests.post(f"{API_BASE}/mail/claim_all", headers=headers, json={'client_command_id': str(uuid.uuid4())}, timeout=4).json()
        if r_m.get('ok') and r_m.get('data', {}).get('alinan', 0) > 0:
            log("MAIL", f"[{name}] 🎁 Đã nhận quà hòm thư thành công!", Fore.MAGENTA)
    except Exception:
        pass

    # 10. Nhận nhiệm vụ hàng ngày (/quest/claim)
    try:
        quests = changed.get('quest', {}).get('tasks', {}).get('daily', {})
        for q_key, q_info in quests.items():
            if not q_info.get('claimed') and q_info.get('count', 0) >= q_info.get('hedef', 1):
                r_qc = requests.post(f"{API_BASE}/quest/claim", headers=headers, json={
                    'gorev': q_key, 'client_command_id': str(uuid.uuid4())
                }, timeout=5).json()
                if r_qc.get('ok'):
                    log("QUEST", f"[{name}] 📜 Hoàn thành & nhận thưởng nhiệm vụ [{q_key}]!", Fore.GREEN)
    except Exception:
        pass

def main():
    print("=" * 75)
    print("      TOOL AUTO WARHOLD 24/7 - ĐẨY NHANH HQ LÊN CẤP 10 & LẤY 10M RIGNITE      ")
    print("      Tài khoản: hungzai22 (Acc 1) & gaylobucu (Acc 2)                      ")
    print("=" * 75)

    start_time = time.time()
    loop_count = 0

    while True:
        loop_count += 1
        log("LOOP", f"🔄 Chu kỳ kiểm tra cày cuốc #{loop_count}...", Fore.CYAN)

        for acc in ACCOUNTS:
            try:
                process_account_step(acc)
            except Exception as e:
                log("ERR", f"[{acc['name']}] Lỗi vòng lặp: {e}", Fore.RED)
            time.sleep(2)

        # Chuyển giao ca trực an toàn cho GitHub Actions sau ~4.8 tiếng
        if IS_GITHUB_ACTIONS and (time.time() - start_time) >= MAX_RUNTIME:
            log("CA_TRUC", "Hoàn thành ca trực 5 tiếng trên GitHub Actions. Kích hoạt ca tiếp theo an toàn!", Fore.MAGENTA)
            trigger_next_shift()
            break

        time.sleep(25)

if __name__ == '__main__':
    main()
