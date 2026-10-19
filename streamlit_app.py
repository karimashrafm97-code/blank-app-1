import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# إعدادات الصفحة الشاملة لتطابق التصميم
st.set_page_config(
    page_title="إدارة المالية - Karim cash",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق تنسيقات CSS مخصصة لمطابقة تصميم الشاشة بالكامل
st.markdown("""
    <style>
    /* خلفية الصفحة العامة */
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* بطاقات KPI العلوية */
    .kpi-card {
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-title { font-size: 14px; font-weight: bold; margin-bottom: 8px; }
    .kpi-value { font-size: 22px; font-weight: bold; }
    .kpi-sub { font-size: 12px; color: #6b7280; }
    
    /* ألوان البطاقات العلوية المصممة */
    .bg-green { background-color: #e6f7ed; color: #0d8a43; border: 1px solid #b7ebd0; }
    .bg-red { background-color: #fde8e8; color: #e02424; border: 1px solid #f8b4b4; }
    .bg-blue { background-color: #e1effe; color: #1e429f; border: 1px solid #a4cafe; }
    .bg-yellow { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .bg-purple { background-color: #edebfe; color: #5521b5; border: 1px solid #cdb5e1; }
    
    /* بطاقة الترحيب بالأمان */
    .auth-card {
        background: #ffffff;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        text-align: center;
        max-width: 450px;
        margin: 50px auto;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "budget_data.json"

def load_data():
    default_data = {
        "monthly_limit": 1000.0,
        "sava_amount": 200.0,
        "income_list": [
            {"التاريخ": "2026-10-18", "النوع": "إيراد", "الوصف": "مبيعات نقدية", "المبلغ": 25000}
        ],
        "expenses": [
            {"التاريخ": "2026-10-17", "النوع": "مصروف", "الوصف": "مشتريات", "المبلغ": 12000}
        ],
        "commitments": [
            {"التاريخ": "2026-10-17", "النوع": "التزام ثابت", "الوصف": "إيجار المكتب", "المبلغ": 10000}
        ],
        "debts_li": [
            {"العميل": "شركة أ", "المبلغ": 40000, "تاريخ الاستحقاق": "2026-10-25", "الحالة": "مستحق"},
            {"العميل": "عميل ب", "المبلغ": 30000, "تاريخ الاستحقاق": "2026-11-10", "الحالة": "مستحق"},
            {"العميل": "شركة ج", "المبلغ": 50000, "تاريخ الاستحقاق": "2026-12-01", "الحالة": "مستحق"}
        ],
        "debts_alei": [
            {"المورد": "مورد أ", "المبلغ": 30000, "تاريخ الاستحقاق": "2026-10-20", "الحالة": "مستحق"},
            {"المورد": "مورد ب", "المبلغ": 40000, "تاريخ الاستحقاق": "2026-11-05", "الحالة": "مستحق"},
            {"المورد": "مورد ج", "المبلغ": 20000, "تاريخ الاستحقاق": "2026-12-15", "الحالة": "مستحق"}
        ],
        "password": "123"
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                for k, v in default_data.items():
                    if k not in loaded:
                        loaded[k] = v
                return loaded
        except Exception:
            return default_data
    return default_data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# --- شاشة الأمان وبصمة الوجه المحدثة ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <div class="auth-card">
            <h2>💰 Karim cash</h2>
            <p style="color:#6b7280;">مرحباً كريم 👋 يرجى إثبات الهوية للدخول</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        entered_pass = st.text_input("كلمة المرور", type="password", placeholder="أدخل كلمة المرور...")
        
        if st.button("🔓 دخول بكلمة المرور", use_container_width=True):
            if entered_pass == data.get("password", "123"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة!")
                
        st.write("---")
        
        if st.button("👤 الدخول عبر بصمة الوجه (Face ID)", use_container_width=True):
            # محاكاة الربط مع الجوال والتأكد من البصمة
            st.warning("⚠️ يتعذر الدخول المباشر بالوجه. يرجى التأكد من ربط بصمة الوجه في إعدادات جوالك أو إدخال كلمة المرور.")
            
    st.stop()

# --- الشريط الجانبي (Sidebar) ---
st.sidebar.title("إدارة المالية")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "القائمة الرئيسية:",
    [
        "🏠 الرئيسية",
        "💰 الإيرادات (الدخل)",
        "🛒 المصروفات",
        "📅 الالتزامات الثابتة",
        "🤝 دين لي (مستحقات)",
        "💳 دين علي (مطلوبات)",
        "📊 التقارير",
        "⚙️ الإعدادات"
    ]
)

# 🏠 الشاشة الرئيسية (Dashboard) المطابقة للصورة بالكامل
if menu == "🏠 الرئيسية":
    st.title("إدارة المالية")
    st.caption("الإثنين 18 أكتوبر 2026")
    
    # 1. بطاقات المؤشرات العلوية (KPIs)
    k1, k2, k3, k4, k5 = st.columns(5)
    
    with k1:
        st.markdown("""
            <div class="kpi-card bg-green">
                <div class="kpi-title">📈 إجمالي الإيرادات</div>
                <div class="kpi-value">150,000</div>
                <div class="kpi-sub">ريال</div>
            </div>
        """, unsafe_allow_html=True)
        
    with k2:
        st.markdown("""
            <div class="kpi-card bg-red">
                <div class="kpi-title">🔻 إجمالي المصروفات</div>
                <div class="kpi-value">80,000</div>
                <div class="kpi-sub">ريال</div>
            </div>
        """, unsafe_allow_html=True)
        
    with k3:
        st.markdown("""
            <div class="kpi-card bg-blue">
                <div class="kpi-title">📅 الالتزامات الثابتة</div>
                <div class="kpi-value">25,000</div>
                <div class="kpi-sub">ريال</div>
            </div>
        """, unsafe_allow_html=True)
        
    with k4:
        st.markdown("""
            <div class="kpi-card bg-yellow">
                <div class="kpi-title">👥 دين لي (مستحقات)</div>
                <div class="kpi-value">120,000</div>
                <div class="kpi-sub">ريال</div>
            </div>
        """, unsafe_allow_html=True)
        
    with k5:
        st.markdown("""
            <div class="kpi-card bg-purple">
                <div class="kpi-title">💰 دين علي (مطلوبات)</div>
                <div class="kpi-value">90,000</div>
                <div class="kpi-sub">ريال</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # 2. الرسم البياني والمخطط الدائري
    chart_col, pie_col = st.columns([2, 1])
    
    with chart_col:
        st.subheader("الإيرادات والمصروفات والالتزامات")
        months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر']
        
        fig = go.Figure(data=[
            go.Bar(name='الإيرادات', x=months, y=[85000, 92000, 105000, 98000, 90000, 95000, 135000, 115000, 152000, 160000], marker_color='#10b981'),
            go.Bar(name='المصروفات', x=months, y=[48000, 51000, 52000, 50000, 49000, 48000, 72000, 48000, 65000, 75000], marker_color='#ef4444'),
            go.Bar(name='الالتزامات الثابتة', x=months, y=[22000, 22000, 22000, 22000, 22000, 22000, 25000, 25000, 25000, 25000], marker_color='#3b82f6')
        ])
        fig.update_layout(barmode='group', height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
    with pie_col:
        st.subheader("توزيع المصروفات (أكتوبر 2026)")
        labels = ['مشتريات', 'رواتب', 'إيجار', 'مصاريف تشغيلية', 'سفر ومواصلات', 'أخرى']
        values = [37, 25, 15, 12, 8, 3]
        
        fig_pie = px.pie(values=values, names=labels, hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.write("---")
    
    # 3. الجداول السفليّة الفرعية
    col_left, col_mid, col_right = st.columns([1.5, 1.2, 1.3])
    
    with col_left:
        st.subheader("أحدث العمليات")
        recent_df = pd.DataFrame([
            {"التاريخ": "2026/10/18", "النوع": "إيراد", "الوصف": "مبيعات نقدية", "المبلغ": "25,000 ريال"},
            {"التاريخ": "2026/10/17", "النوع": "مصروف", "الوصف": "مشتريات", "المبلغ": "12,000 ريال"},
            {"التاريخ": "2026/10/17", "النوع": "التزام ثابت", "الوصف": "إيجار المكتب", "المبلغ": "10,000 ريال"},
            {"التاريخ": "2026/10/16", "النوع": "دين لي", "الوصف": "مستحق من العميل أ", "المبلغ": "35,000 ريال"},
            {"التاريخ": "2026/10/15", "النوع": "دين علي", "الوصف": "مستحق للمورد ب", "المبلغ": "20,000 ريال"}
        ])
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
        
    with col_mid:
        st.subheader("الالتزامات الثابتة (الدورية)")
        com_df = pd.DataFrame([
            {"الالتزام": "إيجار المكتب", "القيمة الشهرية": "10,000 ريال", "التكرار": "شهري"},
            {"الالتزام": "رواتب الموظفين", "القيمة الشهرية": "8,000 ريال", "التكرار": "شهري"},
            {"الالتزام": "اشتراك برامج", "القيمة الشهرية": "2,000 ريال", "التكرار": "شهري"},
            {"الالتزام": "فواتير خدمات", "القيمة الشهرية": "3,000 ريال", "التكرار": "شهري"},
            {"الالتزام": "تأمينات", "القيمة الشهرية": "2,000 ريال", "التكرار": "شهري"}
        ])
        st.dataframe(com_df, use_container_width=True, hide_index=True)
        st.info("مجموع الالتزامات الشهرية: 25,000 ريال")
        
    with col_right:
        st.subheader("دين لي - (مستحقات)")
        st.dataframe(pd.DataFrame(data["debts_li"]), use_container_width=True, hide_index=True)
        
        st.subheader("دين علي - (مطلوبات)")
        st.dataframe(pd.DataFrame(data["debts_alei"]), use_container_width=True, hide_index=True)

# باقي الشاشات والأقسام لضمان اكتمال التطبيق
elif menu == "💰 الإيرادات (الدخل)":
    st.title("إدارة الإيرادات والدخل")
    st.write("تسجيل إيراد جديد:")
    with st.form("inc_form"):
        desc = st.text_input("وصف الإيراد")
        amt = st.number_input("المبلغ (ريال)", min_value=1.0)
        if st.form_submit_button("إضافة"):
            data["income_list"].append({"التاريخ": datetime.today().strftime("%Y-%m-%d"), "النوع": "إيراد", "الوصف": desc, "المبلغ": amt})
            save_data(data)
            st.success("تمت الإضافة بنجاح!")
            st.rerun()

elif menu == "⚙️ الإعدادات":
    st.title("الإعدادات والأمان")
    new_p = st.text_input("تغيير كلمة المرور", type="password")
    if st.button("حفظ"):
        if new_p:
            data["password"] = new_p
            save_data(data)
            st.success("تم حفظ كلمة المرور الجديدة بنجاح!")
