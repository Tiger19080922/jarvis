"""
emailer.py — HTML email exactly matching the briefing_preview_v4 design.
One story per email. Georgia serif. Blue accent. Four sections.
"""

import re

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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


def _essay_to_html(text: str) -> str:
    """
    Convert essay plain text to HTML.
    Handles:
      - em/en dashes  →  stripped via _clean()
      - ## Heading    →  section headers
      - **bold**      →  <strong>
      - blank lines   →  paragraph breaks
    """
    import re

    text = _clean(text)

    # Split into blocks on blank lines
    blocks = re.split(r'\n{2,}', text.strip())
    html_parts = []

    heading_style = (
        'style="margin:28px 0 8px 0; font-family:Calibri, Helvetica, Arial, sans-serif; '
        'font-size:11px; letter-spacing:2px; color:#1A6B3C; text-transform:uppercase; '
        'font-weight:600;"'
    )
    para_style = (
        'style="margin:0 0 20px 0; font-family:Georgia, serif; font-size:16px; '
        'font-weight:400; color:#222222; line-height:1.8;"'
    )

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Bold inline
        block = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', block)

        if block.startswith('## '):
            heading_text = block[3:].strip()
            html_parts.append(f'<p {heading_style}>{heading_text}</p>')
        elif block.startswith('# '):
            heading_text = block[2:].strip()
            html_parts.append(f'<p {heading_style}>{heading_text}</p>')
        else:
            # Convert single newlines within a block to <br>
            block = block.replace('\n', '<br>')
            html_parts.append(f'<p {para_style}>{block}</p>')

    return '\n'.join(html_parts)


def _pivot_lens_to_html(text: str) -> str:
    """Strip the 'Your Pivot Lens' heading line and return the body as HTML paragraphs."""
    import re

    text = _clean(text)

    lines = text.strip().split('\n')
    # Drop the heading line
    if lines and 'pivot lens' in lines[0].lower():
        lines = lines[1:]

    body = '\n'.join(lines).strip()
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)

    # Split on blank lines into paragraphs
    paras = re.split(r'\n{2,}', body)
    para_style = (
        'style="margin:0 0 12px 0; font-family:Georgia, serif; font-size:15px; '
        'font-weight:400; color:#1A3D2B; line-height:1.7;"'
    )
    parts = [f'<p {para_style}>{p.strip().replace(chr(10), "<br>")}</p>' for p in paras if p.strip()]
    return '\n'.join(parts)


def _build_essay_section(essay: Dict) -> str:
    """Build the full essay HTML block to append below the digest."""
    essay_html   = _essay_to_html(essay["essay_text"])
    pivot_html   = _pivot_lens_to_html(essay["pivot_lens"])
    day_num      = essay["day_number"]
    day_in_week  = essay.get("day_in_week", "")
    days_left    = essay["days_remaining"]
    phase        = essay["phase"]
    topic        = essay["topic"]
    angle        = essay.get("angle", "")
    role_lens    = essay["role_lens"]

    return f"""
<!-- ═══ ESSAY DIVIDER ═══ -->
<tr><td style="padding:40px 36px 0 36px;">
    <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td style="border-top:2px solid #1A6B3C;"></td></tr>
    </table>
</td></tr>

<!-- Essay label -->
<tr><td style="padding:24px 36px 0 36px;">
    <p style="margin:0 0 4px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#1A6B3C; text-transform:uppercase; font-weight:600;">Daily Learning Essay</p>
    <p style="margin:0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; color:#888888;">Day {day_num} of 90 &middot; Day {day_in_week} of 7 &middot; {phase} &middot; {role_lens} Lens &middot; {days_left} days remaining</p>
</td></tr>

<!-- Essay title -->
<tr><td style="padding:12px 36px 0 36px;">
    <h2 style="margin:0; font-family:Georgia, serif; font-size:24px; font-weight:400; color:#0D3320; line-height:1.35;">{topic}</h2>
    <p style="margin:6px 0 0 0; font-family:Georgia, serif; font-size:15px; font-style:italic; color:#3A6B50; line-height:1.4;">{angle}</p>
</td></tr>

<!-- Essay body -->
<tr><td style="padding:20px 36px 0 36px;">
    {essay_html}
</td></tr>

<!-- Pivot lens box -->
<tr><td style="padding:8px 36px 32px 36px;">
    <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
        <td width="3" style="background-color:#1A6B3C;"></td>
        <td style="background-color:#E8F5EE; padding:18px 20px;">
            <p style="margin:0 0 8px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#0D3320; text-transform:uppercase; font-weight:700;">Your Pivot Lens &middot; {role_lens}</p>
            {pivot_html}
        </td>
    </tr>
    </table>
</td></tr>
"""


def build_html(story: Dict, date_str: str, essay: Dict = None) -> str:
    """
    Build HTML email matching the briefing_preview_v4 design exactly.
    story dict keys: headline, stat_number, stat_label, what_happened,
                     why_it_matters, india_lens, implication,
                     source_name, source_url
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
    for field in ['headline', 'what_happened', 'why_it_matters', 'india_lens', 'implication']:
        if story.get(field):
            story[field] = _clean(story[field])
            story[field] = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', story[field])

    # What happened — convert newlines to paragraph breaks
    what_happened = story.get("what_happened", "").replace("\n", "</p><p style=\"margin:22px 0; font-family:Georgia, serif; font-size:16px; font-weight:400; color:#222222; line-height:1.75;\">")

    # Essay section — empty string if no essay was generated
    essay_section = _build_essay_section(essay) if essay else ""

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

    <!-- Why This Matters -->
    <p style="margin:28px 0 8px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#0050C8; text-transform:uppercase; font-weight:600;">Why This Matters</p>
    <p style="margin:0 0 28px 0; font-family:Georgia, serif; font-size:16px; font-weight:400; color:#222222; line-height:1.75;">{story["why_it_matters"]}</p>

    <!-- India Lens box -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 16px 0;">
    <tr>
        <td width="3" style="background-color:#0050C8;"></td>
        <td class="box" style="background-color:#E8EEF8; padding:18px 20px;">
            <p style="margin:0 0 8px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#001A5E; text-transform:uppercase; font-weight:700;">India Lens</p>
            <p style="margin:0; font-family:Georgia, serif; font-size:15px; font-weight:400; color:#222222; line-height:1.7;">{story["india_lens"]}</p>
        </td>
    </tr>
    </table>

    <!-- Implication For You box -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px 0;">
    <tr>
        <td width="3" style="background-color:#001A5E;"></td>
        <td class="box" style="background-color:#f5f5f5; padding:18px 20px;">
            <p style="margin:0 0 8px 0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; letter-spacing:2px; color:#001A5E; text-transform:uppercase; font-weight:700;">Implication For You</p>
            <p style="margin:0; font-family:Georgia, serif; font-size:15px; font-weight:400; color:#333333; line-height:1.7; font-style:italic;">{story["implication"]}</p>
        </td>
    </tr>
    </table>

    <!-- Source -->
    <p style="margin:0; font-family:Calibri, Helvetica, Arial, sans-serif; font-size:11px; color:#aaaaaa;">
        Source: {source_html}
    </p>

</td></tr>

{essay_section}

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
        msg["Subject"] = subject
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECIPIENT
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, SMTP_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

        print(f"[emailer] sent → {EMAIL_RECIPIENT}")
        return True

    except Exception as e:
        print(f"[emailer] ERROR: {e}")
        return False
