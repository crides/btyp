from dataclasses import dataclass
from functools import reduce
from typing import Callable, cast
import build123d as b, math, build123d.topology
X, Y, Z = b.Axis.X, b.Axis.Y, b.Axis.Z
XY, XZ, YZ, YX, ZX, ZY = b.Plane.XY, b.Plane.XZ, b.Plane.YZ, b.Plane.YX, b.Plane.ZX, b.Plane.ZY
LOW, MID, HIGH = b.Align.MIN, b.Align.CENTER, b.Align.MAX
Vec = b.Vector
Pos, Loc = b.Pos, b.Location

M3D = build123d.topology.three_d.Mixin3D
m3d_add = M3D.__add__
def new_m3d_add(self, other):
    r = m3d_add(self, other)
    return b.Compound(r) if isinstance(r, b.ShapeList) else r
M3D.__add__ = new_m3d_add

from kicaq import *
import os, pcbnew

mag_I = 46
mag_O = 54.2
holes = [(34, 9), (-34, 32), (34, -9), (-34, -32)]
bat = 40, 16
mag_t = 0.5
bat_h = 5.5
pcb_w = 75
mag_clr = 72
pcb_h = 78
pcb_fr = 7.5
sh_t = 2.5
sh_d = 4
m2_hd = 2.3

def gen_bot():
    top = bat_h + mag_t
    base = b.loft([Pos(Z=top) * b.RectangleRounded(pcb_w, mag_clr, 4), b.RectangleRounded(pcb_w, pcb_h, pcb_fr)])
    for loc in b.Locations(holes):
        base -= loc * b.Cylinder(m2_hd / 2, 100)
        base -= Pos(Z=sh_t) * loc * b.Cylinder(sh_d / 2, 100, align=(MID, MID, LOW))
    base -= b.extrude(b.Circle(mag_O / 2) - b.Circle(mag_I / 2), bat_h)
    base -= b.extrude(b.RectangleRounded(bat[0], bat[1], 2), bat_h)
    base -= b.extrude(Pos(-pcb_w / 2, 2.5) * b.Rectangle(23, 2.5 + 12.5, align=(LOW, HIGH)), bat_h)
    return base

def gen_top():
    PINKIES = [1, 5, 9, 16, 20, 24]
    HOME = [5, 6, 7, 8, 17, 18, 19, 20]
    board = Board(os.getenv("HOME") + "/gitproj/btyp/btyp.kicad_pcb")
    def fp_loc(fp: Component):
        fp = board.fp(fp)
        return b.Location(board.pos(fp), fp.GetOrientation().AsDegrees())
    edges = board.edges_bd()
    center = edges.bounding_box().center()
    board.center = pcbnew.VECTOR2I_MM(center.X, -center.Y)
    base = b.Pos(-center) * b.offset(edges, 0.5)
    cols = lambda x: [fp_loc(board.fp(f"K{i}")) * b.RectangleRounded(x * 16.5, 3 * (10.5 if i in PINKIES else 11.5), 0.5) for i in HOME]
    fat_cols = cols(1.25)
    inter = reduce((lambda x, y: x + y), (fat_cols[i] & fat_cols[i + 1] for i in range(len(fat_cols) - 1)))
    for col in cols(1):
        base -= col
    base -= inter
    base = b.extrude(base, 4)
    base -= Pos(-75 / 2 + 3) * b.extrude(b.RectangleRounded(75 - 9 - 3, 14, 1, align=(LOW, MID)), 2) # center components
    port_hole = b.Box(20, 10, 3.2, align=(LOW, MID, LOW))
    port_hole = b.fillet((port_hole.edges() | X) >> Z, 0.75)
    base -= Pos(75 / 2 - 9) * port_hole
    for fp in ["SW1", "SW2", "D1"]:
        base -= b.extrude(board.layer_of_bd(fp, pcbnew.F_CrtYd), 2, dir=(0, 0, 1))
    base -= fp_loc("SW1") * b.Box(2.5, 4, 2, align=(MID, HIGH, LOW))
    base -= fp_loc("D1") * b.Cone(0, 5, 10, align=(MID, MID, LOW))
    for i in range(1, 5):
        base -= fp_loc(f"H{i}") * b.Cylinder(3.3 / 2, 3, align=(MID, MID, LOW))
    return base

# top = gen_top()
# b.export_step(top, "top.step")
# show_object(top)

bot = gen_bot()
b.export_step(bot, "bot.step")
show_object(bot)
