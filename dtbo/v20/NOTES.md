# V20 clone screen file

- **Unit:** V20 clone board, Arch R **Clone** image, board `eeclone`
- **Made from:** `dtb_02_at_58MB.dtb` scanned off the stock card (`rk3326-evb-lp3-v12-linux`), website generator, console **R36S Clone**
- **Default mode:** `M clock=30000 horizontal=640,46,2,44 vertical=480,16,2,14` (~80 Hz, same as the factory firmware)
- **Flags:** `0xe03`
- **Also carries:** speaker amplifier, headphone detect, LED and LCD power wiring from the stock DTB. Needed for the built-in speaker.
- **Confirmed working:** 2026-10-21

## Did not work on this unit

The built-in **R36S V20** panel from the Arch R Flasher's list (the first one tried) gave no usable picture on this board. It is a different panel: 24 setup commands (`seq=b9f11283...`), default `clock=30000 horizontal=640,150,50,150 vertical=480,20,6,12` (~58 Hz), SHA-256 starting `8e45cb138b9b`. "V20" on the board does not guarantee that panel. Make the file from your own stock card.
