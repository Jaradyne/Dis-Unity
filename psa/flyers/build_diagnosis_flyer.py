"""Build the user-authored one-page PSA with selectable, embedded-font text.

Run from any directory with Python and ReportLab installed. Uses the system
DejaVu Sans fonts, overridable through --font-dir. No network or model calls.
"""
from argparse import ArgumentParser
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

BODY = ("The state cannot call coercion compassion simply because it claims to know "
        "what's best for you. The right to refuse help is part of what makes help "
        "different from control.")


def wrap(text, font, size, width):
    lines, line = [], ''
    for word in text.split():
        candidate = f'{line} {word}'.strip()
        if pdfmetrics.stringWidth(candidate, font, size) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    return lines + ([line] if line else [])


def build(output, font_dir):
    pdfmetrics.registerFont(TTFont('PSA-Display', str(font_dir / 'DejaVuSansCondensed-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('PSA-Body', str(font_dir / 'DejaVuSans.ttf')))
    output.parent.mkdir(parents=True, exist_ok=True)
    page = canvas.Canvas(str(output), pagesize=(612, 792), pageCompression=1, invariant=1)
    page.setTitle('Homelessness is not a psychiatric diagnosis. Neither is disobedience.')
    page.setAuthor('Jared / Garden PSAs / Dis-Unity')
    page.setSubject('User-authored advocacy for autonomy and meaningful consent')
    ink, accent, quiet = HexColor('#151515'), HexColor('#8F2029'), HexColor('#555555')
    page.setFillColor(accent)
    page.rect(42, 745, 528, 6, fill=1, stroke=0)
    for text, y, size, color in [
        ('HOMELESSNESS', 685, 50, ink),
        ('IS NOT A', 625, 50, accent),
        ('PSYCHIATRIC', 565, 50, ink),
        ('DIAGNOSIS.', 505, 50, ink),
        ('NEITHER IS', 418, 43, ink),
        ('DISOBEDIENCE.', 365, 43, accent),
    ]:
        assert pdfmetrics.stringWidth(text, 'PSA-Display', size) <= 528
        page.setFillColor(color)
        page.setFont('PSA-Display', size)
        page.drawString(42, y, text)
    page.setFillColor(accent)
    page.rect(42, 324, 64, 4, fill=1, stroke=0)
    page.setFillColor(ink)
    page.setFont('PSA-Body', 20)
    lines = wrap(BODY, 'PSA-Body', 20, 514)
    for index, line in enumerate(lines):
        page.drawString(42, 282 - index * 28, line)
    assert 282 - (len(lines) - 1) * 28 >= 92, 'Body overlaps footer'
    page.setStrokeColor(HexColor('#D0D0D0'))
    page.setLineWidth(0.6)
    page.line(42, 62, 570, 62)
    page.setFillColor(quiet)
    page.setFont('PSA-Body', 9)
    page.drawString(42, 43, 'GARDEN PSAs')
    page.drawRightString(570, 43, 'github.com/Jaradyne/Dis-Unity')
    page.showPage()
    page.save()


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('homelessness-is-not-a-diagnosis.pdf'))
    parser.add_argument('--font-dir', type=Path, default=Path('/usr/share/fonts/truetype/dejavu'))
    args = parser.parse_args()
    build(args.output, args.font_dir)
