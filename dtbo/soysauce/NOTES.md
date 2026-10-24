# Soysauce screen file

- **Unit:** Soysauce `Y3506_V05_20251215`, Arch R **Original** image, board pinned to `soysauce` (`device-switch soysauce`)
- **Made from:** the DTB on the unit's card, generator console **R36S Soysauce**
- **Default mode:** `M clock=40760 horizontal=640,120,139,120 vertical=480,17,5,13`
- **Flags:** `0xa03` (continuous DSI clock). The generator writes `0xe03`, which made the colors slowly bleed.
- **`before-fix/mipi-panel.dtbo.orig`:** the generator's output before the fix, kept for reference. It differs by one byte. Recreate the fix with:
  ```bash
  python3 tools/check_card.py --set-flags 0xa03 dtbo/soysauce/before-fix/mipi-panel.dtbo.orig mipi-panel.dtbo
  ```
  The result is byte-for-byte identical to `soysauce/mipi-panel.dtbo`.
- **Confirmed working:** 2026-10
