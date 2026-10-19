import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# إعدادات الصفحة
st.set_page_config(page_title="Karim cash", page_icon="💰", layout="centered")

# تنسيقات CSS لتحسين المظهر
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
    }
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "budget_data.json"

def load_data():
    default_data = {
        "monthly_limit": 1000.0,
        "sava_amount": 200.0,
        "income_list": [],
        "commitments": [],
        "expenses": [],
        "debts_li": [],
        "debts_alei": [],
        "password": "123"
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # دمج البيانات مع البيانات الافتراضية لمنع KeyError عند تحديث الهيكل
                for key, val in default_data.items():
                    if key not in loaded:
                        loaded[key] = val
                return loaded
        except Exception:
            return default_data
    return default_data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# --- شاشة الأمان وقفل التطبيق ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 Karim cash</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6b7280;'>يرجى إدخال كلمة المرور للوصول إلى المحفظة</p>", unsafe_allow_html=True)
        entered_pass = st.text_input("كلمة المرور", type="password", placeholder="اكتب كلمة المرور...")
        if st.button("🔓 دخول", use_container_width=True):
            if entered_pass == data.get("password", "123"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة!")
    st.stop()

# --- القائمة الجانبية والأيقونات ---
st.sidebar.markdown("# 💰 Karim cash")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "القائمة الرئيسية:",
    [
        "📊 الملخص المالي والسيولة",
        "💵 إدارة الدخل",
        "📋 الالتزامات الثابتة",
        "🛒 المصاريف اليومية",
        "📥 الديون (لك / لي)",
        "📤 الديون (عليك)",
        "⚙️ الإعدادات والأمان"
    ]
)

# الحسابات الإجمالية آمنة باستخدام دالة .get() لتجنب أي KeyError
total_income = sum(item.get("المبلغ", 0.0) for item in data.get("income_list", [])) if data.get("income_list") else data.get("monthly_limit", 1000.0)
sava_amount = data.get("sava_amount", 200.0)
effective_limit = total_income - sava_amount

total_commitments = sum(item.get("المبلغ", 0.0) for item in data.get("commitments", [])) if data.get("commitments") else 0.0
total_expenses = sum(item.get("المبلغ", 0.0) for item in data.get("expenses", [])) if data.get("expenses") else 0.0
total_out = total_commitments + total_expenses
remaining_budget = effective_limit - total_out

# 📊 1. الملخص المالي والسيولة
if menu == "📊 الملخص المالي والسيولة":
    st.title("📊 لوحة المؤشرات المالية")
    st.markdown("نظرة شاملة ومحدثة لمصاريفك وميزانيتك.")
    
    col1, col2 = st.columns(2)
    col1.metric("🎯 المتبقي الفعلي للصرف", f"{remaining_budget:,.2f} ر.س")
    col2.metric("🛡️ مستقطع Sava (الادخار)", f"{sava_amount:,.2f} ر.س")
    
    st.write("")
    col3, col4, col5 = st.columns(3)
    col3.metric("💰 إجمالي الدخل", f"{total_income:,.2f} ر.س")
    col4.metric("📋 الالتزامات", f"{total_commitments:,.2f} ر.س")
    col5.metric("🛒 المصاريف اليومية", f"{total_expenses:,.2f} ر.س")
    
    st.markdown("---")
    st.markdown("### 📈 مؤشر استهلاك الميزانية")
    progress = min(max(total_out / effective_limit if effective_limit > 0 else 1.0, 0.0), 1.0)
    st.progress(progress, text=f"تم استهلاك {progress*100:.1f}% من المتبقي الفعلي")

# 💵 2. إدارة الدخل
elif menu == "💵 إدارة الدخل":
    st.title("💵 إدارة الدخل الأساسي والإضافي")
    with st.form("income_form", clear_on_submit=True):
        inc_title = st.text_input("📌 مصدر الدخل (مثال: راتب، مكافأة...)")
        inc_amount = st.number_input("💵 المبلغ (ريال)", min_value=0.1, step=10.0)
        if st.form_submit_button("➕ إضافة الدخل", use_container_width=True):
            if inc_title:
                data["income_list"].append({"التاريخ": datetime.today().strftime("%Y-%m-%d"), "البند": inc_title, "المبلغ": inc_amount})
                save_data(data)
                st.success("✨ تمت إضافة الدخل بنجاح!")
                st.rerun()
            
    st.markdown("### 📜 السجل المالي للدخل")
    if data.get("income_list"):
        st.dataframe(pd.DataFrame(data["income_list"]), use_container_width=True)
        if st.button("🗑️ حذف آخر دخل مسجل"):
            data["income_list"].pop()
            save_data(data)
            st.rerun()
    else:
        st.info("ℹ️ الميزانية الأساسية المعتمدة هي 1000 ريال (يمكنك إضافة مبالغ أخرى فوقها).")

# 📋 3. الالتزامات الثابتة
elif menu == "📋 الالتزامات الثابتة":
    st.title("📋 الالتزامات والفواتير الثابتة")
    with st.form("commitment_form", clear_on_submit=True):
        com_title = st.text_input("📌 وصف الالتزام (مثال: فاتورة جوال، إيجار...)")
        com_amount = st.number_input("💵 المبلغ (ريال)", min_value=0.1, step=1.0)
        if st.form_submit_button("➕ إضافة التزام", use_container_width=True):
            if com_title:
                data["commitments"].append({"التاريخ": datetime.today().strftime("%Y-%m-%d"), "البند": com_title, "المبلغ": com_amount})
                save_data(data)
                st.success("✨ تمت إضافة الالتزام بنجاح!")
                st.rerun()
            
    st.markdown("### 📜 سجل الالتزامات")
    if data.get("commitments"):
        st.dataframe(pd.DataFrame(data["commitments"]), use_container_width=True)
        if st.button("🗑️ حذف آخر التزام مسجل"):
            data["commitments"].pop()
            save_data(data)
            st.rerun()
    else:
        st.info("ℹ️ لا توجد التزامات مسجلة حالياً.")

# 🛒 4. المصاريف اليومية
elif menu == "🛒 المصاريف اليومية":
    st.title("🛒 المصاريف اليومية")
    with st.form("expense_form", clear_on
