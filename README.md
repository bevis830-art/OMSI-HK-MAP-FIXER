# HK Map TTData Auto‑Rebuilder  
### Professional Edition · GUI + Multi‑Module + Auto Repair Tool  
Created by Bevis

---

## 📌 Overview

**HK Map TTData Auto‑Rebuilder** 是一款專為 **OMSI 2 香港地圖（HK Map）** 設計的  
**全自動 TTData 修復工具**。

它能自動修復：

- `stnlink.cfg`（站點連結）
- `AIlist.cfg`（AI 車輛路線）
- `*.tt / *.ttp`（時刻表）
- `stops.txt / tracks.txt`（站點與路軌索引）

並提供：

- ✔ **多頁籤 GUI（Notebook）**
- ✔ **Light Mode（Windows 原生風格）**
- ✔ **不可取消進度條（安全模式）**
- ✔ **Console 即時輸出**
- ✔ **StnLink / Timetable / AIlist / Log Viewer**
- ✔ **自動備份 .bak**
- ✔ **自動生成缺失 timetable**
- ✔ **自動修復 StopID / TrackID / SplineID**
- ✔ **自動重建站點序列、距離欄位、seq 欄位**

這是一個專業級的 HK Map TTData 修復工具。

---

## 📁 Folder Structure

---

## 🚀 How to Run

### **1. 安裝 Python 3.8+**
建議使用：

- Python 3.8 ~ 3.12  
- Windows 10 / 11

### **2. 安裝必要套件（標準庫即可）**
本工具 **不需要任何額外套件**，完全使用 Python 內建模組。

### **3. 執行 GUI 主程式**

```bash
python fix_ttdata_gui.py
