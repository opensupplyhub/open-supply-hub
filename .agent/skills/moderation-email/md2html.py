#!/usr/bin/env python3
"""Render a list-review markdown artifact to a browser-friendly HTML file.

Dependency-free. Handles the subset used by summary.md / email.md:
headings, bold/italic/inline-code/links, tables, bullet lists,
checklists, horizontal rules, Subject: line.

Usage: python3 md2html.py <input.md> <output.html>
"""
import html
import re
import sys


def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'==([^=]+)==', r'<span style="background-color:#ffeb3b; font-weight:bold">\1</span>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    # autolink bare URLs not already inside an anchor
    t = re.sub(r'(?<![">=])(https?://[^\s<)]+)', r'<a href="\1">\1</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<i>\1</i>', t)
    return t



def render_banner(mode: str, lines: list) -> str:
    styles = {
        'reject': ('#ffebee', '#c62828', '🛑 REJECTED (FEEDBACK PHASE)'),
        'approve': ('#e8f5e9', '#2e7d32', '✅ REMOVE AND APPROVE'),
    }
    bg, border, label = styles.get(mode, ('#fff8e1', '#f9a825', '⚠️ ' + mode.upper()))
    out = [
        f'<div style="background:{bg};border:3px solid {border};'
        'border-radius:8px;padding:14px 18px;margin-bottom:8px;'
        'font-family:-apple-system,Arial,sans-serif">',
        f'<div style="font-size:20px;font-weight:800;color:{border}">{label}</div>',
        '<div style="font-size:12px;color:#666;margin:2px 0 8px">'
        'INTERNAL — for the moderator. Do not include in the email.</div>',
        '<ul style="margin:0;padding-left:1.2em;font-size:14px">',
    ]
    for ln in lines:
        if ln.strip():
            out.append(f'<li>{inline(ln.strip().lstrip("- "))}</li>')
    out.append('</ul></div>')
    out.append(
        '<div style="text-align:center;color:#999;font-family:monospace;'
        'margin:10px 0">──────── ✂️ copy the email below this line ✂️ ────────</div>'
    )
    return '\n'.join(out)

def render(src: str) -> str:
    out = [
        '<meta charset="utf-8">',
        '<div style="font-family: -apple-system, Arial, sans-serif; '
        'font-size: 14px; line-height: 1.55; max-width: 52em; '
        'margin: 2em auto; padding: 0 1em;">',
        '<style>table{border-collapse:collapse;margin:0.8em 0}'
        'td,th{border:1px solid #ccc;padding:4px 9px;text-align:left;'
        'vertical-align:top}th{background:#f2f2f2}'
        'code{background:#f4f4f4;padding:1px 4px;border-radius:3px}</style>',
    ]
    lines = src.split('\n')
    if lines and lines[0].startswith(':::'):
        mode = lines[0][3:].strip()
        end = next(
            (i for i, l in enumerate(lines[1:], 1) if l.strip() == ':::'),
            None,
        )
        if end is not None:  # unclosed banner: render the file as-is
            out.insert(1, render_banner(mode, lines[1:end]))
            lines = lines[end + 1:]
    in_list = in_table = False
    table_row_idx = 0
    for ln in lines:
        stripped = ln.strip()
        is_table = stripped.startswith('|') and stripped.endswith('|')
        if in_table and not is_table:
            out.append('</table>')
            in_table = False
        if in_list and not stripped.startswith('- '):
            out.append('</ul>')
            in_list = False

        if is_table:
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if all(re.fullmatch(r':?-{3,}:?', c) for c in cells if c):
                continue  # separator row
            if not in_table:
                out.append('<table>')
                in_table = True
                table_row_idx = 0
            tag = 'th' if table_row_idx == 0 else 'td'
            out.append(
                '<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells)
                + '</tr>'
            )
            table_row_idx += 1
        elif stripped.startswith('- [ ]') or stripped.startswith('- [x]'):
            if not in_list:
                out.append('<ul style="list-style:none;padding-left:0.5em">')
                in_list = True
            checked = ' checked' if stripped.startswith('- [x]') else ''
            out.append(
                f'<li><input type="checkbox"{checked} disabled> '
                f'{inline(stripped[5:].strip())}</li>'
            )
        elif stripped.startswith('- '):
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'<li>{inline(stripped[2:])}</li>')
        elif stripped.startswith('#'):
            level = min(len(stripped) - len(stripped.lstrip('#')), 4)
            out.append(f'<h{level}>{inline(stripped.lstrip("# "))}</h{level}>')
        elif stripped.startswith('Subject:'):
            out.append(f'<p style="color:#666"><b>{inline(stripped)}</b></p><hr>')
        elif stripped in ('---', '***'):
            out.append('<hr>')
        elif stripped:
            out.append(f'<p>{inline(stripped)}</p>')
    if in_table:
        out.append('</table>')
    if in_list:
        out.append('</ul>')
    out.append('</div>')
    return '\n'.join(out)


def render_csv(src_path: str) -> str:
    import csv
    out = [
        '<meta charset="utf-8">',
        '<div style="font-family: -apple-system, Arial, sans-serif; '
        'font-size: 13px; line-height: 1.4; margin: 1.5em; overflow-x: auto;">',
        '<style>table{border-collapse:collapse}'
        'td,th{border:1px solid #ccc;padding:3px 8px;text-align:left;'
        'vertical-align:top}th{background:#f2f2f2;position:sticky;top:0}'
        'tr:has(td:nth-last-child(2):not(:empty)) td'
        '{background:#fff8e1}</style>',
        '<table>',
    ]
    with open(src_path) as f:
        for i, row in enumerate(csv.reader(f)):
            tag = 'th' if i == 0 else 'td'
            out.append('<tr>' + ''.join(
                f'<{tag}>{html.escape(c)}</{tag}>' for c in row) + '</tr>')
    out.append('</table></div>')
    return '\n'.join(out)


if __name__ == '__main__':
    src_path, dst_path = sys.argv[1], sys.argv[2]
    if src_path.endswith('.csv'):
        rendered = render_csv(src_path)
    else:
        with open(src_path) as f:
            rendered = render(f.read())
    with open(dst_path, 'w') as f:
        f.write(rendered)
    print(f'wrote {dst_path}')
