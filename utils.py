# ============================================
# modules/utils.py
# 共用工具：GUI 輸出、進度條、備份、掃描
# ============================================

import os
import shutil

# ------------------------------------------------
# GUI Console 安全輸出
# ------------------------------------------------
def gui_print(console, text):
    """
    安全輸出到 GUI Console（或 fallback 到 print）
    """
    if console:
        console.insert("end", text + "\n")
        console.see("end")
    else:
        print(text)


# ------------------------------------------------
# GUI 進度條安全更新
# ------------------------------------------------
def gui_progress_step(progress, step=1):
    """
    安全更新進度條
    """
    if progress:
        try:
            progress.step(step)
        except:
            pass


# ------------------------------------------------
# 備份檔案
# ------------------------------------------------
def backup_file(path, console=None):
    """
    建立 .bak 備份
    """
    try:
        shutil.copy2(path, path + ".bak")
        gui_print(console, f"[Backup] 已備份 {os.path.basename(path)}")
    except Exception as e:
        gui_print(console, f"[ERROR] 備份失敗：{path} — {e}")


# ------------------------------------------------
# 遞迴掃描所有檔案
# ------------------------------------------------
def scan_files(folder, exts=None):
    """
    遞迴掃描資料夾，回傳所有符合副檔名的檔案
    exts = ["cfg", "tt", "ttp"]
    """
    results = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if exts is None:
                results.append(os.path.join(root, file))
            else:
                if any(file.lower().endswith(ext) for ext in exts):
                    results.append(os.path.join(root, file))

    return results


# ------------------------------------------------
# 計算總工作量（給進度條用）
# ------------------------------------------------
def count_total_tasks(ttdata_folder):
    """
    計算：
    - stnlink.cfg 數量
    - AIlist.cfg 數量
    - timetable (.tt / .ttp) 數量
    """
    stnlinks = scan_files(ttdata_folder, ["cfg"])
    stnlinks = [f for f in stnlinks if "stnlink" in os.path.basename(f).lower()]

    ailists = scan_files(ttdata_folder, ["cfg"])
    ailists = [f for f in ailists if "ailist" in os.path.basename(f).lower()]

    timetables = scan_files(ttdata_folder, ["tt", "ttp"])

    return len(stnlinks) + len(ailists) + len(timetables)


# ------------------------------------------------
# 讀取文字檔
# ------------------------------------------------
def read_text_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []


# ------------------------------------------------
# 寫入 log 檔案
# ------------------------------------------------
def write_log(path, log_text, console=None):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(log_text)
        gui_print(console, f"[Log] 已寫入 log：{path}")
    except Exception as e:
        gui_print(console, f"[ERROR] 無法寫入 log：{e}")
