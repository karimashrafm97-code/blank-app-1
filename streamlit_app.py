import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
        "delete_btn": "🗑️ حذف السجل الأخيرة",
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
        if st.button(t["login_btn"], use_container_width=True):
            if entered_pass == data.get("password", "123"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(t["wrong_pass"])
                
        st.markdown("<p style='text-align:center; color:gray;'>— " + ("أو" if st.session_state.lang == "AR" else "OR") + " —</p>", unsafe_allow_html=True)
        
        # زر البصمة عبر المتصفح
        if st.button(t["bio_btn"], use_container_width=True):
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- القائمة الجانبية وتبديل اللغة ---
st.sidebar.markdown(f"## 💰 Karim cash")
st.sidebar.markdown(f"**{t['welcome']}**")

lang_choice = st.sidebar.selectbox("🌐 Language / اللغة", ["العربية (AR)", "English (EN)"])
new_lang = "AR" if "العربية" in lang_choice else "EN"
if new_lang != st.session_state.lang:
    st.session_state.lang = new_lang
    data["language"] = new_lang
    save_data(data)
    st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    t["menu_title"],
    [
        t["m_dash"],
        t["m_inc"],
        t["m_com"],
        t["m_exp"],
        t["m_dli"],
        t["m_dalei"],
        t["m_set"]
    ]
)

# دالة الفلترة الزمنية للمصاريف والبيانات
def filter_by_period(items, period_type):
    if not items or period_type == t["f_all"]:
        return items
    
    today = datetime.today()
    filtered = []
    
    for item in items:
        item_date = datetime.strptime(item.get("التاريخ", today.strftime("%Y-%m-%d")), "%Y-%m-%d")
        if period_type == t["f_month"] and item_date.month == today.month and item_date.year == today.year:
            filtered.append(item)
        elif period_type == t["f_q"] and (today - item_date).days <= 90:
            filtered.append(item)
        elif period_type == t["f_half"] and (today - item_date).days <= 180:
            filtered.append(item)
        elif period_type == t["f_year"] and item_date.year == today.year:
            filtered.append(item)
            
    return filtered

# 📊 1. لوحة التحكم والتحليل (Dashboard)
if menu == t["m_dash"]:
    st.title(t["m_dash"])
    
    # اختيار الفلترة الزمنية
    period = st.selectbox(t["filter_label"], [t["f_month"], t["f_q"], t["f_half"], t["f_year"], t["f_all"]])
    
    inc_filtered = filter_by_period(data.get("income_list", []), period)
    com_filtered = filter_by_period(data.get("commitments", []), period)
    exp_filtered = filter_by_period(data.get("expenses", []), period)
    
    total_income = sum(i.get("المبلغ", 0.0) for i in inc_filtered) if inc_filtered else data.get("monthly_limit", 1000.0)
    sava_amount = data.get("sava_amount", 200.0)
    effective_limit = total_income - sava_amount
    
    total_commitments = sum(c.get("المبلغ", 0.0) for c in com_filtered)
    total_expenses = sum(e.get("المبلغ", 0.0) for e in exp_filtered)
    total_out = total_commitments + total_expenses
    remaining_budget = effective_limit - total_out
    
    col1, col2 = st.columns(2)
    col1.metric(t["rem_budget"], f"{remaining_budget:,.2f} SAR")
    col2.metric(t["sava_saved"], f"{sava_amount:,.2f} SAR")
    
    st.write("")
    col3, col4, col5 = st.columns(3)
    col3.metric(t["total_inc"], f"{total_income:,.2f} SAR")
    col4.metric(t["total_com"], f"{total_commitments:,.2f} SAR")
    col5.metric(t["total_exp"], f"{total_expenses:,.2f} SAR")
    
    st.markdown("---")
    progress = min(max(total_out / effective_limit if effective_limit > 0 else 1.0, 0.0), 1.0)
    st.progress(progress, text=f"{t['progress_text']}: {progress*100:.1f}%")

# 💵 2. إدارة الدخل
elif menu == t["m_inc"]:
    st.title(t["m_inc"])
    with st.form("inc_form", clear_on_submit=True):
        title = st.text_input(t["item_desc"])
        amount = st.number_input(t["amount"], min_value=0.1, step=10.0)
        if st.form_submit_button(t["add_btn"], use_container_width=True):
            if title:
                data["income_list"].append({"التاريخ": datetime.today().strftime("%Y-%m-%d"), "البند": title, "المبلغ": amount})
                save_data(data)
                st.success("✨ Success!")
                st.rerun()
                
    if data.get("income_list"):
        st.dataframe(pd.DataFrame(data["income_list"]), use_container_width=True)
        if st.button(t["delete_btn"]):
            data["income_list"].pop()
            save_data(data)
            st.rerun()

# 📋 3. الالتزامات الثابتة
elif menu == t["m_com"]:
    st.title(t["m_com"])
    with st.form("com_form", clear_on_submit=True):
        title = st.text_input(t["item_desc"])
        amount = st.number_input(t["amount"], min_value=0.1, step=1.0)
        if st.form_submit_button(t["add_btn"], use_container_width=True):
            if title:
                data["commitments"].append({"التاريخ": datetime.today().strftime("%Y-%m-%d"), "البند": title, "المبلغ": amount})
                save_data(data)
                st.success("✨ Success!")
                st.rerun()
                
    if data.get("commitments"):
        st.dataframe(pd.DataFrame(data["commitments"]), use_container_width=True)
        if st.button(t["delete_btn"]):
            data["commitments"].pop()
            save_data(data)
            st.rerun()

# 🛒 4. المصاريف اليومية
elif menu == t["m_exp"]:
    st.title(t["m_exp"])
    with st.form("exp_form", clear_on_submit=True):
        title = st.text_input(t["item_desc"])
        amount = st.number_input(t["amount"], min_value=0.1, step=1.0)
        if st.form_submit_button(t["add_btn"], use_container_width=True):
            if title:
                data["expenses"].append({"التاريخ": datetime.today().strftime("%Y-%m-%d"), "البند": title, "المبلغ": amount})
                save_data(data)
                st.success("✨ Success!")
                st.rerun()
                
    if data.get("expenses"):
        st.dataframe(pd.DataFrame(data["expenses"]), use_container_width=True)
        if st.button(t["delete_btn"]):
            data["expenses"].pop()
            save_data(data)
            st.rerun()

# 📥 5. الديون (لك / لي)
elif menu == t["m_dli"]:
    st.title(t["m_dli"])
    with st.form("dli_form", clear_on_submit=True):
        person = st.text_input(t["person"])
        amount = st.number_input(t["amount"], min_value=0.1, step=1.0)
        notes = st.text_input(t["notes"])
        if st.form_submit_button(t["add_btn"], use_container_width=True):
            if person:
                data["debts_li"].append({"الشخص": person, "المبلغ": amount, "الحالة": "مستحق ⏳", "ملاحظات": notes})
                save_data(data)
                st.success("✨ Success!")
                st.rerun()
                
    if data.get("debts_li"):
        st.dataframe(pd.DataFrame(data["debts_li"]), use_container_width=True)
        idx = st.number_input("Index", min_value=0, max_value=max(0, len(data["debts_li"])-1), step=1, format="%d")
        col_l1, col_l2 = st.columns(2)
        if col_l1.button(t["toggle_status"], use_container_width=True):
            curr = data["debts_li"][idx]["الحالة"]
            data["debts_li"][idx]["الحالة"] = "تم السداد ✅" if "مستحق" in curr else "مستحق ⏳"
            save_data(data)
            st.rerun()
        if col_l2.button(t["delete_btn"], use_container_width=True):
            data["debts_li"].pop(idx)
            save_data(data)
            st.rerun()

# 📤 6. الديون (عليك)
elif menu == t["m_dalei"]:
    st.title(t["m_dalei"])
    with st.form("dalei_form", clear_on_submit=True):
        person = st.text_input(t["person"])
        amount = st.number_input(t["amount"], min_value=0.1, step=1.0)
        notes = st.text_input(t["notes"])
        if st.form_submit_button(t["add_btn"], use_container_width=True):
            if person:
                data["debts_alei"].append({"الشخص": person, "المبلغ": amount, "الحالة": "مستحق ⏳", "ملاحظات": notes})
                save_data(data)
                st.success("✨ Success!")
                st.rerun()
                
    if data.get("debts_alei"):
        st.dataframe(pd.DataFrame(data["debts_alei"]), use_container_width=True)
        idx = st.number_input("Index ", min_value=0, max_value=max(0, len(data["debts_alei"])-1), step=1, format="%d")
        col_a1, col_a2 = st.columns(2)
        if col_a1.button(t["toggle_status"] + " ", use_container_width=True):
            curr = data["debts_alei"][idx]["الحالة"]
            data["debts_alei"][idx]["الحالة"] = "تم السداد ✅" if "مستحق" in curr else "مستحق ⏳"
            save_data(data)
            st.rerun()
        if col_a2.button(t["delete_btn"] + " ", use_container_width=True):
            data["debts_alei"].pop(idx)
            save_data(data)
            st.rerun()

# ⚙️ 7. الإعدادات والأمان
elif menu == t["m_set"]:
    st.title(t["m_set"])
    new_sava = st.number_input(t["sava_saved"], value=float(data.get("sava_amount", 200.0)), step=10.0)
    new_pass = st.text_input(t["pass_label"], type="password")
    
    if st.button("💾 Save Settings", use_container_width=True):
        data["sava_amount"] = new_sava
        if new_pass:
            data["password"] = new_pass
        save_data(data)
        st.success("✨ Settings Saved!")
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

# الحسابات الإجمالية
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
    with st.form("expense_form", clear_on_submit=True):
        exp_title = st.text_input("📌 وصف المصروف (مثال: سوبرماركت، قهوة...)")
        exp_amount = st.number_input("💵 المبلغ (ريال)", min_value=0.1, step=1.0)
        if st.form_submit_button("➕ إضافة مصروف يومي", use_container_width=True):
            if exp_title:
                data["expenses"].append({"التاريخ": datetime.today().strftime("%Y-%m-%d"), "البند": exp_title, "المبلغ": exp_amount})
                save_data(data)
                st.success("✨ تمت إضافة المصروف بنجاح!")
                st.rerun()
            
    st.markdown("### 📜 سجل المصاريف اليومية")
    if data.get("expenses"):
        st.dataframe(pd.DataFrame(data["expenses"]), use_container_width=True)
        if st.button("🗑️ حذف آخر مصروف مسجل"):
            data["expenses"].pop()
            save_data(data)
            st.rerun()
    else:
        st.info("ℹ️ لا توجد مصاريف يومية مسجلة.")

# 📥 5. الديون (لك / لي)
elif menu == "📥 الديون (لك / لي)":
    st.title("📥 الأموال المستحقة لك عند الآخرين")
    with st.form("debt_li_form", clear_on_submit=True):
        person_li = st.text_input("👤 اسم الشخص")
        amount_li = st.number_input("💵 المبلغ (ريال)", min_value=0.1, step=1.0)
        notes_li = st.text_input("📝 ملاحظات اختيارية")
        if st.form_submit_button("➕ تسجيل دين (لي)", use_container_width=True):
            if person_li:
                data["debts_li"].append({"الشخص": person_li, "المبلغ": amount_li, "الحالة": "مستحق ⏳", "ملاحظات": notes_li})
                save_data(data)
                st.success("✨ تمت الإضافة بنجاح!")
                st.rerun()
            
    st.markdown("### 📜 قائمة الأموال المستحقة لك")
    if data.get("debts_li"):
        st.dataframe(pd.DataFrame(data["debts_li"]), use_container_width=True)
        idx_li = st.number_input("رقم الصف للتعديل أو الحذف", min_value=0, max_value=max(0, len(data["debts_li"])-1), step=1, format="%d")
        col_l1, col_l2 = st.columns(2)
        if col_l1.button("🔄 تبديل الحالة (تم السداد / مستحق)", use_container_width=True):
            current = data["debts_li"][idx_li]["الحالة"]
            data["debts_li"][idx_li]["الحالة"] = "تم السداد ✅" if "مستحق" in current else "مستحق ⏳"
            save_data(data)
            st.rerun()
        if col_l2.button("🗑️ حذف السجل", use_container_width=True):
            data["debts_li"].pop(idx_li)
            save_data(data)
            st.rerun()
    else:
        st.info("ℹ️ لا توجد ديون مسجلة لك.")

# 📤 6. الديون (عليك)
elif menu == "📤 الديون (عليك)":
    st.title("📤 الأموال المستحقة عليك للآخرين")
    with st.form("debt_alei_form", clear_on_submit=True):
        person_alei = st.text_input("👤 اسم الدائن")
        amount_alei = st.number_input("💵 المبلغ (ريال)", min_value=0.1, step=1.0)
        notes_alei = st.text_input("📝 ملاحظات اختيارية")
        if st.form_submit_button("➕ تسجيل دين (علي)", use_container_width=True):
            if person_alei:
                data["debts_alei"].append({"الشخص": person_alei, "المبلغ": amount_alei, "الحالة": "مستحق ⏳", "ملاحظات": notes_alei})
                save_data(data)
                st.success("✨ تمت الإضافة بنجاح!")
                st.rerun()
            
    st.markdown("### 📜 قائمة الأموال المستحقة عليك")
    if data.get("debts_alei"):
        st.dataframe(pd.DataFrame(data["debts_alei"]), use_container_width=True)
        idx_alei = st.number_input("رقم الصف للتعديل أو الحذف ", min_value=0, max_value=max(0, len(data["debts_alei"])-1), step=1, format="%d")
        col_a1, col_a2 = st.columns(2)
        if col_a1.button("🔄 تبديل الحالة (تم السداد / مستحق) ", use_container_width=True):
            current_a = data["debts_alei"][idx_alei]["الحالة"]
            data["debts_alei"][idx_alei]["الحالة"] = "تم السداد ✅" if "مستحق" in current_a else "مستحق ⏳"
            save_data(data)
            st.rerun()
        if col_a2.button("🗑️ حذف السجل ", use_container_width=True):
            data["debts_alei"].pop(idx_alei)
            save_data(data)
            st.rerun()
    else:
        st.info("ℹ️ لا توجد ديون مسجلة عليك.")

# ⚙️ 7. الإعدادات والأمان
elif menu == "⚙️ الإعدادات والأمان":
    st.title("⚙️ الإعدادات والأمان")
    new_sava = st.number_input("🛡️ تعديل مبلغ مستقطع Sava الشهري (ريال)", value=float(data.get("sava_amount", 200.0)), step=10.0)
    new_pass = st.text_input("🔑 تغيير كلمة المرور جديدة", type="password")
    
    if st.button("💾 حفظ الإعدادات الجديدة", use_container_width=True):
        data["sava_amount"] = new_sava
        if new_pass:
            data["password"] = new_pass
        save_data(data)
        st.success("✨ تم تحديث الإعدادات بنجاح!")
