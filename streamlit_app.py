
import json
from pathlib import Path
from datetime import date
import streamlit as st

st.set_page_config(
    page_title="ميزانيتي",
    page_icon="💰",
    layout="wide"
)

DATA_FILE = Path("mizanati_data.json")
CURRENCY = "ر.س"


def load_data():
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        result = []
        for item in data:
            try:
                amount = float(item["amount"])
                kind = item["type"]
                title = str(item["title"]).strip()
                tx_date = date.fromisoformat(item["date"]).isoformat()
                if amount > 0 and kind in ("دخل", "مصروف") and title:
                    result.append({
                        "id": str(item.get("id", f"{tx_date}-{len(result)}")),
                        "date": tx_date,
                        "type": kind,
                        "title": title,
                        "category": str(item.get("category", "عام")),
                        "amount": amount,
                        "notes": str(item.get("notes", "")),
                    })
            except (KeyError, TypeError, ValueError):
                continue
        return result
    except (OSError, json.JSONDecodeError):
        return []


def save_data():
    try:
        DATA_FILE.write_text(
            json.dumps(st.session_state.transactions,
                       ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return True
    except OSError as exc:
        st.error(f"تعذر حفظ البيانات: {exc}")
        return False


if "transactions" not in st.session_state:
    st.session_state.transactions = load_data()

st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl; }
.block-container { max-width: 1200px; padding-top: 1.5rem; }
h1, h2, h3, p, label { text-align: right; }
div[data-testid="stMetric"] {
    background: #f1f7f3;
    border: 1px solid #d9e8df;
    padding: 14px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 ميزانيتي")
st.caption("إدارة الدخل والمصروفات بالريال السعودي")

with st.sidebar:
    st.header("القائمة")
    page = st.radio(
        "اختر الصفحة",
        ["لوحة التحكم", "إضافة عملية", "سجل العمليات", "النسخ الاحتياطي"]
    )

transactions = st.session_state.transactions


def money(value):
    return f"{value:,.2f} {CURRENCY}"


if page == "لوحة التحكم":
    today = date.today()
    period = st.selectbox(
        "الفترة",
        ["هذا الشهر", "آخر 3 أشهر", "هذا العام", "كل البيانات"]
    )

    filtered = []
    for t in transactions:
        try:
            d = date.fromisoformat(t["date"])
        except (ValueError, TypeError):
            continue

        months_ago = (today.year - d.year) * 12 + today.month - d.month

        if period == "هذا الشهر" and (d.year, d.month) != (
            today.year, today.month
        ):
            continue
        if period == "آخر 3 أشهر" and not 0 <= months_ago < 3:
            continue
        if period == "هذا العام" and d.year != today.year:
            continue

        filtered.append(t)

    income = sum(
        t["amount"] for t in filtered if t["type"] == "دخل"
    )
    expenses = sum(
        t["amount"] for t in filtered if t["type"] == "مصروف"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الدخل", money(income))
    c2.metric("إجمالي المصروفات", money(expenses))
    c3.metric("صافي الرصيد", money(income - expenses))

    st.subheader("أحدث العمليات")
    if filtered:
        rows = sorted(filtered, key=lambda x: x["date"], reverse=True)
        st.dataframe(
            [{
                "التاريخ": t["date"],
                "النوع": t["type"],
                "البيان": t["title"],
                "التصنيف": t["category"],
                "المبلغ": money(t["amount"])
            } for t in rows[:10]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("لا توجد عمليات في هذه الفترة.")

elif page == "إضافة عملية":
    st.subheader("إضافة دخل أو مصروف")

    with st.form("transaction_form", clear_on_submit=True):
        title = st.text_input("اسم العملية")
        col1, col2 = st.columns(2)

        with col1:
            kind = st.selectbox("نوع العملية", ["مصروف", "دخل"])
            category = st.selectbox(
                "التصنيف",
                ["عام", "راتب", "سكن", "طعام", "مواصلات",
                 "صحة", "تسوق", "فواتير", "أخرى"]
            )

        with col2:
            amount = st.number_input(
                "المبلغ بالريال",
                min_value=0.0,
                step=10.0,
                format="%.2f"
            )
            tx_date = st.date_input("التاريخ", value=date.today())

        notes = st.text_input("ملاحظات اختيارية")
        submitted = st.form_submit_button(
            "حفظ العملية",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not title.strip():
            st.error("أدخل اسم العملية.")
        elif amount <= 0:
            st.error("يجب أن يكون المبلغ أكبر من صفر.")
        else:
            st.session_state.transactions.append({
                "id": f"{date.today().isoformat()}-{len(transactions)+1}",
                "date": tx_date.isoformat(),
                "type": kind,
                "title": title.strip(),
                "category": category,
                "amount": float(amount),
                "notes": notes.strip()
            })
            if save_data():
                st.success("تم حفظ العملية.")
                st.rerun()

elif page == "سجل العمليات":
    st.subheader("سجل العمليات")
    col1, col2 = st.columns(2)

    with col1:
        type_filter = st.selectbox(
            "نوع العملية", ["الكل", "دخل", "مصروف"]
        )
    with col2:
        search = st.text_input("ابحث عن عملية")

    filtered = [
        t for t in transactions
        if (type_filter == "الكل" or t["type"] == type_filter)
        and search.strip().casefold()
        in (t["title"] + " " + t["category"]).casefold()
    ]

    if filtered:
        st.dataframe(
            [{
                "التاريخ": t["date"],
                "النوع": t["type"],
                "البيان": t["title"],
                "التصنيف": t["category"],
                "المبلغ": money(t["amount"]),
                "ملاحظات": t.get("notes", "")
            } for t in sorted(
                filtered, key=lambda x: x["date"], reverse=True
            )],
            use_container_width=True,
            hide_index=True
        )

        labels = [
            f'{t["date"]} | {t["type"]} | {t["title"]} | '
            f'{money(t["amount"])}'
            for t in filtered
        ]
        selected = st.selectbox("اختر عملية للحذف", ["—"] + labels)

        if selected != "—" and st.button("حذف العملية المحددة"):
            index = labels.index(selected)
            transaction_id = filtered[index]["id"]
            st.session_state.transactions = [
                t for t in st.session_state.transactions
                if t["id"] != transaction_id
            ]
            if save_data():
                st.success("تم حذف العملية.")
                st.rerun()
    else:
        st.info("لا توجد عمليات مطابقة.")

elif page == "النسخ الاحتياطي":
    st.subheader("النسخ الاحتياطي")

    backup = json.dumps(
        st.session_state.transactions,
        ensure_ascii=False,
        indent=2
    )

    st.download_button(
        "تنزيل نسخة احتياطية",
        data=backup.encode("utf-8"),
        file_name="mizanati_backup.json",
        mime="application/json",
        use_container_width=True
    )

    uploaded = st.file_uploader(
        "استعادة نسخة سابقة بصيغة JSON",
        type=["json"]
    )

    if uploaded is not None and st.button("استعادة النسخة"):
        try:
            data = json.load(uploaded)
            if not isinstance(data, list):
                raise ValueError("صيغة الملف غير صحيحة.")

            restored = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                amount = float(item["amount"])
                kind = item["type"]
                title = str(item["title"]).strip()
                tx_date = date.fromisoformat(item["date"]).isoformat()

                if amount <= 0 or kind not in ("دخل", "مصروف") or not title:
                    continue

                restored.append({
                    "id": str(item.get("id", f"{tx_date}-{len(restored)}")),
                    "date": tx_date,
                    "type": kind,
                    "title": title,
                    "category": str(item.get("category", "عام")),
                    "amount": amount,
                    "notes": str(item.get("notes", ""))
                })

            st.session_state.transactions = restored
            if save_data():
                st.success(f"تمت استعادة {len(restored)} عملية.")
                st.rerun()

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            st.error(f"تعذر استعادة الملف: {exc}")

st.divider()
st.caption(
    "نسخة أولية. لا تتضمن بعد الالتزامات المتكررة أو الديون "
    "أو قفل كلمة المرور والبصمة."
)


