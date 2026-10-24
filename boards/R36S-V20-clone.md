# R36S V20 (Clone board)

| | |
|---|---|
| Board marking | `V20` (clone) |
| Arch R image | **Clone** (`...-clone.img.gz`) |
| Generator console | **R36S Clone** (`SDCLONE`) |
| Board file Arch R should use | `rk3326-gameconsole-eeclone.dtb` (picked automatically) |
| Stock DTB | Hidden inside the stock card. Reports `rk3326-evb-lp3-v12-linux`. |

## Install

Follow the [main guide](../README.md) with the values above. The differences from an Original board:

### 1. Don't trust the Flasher's built-in "V20" panel

The first thing we tried was the **R36S V20** panel from the Arch R Flasher's list. It did not work on this unit: it is a different screen (different panel chip and timing). Clone boards with the same marking can ship with different screens, so make the file from **your own stock card**.

### 1b. The stock card may look broken in your PC

Our V20's stock card **still booted the V20 fine**, but the PC couldn't read it: it showed 16 GB instead of the 64 GB on the label and no partitions at all. That is a cheap fake-capacity card with a damaged partition table. The files were still on it, just hidden, and the scanner below found the right DTB anyway.

- Back it up anyway (Step 2 of the main guide). The backup only reads the card.
- **Never** use that card for Arch R.

### 2. Pull the DTB out with the scanner

```bash
python3 tools/find_dtbs.py v20-stock.img v20_dtbs
```

Use the DTB near the start of the card that reports:

```
model: Rockchip rk3326 evb lpddr3 v12 board for linux
compatible: rockchip,rk3326-evb-lp3-v12-linux
```

On our V20 it was `dtb_02_at_58MB.dtb`, about 105 KB. Rename it `v20-stock.dtb`.

This DTB was clean: its default timing is **30 MHz, about 80 Hz**. That is how this clone panel runs from the factory. No fix needed.

### 3. Use the website generator, not a hand-made overlay

For clone boards the generator also copies the **speaker amplifier and headphone-jack wiring** from your DTB. The V20 needs that for its built-in speaker to work. A hand-built overlay without it gives sound in headphones only.

### 4. Confirm it is the Clone image before booting

```bash
python3 tools/check_card.py /media/$USER/ARCHR --board v20
```

It must say **Image: clone** and list `rk3326-gameconsole-eeclone.dtb`. If it says `original`, you flashed the wrong file. Reflash with `-clone.img.gz`.

## Known issues

| Symptom | Cause | Fix |
|---|---|---|
| Only a lit screen, nothing else | Original image (or a V21/Soysauce card) in the V20 | Flash the **Clone** image on its own card |
| `error.log` on ARCHR says `lcd init fail, check dtb file` | Original image: no clone board file, fell back to another board | Same as above |
| Storage stays 32 MB, never reaches the menu | Boot stops before resizing | Boot once without `overlays/mipi-panel.dtbo`. If storage grows, the overlay is the problem: regenerate it. |
| No speaker sound, headphones OK | Overlay missing amp wiring, or pre-2.1 Arch R | Regenerate on the website (R36S Clone) and update to Arch R 2.1+ |

## If you need to force the board file

Only if `check_card.py` shows the Clone image but the wrong board loads:

1. Open `extlinux/extlinux.conf` on ARCHR.
2. Change the commented line `  # FDT /dtbs/your-custom-devicetree.dtb` to:
   ```
     FDT /dtbs/rk3326-gameconsole-eeclone.dtb
   ```
3. Save, eject safely, boot.
