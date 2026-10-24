# Installing Arch R on the R36S (Original, V20/V21 Clone, Soysauce)

A step-by-step guide for getting [Arch R](https://github.com/archr-linux/Arch-R) (an Arch Linux based handheld OS) running on the different R36S boards. Written from real installs on three units:

| Unit | Board marking | Arch R image | Generator console |
|---|---|---|---|
| R36S V21 | `R36S-V21 2024-12-18` | **Original** | R36S Original |
| R36S V20 | `V20` clone board | **Clone** | R36S Clone |
| Soysauce | `Y3506_V05_20251215` | **Original** | R36S Soysauce |

If you only read one thing: **every R36S needs two matching pieces.**

1. **The right image.** Original or Clone. The wrong one won't boot at all.
2. **The right screen file** (`overlays/mipi-panel.dtbo`). Made from the DTB on the SD card that **came with that exact unit**. The wrong one gives a black screen, bad colors or a rolling band.

Buttons and USB are a third piece, but Arch R normally sets them automatically. See [Buttons and USB](#step-7-check-the-buttons-and-usb).

---

## Contents

- [What you need](#what-you-need)
- [Step 1: Identify your board](#step-1-identify-your-board)
- [Step 2: Back up the stock card](#step-2-back-up-the-stock-card)
- [Step 3: Get your stock DTB](#step-3-get-your-stock-dtb)
- [Step 4: Make the screen file (DTBO)](#step-4-make-the-screen-file-dtbo)
- [Step 5: Flash Arch R](#step-5-flash-arch-r)
- [Step 6: First boot](#step-6-first-boot)
- [Step 7: Check the buttons and USB](#step-7-check-the-buttons-and-usb)
- [Step 8: Save your working files](#step-8-save-your-working-files)
- [Board pages](#board-pages)
- [Tools in this repo](#tools-in-this-repo)

---

## What you need

- A **new, name-brand microSD card** (Samsung or SanDisk, 16 GB or more). **Do not reuse the card that came with the R36S.** Those cards are often fake-capacity and fail. Keep it only as the source of your DTB.
- A PC with an SD card reader (Windows 10/11 or Linux).
- The **stock card that shipped with your unit**, untouched.
- Optional: a USB Wi-Fi dongle for SSH later.

**One card per unit.** Do not move a card between an Original and a Clone board. Flashing a new image erases the whole card, including anything you installed on it.

---

## Step 1: Identify your board

Take the back cover off (4 screws) or check the label through the battery area. The board marking is printed on the PCB near the edge.

| Printed on the board | What it is | Image |
|---|---|---|
| `R36S-V1x`, `R36S-V21`, `R36S-V22` (genuine style) | R36S Original | Original |
| `Y3506_V0x_...` | R36S Soysauce | Original |
| `V20` clone, `K36`, `G80CA-MB`, `EE clone` | R36S Clone | Clone |

**Not sure?** The stock card tells you. In Step 3, an Original board's card has a DTB file you can see (for example `rk3326-r35s-linux.dtb`). A clone's DTB is usually hidden inside the card and reports `rk3326-evb-lp3-v12-linux`. And if you flash the wrong image, a clone shows "BOOT FAILED" or just a lit screen.

> **V20 vs V21 trap:** the names look alike but they are different families. In our testing the V21 is an Original board and the V20 is a Clone board. The V21's card would not boot the V20 at all, only lit the screen.

---

## Step 2: Back up the stock card

Before anything else, make a full image of the stock card. If something goes wrong you can always get back to factory.

**Windows:** install [Win32 Disk Imager](https://sourceforge.net/projects/win32diskimager/).
1. Put the stock card in the reader.
2. In **Image File**, type a path such as `C:\r36s\v21-stock.img`.
3. Pick the card's drive letter under **Device**.
4. Click **Read** (not Write). Wait for it to finish.

**Linux:**
```bash
lsblk                      # find the card, for example sdc
sudo dd if=/dev/sdc of=~/v21-stock.img bs=4M status=progress
sudo chown $USER ~/v21-stock.img
```

Name each backup after the unit (`v20-stock.img`, `v21-stock.img`, `soysauce-stock.img`).

---

## Step 3: Get your stock DTB

The DTB is the file that describes your exact screen. It **must** come from the card that shipped with that unit. A DTB from ArkOS, dArkOS, ArkOS4Clone or another unit describes a different setup and will not match.

### Original boards (V21, Soysauce)

1. Put the stock card in your PC. A small partition (often called `BOOT`) shows up.
2. Open `boot.ini` in Notepad and find the line with `${dtb_loadaddr}`. The filename on that line is the DTB the unit actually uses, for example:
   ```
   load mmc 1:1 ${dtb_loadaddr} rk3326-r35s-linux.dtb
   ```
3. Copy that `.dtb` file to your PC and rename it after the unit, for example `v21-stock.dtb`.

### Clone boards (V20)

Clone cards often have no visible DTB file. Use the scanner in this repo on your backup image from Step 2:

```bash
python3 tools/find_dtbs.py v20-stock.img v20_dtbs
```

(On Windows type `python` instead of `python3`.)

It lists every DTB it finds. **Use the one near the start of the card that reports `rk3326-evb-lp3-v12-linux`** (on our V20 it was `dtb_02_at_58MB.dtb`). Ignore tiny ones (boot loader copies) and the large group past a few GB (spare files for other Rockchip devices).

---

## Step 4: Make the screen file (DTBO)

1. Open the generator: <https://arch-r.io/overlay-generator/>
2. **Console variant:** pick from the table at the top (R36S Original, R36S Clone or R36S Soysauce).
3. **Stock firmware DTB:** drop in your file from Step 3.
4. **Customization:** leave everything on default for the first try (Joypad layout `auto`, rotation 0°, no inverts).
5. Click **Generate overlay** and save the file. It must be named exactly **`mipi-panel.dtbo`**.

**If the website won't load** (it downloads an 8 MB runtime first), use the offline version, [archr-dtbo-offline.zip](https://arch-r.io/archr-dtbo-offline.zip). It needs only Python 3.5+. Extract it, open a terminal in that folder, and run:

```bash
python archr_dtbo.py v21-stock.dtb SDORIG -o mipi-panel.dtbo
```

| Console | Option string |
|---|---|
| R36S Original | `SDORIG` |
| R36S Clone | `SDCLONE` |
| R36S Soysauce | `SDORIG-NAm` |

> Check your board page before booting. **The V21 and the Soysauce each needed one fix** to the generated file. See [boards/](boards/).

---

## Step 5: Flash Arch R

### Option A: Arch R Flasher (easiest)

1. Download the flasher from [archr-flasher releases](https://github.com/archr-linux/archr-flasher/releases). Windows: `Arch.R.Flasher_x64-setup.exe` (Windows 10 1809 or newer; Windows 7 does not work).
2. **Console:** R36S Original, R36S Clone or Soysauce (same as Step 1).
3. **Image:** let it download the latest.
4. **Panel:** choose **Import DTB** and pick your stock DTB, or pick the `mipi-panel.dtbo` you made. If you already fixed the DTBO by hand, skip this and copy it on afterward (Option B, step 6).
5. **SD Card:** pick the new card. Double-check it is not your stock card.
6. Click **Flash**. Leave **Verify after writing** on.

### Option B: By hand

1. From [Arch R releases](https://github.com/archr-linux/Arch-R/releases), download the file ending in **`-original.img.gz`** or **`-clone.img.gz`**, plus `SHA256SUMS`.
2. Check the download.
   - Windows (PowerShell): `Get-FileHash .\ArchR-R36S*.img.gz -Algorithm SHA256`
   - Linux: `sha256sum -c SHA256SUMS --ignore-missing`
3. Write it with [Rufus](https://rufus.ie), balenaEtcher, or on Linux:
   ```bash
   gunzip ArchR-R36S.aarch64-*-clone.img.gz
   sudo dd if=ArchR-R36S.aarch64-*-clone.img of=/dev/sdX bs=4M conv=fsync status=progress
   sync
   ```
   Replace `sdX` with your card (check with `lsblk`). The wrong letter will erase that disk.
4. Unplug and replug the card. Open the **ARCHR** partition.
5. **Confirm the image** before going further. Run the checker from this repo (replace the path with your ARCHR drive):
   ```bash
   python3 tools/check_card.py /media/$USER/ARCHR --board v20
   ```
   Windows: `python tools\check_card.py E:\ --board v20`
6. Copy your `mipi-panel.dtbo` into the **`overlays`** folder, replacing any file there. The final path must be `overlays/mipi-panel.dtbo`. Any other name or folder is ignored and you get a black screen.
7. Eject the card safely.

---

## Step 6: First boot

1. Put the card in **TF1** (the OS slot, marked on the case).
2. Power on. The first boot grows the storage partition and **reboots once on its own**. This normally takes under a minute but can take up to 5. Don't power off during it.
3. The second boot lands in EmulationStation.

| What you see | What it means | Go to |
|---|---|---|
| Menu shows, picture is clean | Done | Step 7 |
| Black screen after the logo | Screen file missing, misnamed, or wrong | [Troubleshooting: screen](TROUBLESHOOTING.md#screen) |
| Only a lit screen, or "BOOT FAILED" | Wrong image (Original vs Clone) | [Troubleshooting: boot](TROUBLESHOOTING.md#boot) |
| Rolling band, bleeding, wrong colors | DTBO needs the board fix | your [board page](#board-pages) |

---

## Step 7: Check the buttons and USB

Test every button in the EmulationStation menu, then plug something into the OTG port.

- **All buttons work:** done.
- **Only a couple of buttons work, OTG port dead:** the board file is wrong (most often a card that was set to Soysauce now in a V21). See [Troubleshooting: buttons](TROUBLESHOOTING.md#buttons).
- **A stick moves the wrong way:** regenerate the DTBO with **Invert left stick** or **Invert right stick** ticked.
- **A and B feel swapped in menus:** EmulationStation, Start > UI Settings > **Switch confirm & cancel buttons**.

### Arch R hotkeys (all boards)

| Buttons | Action |
|---|---|
| VOL+ / VOL- | Volume |
| SELECT + VOL+ / VOL- | Brightness |
| SELECT + START + VOL+ / VOL- | Wi-Fi on / off |
| L1 + SELECT + START | Force-quit whatever is running |
| POWER | Sleep (press again to wake). Shut down from the menu. |
| SELECT + START (in a game) | Exit to the menu |
| SELECT + X (in a game) | RetroArch quick menu |
| SELECT + R1 / L1 | Save / load state |

---

## Step 8: Save your working files

Once a unit is fully working, copy its screen file off the card and keep it. An update, a reflash or a regenerated overlay can bring an old problem back, and putting this file back fixes it.

1. Copy `overlays/mipi-panel.dtbo` to [`dtbo/<your-unit>/`](dtbo/) in this repo.
2. Record it with the checker (it prints the SHA-256 to paste into `dtbo/known-good.json`):
   ```bash
   python3 tools/check_card.py /media/$USER/ARCHR --board v21
   ```

From then on, `check_card.py` tells you whether a card has the known-good file for that unit.

**SSH** (optional): EmulationStation > Start > System Settings > Network > **Enable SSH**. Log in with `ssh root@archr.local` (or the IP shown in System Information). The default password is `archr`. Change it with `passwd`.

---

## Board pages

- [R36S V21 (Original)](boards/R36S-V21.md)
- [R36S V20 (Clone)](boards/R36S-V20-clone.md)
- [Soysauce Y3506 V05 (Original)](boards/Soysauce-Y3506.md)
- [Troubleshooting](TROUBLESHOOTING.md)

## Tools in this repo

| Tool | What it does |
|---|---|
| [`tools/find_dtbs.py`](tools/find_dtbs.py) | Finds and copies every DTB on a stock card or card image. Read-only. |
| [`tools/check_card.py`](tools/check_card.py) | Reads a flashed ARCHR partition and reports: image type, board file, screen file, its timing and flags, and whether it matches your known-good copy. Read-only. |

Both need only Python 3 (no extra packages) and work on Windows and Linux.

---

## Credits and licenses

- [Arch R](https://github.com/archr-linux/Arch-R) and the [Arch R Flasher](https://github.com/archr-linux/archr-flasher) by the Arch R project (GPL-2.0 software; the distribution is CC BY-NC-SA). This guide is not affiliated with them.
- Panel overlay generator based on [overlay_server](https://github.com/stolen/overlay_server) (ROCKNIX).
- The guide text and tools in this repo: see [LICENSE](LICENSE).
