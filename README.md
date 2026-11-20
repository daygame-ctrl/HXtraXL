# HXtraXL 1.0

Independently maintained custom firmware for the **Line 6 HX Stomp XL**, based on stock firmware **3.80.0**.

## Features

- Six snapshots per preset and two-slot NAM A2 Lite.
- Compressor gain reduction and DSP usage displays.
- FX Loop and Return noise gates, clean-input sidechain, and USB/Send routing.
- Tap tempo display, tuner controls, metronome, virtual footswitches, and preset LED colors.
- Original Line 6 model names. The beat dot and breathing animation default to Off.

## Setup

[Open the HXtraXL 1.0 setup page](https://daygame-ctrl.github.io/HXtraXL/HXtraXL-setup.html). It accepts only the original HX Stomp XL 3.80.0 firmware file and builds locally in your browser.

The XL source and Windows build guide are being prepared for this repository.

## Owner’s guide

### Finding the controls

Press **⌂ VIEW** to switch between **Play view** (footswitch labels) and **Edit view** (signal chain and block parameters). In Edit, turn the **Upper Knob** to select a block, press it to enable or bypass the block, and press **PAGE ▶** for more parameters. Press both PAGE buttons for the menu. Most custom settings are under **Global Settings → Displays**, **Footswitches**, or **Ins/Outs**. Teal labels identify supported custom controls. Press a parameter knob to reset its value.

### Six snapshots

In Snapshot mode, select **1** or **2**, then press its lit switch again to enter the extra bank. The first two positions now show **5** and **6**. Press the lit extra snapshot switch again to return to its native counterpart, or select **3** or **4** to return to the native bank. Set bypass states and snapshot-controlled parameters as usual, then **save the preset**.

| Incoming MIDI | Action |
|---|---|
| CC69, values **0–5** | Select snapshots **1–6** directly |
| CC69, value **8** | Next snapshot |
| CC69, value **9** | Previous snapshot |

Next and Previous wrap across six once the extra bank exists. **SnpshtUp** and **SnpshtDn** offer the same stepping as virtual footswitch functions.

HX Edit’s **.hlx** files preserve snapshots **1–4**. Exporting leaves snapshots 5 and 6 on the pedal, but re-importing the .hlx cannot recover them. The raw USB preset round trip preserved all six in testing. Full **.hxb** backup behavior on the XL is unverified. If direct **5 → 1** or **6 → 2** fails in HX Edit, select **3** first.

### NAM A2 Lite

1. Convert a supported .nam capture with the [NAM A2 Lite converter](https://nocaseguy.github.io/hx-stomp-nam-lite/web/).
2. Import the resulting .wav into a **User IR** slot in HX Edit. This file carries the model data.
3. On the XL, add **Amp → NAM → NAM A2 Lite**, then set **Model** to the slot you imported.
4. Add a cab or regular IR after the NAM block if the capture and monitoring setup call for it.

The build supports **two NAM blocks per preset**. HX Edit may show the stock **Xenomorph Fuzz** name because NAM reuses that model ID. Select and configure NAM on the pedal.

### Displays and tuner

| Control | What it does |
|---|---|
| **BPM Size** | Sets tempo text size. **Off** hides the number. |
| **BPM Color** | Sets the text and dot color. **Tempo** follows the TAP color. |
| **Beat Dot** | Positions the beat indicator beside the preset number. Defaults to **Off**. |
| **Line Color** | Selects the display divider’s color or gradient. |
| **Line Motion** | Selects the animation. **Off**, the default, restores the stock divider. |
| **Line Speed** | Adjusts speed. **Tempo** syncs the animation to BPM. |
| **Tap LED Color** | Colors the TAP ring and label. Includes **Rainbow** and **Random**. Use **Tap Tempo LED** to turn off the ring blink. |
| **Preset LED Color** | Sets the default selected preset ring and icon color in Preset footswitch mode. |
| **This Preset** | Assigns the current preset its own color. Save the preset to keep it. **None** uses the default color. |
| **Model Browser**, **Edit Blocks**, **Total** | Control DSP usage displays. **Total** offers **Small**, **Large**, and **Off**. |

Previously saved settings retain their values. Press the **Beat Dot** or **Line Motion** parameter knob to reset it to **Off**. The BPM number can stay visible with the dot off.

On the tuner’s third page, **Tuner Button → Hold** preserves short-press tap tempo. **Press** opens the tuner immediately. **Tuner Lock** protects the other tuner settings from changes.

### Compressor gain reduction

The meter supports **Deluxe Comp, LA Studio Comp, Kinky Comp, Ampeg Opto Comp, Rochester Comp, and Red Squeeze**. Enable the compressor and set **Mtr Size** to **S**, **M**, **L**, or **XL**. Choose **Middle**, **Top**, **Left**, **Bottom**, or **Right** with **Mtr Pos**. **Mtr Dir** reverses the fill direction.

The colored segments show gain reduction in Play view and in Edit when that compressor is selected. The meter has no idle outline. **Middle** occupies the divider area. For a quick check, use **Rochester Comp**, **Mtr Size = XL**, and **Mtr Pos = Bottom**, then lower the threshold and play several chords.

### Footswitches and Command Center

Under **Global Settings → Footswitches**, set an **FS Hold** action for a Stomp switch. Hold actions default to **Off**. Options include the tuner, virtual switches, and supported physical switch targets.

**VFS1–VFS5** use **MIDI CC20–24**. Use **Bypass Assign** to assign a block or **Controller Assign** for a parameter. Their **Function** settings include **Stomp**, **Tuner**, snapshot stepping, and **GlobalEQ**. HX Edit may show the CC numbers.

To tap tempo from an eligible Stomp switch, choose **Menu → Command Center**, select that switch, set its command to **Tap**, and save the preset.

### Metronome

Add **Looper → Metronome** and enable it. **Time** sets the synced division, **Level** sets click volume, and **Accent** emphasizes every selected number of beats. Turn **Thru** on to hear your signal with the click or off for click alone.

### FX Loop and Return noise gates

Use **FX Loop L** for a pedal connected from **Send** back to **Return L/Mono**. Use a **Return** block to bring in an external signal directly. Enable the block, turn **Gate** on, and raise **Threshold** with the strings muted until the hiss drops. Lower it if it cuts soft notes. Increase **Decay** if the gate closes too abruptly. For a quick loop test, use **Mix = 100%**. The gate acts on the return signal.

### Noise Gate Input Sidechain

Plug your guitar into **Input L/Mono**. Put a regular **Noise Gate** after a high-gain drive or amp and turn **Input Sidechain** on. The gate responds to the clean guitar, so muting the strings can close it even while the drive hisses. Compare On and Off with the same Threshold and Decay.

### USB & Send routing

Find **Path A Out** under **Global Settings → Ins/Outs**. The setting applies across presets.

| Path A Out | Destination |
|---|---|
| **Main L/R** | Normal Main L/R route. |
| **Send/USB** | Send jacks and **USB 3/4**. Monitor DAW return on **USB 1/2**. |
| **USB Only** | **USB 3/4** with the Send jacks quiet. Monitor DAW return on **USB 1/2**. |
| **Main+Snd** | Main L/R plus Send jacks and **USB 3/4**. |

Set a DAW track to receive **HX Stomp XL USB 3/4** to check the processed signal. Leave DAW monitoring off initially to distinguish direct output from the computer return. **Set Path A Out back to Main L/R before using an FX Loop preset.** Sending Path A to the Send jacks can feed the loop back into itself.

### Build notes

The beat dot, gain-reduction redraw, FX Loop gate, and Input Sidechain worked on the XL during RAM testing. USB/Send routing and per-preset LED color still need complete hardware checks. The release uses original Line 6 names. Screen mirroring and recording belong to a separate diagnostic RAM build. A normal power cycle exits a RAM test and returns to the installed firmware.

## Source credits

HXtraXL is maintained by [Daygame](https://github.com/daygame-ctrl). It draws on code from [HXtra](https://github.com/wisemandenny/hxtra) and [NAM A2 Lite](https://github.com/nocaseguy/hx-stomp-nam-lite). Their maintainers are credited for their upstream work and are not involved in this release.

See [LICENSE](LICENSE) and [NOTICE](NOTICE).
