# Known-good screen files

One folder per unit. Each holds the `mipi-panel.dtbo` that is confirmed working on that unit.

| Folder | Unit | Image | Board pin |
|---|---|---|---|
| `v21/` | R36S-V21 2024-12-18 | Original | none (auto, `r36s`) |
| `v20/` | V20 clone | Clone | none (auto, `eeclone`) |
| `soysauce/` | Soysauce Y3506_V05_20251215 | Original | `soysauce` |

Each folder has a `NOTES.md` saying how the file was made and what it fixes.

## Adding or updating a file

1. With the unit working, put its card in your PC.
2. Copy `overlays/mipi-panel.dtbo` from the ARCHR partition into the matching folder here.
3. Run the checker and copy the **SHA-256** line it prints:
   ```bash
   python3 tools/check_card.py /media/$USER/ARCHR --board v21
   ```
4. Paste it into `known-good.json` under that board's `"sha256"`.
5. Commit both files.

## Using one

Copy the file to `overlays/mipi-panel.dtbo` on the ARCHR partition, keeping that exact name.

**These files only fit the board they were made from.** Another unit with the same marking usually has the same panel, but a different production batch can differ. If the picture is wrong, make your own from that unit's stock card (main guide, Steps 3 and 4).
