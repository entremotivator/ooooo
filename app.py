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

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.member-card {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.ownership-bar-container {
    background: #e9ecef;
    border-radius: 6px;
    height: 18px;
    width: 100%;
    margin: 6px 0 2px 0;
    overflow: hidden;
}
.ownership-bar-fill {
    height: 18px;
    border-radius: 6px;
    transition: width 0.3s;
}
.tag-ok   { color: #198754; font-weight: 600; }
.tag-warn { color: #dc3545; font-weight: 600; }
.tag-info { color: #0d6efd; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("🏛 Professional LLC Operating Agreement Generator")
st.caption("Generate a comprehensive, legally-structured operating agreement for your LLC.")

# =========================
# SESSION STATE – MEMBERS
# =========================
if "members" not in st.session_state:
    st.session_state.members = [
        {"name": "", "address": "", "capital": 0.0, "ownership": 100.0, "member_type": "Individual"}
    ]

def add_member():
    st.session_state.members.append(
        {"name": "", "address": "", "capital": 0.0, "ownership": 0.0, "member_type": "Individual"}
    )

def remove_member(idx):
    if len(st.session_state.members) > 1:
        st.session_state.members.pop(idx)

def distribute_equally():
    n = len(st.session_state.members)
    share = round(100.0 / n, 4)
    for i in range(n):
        st.session_state.members[i]["ownership"] = share
    # Correct rounding on last member
    total = sum(m["ownership"] for m in st.session_state.members)
    diff = round(100.0 - total, 4)
    if diff != 0:
        st.session_state.members[-1]["ownership"] = round(
            st.session_state.members[-1]["ownership"] + diff, 4
        )

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

    # ── Ownership summary bar ────────────────────────────────────────────────
    total_ownership = sum(m["ownership"] for m in st.session_state.members)
    bar_color = "#198754" if abs(total_ownership - 100.0) < 0.01 else "#dc3545"
    bar_pct = min(total_ownership, 100.0)
    ownership_status = "✅ 100% — Ownership is fully allocated." if abs(total_ownership - 100.0) < 0.01 \
        else f"⚠️ {total_ownership:.2f}% allocated — Must equal exactly 100%."
    tag_class = "tag-ok" if abs(total_ownership - 100.0) < 0.01 else "tag-warn"

    st.markdown(f"""
    <div style="margin-bottom:4px;">
        <span class="{tag_class}">{ownership_status}</span>
    </div>
    <div class="ownership-bar-container">
        <div class="ownership-bar-fill" style="width:{bar_pct}%; background:{bar_color};"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Member count & quick actions ────────────────────────────────────────
    n_members = len(st.session_state.members)
    st.markdown(
        f'<span class="tag-info">👤 {n_members} member{"s" if n_members != 1 else ""} added</span>',
        unsafe_allow_html=True
    )

    col_add, col_dist, col_spacer = st.columns([1, 2, 3])
    with col_add:
        if st.form_submit_button("➕ Add Member", use_container_width=True):
            add_member()
            st.rerun()
    with col_dist:
        if st.form_submit_button("⚖️ Distribute Equally", use_container_width=True):
            distribute_equally()
            st.rerun()

    st.markdown("---")

    # ── Per-member fields ────────────────────────────────────────────────────
    names_seen = {}
    for i, m in enumerate(st.session_state.members):
        label = m["name"].strip() if m["name"].strip() else f"Member {i+1}"
        with st.expander(f"**Member {i+1}** — {label}", expanded=True):

            # Member type
            m_type = st.selectbox(
                "Member Type",
                ["Individual", "Entity (LLC / Corp / Trust)"],
                index=0 if m["member_type"] == "Individual" else 1,
                key=f"mtype_{i}"
            )
            st.session_state.members[i]["member_type"] = (
                "Individual" if m_type == "Individual" else "Entity"
            )

            c1, c2 = st.columns(2)
            with c1:
                name_label = "Full Legal Name" if m_type == "Individual" else "Entity Legal Name"
                name_val = st.text_input(name_label, value=m["name"], key=f"name_{i}")
                st.session_state.members[i]["name"] = name_val

                # Duplicate check
                name_key = name_val.strip().lower()
                if name_key:
                    if name_key in names_seen:
                        st.warning(f"⚠️ Duplicate name detected: \"{name_val.strip()}\" already used by Member {names_seen[name_key]+1}.")
                    else:
                        names_seen[name_key] = i

            with c2:
                addr_label = "Address" if m_type == "Individual" else "Registered / Principal Address"
                addr_val = st.text_input(addr_label, value=m["address"], key=f"address_{i}")
                st.session_state.members[i]["address"] = addr_val

            c3, c4 = st.columns(2)
            with c3:
                cap_val = st.number_input(
                    "Capital Contribution ($)",
                    min_value=0.0,
                    value=float(m["capital"]),
                    step=500.0,
                    format="%.2f",
                    key=f"capital_{i}"
                )
                st.session_state.members[i]["capital"] = cap_val

            with c4:
                own_val = st.number_input(
                    "Ownership Percentage (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(m["ownership"]),
                    step=0.01,
                    format="%.4f",
                    key=f"ownership_{i}"
                )
                st.session_state.members[i]["ownership"] = own_val

            # Remove button (only if more than 1 member)
            if len(st.session_state.members) > 1:
                if st.form_submit_button(f"🗑️ Remove Member {i+1}", key=f"remove_{i}"):
                    remove_member(i)
                    st.rerun()

    st.markdown("---")

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
# ROMAN NUMERAL HELPER
# =========================
def roman(n):
    val  = [1000,900,500,400,100,90,50,40,10,9,5,4,1]
    syms = ['M','CM','D','CD','C','XC','L','XL','X','IX','V','IV','I']
    result = ''
    for i in range(len(val)):
        while n >= val[i]:
            result += syms[i]
            n -= val[i]
    return result


# =========================
# PDF GENERATION FUNCTION
# =========================
def generate_pdf(members):
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

    # ── TABLE OF CONTENTS ────────────────────────────────────────────────────
    elements.append(PageBreak())
    elements.append(Paragraph("TABLE OF CONTENTS", s["article"]))
    toc_items = [
        ("Article I",    "Formation"),
        ("Article II",   "Business Purpose"),
        ("Article III",  "Term"),
        ("Article IV",   "Members and Capital Contributions"),
        ("Article V",    "Allocation of Profits and Losses"),
        ("Article VI",   "Distributions"),
        ("Article VII",  "Management and Authority"),
        ("Article VIII", "Voting Rights and Member Meetings"),
        ("Article IX",   "Books, Records, and Accounting"),
        ("Article X",    "Tax Treatment"),
        ("Article XI",   "Transfer of Membership Interest"),
        ("Article XII",  "Admission of New Members"),
        ("Article XIII", "Withdrawal and Dissociation of Members"),
        ("Article XIV",  "Dissolution and Winding Up"),
        ("Article XV",   "Indemnification and Liability"),
        ("Article XVI",  "Dispute Resolution"),
    ]
    art_num = 17
    if non_compete_clause:
        toc_items.append((f"Article {roman(art_num)}", "Non-Compete and Non-Solicitation"))
        art_num += 1
    if confidentiality_clause:
        toc_items.append((f"Article {roman(art_num)}", "Confidentiality"))
        art_num += 1
    if buyout_clause:
        toc_items.append((f"Article {roman(art_num)}", "Right of First Refusal and Buyout"))
        art_num += 1
    toc_items.append((f"Article {roman(art_num)}", "General Provisions and Amendments"))
    toc_items.append(("Schedule A", "Members and Capital Contributions"))

    toc_data = [[Paragraph(a, s["small"]), Paragraph(t, s["small"])] for a, t in toc_items]
    toc_table = Table(toc_data, colWidths=[1.6 * inch, 4.4 * inch])
    toc_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.25, colors.HexColor("#eeeeee")),
    ]))
    elements.append(toc_table)

    # ── ARTICLE I – FORMATION ────────────────────────────────────────────────
    elements.append(PageBreak())
    elements.extend(article_heading("ARTICLE I — FORMATION"))
    elements.append(section_heading("1.1  Name"))
    elements.append(body(
        f"The name of the limited liability company is {company_name} LLC (the \"Company\")."
    ))
    elements.append(section_heading("1.2  State of Organization"))
    elements.append(body(
        f"The Company is organized under the laws of the State of {state} and shall be governed by the applicable "
        f"provisions of the {state} Limited Liability Company Act, as amended from time to time."
    ))
    elements.append(section_heading("1.3  Principal Office"))
    elements.append(body(
        f"The principal office of the Company shall be located at {principal_address or '[Principal Address]'}. "
        "The Company may establish additional offices at such other locations as the Members may determine."
    ))
    elements.append(section_heading("1.4  Registered Agent"))
    elements.append(body(
        f"The registered agent for service of process is {registered_agent_name or '[Registered Agent Name]'}, "
        f"located at {registered_agent_address or '[Registered Agent Address]'}. The registered agent may be changed "
        "by filing the appropriate form with the state and providing notice to all Members."
    ))
    elements.append(section_heading("1.5  Effective Date"))
    elements.append(body(
        f"This Agreement shall be effective as of {formation_date.strftime('%B %d, %Y')}."
    ))

    # ── ARTICLE II – PURPOSE ─────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE II — BUSINESS PURPOSE"))
    elements.append(section_heading("2.1  Purpose"))
    elements.append(body(
        f"The purpose of the Company is to engage in {purpose or 'any lawful business activity permitted under applicable law'}. "
        "The Company may also engage in any and all activities necessary, incidental, or ancillary to the foregoing purpose."
    ))
    elements.append(section_heading("2.2  Powers"))
    elements.append(body(
        "The Company shall have the power to do all things necessary or convenient to carry out its business and affairs, "
        "including but not limited to: entering into contracts; acquiring, holding, and disposing of property; borrowing "
        "money; and taking any other action permitted under applicable law."
    ))

    # ── ARTICLE III – TERM ───────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE III — TERM"))
    elements.append(section_heading("3.1  Duration"))
    if duration == "Perpetual":
        elements.append(body(
            "The Company shall have a perpetual existence unless dissolved in accordance with the provisions "
            "of this Agreement or as required by applicable law."
        ))
    else:
        elements.append(body(
            f"The Company shall continue for a term of {duration_detail or '[specified term]'}, "
            "unless earlier dissolved in accordance with the provisions of this Agreement or applicable law."
        ))

    # ── ARTICLE IV – MEMBERS & CAPITAL ──────────────────────────────────────
    elements.extend(article_heading("ARTICLE IV — MEMBERS AND CAPITAL CONTRIBUTIONS"))
    elements.append(section_heading("4.1  Initial Members"))
    elements.append(body(
        "The initial Members of the Company, their addresses, capital contributions, and ownership percentages "
        "are set forth in Schedule A attached hereto and incorporated herein by reference."
    ))

    # Members table
    total_capital = sum(m["capital"] for m in members)
    header_row = [
        Paragraph("Member Name", s["section"]),
        Paragraph("Type", s["section"]),
        Paragraph("Address", s["section"]),
        Paragraph("Capital ($)", s["section"]),
        Paragraph("Ownership (%)", s["section"]),
    ]
    member_rows = [header_row]
    for m in members:
        member_rows.append([
            Paragraph(m["name"] or "—", s["small"]),
            Paragraph(m.get("member_type", "Individual"), s["small"]),
            Paragraph(m["address"] or "—", s["small"]),
            Paragraph(f"${m['capital']:,.2f}", s["small"]),
            Paragraph(f"{m['ownership']:.4f}%", s["small"]),
        ])
    member_rows.append([
        Paragraph("TOTAL", s["section"]),
        Paragraph("", s["small"]),
        Paragraph("", s["small"]),
        Paragraph(f"${total_capital:,.2f}", s["section"]),
        Paragraph("100.0000%", s["section"]),
    ])
    members_table = Table(
        member_rows,
        colWidths=[1.4*inch, 0.7*inch, 1.8*inch, 1.0*inch, 1.1*inch]
    )
    members_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#e8e8f0")),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [colors.white, colors.HexColor("#f5f5fa")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    elements.append(members_table)
    elements.append(spacer(0.15))

    elements.append(section_heading("4.2  Additional Capital Contributions"))
    elements.append(body(
        "No Member shall be required to make any additional capital contribution to the Company without such "
        "Member's prior written consent. The Members may, by unanimous written agreement, agree to make "
        "additional capital contributions in such amounts and at such times as they may determine."
    ))
    elements.append(section_heading("4.3  Capital Accounts"))
    elements.append(body(
        "A separate capital account shall be maintained for each Member. Each Member's capital account shall "
        "be credited with such Member's capital contributions and allocated share of profits, and shall be "
        "debited with such Member's allocated share of losses and distributions."
    ))
    elements.append(section_heading("4.4  No Interest on Capital"))
    elements.append(body(
        "No Member shall be entitled to receive interest on their capital contribution unless otherwise "
        "unanimously agreed in writing by all Members."
    ))
    elements.append(section_heading("4.5  Return of Capital"))
    elements.append(body(
        "No Member shall have the right to demand or receive the return of their capital contribution except "
        "upon dissolution and winding up of the Company or as otherwise agreed in writing by all Members."
    ))

    # ── ARTICLE V – PROFITS & LOSSES ─────────────────────────────────────────
    elements.extend(article_heading("ARTICLE V — ALLOCATION OF PROFITS AND LOSSES"))
    elements.append(section_heading("5.1  Allocation of Profits"))
    elements.append(body(
        "The net profits of the Company for each fiscal year shall be allocated among the Members in proportion "
        "to their respective ownership percentages as set forth in Schedule A, unless otherwise agreed in writing."
    ))
    elements.append(section_heading("5.2  Allocation of Losses"))
    elements.append(body(
        "The net losses of the Company for each fiscal year shall be allocated among the Members in proportion "
        "to their respective ownership percentages, subject to the limitations of applicable tax law regarding "
        "the deductibility of losses."
    ))
    elements.append(section_heading("5.3  Special Allocations"))
    elements.append(body(
        "Notwithstanding the foregoing, the Members may agree in writing to make special allocations of income, "
        "gain, loss, or deduction for tax purposes, provided such allocations have substantial economic effect "
        "as required under the Internal Revenue Code and Treasury Regulations."
    ))

    # ── ARTICLE VI – DISTRIBUTIONS ───────────────────────────────────────────
    elements.extend(article_heading("ARTICLE VI — DISTRIBUTIONS"))
    elements.append(section_heading("6.1  Distributions"))
    elements.append(body(
        f"Distributions of available cash or other assets shall be made {distribution_frequency.lower()} "
        "to the Members in proportion to their respective ownership percentages, subject to the retention of "
        "reasonable reserves for Company operations, liabilities, and contingencies."
    ))
    elements.append(section_heading("6.2  Limitations on Distributions"))
    elements.append(body(
        f"No distribution shall be made to any Member if, after giving effect to such distribution, the Company "
        "would be unable to pay its debts as they become due in the ordinary course of business, or if such "
        f"distribution would violate applicable {state} law."
    ))
    elements.append(section_heading("6.3  Tax Distributions"))
    elements.append(body(
        "To the extent funds are available, the Company shall make quarterly tax distributions to each Member "
        "in an amount sufficient to enable each Member to pay estimated income taxes on their allocable share "
        "of Company taxable income, calculated at the highest combined federal and state marginal rate applicable."
    ))

    # ── ARTICLE VII – MANAGEMENT ─────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE VII — MANAGEMENT AND AUTHORITY"))
    if management_type == "Member-Managed":
        elements.append(section_heading("7.1  Member-Managed"))
        elements.append(body(
            "The Company shall be managed by its Members. Each Member shall have the right and authority to "
            "act on behalf of the Company in the ordinary course of its business, subject to the voting "
            "requirements set forth in Article VIII."
        ))
        elements.append(section_heading("7.2  Authority of Members"))
        elements.append(body(
            "Each Member is hereby authorized to execute contracts, open and manage bank accounts, hire and "
            "terminate employees, and take all other actions necessary to carry out the Company's business, "
            "provided that major decisions shall require Member approval as set forth in Article VIII."
        ))
    else:
        elements.append(section_heading("7.1  Manager-Managed"))
        elements.append(body(
            f"The business and affairs of the Company shall be managed by one or more Managers. The initial "
            f"Manager(s) of the Company shall be {manager_name or '[Manager Name]'}, located at "
            f"{manager_address or '[Manager Address]'}."
        ))
        elements.append(section_heading("7.2  Authority of Manager"))
        elements.append(body(
            "The Manager(s) shall have full and exclusive authority to manage and control the business and "
            "affairs of the Company, including the power to execute contracts, manage accounts, hire personnel, "
            "and take all actions in the ordinary course of business, subject to the limitations set forth herein."
        ))
        elements.append(section_heading("7.3  Limitations on Manager Authority"))
        elements.append(body(
            f"Without the approval of Members by {voting_threshold_major.lower()}, no Manager shall: "
            "(a) sell, lease, or otherwise dispose of all or substantially all of the Company's assets; "
            "(b) merge or consolidate the Company with another entity; (c) incur indebtedness exceeding "
            "$50,000 in any single transaction; (d) admit new Members; or (e) amend this Agreement."
        ))
        elements.append(section_heading("7.4  Removal and Replacement of Manager"))
        elements.append(body(
            f"A Manager may be removed with or without cause by a {voting_threshold_major.lower()} vote of "
            "the Members. A successor Manager shall be elected by the same voting threshold."
        ))

    elements.append(section_heading("7.3  Officers" if management_type == "Member-Managed" else "7.5  Officers"))
    elements.append(body(
        "The Members or Manager(s) may appoint officers of the Company, including a President, Vice President, "
        "Secretary, and Treasurer, with such duties and compensation as the Members or Managers may determine. "
        "Officers serve at the pleasure of the Members or Managers and may be removed at any time."
    ))

    # ── ARTICLE VIII – VOTING ────────────────────────────────────────────────
    elements.extend(article_heading("ARTICLE VIII — VOTING RIGHTS AND MEMBER MEETINGS"))
    elements.append(section_heading("8.1  Voting Rights"))
    elements.append(body(
        "Each Member shall be entitled to vote on matters submitted to a vote of the Members in proportion to "
        "their ownership percentage. Voting may be conducted in person, by proxy, or by written consent."
    ))
    elements.append(section_heading("8.2  Major Decisions"))
    elements.append(body(
        f"The following actions shall require approval by {voting_threshold_major.lower()} of the Members: "
        "(a) amendment of this Agreement or the Articles of Organization; (b) sale of all or substantially "
        "all Company assets; (c) merger, consolidation, or reorganization; (d) admission of new Members; "
        "(e) dissolution of the Company; (f) any transaction involving a conflict of interest; and "
        "(g) any other matter designated as a major decision in this Agreement."
    ))
    elements.append(section_heading("8.3  Annual Meeting"))
    elements.append(body(
        "The Members shall hold an annual meeting at a time and place determined by the Members or Managers to "
        "review the financial condition of the Company, elect or confirm Managers (if applicable), and transact "
        "such other business as may properly come before the meeting."
    ))
    elements.append(section_heading("8.4  Special Meetings"))
    elements.append(body(
        "Special meetings of the Members may be called at any time by Members holding at least twenty-five percent "
        "(25%) of the total membership interests, upon not less than five (5) days' prior written notice stating "
        "the purpose of the meeting."
    ))
    elements.append(section_heading("8.5  Written Consent in Lieu of Meeting"))
    elements.append(body(
        "Any action required or permitted to be taken at a meeting of the Members may be taken without a meeting "
        "if all Members consent in writing to such action. Such written consent shall be filed with the minutes "
        "of the Company and shall have the same force and effect as a unanimous vote at a duly convened meeting."
    ))
    elements.append(section_heading("8.6  Quorum"))
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
        "consistent with this tax treatment."
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
        "The Company may purchase and maintain insurance on behalf of any Indemnified Person against any liability "
        "asserted against such person in their official capacity."
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
            f"During the period described in Section {article_num}.1, no Member shall, directly or indirectly, "
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

    # ── GENERAL PROVISIONS ───────────────────────────────────────────────────
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
            [Paragraph("Signature:", s["small"]),        Paragraph("_" * 42, s["small"])],
            [Paragraph("Printed Name:", s["small"]),     Paragraph(m["name"] or "____________________", s["small"])],
            [Paragraph("Member Type:", s["small"]),      Paragraph(m.get("member_type", "Individual"), s["small"])],
            [Paragraph("Date:", s["small"]),             Paragraph("____________________", s["small"])],
            [Paragraph("Ownership Interest:", s["small"]), Paragraph(f"{m['ownership']:.4f}%", s["small"])],
            [Paragraph("Capital Contribution:", s["small"]), Paragraph(f"${m['capital']:,.2f}", s["small"])],
        ]
        sig_table = Table(sig_data, colWidths=[1.6 * inch, 4.0 * inch])
        sig_table.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ]))
        elements.append(KeepTogether([sig_table, spacer(0.4)]))

    if management_type == "Manager-Managed" and manager_name:
        elements.append(spacer(0.2))
        elements.append(Paragraph("MANAGER SIGNATURE", s["section"]))
        elements.append(spacer(0.1))
        sig_data = [
            [Paragraph("Signature:", s["small"]),    Paragraph("_" * 42, s["small"])],
            [Paragraph("Manager Name:", s["small"]), Paragraph(manager_name or "____________________", s["small"])],
            [Paragraph("Date:", s["small"]),         Paragraph("____________________", s["small"])],
        ]
        sig_table = Table(sig_data, colWidths=[1.6 * inch, 4.0 * inch])
        sig_table.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
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


# =========================
# GENERATE ON SUBMIT
# =========================
if submit:
    members_snapshot = [dict(m) for m in st.session_state.members]
    total_own = sum(m["ownership"] for m in members_snapshot)
    errors = []

    if not company_name or not state:
        errors.append("LLC Name and State of Formation are required.")
    if abs(total_own - 100.0) >= 0.01:
        errors.append(
            f"Total ownership is **{total_own:.4f}%** — it must equal exactly **100%**. "
            "Use the '⚖️ Distribute Equally' button or adjust individual percentages."
        )
    missing_names = [i+1 for i, m in enumerate(members_snapshot) if not m["name"].strip()]
    if missing_names:
        errors.append(
            f"Full Legal Name is required for Member(s): {', '.join(str(n) for n in missing_names)}."
        )
    # Duplicate name check
    seen = {}
    for i, m in enumerate(members_snapshot):
        key = m["name"].strip().lower()
        if key:
            if key in seen:
                errors.append(
                    f"Duplicate member name: \"{m['name'].strip()}\" appears for both "
                    f"Member {seen[key]+1} and Member {i+1}."
                )
            else:
                seen[key] = i

    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Generating your professional operating agreement..."):
            pdf_path = generate_pdf(members_snapshot)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.success("✅ Your Operating Agreement has been generated successfully!")

        # Member summary table in the UI
        st.markdown("#### 👥 Member Summary")
        summary_cols = st.columns([3, 2, 2, 2])
        summary_cols[0].markdown("**Name**")
        summary_cols[1].markdown("**Type**")
        summary_cols[2].markdown("**Capital**")
        summary_cols[3].markdown("**Ownership**")
        for m in members_snapshot:
            c = st.columns([3, 2, 2, 2])
            c[0].write(m["name"])
            c[1].write(m.get("member_type", "Individual"))
            c[2].write(f"${m['capital']:,.2f}")
            c[3].write(f"{m['ownership']:.4f}%")

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
