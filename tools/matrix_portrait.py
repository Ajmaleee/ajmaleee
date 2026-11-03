"""Generate the animated Matrix-rain portrait used by the profile README.

Pipeline: luminance mapping -> seeded glyph field -> looping rain streams ->
phosphor composite -> fixed-palette GIF.
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "assets" / "source" / "portrait.png"
DEFAULT_OUTPUT = ROOT / "assets" / "matrix-portrait.gif"

W = H = 560
CX = CY = 280
R = 236
RING = 246
CROP = (120, 148, 320, 348)
N_FRAMES = 56
DELAY_MS = 70
CELL_W = 6
CELL_H = 10
COLS = W // CELL_W + 1
ROWS = math.ceil(H / CELL_H)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msgothic.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

RAIN_CHARS = (
    "0123456789ABCDEF"
    "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "+*=<>/\\|[]{}()$#%&@"
)

RAMP = [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]

GREEN_STOPS = [
    (0.00, (3, 6, 4)),
    (0.08, (4, 24, 11)),
    (0.20, (6, 50, 22)),
    (0.34, (9, 92, 39)),
    (0.50, (16, 148, 64)),
    (0.64, (32, 205, 96)),
    (0.78, (78, 238, 128)),
    (0.90, (158, 253, 182)),
    (1.00, (235, 255, 240)),
]


def load_font() -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, 10)
    raise FileNotFoundError("No monospaced CJK-capable font found")


def build_palette() -> Image.Image:
    colors: list[tuple[int, int, int]] = []
    for i in range(64):
        t = i / 63
        colors.append(green(t))
    for value in range(0, 18):
        colors.append((value // 3, value, value // 2))
    while len(colors) < 255:
        colors.append((0, 0, 0))
    colors = colors[:255] + [(1, 2, 1)]
    pal = Image.new("P", (1, 1))
    flat: list[int] = []
    for r, g, b in colors[:256]:
        flat.extend((r, g, b))
    pal.putpalette(flat)
    return pal


def green(t: float) -> tuple[int, int, int]:
    t = min(1.0, max(0.0, t))
    for i in range(len(GREEN_STOPS) - 1):
        a, ca = GREEN_STOPS[i]
        b, cb = GREEN_STOPS[i + 1]
        if a <= t <= b:
            k = (t - a) / (b - a)
            return tuple(int(round(ca[j] + (cb[j] - ca[j]) * k)) for j in range(3))
    return GREEN_STOPS[-1][1]


def load_portrait() -> Image.Image:
    src = Image.open(DEFAULT_SOURCE).convert("RGBA").crop(CROP)
    src = src.resize((R * 2, R * 2), Image.LANCZOS)
    return src


def portrait_fields(portrait: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(portrait, dtype=np.float32)
    alpha = arr[:, :, 3] / 255.0
    lum = (0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]) / 255.0
    lum = np.clip((lum - 0.030) / (0.78 - 0.030), 0.0, 1.0) ** 1.05
    soft_alpha = np.clip((alpha - 0.10) / 0.75, 0.0, 1.0)
    intensity = lum * soft_alpha

    gray = (intensity * 255).astype(np.uint8)
    sharp = Image.fromarray(gray, "L").filter(
        ImageFilter.UnsharpMask(radius=1.5, percent=165, threshold=2)
    )
    intensity = np.asarray(sharp, dtype=np.float32) / 255.0

    focus_y = np.linspace(0.0, 1.0, 2 * R)[:, None]
    focus = 0.62 + 0.38 * np.exp(-(((focus_y - 0.40) / 0.30) ** 2))
    intensity = np.clip(intensity * focus, 0.0, 1.0)

    iy, ix = np.mgrid[0 : 2 * R, 0 : 2 * R]
    falloff = np.clip((R - np.sqrt((ix - R + 0.5) ** 2 + (iy - R + 0.5) ** 2)) / 9.0, 0.0, 1.0)
    intensity = intensity * falloff
    return intensity, soft_alpha * falloff


class Cell:
    __slots__ = ("x", "y", "inside", "intensity", "alpha", "base_char", "jitter")

    def __init__(self, x, y, inside, intensity, alpha, base_char, jitter):
        self.x = x
        self.y = y
        self.inside = inside
        self.intensity = intensity
        self.alpha = alpha
        self.base_char = base_char
        self.jitter = jitter


def build_cells(portrait: Image.Image, font: ImageFont.FreeTypeFont) -> list[Cell]:
    intensity, soft_alpha = portrait_fields(portrait)
    rng = random.Random(0xA17A1EEE)
    cells: list[Cell] = []
    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_W + CELL_W / 2
            y = row * CELL_H + CELL_H / 2
            if x >= W or y >= H:
                continue
            inside = (x - CX) ** 2 + (y - CY) ** 2 <= (R - 2) ** 2
            px = int(round(x - CX + R - CELL_W / 2))
            py = int(round(y - CY + R - CELL_H / 2))
            px = min(max(px, 0), 2 * R - 3)
            py = min(max(py, 0), 2 * R - 3)
            block = intensity[py : py + 3, px : px + 3]
            ablock = soft_alpha[py : py + 3, px : px + 3]
            value = float(block.mean()) * rng.uniform(0.94, 1.06)
            alpha = float(ablock.mean())
            band = 0 if value < 0.05 else min(len(RAMP) - 1, int(value * len(RAMP)))
            char = RAMP[band]
            cells.append(Cell(x, y, inside, value, alpha, char, rng.random()))
    return cells


def build_background() -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2) / R
    radial = np.clip(1.0 - dist, 0.0, 1.0) ** 2.2
    base = np.zeros((H, W, 3), dtype=np.float32)
    base[:, :, 0] = 2.0 + radial * 3.0
    base[:, :, 1] = 5.0 + radial * 9.0
    base[:, :, 2] = 3.0 + radial * 5.0

    for y in range(0, H, 3):
        base[y, :, :] *= 0.86
    for x in range(0, W, 28):
        base[:, x, 1] += 1.6
    for y in range(0, H, 28):
        base[y, :, 1] += 1.6

    vig = np.clip(1.0 - (dist * 0.55) ** 2, 0.55, 1.0)
    base *= vig[:, :, None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")


def draw_frame(
    frame: int,
    cells: list[Cell],
    stream_map: dict[int, list[tuple[int, int, int]]],
    font: ImageFont.FreeTypeFont,
    background: Image.Image,
    poster: bool = False,
) -> Image.Image:
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(layer)
    f = 0 if poster else frame
    rng = random.Random(0xBADC0DE)

    rain_bright: dict[tuple[int, int], tuple[float, str]] = {}
    for col, streams in stream_map.items():
        for start, speed, tail in streams:
            head = (start + speed * f) % N_FRAMES
            for d in range(tail):
                row = head - d
                if row < 0 or row >= ROWS:
                    continue
                fall = (1.0 - d / tail) ** 1.55
                if d == 0:
                    fall = 1.0
                char_rng = random.Random((col * 73856093) ^ (row * 19349663) ^ ((f // 3) * 83492791))
                char = char_rng.choice(RAIN_CHARS)
                key = (col, row)
                prev = rain_bright.get(key)
                if prev is None or fall > prev[0]:
                    rain_bright[key] = (fall, char)

    for cell in cells:
        col = int(cell.x // CELL_W)
        row = int(cell.y // CELL_H)
        is_rain = (col, row) in rain_bright
        if not cell.inside:
            if is_rain:
                fall, char = rain_bright[(col, row)]
                if fall < 0.72 and ((col + row) % 3):
                    continue
                b = 0.16 + 0.24 * fall
                color = green(b * 0.55)
                draw.text((cell.x - CELL_W / 2 + 1, cell.y - CELL_H / 2 - 1), char, font=font, fill=color)
            continue

        base = 0.11 + 0.69 * cell.intensity
        brightness = base
        char = cell.base_char
        if is_rain:
            fall, rchar = rain_bright[(col, row)]
            modulated = fall * (0.32 + 0.68 * min(1.0, cell.intensity * 1.35))
            if modulated > base * 0.35:
                char = rchar
                brightness = max(base * 0.95, modulated * 1.05)
            if fall > 0.96:
                brightness = min(1.0, brightness + 0.12)
        if brightness < 0.06:
            continue
        color = green(min(1.0, brightness ** 0.86))
        draw.text((cell.x - CELL_W / 2 + 1, cell.y - CELL_H / 2 - 1), char, font=font, fill=color)

    glow = layer.filter(ImageFilter.GaussianBlur(2.2))
    glow = glow.point(lambda v: int(v * 0.30))
    composed = ImageChops.add(background, glow)
    composed = ImageChops.add(composed, layer)

    ring = Image.new("RGB", (W, H), (0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((CX - RING, CY - RING, CX + RING, CY + RING), outline=green(0.52), width=1)
    rd.ellipse((CX - R - 5, CY - R - 5, CX + R + 5, CY + R + 5), outline=green(0.28), width=1)
    for i in range(96):
        ang = i / 96 * math.tau
        inner = RING + 3
        outer = RING + (7 if i % 8 == 0 else 4)
        c = green(0.40 if i % 8 else 0.68)
        rd.line(
            (
                CX + math.cos(ang) * inner,
                CY + math.sin(ang) * inner,
                CX + math.cos(ang) * outer,
                CY + math.sin(ang) * outer,
            ),
            fill=c,
            width=1,
        )

    if not poster:
        start_ang = (f / N_FRAMES) * 360
        for i in range(26):
            a0 = start_ang - i * 1.9
            frac = 1.0 - i / 26
            rd.arc(
                (CX - RING - 3, CY - RING - 3, CX + RING + 3, CY + RING + 3),
                a0 - 2.0,
                a0,
                fill=green(0.22 + 0.55 * frac),
                width=2,
            )
    composed = ImageChops.add(composed, ring)

    corners = Image.new("RGB", (W, H), (0, 0, 0))
    cd = ImageDraw.Draw(corners)
    margin = 18
    length = 20
    cc = green(0.28)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        x = margin if sx > 0 else W - margin
        y = margin if sy > 0 else H - margin
        cd.line((x, y, x + sx * length, y), fill=cc, width=1)
        cd.line((x, y, x, y + sy * length), fill=cc, width=1)
    composed = ImageChops.add(composed, corners)

    arr = np.asarray(composed, dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2) / R
    vig = np.clip(1.08 - (dist * 0.48) ** 2, 0.66, 1.0)
    arr *= vig[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="write a poster PNG only")
    args = parser.parse_args()

    font = load_font()
    portrait = load_portrait()
    cells = build_cells(portrait, font)
    background = build_background()

    rng = random.Random(1337)
    stream_map: dict[int, list[tuple[int, int, int]]] = {}
    for col in range(COLS):
        streams = []
        count = 1 if rng.random() < 0.55 else 2
        for _ in range(count):
            streams.append((rng.randrange(N_FRAMES), rng.choice((1, 2, 2, 3)), rng.randint(9, 17)))
        stream_map[col] = streams

    if args.preview:
        poster = draw_frame(0, cells, stream_map, font, background, poster=True)
        out = DEFAULT_OUTPUT.with_name("matrix-portrait-poster.png")
        poster.save(out, optimize=True)
        print(f"wrote {out}")
        return

    palette = build_palette()
    frames: list[Image.Image] = []
    previous: np.ndarray | None = None
    for f in range(N_FRAMES):
        img = draw_frame(f, cells, stream_map, font, background)
        rgb = np.asarray(img)
        qimg = img.quantize(palette=palette, dither=Image.Dither.NONE)
        q = np.asarray(qimg).copy()
        if previous is not None:
            changed = np.any(rgb != previous, axis=2)
            q[~changed] = 255
        out = Image.fromarray(q, "P")
        out.putpalette(qimg.getpalette())
        frames.append(out)
        previous = rgb
        if f % 10 == 0:
            print(f"frame {f + 1}/{N_FRAMES}")

    poster = draw_frame(0, cells, stream_map, font, background, poster=True)
    poster.save(DEFAULT_OUTPUT.with_name("matrix-portrait-poster.png"), optimize=True)

    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        DEFAULT_OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=DELAY_MS,
        loop=0,
        optimize=True,
        disposal=1,
        transparency=255,
    )
    size = DEFAULT_OUTPUT.stat().st_size
    print(f"wrote {DEFAULT_OUTPUT} ({size / 1024:.0f} KiB, {N_FRAMES} frames)")


if __name__ == "__main__":
    main()
