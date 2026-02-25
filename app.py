import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import Table
from datetime import datetime
import os

st.set_page_config(page_title="LLC Operating Agreement Maker", layout="centered")

st.title("📄 LLC Operating Agreement PDF Generator")

# ---------- FORM ----------
with st.form("operating_agreement_form"):
    company_name = st.text_input("LLC Name")
    state = st.text_input("State of Formation")
    formation_date = st.date_input("Formation Date", datetime.today())
    business_purpose = st.text_area("Business Purpose")
    duration = st.selectbox("Duration", ["Perpetual", "Specific Term"])
    duration_details = ""
    if duration == "Specific Term":
        duration_details = st.text_input("Specify Duration")

    management_type = st.selectbox("Management Type", ["Member-Managed", "Manager-Managed"])

    st.subheader("Members")

    num_members = st.number_input("Number of Members", min_value=1, max_value=10, value=1)

    members = []
    for i in range(num_members):
        st.markdown(f"### Member {i+1}")
        name = st.text_input(f"Name {i}", key=f"name_{i}")
        address = st.text_input(f"Address {i}", key=f"address_{i}")
        ownership = st.number_input(f"Ownership % {i}", min_value=0.0, max_value=100.0, key=f"ownership_{i}")
        members.append({
            "name": name,
            "address": address,
            "ownership": ownership
        })

    submit = st.form_submit_button("Generate Operating Agreement PDF")


# ---------- PDF GENERATOR ----------
def generate_pdf():
    file_path = "Operating_Agreement.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=LETTER)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    heading = styles["Heading1"]

    elements.append(Paragraph(f"{company_name} LLC OPERATING AGREEMENT", heading))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"This Operating Agreement is entered into on {formation_date.strftime('%B %d, %Y')} for {company_name} LLC, formed in the State of {state}.", normal))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>1. Formation</b>", styles["Heading2"]))
    elements.append(Paragraph(f"The Members hereby form a Limited Liability Company under the laws of {state}.", normal))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>2. Purpose</b>", styles["Heading2"]))
    elements.append(Paragraph(business_purpose, normal))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>3. Duration</b>", styles["Heading2"]))
    if duration == "Perpetual":
        elements.append(Paragraph("The Company shall exist perpetually.", normal))
    else:
        elements.append(Paragraph(f"The Company shall exist for {duration_details}.", normal))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>4. Management</b>", styles["Heading2"]))
    elements.append(Paragraph(f"This Company shall be {management_type}.", normal))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>5. Members and Ownership</b>", styles["Heading2"]))
    for member in members:
        elements.append(Paragraph(
            f"{member['name']}, Address: {member['address']}, Ownership: {member['ownership']}%",
            normal
        ))
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("IN WITNESS WHEREOF, the Members execute this Agreement:", styles["Heading2"]))
    elements.append(Spacer(1, 0.3 * inch))

    for member in members:
        elements.append(Paragraph(f"______________________________", normal))
        elements.append(Paragraph(f"{member['name']}", normal))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    return file_path


# ---------- DOWNLOAD ----------
if submit:
    pdf_file = generate_pdf()

    with open(pdf_file, "rb") as f:
        st.success("Operating Agreement Generated Successfully!")
        st.download_button(
            label="📥 Download PDF",
            data=f,
            file_name="LLC_Operating_Agreement.pdf",
            mime="application/pdf"
        )
