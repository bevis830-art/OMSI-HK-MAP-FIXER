# ============================================
# modules/indexer.py
# HK Map TTData — stops/tracks 索引器
# ============================================

import os

def load_name_id_pairs(file_path):
    """
    讀取 stops.txt 或 tracks.txt，建立：
    - 名稱 → [ID 列表]
    - ID → 名稱
    """
    name_to_ids = {}
    id_to_name = {}

    if not os.path.exists(file_path):
        return name_to_ids, id_to_name

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    id_val, name = parts
                    name_to_ids.setdefault(name, []).append(id_val)
                    id_to_name[id_val] = name
    except Exception as e:
        print(f"[ERROR] Failed to read {file_path}: {e}")

    return name_to_ids, id_to_name


def build_global_maps(ttdata_folder, console=None):
    """
    建立 stops / tracks 的全域索引
    - 名稱 → [ID 列表]
    - ID → 名稱
    """
    global_name_map = {}
    global_id_to_name = {}

    for root, dirs, files in os.walk(ttdata_folder):
        for file in files:
            if file.lower() in ("stops.txt", "tracks.txt"):
                path = os.path.join(root, file)

                if console:
                    console.insert("end", f"[INDEX] Loading {file}...\n")
                    console.see("end")

                name_map, id_map = load_name_id_pairs(path)

                # 合併名稱 → ID
                for name, ids in name_map.items():
                    global_name_map.setdefault(name, []).extend(ids)

                # 合併 ID → 名稱
                global_id_to_name.update(id_map)

    # 同名優先：使用最後一個 ID（HK map 標準）
    for name, ids in global_name_map.items():
        global_name_map[name] = ids  # 保留全部，但修復時用最後一個

    if console:
        console.insert("end", f"[INDEX] 完成 stops/tracks 索引建立\n")
        console.see("end")

    return global_name_map, global_id_to_name
