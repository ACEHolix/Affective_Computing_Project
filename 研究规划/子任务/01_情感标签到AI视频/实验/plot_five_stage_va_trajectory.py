from pathlib import Path


WIDTH = 1200
HEIGHT = 640
MARGIN_LEFT = 90
MARGIN_RIGHT = 50
MARGIN_TOP = 80
MARGIN_BOTTOM = 90

STAGE_NAMES = [
    "Stage 1 / Positive Activation",
    "Stage 2 / Positive Softening",
    "Stage 3 / Low-arousal Negative Shift",
    "Stage 4 / Negative Escalation",
    "Stage 5 / Recovery",
]


def interpolate(levels, steps_per_stage=60):
    points = []
    for stage_idx, (y0, y1) in enumerate(zip(levels[:-1], levels[1:])):
        for step in range(steps_per_stage):
            t = step / steps_per_stage
            x = stage_idx + t
            y = y0 + (y1 - y0) * t
            points.append((x, y))
    points.append((len(levels) - 1, levels[-1]))
    return points


def map_x(x):
    usable = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    return MARGIN_LEFT + usable * (x / 5.0)


def map_y(y):
    usable = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
    # y is in [-1, 1.1]
    y_min, y_max = -1.0, 1.1
    ratio = (y - y_min) / (y_max - y_min)
    return HEIGHT - MARGIN_BOTTOM - usable * ratio


def points_to_path(points):
    commands = []
    for idx, (x, y) in enumerate(points):
        sx, sy = map_x(x), map_y(y)
        cmd = "M" if idx == 0 else "L"
        commands.append(f"{cmd} {sx:.2f},{sy:.2f}")
    return " ".join(commands)


def circle(cx, cy, r, fill):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r}" fill="{fill}" />'


def text(x, y, content, size=16, weight="normal", fill="#222", anchor="middle"):
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
        f'font-family="Arial, Helvetica, sans-serif">{content}</text>'
    )


def line(x1, y1, x2, y2, color="#bbb", width=1, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{color}" stroke-width="{width}"{dash_attr} />'
    )


def rect(x, y, w, h, fill, opacity=1.0):
    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'fill="{fill}" opacity="{opacity}" />'
    )


def main():
    valence_levels = [0.0, 0.8, 0.8, -0.7, -0.7, -0.1]
    arousal_levels = [0.2, 0.85, 0.35, 0.3, 0.85, 0.2]

    valence_points = interpolate(valence_levels)
    arousal_points = interpolate(arousal_levels)

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    )
    svg.append(rect(0, 0, WIDTH, HEIGHT, "#fffdf9"))

    plot_left = MARGIN_LEFT
    plot_top = MARGIN_TOP
    plot_width = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    plot_height = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

    for idx in range(5):
        if idx % 2 == 0:
            x0 = map_x(idx)
            x1 = map_x(idx + 1)
            svg.append(rect(x0, plot_top, x1 - x0, plot_height, "#f3ede3", 0.75))

    for y in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        sy = map_y(y)
        svg.append(line(plot_left, sy, plot_left + plot_width, sy, "#d6d6d6", 1))
        svg.append(text(plot_left - 15, sy + 5, f"{y:.1f}", 13, fill="#666", anchor="end"))

    for x in range(6):
        sx = map_x(x)
        svg.append(line(sx, plot_top, sx, plot_top + plot_height, "#d6d6d6", 1))

    neutral_y = map_y(0.0)
    svg.append(line(plot_left, neutral_y, plot_left + plot_width, neutral_y, "#666", 1.5, "6,6"))

    svg.append(
        f'<path d="{points_to_path(valence_points)}" fill="none" stroke="#d1495b" stroke-width="4" />'
    )
    svg.append(
        f'<path d="{points_to_path(arousal_points)}" fill="none" stroke="#2f6690" stroke-width="4" />'
    )

    for idx, y in enumerate(valence_levels):
        svg.append(circle(map_x(idx), map_y(y), 5, "#d1495b"))
    for idx, y in enumerate(arousal_levels):
        svg.append(circle(map_x(idx), map_y(y), 5, "#2f6690"))

    svg.append(text(WIDTH / 2, 36, "Five-Stage Valence-Arousal Trajectory (Schematic)", 26, "bold"))
    svg.append(text(WIDTH / 2, 60, "Based on the revised five-stage design for Subtask 01", 15, fill="#555"))

    for idx, label in enumerate(STAGE_NAMES):
        svg.append(text(map_x(idx + 0.5), 74, label, 13, fill="#333"))

    svg.append(text(WIDTH / 2, HEIGHT - 25, "Trajectory progression", 16))
    svg.append(text(28, HEIGHT / 2, "Normalized level", 16, anchor="middle"))

    legend_x = WIDTH - 250
    legend_y = HEIGHT - 120
    svg.append(rect(legend_x, legend_y, 190, 62, "#ffffff", 0.95))
    svg.append(line(legend_x + 16, legend_y + 20, legend_x + 56, legend_y + 20, "#d1495b", 4))
    svg.append(text(legend_x + 70, legend_y + 25, "Valence", 14, anchor="start"))
    svg.append(line(legend_x + 16, legend_y + 44, legend_x + 56, legend_y + 44, "#2f6690", 4))
    svg.append(text(legend_x + 70, legend_y + 49, "Arousal", 14, anchor="start"))

    note_x = MARGIN_LEFT + 10
    note_y = HEIGHT - 95
    svg.append(rect(note_x, note_y - 25, 360, 56, "#ffffff", 0.96))
    svg.append(text(note_x + 10, note_y - 5, "Stage 3: low-arousal negative transition", 13, anchor="start"))
    svg.append(text(note_x + 10, note_y + 16, "Stage 5: recovery toward neutral, not full reset", 13, anchor="start"))

    svg.append("</svg>")

    out_dir = Path(__file__).resolve().parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "five_stage_va_trajectory.svg"
    out_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
