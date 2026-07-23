"""
emailer.py — HTML email: raw facts, a VC thesis excerpt, and interrogation
questions. No finished narrative, no synthesis section, no essay.
Georgia serif. Blue accent.
"""

import re

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from typing import Dict

from config import EMAIL_SENDER, EMAIL_RECIPIENT, SMTP_PASSWORD


def _clean(text: str) -> str:
    """
    Safety-net post-processor applied to every piece of rendered text.
    1. Em dash (—) with spaces around it  →  period + space
    2. Em dash (—) without spaces         →  comma + space
    3. En dash (–)                         →  comma + space
    """
    if not text:
        return text
    text = re.sub(r'\s*\u2014\s*', '. ', text)   # em dash  — → .
    text = re.sub(r'\s*\u2013\s*', ', ', text)   # en dash  – → ,
    return text


def _questions_to_html(questions: list) -> str:
    """Render the interrogation questions as a numbered list. No answers, no hints."""
    if not questions:
        return ""
    item_style = (
        'style="margin:0 0 14px 0; font-family:Georgia, serif; font-size:16px; '
        'font-weight:400; color:#222222; line-height:1.6;"'
    )
    items = "".join(f"<li {item_style}>{q}</li>" for q in questions)
    return f'<ol style="margin:0; padding-left:20px;">{items}</ol>'


def _build_vc_excerpt_html(story: Dict) -> str:
    """Render the VC thesis excerpt box. Empty string if no excerpt was grounded."""
    excerpt = story.get("vc_excerpt", "")
    if not excerpt:
        return ""
    firm       = story.get("vc_excerpt_firm", "")
    post_title = story.get("vc_excerpt_post_title", "")
    post_url   = story.get("vc_excerpt_post_url", "")

    attribution = firm
    if post_title:
        attribution += f", &ldquo;{post_title}&rdquo;"

    link_html = (
        f'<a href="{post_url}" style="color:#1A6B3C; text-decoration:none;">{attribution}</a>'
        if post_url else attribution
    )

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 16px 0;">
    <tr>
        <td width="3" style="background-color:#1A6B3C;"></td>
        <td class="box" style="background-color:#E8F5EE; padding:18px 20px;">
            <p style="margin:0 0 8px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#0D3320; text-transform:uppercase; font-weight:700;">VC Thesis Excerpt</p>
            <p style="margin:0 0 8px 0; font-family:Georgia, serif; font-size:16px; font-style:italic; font-weight:400; color:#222222; line-height:1.6;">&ldquo;{excerpt}&rdquo;</p>
            <p style="margin:0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:12px; color:#3A6B50;">&mdash; {link_html}</p>
        </td>
    </tr>
    </table>
"""


def build_html(story: Dict, date_str: str) -> str:
    """
    Build HTML email: raw facts, a VC thesis excerpt, and interrogation
    questions. No narrative, no synthesis, no essay.

    story dict keys: headline, stat_number, stat_label, what_happened,
                     funding_facts, india_lens, source_name, source_url,
                     vc_excerpt, vc_excerpt_firm, vc_excerpt_post_title,
                     vc_excerpt_post_url, interrogation_questions
    """

    # Stat block — only render if we have a number
    stat_html = ""
    if story.get("stat_number"):
        stat_html = f"""
    <p style="margin:20px 0 2px 0;">
        <span class="stat-number" style="font-family:Georgia, serif; font-size:36px; font-weight:400; color:#00BFFF;">{story["stat_number"]}</span>
    </p>
    <p style="margin:0 0 16px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:12px; color:#888888;">{story["stat_label"]}</p>
"""

    # Source link
    source_html = ""
    if story.get("source_url"):
        source_html = f'<a href="{story["source_url"]}" style="color:#0050C8; text-decoration:none;">{story["source_name"]}</a>'
    else:
        source_html = story.get("source_name", "")

    # Clean em/en dashes + convert markdown bold for all body fields
    for field in ['headline', 'what_happened', 'funding_facts', 'india_lens']:
        if story.get(field):
            story[field] = _clean(story[field])
            story[field] = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', story[field])

    # What happened — convert newlines to paragraph breaks
    what_happened = story.get("what_happened", "").replace("\n", "</p><p style=\"margin:22px 0; font-family:Georgia, serif; font-size:16px; font-weight:400; color:#222222; line-height:1.75;\">")

    vc_excerpt_html    = _build_vc_excerpt_html(story)
    questions_html     = _questions_to_html(story.get("interrogation_questions", []))

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily AI Intelligence Briefing</title>
<style>
    @media only screen and (max-width: 640px) {{
        .container {{ width: 100% !important; }}
        .content {{ padding: 24px 20px !important; }}
        .header {{ padding: 36px 20px 10px 20px !important; }}
        .header-border {{ padding: 0 20px 24px 20px !important; }}
        .footer {{ padding: 20px 20px 36px 20px !important; }}
        .topic-title {{ font-size: 23px !important; }}
        .stat-number {{ font-size: 28px !important; }}
        .box {{ padding: 14px 16px !important; }}
    }}
</style>
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5; font-family:Georgia, 'Times New Roman', Times, serif; color:#222222; -webkit-font-smoothing:antialiased;">

<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f5;">
<tr><td align="center" style="padding:16px 8px;">

<table class="container" width="620" cellpadding="0" cellspacing="0" style="background-color:#ffffff; max-width:620px;">

<!-- Header label -->
<tr><td class="header" style="padding:48px 36px 10px 36px;">
    <p style="margin:0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#0050C8; text-transform:uppercase; font-weight:600;">Daily AI Intelligence Briefing</p>
</td></tr>

<!-- Date + rule -->
<tr><td class="header-border" style="padding:0 36px 28px 36px; border-bottom:2px solid #001A5E;">
    <p style="margin:0; font-family:Georgia, serif; font-size:13px; color:#888888; font-weight:400;">{date_str}</p>
</td></tr>

<!-- Body -->
<tr><td class="content" style="padding:36px 36px 20px 36px;">

    <!-- Headline -->
    <h1 class="topic-title" style="margin:0; font-family:Georgia, serif; font-size:27px; font-weight:400; color:#001A5E; line-height:1.35;">{story["headline"]}</h1>

    <!-- Stat callout -->
    {stat_html}

    <!-- What happened -->
    <p style="margin:22px 0; font-family:Georgia, serif; font-size:16px; font-weight:400; color:#222222; line-height:1.75;">{what_happened}</p>

    <!-- Funding Facts -->
    <p style="margin:28px 0 8px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#0050C8; text-transform:uppercase; font-weight:600;">Funding Facts</p>
    <p style="margin:0 0 28px 0; font-family:Georgia, serif; font-size:16px; font-weight:400; color:#222222; line-height:1.75;">{story.get("funding_facts", "")}</p>

    <!-- India Lens box -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 16px 0;">
    <tr>
        <td width="3" style="background-color:#0050C8;"></td>
        <td class="box" style="background-color:#E8EEF8; padding:18px 20px;">
            <p style="margin:0 0 8px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#001A5E; text-transform:uppercase; font-weight:700;">India Lens</p>
            <p style="margin:0; font-family:Georgia, serif; font-size:15px; font-weight:400; color:#222222; line-height:1.7;">{story.get("india_lens", "")}</p>
        </td>
    </tr>
    </table>

    <!-- VC Thesis Excerpt box — empty string if none was grounded -->
    {vc_excerpt_html}

    <!-- Source -->
    <p style="margin:0 0 24px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; color:#aaaaaa;">
        Source: {source_html}
    </p>

    <!-- Interrogation questions — no answers, no hints. Yours to work out. -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0 0 0;">
    <tr>
        <td width="3" style="background-color:#B8332F;"></td>
        <td class="box" style="background-color:#FBEEED; padding:18px 20px;">
            <p style="margin:0 0 12px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#7A1D1A; text-transform:uppercase; font-weight:700;">Defend This Pick</p>
            {questions_html}
        </td>
    </tr>
    </table>

</td></tr>

<!-- Footer -->
<tr><td class="footer" style="padding:24px 36px 40px 36px; border-top:1px solid #e0e0e0;">
    <p style="margin:0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; color:#aaaaaa; text-align:center;">
        Jarvis Daily Briefing &middot; Personal AI Intelligence System
    </p>
</td></tr>

</table>

</td></tr>
</table>

</body>
</html>"""


def send(subject: str, html: str) -> bool:
    """Send via Gmail SMTP. Returns True on success."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(subject, "utf-8")  # RFC 2047 encode — handles ₹, —, emoji
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECIPIENT
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"[emailer] sent → {EMAIL_RECIPIENT}")
        return True

    except Exception as e:
        print(f"[emailer] ERROR: {e}")
        return False
