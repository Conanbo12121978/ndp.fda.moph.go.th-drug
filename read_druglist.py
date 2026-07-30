import streamlit as st
import pandas as pd
from io import BytesIO
import base64
import re

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Drug Finder",
    page_icon="💊",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    df = pd.read_excel("media.xlsx")

    # -----------------------------
    # Rename Columns
    # -----------------------------
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

    # -----------------------------
    # Clean Column Name
    # -----------------------------
    df.columns = df.columns.str.strip()

    # -----------------------------
    # Replace text
    # -----------------------------
    df = df.replace("_x000d_", " ", regex=True)
    df = df.replace("-", "")

    # -----------------------------
    # Clean string
    # -----------------------------
    for c in df.columns:

        if df[c].dtype == "object":

            df[c] = (
                df[c]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


df = load_data()


# =====================================================
# NATURAL SORT
# =====================================================

def sort_number(text):

    text = str(text).strip()

    m = re.match(r"^(\d+)", text)

    if m:
        return int(m.group(1))

    return 9999


# =====================================================
# SUB ACCOUNT COLOR
# =====================================================

def sub_account_color(sub):

    sub = str(sub).strip().lower()

    colors = {

        "b": "#2563eb",      # Blue
        "s": "#16a34a",      # Green
        "ex": "#f59e0b",     # Orange

        "r1": "#ec4899",     # Pink
        "r2": "#ef4444",     # Red

        "": "#9ca3af"

    }

    return colors.get(sub, "#7c3aed")


# =====================================================
# BADGE COLOR
# =====================================================

def badge_style(sub):

    color = sub_account_color(sub)

    return f"""
display:inline-block;
padding:4px 10px;
border-radius:999px;
background:{color};
color:white;
font-size:13px;
font-weight:700;
margin-right:8px;
"""


# =====================================================
# DOWNLOAD EXCEL
# =====================================================

def excel_download(df):

    export = df.copy()

    export.insert(
        0,
        "ลำดับ",
        range(1, len(export) + 1)
    )

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        export.to_excel(
            writer,
            index=False
        )

    b64 = base64.b64encode(
        output.getvalue()
    ).decode()

    return f"""
<a href="
data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}
"
download="DrugList.xlsx"
style="
background:#2563eb;
color:white;
padding:10px 18px;
border-radius:8px;
text-decoration:none;
display:inline-block;
font-weight:600;
">
📥 ดาวน์โหลด Excel
</a>
"""
