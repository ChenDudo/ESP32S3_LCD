# -*- coding: utf-8 -*-
"""Rev E 批量修订：顶板取消 U 形镂空，改为侧壁天线让位窗；版本升 E。"""
import io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def patch(fname, pairs, globals_=()):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    # 幂等：已打过补丁的文件直接跳过，便于中断后续跑
    if fname == "params_v2.py" and "Rev E 相对 Rev D 的修正" in s:
        print("SKIP params_v2.py (already patched)")
        return
    if fname == "build_v2.py" and "ant_slot = prism" in s:
        print("SKIP build_v2.py (already patched)")
        return
    if fname == "make_pdf_v2.py" and "侧壁让位窗（顶板完整）" in s:
        print("SKIP make_pdf_v2.py (already patched)")
        return
    for i, (old, new) in enumerate(pairs, 1):
        n = s.count(old)
        if n != 1:
            print(f"!! {fname} pair#{i}: hit {n} (expect 1) :: {old[:60]!r}")
            sys.exit(1)
        s = s.replace(old, new)
    for old, new in globals_:
        n = s.count(old)
        if n == 0:
            print(f"!! {fname} global {old!r}: hit 0")
            sys.exit(1)
        s = s.replace(old, new)
        print(f"   global {old!r} -> {new!r}  x{n}")
    io.open(p, "w", encoding="utf-8").write(s)
    print(f"OK {fname}: {len(pairs)} exact + {len(globals_)} global replacements")


# ==================== params_v2.py ====================
patch("params_v2.py", [
    ('''"""ESP32S3_LCD 全覆盖外壳 Rev D —— 统一设计参数 (单位 mm)

Rev D 相对 Rev C 的修正（依据用户 11-07 实测与重新核对）：''',
     '''"""ESP32S3_LCD 全覆盖外壳 Rev E —— 统一设计参数 (单位 mm)

Rev E 相对 Rev D 的修正（用户 11-08 要求）：
  ★【顶板不再镂空】取消上边 U 形天线敞口（原切除体 z=-1~17 把顶板一起挖穿）。
    顶板改为完整封闭、不透明全覆盖，仅保留显示窗 + Φ4.0 复位键孔。
    天线 / ESP32 模组端部改由【上边侧壁矩形让位窗】伸出壳外
    （27.00 宽，Z 8.0~14.2，止于顶板内表面），顶板本身不开洞。
    原「天线段顶板加强筋」取消（顶板完整，无需加强）。
  ★ 新增独立 A3 三视图 PDF / DXF（正视图 / 上视图 / 右视图 + 辅助下视图）。

Rev D 相对 Rev C 的修正（依据用户 11-07 实测与重新核对）：'''),

    ('''# ---------------- 天线敞口（上边 / Yo 大端） ----------------
# ESP32-S3-Metric.pdf：开发板 63.39 长 × 27.94 宽，天线在板顶端且需伸出 PCB 边。
# 上边 4 个 I2C 槽占 Xo 12.35~37.31 与 67.90~92.86，中间空档 37.31~67.90 = 30.59。
# 取 27.00 宽居中，两侧各留约 1.8 mm 实壁；天线本体（约 15~20 宽）完全外露。
ANT_X0, ANT_X1 = 39.1, 66.1   # 27.0 宽
ANT_Y0 = 59.6                 # 保留显示区压边：窗口上沿 57.30 到此留 2.30
RIB_Y1 = 59.0                 # 天线段顶板加强筋
RIB_Z0, RIB_Z1 = Z_TOP_IN - 1.6, Z_TOP_IN''',
     '''# ---------------- 天线让位（上边 / Yo 大端）—— Rev E：顶板不镂空 ----------------
# ESP32-S3-Metric.pdf：开发板 63.39 长 × 27.94 宽，天线在板顶端且需伸出 PCB 边。
# 上边 4 个 I2C 槽占 Xo 12.35~37.31 与 67.90~92.86，中间空档 37.31~67.90 = 30.59。
# 取 27.00 宽居中，两侧各留约 1.8 mm 实壁。
# 【Rev E】顶板完整封闭，不切 U 形敞口；只在上边侧壁开让位窗让天线端伸出壳外。
ANT_X0, ANT_X1 = 39.1, 66.1             # 让位窗宽 27.00
ANT_Y0 = H - T_WALL - 0.2               # 65.20：让位窗在俯视图上的 y 起点（仅侧壁）
ANT_SLOT_Z0, ANT_SLOT_Z1 = 8.0, Z_TOP_IN  # 侧壁让位窗 Z 8.0~14.2，不触及顶板
# 复位键孔：SW1 在 (40.59, 62.42)，顶板开 Φ4 小孔，细针 / 加长键帽按压
RESET_POS = (40.59, 62.42)
RESET_HOLE_D = 4.0'''),

    ("  4. 沿用 Rev C：取消磁吸、天线敞口 27.0 mm、ESP32-S3-Metric.pdf 63.39×27.94 mm、",
     "  4. 沿用 Rev C：取消磁吸、天线让位窗 27.0 mm、ESP32-S3-Metric.pdf 63.39×27.94 mm、"),
])


# ==================== build_v2.py ====================
patch("build_v2.py", [
    ('''"""ESP32S3_LCD 全覆盖不透明外壳 Rev D —— 生成 STL / DXF / 报价 / 下单说明

结构：上盖（不透明顶板 + 四周侧壁 + 4 螺丝柱，仅开显示区窗口）
      底座（平板 + 4 支撑台 + 4 沉孔）
      天线侧整段 U 形敞口，天线完全在壳外
"""''',
     '''"""ESP32S3_LCD 全覆盖不透明外壳 Rev E —— 生成 STL / DXF / 报价 / 下单说明

结构：上盖（完整不透明顶板 + 四周侧壁 + 4 螺丝柱，仅开显示区窗口 + Φ4 复位孔）
      底座（平板 + 4 支撑台 + 4 沉孔）
      上边侧壁开 27.00 宽天线让位窗（Z 8.0~14.2），顶板不镂空
"""'''),

    ('''    ant = prism(box(P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H + 4.0), -1.0, P.H_TOTAL + 1.0)
    cut = [outer, cavity, window, ant]''',
     '''    # Rev E：顶板完整无镂空；天线让位只切上边侧壁（止于顶板内表面 Z=14.2）
    ant_slot = prism(box(P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H + 2.0),
                     P.ANT_SLOT_Z0, P.ANT_SLOT_Z1)
    reset = cyl(P.RESET_HOLE_D / 2, P.Z_TOP_IN - 0.2, P.H_TOTAL + 0.5,
                *P.RESET_POS)
    cut = [outer, cavity, window, ant_slot, reset]'''),

    ('''    # 天线敞口段顶板加强筋
    rib = prism(box(P.ANT_X0, P.WIN_CY + win_h / 2, P.ANT_X1, P.RIB_Y1),
                P.RIB_Z0, P.RIB_Z1)
    return bunion([shell] + posts + [rib])''',
     '''    # 顶板完整封闭，无需加强筋
    return bunion([shell] + posts)'''),

    ('''# 天线敞口
RECT(m, P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H, "ANT")''',
     '''# 侧壁天线让位窗（俯视投影为靠上边窄条；顶板完整不开洞）
RECT(m, P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H, "ANT")
# 顶板复位键孔
m.add_circle(P.RESET_POS, P.RESET_HOLE_D / 2, dxfattribs={"layer": "HOLE"})
T(m, "复位孔 Φ4.0", P.RESET_POS[0] + 3, P.RESET_POS[1] + 1, 1.8, "NOTE")'''),

    ('''DIMH(m, P.ANT_X0, P.ANT_X1, P.H, f"{P.ANT_X1-P.ANT_X0:.2f} 天线敞口", 15)''',
     '''DIMH(m, P.ANT_X0, P.ANT_X1, P.H, f"{P.ANT_X1-P.ANT_X0:.2f} 侧壁让位窗(顶板不开)", 15)'''),

    ('''T(m, "ANT 天线敞口：顶板+侧壁全切，天线完全在壳外", 0, P.H + 22, 3.0, "ANT")
T(m, "上边 4x I2C 口 / 复位键(敞口内) / 天线；下边 双 Type-C；右边 5V Type-C + XH2.54-5P",
  0, P.H + 27, 2.8, "ANT")''',
     '''T(m, "顶板完整封闭、无镂空；仅显示窗 + Φ4 复位孔", 0, P.H + 22, 3.0, "ANT")
T(m, "上边侧壁：27.00 天线让位窗(Z 8.0~14.2) / 4x I2C；下边 双 Type-C；右边 5V + XH-5P",
  0, P.H + 27, 2.8, "ANT")'''),

    ('''top_segs += [(P.ANT_X0, P.ANT_X1, P.T_BASE, P.Z_TOP_IN, "ANT")]''',
     '''top_segs += [(P.ANT_X0, P.ANT_X1, P.ANT_SLOT_Z0, P.ANT_SLOT_Z1, "ANT 让位窗")]'''),

    ('''RECT(m3, P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H, "ANT")''',
     '''RECT(m3, P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H, "ANT")
m3.add_circle(P.RESET_POS, P.RESET_HOLE_D / 2, dxfattribs={"layer": "HOLE"})'''),

    ('''    "3. 天线敞口 27.00 宽，位于上边（PCB 左旋后天线的位置）；天线及 ESP32 模组端部完全在壳外。",''',
     '''    "3. 顶板完整封闭不镂空；上边侧壁开 27.00 宽天线让位窗（Z 8.0~14.2），天线端穿出壳外。",'''),

    ('''    "5. 上边：4x I2C XH2.54-4P 开口 + 复位（位于天线敞口内，直接可按压）。",''',
     '''    "5. 上边：4x I2C XH2.54-4P 开口 + 顶板 Φ4 复位孔（细针按压）+ 天线侧壁让位窗。",'''),

    ('''  （四角 R1.5），上边有 27.0 mm 宽天线敞口，四边有接口开窗（见 PDF 展开图）。''',
     '''  （四角 R1.5），顶板完整无镂空，仅显示窗 + Φ4 复位孔；上边侧壁有 27.0 mm 宽
  天线让位窗（Z 8.0~14.2）供 ESP32 天线端伸出壳外，四边另有接口开窗（见 PDF 展开图）。'''),

    ('''  2. LCD 屏插 PCB 排座；ESP32 系统板焊/插在 PCB 上，天线端朝【上边敞口】并伸到壳外。''',
     '''  2. LCD 屏插 PCB 排座；ESP32 系统板焊/插在 PCB 上，天线端对准【上边侧壁让位窗】
     并穿出壳外（顶板完整盖住，不包住天线外露段）。'''),

    ('''  上边：天线敞口 27.0 mm + 复位键（在敞口内，可直接按）+ 4 个 I2C 传感器 XH2.54-4P''',
     '''  上边：侧壁天线让位窗 27.0 mm 宽（Z 8.0~14.2，顶板完整不镂空）
        + 顶板 Φ4 复位键孔（细针 / 加长键帽按压）+ 4 个 I2C 传感器 XH2.54-4P'''),

    ('''【六、天线净空】
  天线及模组端部完全在敞口之外，壳体是绝缘塑料，不屏蔽。
  4 个螺丝柱距天线中心均 >45 mm，远超 2.4GHz 近场 20 mm。
  接线与安装时避免让整块金属背板贴近天线端，建议天线端朝外或悬出安装面边缘。''',
     '''【六、天线净空】
  顶板完整封闭、不镂空；天线及模组端部从上边侧壁让位窗穿出，外露段不被壳体包住。
  壳体是绝缘塑料不屏蔽；4 个螺丝柱距天线中心均 >45 mm，远超 2.4GHz 近场 20 mm。
  注意：塑料顶板仍覆盖天线内段上方约 1.1mm 间隙，介电加载可能让谐振略下偏；
  装好后对比悬空 / 吸铁板的 WiFi RSSI，若掉 >3dB 可把天线端再多伸出 5~10 mm，
  或让商家把顶板天线区内表面减薄 0.8 mm（外表面仍平整无洞）。
  接线与安装时避免整块金属背板贴近天线端，建议天线端朝外或悬出安装面边缘。'''),

    ('''  ESP32S3_LCD_全覆盖外壳_工程图.pdf             3 页 A4，可直接发给商家''',
     '''  ESP32S3_LCD_全覆盖外壳_工程图.pdf             3 页 A4，可直接发给商家
  ESP32S3_LCD_全覆盖外壳_三视图.pdf             A3 三视图 + 辅助下视图（重点看这页）
  ESP32S3_LCD_全覆盖外壳_三视图.dxf             1:1 可编辑三视图'''),

    ('''    ANT=[P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H],''',
     '''    ANT=[P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H],
    ANT_SLOT_Z0=P.ANT_SLOT_Z0, ANT_SLOT_Z1=P.ANT_SLOT_Z1,
    RESET_POS=list(P.RESET_POS), RESET_HOLE_D=P.RESET_HOLE_D,
    REV="E",'''),
], globals_=[("Rev D", "Rev E")])


# ==================== make_pdf_v2.py ====================
patch("make_pdf_v2.py", [
    ('''HEADER("页 1  上盖俯视图  ·  不透明全覆盖 / 仅开显示区窗口", 1)''',
     '''HEADER("页 1  上盖俯视图  ·  顶板完整无镂空 / 仅开显示区窗口", 1)'''),

    ('''# 天线敞口
ax0, ay0, ax1, ay1 = ANT
RECT(P(ax0, ay0)[0], P(ax0, ay0)[1], ax1 - ax0, ay1 - ay0,
     REDC, 0.7, fill=HexColor("#fdeceb"), dash=(2, 1.2))
T("天线敞口", P(ax0 + 1.5, ay0 + 3)[0], P(ax0 + 1.5, ay0 + 3)[1], 6.5, REDC)''',
     '''# 侧壁天线让位窗（俯视投影为靠上边窄条；顶板完整不开洞）
ax0, ay0, ax1, ay1 = ANT
RECT(P(ax0, ay0)[0], P(ax0, ay0)[1], ax1 - ax0, ay1 - ay0,
     BLUE, 0.5, fill=HexColor("#e6eff9"), dash=(2, 1.2))
T("侧壁让位窗（顶板完整）", P(ax0 + 1.0, ay0 - 5.0)[0],
  P(ax0 + 1.0, ay0 - 5.0)[1], 5.8, BLUE)
# 顶板复位键孔
CIRCLE(*P(*G["RESET_POS"]), G["RESET_HOLE_D"] / 2, REDC, 0.6,
       fill=HexColor("#ffffff"))
T("Φ4 复位孔", P(G["RESET_POS"][0] + 3, G["RESET_POS"][1] - 2.2)[0],
  P(G["RESET_POS"][0] + 3, G["RESET_POS"][1] - 2.2)[1], 5.6, REDC)'''),

    ('''     f"{ax1-ax0:.2f} 天线敞口", REDC)''',
     '''     f"{ax1-ax0:.2f} 侧壁让位窗（顶板不开）", BLUE)'''),

    ('''    ("上边", "天线敞口 27.00 + 复位键 + 4× I2C (XH2.54-4P)", REDC),''',
     '''    ("上边", "侧壁让位窗 27.00（Z 8.0~14.2）+ Φ4 复位孔 + 4× I2C", REDC),'''),

    ('''    "天线敞口保留 2.30 顶板压边，下设 1.6 高加强筋",''',
     '''    "顶板完整无镂空：仅显示窗 + Φ4 复位孔；侧壁留 27.00 让位窗",'''),

    ('''RECT(IX + 55, 16, 6, 3, REDC, 0.4, fill=HexColor("#fdeceb")); T("天线敞口", IX + 63, 17, 6.4, INK)''',
     '''RECT(IX + 55, 16, 6, 3, BLUE, 0.4, fill=HexColor("#e6eff9")); T("侧壁让位窗", IX + 63, 17, 6.4, INK)'''),

    ('''top_segs.append((ANT[0], ANT[1], Z0, G["Z_TOP_IN"], "ANT 天线敞口", REDC))
side(158, "上边（天线侧）展开 1:1  —  4× I2C / 复位 / 天线", W, top_segs,
     "4 个 12.00 宽 XH2.54-4P 窗（Z 4.6~12.8）；复位键位于天线敞口内，直接可按压；天线整段不设侧壁。")''',
     '''top_segs.append((ANT[0], ANT[2], G["ANT_SLOT_Z0"], G["ANT_SLOT_Z1"],
                 "ANT 侧壁让位窗", REDC))
side(158, "上边（天线侧）展开 1:1  —  4× I2C / 复位 / 天线", W, top_segs,
     "4 个 12.00 宽 I2C 窗（Z 4.6~12.8）；天线让位窗 27.00 宽仅开 Z 8.0~14.2，顶板与下段侧壁完整。")'''),

    ('''T("壳体绝缘塑料不屏蔽；天线端朝外或悬出边缘", IX, 137, 6.4, REDC)''',
     '''T("顶板完整；天线端经侧壁让位窗伸出壳外", IX, 137, 6.4, REDC)'''),

    ('''    "2. LCD 插 PCB 排座；ESP32 焊/插上，天线端朝上边敞口",''',
     '''    "2. LCD 插 PCB 排座；ESP32 天线端朝上边让位窗穿出",'''),

    ('''    "· 天线敞口处顶板压边仅 2.30mm，已设 1.6 高加强筋",''',
     '''    "· 顶板完整无镂空；天线内段上方留 1.1mm，RSSI 偏低可再外移",'''),

    ('''T("ESP32-S3-Metric.pdf：系统板 63.39×27.94，插 U1/U2，天线端朝上外露", IX, 18, 6.1, GRAY)''',
     '''T("ESP32-S3-Metric.pdf：系统板 63.39×27.94，插 U1/U2，天线端经让位窗外露", IX, 18, 6.1, GRAY)'''),

    ('''FOOTER("注：侧壁展开图横轴为边长方向、纵轴为侧壁高 11.80（Z 2.4~14.2）；色块为需开通的窗口。")''',
     '''FOOTER("注：Rev E 顶板完整无镂空，天线让位仅在上边侧壁；展开图横轴为边长、纵轴为侧壁高 11.80。")'''),

    ('''    TR(f"Rev D   {page}/3   2026-11-07   单位 mm", 289, 200.5, 8, HexColor("#dce8f5"))''',
     '''    TR(f"Rev E   {page}/3   2026-11-08   单位 mm", 289, 200.5, 8, HexColor("#dce8f5"))'''),
], globals_=[("Rev D", "Rev E"), ("ESP32S3-LCD-EN-C", "ESP32S3-LCD-EN-E")])

print("ALL PATCHES APPLIED")
