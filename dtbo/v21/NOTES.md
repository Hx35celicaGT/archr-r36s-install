# V21 screen file

- **Unit:** R36S-V21 2024-12-18, Arch R **Original** image, board `r36s` (no Soysauce pin)
- **Made from:** stock `rk3326-r35s-linux.dtb` (model "Game Console R35S/R36S fix by lxc"), with `native-mode` pointed at the 29 MHz timing
- **Default mode:** `M clock=29000 horizontal=640,46,2,44 vertical=480,165,2,14` (~59.9 Hz)
- **Flags:** `0xe03` (fine on this panel)
- **Fixes:** rolling band and wrong colors from the unpatched generator output (23.04 MHz default)
- **Confirmed working:** 2026-10-08
