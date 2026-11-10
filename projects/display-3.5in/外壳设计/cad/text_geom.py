# -*- coding: utf-8 -*-
"""上盖顶面「接口标注」的矢量字形（STL / STEP / DXF / PDF / 预览共用）。

用 matplotlib 自带的 DejaVuSans-Bold 把字符串转成带内孔的 shapely 多边形，
保证 5 份交付物（STL 实体 / STEP 实体 / DXF 轮廓 / PDF 图面 / 预览 PNG）
的字形、大小、位置完全一致；不需要商家或用户本机另装字体。

标注内容见 params_v2.TEXT_MARKS；字高、凸字高度见 params_v2.TEXT_SIZE / TEXT_RAISE。
"""
from matplotlib import font_manager
from matplotlib.textpath import TextPath
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

import params_v2 as P

_FP = font_manager.FontProperties(family="DejaVu Sans", weight="bold")
FONT_PATH = font_manager.findfont(_FP)


def _signed_area(pts):
    """环的有向面积：DejaVu/TrueType 外轮廓顺时针（负），内孔逆时针（正）。

    不能用「被几个环包含」判内外：O / P / e 这类圆盘形字母的外环代表点正好
    落在自己的内孔里，会被误判成孔而把整个字母丢掉（COM 会变成 CM）。
    """
    a = 0.0
    for i in range(len(pts) - 1):
        x1, y1 = pts[i][0], pts[i][1]
        x2, y2 = pts[i + 1][0], pts[i + 1][1]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def glyph(text):
    """把字符串转成 shapely 几何（含字母内孔），原点 = 文字 bbox 中心。"""
    tp = TextPath((0, 0), text, size=1.0,
                  prop=font_manager.FontProperties(fname=FONT_PATH))
    shells, holes = [], []
    for raw in tp.to_polygons():
        if len(raw) < 3:
            continue
        (holes if _signed_area(raw) > 0 else shells).append(Polygon(raw))
    if not shells:
        raise ValueError("empty glyph: %r" % text)

    parts = [Polygon(list(sh.exterior.coords),
                     [list(h.exterior.coords) for h in holes if sh.contains(h)])
             for sh in shells]
    g = unary_union(parts)

    # size=1 时大写字母高度约 0.729 em，按目标字高归一化
    cap = max(sh.bounds[3] for sh in shells)
    s = P.TEXT_SIZE / cap
    g = affinity.scale(g, s, s, origin=(0, 0))
    x0, y0, x1, y1 = g.bounds
    return affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)


def mark_polys(text, cx, cy, rot=0.0):
    """返回该标注的全部 Polygon（每个字母一个，内孔保留）。"""
    g = glyph(text)
    if rot:
        g = affinity.rotate(g, rot, origin=(0, 0), use_radians=False)
    g = affinity.translate(g, cx, cy)
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]


def all_marks():
    """[(文字, 中心X, 中心Y, 旋转角, [Polygon...], bbox)]"""
    out = []
    for text, cx, cy, rot in P.TEXT_MARKS:
        polys = mark_polys(text, cx, cy, rot)
        b = unary_union(polys).bounds
        out.append((text, cx, cy, rot, polys, tuple(round(v, 3) for v in b)))
    return out


def mark_z0():
    """凸字底面嵌入顶板 0.05，避免与顶板共面导致布尔失败。"""
    return P.H_TOTAL - P.TEXT_EMBED


def mark_z1():
    return P.H_TOTAL + P.TEXT_RAISE


def diamond_pin_points(center, other, d=None, w=None, steps=24):
    """菱形定位销截面点列（A 方案防过约束）。

    圆销 Φd 沿「两销连线」方向削扁到宽 w，垂直连线方向仍保持 Φd 接触定位；
    这样打印收缩造成的两销中心距误差全部由该方向的间隙吸收，不会顶住 PCB 孔。
    返回 (x, y) 点列，闭合，供 shapely / cadquery / DXF 共用。
    """
    import math
    d = P.LOCATOR_D if d is None else d
    w = P.DIAMOND_W if w is None else w
    r = d / 2.0
    hw = w / 2.0
    h = math.sqrt(r * r - hw * hw)
    ang = math.atan2(other[1] - center[1], other[0] - center[0])
    ca, sa = math.cos(ang), math.sin(ang)

    a = math.atan2(h, hw)
    upper = [a + (math.pi - 2 * a) * i / steps for i in range(steps + 1)]
    lower = [math.pi + a + (math.pi - 2 * a) * i / steps
             for i in range(steps + 1)]
    local = [(r * math.cos(t), r * math.sin(t)) for t in upper]
    local += [(r * math.cos(t), r * math.sin(t)) for t in lower]
    return [(center[0] + u * ca - v * sa,
             center[1] + u * sa + v * ca) for u, v in local]
