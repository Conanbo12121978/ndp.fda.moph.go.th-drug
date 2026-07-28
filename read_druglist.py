import streamlit as st
import pandas as pd
from io import BytesIO
import base64

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

    df = df.rename(columns={
        "group_name":"subtype1_name",
        "subgroup1_name":"subtype2_name",
        "subgroup2_name":"subtype3_name",
        "subgroup3_name":"subtype4_name",
        "generic_name":"drug_name",
        "บัญชียา":"account_drug_ID",
        "บัญชีใหม่":"account_sub",
        "ประเภทยา":"drug_type",
        "เงื่อนไข":"condition",
        "คำเตือน":"warning",
        "หมายเหตุ":"note"
    })

    df.columns = df.columns.str.strip()

    df = df.replace("_x000d_", " ", regex=True)
    df = df.replace("-", "")

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
# SUB ACCOUNT COLOR
# =====================================================

def sub_account_color(sub):

    sub = str(sub).strip().lower()

    color = {

        "b":"#2563eb",
        "s":"#16a34a",
        "ex":"#f59e0b",
        "R1":"#FCE4EC",
        "R2":"#F4CCCC",


        "":"#9ca3af"

    }

    return color.get(sub, "#7c3aed")

# =====================================================
# DOWNLOAD EXCEL
# =====================================================

def excel_download(df):

    export = df.copy()

    export.insert(
        0,
        "ลำดับ",
        range(1, len(export)+1)
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
<a
href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
download="DrugList.xlsx"
style="
background:#2563eb;
color:white;
padding:10px 18px;
border-radius:8px;
text-decoration:none;
display:inline-block;
">
📥 ดาวน์โหลด Excel
</a>
"""

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:20px;
}

.group-box{

    background:#ede9fe;

    border-left:8px solid #7c3aed;

    border-radius:10px;

    padding:14px 18px;

    margin-top:24px;

    margin-bottom:12px;

    color:#111827;

    font-size:24px;

    font-weight:bold;

}

.subgroup2{

    font-size:20px;

    font-weight:bold;

    color:#4c1d95;

    margin-top:18px;

}

.subgroup3{

    font-size:17px;

    font-weight:bold;

    color:#6d28d9;

    margin-left:20px;

    margin-top:12px;

}

.subgroup4{

    font-size:16px;

    font-weight:bold;

    color:#9333ea;

    margin-left:40px;

    margin-top:10px;

}

.drug-card{

    background:white;

    border-radius:10px;

    border:1px solid #dddddd;

    padding:14px;

    margin-left:50px;

    margin-bottom:10px;

    box-shadow:0 1px 4px rgba(0,0,0,.08);

}

.drug-name{

    font-size:18px;

    font-weight:bold;

    color:#111827;

}

.drug-detail{

    font-size:14px;

    color:#666666;

    margin-top:4px;

}

</style>
""", unsafe_allow_html=True)

# =====================================================
# DRUG CARD
# =====================================================

def render_card(row, dosage_text=""):

    color = sub_account_color(row.get("account_sub", ""))

    account = row.get("account_drug_ID", "-")
    sub = row.get("account_sub", "")
    drug_type = row.get("drug_type", "")
    condition = row.get("condition", "")
    warning = row.get("warning", "")
    note = row.get("note", "")

    html = f"""
<div class="drug-card" style="border-left:7px solid {color};">

<div class="drug-name">
💊 {row["drug_name"]}
</div>

<div class="drug-detail">
🏷️ <b>บัญชี :</b> {account}
&nbsp;&nbsp;&nbsp;
📑 <b>บัญชีใหม่ :</b> {sub}
</div>
"""

    if dosage_text:
        html += f"""
<div class="drug-detail">
📦 {dosage_text}
</div>
"""

    if drug_type:
        html += f"""
<div class="drug-detail">
🧪 {drug_type}
</div>
"""

    if condition:
        html += f"""
<div class="drug-detail">
📝 {condition}
</div>
"""

    if warning:
        html += f"""
<div class="drug-detail">
⚠️ {warning}
</div>
"""

    if note:
        html += f"""
<div class="drug-detail">
📌 {note}
</div>
"""

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.title("💊 บัญชียาหลักแห่งชาติ พ.ศ. 2569")
st.caption("ค้นหายา • จัดหมวดหมู่ • ดาวน์โหลด Excel")

# =====================================================
# SESSION STATE
# =====================================================

defaults = {
    "subtype1":"--ทั้งหมด--",
    "subtype2":"--ทั้งหมด--",
    "subtype3":"--ทั้งหมด--",
    "account":"--ทั้งหมด--",
    "account_sub":"--ทั้งหมด--",
    "search":"",
    "view_mode":"📋 รายการยา"
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# =====================================================
# CLEAR
# =====================================================

if st.button("🔄 เคลียร์ตัวกรองทั้งหมด"):

    for k,v in defaults.items():
        st.session_state[k]=v

    st.rerun()

# =====================================================
# FILTER
# =====================================================

df_filter = df.copy()

col1,col2 = st.columns(2)

with col1:

    subtype1 = st.selectbox(
        "ประเภทหลัก",
        ["--ทั้งหมด--"] + sorted(df["subtype1_name"].unique()),
        key="subtype1"
    )

if subtype1!="--ทั้งหมด--":
    df_filter=df_filter[
        df_filter["subtype1_name"]==subtype1
    ]

with col2:

    subtype2 = st.selectbox(
        "ประเภทรอง",
        ["--ทั้งหมด--"] + sorted(df_filter["subtype2_name"].unique()),
        key="subtype2"
    )

if subtype2!="--ทั้งหมด--":
    df_filter=df_filter[
        df_filter["subtype2_name"]==subtype2
    ]

subtype3 = st.selectbox(
    "ประเภทย่อย",
    ["--ทั้งหมด--"] + sorted(df_filter["subtype3_name"].unique()),
    key="subtype3"
)

if subtype3!="--ทั้งหมด--":
    df_filter=df_filter[
        df_filter["subtype3_name"]==subtype3
    ]

col3,col4 = st.columns(2)

with col3:

    account = st.selectbox(
        "บัญชี",
        ["--ทั้งหมด--"] + sorted(df["account_drug_ID"].unique()),
        key="account"
    )

if account!="--ทั้งหมด--":
    df_filter=df_filter[
        df_filter["account_drug_ID"]==account
    ]

with col4:

    account_sub = st.selectbox(
        "บัญชีย่อย",
        ["--ทั้งหมด--"] + sorted(df["account_sub"].unique()),
        key="account_sub"
    )

if account_sub!="--ทั้งหมด--":
    df_filter=df_filter[
        df_filter["account_sub"]==account_sub
    ]

# =====================================================
# SEARCH
# =====================================================

search = st.text_input(
    "🔍 ค้นหาชื่อยา",
    key="search"
)

if search:

    df_filter=df_filter[
        df_filter["drug_name"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# =====================================================
# SUMMARY
# =====================================================

st.markdown(
    excel_download(df_filter),
    unsafe_allow_html=True
)

st.caption(
    f"พบทั้งหมด {len(df_filter):,} รายการ"
)

# =====================================================
# VIEW MODE
# =====================================================

view_mode = st.radio(
    "รูปแบบการแสดงผล",
    [
        "📋 รายการยา",
        "🗂 จัดตามหมวดหมู่"
    ],
    horizontal=True,
    key="view_mode"
)
# =====================================================
# 📋 LIST VIEW
# =====================================================

if view_mode == "📋 รายการยา":

    if df_filter.empty:

        st.info("ไม่พบข้อมูล")

    else:

        # เรียงข้อมูล
        df_show = df_filter.copy()

        df_show = df_show.sort_values(
            by=[
                "drug_name",
                "account_sub",
                "dosage"
            ]
        )

        st.subheader(
            f"📋 พบ {len(df_show):,} รายการ"
        )

        # ----------------------------
        # รวมชื่อยา + บัญชีใหม่
        # ----------------------------

        for (drug_name, account_sub), group in df_show.groupby(
            ["drug_name", "account_sub"],
            sort=True
        ):

            row = group.iloc[0]

            # รวม dosage
            dosage_list = (
                group["dosage"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            dosage_list = [
                x for x in dosage_list
                if x != ""
            ]

            dosage_list = sorted(
                set(dosage_list)
            )

            dosage_text = " • ".join(
                dosage_list
            )

            render_card(
                row,
                dosage_text
            )

# =====================================================
# 🗂 CATEGORY VIEW
# =====================================================

elif view_mode == "🗂 จัดตามหมวดหมู่":

    if df_filter.empty:

        st.info("ไม่พบข้อมูล")

    else:

        df_show = df_filter.copy()

        cols = [
            "subtype1_name",
            "subtype2_name",
            "subtype3_name",
            "subtype4_name",
            "drug_name",
            "account_sub",
            "dosage"
        ]

        for c in cols:
            if c in df_show.columns:
                df_show[c] = (
                    df_show[c]
                    .fillna("")
                    .astype(str)
                )

        df_show = df_show.sort_values(by=cols)

        # =================================================
        # subtype1
        # =================================================

        for subtype1, g1 in df_show.groupby("subtype1_name", dropna=False):

            st.markdown(
                f"""
<div class="group-box">
🟣 {subtype1 if subtype1 else "ไม่ระบุ"}
</div>
""",
                unsafe_allow_html=True
            )

            # =============================================

            for subtype2, g2 in g1.groupby("subtype2_name", dropna=False):

                if subtype2:

                    st.markdown(
                        f"""
<div class="subgroup2">
🔷 {subtype2}
</div>
""",
                        unsafe_allow_html=True
                    )

                # =============================================

                for subtype3, g3 in g2.groupby("subtype3_name", dropna=False):

                    if subtype3:

                        st.markdown(
                            f"""
<div class="subgroup3">
▸ {subtype3}
</div>
""",
                            unsafe_allow_html=True
                        )

                    # =============================================

                    for subtype4, g4 in g3.groupby("subtype4_name", dropna=False):

                        if subtype4:

                            st.markdown(
                                f"""
<div class="subgroup4">
• {subtype4}
</div>
""",
                                unsafe_allow_html=True
                            )

                        # ==========================================
                        # รวม dosage และแยกตามบัญชีย่อย
                        # ==========================================

                        for (drug_name, account_sub), group in g4.groupby(
                            ["drug_name", "account_sub"],
                            sort=True
                        ):

                            row = group.iloc[0]

                            dosage_list = (
                                group["dosage"]
                                .dropna()
                                .astype(str)
                                .str.strip()
                            )

                            dosage_list = [
                                d for d in dosage_list
                                if d != ""
                            ]

                            dosage_text = " • ".join(
                                sorted(set(dosage_list))
                            )

                            render_card(
                                row,
                                dosage_text
                            )
