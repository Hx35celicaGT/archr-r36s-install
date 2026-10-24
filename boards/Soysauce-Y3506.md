# Soysauce Y3506 V05 (Original family)

| | |
|---|---|
| Board marking | `Y3506_V05_20251215` |
| Arch R image | **Original** (`...-original.img.gz`) |
| Generator console | **R36S Soysauce** (`SDORIG-NAm`) |
| Board file Arch R should use | `rk3326-gameconsole-soysauce.dtb` |
| Stock DTB | the file named in the stock card's `boot.ini` (ours: `rk3326-r35s-linux.dtb`) |

## Install

Follow the [main guide](../README.md) with the values above, then do the two Soysauce steps below.

### 1. Set the board to Soysauce

The Soysauce wires the buttons and USB differently from an R36S. If buttons or the OTG port don't work after the first boot, pin the Soysauce board file.

**Over SSH:**
```bash
ssh root@archr.local          # password: archr
device-switch                 # shows the current board
device-switch soysauce
reboot
```

**From your PC:** open `extlinux/extlinux.conf` on ARCHR and set the FDT line to:
```
  FDT /dtbs/rk3326-gameconsole-soysauce.dtb
```
If there is a `device.name` file in the root of ARCHR, set its contents to `soysauce`.

> This pin stays on the card. If you later move the card to a V21 or another R36S, switch it back (`device-switch r36s`). See [Troubleshooting: buttons](../TROUBLESHOOTING.md#buttons).

### 2. Fix the screen bleeding (clock flag)

**Symptom:** the picture is fine right after boot or wake, then colors slowly bleed or smear, especially white text on dark blue.

**Cause:** the generator writes DSI flags `0xe03`. The extra bit (`0x400`) turns on *non-continuous clock*, which stops the panel's clock between lines. The stock firmware uses `0xa03` (clock always running), and this panel drifts without it.

**Check:**
```bash
python3 tools/check_card.py /media/$USER/ARCHR --board soysauce
```
The **Screen flags** line shows `0xe03` (needs the fix) or `0xa03` (fixed).

**Fix:**
1. **Best:** copy the known-good file from [`dtbo/soysauce/`](../dtbo/) to `overlays/mipi-panel.dtbo`.
2. **Rebuild:** the tool can change only that one value and nothing else:
   ```bash
   python3 tools/check_card.py --set-flags 0xa03 mipi-panel.dtbo mipi-panel-fixed.dtbo
   ```
   The output file is the same size. Copy it to `overlays/mipi-panel.dtbo` (keep that exact name).
   If the tool says it found no `flags=`, your generator version stores it differently: use the known-good file instead.

Keep a copy of the old file (`mipi-panel.dtbo.orig`) on the card so you can go back.

## Things that did not help (so you don't repeat them)

- Swapping in panel settings from other DTBs (for example `rk3326-rg351mp-linux.dtb`, which is really an ODROID-GO3): mirrored picture, inverted colors, flicker.
- DTB download sites: they didn't have this board. The DTB from the card that came with the unit, run through the generator, plus the flag fix above, is what worked.
