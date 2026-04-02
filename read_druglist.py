import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# ========== LOAD ==========
@st.cache_data
def load_data():
    df = pd.read_excel("media.xlsx")

    df = df.rename(columns={
        "group_name": "subtype1_name",
        "subgroup1_name": "subtype2_name",
        "subgroup2_name": "subtype3_name",
        "subgroup3_name": "subtype4_name",
        "generic_name": "drug_name",
        "บัญชียา": "account_drug_ID",
        "บัญชีย่อย": "account_sub",
        "ประเภทยา": "drug_type",
        "เงื่อนไข": "condition",
        "คำเตือน": "warning",
        "หมายเหตุ": "note"
    })

    df.columns = df.columns.str.strip()
    df = df.replace('_x000d_', ' ', regex=True)
    df = df.replace('-', '')

    df["account_drug_ID"] = df["account_drug_ID"].astype(str).str.strip()
    df["account_sub"] = df.get("account_sub", "").astype(str).str.strip()

    return df

df = load_data()

# ========== DOWNLOAD ==========
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    b64 = base64.b64encode(output.getvalue()).decode()
    return f"""
    <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
       download="filtered_drugs.xlsx"
       style="background:#2563eb;color:white;padding:8px 14px;border-radius:6px;text-decoration:none;">
       📥 ดาวน์โหลด Excel
    </a>
    """

# ========== UI ==========
st.set_page_config(page_title="Drug Finder", page_icon="💊")
st.markdown("## 💊 บัญชียาหลักแห่งชาติ")

# ========== CLEAR BUTTON ==========
if st.button("🔄 เคลียร์ทั้งหมด"):
    keys_to_clear = [
        "subtype1",
        "subtype2",
        "subtype3",
        "account",
        "sub_account",
        "search"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ========== FILTER ==========
col1, col2 = st.columns(2)

with col1:
    subtype1 = st.selectbox(
        "ประเภทหลัก",
        ["--ทั้งหมด--"] + sorted(df["subtype1_name"].dropna().unique()),
        key="subtype1"
    )

with col2:
    subtype2 = st.selectbox(
        "ประเภทรอง",
        ["--ทั้งหมด--"] + sorted(df["subtype2_name"].dropna().unique()),
        key="subtype2"
    )

subtype3 = st.selectbox(
    "ประเภทย่อย",
    ["--ทั้งหมด--"] + sorted(df["subtype3_name"].dropna().unique()),
    key="subtype3"
)

account = st.selectbox(
    "บัญชี",
    ["--ทั้งหมด--"] + sorted(df["account_drug_ID"].dropna().unique()),
    key="account"
)

sub_account = st.selectbox(
    "บัญชีย่อย",
    ["--ทั้งหมด--"] + sorted(df["account_sub"].dropna().unique()),
    key="sub_account"
)

search = st.text_input("🔍 ค้นหาชื่อยา", key="search")

# ========== FILTER LOGIC ==========
df_filtered = df.copy()

if subtype1 != "--ทั้งหมด--":
    df_filtered = df_filtered[df_filtered["subtype1_name"] == subtype1]

if subtype2 != "--ทั้งหมด--":
    df_filtered = df_filtered[df_filtered["subtype2_name"] == subtype2]

if subtype3 != "--ทั้งหมด--":
    df_filtered = df_filtered[df_filtered["subtype3_name"] == subtype3]

if account != "--ทั้งหมด--":
    df_filtered = df_filtered[df_filtered["account_drug_ID"] == account]

if sub_account != "--ทั้งหมด--":
    df_filtered = df_filtered[df_filtered["account_sub"] == sub_account]

if search:
    df_filtered = df_filtered[df_filtered["drug_name"].str.contains(search, case=False, na=False)]

# ========== DOWNLOAD ==========
st.markdown(to_excel_download(df_filtered), unsafe_allow_html=True)

# ========== VIEW ==========
view_mode = st.radio("โหมดแสดง", ["⚡ ตาราง", "📦 กล่อง"])

st.subheader(f"📋 พบ {len(df_filtered)} รายการ")

# ===== TABLE MODE =====
if view_mode == "⚡ ตาราง":
    st.dataframe(df_filtered, use_container_width=True)

# ===== BOX MODE =====
else:
    MAX_ROWS = 80
    df_show = df_filtered.head(MAX_ROWS)

    if len(df_filtered) > MAX_ROWS:
        st.warning("⚠️ แสดงเฉพาะ 80 รายการแรก (ป้องกันมือถือค้าง)")

    for _, row in df_show.iterrows():

        drug = row.get("drug_name", "-")
        dosage = row.get("dosage", "-")
        acc = row.get("account_drug_ID", "-")
        sub = row.get("account_sub", "-")
        drug_type = row.get("drug_type", "-")

        advice = row.get("advice", "")
        condition = row.get("condition", "")
        warning = row.get("warning", "")
        note = row.get("note", "")

        details = ""
        if advice:
            details += f"คำแนะนำ: {advice}<br>"
        if condition:
            details += f"เงื่อนไข: {condition}<br>"
        if warning:
            details += f"คำเตือน: {warning}<br>"
        if note:
            details += f"หมายเหตุ: {note}<br>"

        st.markdown(f"""
        <div style="padding:10px; margin:6px; border-radius:6px; border:1px solid #ddd;">
            💊 <b>{drug}</b><br>
            รูปแบบ: {dosage}<br>
            บัญชี: {acc}<br>
            บัญชีใหม่: {sub}<br>
            ประเภทยา: {drug_type}<br>
            {details}
        </div>
        """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.caption("© กลุ่มงานเภสัชกรรม")
