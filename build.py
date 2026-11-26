#!/usr/bin/env python3
"""Build HXtra 3.80.0 from your own copy of the stock firmware.

usage: python3 build.py HX_Stomp_v3.80.0_0x103966115.hxf [-o out.hxf] [--no-check]
                        [--splash picture [--splash-fit fill|fit]] [--splash-text "text" [--splash-glyph EMOJI=picture ...]]

The input is Line 6's own HX Stomp firmware file, version 3.80.0
(Line 6 Updater keeps a copy; see README.md). Nothing of it is in this
repository: the build reads it, adds NAM A2 Lite and writes a new .hxf
(default build/HX_Stomp_v3.80.0_HXtra.hxf) for Line 6 Updater.
The HX Effects CLI build uses the stock HX Effects 3.80.0 file and adds NAM A2 Lite.
It supports -o, --no-check, and HX_NAM_SLOTS=1, 2 or 3.

NAM A2 Lite runs as up to three blocks at once, each playing its own capture from a User IR slot.
HX_NAM_SLOTS=3, 2, 1 or 0 sets how many (0: no NAM A2 Lite); unset, the most that
leave room in Block 3 for the DSP features that are on (tools/block3.py: HX_GR=1 gives 2). The block's title shows the selected IR's name.
Amp > NAM > NAM A2 Lite, ten knobs: Input, Treble, Output, Polarity, Bass,
Mid, Model, Mid Freq, Q, High Cut. See STEPS.

Steps:
  1. tools/sharc/nam_multi.py: the SHARC kernel (none with HX_NAM_SLOTS=0, which skips steps 2 and 3's kernel too), checked in the simulator
     against src/sharc/nam_a2.asm bit for bit, each block on its own capture
     (--no-check skips it, ~2 min)
  2. tools/patch_amp.py, STEPS: the model (each block with its own
     SDRAM block), its menu entry and the IR name in the block title
  3. tools/patch_amp.py patch: the kernel into the SHARC boot stream
     (first: tools/patch_menu.py, the HXtra features of tools/features; --splash, --splash-fit,
     --splash-text and --splash-glyph are the splash feature's HX_SPLASH, HX_SPLASH_FIT, HX_SPLASH_TEXT and HX_SPLASH_GLYPHS;
     with HX_CLICK=1, then tools/patch_click.py: the Metronome block; with HX_FX_GATE=1, tools/patch_gate.py: the gate in
     the FX Loop and Return blocks; with HX_GATE_SC=1, tools/patch_sidechain.py: the Noise Gate's Input Sidechain;
     with HX_GR=1, last, tools/patch_comp.py: the GR meter's compressor knobs and DSP code)
  4. tools/l6ia_verify.py: every checksum of the result
  5. tools/hxf.py pack: the .hxf
"""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

STOCK_MD5 = {
    "a2cd8f4ae56f49415380270ebc484bf1": "HX_Stomp",       # HX_Stomp_v3.80.0_0x103966115.hxf
}
# The browser uses the Stomp tables above. HX Effects is CLI-only.
HX_EFFECTS_STOCK_MD5 = "7c2ebdf1bffb6bcc5f89dda97f91e40c"
# The kernel and the patch_amp.py steps (tests/test_web_build.py keeps web/firmware-worker.js's copies
# equal). Each step reads the previous one's output: patch_amp.py CMD IN OUT ARGS...
#
# NAM A2 Lite with ten knobs and a tone stack in Amp > NAM, on Xenomorph Fuzz Mono's preset ID 555 (that
# stock model is removed), the knobs type for type on its own so HX Edit keeps NAM blocks and their
# values, in live order: Input, Treble, Output | Polarity, Bass, Mid | Model, Mid Freq, Q | High Cut.
# Tone stack (the kernel's --mid-sweep): Bass a 150 Hz shelf, Mid a peak at Mid Freq (150..3000 Hz)
# with Q 0.7/1.4/2.8, Treble a 2.5 kHz peak, High Cut a low-pass (10.0 off); +-12 dB, flat at 5.0.
# Presets saved with an earlier NAM build (IDs 147/148, or 461) don't open as NAM in this one.
KERNEL = {"HX_Stomp": ["tools/sharc/nam_multi.py", "--mid-sweep"]}
NAM_EQ = [
    ["remove-model", "--preset-id", "555"],
    ["add-fx-model", "--knobs", "eq", "--name", "HD2_DistNAMLite", "--display-name", "NAM A2 Lite",
     "--category", "distortion", "--folder", "NAM", "--preset-id", "555", "--dsp-cost", "2275",
     "--sdram-words", "0x5000", "--dm-words", "0x303", "--pm-words", "0x147"],
    ["move-folder", "--name", "NAM", "--from", "2", "--to", "12"],
    ["ir-title", "--fx-preset-id", "555", "--knob", "6"],
]
# model-int: NAM's Model as a whole number.
STEPS = {"HX_Stomp": NAM_EQ + [["model-int"]]}
# The largest Entry 3 an HX Stomp is known to load amps from; at 0xf3888 it drops every amp and preamp [verified on unit]
E3_MAX = 0xf10f0
HERE = os.path.dirname(os.path.abspath(__file__))


def kernel(unit, slots=3):
    """KERNEL[unit] for `slots` NAM slots (1..3)."""
    return KERNEL[unit] + ([] if slots == 3 else ["--slots", str(slots)])


def run(*args):
    print("$ " + " ".join(args[1:] if args[0] == sys.executable else args), flush=True)
    r = subprocess.run(list(args), cwd=HERE, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode:
        sys.stderr.write(r.stderr)
        sys.exit(f"build.py: step failed ({args[1]})")
    return r.stdout


def build_effects(stock, argv):
    parser = argparse.ArgumentParser(prog="build.py " + os.path.basename(stock),
                                     description="Build NAM A2 Lite for HX Effects 3.80.0.")
    parser.add_argument("-o", type=Path)
    parser.add_argument("--no-check", action="store_true")
    args = parser.parse_args(argv)
    out = args.o.resolve() if args.o else Path(HERE) / "build/HX_Effects_v3.80.0_HXtra.hxf"
    if out == Path(stock).resolve() or (out.exists() and os.path.samefile(out, stock)):
        parser.error("the output must be a separate file from the stock firmware")
    slots = os.environ.get("HX_NAM_SLOTS", "3")
    if slots not in {"1", "2", "3"}:
        parser.error("HX_NAM_SLOTS must be 1, 2 or 3 for HX Effects")

    sys.path.insert(0, os.path.join(HERE, "tools"))
    from l6ia import parse

    print(f"stock firmware: HX Effects 3.80.0\nNAM slots: {slots}")
    py = sys.executable
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        original, model, image = (work / f"{name}.l6ia" for name in ("stock", "model", "image"))
        asm = work / "nam.asm"
        run(py, "tools/sharc/nam_multi.py", "--mid-sweep", "--effects", "--slots", slots,
            "-o", str(asm), *([] if args.no_check else ["--check"]))
        run(py, "tools/hxf.py", "unpack", stock, str(original))
        run(py, "tools/patch_amp.py", "effects-eq", str(original), str(model))
        run(py, "tools/patch_amp.py", "patch", str(model), str(image), "--asm", str(asm))
        if "ALL OK" not in run(py, "tools/l6ia_verify.py", str(image)):
            sys.exit("build.py: the image failed its check")

        def payloads(data):
            return [data[e["payload_off"]:e["payload_off"] + e["payload_len"]] for e in parse(data)]

        before, after = payloads(original.read_bytes()), payloads(image.read_bytes())
        if len(before) != 14 or len(after) != 14:
            sys.exit("build.py: unexpected HX Effects entry count")
        # Payload start sector and exclusive end for the fixed 3.80.0 data partitions.
        partitions = {2: (0x8803, 0x8C03), 3: (0x8C04, 0x9406), 4: (0x9407, 0x11005)}
        for entry, (start, end) in partitions.items():
            if len(after[entry]) > (end - start) * 512:
                sys.exit(f"build.py: HX Effects entry {entry} exceeds its eMMC partition")
        if any(old != new for entry, (old, new) in enumerate(zip(before, after))
               if entry != 0 and entry not in partitions):
            sys.exit("build.py: unexpected HX Effects payload change")
        if args.o is None:
            out.parent.mkdir(exist_ok=True)
        run(py, "tools/hxf.py", "pack", str(image), str(out), "--donor", stock)
    print(f"\nDone: {out}")


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("-"):
        sys.exit(__doc__)
    stock = os.path.abspath(argv[0])
    md5 = hashlib.md5(open(stock, "rb").read()).hexdigest()
    if md5 == HX_EFFECTS_STOCK_MD5:
        return build_effects(stock, argv[1:])
    if md5 not in STOCK_MD5:
        sys.exit(f"{stock}: MD5 {md5}, not the stock HX Stomp or HX Effects 3.80.0 firmware.")
    unit = STOCK_MD5[md5]
    print(f"stock firmware: {unit.replace('_', ' ')} 3.80.0")
    splash = os.path.abspath(argv[argv.index("--splash") + 1]) if "--splash" in argv else None
    splash_text = argv[argv.index("--splash-text") + 1] if "--splash-text" in argv else None
    splash_fit = argv[argv.index("--splash-fit") + 1] if "--splash-fit" in argv else "fill"
    if splash:
        os.environ.update(HX_SPLASH=splash, HX_SPLASH_FIT=splash_fit)
    if splash_text:
        os.environ["HX_SPLASH_TEXT"] = splash_text
    glyphs = [argv[i + 1].split("=", 1) for i, a in enumerate(argv) if a == "--splash-glyph"]
    if any(len(g) != 2 for g in glyphs):
        sys.exit("build.py: --splash-glyph takes EMOJI=picture")
    if glyphs:
        os.environ["HX_SPLASH_GLYPHS"] = ",".join(f"{e}={os.path.abspath(path)}" for e, path in glyphs)
    out = os.path.abspath(argv[argv.index("-o") + 1]) if "-o" in argv else \
        os.path.join(HERE, "build", f"{unit}_v3.80.0_HXtra.hxf")
    build = os.path.join(HERE, "build")
    os.makedirs(build, exist_ok=True)
    asm = os.path.join(build, "nam_lite.asm")
    image = os.path.join(build, "nam_lite.l6ia")
    titled = os.path.join(build, "nam_lite_title.l6ia")
    py = sys.executable

    sys.path.insert(0, os.path.join(HERE, "tools"))
    import block3
    slots = block3.slots()
    print(f"NAM slots: {slots}")
    if slots:
        run(py, *kernel(unit, slots), "-o", asm, *([] if "--no-check" in argv else ["--check"]))
    src = stock
    for k, step in enumerate(STEPS[unit] if slots else []):
        dst = os.path.join(build, f"nam_lite_{k}.l6ia")
        run(py, "tools/patch_amp.py", step[0], src, dst, *step[1:])
        if src != stock:
            os.remove(src)
        src = dst
    base = src
    run(py, "tools/patch_menu.py", base, titled, "--cwd", os.getcwd())
    if base == stock:
        base = os.path.join(build, "nam_lite_menu.l6ia")
    os.replace(titled, base)
    if slots:
        run(py, "tools/patch_amp.py", "patch", base, image, "--asm", asm)
    else:
        os.replace(base, image)
    if os.environ.get("HX_CLICK"):
        run(py, "tools/patch_click.py", image, titled)
        os.replace(titled, image)
    if os.environ.get("HX_FX_GATE"):
        run(py, "tools/patch_gate.py", image, titled)
        os.replace(titled, image)
    if os.environ.get("HX_GATE_SC"):
        run(py, "tools/patch_sidechain.py", image, titled)
        os.replace(titled, image)
    if os.environ.get("HX_USB_MONITOR"):
        run(py, "tools/patch_usbmon.py", image, titled)
        os.replace(titled, image)
    if os.environ.get("HX_GR"):
        # last: every step that adds a model rebuilds the Entry 3 and 4 tails the knobs live in
        run(py, "tools/patch_comp.py", image, titled)
        os.replace(titled, image)
    report = run(py, "tools/l6ia_verify.py", image, "--e3-max", hex(E3_MAX))
    if "ALL OK" not in report:
        sys.exit("build.py: the image failed its check")
    run(py, "tools/hxf.py", "pack", image, out, "--donor", stock)
    if slots:
        os.remove(base)
    print(f"\nDone: {out}\nInstall it with Line 6 Updater (Choose File); see README.md first.")


if __name__ == "__main__":
    main()
