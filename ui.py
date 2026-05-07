import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import os

from signature import (
    fast_mod_exp, gcd, mod_inverse, is_prime,
    text_to_nums, compute_hash
)


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TI_Lab_4")
        self.root.geometry("420x550")
        self.root.resizable(False, False)
        self._center_window()
        self.vcmd = (self.root.register(self._validate_digits), '%P')

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.frame_sign = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_sign, text="1. Подписание")
        self._init_sign_tab()

        self.frame_verify = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_verify, text="2. Проверка подписи")
        self._init_verify_tab()

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _validate_digits(self, new_value):
        return new_value == "" or new_value.isdigit()

    def _init_sign_tab(self):
        ttk.Label(self.frame_sign, text="Параметры закрытого ключа:").pack(anchor="w", pady=(0, 5))

        ttk.Label(self.frame_sign, text="Простое число p:").pack(anchor="w")
        self.entry_p = ttk.Entry(self.frame_sign, width=25, validate="key", validatecommand=self.vcmd)
        self.entry_p.pack(anchor="w", pady=2)

        ttk.Label(self.frame_sign, text="Простое число q:").pack(anchor="w")
        self.entry_q = ttk.Entry(self.frame_sign, width=25, validate="key", validatecommand=self.vcmd)
        self.entry_q.pack(anchor="w", pady=2)

        ttk.Label(self.frame_sign, text="Закрытая экспонента d:").pack(anchor="w")
        self.entry_d = ttk.Entry(self.frame_sign, width=25, validate="key", validatecommand=self.vcmd)
        self.entry_d.pack(anchor="w", pady=5)

        ttk.Button(self.frame_sign, text="Подписать файл", command=self.sign_file).pack(pady=10)

        ttk.Separator(self.frame_sign, orient='horizontal').pack(fill='x', pady=10)

        ttk.Label(self.frame_sign, text="Результаты вычислений", font=("Helvetica", 10, "bold")).pack(anchor="center")

        self.lbl_pub_key = ttk.Label(self.frame_sign, text="Открытый ключ (e, r): ", foreground="blue", font=("Helvetica", 10, "bold"))
        self.lbl_pub_key.pack(anchor="w", pady=2)

        self.lbl_hash = ttk.Label(self.frame_sign, text="Хеш сообщения: ", foreground="red", font=("Helvetica", 10, "bold"))
        self.lbl_hash.pack(anchor="w", pady=2)

        self.lbl_sig = ttk.Label(self.frame_sign, text="Цифровая подпись: ", foreground="darkgreen", font=("Helvetica", 10, "bold"))
        self.lbl_sig.pack(anchor="w", pady=2)

        ttk.Label(self.frame_sign, text="Формулы вычислений:").pack(anchor="w", pady=(10, 2))
        self.txt_formulas = tk.Text(self.frame_sign, height=10, width=55, state="disabled", font=("Courier New", 9))
        self.txt_formulas.pack(padx=5, pady=5)

    def _init_verify_tab(self):
        ttk.Label(self.frame_verify, text="Параметры открытого ключа:").pack(anchor="w", pady=(0, 5))

        ttk.Label(self.frame_verify, text="Открытая экспонента e:").pack(anchor="w")
        self.entry_e = ttk.Entry(self.frame_verify, width=25, validate="key", validatecommand=self.vcmd)
        self.entry_e.pack(anchor="w", pady=2)

        ttk.Label(self.frame_verify, text="Модуль r:").pack(anchor="w")
        self.entry_r = ttk.Entry(self.frame_verify, width=25, validate="key", validatecommand=self.vcmd)
        self.entry_r.pack(anchor="w", pady=5)

        ttk.Button(self.frame_verify, text="Проверить ЭЦП", command=self.verify_file).pack(pady=10)

        ttk.Separator(self.frame_verify, orient='horizontal').pack(fill='x', pady=10)

        self.txt_verify = tk.Text(self.frame_verify, height=20, width=55, state="disabled")
        self.txt_verify.pack(padx=5, pady=5)

    def _parse_sign_params(self):
        try:
            p = int(self.entry_p.get())
            q = int(self.entry_q.get())
            d = int(self.entry_d.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Параметры p, q, d должны быть целыми числами.")
            return None

        if not (is_prime(p) and is_prime(q)):
            messagebox.showerror("Ошибка", "p и q должны быть простыми числами.")
            return None
        if p == q:
            messagebox.showerror("Ошибка", "p и q должны быть различными.")
            return None

        r = p * q
        phi_r = (p - 1) * (q - 1)

        if not (1 < d < phi_r):
            messagebox.showerror("Ошибка", f"d должен быть в диапазоне (1, {phi_r}).")
            return None
        if gcd(d, phi_r) != 1:
            messagebox.showerror("Ошибка", "НОД(d, φ(r)) != 1. Выберите другое d.")
            return None
        e = mod_inverse(d, phi_r)
        return p, q, r, d, e, phi_r

    def sign_file(self):
        res = self._parse_sign_params()
        if not res: return

        p, q, r, d, e, phi_r = res

        self.lbl_pub_key.config(text=f"Открытый ключ (e, r): e = {e},  r = {r}")

        file_path = filedialog.askopenfilename(title="Выберите файл для подписи", filetypes=[("Text Files", "*.txt")])
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as ex:
            messagebox.showerror("Ошибка", str(ex))
            return

        content = content.rstrip('\r\n')
        nums = text_to_nums(content)

        hash_val = compute_hash(nums, r)
        self.lbl_hash.config(text=f"Хеш сообщения: {hash_val}")

        signature = fast_mod_exp(hash_val, d, r)
        self.lbl_sig.config(text=f"Цифровая подпись: {signature}")

        self.txt_formulas.config(state="normal")
        self.txt_formulas.delete(1.0, tk.END)
        self.txt_formulas.insert(tk.END, f"φ(r) = ({p}-1)*({q}-1) = {phi_r}\n\n")
        self.txt_formulas.insert(tk.END, f"H0 = 100\n")
        self.txt_formulas.insert(tk.END, f"Хеш h(M) = {hash_val}\n\n")
        self.txt_formulas.insert(tk.END, f"S = h(M)^d mod r\n")
        self.txt_formulas.insert(tk.END, f"S = {hash_val}^{d} mod {r}\n")
        self.txt_formulas.insert(tk.END, f"S = {signature}")
        self.txt_formulas.config(state="disabled")

        out_path = os.path.splitext(file_path)[0] + "_signed.txt"
        with open(out_path, 'w', encoding='utf-8') as f:
            if content:
                f.write(content)
            f.write(f"\n{signature}")

        messagebox.showinfo("Успех", f"Файл подписан.\nОткрытый ключ: e={e}, r={r}\nСохранен в: {out_path}")

    def verify_file(self):
        try:
            e = int(self.entry_e.get())
            r = int(self.entry_r.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Параметры e и r должны быть целыми числами.")
            return

        if r <= 1 or e < 1:
            messagebox.showerror("Ошибка", "Параметры должны быть положительными.")
            return

        file_path = filedialog.askopenfilename(title="Выберите файл для проверки", filetypes=[("Text Files", "*.txt")])
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as ex:
            messagebox.showerror("Ошибка", str(ex))
            return

        if '\n' not in content:
            messagebox.showerror("Ошибка формата",
                                 "Файл не содержит подписи (должен быть перенос строки перед подписью).")
            return

        text_part, sig_str = content.rsplit('\n', 1)
        text_part = text_part.rstrip('\r\n')

        try:
            sig = int(sig_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Подпись не является числом.")
            return

        nums = text_to_nums(text_part)
        computed_hash = compute_hash(nums, r)
        recovered_hash = fast_mod_exp(sig, e, r)

        self.txt_verify.config(state="normal")
        self.txt_verify.delete(1.0, tk.END)
        self.txt_verify.insert(tk.END, "- Параметры проверки\n")
        self.txt_verify.insert(tk.END, f"Используемая экспонента e: {e}\n")
        self.txt_verify.insert(tk.END, f"Используемый модуль r: {r}\n\n")
        self.txt_verify.insert(tk.END, f"Подпись S: {sig}\n\n")
        self.txt_verify.insert(tk.END, "- Хеш-значения\n")
        self.txt_verify.insert(tk.END, f"1. Вычисленный хеш (m'): {computed_hash}\n")
        self.txt_verify.insert(tk.END, f"2. Восстановленный хеш (m): {recovered_hash}\n\n")

        if computed_hash == recovered_hash:
            self.txt_verify.insert(tk.END, "РЕЗУЛЬТАТ: Подпись ВЕРНА.\nХеши совпадают (m' = m).")
            messagebox.showinfo("Проверка", "Подпись ВЕРНА.\nХеши совпадают (m' = m).")
        else:
            self.txt_verify.insert(tk.END, "РЕЗУЛЬТАТ: Подпись НЕВЕРНА.\nХеш, вычисленный из полученного файла (m'), не совпадает с хешем, восстановленным из подписи (m).\n")
            messagebox.showwarning("Проверка", "Подпись НЕВЕРНА.\nХеш, вычисленный из полученного файла (m'), не совпадает с хешем, восстановленным из подписи (m).")

        self.txt_verify.config(state="disabled")