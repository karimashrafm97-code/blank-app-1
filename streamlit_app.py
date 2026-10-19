import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# إعدادات الصفحة المخصصة للجوال
st.set_page_config(page_title="Karim cash", page_icon="💰", layout="centered", initial_sidebar_state="expanded")

# تنسيقات CSS احترافية ومناسبة للهواتف الذكية
st.markdown("""
    <style>
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eaedf1;
    }
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        height: 2.8rem;
    }
    .welcome-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
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
        "password": "123",
        "language": "AR"
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
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

# --- اختيار اللغة (Language Selection) ---
if "lang" not in st.session_state:
    st.session_state.lang = data.get("language", "AR")

# القواميس النصية للثنائية اللغوية (Arabic & English Dicts)
TEXTS = {
    "AR": {
        "welcome": "مرحباً كريم 👋",
        "lock_msg": "Karim cash - يرجى تأكيد الهوية للدخول",
        "pass_label": "كلمة المرور",
        "login_btn": "🔓 دخول بكلمة المرور",
        "bio_btn": "👤 الدخول عبر بصمة الوجه / الإصبع",
        "wrong_pass": "❌ كلمة المرور غير صحيحة!",
        "menu_title": "القائمة الرئيسية",
        "m_dash": "📊 لوحة التحكم والتحليل",
        "m_inc": "💵 إدارة الدخل",
        "m_com": "📋 الالتزامات الثابتة",
        "m_exp": "🛒 المصاريف اليومية",
        "m_dli": "📥 الديون (لك / لي)",
        "m_dalei": "📤 الديون (عليك)",
        "m_set": "⚙️ الإعدادات والأمان",
        "filter_label": "📅 اختر الفترة الزمنية للتحليل:",
        "f_month": "شهري (Monthly)",
        "f_q": "ربع سنوي (Quarterly)",
        "f_half": "نصف سنوي (Semi-Annual)",
        "f_year": "سنوي (Annual)",
        "f_all": "كل الفترات (All Time)",
        "rem_budget": "🎯 المتبقي الفعلي",
        "sava_saved": "🛡️ مستقطع Sava",
        "total_inc": "💰 إجمالي الدخل",
        "total_com": "📋 الالتزامات",
        "total_exp": "🛒 المصاريف",
        "progress_text": "نسبة الاستهلاك من المتبقي الفعلي",
        "add_btn": "➕ إضافة",
        "delete_btn": "🗑️ حذف السجل الأخير",
        "amount": "المبلغ (ريال)",
        "item_desc": "الوصف / البند",
        "person": "اسم الشخص / الدائن",
        "status": "الحالة",
        "notes": "ملاحظات",
        "toggle_status": "🔄 تغيير الحالة (تم السداد / مستحق)"
    },
    "EN": {
        "welcome": "Welcome Karim 👋",
        "lock_msg": "Karim cash - Please authenticate to enter",
        "pass_label": "Password",
        "login_btn": "🔓 Login with Password",
        "bio_btn": "👤 Sign in with Face ID / Touch ID",
        "wrong_pass": "❌ Incorrect Password!",
        "menu_title": "Main Menu",
        "m_dash": "📊 Dashboard & Analytics",
        "m_inc": "💵 Income Management",
        "m_com": "📋 Fixed Commitments",
        "m_exp": "🛒 Daily Expenses",
        "m_dli": "📥 Debts (Owed to You)",
        "m_dalei": "📤 Debts (You Owe)",
        "m_set": "⚙️ Settings & Security",
        "filter_label": "📅 Select Time Period:",
        "f_month": "Monthly",
        "f_q": "Quarterly",
        "f_half": "Semi-Annual",
        "f_year": "Annual",
        "f_all": "All Time",
        "rem_budget": "🎯 Effective Remaining",
        "sava_saved": "🛡️ Sava Savings",
        "total_inc": "💰 Total Income",
        "total_com": "📋 Commitments",
        "total_exp": "🛒 Expenses",
        "progress_text": "Spent ratio of effective limit",
        "add_btn": "➕ Add",
        "delete_btn": "🗑️ Delete Last Record",
        "amount": "Amount (SAR)",
        "item_desc": "Description / Item",
        "person": "Person / Creditor Name",
        "status": "Status",
        "notes": "Notes",
        "toggle_status": "🔄 Toggle Status (Paid / Pending)"
    }
}

t = TEXTS[st.session_state.lang]

# --- شاشة قفل التطبيق وبصمة الوجه ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div class="welcome-card">
                <h2>{t['welcome']}</h2>
                <p style="margin:0;">Karim cash</p>
            </div>
        """, unsafe_allow_html=True)
        
        entered_pass = st.text_input(t["pass_label"], type="password")
        if st.button
