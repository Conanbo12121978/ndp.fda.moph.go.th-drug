import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Drug Finder",
    page_icon="💊",
    layout="wide"
)

# ======================================================
# LOAD DATA
# ======================================================

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
        "บัญชีใหม่": "account_sub",
        "ประเภทยา": "drug_type",
        "เงื่อนไข": "condition",
        "คำเตือน": "warning",
        "หมายเหตุ": "note"
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

# ======================================================
# ACCOUNT COLOR
# ======================================================

def account_color(account):

    account = str(account).strip()

    colors = {

        "b": "#3b82f6",
        "s": "#10b981",
        "ex": "#eab308",
        "R1": "#f97316",
        "R2": "#ec4899",

        "A": "#3b82f6",
        "B": "#10b981",
        "C": "#eab308",

        "นอกบัญชี": "#9ca3af",
        "บัญชียาจากสมุนไพร": "#8b5a2b"

    }

    return colors.get(account, "#8b5cf6")

# ======================================================
# DOWNLOAD EXCEL
# ======================================================

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
<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
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

# ======================================================
# DRUG CARD
# ======================================================

def render_card(row):

    color = account_color(
        row["account_sub"]
    )

    dosage = row.get("dosage", "")
    account = row.get("account_drug_ID", "-")
    sub = row.get("account_sub", "")
    drug_type = row.get("drug_type", "")

    html = f"""
<div class="drug-card"
style="border-left:7px solid {color};">

<div class="drug-name">

💊 {row["drug_name"]}

</div>

<div class="drug-detail">

🏷️ <b>บัญชี :</b> {account}
</div>

<div class="drug-detail">

📑 <b>บัญชีใหม่ :</b> {sub}

</div>
"""

    if dosage:

        html += f"""

<div class="drug-detail">

💉 {dosage} 

</div>
"""

    if drug_type:
        html += f"""
<div class="drug-detail">

🧪 {drug_type}

</div>
"""

    if row.get("condition", ""):
        html += f"""
<div class="drug-detail">

📝 {row["condition"]}

</div>
"""

    if row.get("warning", ""):
        html += f"""
<div class="drug-detail">

⚠️ {row["warning"]}

</div>
"""

    if row.get("note", ""):
        html += f"""
<div class="drug-detail">

📌 {row["note"]}

</div>
"""

    html += "</div>"

    st.markdown(
        html,
        unsafe_allow_html=True
    )

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>

.block-container{
    padding-top:25px;
}

.group-box{
    background:#ede9fe;
    border-left:8px solid #7c3aed;
    border-radius:10px;
    padding:14px 18px;
    margin-top:24px;
    margin-bottom:12px;
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

# ======================================================
# HEADER
# ======================================================

st.title("💊 บัญชียาหลักแห่งชาติ พ.ศ. 2569")
st.caption("ค้นหายา • จัดหมวดหมู่ • ดาวน์โหลดข้อมูล Excel")

# ======================================================
# SESSION STATE
# ======================================================

defaults = {
    "subtype1": "--ทั้งหมด--",
    "subtype2": "--ทั้งหมด--",
    "subtype3": "--ทั้งหมด--",
    "account": "--ทั้งหมด--",
    "account_sub": "--ทั้งหมด--",
    "search": "",
    "view_mode": "📋 รายการยา"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ======================================================
# CLEAR FILTER
# ======================================================

if st.button("🔄 เคลียร์ตัวกรองทั้งหมด"):

    for key, value in defaults.items():
        st.session_state[key] = value

    st.rerun()

# ======================================================
# FILTER
# ======================================================

df_filter = df.copy()

col1, col2 = st.columns(2)

# ----------------------------
# subtype1
# ----------------------------

with col1:

    subtype1_list = ["--ทั้งหมด--"] + sorted(
        df["subtype1_name"].dropna().unique()
    )

    subtype1 = st.selectbox(
        "ประเภทหลัก",
        subtype1_list,
        key="subtype1"
    )

if subtype1 != "--ทั้งหมด--":

    df_filter = df_filter[
        df_filter["subtype1_name"] == subtype1
    ]

# ----------------------------
# subtype2
# ----------------------------

with col2:

    subtype2_list = ["--ทั้งหมด--"] + sorted(
        df_filter["subtype2_name"].dropna().unique()
    )

    subtype2 = st.selectbox(
        "ประเภทรอง",
        subtype2_list,
        key="subtype2"
    )

if subtype2 != "--ทั้งหมด--":

    df_filter = df_filter[
        df_filter["subtype2_name"] == subtype2
    ]

# ----------------------------
# subtype3
# ----------------------------

subtype3_list = ["--ทั้งหมด--"] + sorted(
    df_filter["subtype3_name"].dropna().unique()
)

subtype3 = st.selectbox(
    "ประเภทย่อย",
    subtype3_list,
    key="subtype3"
)

if subtype3 != "--ทั้งหมด--":

    df_filter = df_filter[
        df_filter["subtype3_name"] == subtype3
    ]

# ======================================================
# ACCOUNT
# ======================================================

col3, col4 = st.columns(2)

with col3:

    account_list = ["--ทั้งหมด--"] + sorted(
        df["account_drug_ID"].dropna().unique()
    )

    account = st.selectbox(
        "บัญชียา",
        account_list,
        key="account"
    )

if account != "--ทั้งหมด--":

    df_filter = df_filter[
        df_filter["account_drug_ID"] == account
    ]

with col4:

    account_sub_list = ["--ทั้งหมด--"] + sorted(
        df["account_sub"].dropna().unique()
    )

    account_sub = st.selectbox(
        "บัญชีใหม่",
        account_sub_list,
        key="account_sub"
    )

if account_sub != "--ทั้งหมด--":

    df_filter = df_filter[
        df_filter["account_sub"] == account_sub
    ]

# ======================================================
# SEARCH
# ======================================================

search = st.text_input(
    "🔍 ค้นหาชื่อยา",
    key="search",
    placeholder="เช่น Paracetamol"
)

if search:

    df_filter = df_filter[
        df_filter["drug_name"]
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]

# ======================================================
# SUMMARY
# ======================================================

st.markdown(
    excel_download(df_filter),
    unsafe_allow_html=True
)

st.caption(
    f"พบข้อมูลทั้งหมด **{len(df_filter):,}** รายการ"
)

# ======================================================
# VIEW MODE
# ======================================================

view_mode = st.radio(
    "รูปแบบการแสดงผล",
    [
        "📋 รายการยา",
        "🗂 จัดตามหมวดหมู่"
    ],
    horizontal=True,
    key="view_mode"
)
# ======================================================
# 📋 LIST VIEW
# ======================================================

if view_mode == "📋 รายการยา":

    if df_filter.empty:

        st.info("ไม่พบข้อมูล")

    else:

        df_show = df_filter.copy()

        df_show = df_show.sort_values(
            by=[
                "drug_name",
                "account_drug_ID"
            ]
        )

        st.subheader(
            f"📋 พบ {len(df_show):,} รายการ"
        )

        for _, row in df_show.iterrows():

            render_card(row)

# ======================================================
# 🗂 CATEGORY VIEW
# ======================================================

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
            "drug_name"
        ]

        for c in cols:

            df_show[c] = (
                df_show[c]
                .fillna("")
                .astype(str)
            )

        df_show = df_show.sort_values(
            by=cols
        )

        # ----------------------------
        # subtype1
        # ----------------------------

        for subtype1, g1 in df_show.groupby(
            "subtype1_name",
            dropna=False
        ):

            st.markdown(
                f"""
<div class="group-box">

🟣 {subtype1 if subtype1 else 'ไม่ระบุ'}

</div>
""",
                unsafe_allow_html=True
            )

            # ----------------------------
            # subtype2
            # ----------------------------

            for subtype2, g2 in g1.groupby(
                "subtype2_name",
                dropna=False
            ):

                if subtype2:

                    st.markdown(
                        f"""
<div class="subgroup2">

🔷 {subtype2}

</div>
""",
                        unsafe_allow_html=True
                    )

                # ----------------------------
                # subtype3
                # ----------------------------

                for subtype3, g3 in g2.groupby(
                    "subtype3_name",
                    dropna=False
                ):

                    if subtype3:

                        st.markdown(
                            f"""
<div class="subgroup3">

▸ {subtype3}

</div>
""",
                            unsafe_allow_html=True
                        )

                    # ----------------------------
                    # subtype4
                    # ----------------------------

                    for subtype4, g4 in g3.groupby(
                        "subtype4_name",
                        dropna=False
                    ):

                        if subtype4:

                            st.markdown(
                                f"""
<div class="subgroup4">

• {subtype4}

</div>
""",
                                unsafe_allow_html=True
                            )

                        for _, row in g4.iterrows():

                            render_card(row)

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.caption(
        f"📊 จำนวนข้อมูลทั้งหมด : {len(df_filter):,} รายการ"
    )

with col2:
    st.caption(
        "💊 ข้อมูลบัญชียาหลักแห่งชาติ พ.ศ. 2569"
    )

st.markdown(
    """
<div style="
text-align:center;
padding:15px;
color:#888;
font-size:13px;
">

จัดทำโดย กลุ่มงานเภสัชกรรม<br>
โรงพยาบาลท้ายเหมืองชัยพัฒน์

</div>
""",
    unsafe_allow_html=True
)
