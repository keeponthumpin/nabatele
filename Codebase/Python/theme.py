"""
theme — NABATELE UI design tokens (standalone API).

Pure-Python single source of truth for the prototype's visual language.
No TouchDesigner imports, so it's importable anywhere (TD extensions,
unit tests, tooling) and trivially testable.

Colours are `Color` instances (normalized rgba floats, 0..1), keyed by
semantic role in `COLORS`. Typography, metrics, radii and icon glyphs
follow the §7c spec as plain dicts.

    from theme import COLORS, TYPE, METRICS, col
    COLORS['topbar_bg'].r        # 0.0706
    col('cyan').rgba             # (0.2118, 0.7725, 0.8392, 1.0)
    col('amber').rgb             # (0.902, 0.6353, 0.2353)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    """A normalized RGBA colour. Channels are floats in 0..1."""
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0

    @property
    def rgb(self):
        """(r, g, b) tuple — for TD colour-par triples."""
        return (self.r, self.g, self.b)

    @property
    def rgba(self):
        """(r, g, b, a) tuple."""
        return (self.r, self.g, self.b, self.a)

    @property
    def hex(self):
        """'#rrggbb' string (alpha dropped)."""
        return '#%02x%02x%02x' % (
            round(self.r * 255), round(self.g * 255), round(self.b * 255))

    def with_alpha(self, a):
        """Return a copy at a new alpha, e.g. col('home').with_alpha(0.5)."""
        return Color(self.r, self.g, self.b, float(a))

    @classmethod
    def from_hex(cls, hexv, a=1.0):
        """Build from '#rrggbb' (or short '#rgb')."""
        h = hexv.lstrip('#')
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        return cls(int(h[0:2], 16) / 255.0,
                   int(h[2:4], 16) / 255.0,
                   int(h[4:6], 16) / 255.0,
                   float(a))


def _hx(hexv, a=1.0):
    return Color.from_hex(hexv, a)


# ---------------------------------------------------------------------- #
#  COLOURS — semantic role -> Color(rgba)                                #
# ---------------------------------------------------------------------- #
COLORS = {
    # ---- structural / surfaces -------------------------------------
    'bg':                 _hx('#0b0e11'),  # app background
    'topbar_bg':          _hx('#12171c'),  # top bar / rails / table head / footers
    'panel_bg':           _hx('#12171c'),  # alias of topbar_bg (panel surface)
    'panel_alt_bg':       _hx('#161c22'),  # hover fills, sub-panels, meter ticks
    'line':               _hx('#222c34'),  # standard borders / dividers
    'line_bright':        _hx('#33424d'),  # emphasised borders, range track, ticks

    # ---- ink -------------------------------------------------------
    'ink':                _hx('#d6dde2'),  # primary text
    'ink_dim':            _hx('#7c8893'),  # secondary / label text
    'ink_faint':          _hx('#4a555e'),  # tertiary, captions, disabled

    # ---- accents ---------------------------------------------------
    'cyan':               _hx('#36c5d6'),  # primary accent
    'amber':              _hx('#e6a23c'),  # mains / pontoon, dirty edits, warnings
    'green':              _hx('#3fb56a'),  # live status, bound state
    'red':                _hx('#d6504a'),  # fault state (reserved)
    'home':               _hx('#e6532e'),  # Take Me Home border / text

    # ---- cube faces (preview) --------------------------------------
    'cube_top_fill':      _hx('#243743'),
    'cube_top_stroke':    _hx('#36c5d6'),
    'cube_left_fill':     _hx('#192831'),
    'cube_left_stroke':   _hx('#2c5160'),
    'cube_right_fill':    _hx('#10202a'),
    'cube_right_stroke':  _hx('#244451'),

    # ---- winch nodes ----------------------------------------------
    'winch_fill':         _hx('#1b242b'),
    'winch_hover_fill':   _hx('#1f2c33'),
    'winch_sel_side':     _hx('#22343c'),
    'winch_sel_main':     _hx('#332a1c'),
    'cable_rest':         _hx('#2a3942'),
    'main_label':         _hx('#b9924a'),

    # ---- home button ----------------------------------------------
    'home_grad_top':      _hx('#241310'),
    'home_grad_bot':      _hx('#1a0e0b'),
    'home_hover_top':     _hx('#3a1a12'),
    'home_hover_bot':     _hx('#23100b'),
    'home_title':         _hx('#f0795a'),
    'home_sub':           _hx('#9a5a45'),

    # ---- inputs / pills -------------------------------------------
    'input_bg':           _hx('#0d1216'),
    'pill_side_bg':       _hx('#0c1c22'),
    'pill_side_border':   _hx('#244451'),
    'pill_main_bg':       _hx('#1c150b'),
    'pill_main_border':   _hx('#4a3a22'),
    'submode_on_ink':     _hx('#06222a'),

    # ---- drum meter gradient --------------------------------------
    'meter_fill_a':       _hx('#2a6f80'),
    'meter_fill_b':       _hx('#36c5d6'),
}

# ---------------------------------------------------------------------- #
#  TYPOGRAPHY                                                             #
# ---------------------------------------------------------------------- #
# NB: `mono` path is resolved lazily by the extension (needs project.folder).
FONTS = {
    'mono': 'Resources/Fonts/mono.ttf',   # relative to project.folder
    'sans': 'Inter, system-ui, -apple-system, Segoe UI, sans-serif',
}

TYPE = {
    'mode_num':      26,
    'insp_empty':    24,
    'insp_title':    20,
    'wind_speed':    19,
    'readout':       16,
    'base':          15,   # brand / mode H3 / nav-spacing base
    'body':          14,
    'table_cell':    13,
    'mode_body':     12.5,
    'channel':       12,
    'control':       11,   # nav, buttons, foot
    'home_note':     10.5,
    'eyebrow':       10,
    'cap':           9.5,
    'legend':        9,
    'rose_cardinal': 8,
}

TRACKING = {
    'brand':   0.22,
    'eyebrow': 0.16,
    'body':    0.0,
}

# ---------------------------------------------------------------------- #
#  METRICS — panel sizing & spacing (px)                                 #
# ---------------------------------------------------------------------- #
METRICS = {
    'topbar_h':       54,
    'footer_h':       26,
    'brand_min_w':    230,
    'inspector_w':    300,
    'grid_cell':      44,
    'wind_rose':      96,
    'scale_bar':      88,
    'home_rail_w':    360,
    'home_btn_pad_y': 30,
    'toggle_w':       38,
    'toggle_h':       20,
    'toggle_knob':    16,
    'id_input_w':     84,
    'ip_input_w':     150,
    'meter_h':        10,
    'range_track':    3,
    'range_thumb':    14,
    'numbox_w':       78,
    'scroll_w':       10,
}

RADII = {
    'input':   2,
    'readout': 3,
    'card':    4,
    'home':    5,
    'scroll':  5,
}

# ---------------------------------------------------------------------- #
#  ICONS — Unicode glyphs, no icon-font dependency                       #
# ---------------------------------------------------------------------- #
ICONS = {
    'tick':       '\u25B8',  # |>
    'home':       '\u2302',  # house
    'insp_empty': '\u22B9',  # hermitian
    'bind_dot':   '\u25CF',  # filled circle
    'minus':      '\u2212',  # true minus
    'times':      '\u00D7',  # multiply
}


# ---------------------------------------------------------------------- #
#  ACCESSORS                                                              #
# ---------------------------------------------------------------------- #
def col(name):
    """Color instance by role, with a helpful error on a bad key."""
    try:
        return COLORS[name]
    except KeyError:
        raise KeyError(
            "Unknown colour '%s'. Valid: %s"
            % (name, ', '.join(sorted(COLORS))))


def palette_rows():
    """Palette as rows: [name, hex, r, g, b, a]. Header-less, rounded."""
    return [[name, c.hex,
             round(c.r, 4), round(c.g, 4), round(c.b, 4), round(c.a, 4)]
            for name, c in COLORS.items()]