"""Build "Late Sans": Lato 2.015 + the math symbols Lato lacks, taken from Lete Sans Math.

Lato 2.015 has no glyphs for e.g. nabla, propto, cdot, langle/rangle or hbar, and matplotlib's
mathtext can only fall back to Computer Modern or STIX for them. Lete Sans Math is a
math font drawn to match Lato (SIL OFL 1.1), so its symbols blend in. The square-root sign
is also taken from Lete, because Lato's does not join the bar matplotlib draws over the radicand.

Lato's license reserves the name "Lato" for modified copies, so the result gets a new name:
"Late Sans", a blend of Lato and Lete.

Usage:
    python build_late_sans.py LATO_DIR LETE_DIR OUT_DIR
    LATO_DIR: folder with Lato-{Regular,Italic,Bold,BoldItalic}.ttf (official Lato 2.015)
    LETE_DIR: folder with LeteSansMath.otf and LeteSansMath-Bold.otf
              (https://github.com/abccsss/LeteSansMath or CTAN lete-sans-math)
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FAMILY = "Late Sans"
# (file style, full-name style, Lato file, Lete file)
STYLES = [("Regular", "Regular", "Lato-Regular.ttf", "LeteSansMath.otf"),
          ("Italic", "Italic", "Lato-Italic.ttf", "LeteSansMath.otf"),
          ("Bold", "Bold", "Lato-Bold.ttf", "LeteSansMath-Bold.otf"),
          ("BoldItalic", "Bold Italic", "Lato-BoldItalic.ttf", "LeteSansMath-Bold.otf")]
# Unicode blocks math text can draw from (letters/digits/Greek come from Lato itself)
BLOCKS = [(0x2100, 0x214F), (0x2190, 0x21FF), (0x2200, 0x22FF), (0x2300, 0x23FF),
          (0x25A0, 0x25FF), (0x27C0, 0x27EF), (0x27F0, 0x27FF), (0x2900, 0x297F),
          (0x2980, 0x29FF), (0x2A00, 0x2AFF)]
# Lato glyphs to replace with Lete's math versions (the square-root sign)
REPLACE = [0x221A]


def merge(lato_path, lete_path, out_path, file_style, full_style):
    base, src = TTFont(lato_path), TTFont(lete_path)
    scale = base["head"].unitsPerEm / src["head"].unitsPerEm
    base_cmap, src_cmap = base.getBestCmap(), src.getBestCmap()
    src_glyphs = src.getGlyphSet()
    wanted = [cp for lo, hi in BLOCKS for cp in range(lo, hi + 1)
              if cp in src_cmap and (cp not in base_cmap or cp in REPLACE)]

    order = list(base.getGlyphOrder())
    glyf, hmtx = base["glyf"], base["hmtx"]
    added = {}
    for cp in wanted:
        name = f"uni{cp:04X}" if cp not in base_cmap else f"uni{cp:04X}.math"
        if name in glyf.glyphs:
            continue
        src_glyph = src_glyphs[src_cmap[cp]]
        pen = TTGlyphPen(None)
        src_glyph.draw(TransformPen(Cu2QuPen(pen, max_err=1.0, reverse_direction=True),
                                    (scale, 0, 0, scale, 0, 0)))
        bp = BoundsPen(None)
        src_glyph.draw(TransformPen(bp, (scale, 0, 0, scale, 0, 0)))
        glyf.glyphs[name] = pen.glyph()
        hmtx.metrics[name] = (int(round(src_glyph.width * scale)),
                              int(round(bp.bounds[0])) if bp.bounds else 0)
        order.append(name)
        added[cp] = name

    base.setGlyphOrder(order)
    glyf.setGlyphOrder(order)
    for table in base["cmap"].tables:
        if table.isUnicode():
            table.cmap.update({cp: n for cp, n in added.items()
                               if table.format != 4 or cp <= 0xFFFF})
    # per-glyph device tables would now have the wrong length
    for tag in ("hdmx", "LTSH", "VDMX", "DSIG"):
        if tag in base:
            del base[tag]

    ps = FAMILY.replace(" ", "") + "-" + file_style
    for rec in base["name"].names:
        if rec.nameID in (1, 16):
            rec.string = FAMILY
        elif rec.nameID == 4:
            rec.string = f"{FAMILY} {full_style}"
        elif rec.nameID == 6:
            rec.string = ps
        elif rec.nameID == 3:
            rec.string = f"{ps};based on Lato 2.015 + Lete Sans Math"
        elif rec.nameID == 0:
            rec.string = (str(rec) + " Math symbols: Copyright (c) 2018-2024 Xiangdong Zeng, "
                          "Chenjing Bu, Daniel Flipo (Lete Sans Math). SIL Open Font License 1.1.")
    base.save(out_path)
    return len(added)


if __name__ == "__main__":
    lato_dir, lete_dir, out_dir = map(Path, sys.argv[1:4])
    out_dir.mkdir(parents=True, exist_ok=True)
    for file_style, full_style, lato, lete in STYLES:
        out = out_dir / f"LateSans-{file_style}.ttf"
        n = merge(lato_dir / lato, lete_dir / lete, out, file_style, full_style)
        print(f"{out.name}: added {n} math symbols")
