# ============================================
# modules/timetable.py
# HK Map 專用 timetable 強制重建器
# ============================================

import os
import shutil

# ------------------------------------------------
# 工具：安全輸出到 GUI Console
# ------------------------------------------------
def gui_print(console, text):
    if console:
        console.insert("end", text + "\n")
        console.see("end")
    else:
        print(text)


# ------------------------------------------------
# 解析 Trip Header（HK map 格式）
# ------------------------------------------------
def parse_trip_header(lines, idx):
    """
    [trip]
    RouteName
    DirectionName
    LineNumber
    """
    header = {
        "route": lines[idx+1].strip(),
        "direction": lines[idx+2].strip(),
        "line": lines[idx+3].strip()
    }
    return header, idx + 4


# ------------------------------------------------
# 解析 Station Block（HK map 格式）
# ------------------------------------------------
def parse_station_block(lines, idx):
    """
    [station]
    StopID
    Sequence
    Name
    Unknown
    OffsetX
    Dist
    CumDist
    Wait
    """
    station = {
        "id": lines[idx+1].strip(),
        "seq": int(lines[idx+2].strip()),
        "name": lines[idx+3].strip(),
        "unknown": lines[idx+4].strip(),
        "offset": float(lines[idx+5].strip()),
        "dist": float(lines[idx+6].strip()),
        "cumdist": float(lines[idx+7].strip()),
        "wait": float(lines[idx+8].strip())
    }
    return station, idx + 9


# ------------------------------------------------
# 修復 StopID（同名優先）
# ------------------------------------------------
def fix_stop_id(stop_id, name_map, id_to_name, log):
    if stop_id in id_to_name:
        return stop_id

    name = id_to_name.get(stop_id, None)
    if not name:
        log.append(f"[WARN] StopID {stop_id} 無法找到名稱映射，跳過")
        return stop_id

    correct_id = name_map[name][-1]
    log.append(f"[FIX] StopID {stop_id} → {correct_id} (name: {name})")
    return correct_id


# ------------------------------------------------
# 強制重建站點序列（依照 stnlink chain）
# ------------------------------------------------
def rebuild_station_sequence(stations, stn_chain, log):
    new_seq = []
    used_ids = set()

    for stop_id in stn_chain:
        match = next((s for s in stations if s["id"] == stop_id), None)

        if match:
            new_seq.append(match)
            used_ids.add(stop_id)
        else:
            # timetable 缺站 → 自動補上
            new_seq.append({
                "id": stop_id,
                "seq": 0,
                "name": "AUTO",
                "unknown": "0",
                "offset": 0.0,
                "dist": 0.0,
                "cumdist": 0.0,
                "wait": 0.0
            })
            log.append(f"[ADD] 自動補上缺失站點 {stop_id}")

    log.append(f"[SEQ] 站點序列已重建，共 {len(new_seq)} 站")
    return new_seq


# ------------------------------------------------
# 重建距離欄位（簡化：固定距離）
# ------------------------------------------------
def rebuild_distances(stations, log):
    cum = 0.0
    for i, s in enumerate(stations):
        if i == 0:
            s["dist"] = 0.0
        else:
            s["dist"] = 50.0  # HK map 常用固定距離，可改 spline 計算

        cum += s["dist"]
        s["cumdist"] = cum

    log.append("[DIST] 距離欄位已重建")
    return stations


# ------------------------------------------------
# 重建 seq 欄位
# ------------------------------------------------
def rebuild_sequence_numbers(stations, log):
    for i, s in enumerate(stations):
        s["seq"] = i

    log.append("[SEQ] seq 欄位已重建")
    return stations


# ------------------------------------------------
# 處理 timetable (.tt / .ttp)
# ------------------------------------------------
def process_timetable_file(path, stnlink_chain_map, name_map, id_to_name, console=None, progress=None):
    log = []

    gui_print(console, f"[Timetable] 處理 {os.path.basename(path)} ...")

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        gui_print(console, f"[ERROR] 無法讀取 {path}: {e}")
        return False

    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.strip() == "[trip]":
            log.append(f"\n=== 修復 Trip（行 {i}） ===")

            # 解析 header
            header, idx = parse_trip_header(lines, i)

            # 找 stnlink chain
            route_key = header["route"]
            stn_chain = stnlink_chain_map.get(route_key, [])

            # 解析所有 station
            stations = []
            while idx < len(lines) and lines[idx].strip() == "[station]":
                station, idx = parse_station_block(lines, idx)
                stations.append(station)

            # 修復 StopID
            for s in stations:
                s["id"] = fix_stop_id(s["id"], name_map, id_to_name, log)

            # 強制重建站點序列
            stations = rebuild_station_sequence(stations, stn_chain, log)

            # 重建距離欄位
            stations = rebuild_distances(stations, log)

            # 重建 seq 欄位
            stations = rebuild_sequence_numbers(stations, log)

            # 寫回 trip header
            new_lines.append("[trip]\n")
            new_lines.append(header["route"] + "\n")
            new_lines.append(header["direction"] + "\n")
            new_lines.append(header["line"] + "\n")

            # 寫回 stations
            for s in stations:
                new_lines.append("[station]\n")
                new_lines.append(f"{s['id']}\n")
                new_lines.append(f"{s['seq']}\n")
                new_lines.append(f"{s['name']}\n")
                new_lines.append(f"{s['unknown']}\n")
                new_lines.append(f"{s['offset']}\n")
                new_lines.append(f"{s['dist']}\n")
                new_lines.append(f"{s['cumdist']}\n")
                new_lines.append(f"{s['wait']}\n")

            i = idx
            continue

        else:
            new_lines.append(line)
            i += 1

    # 備份
    shutil.copy2(path, path + ".bak")

    # 寫回檔案
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # 輸出 log
    for l in log:
        gui_print(console, l)

    gui_print(console, f"[OK] 已修復：{os.path.basename(path)}")

    # 更新進度條
    if progress:
        progress.step(1)

    return True
