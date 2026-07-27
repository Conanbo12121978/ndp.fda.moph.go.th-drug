import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# ==========================
# Page
# ==========================
st.set_page_config(
    page_title="Drug Finder",
    page_icon="💊",
    layout="wide"
)

# ==========================
# Load Excel
# ==========================
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
        "บัญชีย่อย":"account_sub",
        "ประเภทยา":"drug_type",
        "เงื่อนไข":"condition",
        "คำเตือน":"warning",
        "หมายเหตุ":"note"
    })

    df.columns=df.columns.str.strip()

    df=df.replace("_x000d_"," ",regex=True)
    df=df.replace("-", "")

    for c in df.columns:
        if df[c].dtype=="object":
            df[c]=df[c].fillna("").astype(str).str.strip()

    return df

df=load_data()


def account_color(acc):

    acc=str(acc).strip()

    color={

        "ก":"#3b82f6",
        "ข":"#10b981",
        "ค":"#eab308",
        "ง":"#fb923c",
        "จ":"#ec4899",

        "A":"#3b82f6",
        "B":"#10b981",
        "C":"#eab308",

        "นอกบัญชี":"#9ca3af",
        "บัญชียาจากสมุนไพร":"#8b5a2b"

    }

    return color.get(acc,"#8b5cf6")

# ========== DOWNLOAD ==========
def excel_download(df):

    out=BytesIO()

    export=df.copy()

    export.insert(0,"ลำดับ",range(1,len(export)+1))

    with pd.ExcelWriter(out,engine="openpyxl") as writer:
        export.to_excel(writer,index=False)

    b64=base64.b64encode(out.getvalue()).decode()

    return f"""
<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
download="DrugList.xlsx"
style="
background:#2563eb;
padding:10px 18px;
color:white;
border-radius:8px;
text-decoration:none;
">
📥 ดาวน์โหลด Excel
</a>
"""

st.markdown("""

<style>

.block-container{

    padding-top:25px;

}

/*========================*/

.group-box{

background:#ede9fe;

padding:14px 18px;

border-radius:10px;

border-left:8px solid #7c3aed;

font-size:24px;

font-weight:bold;

margin-top:25px;

margin-bottom:12px;

}

/*========================*/

.subgroup2{

font-size:20px;

font-weight:700;

color:#4c1d95;

margin-top:18px;

margin-bottom:10px;

}

/*========================*/

.subgroup3{

font-size:17px;

font-weight:600;

margin-left:20px;

color:#6d28d9;

margin-top:12px;

}

/*========================*/

.subgroup4{

font-size:16px;

font-weight:600;

margin-left:40px;

color:#9333ea;

margin-top:10px;

}

/*========================*/

.drug-card{

background:white;

border-radius:10px;

padding:14px;

margin-left:50px;

margin-bottom:10px;

border:1px solid #dddddd;

box-shadow:0px 1px 4px rgba(0,0,0,.08);

}

.drug-name{

font-size:18px;

font-weight:bold;

}

.drug-detail{

color:#666;

font-size:14px;

margin-top:5px;

}

/*========================*/

[data-theme="dark"] .drug-card{

background:#1f2937;

border:1px solid #444;

}

[data-theme="dark"] .group-box{

background:#312e81;

}

[data-theme="dark"] .subgroup2{

color:#ddd6fe;

}

[data-theme="dark"] .subgroup3{

color:#e9d5ff;

}

[data-theme="dark"] .subgroup4{

color:#f3e8ff;

}

</style>

""",unsafe_allow_html=True)

# ==========================

# ฟังก์ชันแสดงการ์ดยา

# =========================
def render_card(row):

    color = account_color(row["account_drug_ID"])

    dosage = row.get("dosage", "")
    if dosage:
        dosage = f"<br><span style='color:#666;'>{dosage}</span>"

    st.markdown(
        f"""
<div class="drug-card"
style="border-left:7px solid {color};">

<div class="drug-name">

💊 {row["drug_name"]}

{dosage}

</div>

<div class="drug-detail">

<b>บัญชี :</b> {row["account_drug_ID"]}

&nbsp;&nbsp;

<b>บัญชีย่อย :</b> {row["account_sub"]}

</div>

</div>
""",
        unsafe_allow_html=True,
    )

# ==========================
# HEADER
# ==========================

st.title("💊 บัญชียาหลักแห่งชาติ 2569")

st.caption(
    "ค้นหายา เรียงตามหมวดหมู่ และดาวน์โหลดข้อมูลได้"
)

# ==========================
# SESSION STATE
# ==========================

defaults = {
    "subtype1": "--ทั้งหมด--",
    "subtype2": "--ทั้งหมด--",
    "subtype3": "--ทั้งหมด--",
    "account": "--ทั้งหมด--",
    "account_sub": "--ทั้งหมด--",
    "search": "",
    "view_mode": "📋 รายการยา"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================
# CLEAR BUTTON
# ==========================

if st.button("🔄 เคลียร์ตัวกรองทั้งหมด"):

    for k, v in defaults.items():
        st.session_state[k] = v

    st.rerun()

# ==========================
# FILTER
# ==========================

df_filter = df.copy()

col1, col2 = st.columns(2)

with col1:

    subtype1 = st.selectbox(
        "ประเภทหลัก",
        ["--ทั้งหมด--"] +
        sorted(df["subtype1_name"].dropna().unique()),
        key="subtype1"
    )

    if subtype1 != "--ทั้งหมด--":
        df_filter = df_filter[
            df_filter["subtype1_name"] == subtype1
        ]

with col2:

    subtype2 = st.selectbox(
        "ประเภทรอง",
        ["--ทั้งหมด--"] +
        sorted(df_filter["subtype2_name"].dropna().unique()),
        key="subtype2"
    )

    if subtype2 != "--ทั้งหมด--":
        df_filter = df_filter[
            df_filter["subtype2_name"] == subtype2
        ]

subtype3 = st.selectbox(

    "ประเภทย่อย",

    ["--ทั้งหมด--"] +
    sorted(df_filter["subtype3_name"].dropna().unique()),

    key="subtype3"

)

if subtype3 != "--ทั้งหมด--":

    df_filter = df_filter[
        df_filter["subtype3_name"] == subtype3
    ]

col3, col4 = st.columns(2)

with col3:

    account = st.selectbox(

        "บัญชียา",

        ["--ทั้งหมด--"] +
        sorted(df["account_drug_ID"].dropna().unique()),

        key="account"

    )

    if account != "--ทั้งหมด--":

        df_filter = df_filter[
            df_filter["account_drug_ID"] == account
        ]

with col4:

    account_sub = st.selectbox(

        "บัญชีย่อย",

        ["--ทั้งหมด--"] +
        sorted(df["account_sub"].dropna().unique()),

        key="account_sub"

    )

    if account_sub != "--ทั้งหมด--":

        df_filter = df_filter[
            df_filter["account_sub"] == account_sub
        ]

# ==========================
# SEARCH
# ==========================

search = st.text_input(

    "🔍 ค้นหาชื่อยา",

    key="search"

)

if search:

    df_filter = df_filter[
        df_filter["drug_name"]
        .str.contains(search, case=False, na=False)
    ]

# ==========================
# DOWNLOAD
# ==========================

st.markdown(
    excel_download(df_filter),
    unsafe_allow_html=True
)

# ==========================
# VIEW MODE
# ==========================

view_mode = st.radio(

    "โหมดการแสดงผล",

    [

        "📋 รายการยา",

        "🗂 จัดตามหมวดหมู่"

    ],

    horizontal=True,

    key="view_mode"

)

st.subheader(

    f"📋 พบ {len(df_filter)} รายการ"

)

# ======================================================
# 📋 LIST VIEW
# ======================================================

if view_mode == "📋 รายการยา":

    if len(df_filter) == 0:
        st.warning("ไม่พบข้อมูล")
    else:

        df_show = df_filter.copy()

        df_show = df_show.sort_values(
            by=["drug_name"]
        )

        for i, row in enumerate(df_show.itertuples(), start=1):

            color = account_color(row.account_drug_ID)

            st.markdown(
                f"""
<div class="drug-card"
style="border-left:8px solid {color};">

<div class="drug-name">
{i}. 💊 {row.drug_name}
</div>

<div class="drug-detail">

<b>บัญชียา</b> :
{row.account_drug_ID if row.account_drug_ID else "-"}

&nbsp;&nbsp;&nbsp;

<b>บัญชีย่อย</b> :
{row.account_sub if row.account_sub else "-"}

</div>

<div class="drug-detail">

<b>ประเภท</b> :
{row.drug_type if row.drug_type else "-"}

</div>

""",
                unsafe_allow_html=True,
            )

            if row.condition:
                st.markdown(
                    f"""
<div class="drug-detail">

📝 <b>เงื่อนไข :</b>

{row.condition}

</div>
""",
                    unsafe_allow_html=True,
                )

            if row.warning:
                st.markdown(
                    f"""
<div class="drug-detail">

⚠️ <b>คำเตือน :</b>

{row.warning}

</div>
""",
                    unsafe_allow_html=True,
                )

            if row.note:
                st.markdown(
                    f"""
<div class="drug-detail">

📌 <b>หมายเหตุ :</b>

{row.note}

</div>
""",
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
</div>
""",
                unsafe_allow_html=True,
            )

# ======================================================
# 🗂 CATEGORY VIEW
# ======================================================

elif view_mode == "🗂 จัดตามหมวดหมู่":

    if len(df_filter) == 0:
        st.warning("ไม่พบข้อมูล")
    else:

        df_group = df_filter.copy()

        # เรียงข้อมูล
        df_group = df_group.sort_values(
            by=[
                "subtype1_name",
                "subtype2_name",
                "subtype3_name",
                "subtype4_name",
                "drug_name"
            ]
        )

        for subtype1, g1 in df_group.groupby("subtype1_name"):

            st.markdown(
                f"""
<div class="group-box">

🟣 {subtype1}

</div>
""",
                unsafe_allow_html=True
            )

            g1 = g1.fillna("")

            for subtype2, g2 in g1.groupby("subtype2_name"):

                if subtype2.strip():

                    st.markdown(
                        f"""
<div class="subgroup2">

🔷 {subtype2}

</div>
""",
                        unsafe_allow_html=True
                    )

                for subtype3, g3 in g2.groupby("subtype3_name"):

                    if subtype3.strip():

                        st.markdown(
                            f"""
<div class="subgroup3">

▸ {subtype3}

</div>
""",
                            unsafe_allow_html=True
                        )

                    for subtype4, g4 in g3.groupby("subtype4_name"):

                        if subtype4.strip():

                            st.markdown(
                                f"""
<div class="subgroup4">

• {subtype4}

</div>
""",
                                unsafe_allow_html=True
                            )

                        for row in g4.itertuples():

                            render_card(row._asdict())






# ========== FOOTER ==========
st.markdown("---")
st.caption("© กลุ่มงานเภสัชกรรม")
