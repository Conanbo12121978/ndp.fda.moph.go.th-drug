import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# ========== CACHE LOAD ==========
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

# ========== COLOR ==========
def get_border_color(account_id):
    return {
        "ก": "#38bdf8",
        "ข": "#4ade80",
        "ค": "#facc15",
        "ง": "#fb923c",
        "จ(1)": "#f472b6",
        "จ(2)": "#7a3a1d",
        "นอกบัญชี": "#a3a3a3",
    }.get(str(account_id).strip(), "#d1c4e9")

def get_sub_color(sub):
    return {
        "b": "#60a5fa",
        "s": "#34d399",
        "ex": "#f87171",
        "R1": "#fbbf24",
        "R2": "#a78bfa"
    }.get(str(sub).strip(), "#9ca3af")

# ========== UI ==========
st.set_page_config(page_title="Drug Finder", page_icon="💊")
st.markdown("## 💊 บัญชียาหลักแห่งชาติ")

# clear
if st.button("🔄 เคลียร์"):
    st.session_state.clear()

# ========== FILTER ==========
col1, col2 = st.columns(2)

with col1:
    subtype1 = st.selectbox("ประเภทหลัก", ["--ทั้งหมด--"] + sorted(df["subtype1_name"].dropna().unique()))
with col2:
    subtype2 = st.selectbox("ประเภทรอง", ["--ทั้งหมด--"] + sorted(df["subtype2_name"].dropna().unique()))

subtype3 = st.selectbox("ประเภทย่อย", ["--ทั้งหมด--"] + sorted(df["subtype3_name"].dropna().unique()))
account = st.selectbox("บัญชี", ["--ทั้งหมด--"] + sorted(df["account_drug_ID"].dropna().unique()))
sub_account = st.selectbox("บัญชีย่อย", ["--ทั้งหมด--"] + sorted(df["account_sub"].dropna().unique()))

search = st.text_input("🔍 ค้นหาชื่อยา")

# apply filter
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

# download
st.markdown(to_excel_download(df_filtered), unsafe_allow_html=True)

# ========== VIEW MODE ==========
view_mode = st.radio("โหมดแสดงผล", ["⚡ เร็ว (ตาราง)", "🎨 สวย (การ์ด)"])

st.subheader(f"📋 พบ {len(df_filtered)} รายการ")

# ========== FAST MODE ==========
if view_mode == "⚡ เร็ว (ตาราง)":
    st.dataframe(df_filtered, use_container_width=True)

# ========== CARD MODE ==========
else:
    MAX_ROWS = 150
    df_show = df_filtered.head(MAX_ROWS)

    st.caption(f"แสดง {len(df_show)} / {len(df_filtered)} รายการ (ป้องกันค้างมือถือ)")

    for _, row in df_show.iterrows():

        color = get_border_color(row["account_drug_ID"])
        sub_color = get_sub_color(row["account_sub"])

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
        if any([advice, condition, warning, note]):
            details += "<details><summary>📌 รายละเอียด</summary>"
            if advice: details += f"<div>คำแนะนำ: {advice}</div>"
            if condition: details += f"<div>เงื่อนไข: {condition}</div>"
            if warning: details += f"<div>คำเตือน: {warning}</div>"
            if note: details += f"<div>หมายเหตุ: {note}</div>"
            details += "</details>"

        st.markdown(f"""
        <div style="border-left:6px solid {color}; padding:10px; margin:6px; border-radius:6px; border:1px solid #ddd;">
            💊 <b>{drug}</b><br>
            <span style="color:#666;">{dosage}</span><br>
            <span style="color:#888;">บัญชี: {acc}</span><br>

            <span style="background:{sub_color};color:white;padding:2px 6px;border-radius:4px;">
            {sub}
            </span><br>

            <span style="color:#888;">ประเภท: {drug_type}</span>
            {details}
        </div>
        """, unsafe_allow_html=True)

# footer
st.markdown("---")
st.caption("© กลุ่มงานเภสัชกรรม")
