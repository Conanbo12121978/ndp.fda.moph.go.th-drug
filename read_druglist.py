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
    df_export = df.copy().fillna("-")
    df_export.insert(0, "ลำดับ", range(1, len(df_export) + 1))

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False)

    b64 = base64.b64encode(output.getvalue()).decode()
    return f"""
    <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
       download="filtered_drugs.xlsx"
       style="background:#2563eb;color:white;padding:8px 14px;border-radius:6px;text-decoration:none;">
       📥 ดาวน์โหลด Excel
    </a>
    """

# ========== DEFAULT STATE ==========
defaults = {
    "subtype1": "--ทั้งหมด--",
    "subtype2": "--ทั้งหมด--",
    "subtype3": "--ทั้งหมด--",
    "account": "--ทั้งหมด--",
    "sub_account": "--ทั้งหมด--",
    "search": "",
    "view_mode": "⚡ ตาราง"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ========== UI ==========
st.set_page_config(page_title="Drug Finder", page_icon="💊")
st.markdown("## 💊 บัญชียาหลักแห่งชาติ 2569")

# ========== CLEAR ==========
if st.button("🔄 เคลียร์ทั้งหมด"):
    for k, v in defaults.items():
        st.session_state[k] = v
    st.rerun()

# ========== CASCADE FILTER ==========
df_ui = df.copy()

col1, col2 = st.columns(2)

# ---- subtype1 ----
with col1:
    subtype1 = st.selectbox(
        "ประเภทหลัก",
        ["--ทั้งหมด--"] + sorted(df["subtype1_name"].dropna().unique()),
        key="subtype1"
    )

# reset subtype2/3 เมื่อ subtype1 เปลี่ยน
if "prev_subtype1" not in st.session_state:
    st.session_state.prev_subtype1 = None

if st.session_state.prev_subtype1 != subtype1:
    st.session_state.subtype2 = "--ทั้งหมด--"
    st.session_state.subtype3 = "--ทั้งหมด--"

st.session_state.prev_subtype1 = subtype1

if subtype1 != "--ทั้งหมด--":
    df_ui = df_ui[df_ui["subtype1_name"] == subtype1]

# ---- subtype2 ----
with col2:
    subtype2 = st.selectbox(
        "ประเภทรอง",
        ["--ทั้งหมด--"] + sorted(df_ui["subtype2_name"].dropna().unique()),
        key="subtype2"
    )

if subtype2 != "--ทั้งหมด--":
    df_ui = df_ui[df_ui["subtype2_name"] == subtype2]

# ---- subtype3 ----
subtype3 = st.selectbox(
    "ประเภทย่อย",
    ["--ทั้งหมด--"] + sorted(df_ui["subtype3_name"].dropna().unique()),
    key="subtype3"
)

if subtype3 != "--ทั้งหมด--":
    df_ui = df_ui[df_ui["subtype3_name"] == subtype3]

# ---- account ----
account = st.selectbox(
    "บัญชี",
    ["--ทั้งหมด--"] + sorted(df["account_drug_ID"].dropna().unique()),
    key="account"
)

if account != "--ทั้งหมด--":
    df_ui = df_ui[df_ui["account_drug_ID"] == account]

# ---- sub_account ----
sub_account = st.selectbox(
    "บัญชีย่อย",
    ["--ทั้งหมด--"] + sorted(df["account_sub"].dropna().unique()),
    key="sub_account"
)

if sub_account != "--ทั้งหมด--":
    df_ui = df_ui[df_ui["account_sub"] == sub_account]

# ---- search ----
search = st.text_input("🔍 ค้นหาชื่อยา", key="search")

if search:
    df_ui = df_ui[df_ui["drug_name"].str.contains(search, case=False, na=False)]

df_filtered = df_ui

# ========== DOWNLOAD ==========
st.markdown(to_excel_download(df_filtered), unsafe_allow_html=True)

# ========== VIEW ==========
view_mode = st.radio(
    "โหมดแสดง",
    ["⚡ ตาราง", "📦 กล่อง"],
    key="view_mode"
)

st.subheader(f"📋 พบ {len(df_filtered)} รายการ")

# ===== TABLE =====
if view_mode == "⚡ ตาราง":
    df_show = df_filtered.copy().fillna("-")
    df_show.insert(0, "ลำดับ", range(1, len(df_show) + 1))
    st.dataframe(df_show, use_container_width=True, hide_index=True)

# ===== BOX =====
else:
    df_show = df_filtered.head(80).fillna("-")

    if len(df_filtered) > 80:
        st.warning("⚠️ แสดงเฉพาะ 80 รายการแรก")

    for i, row in df_show.iterrows():
        st.markdown(f"""
        <div style="padding:10px; margin:6px; border-radius:6px; border:1px solid #ddd;">
            <b>{i+1}. {row['drug_name']}</b><br>
            รูปแบบ: {row.get('dosage','-')}<br>
            บัญชี: {row.get('account_drug_ID','-')}<br>
            บัญชีใหม่: {row.get('account_sub','-')}<br>
            ประเภทยา: {row.get('drug_type','-')}<br>
            เงื่อนไข: {row.get('condition','-')}<br>
            คำเตือน: {row.get('warning','-')}<br>
            หมายเหตุ: {row.get('note','-')}<br>
        </div>
        """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.caption("© กลุ่มงานเภสัชกรรม")
