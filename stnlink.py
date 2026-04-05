# ============================================
# modules/stnlink.py
# HK Map 專用 StnLink 強制重建器
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
# 解析 StnLink Header（HK map 格式）
# ------------------------------------------------
def parse_stnlink_header(lines, idx):
    header = {
        "length": float(lines[idx+1].strip()),
        "from_stop": lines[idx+2].strip(),
        "to_stop": lines[idx+3].strip(),
        "angle_start": float(lines[idx+4].strip()),
        "angle_end": float(lines[idx+5].strip()),
        "height_start": float(lines[idx+6].strip()),
        "height_end": float(lines[idx+7].strip()),
        "unknown": lines[idx+8].strip(),
        "entry_count": int(lines[idx+9].strip())
    }
    return header, idx + 10


# ------------------------------------------------
# 解析 StnLink Entry（HK map 格式）
# ------------------------------------------------
def parse_stnlink_entry(lines, idx):
    entry = {
        "track_id": lines[idx+1].strip(),
        "lane": lines[idx+2].strip(),
        "spline_id": lines[idx+3].strip(),
        "length": float(lines[idx+4].strip()),
        "next": lines[idx+5].strip(),
        "prev": lines[idx+6].strip(),
        "unknown": lines[idx+7].strip()
    }
    return entry, idx + 8


# ------------------------------------------------
# 修復 ID（TrackID / SplineID / StopID）
# ------------------------------------------------
def fix_id(id_val, name_map, id_to_name, log, label):
    if id_val in id_to_name:
        return id_val  # 有效 ID

    # 找名稱
    name = id_to_name.get(id_val, None)
    if not name:
        log.append(f"[WARN] {label} {id_val} 無法找到名稱映射，跳過")
        return id_val

    # 同名優先：使用最後一個 ID
    correct_id = name_map[name][-1]
    log.append(f"[FIX] {label} {id_val} → {correct_id} (name: {name})")
    return correct_id


# ------------------------------------------------
# 重建 Entry Chain（強制重建）
# ------------------------------------------------
def rebuild_entry_chain(entries, log):
    for i, e in enumerate(entries):
        e["prev"] = str(i - 1 if i > 0 else -1)
        e["next"] = str(i + 1 if i < len(entries) - 1 else -1)

    log.append(f"[CHAIN] Entry chain 已重建，共 {len(entries)} entries")
    return entries


# ------------------------------------------------
# 重建 Link 長度（累加 entry length）
# ------------------------------------------------
def rebuild_link_length(entries, header, log):
    total = sum(e["length"] for e in entries)
    header["length"] = total
    log.append(f"[LENGTH] Link length 重算 = {total:.3f}")
    return header


# ------------------------------------------------
# 修復整個 StnLink 區塊
# ------------------------------------------------
def fix_stnlink_block(header, entries, name_map, id_to_name, log):
    # 修復 FromStop / ToStop
    header["from_stop"] = fix_id(header["from_stop"], name_map, id_to_name, log, "FromStop")
    header["to_stop"] = fix_id(header["to_stop"], name_map, id_to_name, log, "ToStop")

    # 修復 TrackID / SplineID
    for e in entries:
        e["track_id"] = fix_id(e["track_id"], name_map, id_to_name, log, "TrackID")
        e["spline_id"] = fix_id(e["spline_id"], name_map, id_to_name, log, "SplineID")

    # 強制重建 chain
    entries = rebuild_entry_chain(entries, log)

    # 重建 link 長度
    header = rebuild_link_length(entries, header, log)

    # 更新 entry_count
    header["entry_count"] = len(entries)

    return header, entries


# ------------------------------------------------
# 處理 stnlink.cfg
# ------------------------------------------------
def process_stnlink_file(path, name_map, id_to_name, console=None, progress=None):
    log = []

    gui_print(console, f"[StnLink] 處理 {os.path.basename(path)} ...")

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

        if line.strip() == "[StnLink]":
            log.append(f"\n=== 修復 StnLink（行 {i}） ===")

            # 解析 header
            header, idx = parse_stnlink_header(lines, i)

            # 解析 entries
            entries = []
            for _ in range(header["entry_count"]):
                idx += 1  # 跳過 "   X:"
                entry, idx = parse_stnlink_entry(lines, idx)
                entries.append(entry)

            # 修復整個 block
            header, entries = fix_stnlink_block(header, entries, name_map, id_to_name, log)

            # 寫回新內容
            new_lines.append("[StnLink]\n")
            new_lines.append(f"{header['length']}\n")
            new_lines.append(f"{header['from_stop']}\n")
            new_lines.append(f"{header['to_stop']}\n")
            new_lines.append(f"{header['angle_start']}\n")
            new_lines.append(f"{header['angle_end']}\n")
            new_lines.append(f"{header['height_start']}\n")
            new_lines.append(f"{header['height_end']}\n")
            new_lines.append(f"{header['unknown']}\n")
            new_lines.append(f"{header['entry_count']}\n")

            for idx2, e in enumerate(entries):
                new_lines.append(f"   {idx2}:\n")
                new_lines.append("[StnLink_entry]\n")
                new_lines.append(f"{e['track_id']}\n")
                new_lines.append(f"{e['lane']}\n")
                new_lines.append(f"{e['spline_id']}\n")
                new_lines.append(f"{e['length']}\n")
                new_lines.append(f"{e['next']}\n")
                new_lines.append(f"{e['prev']}\n")
                new_lines.append(f"{e['unknown']}\n")

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
