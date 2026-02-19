"""SVG template: Skill Constellations — star map of skills grouped by arm (850x400)."""

import math

from generator.utils import deterministic_random, esc, resolve_arm_colors

WIDTH, HEIGHT = 850, 500
ZONE_PADDING = 20
STAR_MAX_RADIUS = 6.0
STAR_MIN_RADIUS = 3.0
LINE_OPACITY = 0.2


def _build_defs(arm_colors, theme):
    """Build CSS keyframes, glow filters, and gradients."""
    parts = []

    # Glow filter per arm
    for i, color in enumerate(arm_colors):
        parts.append(f'''    <filter id="const-glow-{i}" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="3" in="SourceGraphic" result="blur"/>
      <feFlood flood-color="{color}" flood-opacity="0.5" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>''')

    # CSS animations
    parts.append('''    <style>
      @keyframes const-twinkle {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
      }
      @keyframes const-line-draw {
        from { stroke-dashoffset: var(--line-len); }
        to { stroke-dashoffset: 0; }
      }
      @keyframes const-label-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }
    </style>''')

    return "\n".join(parts)


def _build_starfield(theme):
    """Build ambient background stars."""
    stars = []
    count = 30
    sx = deterministic_random("const-bg-x", count, 5, WIDTH - 5)
    sy = deterministic_random("const-bg-y", count, 5, HEIGHT - 5)
    sr = deterministic_random("const-bg-r", count, 0.3, 0.8)
    so = deterministic_random("const-bg-o", count, 0.05, 0.25)
    sd = deterministic_random("const-bg-d", count, 4.0, 8.0)
    for i in range(count):
        stars.append(
            f'  <circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.1f}" '
            f'fill="{theme["text_dim"]}" opacity="{so[i]:.2f}">'
            f'<animate attributeName="opacity" values="{so[i]:.2f};{min(so[i] * 3, 0.5):.2f};{so[i]:.2f}" '
            f'dur="{sd[i]:.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    return "\n".join(stars)


def _compute_star_positions(items, zone_x, zone_y, zone_w, zone_h, arm_idx):
    """Compute deterministic (x, y, radius) positions for each skill star in a zone.

    Uses a grid-based layout with jitter to spread stars evenly while
    avoiding overlap. Returns list of (x, y, radius, item_name) tuples.
    """
    n = len(items)
    if n == 0:
        return []

    inner_pad = 20
    usable_w = zone_w - inner_pad * 2
    usable_h = zone_h - inner_pad * 2

    # Compute grid dimensions to spread items evenly
    cols = math.ceil(math.sqrt(n * (usable_w / max(usable_h, 1))))
    cols = max(cols, 1)
    rows = math.ceil(n / cols)

    cell_w = usable_w / max(cols, 1)
    cell_h = usable_h / max(rows, 1)

    # Generate jitter values for natural feel
    jx = deterministic_random(f"const_jx_{arm_idx}", n, -cell_w * 0.25, cell_w * 0.25)
    jy = deterministic_random(f"const_jy_{arm_idx}", n, -cell_h * 0.25, cell_h * 0.25)

    positions = []
    for i, item in enumerate(items):
        col = i % cols
        row = i // cols

        x = zone_x + inner_pad + col * cell_w + cell_w / 2 + jx[i]
        y = zone_y + inner_pad + row * cell_h + cell_h / 2 + jy[i]

        # Clamp within zone bounds
        x = max(zone_x + inner_pad, min(x, zone_x + zone_w - inner_pad))
        y = max(zone_y + inner_pad, min(y, zone_y + zone_h - inner_pad))

        # Size: first items are larger (more prominent)
        t = i / max(n - 1, 1)
        radius = STAR_MAX_RADIUS - t * (STAR_MAX_RADIUS - STAR_MIN_RADIUS)

        positions.append((x, y, radius, item))

    return positions


def _build_constellation_group(arm_idx, arm, color, positions, theme):
    """Build one constellation group: lines, stars, labels."""
    parts = []
    n = len(positions)
    if n == 0:
        return ""

    # Constellation lines (connect stars sequentially)
    for i in range(n - 1):
        x1, y1 = positions[i][0], positions[i][1]
        x2, y2 = positions[i + 1][0], positions[i + 1][1]
        line_len = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        delay = i * 0.4

        parts.append(
            f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="0.8" opacity="{LINE_OPACITY}" '
            f'stroke-dasharray="{line_len:.0f}" stroke-dashoffset="{line_len:.0f}" '
            f'style="--line-len: {line_len:.0f}; animation: const-line-draw 1s ease {delay}s forwards"/>'
        )

    # Close the constellation if 4+ items (connect last to middle)
    if n >= 4:
        mid = n // 2
        x1, y1 = positions[-1][0], positions[-1][1]
        x2, y2 = positions[mid][0], positions[mid][1]
        line_len = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        delay = (n - 1) * 0.4
        parts.append(
            f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="0.6" opacity="{LINE_OPACITY * 0.6:.2f}" '
            f'stroke-dasharray="{line_len:.0f}" stroke-dashoffset="{line_len:.0f}" '
            f'style="--line-len: {line_len:.0f}; animation: const-line-draw 1s ease {delay}s forwards"/>'
        )

    # Stars and labels
    for i, (x, y, r, item) in enumerate(positions):
        twinkle_dur = 2.5 + (i % 3) * 0.5
        twinkle_delay = i * 0.2

        # Glow halo
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 3:.1f}" fill="{color}" '
            f'opacity="0.08" filter="url(#const-glow-{arm_idx})"/>'
        )
        # Star circle
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}" '
            f'opacity="0.85" style="animation: const-twinkle {twinkle_dur:.1f}s ease {twinkle_delay:.1f}s infinite"/>'
        )
        # White center for prominent stars
        if r > 4:
            parts.append(
                f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="#ffffff" opacity="0.9"/>'
            )

        # Label
        label_y = y - r - 6
        parts.append(
            f'  <text x="{x:.1f}" y="{label_y:.1f}" fill="{theme["text_dim"]}" '
            f'font-size="9" font-family="monospace" text-anchor="middle" '
            f'opacity="0" style="animation: const-label-in 0.5s ease {twinkle_delay + 0.5}s forwards">'
            f'{esc(item)}</text>'
        )

    return "\n".join(parts)


def _build_group_label(arm_idx, arm, color, zone_x, zone_w, theme):
    """Build the group name label at the bottom of the zone."""
    cx = zone_x + zone_w / 2
    y = HEIGHT - 25

    # Pill background
    text = arm["name"]
    pill_w = len(text) * 8 + 20
    pill_x = cx - pill_w / 2

    parts = []
    parts.append(
        f'  <rect x="{pill_x:.1f}" y="{y - 12}" width="{pill_w}" height="20" rx="10" ry="10" '
        f'fill="{color}" opacity="0.1"/>'
    )
    parts.append(
        f'  <text x="{cx:.1f}" y="{y + 2}" fill="{color}" font-size="11" '
        f'font-family="monospace" text-anchor="middle" font-weight="bold" '
        f'letter-spacing="1">{esc(text)}</text>'
    )
    return "\n".join(parts)


def render(galaxy_arms: list, theme: dict) -> str:
    """Render the skill constellation SVG.

    Args:
        galaxy_arms: list of arm configs with name, color, items
        theme: color palette dict
    """
    arm_colors = resolve_arm_colors(galaxy_arms, theme)
    n_arms = len(galaxy_arms)

    if n_arms == 0:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>
  <text x="{WIDTH / 2}" y="{HEIGHT / 2}" fill="{theme['text_faint']}" font-size="12"
        font-family="monospace" text-anchor="middle" dominant-baseline="middle">No skills configured</text>
</svg>'''

    # Zone geometry: divide canvas into n_arms vertical zones
    zone_w = (WIDTH - ZONE_PADDING * 2) / n_arms
    zone_y = 50
    zone_h = HEIGHT - 100  # 50px top for title, 50px bottom for labels

    # Build SVG layers
    defs_str = _build_defs(arm_colors, theme)
    starfield_str = _build_starfield(theme)

    # Build constellation groups
    groups = []
    labels = []
    for i, arm in enumerate(galaxy_arms):
        zone_x = ZONE_PADDING + i * zone_w
        items = arm.get("items", [])
        color = arm_colors[i]

        positions = _compute_star_positions(items, zone_x, zone_y, zone_w, zone_h, i)
        groups.append(_build_constellation_group(i, arm, color, positions, theme))
        labels.append(_build_group_label(i, arm, color, zone_x, zone_w, theme))

    groups_str = "\n".join(groups)
    labels_str = "\n".join(labels)

    # Zone separator lines (faint vertical dividers)
    dividers = []
    for i in range(1, n_arms):
        x = ZONE_PADDING + i * zone_w
        dividers.append(
            f'  <line x1="{x:.1f}" y1="50" x2="{x:.1f}" y2="{HEIGHT - 50}" '
            f'stroke="{theme["text_faint"]}" stroke-width="0.5" stroke-dasharray="4,6" opacity="0.15"/>'
        )
    dividers_str = "\n".join(dividers)

    # Title
    title = (
        f'  <text x="30" y="32" fill="{theme["text_faint"]}" font-size="11" '
        f'font-family="monospace" letter-spacing="3">SKILL CONSTELLATIONS</text>'
    )
    # Status dot
    cyan = theme.get("synapse_cyan", "#00d4ff")
    status_dot = (
        f'  <circle cx="235" cy="28" r="3" fill="{cyan}" opacity="0.8">'
        f'<animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>'
        f'</circle>'
    )
    total_skills = sum(len(arm.get("items", [])) for arm in galaxy_arms)
    status_text = (
        f'  <text x="{WIDTH - 30}" y="32" fill="{theme["text_faint"]}" font-size="10" '
        f'font-family="monospace" text-anchor="end" opacity="0.5">{total_skills} SKILLS MAPPED</text>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
{defs_str}
  </defs>

  <!-- Background -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Ambient star field -->
{starfield_str}

  <!-- Title -->
{title}
{status_dot}
{status_text}

  <!-- Zone dividers -->
{dividers_str}

  <!-- Constellation groups -->
{groups_str}

  <!-- Group labels -->
{labels_str}
</svg>'''
