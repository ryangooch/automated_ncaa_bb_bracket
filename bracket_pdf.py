"""Generate a visually appealing NCAA tournament bracket as a PDF."""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.colors import HexColor
import datetime
import os


# Page and layout
PAGE_W, PAGE_H = landscape(letter)  # 792 x 612
MARGIN = 15
TITLE_H = 20
HEADER_H = 16
FF_H = 48

# Colors
DARK = HexColor('#1a1a1a')
NAVY = HexColor('#0a2240')
MID_GRAY = HexColor('#666666')
LINE_COLOR = HexColor('#333333')

# Bracket constants
MATCHUP_ORDER = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
REGION_NAMES = ['SOUTH', 'WEST', 'EAST', 'MIDWEST']


def generate_bracket_pdf(final_68_df, output_path=None, title=None):
    """Generate a PDF bracket from the final 68 teams DataFrame.

    Parameters
    ----------
    final_68_df : pd.DataFrame
        Must contain columns 'Team', 'seed' (and optionally 'Conf').
        Expected to have 68 rows sorted by overall rank.
    output_path : str, optional
        Where to save the PDF.  Defaults to brackets/bracket_<date>.pdf
    title : str, optional
        Title printed at the top of the bracket.

    Returns
    -------
    str – path to the saved PDF file.
    """
    if output_path is None:
        today = datetime.date.today().isoformat()
        output_path = f'brackets/bracket_{today}.pdf'

    if title is None:
        year = datetime.date.today().year
        title = f'{year} NCAA TOURNAMENT BRACKET'

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    regions, first_four = _assign_teams(final_68_df)

    c = pdf_canvas.Canvas(output_path, pagesize=landscape(letter))

    # Vertical zones
    bracket_top = PAGE_H - MARGIN - TITLE_H - HEADER_H
    bracket_bottom = MARGIN + FF_H
    bracket_h = bracket_top - bracket_bottom

    region_gap = 8
    region_h = (bracket_h - region_gap) / 2

    # Uniform column widths: 11 equal cols (4 left + 3 center + 4 right)
    # Team names are drawn inside the first round column on each side.
    total_w = PAGE_W - 2 * MARGIN
    round_w = total_w / 11
    center_w = round_w * 3
    half_w = round_w * 4
    name_w = 0

    # Title
    c.setFont('Helvetica-Bold', 14)
    c.setFillColor(NAVY)
    c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - 15, title)

    # Round headers
    _draw_round_headers(c, MARGIN, half_w, center_w, name_w, round_w,
                        PAGE_H - MARGIN - TITLE_H - 10)

    # Four regions
    left_x = MARGIN
    right_x = PAGE_W - MARGIN - half_w
    top_y = bracket_top
    bot_y = bracket_top - region_h - region_gap

    configs = [
        (left_x,  top_y, 'right'),   # region 0 – top-left
        (left_x,  bot_y, 'right'),   # region 1 – bottom-left
        (right_x, top_y, 'left'),    # region 2 – top-right
        (right_x, bot_y, 'left'),    # region 3 – bottom-right
    ]

    finals_y = []
    for i, (rx, ry, d) in enumerate(configs):
        teams = _matchup_order(regions[i])
        fy = _draw_region(c, teams, rx, ry, d, half_w, region_h,
                          name_w, round_w, REGION_NAMES[i])
        finals_y.append(fy)

    # Final Four + Championship
    _draw_final_four(c, MARGIN + half_w, center_w, finals_y, round_w)

    # First Four
    _draw_first_four(c, first_four, MARGIN, MARGIN + 2,
                     PAGE_W - 2 * MARGIN, FF_H - 6)

    c.save()
    return output_path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _assign_teams(df):
    """S-curve assignment of 68 teams into 4 regions + First Four list."""
    regions = {i: {} for i in range(4)}
    first_four = []

    seed_groups = {}
    for _, row in df.iterrows():
        seed = int(row['seed'])
        seed_groups.setdefault(seed, []).append(row['Team'])

    for seed in sorted(seed_groups):
        teams = seed_groups[seed]
        order = [0, 1, 2, 3] if seed % 2 == 1 else [3, 2, 1, 0]

        if len(teams) == 4:
            for i, r in enumerate(order):
                regions[r][seed] = teams[i]
        elif len(teams) == 6:
            # First two go directly; next four form two play-in games
            regions[order[0]][seed] = teams[0]
            regions[order[1]][seed] = teams[1]
            regions[order[2]][seed] = 'Play-in'
            regions[order[3]][seed] = 'Play-in'
            first_four.append((teams[2], teams[3], seed))
            first_four.append((teams[4], teams[5], seed))

    return regions, first_four


def _matchup_order(region):
    """Return [(seed, team), ...] in standard bracket order for a region."""
    return [(s, region.get(s, 'TBD')) for s in MATCHUP_ORDER]


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _draw_round_headers(c, margin, half_w, center_w, name_w, round_w, y):
    c.setFont('Helvetica', 5.5)
    c.setFillColor(MID_GRAY)

    left_labels = ['1st Round', '2nd Round', 'Sweet 16', 'Elite Eight']
    for i, lbl in enumerate(left_labels):
        x = margin + (i + 0.5) * round_w
        c.drawCentredString(x, y, lbl)

    cx = margin + half_w
    c.setFont('Helvetica', 5)
    c.drawCentredString(cx + center_w * 0.2, y, 'Final Four')
    c.setFont('Helvetica-Bold', 5)
    c.drawCentredString(cx + center_w * 0.5, y, 'Championship')
    c.setFont('Helvetica', 5)
    c.drawCentredString(cx + center_w * 0.8, y, 'Final Four')

    right_labels = ['Elite Eight', 'Sweet 16', '2nd Round', '1st Round']
    rx = margin + half_w + center_w
    for i, lbl in enumerate(right_labels):
        x = rx + (i + 0.5) * round_w
        c.drawCentredString(x, y, lbl)

    # Thin separator line under headers
    c.setStrokeColor(HexColor('#cccccc'))
    c.setLineWidth(0.3)
    c.line(margin, y - 4, PAGE_W - margin, y - 4)


def _draw_region(c, teams, x0, y0, direction, width, height,
                 name_w, round_w, region_name):
    """Draw one 16-team region bracket. Returns y of region winner."""
    n = 16
    slot_h = height / n

    # y positions per round (round 0 = 16 slots, ..., round 4 = 1 slot)
    ys = [[y0 - (i + 0.5) * slot_h for i in range(n)]]
    for _ in range(4):
        prev = ys[-1]
        ys.append([(prev[j] + prev[j + 1]) / 2
                   for j in range(0, len(prev), 2)])

    # x of each vertical junction — names are inside the first round column
    if direction == 'right':
        jx = [x0 + (i + 1) * round_w for i in range(4)]
    else:
        jx = [x0 + width - (i + 1) * round_w for i in range(4)]

    # Region label – above the bracket area
    c.setFont('Helvetica-Bold', 5.5)
    c.setFillColor(NAVY)
    label_y = y0 + 5
    if direction == 'right':
        c.drawString(x0, label_y, region_name)
    else:
        c.drawRightString(x0 + width, label_y, region_name)

    # Bracket lines
    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.5)

    for rd in range(4):
        positions = ys[rd]
        if rd == 0:
            h_start = x0 if direction == 'right' else x0 + width
        else:
            h_start = jx[rd - 1]

        for j in range(0, len(positions), 2):
            yt, yb = positions[j], positions[j + 1]
            c.line(h_start, yt, jx[rd], yt)
            c.line(h_start, yb, jx[rd], yb)
            c.line(jx[rd], yt, jx[rd], yb)

    # Winner line
    wy = ys[4][0]
    if direction == 'right':
        c.line(jx[3], wy, jx[3] + round_w * 0.5, wy)
    else:
        c.line(jx[3], wy, jx[3] - round_w * 0.5, wy)

    # Team names (drawn inside the first round column)
    for i, (seed, team) in enumerate(teams):
        y = ys[0][i]
        display = team if len(team) <= 16 else team[:15] + '.'

        if direction == 'right':
            c.setFont('Helvetica-Bold', 5.5)
            c.setFillColor(DARK)
            c.drawString(x0 + 1, y + 1.5, str(seed))
            c.setFont('Helvetica', 5.5)
            c.drawString(x0 + 12, y + 1.5, display)
        else:
            c.setFont('Helvetica', 5.5)
            c.setFillColor(DARK)
            c.drawRightString(x0 + width - 12, y + 1.5, display)
            c.setFont('Helvetica-Bold', 5.5)
            c.drawRightString(x0 + width - 1, y + 1.5, str(seed))

    return wy


def _draw_final_four(c, cx, cw, finals_y, round_w):
    """Draw Final Four and Championship connectors in the center."""
    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.5)

    semi_w = cw / 3

    # Left semifinal (regions 0 & 1)
    y0, y1 = finals_y[0], finals_y[1]
    lj = cx + semi_w
    c.line(cx, y0, lj, y0)
    c.line(cx, y1, lj, y1)
    c.line(lj, y0, lj, y1)
    l_mid = (y0 + y1) / 2

    # Right semifinal (regions 2 & 3)
    y2, y3 = finals_y[2], finals_y[3]
    rj = cx + cw - semi_w
    c.line(cx + cw, y2, rj, y2)
    c.line(cx + cw, y3, rj, y3)
    c.line(rj, y2, rj, y3)
    r_mid = (y2 + y3) / 2

    # Championship
    champ_x = cx + cw / 2
    c.line(lj, l_mid, champ_x, l_mid)
    c.line(rj, r_mid, champ_x, r_mid)
    c.line(champ_x, l_mid, champ_x, r_mid)

    # Champion winner line + label
    champ_mid = (l_mid + r_mid) / 2
    c.line(champ_x - 18, champ_mid, champ_x + 18, champ_mid)
    c.setFont('Helvetica-Bold', 6)
    c.setFillColor(NAVY)
    c.drawCentredString(champ_x, champ_mid + 10, 'NATIONAL')
    c.drawCentredString(champ_x, champ_mid + 3, 'CHAMPION')


def _draw_first_four(c, first_four, x0, y0, width, height):
    """Draw First Four play-in matchups at the bottom."""
    if not first_four:
        return

    # Section label
    c.setFont('Helvetica-Bold', 7)
    c.setFillColor(NAVY)
    c.drawString(x0, y0 + height - 2, 'FIRST FOUR')

    # Separator line above
    c.setStrokeColor(HexColor('#cccccc'))
    c.setLineWidth(0.3)
    c.line(x0, y0 + height + 4, x0 + width, y0 + height + 4)

    n = len(first_four)
    game_w = width / n

    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.5)

    for i, (t1, t2, seed) in enumerate(first_four):
        gx = x0 + i * game_w + 8
        yt = y0 + height - 16
        yb = yt - 14

        # Seed labels
        c.setFont('Helvetica-Bold', 6)
        c.setFillColor(DARK)
        c.drawString(gx, yt + 1.5, str(seed))
        c.drawString(gx, yb + 1.5, str(seed))

        # Team names
        c.setFont('Helvetica', 6.5)
        nx = gx + 12
        c.drawString(nx, yt + 1.5, t1[:22])
        c.drawString(nx, yb + 1.5, t2[:22])

        # Mini bracket lines
        line_end = nx + 85
        c.line(nx - 2, yt, line_end, yt)
        c.line(nx - 2, yb, line_end, yb)
        c.line(line_end, yt, line_end, yb)

        mid = (yt + yb) / 2
        c.line(line_end, mid, line_end + 12, mid)
