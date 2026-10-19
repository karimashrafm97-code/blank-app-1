
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date

DATA_FILE = "mizanati_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(transactions, file, ensure_ascii=False, indent=2)


transactions = load_data()


def refresh():
    for item in table.get_children():
        table.delete(item)

    income = 0
    expenses = 0

    for t in transactions:
        amount = t["amount"]
        if t["type"] == "دخل":
            income += amount
        else:
            expenses += amount

        table.insert(
            "", "end",
            values=(t["date"], t["type"], t["title"],
                    f'{amount:,.2f} ر.س')
        )

    income_label.config(text=f"إجمالي الدخل: {income:,.2f} ر.س")
    expense_label.config(text=f"إجمالي المصروفات: {expenses:,.2f} ر.س")
    balance_label.config(
        text=f"الرصيد المتبقي: {income - expenses:,.2f} ر.س"
    )


def add_transaction():
    title = title_entry.get().strip()
    amount_text = amount_entry.get().strip()
    kind = type_box.get()

    if not title:
        messagebox.showerror("خطأ", "أدخل اسم العملية")
        return

    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("خطأ", "أدخل مبلغًا صحيحًا أكبر من صفر")
        return

    transactions.append({
        "date": date_entry.get().strip() or date.today().isoformat(),
        "type": kind,
        "title": title,
        "amount": amount
    })

    save_data()
    title_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    refresh()


root = tk.Tk()
root.title("ميزانيتي | إدارة الأموال")
root.geometry("760x560")
root.configure(bg="#f2f5f3")

style = ttk.Style()
style.configure("Treeview", rowheight=30, font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

tk.Label(
    root, text="ميزانيتي", font=("Arial", 24, "bold"),
    bg="#f2f5f3", fg="#176b4d"
).pack(pady=12)

form = tk.Frame(root, bg="#f2f5f3")
form.pack(pady=5)

tk.Label(form, text="اسم العملية", bg="#f2f5f3").grid(row=0, column=0, padx=5)
title_entry = tk.Entry(form, width=20, justify="right")
title_entry.grid(row=0, column=1, padx=5)

tk.Label(form, text="المبلغ (ر.س)", bg="#f2f5f3").grid(row=0, column=2, padx=5)
amount_entry = tk.Entry(form, width=12)
amount_entry.grid(row=0, column=3, padx=5)

tk.Label(form, text="النوع", bg="#f2f5f3").grid(row=1, column=0, padx=5, pady=10)
type_box = ttk.Combobox(
    form, values=["دخل", "مصروف"], state="readonly", width=10
)
type_box.set("مصروف")
type_box.grid(row=1, column=1, sticky="w")

tk.Label(form, text="التاريخ", bg="#f2f5f3").grid(row=1, column=2, padx=5)
date_entry = tk.Entry(form, width=12)
date_entry.insert(0, date.today().isoformat())
date_entry.grid(row=1, column=3, padx=5)

tk.Button(
    root, text="إضافة العملية", command=add_transaction,
    bg="#176b4d", fg="white", font=("Arial", 11, "bold"),
    padx=20, pady=5
).pack(pady=10)

summary = tk.Frame(root, bg="#f2f5f3")
summary.pack(pady=5)

income_label = tk.Label(summary, bg="#f2f5f3", fg="#176b4d", font=("Arial", 11))
income_label.pack(side="right", padx=12)

expense_label = tk.Label(summary, bg="#f2f5f3", fg="#b33a3a", font=("Arial", 11))
expense_label.pack(side="right", padx=12)

balance_label = tk.Label(summary, bg="#f2f5f3", font=("Arial", 11, "bold"))
balance_label.pack(side="right", padx=12)

columns = ("date", "type", "title", "amount")
table = ttk.Treeview(root, columns=columns, show="headings")

for col, label in zip(columns, ["التاريخ", "النوع", "العملية", "المبلغ"]):
    table.heading(col, text=label)
    table.column(col, anchor="center", width=160)

table.pack(fill="both", expand=True, padx=15, pady=15)

refresh()
root.mainloop()

