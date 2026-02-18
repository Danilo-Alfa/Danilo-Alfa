"""SVG template: Coding Timeline — evolution trail with comet animation (850x200)."""

from generator.utils import esc, resolve_arm_colors

WIDTH, HEIGHT = 850, 200
TIMELINE_Y = 100
LEFT_MARGIN = 60
RIGHT_MARGIN = 60
NODE_RADIUS = 5


def _build_defs(arm_colors, theme):
    """Build comet gradient, glow filters, and CSS animations."""
    parts = []

    # Comet trail gradient
    cyan = theme.get("synapse_cyan", "#00d4ff")
    parts.append(f'''    <linearGradient id="comet-trail-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{cyan}" stop-opacity="0"/>
      <stop offset="70%" stop-color="{cyan}" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.8"/>
    </linearGradient>''')

    # Glow filters per arm color
    for i, color in enumerate(arm_colors):
        parts.append(f'''    <filter id="tl-glow-{i}" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="3" in="SourceGraphic" result="blur"/>
      <feFlood flood-color="{color}" flood-opacity="0.6" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>''')

    # Comet glow
    parts.append(f'''    <filter id="comet-glow" x="-200%" y="-200%" width="500%" height="500%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feFlood flood-color="{cyan}" flood-opacity="0.8" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>''')

    # CSS animations
    parts.append('''    <style>
      @keyframes tl-node-activate {
        0%, 80% { opacity: 0.3; }
        85% { opacity: 1; }
        100% { opacity: 0.8; }
      }
      @keyframes tl-label-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes tl-pulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
      }
    </style>''')

    return "\n".join(parts)


def _build_comet_trail(usable_width, theme):
    """Build the horizontal timeline line."""
    cyan = theme.get("synapse_cyan", "#00d4ff")

    parts = []
    # Main line
    parts.append(
        f'  <line x1="{LEFT_MARGIN}" y1="{TIMELINE_Y}" '
        f'x2="{LEFT_MARGIN + usable_width}" y2="{TIMELINE_Y}" '
        f'stroke="{theme["star_dust"]}" stroke-width="1.5" opacity="0.6"/>'
    )
    # Glowing overlay
    parts.append(
        f'  <line x1="{LEFT_MARGIN}" y1="{TIMELINE_Y}" '
        f'x2="{LEFT_MARGIN + usable_width}" y2="{TIMELINE_Y}" '
        f'stroke="{cyan}" stroke-width="0.5" opacity="0.3"/>'
    )
    return "\n".join(parts)


def _build_nodes_and_labels(entries, usable_width, arm_colors, theme):
    """Build nodes and labels for each timeline entry."""
    parts = []
    comet_dur = 6  # seconds for comet to traverse

    for i, entry in enumerate(entries):
        x = entry["x"]
        arm_idx = entry.get("arm", 0)
        color = arm_colors[arm_idx] if arm_idx < len(arm_colors) else arm_colors[0]

        # Animation delay: node lights up when comet reaches its position
        t = (x - LEFT_MARGIN) / max(usable_width, 1)
        node_delay = t * comet_dur

        # Decide label position: alternate above/below
        above = (i % 2 == 0)
        label_y = TIMELINE_Y - 22 if above else TIMELINE_Y + 32
        connector_y2 = TIMELINE_Y - 10 if above else TIMELINE_Y + 10

        # Connector line from node to label area
        parts.append(
            f'  <line x1="{x:.1f}" y1="{TIMELINE_Y}" x2="{x:.1f}" y2="{connector_y2:.1f}" '
            f'stroke="{color}" stroke-width="0.8" opacity="0" '
            f'style="animation: tl-node-activate 1s ease {node_delay:.1f}s forwards"/>'
        )

        # Glow halo
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{TIMELINE_Y}" r="{NODE_RADIUS + 4}" '
            f'fill="{color}" opacity="0" filter="url(#tl-glow-{arm_idx})" '
            f'style="animation: tl-node-activate 1s ease {node_delay:.1f}s forwards"/>'
        )

        # Node circle
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{TIMELINE_Y}" r="{NODE_RADIUS}" '
            f'fill="{color}" opacity="0" '
            f'style="animation: tl-node-activate 1s ease {node_delay:.1f}s forwards"/>'
        )
        # White center
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{TIMELINE_Y}" r="2" '
            f'fill="#ffffff" opacity="0" '
            f'style="animation: tl-node-activate 1s ease {node_delay:.1f}s forwards"/>'
        )

        # Label text
        parts.append(
            f'  <text x="{x:.1f}" y="{label_y:.1f}" fill="{theme["text_dim"]}" '
            f'font-size="10" font-family="monospace" text-anchor="middle" '
            f'opacity="0" style="animation: tl-label-in 0.6s ease {node_delay + 0.3:.1f}s forwards">'
            f'{esc(entry["label"])}</text>'
        )

    return "\n".join(parts)


def _build_year_markers(entries, theme):
    """Build year labels along the timeline."""
    parts = []
    seen_years = set()

    for entry in entries:
        year = entry["year"]
        if year in seen_years:
            continue
        seen_years.add(year)

        x = entry["x"]
        # Year label above the timeline
        parts.append(
            f'  <text x="{x:.1f}" y="{TIMELINE_Y - 42}" fill="{theme["text_faint"]}" '
            f'font-size="10" font-family="monospace" text-anchor="middle" opacity="0.6">'
            f'{year}</text>'
        )
        # Tick mark
        parts.append(
            f'  <line x1="{x:.1f}" y1="{TIMELINE_Y - 5}" x2="{x:.1f}" y2="{TIMELINE_Y + 5}" '
            f'stroke="{theme["text_faint"]}" stroke-width="1" opacity="0.3"/>'
        )

    return "\n".join(parts)


def _build_comet(usable_width, theme):
    """Build the animated comet that sweeps left-to-right."""
    cyan = theme.get("synapse_cyan", "#00d4ff")
    comet_dur = 6

    # Comet path (horizontal line)
    path = f"M 0,0 L {usable_width},0"

    return (
        f'  <g transform="translate({LEFT_MARGIN},{TIMELINE_Y})">'
        f'\n    <circle r="4" fill="#ffffff" opacity="0.9" filter="url(#comet-glow)">'
        f'\n      <animateMotion path="{path}" dur="{comet_dur}s" repeatCount="indefinite"/>'
        f'\n    </circle>'
        f'\n    <circle r="2" fill="{cyan}" opacity="0.6">'
        f'\n      <animateMotion path="{path}" dur="{comet_dur}s" repeatCount="indefinite"/>'
        f'\n    </circle>'
        f'\n  </g>'
    )


def render(timeline: list, galaxy_arms: list, theme: dict) -> str:
    """Render the coding timeline SVG.

    Args:
        timeline: list of dicts with year, label, arm keys
        galaxy_arms: list of arm configs for color resolution
        theme: color palette dict
    """
    arm_colors = resolve_arm_colors(galaxy_arms, theme)

    if not timeline:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>
  <text x="{WIDTH / 2}" y="{HEIGHT / 2}" fill="{theme['text_faint']}" font-size="12"
        font-family="monospace" text-anchor="middle" dominant-baseline="middle">No timeline data</text>
</svg>'''

    # Sort by year
    sorted_tl = sorted(timeline, key=lambda e: (e["year"], e.get("label", "")))

    # Compute x positions
    usable_width = WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    years = [e["year"] for e in sorted_tl]
    min_year, max_year = min(years), max(years)
    year_span = max(max_year - min_year, 1)

    entries = []
    for entry in sorted_tl:
        t = (entry["year"] - min_year) / year_span
        x = LEFT_MARGIN + t * usable_width
        entries.append({**entry, "x": x})

    # Nudge entries with same year apart slightly
    for i in range(1, len(entries)):
        if abs(entries[i]["x"] - entries[i - 1]["x"]) < 20:
            entries[i]["x"] = entries[i - 1]["x"] + 20

    # Build layers
    defs_str = _build_defs(arm_colors, theme)
    trail_str = _build_comet_trail(usable_width, theme)
    years_str = _build_year_markers(entries, theme)
    nodes_str = _build_nodes_and_labels(entries, usable_width, arm_colors, theme)
    comet_str = _build_comet(usable_width, theme)

    # Title
    title = (
        f'  <text x="30" y="28" fill="{theme["text_faint"]}" font-size="11" '
        f'font-family="monospace" letter-spacing="3">EVOLUTION TRAIL</text>'
    )
    cyan = theme.get("synapse_cyan", "#00d4ff")
    status_dot = (
        f'  <circle cx="185" cy="24" r="3" fill="{cyan}" opacity="0.8">'
        f'<animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>'
        f'</circle>'
    )
    status_text = (
        f'  <text x="{WIDTH - 30}" y="28" fill="{theme["text_faint"]}" font-size="10" '
        f'font-family="monospace" text-anchor="end" opacity="0.5">'
        f'{min_year} — {max_year}</text>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
{defs_str}
  </defs>

  <!-- Background -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Title -->
{title}
{status_dot}
{status_text}

  <!-- Timeline track -->
{trail_str}

  <!-- Year markers -->
{years_str}

  <!-- Nodes and labels -->
{nodes_str}

  <!-- Comet -->
{comet_str}
</svg>'''
