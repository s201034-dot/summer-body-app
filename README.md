import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime


class SummerHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Summer Body - 夏季體態強化中心")
        self.root.geometry("550x800")

        # --- 夏季視覺配色 ---
        self.COLOR_OCEAN = "#0077be"  # 海洋藍
        self.COLOR_SAND = "#f4a460"  # 沙灘金
        self.COLOR_ICE = "#f0f8ff"  # 冰雪藍

        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.COLOR_ICE)
        self.style.configure("TLabel", background=self.COLOR_ICE, font=("Microsoft JhengHei", 10))
        self.style.configure("Header.TLabel", background=self.COLOR_ICE, font=("Microsoft JhengHei", 18, "bold"),
                             foreground=self.COLOR_OCEAN)

        # --- 數據表格 ---
        self.ACTIVITY_LEVELS = {
            "久坐 (室內吹冷氣)": 1.2,
            "輕量 (偶爾散步)": 1.375,
            "中度 (每週運動3-5次)": 1.55,
            "高度 (戶外高強度運動)": 1.725
        }

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        # 1. 夏季標題與倒數
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(header_frame, text="🌊 Summer Enhancement", style="Header.TLabel").pack()

        # 倒數計時 (假設目標是 6月21日 夏至)
        summer_start = datetime(2026, 6, 21)
        days_left = (summer_start - datetime.now()).days
        self.countdown_lbl = ttk.Label(header_frame, text=f"距離夏至目標還有: {days_left} 天 ☀️", foreground="#d35400")
        self.countdown_lbl.pack()

        # 2. 輸入區
        input_grid = ttk.LabelFrame(main_frame, text=" 你的身體數據 ", padding="15")
        input_grid.pack(fill="x", pady=10)

        fields = [("年齡", "age"), ("性別 (1=男, 0=女)", "gender"), ("身高 (cm)", "height"), ("體重 (kg)", "weight")]
        self.entries = {}

        for i, (label, key) in enumerate(fields):
            ttk.Label(input_grid, text=label).grid(row=i, column=0, sticky="w", pady=5)
            ent = ttk.Entry(input_grid)
            ent.grid(row=i, column=1, sticky="ew", padx=(10, 0))
            self.entries[key] = ent

        ttk.Label(input_grid, text="夏季活動量:").grid(row=4, column=0, sticky="w", pady=5)
        self.act_box = ttk.Combobox(input_grid, values=list(self.ACTIVITY_LEVELS.keys()), state="readonly")
        self.act_box.current(0)
        self.act_box.grid(row=4, column=1, sticky="ew", padx=(10, 0))

        # 3. 功能按鈕
        self.calc_btn = tk.Button(main_frame, text="計算夏季塑身建議", command=self.calculate,
                                  bg=self.COLOR_OCEAN, fg="white", font=("Microsoft JhengHei", 12, "bold"),
                                  relief="flat")
        self.calc_btn.pack(fill="x", pady=15)

        # 4. 結果顯示區 (含補水)
        self.result_area = tk.Text(main_frame, height=18, font=("Consolas", 10), state="disabled", bg="white",
                                   relief="flat")
        self.result_area.pack(fill="both", expand=True)

    def calculate(self):
        try:
            age = int(self.entries['age'].get())
            gen = int(self.entries['gender'].get())
            h = float(self.entries['height'].get())
            w = float(self.entries['weight'].get())
            mult = self.ACTIVITY_LEVELS[self.act_box.get()]

            # 計算
            bmi = w / ((h / 100) ** 2)
            bmr = (10 * w) + (6.25 * h) - (5 * age) + (5 if gen == 1 else -161)
            tdee = bmr * mult

            # --- 夏季強化計算 ---
            water_need = w * 40  # 夏季高標補水
            beach_ready_cal = tdee - 500  # 溫和減脂熱量

            report = (
                f"--- 夏季塑身報告 ---\n"
                f"【基礎指標】\n"
                f"BMI: {bmi:.2f}\n"
                f"基礎代謝 BMR: {bmr:.0f} kcal\n"
                f"日常消耗 TDEE: {tdee:.0f} kcal\n\n"
                f"【夏季專屬建議】\n"
                f"💧 每日建議飲水量: {water_need:.0f} ml\n"
                f"🔥 夏季塑身目標熱量: {beach_ready_cal:.0f} kcal\n\n"
                f"【營養配比建議】\n"
                f"蛋白質 (保持肌肉): {(w * 1.8):.1f} g\n"
                f"脂肪: {(beach_ready_cal * 0.25 / 9):.1f} g\n"
                f"碳水: {(beach_ready_cal * 0.45 / 4):.1f} g\n"
                f"--------------------\n"
                f"Tips: 夏天戶外運動請注意避開 10am-2pm 高溫時段！"
            )

            self.result_area.config(state="normal")
            self.result_area.delete("1.0", tk.END)
            self.result_area.insert(tk.END, report)
            self.result_area.config(state="disabled")

        except Exception:
            messagebox.showerror("Oops!", "請確保輸入的資料是正確的數字哦！")


if __name__ == "__main__":
    root = tk.Tk()
    app = SummerHealthApp(root)
    root.mainloop()
