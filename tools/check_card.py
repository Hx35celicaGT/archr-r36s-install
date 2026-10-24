#!/usr/bin/env python3
"""
check_card.py - check a flashed Arch R card for a specific R36S unit.

Reads the ARCHR (boot) partition only. Never writes to the card.

Usage:
  python3 check_card.py <ARCHR-path> [--board v21|v20|soysauce]
  python3 check_card.py --set-flags 0xa03 <in.dtbo> <out.dtbo>

Examples:
  python3 check_card.py /media/$USER/ARCHR --board v21
  python  check_card.py E:\\ --board soysauce
  python3 check_card.py --set-flags 0xa03 mipi-panel.dtbo mipi-panel-fixed.dtbo

Known-good screen files are listed in ../dtbo/known-good.json.
Needs only Python 3.5+.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KNOWN_GOOD = os.path.join(HERE, "..", "dtbo", "known-good.json")

BOARDS = {
    "v21":      {"image": "original", "fdt": "rk3326-gameconsole-r36s.dtb",     "pin_ok": [None, "rk3326-gameconsole-r36s.dtb"]},
    "v20":      {"image": "clone",    "fdt": "rk3326-gameconsole-eeclone.dtb",  "pin_ok": [None, "rk3326-gameconsole-eeclone.dtb"]},
    "soysauce": {"image": "original", "fdt": "rk3326-gameconsole-soysauce.dtb", "pin_ok": ["rk3326-gameconsole-soysauce.dtb", None]},
}

problems = []
notes = []


def bad(msg):
    problems.append(msg)


def read_text(path):
    try:
        with open(path, "rb") as f:
            return f.read().decode("utf-8", "replace")
    except OSError:
        return None


def overlay_lines(data):
    """Pull the readable panel_description lines (G = general, M = mode) out of the DTBO."""
    text = data.decode("latin-1")
    return re.findall(r"((?:G size|M clock|I seq)=[\x20-\x7e]*)", text)


def set_flags(new_flags, src, dst):
    data = open(src, "rb").read()
    m = re.search(rb"flags=0x[0-9a-fA-F]+", data)
    if not m:
        print("No 'flags=0x...' found in %s. Nothing changed." % src)
        return 1
    old = m.group(0)
    new = b"flags=" + new_flags.lower().encode("ascii")
    if len(new) != len(old):
        print("New value %s is a different length from %s; the tool only does same-length edits." % (new, old))
        return 1
    if len(re.findall(rb"flags=0x[0-9a-fA-F]+", data)) > 1:
        print("More than one flags= entry found; edit by hand instead.")
        return 1
    out = data[:m.start()] + new + data[m.end():]
    with open(dst, "wb") as f:
        f.write(out)
    print("%s -> %s : %s changed to %s (size %d bytes, unchanged)" % (
        src, dst, old.decode(), new.decode(), len(out)))
    return 0


def main(argv):
    if len(argv) >= 1 and argv[0] == "--set-flags":
        if len(argv) != 4 or not re.fullmatch(r"0x[0-9a-fA-F]+", argv[1]):
            print(__doc__)
            return 1
        return set_flags(argv[1], argv[2], argv[3])

    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 1
    root = argv[0]
    board = None
    if "--board" in argv:
        i = argv.index("--board")
        board = argv[i + 1].lower() if i + 1 < len(argv) else None
        if board not in BOARDS:
            print("--board must be one of: %s" % ", ".join(BOARDS))
            return 1

    if not os.path.isdir(root):
        print("Not a folder: %s  (point this at the ARCHR partition of the card)" % root)
        return 1
    if not os.path.isdir(os.path.join(root, "dtbs")) or not os.path.isdir(os.path.join(root, "extlinux")):
        print("This doesn't look like an Arch R boot partition (no dtbs/ or extlinux/ folder).")
        return 1

    print("Card:  %s" % os.path.abspath(root))
    if board:
        print("Board: %s" % board)
    print()

    # --- image type -------------------------------------------------------
    dtbs = sorted(os.listdir(os.path.join(root, "dtbs")))
    variant = (read_text(os.path.join(root, "variant")) or "").strip().lower()
    has_clone = "rk3326-gameconsole-eeclone.dtb" in dtbs
    image = variant or ("clone" if has_clone else "original")
    print("Image:        %s%s" % (image, "" if variant else "  (guessed from dtbs/)"))
    print("Board files:  %s" % ", ".join(d for d in dtbs if "gameconsole" in d) or "(none)")
    if board:
        want = BOARDS[board]["image"]
        if image != want:
            bad("Wrong image: this card is '%s' but a %s needs the '%s' image. Reflash it." % (image, board, want))
        if BOARDS[board]["fdt"] not in dtbs:
            bad("%s is missing from dtbs/ (it only comes with the '%s' image)." % (BOARDS[board]["fdt"], want))

    # --- board pin ----------------------------------------------------------
    conf = read_text(os.path.join(root, "extlinux", "extlinux.conf")) or ""
    pin = None
    overlay_ref = None
    for line in conf.splitlines():
        s = line.strip()
        m = re.match(r"FDT\s+/?dtbs/(\S+)", s)
        if m:
            pin = m.group(1)
        m = re.match(r"FDTOVERLAYS\s+(\S+)", s)
        if m:
            overlay_ref = m.group(1)
    print("Board pin:    %s" % (pin or "none (automatic detection)"))
    devname = read_text(os.path.join(root, "device.name"))
    if devname is not None:
        print("device.name:  %s" % devname.strip())
    if board:
        ok = BOARDS[board]["pin_ok"]
        if pin not in ok:
            bad("Board pin is %s. For a %s use: FDT /dtbs/%s  (see TROUBLESHOOTING.md#buttons)"
                % (pin, board, BOARDS[board]["fdt"]))
        elif board == "soysauce" and pin is None:
            notes.append("No Soysauce pin. If buttons or USB don't work, run 'device-switch soysauce'.")
    if overlay_ref and overlay_ref.lstrip("/") != "overlays/mipi-panel.dtbo":
        notes.append("extlinux.conf loads %s, not /overlays/mipi-panel.dtbo." % overlay_ref)

    # --- screen file --------------------------------------------------------
    print()
    ov = os.path.join(root, "overlays", "mipi-panel.dtbo")
    others = [f for f in os.listdir(os.path.join(root, "overlays"))] if os.path.isdir(os.path.join(root, "overlays")) else []
    if not os.path.isfile(ov):
        bad("overlays/mipi-panel.dtbo is missing: expect a black screen after the logo.")
        stray = [f for f in others if f.lower().endswith(".dtbo")]
        if stray:
            bad("Found %s in overlays/ but the name must be exactly mipi-panel.dtbo." % ", ".join(stray))
    else:
        data = open(ov, "rb").read()
        sha = hashlib.sha256(data).hexdigest()
        print("Screen file:  overlays/mipi-panel.dtbo  %d bytes" % len(data))
        print("SHA-256:      %s" % sha)
        lines = overlay_lines(data)
        flags = re.search(r"flags=(0x[0-9a-fA-F]+)", " ".join(lines))
        print("Screen flags: %s" % (flags.group(1) if flags else "(not found)"))
        modes = [l for l in lines if l.startswith("M ")]
        if modes:
            print("Screen modes:")
            for l in modes:
                print("   " + l)
        default = next((l for l in modes if "default=1" in l), modes[0] if modes else "")

        if board == "v21" and default:
            if "clock=29000" not in default or ",165," not in default:
                bad("V21: default mode is not 'clock=29000 ... vertical=480,165,...'. "
                    "Expect the rolling band. See boards/R36S-V21.md.")
        if board == "soysauce" and flags and flags.group(1).lower() == "0xe03":
            bad("Soysauce: flags are 0xe03 (non-continuous clock). Expect bleeding. "
                "Fix: python3 check_card.py --set-flags 0xa03 in.dtbo out.dtbo")

        # known-good comparison
        try:
            kg = json.load(open(KNOWN_GOOD))
        except (OSError, ValueError):
            kg = {}
        match = [k for k, v in kg.items() if isinstance(v, dict) and v.get("sha256", "").lower() == sha]
        if match:
            print("Known-good:   YES, matches '%s'" % ", ".join(match))
            if board and board not in match:
                bad("This is the known-good file for %s, not for %s." % (", ".join(match), board))
        elif board and isinstance(kg.get(board), dict) and kg[board].get("sha256"):
            bad("Does not match the known-good file for %s. Copy dtbo/%s/mipi-panel.dtbo over it if the screen is wrong."
                % (board, board))
        elif board:
            notes.append('No known-good file recorded for %s. Once the screen is right, put this SHA-256 in '
                         'dtbo/known-good.json under "%s".' % (board, board))
        if os.path.isfile(ov + ".orig"):
            notes.append("A backup overlays/mipi-panel.dtbo.orig is on the card.")

    # --- logs ------------------------------------------------------------------
    err = read_text(os.path.join(root, "error.log"))
    if err and err.strip():
        print("\nerror.log:    %s" % err.strip())
        if "lcd init fail" in err:
            bad("Boot loader reported 'lcd init fail': wrong image or wrong overlay for this board.")

    print()
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
    else:
        print("No problems found%s." % (" for a " + board if board else ""))
    for n in notes:
        print("  note: " + n)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
