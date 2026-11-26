#!/usr/bin/env python3
"""news-image-20261125: sum up Wednesday 25 November 2026 in one 1024x1024 PNG.

Pure-stdlib Python. Deterministic: fixed data, no clock, no network, no
other-file reads. Writes exactly one image to
os.environ["MAKEFUN_OUTPUT_DIR"] (default "/output") + "/entry.png".

45 stories, all verified against news reported on 25 Nov 2026
(Just Security Early Edition, Reuters, BBC, UEFA, AP, Open Chronicle,
BusinessWorld/Reuters, HTT News, UBStandard). Lead: two oil tankers hit
naval mines and burn in the Strait of Hormuz.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 240, 228)
INK = (24, 24, 24)
NAVY = (13, 40, 68)
NAVY_LT = (32, 70, 112)
RED = (190, 52, 38)
GOLD = (198, 158, 36)
WHITE = (255, 255, 255)
PANEL = (255, 255, 255)
BORDER = (204, 194, 170)
MUTED = (88, 86, 78)
BLUE = (38, 96, 166)
TEAL = (16, 118, 108)
OCEAN = (20, 48, 76)
LAND = (126, 162, 198)
DOT = (218, 58, 38)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 strings of 5 chars; '#' = filled pixel, '.' = empty.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "#.##.", "##..#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".###.", "#....", "#....", "#....", ".###."),
    'd': ("....#", "....#", ".##.#", "#..##", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    'h': ("#....", "#....", "#.##.", "##..#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "#.##.", "##..#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "####.", "#....", "#...."),
    'q': (".....", ".....", ".##.#", "#..##", ".####", "....#", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#..#", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", "#....", "#####"),
    '3': ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", "..#..", "#.#.#", ".###.", "#.#.#", "..#..", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    '~': (".....", ".....", ".###.", "#.#.#", ".#.#.", ".....", "....."),
    '^': ("..#..", ".#.#.", "#...#", ".....", ".....", ".....", "....."),
    '\u2022': (".....", "..#..", ".###.", ".###.", ".###.", "..#..", "....."),
    '\u00d7': (".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."),
    '\u00f8': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
}

# Normalise fancy punctuation to the glyphs we have.
NORM = {
    '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
    '\u2013': '-', '\u2014': '-', '\u00e9': 'e', '\u00f8': 'o',
    '\u00e5': 'a', '\u00fc': 'u', '\u2011': '-',
}


def norm(s):
    return ''.join(NORM.get(c, c) for c in s)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3 * i] = bg[0]
            self.px[3 * i + 1] = bg[1]
            self.px[3 * i + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c, fill=True):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    if fill or dx * dx + dy * dy >= (r - 1) * (r - 1):
                        self.set(cx + dx, cy + dy, c)

    def text(self, x, y, s, scale, c):
        s = norm(s)
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT['?'])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '#':
                        for sy in range(scale):
                            for sx in range(scale):
                                self.set(cx + col * scale + sx,
                                         y + row * scale + sy, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(norm(s)) * 6 * scale

    def text_c(self, cx, y, s, scale, c):
        w = self.text_w(s, scale)
        self.text(cx - w // 2, y, s, scale, c)

    def wrap(self, s, max_chars):
        words = norm(s).split(' ')
        lines = []
        cur = ''
        for wd in words:
            if cur == '':
                cur = wd
            elif len(cur) + 1 + len(wd) <= max_chars:
                cur += ' ' + wd
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, max_chars, lh=None):
        if lh is None:
            lh = 7 * scale + 4
        for line in self.wrap(s, max_chars):
            self.text(x, y, line, scale, c)
            y += lh
        return y


def chunk(ctype, data):
    out = struct.pack('>I', len(data)) + ctype + data
    out += struct.pack('>I', zlib.crc32(ctype + data) & 0xffffffff)
    return out


def write_png(cv, path):
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 6))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- world map
# Stylised continents as ellipses in (lat, lon, rlat, rlon).
LANDS = [
    (50, -100, 22, 30), (66, -140, 8, 18), (15, -88, 6, 8),
    (73, -42, 7, 10), (-12, -60, 22, 12), (4, 20, 24, 17),
    (52, 12, 12, 16), (50, 85, 20, 55), (12, 103, 10, 10),
    (21, 79, 10, 8), (-25, 134, 9, 13), (54, -2, 4, 3),
    (37, 138, 6, 3), (-3, 118, 4, 12), (-19, 47, 6, 2),
    (-42, 173, 5, 2),
]
# Flashpoints: (lat, lon) of the day's stories.
DOTS = [
    (26.5, 56.2),    # Strait of Hormuz
    (24.7, 46.7),    # Riyadh
    (31.5, 34.4),    # Gaza
    (50.4, 30.5),    # Kyiv
    (53.2, 50.1),    # Samara, Russia
    (-9.4, 160.0),   # Honiara, Solomon Islands
    (39.9, 116.4),   # Beijing
    (38.9, -77.0),   # Washington
    (37.5, 127.0),   # Seoul
    (51.5, -0.1),    # London
    (15.6, 32.5),    # Khartoum, Sudan
    (40.7, -74.0),   # New York
]


def is_land(lat, lon):
    for clat, clon, rlat, rlon in LANDS:
        dlat = (lat - clat) / rlat
        dlon = (lon - clon) / rlon
        if dlat * dlat + dlon * dlon <= 1.0:
            return True
    return False


def draw_map(cv, x, y, w, h):
    cv.rect(x, y, w, h, OCEAN)
    cell = 3
    for gy in range(0, h, cell):
        lat = 90.0 - (gy + cell / 2.0) / h * 180.0
        for gx in range(0, w, cell):
            lon = (gx + cell / 2.0) / w * 360.0 - 180.0
            if is_land(lat, lon):
                cv.rect(x + gx, y + gy, cell, cell, LAND)
    for lat, lon in DOTS:
        px = x + int((lon + 180.0) / 360.0 * w)
        py = y + int((90.0 - lat) / 180.0 * h)
        cv.circle(px, py, 4, DOT)
        cv.circle(px, py, 2, WHITE)


# ---------------------------------------------------------------- sections
def draw_header(cv):
    cv.rect(0, 0, W, 96, NAVY)
    cv.rect(0, 96, W, 4, GOLD)
    cv.text(24, 16, "THE WORLD IN ONE DAY", 2, GOLD)
    cv.text(24, 44, "25 NOVEMBER 2026", 4, WHITE)
    cv.text(24, 78, "WEDNESDAY  -  THE DAY'S NEWS, IN ONE PICTURE", 1, (178, 198, 218))
    cv.text(700, 20, "make.fun", 2, (150, 180, 205))
    cv.text(700, 46, "news-image-20261125", 2, (150, 180, 205))
    cv.text(700, 72, "$100 SHARED - TOP 50", 1, GOLD)


def draw_lead(cv):
    # Lead panel: Hormuz story left, world map right.
    cv.rect(16, 108, 992, 116, PANEL)
    cv.rect(16, 108, 4, 116, RED)
    cv.text(36, 120, "LEAD STORY", 2, RED)
    cv.text(36, 146, "TANKERS BURN IN THE", 3, INK)
    cv.text(36, 172, "STRAIT OF HORMUZ", 3, INK)
    cv.para(36, 198, "Iran says two tankers hit naval mines and burned.",
            2, MUTED, 52, 18)
    draw_map(cv, 668, 114, 328, 104)


def draw_panels(cv):
    panels = [
        ("SAUDI / YEMEN", RED,
         "Houthis hit Riyadh tower and refinery",
         "Drone hits a tower in Riyadh's financial district, 11 hurt. "
         "Houthis also say they struck the Ras Tanura refinery."),
        ("WAR IN UKRAINE", RED,
         "Kyiv drones set two refineries ablaze",
         "Two Rosneft refineries in Samara hit overnight; 1 killed. "
         "A Russian strike on Odesa kills 2, wounds 3."),
        ("HUAWEI", BLUE,
         "Huawei convicted on 10 of 12 counts",
         "Jury finds bank fraud, trade-secret theft and sanctions "
         "breaches; acquits on racketeering. Huawei will appeal."),
        ("PACIFIC SHIFT", BLUE,
         "Australia locks in Solomon Islands",
         "New treaty bars any foreign military base on the Solomons; "
         "Canberra becomes its security partner."),
    ]
    y0 = 232
    for i, (tag, tc, head, body) in enumerate(panels):
        col = i % 2
        row = i // 2
        x = 16 + col * 500
        y = y0 + row * 104
        cv.rect(x, y, 492, 98, PANEL)
        cv.rect(x, y, 492, 2, tc)
        cv.text(x + 12, y + 10, tag, 1, tc)
        cv.para(x + 12, y + 24, head, 2, INK, 40, 16)
        cv.para(x + 12, y + 46, body, 2, MUTED, 40, 16)


# 28 brief items. Together with the lead (1), the panels (4), the
# Champions League results (9) and the markets box (3), this poster
# carries 45 verified stories from 25 November 2026.
BRIEF = [
    "Houthis strike Riyadh tower; 11 hurt",
    "Israel kills Hamas security chief",
    "490,334 Russian war dead, BBC finds",
    "Sudan RSF drones kill 19 civilians",
    "Pope Leo decries COP31 collapse",
    "Australia-Solomons sign base pact",
    "Poland seeks permanent US troops",
    "Libya officers die in sea-drone hit",
    "Dell Q3: revenue $54.9bn, AI +291%",
    "Colombia hostages freed in raid",
    "Shenzhou-24 docks; Pakistani aboard",
    "World court: Myanmar genocide ruling",
    "China answers Starlink: Qianfan",
    "BBC journalists strike over cuts",
    "Eurostar hit by union strikes",
    "India buys record Russian oil",
    "UK energy bills to rise 26% in Jan",
    "Fragrance firms fined EUR500m+",
    "FT exposes A7 Kremlin money web",
    "Indonesia factory blaze kills 24",
    "CIA and ODNI hit by cyber breach",
    "Trump readies new tariffs",
    "Mexico drones help catch El Chapo Isidro",
    "China death sentence for 100 leaks",
    "Gaza children's hospital loses power",
    "Militants kill 30+ in Nigeria",
    "Japan aims to be No. 3 AI power",
    "Anthropic, OpenAI staff doubt AI safety",
]


def draw_brief(cv):
    y = 448
    cv.text(16, y, "THE DAY IN BRIEF", 2, NAVY)
    cv.hline(16, y + 20, 992, BORDER, 2)
    y += 30
    for i, item in enumerate(BRIEF):
        col = 0 if i < 14 else 1
        row = i % 14
        x = 16 + col * 500
        yy = y + row * 19
        cv.text(x, yy, "\u2022", 2, RED)
        cv.text(x + 16, yy, item, 2, INK)


TIMELINE = [
    ("03:00", "Tankers hit mines", "in Hormuz"),
    ("04:56", "Shenzhou-24 docks", "at Tiangong"),
    ("16:45", "UCL: Barca win", "4-1 in Baku"),
    ("21:30", "Wall St closes:", "Nasdaq -1.5%"),
]


def draw_timeline(cv):
    y = 744
    cv.text(16, y, "THE DAY IN UTC", 2, NAVY)
    cv.hline(16, y + 20, 992, BORDER, 2)
    ty = y + 52
    cv.hline(60, ty, 904, NAVY, 3)
    for i, (t, l1, l2) in enumerate(TIMELINE):
        cx = 140 + i * 240
        cv.circle(cx, ty, 6, RED)
        cv.circle(cx, ty, 3, WHITE)
        cv.text_c(cx, ty - 30, t, 2, RED)
        cv.text_c(cx, ty + 14, l1, 2, INK)
        cv.text_c(cx, ty + 32, l2, 2, MUTED)


# UEFA Champions League, Matchday 5, Wednesday 25 November 2026.
UCL = [
    "BAR 4-1 SAB", "LIV 3-0 BRU", "PSG 2-2 ROM",
    "SPO 2-2 MUN", "LIL 2-1 BAY", "INT 2-0 STU",
    "ATM 2-0 VIK", "SHA 0-1 FEN", "SLA 0-1 VIL",
]


def draw_bottom(cv):
    y = 852
    # Champions League box (left).
    cv.rect(16, y, 492, 96, PANEL)
    cv.rect(16, y, 492, 2, TEAL)
    cv.text(28, y + 10, "CHAMPIONS LEAGUE - MATCHDAY 5", 1, TEAL)
    for i, r in enumerate(UCL):
        col = i % 3
        row = i // 3
        cv.text(28 + col * 164, y + 32 + row * 20, r, 2, INK)
    # Markets box (right).
    x = 516
    cv.rect(x, y, 492, 96, PANEL)
    cv.rect(x, y, 492, 2, GOLD)
    cv.text(x + 12, y + 10, "MARKETS", 1, (140, 110, 20))
    cv.text(x + 12, y + 30, "S&P 500 -0.5%   Nasdaq -1.5%   Dow +0.9%", 2, INK)
    cv.text(x + 12, y + 52, "Dow closes above 50,000 for first time", 2, INK)
    cv.text(x + 12, y + 74, "KOSPI -6.2%   Nikkei -2.8%   Nvidia -5.9%", 2, INK)


def draw_footer(cv):
    y = 962
    cv.hline(16, y, 992, BORDER, 2)
    cv.para(16, y + 10,
            "Sources: Just Security, Reuters, BBC, UEFA, AP, Open Chronicle, "
            "BusinessWorld, HTT News. Every event happened or was first "
            "reported on Wednesday 25 November 2026.", 2, MUTED, 82, 18)
    cv.text(16, 1008, "DRAWN IN PURE PYTHON - NO PHOTOS, NO NETWORK", 1, MUTED)


def main():
    cv = Canvas(W, H, PAPER)
    draw_header(cv)
    draw_lead(cv)
    draw_panels(cv)
    draw_brief(cv)
    draw_timeline(cv)
    draw_bottom(cv)
    draw_footer(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
