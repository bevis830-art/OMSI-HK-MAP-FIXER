# ============================================
# fix_ttdata_gui.py
# HK Map TTData Auto-Rebuilder — GUI 主程式
# ============================================

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

from ttdata_core import run_full_rebuild


# ------------------------------------------------
# GUI 主框架
# ------------------------------------------------
class TTDataFixerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HK Map TTData Auto-Rebuilder (Professional Edition)")
        self.root.geometry("1200x750")

        # Light Mode 主題
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff")
        style.configure("TButton", padding=6)
        style.configure("TProgressbar", thickness=20)

        # Notebook（多頁籤）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # 建立各頁籤
        self.create_main_tab()
        self.create_stnlink_tab()
        self.create_timetable_tab()
        self.create_ailist_tab()
        self.create_log_tab()

        # 修復器狀態
        self.ttdata_path = None
        self.is_running = False

    # ------------------------------------------------
    # Tab 1：主頁（修復工具）
    # ------------------------------------------------
    def create_main_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="TTData 修復")

        # 選擇資料夾按鈕
        self.btn_select = ttk.Button(tab, text="選擇 TTData 資料夾", command=self.select_folder)
        self.btn_select.pack(pady=10)

        # 顯示選擇的路徑
        self.lbl_path = ttk.Label(tab, text="尚未選擇資料夾")
        self.lbl_path.pack(pady=5)

        # 開始修復按鈕
        self.btn_start = ttk.Button(tab, text="開始修復", command=self.start_fix)
        self.btn_start.pack(pady=10)

        # 進度條
        self.progress = ttk.Progressbar(tab, length=600, mode="determinate")
        self.progress.pack(pady=20)

        # Console 輸出框
        self.console = scrolledtext.ScrolledText(tab, height=20, width=140, bg="#ffffff")
        self.console.pack(pady=10)

    # ------------------------------------------------
    # Tab 2：StnLink Viewer
    # ------------------------------------------------
    def create_stnlink_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="StnLink Viewer")

        self.stnlink_text = scrolledtext.ScrolledText(tab, height=30, width=140)
        self.stnlink_text.pack(fill="both", expand=True)

    # ------------------------------------------------
    # Tab 3：Timetable Viewer
    # ------------------------------------------------
    def create_timetable_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Timetable Viewer")

        self.timetable_text = scrolledtext.ScrolledText(tab, height=30, width=140)
        self.timetable_text.pack(fill="both", expand=True)

    # ------------------------------------------------
    # Tab 4：AIlist Viewer
    # ------------------------------------------------
    def create_ailist_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="AIlist Viewer")

        self.ailist_text = scrolledtext.ScrolledText(tab, height=30, width=140)
        self.ailist_text.pack(fill="both", expand=True)

    # ------------------------------------------------
    # Tab 5：Log Viewer
    # ------------------------------------------------
    def create_log_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Log Viewer")

        self.log_text = scrolledtext.ScrolledText(tab, height=30, width=140)
        self.log_text.pack(fill="both", expand=True)

    # ------------------------------------------------
    # 選擇資料夾
    # ------------------------------------------------
    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.ttdata_path = path
            self.lbl_path.config(text=f"已選擇：{path}")

    # ------------------------------------------------
    # 開始修復（多執行緒）
    # ------------------------------------------------
    def start_fix(self):
        if not self.ttdata_path:
            self.console.insert("end", "請先選擇 TTData 資料夾\n")
            return

        if self.is_running:
            return

        self.is_running = True
        self.progress["value"] = 0
        self.console.insert("end", "開始修復...\n")

        thread = threading.Thread(target=self.run_fix)
        thread.start()

    # ------------------------------------------------
    # 執行修復（呼叫核心模組）
    # ------------------------------------------------
    def run_fix(self):
        run_full_rebuild(
            self.ttdata_path,
            console=self.console,
            progress=self.progress,
            log_viewer=self.log_text
        )

        self.console.insert("end", "修復完成！\n")
        self.is_running = False


# ------------------------------------------------
# 主程式入口
# ------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TTDataFixerGUI(root)
    root.mainloop()
