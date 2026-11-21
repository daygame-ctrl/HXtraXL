from features import Setting, tap_color

COLORS = tap_color.SETTINGS[0].values[:10]
SETTINGS = (
    Setting("color", b"Color\nPreset LED", COLORS),
    Setting("this", b"Preset\nThis", (b"None",) + COLORS),
)
