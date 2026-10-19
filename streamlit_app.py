import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# إعدادات الصفحة
st.set_page_config(page_title="Karim cash", page_icon="💰", layout="centered")

DATA_FILE = "budget_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "monthly_limit": 1000.0,
        "sava_amount": 200.0,
        "expenses": [],
        "debts": []
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.title("💰 Karim cash")
st.markdown("تطبيقك الذكي لتتبع مصروفاتك اليومية، التزاماتك، مستقطع **Sava**، والديون الخارجية بكل سهولة.")

# القائمة الجانبية للإعدادات السريعة
st.sidebar.header("⚙️ إعدادات الميزانية")
new_limit = st.sidebar.number_input("الحد الشهري الأساسي (ريال)", value=float(data["monthly_limit"]), step=50.0)
new_sava = st.sidebar.number_input("مستقطع Sava الشهري (ريال)", value=float(data["sava_amount"]), step=10.0)

if new_limit != data["monthly_limit"] or new_sava != data["sava_amount"]:
    data["monthly_limit"] = new_limit
    data["sava_amount"] = new_sava
    save_data(data)
    st.sidebar.success("تم تحديث الإعدادات بنجاح!")

# حساب المبالغ
monthly_limit = data["monthly_limit"]
sava_amount = data["sava_amount"]
effective_limit = monthly_limit - sava_amount

expenses_df = pd.DataFrame(data["expenses"])
total_expenses = expenses_df["المبلغ"].sum() if not expenses_df.empty else 0.0
remaining_budget = effective_limit - total_expenses

# التنقل بين الأقسام عبر علامات التبويب
tab1, tab2, tab3 = st.tabs(["📊 الملخص الشهري", "🛒 المصاريف والالتزامات", "🤝 الديون (لي وعلي)"])

with tab1:
    st.header("ملخص الميزانية")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("الحد الشهري", f"{monthly_limit:,.2f} ر.س")
    col2.metric("مستقطع Sava", f"{sava_amount:,.2f} ر.س")
    col3.metric("المتبقي الفعلي للصرف", f"{effective_limit:,.2f} ر.س")
    
    st.divider()
    
    col4, col5 = st.columns(2)
    col4.metric("إجمالي المصاريف المسجلة", f"{total_expenses:,.2f} ر.س")
    col5.metric("المتبقي النهائي", f"{remaining_budget:,.2f} ر.س")
    
    # شريط التقدم البصري
    progress = min(max(total_expenses / effective_limit if effective_limit > 0 else 1.0, 0.0), 1.0)
    st.progress(progress, text=f"نسبة استهلاك المتبقي الفعلي: {progress*100:.1f}%")

with tab2:
    st.header("تسجيل مصروف أو التزام جديد")
    with st.form("expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            title = st.text_input("وصف البند (مثال: قهوة، فاتورة...)")
            category = st.selectbox("التصنيف", ["يومي", "التزام"])
        with col_b:
            amount = st.number_input("المبلغ (ريال)", min_value=0.1, step=1.0)
            date = st.date_input("التاريخ", value=datetime.today())
            
        submitted = st.form_submit_button("إضافة المصروف")
        if submitted and title:
            new_item = {
                "التاريخ": date.strftime("%Y-%m-%d"),
                "البند": title,
                "التصنيف": category,
                "المبلغ": amount
            }
            data["expenses"].append(new_item)
            save_data(data)
            st.success("تمت الإضافة بنجاح!")
            st.rerun()

    st.subheader("سجل المصاريف السابقة")
    if not expenses_df.empty:
        st.dataframe(expenses_df, use_container_width=True)
        if st.button("حذف آخر مصروف مسجل"):
            data["expenses"].pop()
            save_data(data)
            st.warning("تم حذف آخر عنصر.")
            st.rerun()
    else:
        st.info("لا توجد مصاريف مسجلة حتى الآن.")

with tab3:
    st.header("إدارة الديون الخارجية (لي وعلي)")
    with st.form("debt_form", clear_on_submit=True):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            person = st.text_input("اسم الشخص")
            debt_type = st.selectbox("النوع", ["لي (عند الآخرين)", "علي (مستحق علي)"])
        with col_d2:
            debt_amount = st.number_input("مبلغ الدين (ريال)", min_value=0.1, step=1.0)
            notes = st.text_input("ملاحظات (اختياري)")
            
        debt_submitted = st.form_submit_button("إضافة الدين")
        if debt_submitted and person:
            new_debt = {
                "الشخص": person,
                "النوع": "لي" if "لي" in debt_type else "علي",
                "المبلغ": debt_amount,
                "الحالة": "مستحق",
                "ملاحظات": notes
            }
            data["debts"].append(new_debt)
            save_data(data)
            st.success("تمت إضافة الدين بنجاح!")
            st.rerun()

    st.subheader("قائمة الديون")
    debts_df = pd.DataFrame(data["debts"])
    if not debts_df.empty:
        st.dataframe(debts_df, use_container_width=True)
        
        debt_idx = st.number_input("رقم الصف لتعديل الحالة أو حذفه", min_value=0, max_value=max(0, len(data["debts"])-1), step=1, format="%d")
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("تغيير الحالة (مستحق / تم السداد)"):
                current_status = data["debts"][debt_idx]["الحالة"]
                data["debts"][debt_idx]["الحالة"] = "تم السداد" if current_status == "مستحق" else "مستحق"
                save_data(data)
                st.success("تم تحديث الحالة!")
                st.rerun()
        with col_act2:
            if st.button("حذف هذا الدين"):
                data["debts"].pop(debt_idx)
                save_data(data)
                st.error("تم حذف الدين.")
                st.rerun()
    else:
        st.info("لا توجد ديون مسجلة حالياً.")
