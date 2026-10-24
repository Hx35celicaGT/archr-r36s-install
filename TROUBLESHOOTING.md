# Troubleshooting

Start every problem the same way: put the card in your PC and run

```bash
python3 tools/check_card.py <path-to-ARCHR> --board v21|v20|soysauce
```

It reads the card only and prints what is wrong in plain words.

---

## Boot

| Symptom | Cause | Fix |
|---|---|---|
| Lit screen only, nothing happens | Wrong image for the board | V20 = **Clone**. V21 and Soysauce = **Original**. Reflash on its own card. |
| "BOOT FAILED" | Original image on a clone board | Use the Clone image |
| `error.log` on ARCHR: `lcd init fail, check dtb file` | No matching board file in the image (usually Original image on a V20) | Use the Clone image |
| Reboots over and over | Wrong image, or overclock on | Check the image. If overclock is on: edit `/storage/.config/system.cfg` and set `enable.turbo-mode=0` |
| Storage stays tiny (32 MB) | First boot stopped before resizing | Boot once without the overlay to see if it's the cause; check `fs-resize.log` on ARCHR |

## Screen

| Symptom | Cause | Fix |
|---|---|---|
| Black screen after the logo | Overlay missing, misnamed, or in the wrong folder | It must be exactly `overlays/mipi-panel.dtbo` |
| Black screen, file is in place | Overlay made from the wrong DTB | Regenerate from the DTB on **that unit's own stock card** |
| Band that rolls when the screen redraws, bad colors (V21) | Broken default timing in the stock DTB | [V21 page](boards/R36S-V21.md) |
| Colors slowly bleed or smear (Soysauce) | Non-continuous DSI clock (`0xe03`) | [Soysauce page](boards/Soysauce-Y3506.md), set flags to `0xa03` |
| Picture upside down or sideways | Rotation | Regenerate with the rotation option |

## Buttons

### Only Select and Start work, OTG port dead

The card has the wrong board file pinned. This happens when a card set to Soysauce goes into a V21 (or the other way round).

**Over SSH** (needs Wi-Fi, which won't work if OTG is dead, so usually use the PC method):
```bash
device-switch            # shows the current board
device-switch r36s       # or: soysauce
reboot
```

**From your PC:**
1. Open `extlinux/extlinux.conf` on ARCHR in a text editor (Notepad++ on Windows, not Word).
2. Find the `FDT /dtbs/...` line and set it for your board:

   | Board | Line |
   |---|---|
   | V21 / R36S | `  FDT /dtbs/rk3326-gameconsole-r36s.dtb` |
   | Soysauce | `  FDT /dtbs/rk3326-gameconsole-soysauce.dtb` |
   | V20 clone | `  FDT /dtbs/rk3326-gameconsole-eeclone.dtb` |

   Keep the spaces at the start of the line.
3. If a `device.name` file is in the root of ARCHR, put the same name in it (`r36s`, `soysauce`).
4. Save, eject safely, boot.

On Linux, if the editor won't save: `sudo mount -o remount,rw /media/$USER/ARCHR`.

### Other button problems

| Symptom | Fix |
|---|---|
| A stick moves the wrong way | Regenerate the overlay with **Invert left stick** / **Invert right stick** |
| Sticks act strangely | Regenerate with **Joypad layout** forced to `K36 (2 sticks)` |
| A/B swapped in menus | ES: Start > UI Settings > Switch confirm & cancel buttons |
| A/B swapped in games | Set `controller_layout` (nintendo / xbox) for that system |

## Sound

| Symptom | Fix |
|---|---|
| No sound at all | Over SSH: `amixer get 'Playback Path'`. If wrong: `amixer set 'Playback Path' SPK` |
| Headphones work, speaker silent (V20) | Regenerate the overlay on the website (R36S Clone), update to Arch R 2.1 or newer |

## Reporting a bug to Arch R

Include: board marking, Arch R version (ES > System Information), image (original/clone), and the output of `check_card.py`. Issues go to <https://github.com/archr-linux/Arch-R/issues>.
