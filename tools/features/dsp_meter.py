"""DSP meter: each block in the Edit view shows its share of the DSP in per cent, and the top right corner the blocks' total as used/75;
the model browser shows each listed model's share between its icon and name.

Global Settings > DSP Usage Display: Model Browser and Edit Blocks (On, Off) turn the numbers on or off in the model browser and
the Edit view's blocks; Total (Small, Large, Off) the corner's
used/75: Small, the default, draws it in the meter's 3x5 digits at 2x, Large in the title's font, as before these settings,
Off not at all, leaving the corner to the title."""
from features import Setting

FLAG = 'HX_DSP_METER'
TITLE = 'DSP Usage Display'
SETTINGS = (
    Setting('browser', b'Browser\nModel', (b'On', b'Off')),     # On first: 0 is what a unit that set 0xd1 reads here
    Setting('blocks', b'Blocks\nEdit', (b'On', b'Off')),
    Setting('total', b'Total', (b'Small', b'Large', b'Off')),     # Small first: 0 is what a unit that set 0xd1 reads here
)

EDIT_PAINT_LIT, EDIT_PAINT = 0x28d96da0, 0x28dc27f9     # the Edit view top half's paint function (block slots), as registered
BROWSER_PAINT_LIT, BROWSER_PAINT = 0x28d96df0, 0x28dc4dd1   # the model browser's paint function, as registered
NAMES_X = 0x28d90f72                # the browser constructor's movs r3, #44: its name list's x
NAMES_X_STOCK, NAMES_X_LABELLED = bytes([44, 0x23]), bytes([60, 0x23])     # room for the labels browser draws


def apply(p):
    m = p.module('src/m4/dsp_meter.s')
    p.chain_ptr(EDIT_PAINT_LIT, EDIT_PAINT, after=m['dsp_paint'])
    p.chain_ptr(BROWSER_PAINT_LIT, BROWSER_PAINT, after=m['dsp_browser'])
    p.expect(NAMES_X, NAMES_X_STOCK, 'the model browser name list\'s x')
    p.put(NAMES_X, NAMES_X_LABELLED, 'the model browser name list\'s x')
