# ============================================
# ttdata_core.py
# HK Map TTData Auto-Rebuilder — 核心整合器
# ============================================

import os

from modules.indexer import build_global_maps
from modules.stnlink import process_stnlink_file
from modules.timetable import process_timetable_file
from modules.ailist import process_ailist_file
from modules.utils import (
    gui_print,
    gui_progress_step,
    scan_files,
    count_total_tasks,
    write_log
)


# ------------------------------------------------
# 主流程：全自動重建 TTData
# ------------------------------------------------
def run_full_rebuild(ttdata_folder, console=None, progress=None, log_viewer=None):
    gui_print(console, "==============================================")
    gui_print(console, " HK Map TTData Auto-Rebuilder — Full Rebuild")
    gui_print(console, "==============================================")

    # ------------------------------------------------
    # Step 0 — 計算總工作量（給進度條）
    # ------------------------------------------------
    total_tasks = count_total_tasks(ttdata_folder)
    if progress:
        progress["maximum"] = max(total_tasks, 1)

    gui_print(console, f"[Init] 預估總工作量：{total_tasks} 項")

    # ------------------------------------------------
    # Step 1 — 建立 stops / tracks 全域索引
    # ------------------------------------------------
    gui_print(console, "[Step 1] 建立 stops / tracks 索引中...")
    name_map, id_to_name = build_global_maps(ttdata_folder, console)
    gui_print(console, "[OK] stops/tracks 索引建立完成\n")

    # ------------------------------------------------
    # Step 2 — 處理 stnlink.cfg
    # ------------------------------------------------
    gui_print(console, "[Step 2] 處理 stnlink.cfg ...")

    stnlink_files = scan_files(ttdata_folder, ["cfg"])
    stnlink_files = [f for f in stnlink_files if "stnlink" in os.path.basename(f).lower()]

    for path in stnlink_files:
        process_stnlink_file(path, name_map, id_to_name, console, progress)

    gui_print(console, f"[OK] 已修復 {len(stnlink_files)} 個 stnlink\n")

    # ------------------------------------------------
    # Step 3 — 處理 AIlist.cfg（自動生成 timetable）
    # ------------------------------------------------
    gui_print(console, "[Step 3] 處理 AIlist.cfg ...")

    ailist_files = scan_files(ttdata_folder, ["cfg"])
    ailist_files = [f for f in ailist_files if "ailist" in os.path.basename(f).lower()]

    timetable_files = []

    for path in ailist_files:
        tt_files = process_ailist_file(path, ttdata_folder, console, progress)
        timetable_files.extend(tt_files)

    # 去重
    timetable_files = list(set(timetable_files))

    gui_print(console, f"[OK] AIlist 處理完成，共 {len(timetable_files)} 個 timetable\n")

    # ------------------------------------------------
    # Step 4 — 處理 timetable (.tt / .ttp)
    # ------------------------------------------------
    gui_print(console, "[Step 4] 處理 timetable (.tt / .ttp) ...")

    # stnlink chain map（目前留空，未來可加入自動 chain builder）
    stnlink_chain_map = {}

    # 掃描所有 timetable
    tt_files = scan_files(ttdata_folder, ["tt", "ttp"])

    for path in tt_files:
        process_timetable_file(path, stnlink_chain_map, name_map, id_to_name, console, progress)

    gui_print(console, f"[OK] 已修復 {len(tt_files)} 個 timetable\n")

    # ------------------------------------------------
    # Step 5 — 寫入 log
    # ------------------------------------------------
    gui_print(console, "[Step 5] 寫入 log ...")

    log_path = os.path.join(ttdata_folder, "fix_log.txt")

    # 收集 console 內容
    if log_viewer:
        log_text = log_viewer.get("1.0", "end")
    else:
        log_text = "TTData rebuild completed."

    write_log(log_path, log_text, console)

    gui_print(console, "[DONE] 全部修復完成！")
    gui_print(console, f"[Log] 已輸出：{log_path}")
