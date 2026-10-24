#!/usr/bin/env python3
"""
find_dtbs.py - find and copy every device tree (DTB) on an SD card or card image.

Read-only: it never writes to the source.

Usage:
  python3 find_dtbs.py <card-image-or-device> <output-folder>

Examples:
  python3 find_dtbs.py v20-stock.img v20_dtbs            (image file, any OS)
  sudo python3 find_dtbs.py /dev/sdc v20_dtbs            (Linux card reader)
  python find_dtbs.py \\\\.\\PhysicalDrive2 v20_dtbs     (Windows, run as Administrator)

Making an image first (Win32 Disk Imager "Read", or dd on Linux) is the safest way.
Needs only Python 3.5+.
"""
import os
import struct
import sys

MAGIC = b"\xd0\x0d\xfe\xed"
CHUNK = 4 * 1024 * 1024          # 4 MiB, a multiple of 512 so raw devices work
SECTOR = 512
MIN_SIZE = 0x40
MAX_SIZE = 4 * 1024 * 1024        # real DTBs are well under this


class AlignedReader:
    """Reads any byte range, but only issues sector-aligned reads (needed on Windows raw disks)."""

    def __init__(self, path):
        self.f = open(path, "rb", buffering=0)

    def read_at(self, offset, size):
        start = offset - (offset % SECTOR)
        end = offset + size
        end += (-end) % SECTOR
        self.f.seek(start)
        data = b""
        want = end - start
        while len(data) < want:
            piece = self.f.read(want - len(data))
            if not piece:
                break
            data += piece
        return data[offset - start: offset - start + size]

    def close(self):
        self.f.close()


def header(buf):
    """Return the header fields if buf starts with a believable FDT header, else None."""
    if len(buf) < 40 or buf[:4] != MAGIC:
        return None
    (totalsize, off_struct, off_strings, off_rsvmap, version,
     last_comp, _boot_cpu, size_strings, size_struct) = struct.unpack(">9I", buf[4:40])
    if not (MIN_SIZE <= totalsize <= MAX_SIZE):
        return None
    if version < 16 or version > 17 or last_comp > 17:
        return None
    for off in (off_struct, off_strings, off_rsvmap):
        if off < 40 or off >= totalsize:
            return None
    if off_struct + size_struct > totalsize or off_strings + size_strings > totalsize:
        return None
    return dict(totalsize=totalsize, off_struct=off_struct, off_strings=off_strings,
                size_struct=size_struct, size_strings=size_strings)


def root_props(dtb, h):
    """Read the properties of the root node (model, compatible)."""
    out = {}
    pos = h["off_struct"]
    end = pos + h["size_struct"]
    strings = dtb[h["off_strings"]: h["off_strings"] + h["size_strings"]]
    depth = 0
    try:
        while pos < end:
            token = struct.unpack(">I", dtb[pos:pos + 4])[0]
            pos += 4
            if token == 1:                      # BEGIN_NODE
                depth += 1
                name_end = dtb.index(b"\x00", pos)
                pos = (name_end + 4) & ~3
                if depth > 1:
                    break                       # past the root's own properties
            elif token == 3:                    # PROP
                length, nameoff = struct.unpack(">II", dtb[pos:pos + 8])
                pos += 8
                value = dtb[pos:pos + length]
                pos = (pos + length + 3) & ~3
                name = strings[nameoff: strings.index(b"\x00", nameoff)].decode("ascii", "replace")
                if depth == 1 and name in ("model", "compatible"):
                    parts = [p.decode("ascii", "replace") for p in value.split(b"\x00") if p]
                    out[name] = ", ".join(parts)
            elif token == 2:                    # END_NODE
                depth -= 1
            elif token == 4:                    # NOP
                continue
            else:                               # 9 = END, or garbage
                break
    except (ValueError, struct.error):
        pass
    return out


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    reader = AlignedReader(src)

    found = 0
    seen = set()
    pos = 0
    overlap = 40                                 # so a header split across chunks is still found
    last_mb = -1
    while True:
        chunk = reader.read_at(pos, CHUNK)
        if not chunk:
            break
        idx = chunk.find(MAGIC)
        while idx != -1:
            offset = pos + idx
            if offset in seen:
                idx = chunk.find(MAGIC, idx + 1)
                continue
            seen.add(offset)
            head = reader.read_at(offset, 40)
            h = header(head)
            if h:
                dtb = reader.read_at(offset, h["totalsize"])
                if len(dtb) == h["totalsize"]:
                    found += 1
                    mb = offset // (1024 * 1024)
                    name = "dtb_%02d_at_%dMB.dtb" % (found, mb)
                    with open(os.path.join(outdir, name), "wb") as f:
                        f.write(dtb)
                    props = root_props(dtb, h)
                    print("\n[%d] %s  size=%d  offset=0x%X" % (found, name, len(dtb), offset))
                    print("     model:      %s" % props.get("model", "(none)"))
                    print("     compatible: %s" % props.get("compatible", "(none)"))
            idx = chunk.find(MAGIC, idx + 1)
        if len(chunk) < CHUNK:
            break
        pos += CHUNK - overlap
        mb = pos // (1024 * 1024)
        if mb // 256 != last_mb:
            last_mb = mb // 256
            sys.stderr.write("\rscanned %d MB..." % mb)
            sys.stderr.flush()
    reader.close()
    sys.stderr.write("\n")

    print("\nFound %d DTB(s). Saved in: %s" % (found, os.path.abspath(outdir)))
    if found:
        print("Pick the one near the start of the card whose model/compatible names an rk3326 board.")
        print("Tiny ones are boot loader copies; a big group far into the card is spares for other devices.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
