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
# SUB ACCOUNT STYLE
# =====================================================

def sub_account_style(sub):

    sub = str(sub).strip()

    styles = {

        "b": {
            "border": "#2563eb",
            "bg": "#DBEAFE",
            "text": "#1D4ED8"
        },

        "s": {
            "border": "#16A34A",
            "bg": "#DCFCE7",
            "text": "#15803D"
        },

        "ex": {
            "border": "#F59E0B",
            "bg": "#FEF3C7",
            "text": "#B45309"
        },

        "R1": {
            "border": "#EC4899",
            "bg": "#FCE7F3",
            "text": "#BE185D"
        },

        "R2": {
            "border": "#EF4444",
            "bg": "#FEE2E2",
            "text": "#B91C1C"
        },

        "": {
            "border": "#9CA3AF",
            "bg": "#F3F4F6",
            "text": "#6B7280"
        }

    }

    return styles.get(
        sub,
        {
            "border": "#7C3AED",
            "bg": "#EDE9FE",
            "text": "#6D28D9"
        }
    )


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
<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
download="DrugList.xlsx"
style="
background:#2563EB;
color:white;
padding:10px 18px;
border-radius:8px;
font-weight:600;
text-decoration:none;
display:inline-block;
">
📥 ดาวน์โหลด Excel
</a>
"""

# =====================================================
# DRUG CARD
# =====================================================

def render_card(row, dosage_text=""):

    sub = str(row.get("account_sub", ""))

    style = sub_account_style(sub)

    drug_name = row.get("drug_name", "")
    account = row.get("account_drug_ID", "")

    drug_type = row.get("drug_type", "")
    condition = row.get("condition", "")
    warning = row.get("warning", "")
    note = row.get("note", "")

    html = f"""

<div class="drug-card"
style="border-left:8px solid {style['border']};">

    <div class="drug-name">

        💊 {drug_name}

    </div>

    <div class="drug-account">

        <span
        class="new-account"

        style="
        background:{style['bg']};
        ">

            📑 บัญชีใหม่ :

            <span
            class="sub-code"

            style="
            color:{style['text']};
            ">

                {sub}

            </span>

        </span>

        <span class="old-account">

            บัญชีเดิม : {account}

        </span>

    </div>

"""

    if dosage_text:

        html += f"""

<div class="drug-detail">

💉 {dosage_text}

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

    html += """

</div>

"""

    st.markdown(
        html,
        unsafe_allow_html=True
    )

# ====================================================
# CSS
# ====================================================

st.markdown("""
<style>

/* =====================================================
   PAGE
===================================================== */

.block-container{
    padding-top:22px;
    padding-bottom:40px;
}

/* =====================================================
   GROUP
===================================================== */

.group-box{

    background:#ede9fe;
    border-left:8px solid #7c3aed;

    border-radius:12px;

    padding:14px 18px;

    margin-top:28px;
    margin-bottom:14px;

    font-size:24px;
    font-weight:700;

    color:#4c1d95;

}

.subgroup2{

    margin-top:18px;
    margin-left:10px;

    font-size:20px;
    font-weight:700;

    color:#5b21b6;

}

.subgroup3{

    margin-top:14px;
    margin-left:28px;

    font-size:18px;
    font-weight:700;

    color:#6d28d9;

}

.subgroup4{

    margin-top:12px;
    margin-left:48px;

    font-size:16px;
    font-weight:700;

    color:#7e22ce;

}

/* =====================================================
   DRUG CARD
===================================================== */

.drug-card{

    background:white;

    border:1px solid #e5e7eb;

    border-radius:12px;

    padding:16px;

    margin-left:56px;
    margin-bottom:12px;

    box-shadow:0 2px 6px rgba(0,0,0,.06);

}

.drug-name{

    font-size:20px;
    font-weight:700;

    color:#111827;

    margin-bottom:10px;

}

.drug-account{

    display:flex;

    align-items:center;

    gap:10px;

    margin-bottom:10px;

    flex-wrap:wrap;

}

.new-account{

    display:inline-flex;

    align-items:center;

    padding:5px 12px;

    border-radius:999px;

    font-size:14px;

    font-weight:700;

}

.sub-code{

    margin-left:6px;

    font-size:15px;

    font-weight:800;

}

.old-account{

    font-size:14px;

    color:#6b7280;

    font-weight:600;

}

.drug-detail{

    margin-top:6px;

    font-size:14px;

    color:#4b5563;

    line-height:1.6;

}

/* =====================================================
   DARK MODE
===================================================== */

[data-theme="dark"] .group-box{

    background:#312e81;

    color:white;

}

[data-theme="dark"] .subgroup2{

    color:#c4b5fd;

}

[data-theme="dark"] .subgroup3{

    color:#ddd6fe;

}

[data-theme="dark"] .subgroup4{

    color:#ede9fe;

}

[data-theme="dark"] .drug-card{

    background:#1f2937;

    border-color:#4b5563;

}

[data-theme="dark"] .drug-name{

    color:#ffffff;

}

[data-theme="dark"] .old-account{

    color:#d1d5db;

}

[data-theme="dark"] .drug-detail{

    color:#e5e7eb;

}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.title("💊 Drug Finder")

st.caption("ค้นหารายการยาและจัดเรียงตามหมวดหมู่")

st.divider()

# =====================================================
# SEARCH
# =====================================================

search = st.text_input(
    "🔍 ค้นหาชื่อยา",
    placeholder="พิมพ์ชื่อยา..."
).strip()

# =====================================================
# VIEW MODE
# =====================================================

view_mode = st.radio(

    "รูปแบบการแสดง",

    [

        "🗂 จัดตามหมวดหมู่",
        "📋 รายการยา"

    ],

    horizontal=True,

    index=0

)

st.divider()

# =====================================================
# FILTER
# =====================================================

df_filter = df.copy()

if search:

    keyword = search.lower()

    df_filter = df_filter[

        df_filter["drug_name"]
        .str.lower()
        .str.contains(keyword, na=False)

    ]

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("ตัวกรอง")

# ---------- subtype1 ----------

sub1_list = sorted(
    df["subtype1_name"].dropna().unique(),
    key=sort_number
)

sub1 = st.sidebar.multiselect(

    "หมวดหลัก",

    options=sub1_list

)

if sub1:

    df_filter = df_filter[
        df_filter["subtype1_name"].isin(sub1)
    ]

# ---------- subtype2 ----------

sub2_list = sorted(
    df_filter["subtype2_name"].dropna().unique(),
    key=sort_number
)

sub2 = st.sidebar.multiselect(

    "หมวดย่อย",

    options=sub2_list

)

if sub2:

    df_filter = df_filter[
        df_filter["subtype2_name"].isin(sub2)
    ]

# ---------- subtype3 ----------

sub3_list = sorted(
    df_filter["subtype3_name"].dropna().unique(),
    key=sort_number
)

sub3 = st.sidebar.multiselect(

    "หมวดย่อย 2",

    options=sub3_list

)

if sub3:

    df_filter = df_filter[
        df_filter["subtype3_name"].isin(sub3)
    ]

# ---------- subtype4 ----------

sub4_list = sorted(
    df_filter["subtype4_name"].dropna().unique(),
    key=sort_number
)

sub4 = st.sidebar.multiselect(

    "หมวดย่อย 3",

    options=sub4_list

)

if sub4:

    df_filter = df_filter[
        df_filter["subtype4_name"].isin(sub4)
    ]

st.sidebar.markdown("---")

st.sidebar.markdown(

    excel_download(df_filter),

    unsafe_allow_html=True

)

st.write(f"พบข้อมูล **{len(df_filter):,}** รายการ")

# =====================================================
# LIST VIEW
# =====================================================

if view_mode == "📋 รายการยา":

    if df_filter.empty:

        st.info("ไม่พบข้อมูล")

    else:

        df_show = df_filter.copy()

        for col in [

            "drug_name",
            "account_sub",
            "dosage"

        ]:

            if col in df_show.columns:

                df_show[col] = (
                    df_show[col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

        df_show = df_show.sort_values(

            by=[

                "drug_name",
                "account_sub"

            ]

        )

        # ==========================
        # รวม dosage
        # ==========================

        for (drug_name, account_sub), group in df_show.groupby(

            [

                "drug_name",
                "account_sub"

            ],

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

                d

                for d in dosage_list

                if d

            ]

            dosage_text = " • ".join(

                sorted(

                    set(dosage_list)

                )

            )

            render_card(

                row,

                dosage_text

            )
# =====================================================
# CATEGORY VIEW
# =====================================================

elif view_mode == "🗂 จัดตามหมวดหมู่":

    if df_filter.empty:

        st.info("ไม่พบข้อมูล")

    else:

        df_show = df_filter.copy()

        # --------------------------------------------
        # Clean
        # --------------------------------------------

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

                    .str.strip()

                )

        # --------------------------------------------
        # Sort
        # --------------------------------------------

        df_show["sort1"] = df_show["subtype1_name"].apply(sort_number)
        df_show["sort2"] = df_show["subtype2_name"].apply(sort_number)
        df_show["sort3"] = df_show["subtype3_name"].apply(sort_number)
        df_show["sort4"] = df_show["subtype4_name"].apply(sort_number)

        df_show = df_show.sort_values(

            by=[

                "sort1",
                "sort2",
                "sort3",
                "sort4",

                "subtype1_name",
                "subtype2_name",
                "subtype3_name",
                "subtype4_name",

                "drug_name",
                "account_sub"

            ]

        )

        # =================================================
        # subtype1
        # =================================================

        for subtype1, g1 in df_show.groupby("subtype1_name", sort=False):

            st.markdown(

                f"""
<div class="group-box">
🟣 {subtype1 if subtype1 else "ไม่ระบุ"}
</div>
""",

                unsafe_allow_html=True

            )

            # =============================================

            for subtype2, g2 in g1.groupby("subtype2_name", sort=False):

                if subtype2:

                    st.markdown(

                        f"""
<div class="subgroup2">
🔷 {subtype2}
</div>
""",

                        unsafe_allow_html=True

                    )

                # =========================================

                for subtype3, g3 in g2.groupby("subtype3_name", sort=False):

                    if subtype3:

                        st.markdown(

                            f"""
<div class="subgroup3">
▸ {subtype3}
</div>
""",

                            unsafe_allow_html=True

                        )

                    # =====================================

                    for subtype4, g4 in g3.groupby("subtype4_name", sort=False):

                        if subtype4:

                            st.markdown(

                                f"""
<div class="subgroup4">
• {subtype4}
</div>
""",

                                unsafe_allow_html=True

                            )

                        # =====================================
                        # รวม dosage
                        # =====================================

                        for (

                            drug_name,
                            account_sub

                        ), group in g4.groupby(

                            [

                                "drug_name",
                                "account_sub"

                            ],

                            sort=False

                        ):

                            row = group.iloc[0]

                            dosage_list = (

                                group["dosage"]

                                .dropna()

                                .astype(str)

                                .str.strip()

                            )

                            dosage_list = sorted(

                                set(

                                    d

                                    for d in dosage_list

                                    if d

                                )

                            )

                            dosage_text = " • ".join(

                                dosage_list

                            )

                            render_card(

                                row,

                                dosage_text

                            )








