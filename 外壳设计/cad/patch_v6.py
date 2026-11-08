# -*- coding: utf-8 -*-
"""Rev F 补丁：四边开口统一平齐 + 插线余量 + 核心板直焊说明"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))

def patch(fname, pairs, globals_=()):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    if "Rev F" in s and "I2C-GROUPS" not in s and "I2C_GROUPS" not in s:
        print(f"[skip] {fname} 已是 Rev F")
        return
    miss = []
    for i, (old, new) in enumerate(pairs, 1):
        if old not in s:
            miss.append((i, old[:60]))
            continue
        s = s.replace(old, new, 1)
    for old, new in globals_:
        s = s.replace(old, new)
    io.open(p, "w", encoding="utf-8").write(s)
    print(f"[ok] {fname}: {len(pairs)-len(miss)}/{len(pairs)} 处精确替换"
          + (f"，未命中 {miss}" if miss else ""))

# ==================== build_v2.py ====================
patch("build_v2.py", [
 ('''"""ESP32S3_LCD 全覆盖不透明外壳 Rev E —— 生成 STL / DXF / 报价 / 下单说明

结构：上盖（完整不透明顶板 + 四周侧壁 + 4 螺丝柱，仅开显示区窗口 + Φ4 复位孔）
      底座（平板 + 4 支撑台 + 4 沉孔）
      上边侧壁开 27.00 宽天线让位窗（Z 8.0~14.2），顶板不镂空
"""''',
  '''"""ESP32S3_LCD 全覆盖不透明外壳 Rev F —— 生成 STL / DXF / 报价 / 下单说明

结构：上盖（完整不透明顶板 + 四周侧壁 + 4 螺丝柱，仅开显示区窗口 + Φ4 复位孔）
      底座（平板 + 4 支撑台 + 4 沉孔）
      Rev F：四边所有对外开口统一开口带 Z 4.00~14.20，上下沿完全平齐；
      天线让位窗 27.00 与 I2C 合并宽窗同高；双 Type-C / 5V / XH-5P 均按
      带壳插头 + 线材外径留余量。顶板保持完整不镂空。
"""'''),
 ("    # Rev E：顶板完整无镂空；天线让位只切上边侧壁（止于顶板内表面 Z=14.2）",
  "    # Rev F：顶板完整无镂空；天线让位与所有接口窗统一 Z 开口带（止于顶板内表面）"),
 ('''top_segs = [(cx - P.I2C_SLOT_W/2, cx + P.I2C_SLOT_W/2, 4.6, 12.8, f"I2C{i}")
            for i, cx in enumerate(P.I2C_X, 1)]
top_segs += [(P.ANT_X0, P.ANT_X1, P.ANT_SLOT_Z0, P.ANT_SLOT_Z1, "ANT 让位窗")]
bot_segs = [(40.0, 66.0, 7.6, 12.8, "2x Type-C")]
rgt_segs = [(15.3, 25.3, 4.6, 8.8, "5V Type-C"), (35.0, 51.5, 4.6, 12.8, "XH-5P")]''',
  '''top_segs = [(b[0], b[2], z0, z1, n) for n, b, z0, z1, d in P.SLOTS
            if n.startswith("I2C")]
top_segs += [(P.ANT_X0, P.ANT_X1, P.ANT_SLOT_Z0, P.ANT_SLOT_Z1, "ANT 让位窗")]
bot_segs = [(b[0], b[2], z0, z1, n) for n, b, z0, z1, d in P.SLOTS if b[1] < 0]
rgt_segs = [(b[1], b[3], z0, z1, n) for n, b, z0, z1, d in P.SLOTS
            if b[0] > P.W - P.T_WALL - 1]'''),
 ('T(m, "上边侧壁：27.00 天线让位窗(Z 8.0~14.2) / 4x I2C；下边 双 Type-C；右边 5V + XH-5P",',
  'T(m, "四边统一开口带 Z 4.00~14.20：天线 27.00 与 I2C 宽窗平齐；双 Type-C 36.00；5V 18.00 / XH-5P 23.00",'),
 ('    "3. 顶板完整封闭不镂空；上边侧壁开 27.00 宽天线让位窗（Z 8.0~14.2），天线端穿出壳外。",',
  '    "3. 顶板完整封闭不镂空；四边开口统一 Z 4.00~14.20，天线让位窗与 I2C 窗上下沿平齐。",'),
 ('''    "5. 上边：4x I2C XH2.54-4P 开口 + 顶板 Φ4 复位孔（细针按压）+ 天线侧壁让位窗。",
    "   下边：ESP32 系统板双 Type-C 共用长窗。右边：5V Type-C 输出 + XH2.54-5P。",''',
  '''    "5. 上边：2 段 I2C 合并宽窗（4 个 XH2.54-4P，座距 12.96）+ Φ4 复位孔 + 27.00 天线让位窗。",
    "   下边：ESP32 核心板（直焊）双 Type-C 共用 36.00 窗；右边：5V 18.00 + XH-5P 23.00。",
    "   所有窗口按带壳插头宽 14~16 / 线材 Ø3~5 留余量，非按母座贴边开孔。",'''),
 ('note = f"""ESP32-S3 LCD 全覆盖显示屏外壳 Rev E —— 淘宝打样下单说明',
  'note = f"""ESP32-S3 LCD 全覆盖显示屏外壳 Rev F —— 淘宝打样下单说明'),
 ('''  两件 3D 打印外壳，外形 105.20 x 67.00 x 16.00 mm，整套约 {vol_all:.0f} cm3。
  上盖顶板厚 1.8、侧壁厚 1.6、总高 16.0；中央显示窗 {P.WIN_A_W:.2f} x {P.WIN_A_H:.2f} mm
  （四角 R1.5），顶板完整无镂空，仅显示窗 + Φ4 复位孔；上边侧壁有 27.0 mm 宽
  天线让位窗（Z 8.0~14.2）供 ESP32 天线端伸出壳外，四边另有接口开窗（见 PDF 展开图）。''',
  '''  两件 3D 打印外壳，外形 105.20 x 67.00 x 16.00 mm，整套约 {vol_all:.0f} cm3。
  上盖顶板厚 1.8、侧壁厚 1.6、总高 16.0；中央显示窗 {P.WIN_A_W:.2f} x {P.WIN_A_H:.2f} mm
  （四角 R1.5），顶板完整无镂空，仅显示窗 + Φ4 复位孔；四边侧壁统一开口带
  Z 4.00~14.20（天线让位窗 27.00 与 I2C 合并宽窗平齐），窗口已按带壳插头与线材留余量，
  请勿擅自缩小窗口；顶板天线区不要开洞、不要加支撑。'''),
 ('''【五、接口开窗对应（PCB 左旋 90°、天线朝上的正视方位）】
  上边：侧壁天线让位窗 27.0 mm 宽（Z 8.0~14.2，顶板完整不镂空）
        + 顶板 Φ4 复位键孔（细针 / 加长键帽按压）+ 4 个 I2C 传感器 XH2.54-4P
  下边：ESP32 系统板自带 2 个 Type-C（UART / USB）共用 26 mm 长窗
  右边：5V Type-C 输出口（USB1）+ XH2.54-5P（CN3，窗口兼容 H2 3P / H3 2P）
  左边：封闭，无外部接口
  底部：4 个 M3 螺丝沉孔''',
  '''【五、接口开窗对应（PCB 左旋 90°、天线朝上的正视方位）】
  ★ 四边所有开口统一 Z 4.00~14.20（下沿留 1.60 实壁、上沿齐平顶板内表面），
    天线让位窗与 I2C 插座窗完全平齐；窗口按「带壳插头 + 线材外径 + 插拔空间」留余量。
  上边：天线让位窗 27.00 宽（39.10~66.10）+ 2 段 I2C 合并宽窗
        （12.00~37.10 / 68.10~93.00，各覆盖 2 个 XH2.54-4P，座中心距仅 12.96
         故不再各开 12mm 小窗；段间各留 2.00 加强筋）+ 顶板 Φ4 复位键孔
  下边：ESP32 核心板（直接焊在 PCB 上）自带 2 个 Type-C（UART / USB）
        共用 36.00 宽窗（34.00~70.00，原 26.00 太窄）
  右边：5V Type-C 18.00 宽窗（11.00~29.00，原 10.00）
        + XH2.54-5P 23.00 宽窗（32.00~55.00，原 16.50，兼容 H2 3P / H3 2P）
  左边：封闭，无外部接口
  底部：4 个 M3 螺丝沉孔
  【余量依据】XH2.54 带扣插头约 13~15 宽、线束出口需 8~10 高；Type-C 线端注塑壳
  约 12~16 宽 x 6~8 厚、线材 Ø3~5，折弯另需 3~5。开口带 10.20 高、各窗宽度
  均含上述余量；打样前建议拿实际线材比一下，若仍紧可改 params_v2.py 加宽。'''),
 ('''  注意：塑料顶板仍覆盖天线内段上方约 1.1mm 间隙，介电加载可能让谐振略下偏；
  装好后对比悬空 / 吸铁板的 WiFi RSSI，若掉 >3dB 可把天线端再多伸出 5~10 mm，
  或让商家把顶板天线区内表面减薄 0.8 mm（外表面仍平整无洞）。''',
  '''  核心板为直接焊接（板间距约 2.5、板厚 1.6），天线铜层约 Z 8~9，顶板内表面
  Z 14.2 与天线之间约 5mm 塑料间隙，介电加载比排母插装版本更弱；
  装好后对比悬空 / 吸铁板的 WiFi RSSI，若掉 >3dB 可把天线端再多伸出 5~10 mm，
  或把顶板天线区内表面减薄 0.8 mm（外表面仍平整无洞）。'''),
 ('    REV="E",', '    REV="F",'),
 ('''    I2C_X=P.I2C_X, I2C_SLOT_W=P.I2C_SLOT_W,''',
  '''    I2C_X=P.I2C_X, I2C_SLOT_W=P.I2C_SLOT_W,
    OPEN_Z0=P.OPEN_Z0, OPEN_Z1=P.OPEN_Z1, RIB_W=P.RIB_W,
    I2C_GROUPS=[list(g) for g in P.I2C_GROUPS],
    DUAL_USBC=[P.DUAL_USBC_X0, P.DUAL_USBC_X1],
    RIGHT_SLOTS=[[P.RIGHT_5V_Y0, P.RIGHT_5V_Y1],
                 [P.RIGHT_XH_Y0, P.RIGHT_XH_Y1]],'''),
], globals_=[("Rev E", "Rev F"), ("ESP32S3-LCD-EN-E", "ESP32S3-LCD-EN-F")])


# ==================== make_pdf_v2.py ====================
patch("make_pdf_v2.py", [
 ('''    ("上边", "侧壁让位窗 27.00（Z 8.0~14.2）+ Φ4 复位孔 + 4× I2C", REDC),
    ("下边", "ESP32 系统板双 Type-C 共用 26.00 长窗", INK),
    ("右边", "5V Type-C 输出 + XH2.54-5P（兼容 2P/3P）", INK),''',
  '''    ("上边", "统一 Z 4.00~14.20：27.00 天线窗与 I2C 宽窗平齐", REDC),
    ("下边", "核心板直焊，双 Type-C 共用 36.00 宽窗", INK),
    ("右边", "5V Type-C 18.00 + XH2.54-5P 23.00 宽窗", INK),'''),
 ('    "顶板完整无镂空：仅显示窗 + Φ4 复位孔；侧壁留 27.00 让位窗",',
  '    "顶板完整无镂空：仅显示窗 + Φ4 复位孔；四边开口统一 Z 4.00~14.20",'),
 ('    "4× Φ7 螺丝柱，内底孔 Φ2.6（M3 自攻，盲孔）",',
  '    "插线余量：窗口按带壳插头 + 线材 Ø3~5 留，不按母座贴边",'),
 ('''top_segs = []
for i, cx in enumerate(G["I2C_X"], 1):
    top_segs.append((cx - G["I2C_SLOT_W"] / 2, cx + G["I2C_SLOT_W"] / 2,
                     4.6, 12.8, f"I2C{i}", GREEN))
top_segs.append((ANT[0], ANT[2], G["ANT_SLOT_Z0"], G["ANT_SLOT_Z1"],
                 "ANT 侧壁让位窗", REDC))
side(158, "上边（天线侧）展开 1:1  —  4× I2C / 复位 / 天线", W, top_segs,
     "4 个 12.00 宽 I2C 窗（Z 4.6~12.8）；天线让位窗 27.00 宽仅开 Z 8.0~14.2，顶板与下段侧壁完整。")
side(126, "下边（双 Type-C）展开 1:1", W,
     [(40.0, 66.0, 7.6, 12.8, "2× Type-C 共用长窗 26.00", GREEN)],
     "对应 ESP32-S3-DevKitC 自带 UART / USB 两个 Type-C（中心约 46.5 / 58.5）；长窗兼容位置偏差。")
side(94, "右边（5V / XH5P）展开 1:1", H,
     [(15.3, 25.3, 4.6, 8.8, "5V Type-C", GREEN),
      (35.0, 51.5, 4.6, 12.8, "XH2.54-5P", GREEN)],
     "5V Type-C 输出口 (USB1)；XH2.54-5P (CN3) 长窗同时兼容 H2 3P / H3 2P 端子。")''',
  '''OZ0, OZ1 = G["OPEN_Z0"], G["OPEN_Z1"]
GL, GR = G["I2C_GROUPS"]
DU = G["DUAL_USBC"]
R5V, RXV = G["RIGHT_SLOTS"]
top_segs = [(GL[0], GL[1], OZ0, OZ1, "I2C 合并窗 25.10", GREEN),
            (ANT[0], ANT[2], OZ0, OZ1, "ANT 让位窗 27.00", REDC),
            (GR[0], GR[1], OZ0, OZ1, "I2C 合并窗 24.90", GREEN)]
side(158, "上边（天线侧）展开 1:1  —  统一开口带 Z 4.00~14.20", W, top_segs,
     "4 个 XH2.54-4P 座中心距仅 12.96，单开 12 窗放不下带壳插头 → 左右各 2 座合并宽窗；"
     "天线让位窗与 I2C 窗上下沿完全平齐，段间各留 2.00 加强筋。")
side(126, "下边（双 Type-C）展开 1:1", W,
     [(DU[0], DU[1], OZ0, OZ1, "2× Type-C 共用窗 36.00", GREEN)],
     "核心板直接焊在 PCB 上，UART / USB 两口中心约 46.5 / 58.5；原 26.00 窗偏窄，"
     "加宽到 36.00 给线端注塑壳 + 线材折弯留余量。")
side(94, "右边（5V / XH5P）展开 1:1", H,
     [(R5V[0], R5V[1], OZ0, OZ1, "5V Type-C 18.00", GREEN),
      (RXV[0], RXV[1], OZ0, OZ1, "XH2.54-5P 23.00", GREEN)],
     "5V Type-C 输出口 (USB1) 由 10.00 加宽到 18.00；XH2.54-5P (CN3) 由 16.50 加宽到 23.00，"
     "两窗之间留 3.00 实壁；均兼容 H2 3P / H3 2P 端子。")'''),
 ('''    "2. LCD 插 PCB 排座；ESP32 天线端朝上边让位窗穿出",''',
  '''    "2. LCD 插 PCB 排座；ESP32 核心板直焊，天线端朝上边让位窗",'''),
 ('''    "· 顶板完整无镂空；天线内段上方留 1.1mm，RSSI 偏低可再外移",''',
  '''    "· 顶板完整无镂空；四边窗口平齐且已留线材余量，勿缩小",'''),
 ('T("ESP32-S3-Metric.pdf：系统板 63.39×27.94，插 U1/U2，天线端经让位窗外露", IX, 18, 6.1, GRAY)',
  'T("ESP32-S3-Metric.pdf：系统板 63.39×27.94 直焊 U1/U2；开口带 Z 4.00~14.20", IX, 18, 6.1, GRAY)'),
 ('FOOTER("注：Rev E 顶板完整无镂空，天线让位仅在上边侧壁；展开图横轴为边长、纵轴为侧壁高 11.80。")',
  'FOOTER("注：Rev F 四边开口统一 Z 4.00~14.20 完全平齐，均含插线余量；顶板完整无镂空。")'),
], globals_=[("Rev E", "Rev F"), ("ESP32S3-LCD-EN-E", "ESP32S3-LCD-EN-F")])


# ==================== make_views.py ====================
patch("make_views.py", [
 ('''# 4 个 I2C 窗投影
for i, cx in enumerate(G["I2C_X"], 1):
    RECT(FX + (cx - G["I2C_SLOT_W"] / 2) * S, FY + (H - 1.6) * S,
         G["I2C_SLOT_W"] * S, 1.6 * S, GREEN, 0.45, fill=GRNF)''',
  '''# 2 段 I2C 合并宽窗投影（4 个座，段间 2.00 加强筋）
for a, b in G["I2C_GROUPS"]:
    RECT(FX + a * S, FY + (H - 1.6) * S, (b - a) * S, 1.6 * S,
         GREEN, 0.45, fill=GRNF)'''),
 ('''TC("27.00 天线让位窗", TX + (AX0 + AX1) / 2 * S,
   TY + (AZ0 + AZ1) / 2 * S - 1.8, 6, BLUE)
T("Z 8.0~14.2", TX + AX0 * S + 1, TY + AZ1 * S - 4.5, 5.5, BLUE)
T("4 × I2C 12.00 宽", TX + 13, TY + TB * S + 2, 5.8, GREEN)''',
  '''TC("27.00 天线让位窗", TX + (AX0 + AX1) / 2 * S,
   TY + (AZ0 + AZ1) / 2 * S - 1.8, 6, BLUE)
T(f"统一开口带 Z {AZ0:.2f}~{AZ1:.2f}", TX + AX0 * S + 1,
  TY + AZ1 * S - 4.5, 5.5, BLUE)
T("2 段 I2C 合并宽窗（4 座）", TX + 13, TY + TB * S + 2, 5.8, GREEN)'''),
 ('    TC("双 Type-C 长窗 26.00", BX + (x0 + x1) / 2 * S,',
  '    TC(f"双 Type-C 窗 {x1-x0:.2f}", BX + (x0 + x1) / 2 * S,'),
 ('    TC("10.00" if "5V" in n else "16.50", RX + (y0 + y1) / 2 * S,',
  '    TC(f"{y1-y0:.2f}", RX + (y0 + y1) / 2 * S,'),
 ('T("5V Type-C", RX + 15.3 * S + 1, RY + TH + 3, 5.6, GREEN)',
  'T("5V Type-C", RX + G["RIGHT_SLOTS"][0][0] * S + 1, RY + TH + 3, 5.6, GREEN)'),
 ('T("XH2.54-5P", RX + 35.0 * S + 1, RY + TH + 3, 5.6, GREEN)',
  'T("XH2.54-5P", RX + G["RIGHT_SLOTS"][1][0] * S + 1, RY + TH + 3, 5.6, GREEN)'),
 ('''    (f"侧壁让位窗 {AX1-AX0:.2f} 宽，Z {AZ0:.1f}~{AZ1:.1f}", BLUE),''',
  '''    (f"统一开口带 Z {AZ0:.2f}~{AZ1:.2f}（四边平齐）", BLUE),
    (f"上边：天线 {AX1-AX0:.2f} + I2C 合并宽窗 25.10/24.90", BLUE),
    (f"下边双 Type-C {G['DUAL_USBC'][1]-G['DUAL_USBC'][0]:.2f}；右边 18.00/23.00", GREEN),'''),
 ('''    "② 上视图 = 从天线侧看：顶板整段连续，4 个 I2C 窗与 27.00",
    "   天线让位窗都在侧壁，顶板与下段侧壁不被切穿。",
    "④ 右视图 = 从右侧看：5V Type-C（10.00 宽）与 XH2.54-5P",
    "   （16.50 宽）两个侧壁开窗；③ 辅助下视图补双 Type-C。",''',
  '''    "② 上视图 = 从天线侧看：顶板整段连续；天线让位窗与 2 段",
    "   I2C 合并宽窗上下沿完全平齐（统一 Z 4.00~14.20）。",
    "④ 右视图 = 从右侧看：5V Type-C（18.00）与 XH2.54-5P（23.00）；",
    "   ③ 辅助下视图补双 Type-C 共用 36.00 窗；均含插线余量。",'''),
 ('''T("· 顶板完整但为塑料，天线内段上方约 1.1 mm 间隙；介电加载", JX, 68, 6.3, REDC)''',
  '''T("· 核心板直焊，天线铜层约 Z 8~9，顶板内表面 Z 14.2，塑料间隙", JX, 68, 6.3, REDC)'''),
 ('''T("  可能让 2.4 GHz 谐振略下偏，装好后对比悬空 / 吸铁板 RSSI。", JX, 62, 6.3, REDC)''',
  '''T("  约 5 mm，介电加载更弱；装好后对比悬空 / 吸铁板 RSSI。", JX, 62, 6.3, REDC)'''),
 ('''for i, cx in enumerate(G["I2C_X"], 1):
    dr(cx - G["I2C_SLOT_W"]/2, H - 1.6, cx + G["I2C_SLOT_W"]/2, H, "SLOT")''',
  '''for a, b in G["I2C_GROUPS"]:
    dr(a, H - 1.6, b, H, "SLOT")'''),
 ('''dt("I2C 窗 Z 4.6~12.8；天线让位窗 Z 8.0~14.2；顶板 Z 14.2~16.0 不切断", 0, SY0 - 18, 2.8)''',
  '''dt(f"四边统一开口带 Z {AZ0:.2f}~{AZ1:.2f}；天线与 I2C 窗平齐；顶板 Z 14.2~16.0 不切断", 0, SY0 - 18, 2.8)'''),
 ('''dt("③ 辅助下视图（接口侧 / -Yo）  1:1   双 Type-C 长窗 26.00", 0, BY0 + HT + 18, 3.4)''',
  '''dt("③ 辅助下视图（接口侧 / -Yo）  1:1   双 Type-C 共用窗 36.00", 0, BY0 + HT + 18, 3.4)'''),
 ('''dt("ESP32S3-LCD-EN-E-VIEW  Rev E  |  单位 mm  1:1  |  顶板完整无镂空",''',
  '''dt("ESP32S3-LCD-EN-F-VIEW  Rev F  |  单位 mm  1:1  |  四边开口平齐",'''),
], globals_=[("Rev E", "Rev F"), ("ESP32S3-LCD-EN-E-VIEW", "ESP32S3-LCD-EN-F-VIEW")])

print("patch_v6 done")
