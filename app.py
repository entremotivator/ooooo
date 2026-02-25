import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table
from datetime import datetime
import os

st.set_page_config(page_title="Professional LLC Operating Agreement Generator", layout="centered")

st.title("🏛 Professional LLC Operating Agreement Generator")

# =========================
# FORM SECTION
# =========================
with st.form("agreement_form"):

    st.header("Company Information")
    company_name = st.text_input("LLC Name")
    state = st.text_input("State of Formation")
    formation_date = st.date_input("Formation Date", datetime.today())
    principal_address = st.text_input("Principal Office Address")

    st.header("Business Details")
    purpose = st.text_area("Business Purpose")
    duration = st.selectbox("Company Duration", ["Perpetual", "Specific Term"])
    duration_detail = ""
    if duration == "Specific Term":
        duration_detail = st.text_input("Specify Duration Term")

    st.header("Management Structure")
    management_type = st.selectbox("Management Type", ["Member-Managed", "Manager-Managed"])

    st.header("Members Information")
    num_members = st.number_input("Number of Members", min_value=1, max_value=10, value=1)

    members = []
    for i in range(num_members):
        st.subheader(f"Member {i+1}")
        name = st.text_input(f"Full Legal Name {i}", key=f"name_{i}")
        address = st.text_input(f"Address {i}", key=f"address_{i}")
        capital = st.number_input(f"Capital Contribution ($) {i}", min_value=0.0, key=f"capital_{i}")
        ownership = st.number_input(f"Ownership Percentage {i}", min_value=0.0, max_value=100.0, key=f"ownership_{i}")
        members.append({
            "name": name,
            "address": address,
            "capital": capital,
            "ownership": ownership
        })

    st.header("Tax Election")
    tax_status = st.selectbox("Federal Tax Classification", [
        "Single-Member Disregarded Entity",
        "Partnership",
        "S-Corporation Election",
        "C-Corporation Election"
    ])

    submit = st.form_submit_button("Generate Professional Operating Agreement")


# =========================
# PDF GENERATION FUNCTION
# =========================
def generate_operating_agreement_pdf():

    file_path = "Professional_LLC_Operating_Agreement.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=LETTER)
    elements = []
    styles = getSampleStyleSheet()

    heading_style = styles["Heading1"]
    subheading_style = styles["Heading2"]
    normal = styles["Normal"]

    # TITLE
    elements.append(Paragraph(f"{company_name} LLC", heading_style))
    elements.append(Paragraph("OPERATING AGREEMENT", heading_style))
    elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph(
        f"This Operating Agreement is entered into effective {formation_date.strftime('%B %d, %Y')} "
        f"by and among the Members listed herein for the formation and governance of {company_name} LLC "
        f"under the laws of the State of {state}.", normal))
    elements.append(Spacer(1, 0.3 * inch))

    # ARTICLE I – FORMATION
    elements.append(Paragraph("ARTICLE I – FORMATION", subheading_style))
    elements.append(Paragraph(
        f"The Company was formed as a Limited Liability Company pursuant to the laws of {state}. "
        f"The principal office shall be located at {principal_address}.", normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE II – PURPOSE
    elements.append(Paragraph("ARTICLE II – PURPOSE", subheading_style))
    elements.append(Paragraph(
        f"The purpose of the Company is: {purpose}. "
        "The Company may engage in any lawful business permitted under state law.", normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE III – TERM
    elements.append(Paragraph("ARTICLE III – TERM", subheading_style))
    if duration == "Perpetual":
        elements.append(Paragraph("The Company shall continue perpetually unless dissolved pursuant to this Agreement.", normal))
    else:
        elements.append(Paragraph(f"The Company shall exist for {duration_detail}.", normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE IV – MEMBERS & CAPITAL
    elements.append(Paragraph("ARTICLE IV – MEMBERS AND CAPITAL CONTRIBUTIONS", subheading_style))
    for m in members:
        elements.append(Paragraph(
            f"{m['name']} – Address: {m['address']} – "
            f"Capital Contribution: ${m['capital']} – Ownership: {m['ownership']}%", normal))
        elements.append(Spacer(1, 0.1 * inch))

    # ARTICLE V – PROFITS & LOSSES
    elements.append(Paragraph("ARTICLE V – ALLOCATION OF PROFITS AND LOSSES", subheading_style))
    elements.append(Paragraph(
        "Profits and losses shall be allocated among the Members in proportion to their respective ownership percentages unless otherwise required by law.",
        normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE VI – MANAGEMENT
    elements.append(Paragraph("ARTICLE VI – MANAGEMENT", subheading_style))
    elements.append(Paragraph(
        f"The Company shall be {management_type}. Managers or Members shall have authority to bind the Company in the ordinary course of business.",
        normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE VII – VOTING
    elements.append(Paragraph("ARTICLE VII – VOTING RIGHTS", subheading_style))
    elements.append(Paragraph(
        "Each Member shall have voting power proportional to their ownership interest. "
        "Major decisions require majority approval unless otherwise stated.",
        normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE VIII – TAXATION
    elements.append(Paragraph("ARTICLE VIII – TAX TREATMENT", subheading_style))
    elements.append(Paragraph(
        f"The Company shall be taxed as a {tax_status}. "
        "All tax filings shall be completed in accordance with federal and state law.",
        normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE IX – TRANSFER OF INTEREST
    elements.append(Paragraph("ARTICLE IX – TRANSFER OF MEMBERSHIP INTEREST", subheading_style))
    elements.append(Paragraph(
        "No Member may transfer their ownership interest without the written consent of the other Members.",
        normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE X – DISSOLUTION
    elements.append(Paragraph("ARTICLE X – DISSOLUTION AND WINDING UP", subheading_style))
    elements.append(Paragraph(
        "The Company shall dissolve upon unanimous written consent of the Members or as otherwise required by law. "
        "Assets shall be distributed in accordance with ownership percentages after liabilities are satisfied.",
        normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE XI – INDEMNIFICATION
    elements.append(Paragraph("ARTICLE XI – INDEMNIFICATION", subheading_style))
    elements.append(Paragraph(
        "The Company shall indemnify Members and Managers to the fullest extent permitted by law.",
        normal))
    elements.append(Spacer(1, 0.2 * inch))

    # ARTICLE XII – AMENDMENTS
    elements.append(Paragraph("ARTICLE XII – AMENDMENTS", subheading_style))
    elements.append(Paragraph(
        "This Agreement may be amended only by written agreement signed by all Members.",
        normal))
    elements.append(PageBreak())

    # SIGNATURE PAGE
    elements.append(Paragraph("IN WITNESS WHEREOF, the Members execute this Agreement:", subheading_style))
    elements.append(Spacer(1, 0.5 * inch))

    for m in members:
        elements.append(Paragraph("____________________________________", normal))
        elements.append(Paragraph(f"{m['name']}", normal))
        elements.append(Spacer(1, 0.4 * inch))

    doc.build(elements)
    return file_path


# =========================
# GENERATE BUTTON
# =========================
if submit:
    pdf_path = generate_operating_agreement_pdf()
    with open(pdf_path, "rb") as f:
        st.success("Professional Operating Agreement Generated Successfully!")
        st.download_button(
            label="📥 Download Professional Operating Agreement",
            data=f,
            file_name="Professional_LLC_Operating_Agreement.pdf",
            mime="application/pdf"
        )
