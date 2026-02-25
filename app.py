import streamlit as st
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    HRFlowable, KeepTogether, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

st.set_page_config(page_title="LLC Operating Agreement Generator", layout="centered")

st.title("🏛 Professional LLC Operating Agreement Generator")
st.caption("Generate a comprehensive, legally-structured operating agreement for your LLC.")

# =========================
# FORM SECTION
# =========================
with st.form("agreement_form"):

    # ── Company Information ──────────────────────────────────────────────────
    st.header("🏢 Company Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("LLC Name (without 'LLC')")
        state = st.text_input("State of Formation")
    with col2:
        formation_date = st.date_input("Formation Date", datetime.today())
        fiscal_year_end = st.selectbox("Fiscal Year End", [
            "December 31", "March 31", "June 30", "September 30"
        ])
    principal_address = st.text_input("Principal Office Address")
    registered_agent_name = st.text_input("Registered Agent Name")
    registered_agent_address = st.text_input("Registered Agent Address")

    # ── Business Details ─────────────────────────────────────────────────────
    st.header("📋 Business Details")
    purpose = st.text_area("Business Purpose (describe the company's primary activities)")
    duration = st.selectbox("Company Duration", ["Perpetual", "Specific Term"])
    duration_detail = ""
    if duration == "Specific Term":
        duration_detail = st.text_input("Specify Duration (e.g., '10 years from the date of formation')")

    # ── Management Structure ─────────────────────────────────────────────────
    st.header("⚙️ Management Structure")
    management_type = st.selectbox("Management Type", ["Member-Managed", "Manager-Managed"])
    if management_type == "Manager-Managed":
        manager_name = st.text_input("Manager Name(s)")
        manager_address = st.text_input("Manager Address")
    else:
        manager_name = ""
        manager_address = ""

    voting_threshold_major = st.selectbox(
        "Voting Threshold for Major Decisions",
        ["Simple Majority (>50%)", "Super Majority (≥66.7%)", "Unanimous (100%)"]
    )

    # ── Members Information ──────────────────────────────────────────────────
    st.header("👥 Members Information")
    num_members = st.number_input("Number of Members", min_value=1, max_value=10, value=1)

    members = []
    for i in range(int(num_members)):
        with st.expander(f"Member {i+1}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(f"Full Legal Name", key=f"name_{i}")
                address = st.text_input(f"Address", key=f"address_{i}")
            with col2:
                capital = st.number_input(f"Capital Contribution ($)", min_value=0.0, key=f"capital_{i}")
                ownership = st.number_input(f"Ownership Percentage (%)", min_value=0.0, max_value=100.0, key=f"ownership_{i}")
            members.append({"name": name, "address": address, "capital": capital, "ownership": ownership})

    # ── Financial & Distribution ─────────────────────────────────────────────
    st.header("💰 Financial & Distributions")
    distribution_frequency = st.selectbox("Distribution Frequency", [
        "At the discretion of the Members/Managers",
        "Quarterly",
        "Semi-Annually",
        "Annually"
    ])
    bank_name = st.text_input("Company Bank / Financial Institution (optional)")
    accounting_method = st.selectbox("Accounting Method", ["Cash Basis", "Accrual Basis"])

    # ── Tax Election ─────────────────────────────────────────────────────────
    st.header("🧾 Tax Classification")
    tax_status = st.selectbox("Federal Tax Classification", [
        "Single-Member Disregarded Entity",
        "Partnership",
        "S-Corporation Election",
        "C-Corporation Election"
    ])

    # ── Additional Provisions ────────────────────────────────────────────────
    st.header("📜 Additional Provisions")
    non_compete_clause = st.checkbox("Include Non-Compete / Non-Solicitation Clause")
    dispute_resolution = st.selectbox("Dispute Resolution Method", [
        "Mediation then Litigation",
        "Binding Arbitration",
        "Mediation then Binding Arbitration"
    ])
    governing_law_state = st.text_input("Governing Law State (leave blank to use State of Formation)")
    confidentiality_clause = st.checkbox("Include Confidentiality / NDA Clause")
    buyout_clause = st.checkbox("Include Member Buyout / Right of First Refusal Clause")

    submit = st.form_submit_button("⚙️ Generate Operating Agreement PDF", use_container_width=True)


# =========================
# STYLES HELPER
# =========================
def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["title"] = ParagraphStyle(
        "DocTitle",
        parent=base["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
        fontName="Helvetica-Bold"
    )
    styles["subtitle"] = ParagraphStyle(
        "DocSubtitle",
        parent=base["Normal"],
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.HexColor("#333333"),
        fontName="Helvetica"
    )
    styles["article"] = ParagraphStyle(
        "Article",
        parent=base["Normal"],
        fontSize=11,
        leading=14,
        spaceBefore=16,
        spaceAfter=4,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        borderPad=4,
    )
    styles["section"] = ParagraphStyle(
        "Section",
        parent=base["Normal"],
        fontSize=10,
        leading=13,
        spaceBefore=10,
        spaceAfter=2,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2d2d2d"),
    )
    styles["body"] = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontSize=10,
        leading=14,
        spaceBefore=4,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
        fontName="Helvetica"
    )
    styles["small"] = ParagraphStyle(
        "Small",
        parent=base["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_JUSTIFY,
        fontName="Helvetica"
    )
    styles["center"] = ParagraphStyle(
        "Center",
        parent=base["Normal"],
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        fontName="Helvetica"
    )
    return styles


# =========================
# PDF GENERATION FUNCTION
# =========================
def generate_pdf():
    file_path = "/tmp/Professional_LLC_Operating_Agreement.pdf"
    doc = SimpleDocTemplate(
        file_path,
        pagesize=LETTER,
        leftMargin=1.1 * inch,
        rightMargin=1.1 * inch,
        topMargin=1.0 * inch,
        bottomMargin=1.0 * inch,
    )
    elements = []
    s = build_styles()
    gov_state = governing_law_state.strip() if governing_law_state.strip() else state

    def rule():
        return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=6)

    def article_heading(text):
        return [rule(), Paragraph(text, s["article"]), rule()]

    def section_heading(text):
        return Paragraph(text, s["section"])

    def body(text):
        return Paragraph(text, s["body"])

    def spacer(h=0.15):
        return Spacer(1, h * inch)

    # ── Cover / Title ────────────────────────────────────────────────────────
    elements.append(spacer(0.5))
    elements.append(Paragraph(f"{company_name.upper()} LLC", s["title"]))
    elements.append(Paragraph("OPERATING AGREEMENT", s["title"]))
    elements.append(spacer(0.1))
    elements.append(Paragraph(f"A {state} Limited Liability Company", s["subtitle"]))
    elements.append(Paragraph(f"Effective Date: {formation_date.strftime('%B %d, %Y')}", s["subtitle"]))
    elements.append(spacer(0.4))
    elements.append(rule())
    elements.append(spacer(0.1))

    # ── Preamble ─────────────────────────────────────────────────────────────
    elements.append(body(
        f"This Operating Agreement (the \"Agreement\") is entered into as of {formation_date.strftime('%B %d, %Y')} "
        f"(the \"Effective Date\"), by and among the persons executing this Agreement as Members (collectively, the \"Members\"), "
        f"for the purpose of forming and governing {company_name} LLC (the \"Company\"), a limited liability company "
        f"organized under the laws of the State of {state}. This Agreement sets forth the rights, duties, and obligations "
        f"of the Members with respect to the Company and shall be binding upon all Members and their permitted successors and assigns."
    ))
    elements.append(spacer(0.2))

    # ── TABLE OF CONTENTS (simple) ───────────────────────────────────────────
    elements.append(PageBreak())
    elements.append(Paragraph("TABLE OF CONTENTS", s["article"]))
    toc_items = [
        ("Article I", "Formation"),
        ("Article II", "Business Purpose"),
        ("Article III", "Term"),
        ("Article IV", "Members and Capital Contributions"),
        ("Article V", "Allocation of Profits and Losses"),
        ("Article VI", "Distributions"),
        ("Article VII", "Management and Authority"),
        ("Article VIII", "Voting Rights and Member Meetings"),
        ("Article IX", "Books, Records, and Accounting"),
        ("Article X", "Tax Treatment"),
        ("Article XI", "Transfer of Membership Interest"),
        ("Article XII", "Admission of New Members"),
        ("Article XIII", "Withdrawal and Dissociation of Members"),
        ("Article XIV", "Dissolution and Winding Up"),
        ("Article XV", "Indemnification and Liability"),
        ("Article XVI", "Dispute Resolution"),
    ]
    if non_compete_clause:
        toc_items.append(("Article XVII", "Non-Compete and Non-Solicitation"))
    if confidentiality_clause:
        toc_items.append(("Article XVIII", "Confidentiality"))
    if buyout_clause:
        toc_items.append(("Article XIX", "Right of First Refusal and Buyout"))
    toc_items.append(("Article XX", "General Provisions and Amendments"))

    for art, title in toc_items:
        elements.append(body(f"<b>{art}</b> — {title}"))
    elements.append(PageBreak())

    # ── ARTICLE I – FORMATION ────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE I — FORMATION"))
    elements.append(section_heading("1.1  Company Name"))
    elements.append(body(
        f"The name of the Company is {company_name} LLC. The Company may conduct business under such trade names "
        f"or assumed names as the Members may approve from time to time in accordance with applicable law."
    ))
    elements.append(section_heading("1.2  State of Organization"))
    elements.append(body(
        f"The Company is organized as a limited liability company under and pursuant to the laws of the State of {state}, "
        f"including the applicable provisions of the {state} Limited Liability Company Act, as amended from time to time."
    ))
    elements.append(section_heading("1.3  Principal Office"))
    elements.append(body(
        f"The principal office and place of business of the Company shall be located at {principal_address}, "
        f"or such other location as the Members may determine from time to time."
    ))
    elements.append(section_heading("1.4  Registered Agent"))
    elements.append(body(
        f"The registered agent for service of process in the State of {state} is {registered_agent_name}, "
        f"whose address is {registered_agent_address}. The Company may change its registered agent and/or "
        f"registered office by filing the appropriate documentation with the {state} Secretary of State."
    ))
    elements.append(section_heading("1.5  Formation"))
    elements.append(body(
        f"The Company was formed upon the filing of its Articles of Organization (or Certificate of Formation) "
        f"with the {state} Secretary of State. The Members agree to be bound by this Agreement from and after the Effective Date."
    ))

    # ── ARTICLE II – PURPOSE ─────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE II — BUSINESS PURPOSE"))
    elements.append(section_heading("2.1  Primary Purpose"))
    elements.append(body(
        f"The primary purpose of the Company is: {purpose}."
    ))
    elements.append(section_heading("2.2  General Powers"))
    elements.append(body(
        "The Company may engage in any and all activities and transactions that are permitted under applicable law "
        "and that are necessary or convenient to carry out the purposes of the Company, including without limitation: "
        "(a) acquiring, holding, managing, and disposing of assets; (b) entering into contracts and agreements; "
        "(c) borrowing money and issuing evidences of indebtedness; (d) employing personnel and engaging contractors; "
        "and (e) any other lawful activity approved by the Members."
    ))

    # ── ARTICLE III – TERM ───────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE III — TERM"))
    elements.append(section_heading("3.1  Duration"))
    if duration == "Perpetual":
        elements.append(body(
            "The Company shall continue in existence perpetually unless and until dissolved in accordance with this Agreement "
            "or as otherwise required by applicable law."
        ))
    else:
        elements.append(body(
            f"The Company shall exist for {duration_detail}, unless sooner dissolved in accordance with this Agreement "
            f"or as otherwise required by applicable law. Upon expiration of such term, the Company shall wind up and dissolve "
            f"unless the Members unanimously agree in writing to extend the term."
        ))

    # ── ARTICLE IV – MEMBERS & CAPITAL ───────────────────────────────────────
    elements.extend(article_heading("ARTICLE IV — MEMBERS AND CAPITAL CONTRIBUTIONS"))
    elements.append(section_heading("4.1  Initial Members"))
    elements.append(body(
        "The following persons are the initial Members of the Company, with their respective addresses, "
        "initial capital contributions, and ownership (membership) interests:"
    ))
    elements.append(spacer(0.1))

    # Members Table
    table_data = [["Member Name", "Address", "Capital Contribution", "Ownership %"]]
    for m in members:
        table_data.append([
            m["name"] or "—",
            m["address"] or "—",
            f"${m['capital']:,.2f}",
            f"{m['ownership']:.2f}%"
        ])
    total_capital = sum(m["capital"] for m in members)
    total_ownership = sum(m["ownership"] for m in members)
    table_data.append(["TOTAL", "", f"${total_capital:,.2f}", f"{total_ownership:.2f}%"])

    col_widths = [1.6 * inch, 1.9 * inch, 1.4 * inch, 1.0 * inch]
    members_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    members_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f5f5f5")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8e8e8")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(members_table)
    elements.append(spacer(0.15))

    elements.append(section_heading("4.2  Additional Capital Contributions"))
    elements.append(body(
        "No Member shall be required to make any additional capital contribution to the Company beyond the initial "
        "contribution set forth in Section 4.1 without the unanimous written consent of all Members. Any additional "
        "capital contribution shall be made on terms and conditions as agreed by the Members and shall be reflected "
        "in an amendment to this Agreement or a separate written instrument signed by all Members."
    ))
    elements.append(section_heading("4.3  Capital Accounts"))
    elements.append(body(
        "A separate capital account shall be maintained for each Member. Each Member's capital account shall be "
        "credited with such Member's capital contributions and allocated profits, and shall be debited with "
        "such Member's allocated losses and distributions. Capital accounts shall be maintained in accordance "
        "with applicable Treasury Regulations."
    ))
    elements.append(section_heading("4.4  No Interest on Capital"))
    elements.append(body(
        "No Member shall be entitled to receive interest on their capital contribution unless otherwise unanimously "
        "agreed in writing by all Members."
    ))
    elements.append(section_heading("4.5  Return of Capital"))
    elements.append(body(
        "No Member shall have the right to demand or receive the return of their capital contribution except upon "
        "dissolution and winding up of the Company, or as otherwise agreed in writing by all Members. No Member "
        "shall be liable to any other Member for the return of a capital contribution."
    ))

    # ── ARTICLE V – PROFITS & LOSSES ─────────────────────────────────────────
    elements.extend(article_heading("ARTICLE V — ALLOCATION OF PROFITS AND LOSSES"))
    elements.append(section_heading("5.1  General Allocation"))
    elements.append(body(
        "Except as otherwise provided in this Agreement, the net profits and net losses of the Company for each "
        "fiscal year shall be allocated among the Members in proportion to their respective ownership percentages "
        "as set forth in Section 4.1, as adjusted from time to time."
    ))
    elements.append(section_heading("5.2  Special Allocations"))
    elements.append(body(
        "Notwithstanding Section 5.1, the following special allocations shall be made in the following order: "
        "(a) Minimum Gain Chargeback: If there is a net decrease in Company minimum gain during any fiscal year, "
        "each Member shall be allocated items of income and gain as required under Treasury Regulation "
        "Section 1.704-2(f); (b) Member Minimum Gain Chargeback: If there is a net decrease in Member nonrecourse "
        "debt minimum gain during any fiscal year, certain items of income and gain shall be allocated to the Members "
        "as required under Treasury Regulation Section 1.704-2(i)(4)."
    ))
    elements.append(section_heading("5.3  Tax Allocations"))
    elements.append(body(
        "For income tax purposes, each item of Company income, gain, loss, deduction, and credit shall be allocated "
        "among the Members in the same manner as the corresponding book item is allocated, except as required by "
        "Section 704(c) of the Internal Revenue Code and the Treasury Regulations thereunder."
    ))

    # ── ARTICLE VI – DISTRIBUTIONS ───────────────────────────────────────────
    elements.extend(article_heading("ARTICLE VI — DISTRIBUTIONS"))
    elements.append(section_heading("6.1  Distributions"))
    elements.append(body(
        f"Distributions of available cash and other Company assets shall be made to the Members "
        f"{distribution_frequency.lower()}, in proportion to their respective ownership percentages, "
        f"unless the Members unanimously agree otherwise in writing. The Company shall retain sufficient "
        f"reserves for working capital, liabilities, and contingencies as reasonably determined by the "
        f"Members or Managers."
    ))
    elements.append(section_heading("6.2  Withholding"))
    elements.append(body(
        "The Company is authorized to withhold from any distribution to a Member, or to pay on behalf of a Member, "
        "any amount required by applicable federal, state, or local law. Any amount so withheld shall be treated as "
        "a distribution to that Member for all purposes of this Agreement."
    ))
    elements.append(section_heading("6.3  Limitations on Distributions"))
    elements.append(body(
        "No distribution shall be made if, after giving effect to the distribution, the Company would be unable to "
        "pay its debts as they become due in the ordinary course of business, or if the Company's total assets would "
        "be less than the sum of its total liabilities. Any distribution made in violation of this provision shall "
        "be returned to the Company."
    ))

    # ── ARTICLE VII – MANAGEMENT ─────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE VII — MANAGEMENT AND AUTHORITY"))
    elements.append(section_heading("7.1  Management Structure"))
    elements.append(body(
        f"The Company shall be {management_type}. "
        + (f"The Manager(s) of the Company are {manager_name}, whose address is {manager_address}. "
           f"The Managers shall have full authority to manage and control the business and affairs of the Company, "
           f"subject to the provisions of this Agreement."
           if management_type == "Manager-Managed"
           else
           "All Members shall have the right and authority to participate in the management and conduct of the "
           "Company's business, subject to the provisions of this Agreement. Each Member acting alone shall have "
           "authority to bind the Company in the ordinary course of business unless otherwise restricted herein.")
    ))
    elements.append(section_heading("7.2  Authority of Managers/Members"))
    elements.append(body(
        "Subject to the limitations set forth in this Agreement, the authorized manager(s) or member(s) shall have "
        "full power and authority on behalf of the Company to: (a) execute contracts and agreements; (b) open and "
        "manage bank accounts; (c) hire and terminate employees and independent contractors; (d) purchase, lease, "
        "or dispose of Company assets; (e) borrow money and grant security interests in Company assets; "
        "(f) institute or defend legal proceedings; and (g) take all other actions necessary or appropriate to "
        "carry out the purposes of the Company."
    ))
    elements.append(section_heading("7.3  Actions Requiring Member Approval"))
    elements.append(body(
        f"Notwithstanding Section 7.2, the following actions shall require {voting_threshold_major.lower()} of "
        "the Members: (a) amendment of this Agreement or the Articles of Organization; (b) merger, consolidation, "
        "or conversion of the Company; (c) sale of all or substantially all of the Company's assets outside the "
        "ordinary course of business; (d) incurring indebtedness in excess of amounts established by the Members; "
        "(e) admission of new Members; (f) dissolution of the Company; and (g) any other action expressly requiring "
        "Member approval under this Agreement or applicable law."
    ))
    if management_type == "Manager-Managed":
        elements.append(section_heading("7.4  Removal and Replacement of Managers"))
        elements.append(body(
            "A Manager may be removed at any time, with or without cause, by a vote of the Members holding a majority "
            "of the membership interests. Upon removal, resignation, or incapacity of a Manager, a successor Manager "
            "shall be appointed by majority vote of the Members."
        ))

    # ── ARTICLE VIII – VOTING ─────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE VIII — VOTING RIGHTS AND MEMBER MEETINGS"))
    elements.append(section_heading("8.1  Voting Power"))
    elements.append(body(
        "Each Member shall have voting power proportional to their ownership interest as set forth in Section 4.1. "
        "Votes may be cast in person, by proxy, or by written consent."
    ))
    elements.append(section_heading("8.2  Annual Meetings"))
    elements.append(body(
        "The Members shall hold an annual meeting at a time and place determined by the Members or Managers to "
        "review the financial condition of the Company, elect or confirm Managers (if applicable), and transact "
        "such other business as may properly come before the meeting."
    ))
    elements.append(section_heading("8.3  Special Meetings"))
    elements.append(body(
        "Special meetings of the Members may be called at any time by Members holding at least twenty-five percent "
        "(25%) of the total membership interests, upon not less than five (5) days' prior written notice stating "
        "the purpose of the meeting."
    ))
    elements.append(section_heading("8.4  Written Consent in Lieu of Meeting"))
    elements.append(body(
        "Any action required or permitted to be taken at a meeting of the Members may be taken without a meeting "
        "if all Members consent in writing to such action. Such written consent shall be filed with the minutes "
        "of the Company and shall have the same force and effect as a unanimous vote at a duly convened meeting."
    ))
    elements.append(section_heading("8.5  Quorum"))
    elements.append(body(
        "Members holding a majority of the total membership interests shall constitute a quorum for the transaction "
        "of business at any meeting. In the absence of a quorum, the Members present may adjourn the meeting to "
        "a future date without further notice."
    ))

    # ── ARTICLE IX – BOOKS & RECORDS ─────────────────────────────────────────
    elements.extend(article_heading("ARTICLE IX — BOOKS, RECORDS, AND ACCOUNTING"))
    elements.append(section_heading("9.1  Books and Records"))
    elements.append(body(
        "The Company shall maintain complete and accurate books of account and other records of the Company's "
        "business and affairs at the Company's principal office. Such books shall include, at a minimum: "
        "(a) a current list of the full name and last known address of each Member; (b) a copy of this Agreement "
        "and all amendments; (c) the Articles of Organization and all amendments; (d) federal, state, and local "
        "tax returns for the three most recent years; and (e) financial statements for the three most recent fiscal years."
    ))
    elements.append(section_heading("9.2  Inspection Rights"))
    elements.append(body(
        "Each Member shall have the right, upon reasonable written notice, to inspect and copy the Company's books "
        "and records at the Member's own expense during normal business hours."
    ))
    elements.append(section_heading("9.3  Accounting Method and Fiscal Year"))
    elements.append(body(
        f"The Company shall use the {accounting_method} method of accounting. The fiscal year of the Company shall "
        f"end on {fiscal_year_end} of each year, unless changed by unanimous written consent of the Members."
        + (f" The Company's primary bank shall be {bank_name}." if bank_name else "")
    ))
    elements.append(section_heading("9.4  Financial Statements"))
    elements.append(body(
        "Within ninety (90) days after the end of each fiscal year, the Company shall prepare or cause to be prepared "
        "annual financial statements, including a balance sheet, income statement, and statement of cash flows. "
        "Copies shall be provided to each Member."
    ))

    # ── ARTICLE X – TAXATION ─────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE X — TAX TREATMENT"))
    elements.append(section_heading("10.1  Federal Tax Classification"))
    elements.append(body(
        f"It is the intent of the Members that the Company be treated as a {tax_status} for federal income tax "
        "purposes. The Company and each Member shall file all tax returns and shall make all tax elections "
        "consistent with this tax treatment. The Members acknowledge that this Agreement shall not be construed "
        "to create an association taxable as a corporation unless affirmatively elected."
    ))
    elements.append(section_heading("10.2  Tax Matters Member/Partner"))
    elements.append(body(
        "The Members shall designate a Tax Matters Member (or Partnership Representative, if applicable) "
        "who shall have authority to make tax elections, represent the Company in tax proceedings, and "
        "communicate with taxing authorities. Unless otherwise designated, the Member with the largest "
        "ownership interest shall serve in such capacity."
    ))
    elements.append(section_heading("10.3  Tax Returns"))
    elements.append(body(
        "The Tax Matters Member shall cause all required federal, state, and local tax returns to be timely "
        "prepared and filed on behalf of the Company. Copies of all returns shall be made available to each Member."
    ))

    # ── ARTICLE XI – TRANSFER ────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE XI — TRANSFER OF MEMBERSHIP INTEREST"))
    elements.append(section_heading("11.1  Restrictions on Transfer"))
    elements.append(body(
        "No Member may sell, assign, transfer, pledge, hypothecate, or otherwise dispose of all or any portion "
        "of their membership interest (a \"Transfer\") without the prior written consent of the other Members "
        f"by {voting_threshold_major.lower()} vote. Any purported Transfer in violation of this Agreement shall "
        "be null and void and shall have no effect."
    ))
    elements.append(section_heading("11.2  Permitted Transfers"))
    elements.append(body(
        "Notwithstanding Section 11.1, a Member may Transfer their membership interest to: (a) a revocable "
        "living trust for estate planning purposes, provided the Member retains control as trustee; or "
        "(b) an entity wholly owned and controlled by the Member, provided that any such permitted transferee "
        "agrees in writing to be bound by all terms of this Agreement."
    ))
    elements.append(section_heading("11.3  Transferees"))
    elements.append(body(
        "A permitted transferee who is admitted as a substituted Member shall have all the rights and obligations "
        "of a Member under this Agreement. An assignee who is not admitted as a substituted Member shall be "
        "entitled to receive the transferring Member's economic rights only, without voting, management, "
        "or inspection rights."
    ))

    # ── ARTICLE XII – ADMISSION ──────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE XII — ADMISSION OF NEW MEMBERS"))
    elements.append(section_heading("12.1  New Members"))
    elements.append(body(
        "New Members may be admitted to the Company upon the unanimous written consent of all existing Members. "
        "Any new Member shall (a) execute a written joinder agreement to this Agreement; (b) make such capital "
        "contribution as agreed by the existing Members; and (c) be assigned a membership interest as agreed. "
        "The admission of a new Member shall require an amendment to Schedule A of this Agreement."
    ))

    # ── ARTICLE XIII – WITHDRAWAL ────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE XIII — WITHDRAWAL AND DISSOCIATION OF MEMBERS"))
    elements.append(section_heading("13.1  Voluntary Withdrawal"))
    elements.append(body(
        "A Member may withdraw from the Company upon not less than ninety (90) days' prior written notice to all "
        "other Members. The withdrawing Member shall not be entitled to receive the fair value of their interest "
        "upon withdrawal unless otherwise agreed by the remaining Members in writing."
    ))
    elements.append(section_heading("13.2  Involuntary Dissociation"))
    elements.append(body(
        "A Member shall be dissociated upon: (a) the Member's death or legal incapacity; (b) bankruptcy or "
        "insolvency of the Member; (c) the Member's expulsion by unanimous written vote of all other Members "
        "for material breach of this Agreement; or (d) any other event causing dissociation under applicable law."
    ))
    elements.append(section_heading("13.3  Buyout Upon Dissociation"))
    elements.append(body(
        "Upon dissociation, the dissociated Member's interest shall be subject to purchase by the remaining Members "
        "at fair market value as determined by agreement of the parties or, if they cannot agree within thirty (30) "
        "days, by an independent appraiser selected by the parties."
    ))

    # ── ARTICLE XIV – DISSOLUTION ────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE XIV — DISSOLUTION AND WINDING UP"))
    elements.append(section_heading("14.1  Events of Dissolution"))
    elements.append(body(
        "The Company shall be dissolved upon the occurrence of any of the following: "
        f"(a) the unanimous written consent of all Members to dissolve; "
        f"(b) expiration of the Company's term (if not perpetual); "
        f"(c) the entry of a decree of judicial dissolution; or "
        f"(d) any other event causing mandatory dissolution under {state} law."
    ))
    elements.append(section_heading("14.2  Winding Up"))
    elements.append(body(
        "Upon dissolution, the Company's affairs shall be wound up by the Members or a liquidating trustee "
        "appointed by the Members. The person winding up the Company's affairs shall (a) complete any unfinished "
        "business; (b) collect and liquidate all Company assets; (c) pay or provide for all Company liabilities; "
        "and (d) distribute remaining assets to the Members."
    ))
    elements.append(section_heading("14.3  Order of Distribution"))
    elements.append(body(
        "Assets remaining after paying or providing for all liabilities shall be distributed in the following order: "
        "(a) first, to Members in respect of any unpaid loans made by Members to the Company; "
        "(b) second, to Members in respect of their positive capital account balances; and "
        "(c) third, to Members in proportion to their ownership percentages."
    ))

    # ── ARTICLE XV – INDEMNIFICATION ─────────────────────────────────────────
    elements.extend(article_heading("ARTICLE XV — INDEMNIFICATION AND LIABILITY"))
    elements.append(section_heading("15.1  Indemnification"))
    elements.append(body(
        "The Company shall indemnify, defend, and hold harmless each Member, Manager, officer, employee, and agent "
        "(each an \"Indemnified Person\") from and against any and all claims, damages, losses, costs, and expenses "
        "(including reasonable attorneys' fees) arising out of or in connection with the business of the Company "
        "or such Indemnified Person's capacity, except to the extent caused by such person's fraud, willful "
        "misconduct, or gross negligence."
    ))
    elements.append(section_heading("15.2  Limitation of Liability"))
    elements.append(body(
        "No Member or Manager shall be personally liable for any debt, obligation, or liability of the Company "
        "solely by reason of being a Member or Manager, except as required by applicable law. No Member or Manager "
        "shall be liable to the Company or to any other Member for any act or omission performed in good faith "
        "and in a manner reasonably believed to be in or not opposed to the best interests of the Company."
    ))
    elements.append(section_heading("15.3  Insurance"))
    elements.append(body(
        "The Company may, at the discretion of the Members, purchase and maintain insurance on behalf of any "
        "Indemnified Person against any liability asserted against such person in their official capacity."
    ))

    # ── ARTICLE XVI – DISPUTE RESOLUTION ────────────────────────────────────
    elements.extend(article_heading("ARTICLE XVI — DISPUTE RESOLUTION"))
    elements.append(section_heading("16.1  Negotiation"))
    elements.append(body(
        "In the event of any dispute arising out of or related to this Agreement or the Company's business, "
        "the parties shall first attempt to resolve such dispute through good faith negotiation for a period "
        "of thirty (30) days after written notice of the dispute."
    ))
    elements.append(section_heading("16.2  Resolution Method"))
    if dispute_resolution == "Binding Arbitration":
        elements.append(body(
            "If negotiation fails, any dispute shall be resolved by binding arbitration administered by the "
            "American Arbitration Association under its Commercial Arbitration Rules. The arbitration shall "
            "take place in the county in which the Company's principal office is located. The arbitrator's "
            "decision shall be final and binding and may be entered as a judgment in any court of competent jurisdiction."
        ))
    elif dispute_resolution == "Mediation then Litigation":
        elements.append(body(
            "If negotiation fails, the parties shall submit the dispute to non-binding mediation before a "
            "mutually acceptable mediator. If mediation does not resolve the dispute within sixty (60) days, "
            "either party may pursue litigation in the courts of the State of "
            f"{gov_state}, which the parties agree shall have exclusive jurisdiction."
        ))
    else:
        elements.append(body(
            "If negotiation fails, the parties shall submit the dispute to non-binding mediation. If mediation "
            "does not resolve the dispute within sixty (60) days, the dispute shall be submitted to binding "
            "arbitration under the rules of the American Arbitration Association."
        ))
    elements.append(section_heading("16.3  Governing Law"))
    elements.append(body(
        f"This Agreement shall be governed by and construed in accordance with the laws of the State of {gov_state}, "
        "without regard to conflict of law principles."
    ))

    # ── OPTIONAL: NON-COMPETE ────────────────────────────────────────────────
    article_num = 17
    if non_compete_clause:
        elements.extend(article_heading(f"ARTICLE {roman(article_num)} — NON-COMPETE AND NON-SOLICITATION"))
        elements.append(section_heading(f"{article_num}.1  Non-Compete"))
        elements.append(body(
            "During the term of their membership and for a period of two (2) years following the termination "
            "or transfer of their membership interest, each Member agrees not to, directly or indirectly, "
            "own, manage, operate, control, be employed by, or participate in any business that competes "
            "directly with the Company within the geographic area in which the Company conducts its business."
        ))
        elements.append(section_heading(f"{article_num}.2  Non-Solicitation"))
        elements.append(body(
            "During the period described in Section {article_num}.1, no Member shall, directly or indirectly, "
            "solicit, hire, or attempt to induce any employee, contractor, or customer of the Company to "
            "terminate their relationship with the Company."
        ))
        elements.append(section_heading(f"{article_num}.3  Severability of Restriction"))
        elements.append(body(
            "If any restriction in this Article is deemed unenforceable by a court of competent jurisdiction, "
            "it shall be reduced in scope or duration to the minimum extent necessary to make it enforceable."
        ))
        article_num += 1

    # ── OPTIONAL: CONFIDENTIALITY ────────────────────────────────────────────
    if confidentiality_clause:
        elements.extend(article_heading(f"ARTICLE {roman(article_num)} — CONFIDENTIALITY"))
        elements.append(section_heading(f"{article_num}.1  Confidential Information"))
        elements.append(body(
            "Each Member acknowledges that in the course of their involvement with the Company, they may "
            "acquire confidential and proprietary information of the Company, including without limitation "
            "business plans, financial data, customer lists, trade secrets, and technical information "
            "(collectively, \"Confidential Information\")."
        ))
        elements.append(section_heading(f"{article_num}.2  Non-Disclosure"))
        elements.append(body(
            "Each Member agrees not to disclose any Confidential Information to any third party or use any "
            "Confidential Information for any purpose other than the benefit of the Company, without the "
            "prior written consent of all other Members. This obligation shall survive the termination of "
            "such Member's membership interest for a period of three (3) years."
        ))
        article_num += 1

    # ── OPTIONAL: BUYOUT / ROFR ──────────────────────────────────────────────
    if buyout_clause:
        elements.extend(article_heading(f"ARTICLE {roman(article_num)} — RIGHT OF FIRST REFUSAL AND BUYOUT"))
        elements.append(section_heading(f"{article_num}.1  Right of First Refusal"))
        elements.append(body(
            "Before any Member may Transfer all or any portion of their membership interest to any third party, "
            "such Member (the \"Selling Member\") must first offer the interest to the other Members on the "
            "same terms and conditions offered by the third party. The other Members shall have thirty (30) "
            "days from receipt of written notice to exercise their right of first refusal."
        ))
        elements.append(section_heading(f"{article_num}.2  Valuation"))
        elements.append(body(
            "If the Members cannot agree on the purchase price for a buyout, the fair market value of the "
            "membership interest shall be determined by an independent, certified business appraiser mutually "
            "selected by the parties, whose determination shall be final and binding."
        ))
        elements.append(section_heading(f"{article_num}.3  Payment Terms"))
        elements.append(body(
            "Unless otherwise agreed, the purchase price for a buyout shall be payable as follows: "
            "twenty-five percent (25%) at closing and the balance in equal monthly installments over "
            "thirty-six (36) months, with interest at the then-applicable federal rate."
        ))
        article_num += 1

    # ── ARTICLE XX – GENERAL PROVISIONS ─────────────────────────────────────
    elements.extend(article_heading(f"ARTICLE {roman(article_num)} — GENERAL PROVISIONS AND AMENDMENTS"))
    elements.append(section_heading(f"{article_num}.1  Entire Agreement"))
    elements.append(body(
        "This Agreement constitutes the entire agreement of the Members with respect to the subject matter "
        "hereof and supersedes all prior and contemporaneous agreements, representations, and understandings "
        "of the Members."
    ))
    elements.append(section_heading(f"{article_num}.2  Amendments"))
    elements.append(body(
        "This Agreement may be amended, modified, or supplemented only by a written instrument signed by "
        "all Members. No oral modification of this Agreement shall be effective."
    ))
    elements.append(section_heading(f"{article_num}.3  Severability"))
    elements.append(body(
        "If any provision of this Agreement is held to be invalid, illegal, or unenforceable, such provision "
        "shall be modified to the minimum extent necessary to make it enforceable, and the remaining provisions "
        "shall continue in full force and effect."
    ))
    elements.append(section_heading(f"{article_num}.4  Notices"))
    elements.append(body(
        "All notices required or permitted under this Agreement shall be in writing and shall be deemed "
        "delivered when (a) personally delivered; (b) sent by certified mail, return receipt requested; "
        "(c) sent by overnight courier; or (d) sent by email with confirmed receipt, in each case to the "
        "addresses set forth in this Agreement or as updated by a Member in writing."
    ))
    elements.append(section_heading(f"{article_num}.5  Counterparts"))
    elements.append(body(
        "This Agreement may be executed in one or more counterparts, each of which shall be deemed an original, "
        "and all of which together shall constitute one and the same instrument. Electronic and digital signatures "
        "shall be deemed valid for purposes of this Agreement."
    ))
    elements.append(section_heading(f"{article_num}.6  Headings"))
    elements.append(body(
        "Article and section headings are for convenience only and shall not affect the construction or "
        "interpretation of this Agreement."
    ))
    elements.append(section_heading(f"{article_num}.7  Waiver"))
    elements.append(body(
        "No failure or delay by any Member in exercising any right, power, or remedy shall operate as a waiver "
        "thereof, nor shall any single or partial exercise of any right, power, or remedy preclude any other "
        "or further exercise thereof."
    ))

    # ── SIGNATURE PAGE ────────────────────────────────────────────────────────
    elements.append(PageBreak())
    elements.append(Paragraph("SIGNATURE PAGE", s["article"]))
    elements.append(rule())
    elements.append(spacer(0.1))
    elements.append(body(
        f"IN WITNESS WHEREOF, the undersigned Members of {company_name} LLC have executed this Operating "
        f"Agreement as of the date first written above, intending to be legally bound."
    ))
    elements.append(spacer(0.4))

    for m in members:
        sig_data = [
            [Paragraph("Signature:", s["small"]), Paragraph("_" * 42, s["small"])],
            [Paragraph("Printed Name:", s["small"]), Paragraph(m["name"] or "____________________", s["small"])],
            [Paragraph("Date:", s["small"]), Paragraph("____________________", s["small"])],
            [Paragraph("Ownership Interest:", s["small"]), Paragraph(f"{m['ownership']:.2f}%", s["small"])],
        ]
        sig_table = Table(sig_data, colWidths=[1.5 * inch, 4.0 * inch])
        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]))
        elements.append(KeepTogether([sig_table, spacer(0.4)]))

    if management_type == "Manager-Managed" and manager_name:
        elements.append(spacer(0.2))
        elements.append(Paragraph("MANAGER SIGNATURE", s["section"]))
        elements.append(spacer(0.1))
        sig_data = [
            [Paragraph("Signature:", s["small"]), Paragraph("_" * 42, s["small"])],
            [Paragraph("Manager Name:", s["small"]), Paragraph(manager_name or "____________________", s["small"])],
            [Paragraph("Date:", s["small"]), Paragraph("____________________", s["small"])],
        ]
        sig_table = Table(sig_data, colWidths=[1.5 * inch, 4.0 * inch])
        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]))
        elements.append(sig_table)

    # ── SCHEDULE A ────────────────────────────────────────────────────────────
    elements.append(PageBreak())
    elements.append(Paragraph("SCHEDULE A — MEMBERS AND CAPITAL CONTRIBUTIONS", s["article"]))
    elements.append(rule())
    elements.append(body(f"As of {formation_date.strftime('%B %d, %Y')}"))
    elements.append(spacer(0.15))
    elements.append(members_table)
    elements.append(spacer(0.3))
    elements.append(body(
        "This Schedule A may be updated from time to time to reflect changes in membership, "
        "ownership percentages, and capital contributions in accordance with the terms of the Agreement."
    ))

    doc.build(elements)
    return file_path


def roman(n):
    """Convert integer to Roman numeral string."""
    val = [1000,900,500,400,100,90,50,40,10,9,5,4,1]
    syms = ['M','CM','D','CD','C','XC','L','XL','X','IX','V','IV','I']
    result = ''
    for i in range(len(val)):
        while n >= val[i]:
            result += syms[i]
            n -= val[i]
    return result


# =========================
# GENERATE ON SUBMIT
# =========================
if submit:
    if not company_name or not state:
        st.error("Please fill in at least the LLC Name and State of Formation.")
    else:
        with st.spinner("Generating your professional operating agreement..."):
            pdf_path = generate_pdf()
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.success("✅ Your Operating Agreement has been generated successfully!")
        st.download_button(
            label="📥 Download Operating Agreement (PDF)",
            data=pdf_bytes,
            file_name=f"{company_name.replace(' ', '_')}_LLC_Operating_Agreement.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.info(
            "⚠️ **Legal Disclaimer:** This document is generated for informational purposes only and does not "
            "constitute legal advice. Please consult a qualified attorney in your state before relying on this "
            "agreement for any legal purpose."
        )
