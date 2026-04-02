import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# ========== ฟังก์ชันดาวน์โหลด Excel ==========
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Drugs')
    b64 = base64.b64encode(output.getvalue()).decode()
    return f"""
    <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
       download="filtered_drugs.xlsx" style="
       text-decoration: none;
       background-color: #2563eb;
       color: white;
       padding: 8px 16px;
       border-radius: 6px;
       display: inline-block;
       margin-top: 10px;
    ">
       📥 ดาวน์โหลด Excel
    </a>
    """

# 🎨 ฟังก์ชันเลือกสี border-left ตามบัญชียา
def get_border_color(account_id):
    account_id = str(account_id).strip()
    color_map = {
        "ก": "#38bdf8",
        "ข": "#4ade80",
        "ค": "#facc15",
        "ง": "#fb923c",
        "จ(1)": "#f472b6",
        "นอกบัญชี": "#a3a3a3",
        "จ(2)": "#7a3a1d",
    }
    return color_map.get(account_id, "#d1c4e9")

# ========== เริ่ม Streamlit ==========
st.set_page_config(page_title="Drug Finder", page_icon="💊", layout="centered")

# โหลดข้อมูล
df = pd.read_excel("druglist.xlsx")
# แก้ปัญหา _x000d_ โดยลบออกจากทุก column ที่เป็นข้อความ
df = df.replace('_x000d_', ' ', regex=True)
# หัวเรื่อง
st.markdown('<h3 style="margin-bottom: 0; color: #006ebc;">📖 บัญชียาหลักแห่งชาติ edit ฉ.67 (2)</h3>', unsafe_allow_html=True)
# CSS รองรับ dark mode
st.markdown("""
<style>
:root {
  --text-color: #111827;
}
[data-theme="dark"] {
  --text-color: #F1F5F9;
}

.drug-card {
    padding: 8px 14px;
    margin-bottom: 8px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 15px;
    color: var(--text-color);
}
.group-box {
    padding: 12px;
    background-color: #ede9fe;
    border: 2px solid #6D28D9;
    border-radius: 6px;
    margin-top: 16px;
    margin-bottom: 8px;
    color: var(--text-color);
}
[data-theme="dark"] .group-box {
    background-color: #3b0764;
    border-color: #c084fc;
}
.subgroup-title {
    margin-top: 12px;
    font-weight: bold;
    color: #4B0082;
}
[data-theme="dark"] .subgroup-title {
    color: #c4b5fd;
}
/* กล่องยา (.drug-card) สีพื้นต่างกันตามธีม */
.drug-card {
    background-color: #ffffff;  /* พื้นหลังขาวสำหรับโหมดสว่าง */
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px 14px;
    margin-bottom: 8px;
    font-size: 15px;
    color: var(--text-color);
}

[data-theme="dark"] .drug-card {
    background-color: #1f2937;  /* พื้นหลังเข้มในโหมดมืด */
    border: 1px solid #4b5563;
}

/* สีข้อความชื่อยา */
.drug-card strong {
    color: #111827;
}
[data-theme="dark"] .drug-card strong {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ปุ่มเคลียร์ตัวกรอง
if st.button("🔄 เคลียร์ตัวกรองทั้งหมด"):
    st.session_state["subtype1_filter"] = "--ทั้งหมด--"
    st.session_state["subtype2_filter"] = "--ทั้งหมด--"
    st.session_state["subtype3_filter"] = "--ทั้งหมด--"
    st.session_state["account_filter"] = "--ทั้งหมด--"
    st.session_state["search_text"] = ""
    st.session_state["sort_mode"] = "เรียงตามชื่อยา"

# ตัวเลือกการเรียง
sort_mode = st.radio("🧭 เรียงข้อมูลโดย", ["เรียงตามชื่อยา", "เรียงตามกลุ่มยา"], key="sort_mode", horizontal=True)

# ตัวกรอง subtype1, subtype2, subtype3, account, search
subtype1_list = df["subtype1_name"].dropna().unique()
selected_subtype1 = st.selectbox("เลือกประเภทหลัก", ["--ทั้งหมด--"] + sorted(subtype1_list), key="subtype1_filter")
if selected_subtype1 != "--ทั้งหมด--":
    df = df[df["subtype1_name"] == selected_subtype1]

subtype2_list = df["subtype2_name"].dropna().unique()
selected_subtype2 = st.selectbox("เลือกประเภทรอง", ["--ทั้งหมด--"] + sorted(subtype2_list), key="subtype2_filter")
if selected_subtype2 != "--ทั้งหมด--":
    df = df[df["subtype2_name"] == selected_subtype2]

subtype3_list = df["subtype3_name"].dropna().unique()
selected_subtype3 = st.selectbox("เลือกประเภทย่อย", ["--ทั้งหมด--"] + sorted(subtype3_list), key="subtype3_filter")
if selected_subtype3 != "--ทั้งหมด--":
    df = df[df["subtype3_name"] == selected_subtype3]

account_list = df["account_drug_ID"].dropna().unique()
selected_account = st.selectbox("เลือกบัญชียา", ["--ทั้งหมด--"] + sorted(account_list), key="account_filter")
if selected_account != "--ทั้งหมด--":
    df = df[df["account_drug_ID"] == selected_account]

search_text = st.text_input("🔍 พิมพ์ชื่อยา", key="search_text")
if search_text.strip():
    df = df[df["drug_name"].fillna("").str.contains(search_text, case=False)]

# ปุ่มดาวน์โหลด Excel (ด้านบน)
st.markdown(to_excel_download(df), unsafe_allow_html=True)

# Caption แสดงเงื่อนไข
st.caption(f"🎯 ตัวกรอง: {selected_subtype1} > {selected_subtype2} > {selected_subtype3} > {selected_account} | ค้นหา: {search_text if search_text else '-'}")

# ถ้าเรียงตามชื่อยา: ใช้โค้ดเดิม
if sort_mode == "เรียงตามชื่อยา":
    unique_drugs = df["drug_name"].dropna().unique()
    st.subheader(f"📋 พบ {len(unique_drugs)} รายการ (ชื่อยาไม่ซ้ำ)")
    if len(unique_drugs) == 0:
        st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
    else:
        for drug in sorted(unique_drugs, key=lambda x: str(x)):
            entries = df[df["drug_name"] == drug]
            if len(entries) == 1:
                row = entries.iloc[0]
                dosage = row.get("dosage", "-")
                dosage = dosage if pd.notna(dosage) and str(dosage).strip() != "" else "-"
                color = get_border_color(row['account_drug_ID'])
                group_parts = [
                    str(row.get("subtype1_name", "")).strip(),
                    str(row.get("subtype2_name", "")).strip(),
                    str(row.get("subtype3_name", "")).strip(),
                    str(row.get("subtype4_name", "")).strip()
                ]
                group_info = " > ".join([g for g in group_parts if g and g.lower() != "nan"])
                st.markdown(f"""
                <div class="drug-card" style="border-left: 6px solid {color};">
                    <strong>{row['drug_name']}</strong><br>
                    <div style="color: #888;">{dosage}</div>
                    <span style="color: #888;">[บัญชี: {row['account_drug_ID'] if pd.notna(row['account_drug_ID']) else ''}]</span><br>
                    <span style="color: #888;">กลุ่ม: {group_info if group_info else 'ไม่ระบุ'}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.expander(f"💊 {drug} ({len(entries)} กลุ่มยา)"):
                    for _, row in entries.iterrows():
                        dosage = row.get("dosage", "-")
                        dosage = dosage if pd.notna(dosage) and str(dosage).strip() != "" else "-"
                        color = get_border_color(row['account_drug_ID'])
                        group_parts = [
                            str(row.get("subtype1_name", "")).strip(),
                            str(row.get("subtype2_name", "")).strip(),
                            str(row.get("subtype3_name", "")).strip(),
                            str(row.get("subtype4_name", "")).strip()
                        ]
                        group_info = " > ".join([g for g in group_parts if g and g.lower() != "nan"])
                        st.markdown(f"""
                        <div class="drug-card" style="border-left: 6px solid {color};">
                            <strong>{row['drug_name']}</strong><br> 
                            <div style="color: #888;">{dosage}</div>
                            <span style="color: #888;">[บัญชี: {row['account_drug_ID'] if pd.notna(row['account_drug_ID']) else ''}]</span><br>
                            <span style="color: #888;">กลุ่ม: {group_info if group_info else 'ไม่ระบุ'}</span>
                        </div>
                        """, unsafe_allow_html=True)

# ถ้าเรียงตามกลุ่มยา: ใช้กรอบใหญ่ตาม subtype1_name แยกย่อย subtype2/3
else:
    st.subheader("🧪 เรียงตามกลุ่มยา")
     # ✅ วางตรงนี้
    account_order_map = {
        "ก": 1,
        "ข": 2,
        "ค": 3,
        "ง": 4,
        "จ": 5,
        "นอกบัญชี": 6,
        "บัญชียาจากสมุนไพร": 7
    }
    df["account_order"] = df["account_drug_ID"].map(account_order_map).fillna(99)
    df = df[df["drug_name"].notna() & (df["drug_name"].str.strip() != "")]
    
    # ✨ แก้ตรงนี้
    df["drug_name_lower"] = df["drug_name"].str.lower()
    df = df.sort_values(by=["subtype1_name", "subtype2_name", "subtype3_name", "account_order", "drug_name_lower"])
    df = df.drop(columns=["drug_name_lower"])

    for subtype1, group1 in df.groupby("subtype1_name"):
        st.markdown(f"<div class='group-box'><strong>🟣 {subtype1}</strong></div>", unsafe_allow_html=True)

        group1_mod = group1.copy()
        group1_mod["subtype2_name"] = group1_mod["subtype2_name"].fillna("")
        for subtype2, group2 in group1_mod.groupby("subtype2_name"):
            if subtype2:
                st.markdown(f"<div class='subgroup-title'>🔹 {subtype2}</div>", unsafe_allow_html=True)
            group2_mod = group2.copy()
            group2_mod["subtype3_name"] = group2_mod["subtype3_name"].fillna("")
            for subtype3, group3 in group2_mod.groupby("subtype3_name"):
                if subtype3:
                    st.markdown(f"<div style='margin-left:10px;font-weight:bold;color:#9C27B0;'>⇨ {subtype3}</div>", unsafe_allow_html=True)
                group3 = group3.copy()
                group3["subtype4_name"] = group3["subtype4_name"].fillna("")
                for subtype4, group4 in group3.groupby("subtype4_name"):
                    if subtype4:
                        st.markdown(f"<div style='margin-left:20px;font-weight:bold;color:#A83279;'>▪ {subtype4}</div>", unsafe_allow_html=True)
                    for _, row in group4.iterrows():
                        color = get_border_color(row['account_drug_ID'])
                        drug_name = row['drug_name']
                        dosage = row.get("dosage", "-")
                        dosage = dosage if pd.notna(dosage) and str(dosage).strip() != "" else "-"
                        account = row['account_drug_ID'] if pd.notna(row['account_drug_ID']) else "-"
                        drug_type = row['ประเภทยา'] if pd.notna(row['ประเภทยา']) else "-"
                        
                        advice = row.get("advice", "")
                        condition = row.get("condition", "")
                        warning = row.get("warning", "")
                        note = row.get("note", "")

                        

                        # ตรวจสอบว่ามีอย่างน้อย 1 ช่องที่ไม่ว่าง และไม่ใช่ "nan"
                        has_details = any([
                            pd.notna(advice) and str(advice).strip() != "",
                            pd.notna(condition) and str(condition).strip() != "",
                            pd.notna(warning) and str(warning).strip() != "",
                            pd.notna(note) and str(note).strip() != ""
                        ])

                        details_html = ""
                        if has_details:
                            details_html += "<details style='margin-left: 22px; margin-top: 6px;'>"
                            details_html += "<summary style='cursor: pointer; color: #2563eb;'>📌 รายละเอียดเพิ่มเติม</summary><div style='padding-left:10px;'>"

                            if pd.notna(advice) and str(advice).strip() != "":
                                details_html += f"<div style='color:#1e40af;'><b>คำแนะนำ:</b> {advice}</div>"
                            if pd.notna(condition) and str(condition).strip() != "":
                               details_html += f"<div style='color:#047857;'><b>เงื่อนไข:</b> {condition}</div>"
                            if pd.notna(warning) and str(warning).strip() != "":
                               details_html += f"<div style='color:#b91c1c;'><b>คำเตือนและข้อควรระวัง:</b> {warning}</div>"
                            if pd.notna(note) and str(note).strip() != "":
                               details_html += f"<div style='color:#6b21a8;'><b>หมายเหตุ:</b> {note}</div>"

                            details_html += "</div></details>"
                   
                    

                        group_parts = [
                            str(row.get("subtype1_name", "")).strip(),
                            str(row.get("subtype2_name", "")).strip(),
                            str(row.get("subtype3_name", "")).strip(),
                            str(row.get("subtype4_name", "")).strip()
                        ]
                        group_info = " > ".join([g for g in group_parts if g and g.lower() != "nan"])
                        st.markdown(f"""
                       <div class="drug-card" style="border-left: 6px solid {color}; margin-left: 20px;">
                           💊 <strong>{drug_name}</strong><br>
                           <div style="margin-left: 22px; color: #888;">{dosage}</div>
                           <span style="margin-left: 22px; color: #888;">บัญชี: {account}</span><br>
                           <span style="margin-left: 22px; color: #888;">ประเภทยา: {drug_type}</span><br>
                           {details_html}
                       </div>
                       """, unsafe_allow_html=True)

# ปุ่มดาวน์โหลด Excel (ด้านล่าง)
st.markdown(to_excel_download(df), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("จัดทำโดย กลุ่มงานเภสัชกรรม รพ.ท้ายเหมืองชัยพัฒน์ | © 2568")
