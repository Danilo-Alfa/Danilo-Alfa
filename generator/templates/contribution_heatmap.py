"""SVG template: Contribution Nebula — cosmic heatmap calendar (850x~185)."""

from generator.utils import esc, format_number

WIDTH = 850
CELL_SIZE = 11
CELL_GAP = 3
CELL_RADIUS = 2
LEFT_MARGIN = 45
TOP_MARGIN = 55
BOTTOM_MARGIN = 35
DAYS_PER_WEEK = 7

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

DAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def _cell_color_and_opacity(count, theme):
    """Return (fill_color, opacity) based on contribution count."""
    if count == 0:
        return theme["star_dust"], 0.3
    if count <= 3:
        return theme["synapse_cyan"], 0.25
    if count <= 7:
        return theme["synapse_cyan"], 0.50
    if count <= 11:
        return theme["synapse_cyan"], 0.75
    return theme["synapse_cyan"], 1.0


def _build_defs(theme):
    """Build CSS animations and glow filter."""
    cyan = theme.get("synapse_cyan", "#00d4ff")
    parts = []

    # Cell glow filter for high-activity cells
    parts.append(f'''    <filter id="cell-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="2" in="SourceGraphic" result="blur"/>
      <feFlood flood-color="{cyan}" flood-opacity="0.5" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>''')

    # CSS animations
    parts.append('''    <style>
      @keyframes hm-cell-appear {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: var(--cell-op, 0.3); transform: scale(1); }
      }
      @keyframes hm-cell-pulse {
        0%, 100% { opacity: var(--cell-op, 1); }
        50% { opacity: 1; }
      }
      @keyframes hm-count-glow {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
      }
    </style>''')

    return "\n".join(parts)


def _build_month_labels(weeks, theme):
    """Build month name labels positioned above the correct week columns."""
    parts = []
    if not weeks:
        return ""

    last_month = -1
    for col, week in enumerate(weeks):
        if not week:
            continue
        # Use the first day of each week to determine month
        date_str = week[0].get("date", "")
        if len(date_str) >= 7:
            month = int(date_str[5:7]) - 1  # 0-indexed
            if month != last_month:
                last_month = month
                x = LEFT_MARGIN + col * (CELL_SIZE + CELL_GAP)
                parts.append(
                    f'  <text x="{x}" y="{TOP_MARGIN - 8}" fill="{theme["text_faint"]}" '
                    f'font-size="9" font-family="monospace" opacity="0.7">'
                    f'{MONTH_NAMES[month]}</text>'
                )

    return "\n".join(parts)


def _build_day_labels(theme):
    """Build Mon/Wed/Fri labels on the left side."""
    parts = []
    for day_idx, label in DAY_LABELS.items():
        y = TOP_MARGIN + day_idx * (CELL_SIZE + CELL_GAP) + CELL_SIZE / 2 + 3
        parts.append(
            f'  <text x="{LEFT_MARGIN - 8}" y="{y:.1f}" fill="{theme["text_faint"]}" '
            f'font-size="9" font-family="monospace" text-anchor="end" opacity="0.6">'
            f'{label}</text>'
        )
    return "\n".join(parts)


def _build_cells(weeks, theme):
    """Build all day cells with staggered fade-in animation."""
    parts = []

    for col, week in enumerate(weeks):
        for day in week:
            row = day.get("weekday", 0)
            count = day.get("count", 0)
            fill, opacity = _cell_color_and_opacity(count, theme)

            x = LEFT_MARGIN + col * (CELL_SIZE + CELL_GAP)
            y = TOP_MARGIN + row * (CELL_SIZE + CELL_GAP)
            delay = col * 0.015

            # High activity cells get glow filter
            filter_attr = ' filter="url(#cell-glow)"' if count >= 12 else ""
            pulse = ""
            if count >= 12:
                pulse = f" animation: hm-cell-pulse 3s ease {delay + 1}s infinite;"

            parts.append(
                f'  <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'rx="{CELL_RADIUS}" ry="{CELL_RADIUS}" fill="{fill}"{filter_attr} '
                f'opacity="0" style="--cell-op: {opacity}; '
                f'animation: hm-cell-appear 0.4s ease {delay:.2f}s forwards;{pulse}"/>'
            )

    return "\n".join(parts)


def _build_legend(y_pos, theme):
    """Build the intensity legend at the bottom."""
    parts = []
    legend_x = LEFT_MARGIN

    parts.append(
        f'  <text x="{legend_x}" y="{y_pos + 3}" fill="{theme["text_faint"]}" '
        f'font-size="9" font-family="monospace" opacity="0.6">Less</text>'
    )

    levels = [
        (theme["star_dust"], 0.3),
        (theme["synapse_cyan"], 0.25),
        (theme["synapse_cyan"], 0.50),
        (theme["synapse_cyan"], 0.75),
        (theme["synapse_cyan"], 1.0),
    ]
    start_x = legend_x + 32
    for j, (color, op) in enumerate(levels):
        lx = start_x + j * (CELL_SIZE + 2)
        parts.append(
            f'  <rect x="{lx}" y="{y_pos - 5}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="{CELL_RADIUS}" ry="{CELL_RADIUS}" fill="{color}" opacity="{op}"/>'
        )

    more_x = start_x + len(levels) * (CELL_SIZE + 2) + 4
    parts.append(
        f'  <text x="{more_x}" y="{y_pos + 3}" fill="{theme["text_faint"]}" '
        f'font-size="9" font-family="monospace" opacity="0.6">More</text>'
    )

    return "\n".join(parts)


def render(contributions: dict, theme: dict) -> str:
    """Render the contribution heatmap SVG.

    Args:
        contributions: dict with total_count (int) and weeks (list of week lists)
        theme: color palette dict
    """
    weeks = contributions.get("weeks", [])
    total_count = contributions.get("total_count", 0)

    n_weeks = len(weeks)
    if n_weeks == 0:
        height = 120
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>
  <text x="{WIDTH / 2}" y="{height / 2}" fill="{theme['text_faint']}" font-size="12"
        font-family="monospace" text-anchor="middle" dominant-baseline="middle">No contribution data available</text>
</svg>'''

    # Dynamic height
    height = TOP_MARGIN + DAYS_PER_WEEK * (CELL_SIZE + CELL_GAP) + BOTTOM_MARGIN

    # Build layers
    defs_str = _build_defs(theme)
    months_str = _build_month_labels(weeks, theme)
    days_str = _build_day_labels(theme)
    cells_str = _build_cells(weeks, theme)
    legend_y = TOP_MARGIN + DAYS_PER_WEEK * (CELL_SIZE + CELL_GAP) + 12
    legend_str = _build_legend(legend_y, theme)

    # Title
    title = (
        f'  <text x="30" y="30" fill="{theme["text_faint"]}" font-size="11" '
        f'font-family="monospace" letter-spacing="3">CONTRIBUTION NEBULA</text>'
    )

    # Total counter
    cyan = theme.get("synapse_cyan", "#00d4ff")
    total_str = (
        f'  <text x="{WIDTH - 30}" y="30" fill="{cyan}" font-size="12" '
        f'font-family="monospace" text-anchor="end" font-weight="bold" '
        f'style="animation: hm-count-glow 3s ease infinite">'
        f'{format_number(total_count)} contributions</text>'
    )

    # Status dot
    status_dot = (
        f'  <circle cx="240" cy="26" r="3" fill="{cyan}" opacity="0.8">'
        f'<animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>'
        f'</circle>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
{defs_str}
  </defs>

  <!-- Background -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Title -->
{title}
{status_dot}
{total_str}

  <!-- Month labels -->
{months_str}

  <!-- Day labels -->
{days_str}

  <!-- Contribution cells -->
{cells_str}

  <!-- Legend -->
{legend_str}
</svg>'''
