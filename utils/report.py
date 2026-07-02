# utils/report.py
# Day 7 — PDF Report Generator

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime


# =============================================
# COLOR SCHEME
# =============================================

COLOR_PRIMARY   = colors.HexColor('#1E3A5F')
COLOR_SUCCESS   = colors.HexColor('#00C853')
COLOR_DANGER    = colors.HexColor('#FF1744')
COLOR_WARNING   = colors.HexColor('#FF9100')
COLOR_LIGHT     = colors.HexColor('#F5F5F5')
COLOR_WHITE     = colors.white
COLOR_DARK      = colors.HexColor('#212121')


# =============================================
# HELPER — SCORE COLOR
# =============================================

def get_score_color(score):
    if score >= 70:
        return COLOR_SUCCESS
    elif score >= 50:
        return COLOR_WARNING
    else:
        return COLOR_DANGER


def get_score_label(score):
    if score >= 70:
        return "Strong Match"
    elif score >= 50:
        return "Good Match"
    elif score >= 30:
        return "Partial Match"
    else:
        return "Weak Match"


# =============================================
# MAIN REPORT GENERATOR
# =============================================

def generate_report(results, jd_text):
    """
    Generates a PDF report from ranking results

    Input:
    → results: list of candidate result dicts
    → jd_text: job description text

    Output:
    → PDF as bytes (for Streamlit download)
    """

    # Create PDF in memory
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Get styles
    styles  = getSampleStyleSheet()
    content = []

    # =============================================
    # TITLE SECTION
    # =============================================

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        textColor=COLOR_PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.grey,
        spaceAfter=4,
        alignment=TA_CENTER
    )

    content.append(Paragraph(
        "Resume Ranking Report", title_style
    ))
    content.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        subtitle_style
    ))
    content.append(Spacer(1, 0.2*inch))

    # Divider line
    divider = Table(
        [['']],
        colWidths=[7*inch],
        rowHeights=[2]
    )
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PRIMARY),
    ]))
    content.append(divider)
    content.append(Spacer(1, 0.2*inch))

    # =============================================
    # SUMMARY SECTION
    # =============================================

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLOR_PRIMARY,
        spaceBefore=12,
        spaceAfter=8
    )

    content.append(Paragraph(
        "Summary", section_style
    ))

    # Summary stats
    top_score  = results[0]['Final Score']
    avg_score  = round(
        sum(r['Final Score'] for r in results)
        / len(results), 2
    )
    total      = len(results)

    summary_data = [
        ['Total Candidates', 'Top Score',
         'Average Score', 'Report Date'],
        [
            str(total),
            f"{top_score}%",
            f"{avg_score}%",
            datetime.now().strftime('%d %b %Y')
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[1.75*inch]*4
    )
    summary_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR',   (0,0), (-1,0), COLOR_WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0), 11),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND',  (0,1), (-1,-1), COLOR_LIGHT),
        ('FONTSIZE',    (0,1), (-1,-1), 12),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [COLOR_LIGHT, COLOR_WHITE]),
        ('GRID',        (0,0), (-1,-1),
         0.5, colors.grey),
        ('TOPPADDING',  (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 0.2*inch))

    # =============================================
    # RANKING TABLE
    # =============================================

    content.append(Paragraph(
        "Candidate Rankings", section_style
    ))

    rank_headers = [
        'Rank', 'Name', 'Email',
        'Final Score', 'Skill Score', 'Status'
    ]

    rank_data = [rank_headers]
    for i, r in enumerate(results):
        medal = ["1st", "2nd", "3rd"][i] \
                if i < 3 else f"{i+1}th"
        rank_data.append([
            medal,
            r['Name'],
            r['Email'],
            f"{r['Final Score']}%",
            f"{r['Skill Score']}%",
            get_score_label(r['Final Score'])
        ])

    rank_table = Table(
        rank_data,
        colWidths=[
            0.6*inch, 1.4*inch, 1.8*inch,
            1*inch, 1*inch, 1.2*inch
        ]
    )

    # Base style
    rank_style = [
        ('BACKGROUND',   (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR',    (0,0), (-1,0), COLOR_WHITE),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('GRID',         (0,0), (-1,-1),
         0.5, colors.grey),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS',(0,1), (-1,-1),
         [COLOR_LIGHT, COLOR_WHITE]),
    ]

    # Color score cells based on value
    for i, r in enumerate(results):
        row   = i + 1
        color = get_score_color(r['Final Score'])
        rank_style.append((
            'TEXTCOLOR',
            (3, row), (3, row),
            color
        ))
        rank_style.append((
            'FONTNAME',
            (3, row), (3, row),
            'Helvetica-Bold'
        ))

    rank_table.setStyle(TableStyle(rank_style))
    content.append(rank_table)
    content.append(Spacer(1, 0.2*inch))

    # =============================================
    # SKILL GAP PER CANDIDATE
    # =============================================

    content.append(Paragraph(
        "Skill Gap Analysis", section_style
    ))

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4
    )

    for i, r in enumerate(results):
        medal = ["1st", "2nd", "3rd"][i] \
                if i < 3 else f"{i+1}th"

        # Candidate name heading
        candidate_style = ParagraphStyle(
            f'Candidate{i}',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=COLOR_PRIMARY,
            spaceBefore=10,
            spaceAfter=4
        )
        content.append(Paragraph(
            f"{medal} Place — {r['Name']} "
            f"({r['Final Score']}%)",
            candidate_style
        ))

        # Skill gap table
        skill_headers = ['Skill', 'Status']
        skill_data    = [skill_headers]

        for skill in r.get('JD Skills', []):
            if skill in r['Matched']:
                skill_data.append([skill, 'Present'])
            else:
                skill_data.append([skill, 'Missing'])

        if len(skill_data) > 1:
            skill_table = Table(
                skill_data,
                colWidths=[3*inch, 1.5*inch]
            )

            skill_style = [
                ('BACKGROUND',  (0,0), (-1,0),
                 COLOR_PRIMARY),
                ('TEXTCOLOR',   (0,0), (-1,0),
                 COLOR_WHITE),
                ('FONTNAME',    (0,0), (-1,0),
                 'Helvetica-Bold'),
                ('FONTSIZE',    (0,0), (-1,-1), 9),
                ('ALIGN',       (0,0), (-1,-1),
                 'CENTER'),
                ('GRID',        (0,0), (-1,-1),
                 0.5, colors.grey),
                ('TOPPADDING',  (0,0), (-1,-1), 5),
                ('BOTTOMPADDING',(0,0),(-1,-1), 5),
            ]

            # Color Present/Missing cells
            for j, row in enumerate(skill_data[1:]):
                actual_row = j + 1
                if row[1] == 'Present':
                    skill_style.append((
                        'TEXTCOLOR',
                        (1, actual_row),
                        (1, actual_row),
                        COLOR_SUCCESS
                    ))
                    skill_style.append((
                        'FONTNAME',
                        (1, actual_row),
                        (1, actual_row),
                        'Helvetica-Bold'
                    ))
                else:
                    skill_style.append((
                        'TEXTCOLOR',
                        (1, actual_row),
                        (1, actual_row),
                        COLOR_DANGER
                    ))
                    skill_style.append((
                        'FONTNAME',
                        (1, actual_row),
                        (1, actual_row),
                        'Helvetica-Bold'
                    ))

            skill_table.setStyle(TableStyle(skill_style))
            content.append(skill_table)

        content.append(Spacer(1, 0.1*inch))

    # =============================================
    # FOOTER
    # =============================================

    content.append(Spacer(1, 0.3*inch))
    content.append(divider)
    content.append(Spacer(1, 0.1*inch))

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    content.append(Paragraph(
        "Generated by Resume Ranker — "
        "AI Powered Recruitment Tool",
        footer_style
    ))

    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()