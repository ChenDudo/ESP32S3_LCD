# -*- coding: utf-8 -*-
"""Rev G -> Rev H 批量修订（用户 11-08 实测确认 LCD A.A = 73.44 x 48.96）

改动：
  1. 删除 A / B 双版本上盖，只保留一个上盖（文件名去掉 A版/B版 后缀）。
  2. 窗口不再比 A.A 小，改为四周各放大 0.48 / 0.52 mm 让位：
     A.A 73.44 x 48.96 -> 窗口 74.40 x 50.00。
     取舍：宁可露出 <=0.5 mm 极窄黑边，也不切掉显示区边缘像素。
  3. 全部脚本、图纸文字、下单说明、FreeCAD 宏/工程同步为 Rev H。

每条替换都带出现次数断言；任一不匹配立即抛错，不会写出半改状态。
原 Rev G 副本已保存在项目仓库 D:/_0_gitwork/ESP32S3_LCD/外壳设计/ 。
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DELIV = os.path.join(HERE, "deliverables")


def apply(filename, blocks=(), globals_=(), forbid=()):
    """blocks: [(old, new, expected_count)] 精确替换；globals_: [(old,new)] 全量替换"""
    p = os.path.join(HERE, filename)
    with open(p, encoding="utf-8") as f:
        s = f.read()
    for old, new, cnt in blocks:
        n = s.count(old)
        if n == 0:
            raise RuntimeError("%s: NOT FOUND: %r" % (filename, old[:100]))
        if cnt is not None and n != cnt:
            raise RuntimeError("%s: expected %d got %d: %r"
                               % (filename, cnt, n, old[:100]))
        s = s.replace(old, new)
    for old, new in globals_:
        # 精确块可能已经消掉了该 token；此时跳过即可，最终由 forbid 兜底检查残留
        if old in s:
            s = s.replace(old, new)
    for token in forbid:
        if token in s:
            raise RuntimeError("%s: FORBIDDEN RESIDUE %r" % (filename, token))
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)
    print("patched", filename)


# ============================================================ params_v2.py
apply("params_v2.py", blocks=[
    ('"""ESP32S3_LCD 全覆盖外壳 Rev G —— 统一设计参数 (单位 mm)\n\n'
     'Rev G 相对 Rev F 的修正（用户 11-08 提供实物商品图）：',
     '"""ESP32S3_LCD 全覆盖外壳 Rev H —— 统一设计参数 (单位 mm)\n\n'
     'Rev H 相对 Rev G 的修正（用户 11-08 实测确认 LCD A.A）：\n'
     '  ★【删除 A/B 双版本】用户实测确认 LCD A.A（发光显示区）= 73.44 x 48.96 mm。\n'
     '    Rev G 的 A 版窗口 69.00x47.60（依据 EDA 封装可视框 70.46x49.07）比实测\n'
     '    A.A 窄 4.44 mm，B 版 72.00x47.60 仍窄 1.44 mm —— 两者都在切掉亮区边缘像素，\n'
     '    "压边"压的不是黑边而是显示内容。现废弃两版，只保留唯一上盖。\n'
     '  ★【窗口改为放大让位】窗口 74.40 x 50.00，四周各比 A.A 放大 0.48 / 0.52 mm，\n'
     '    用于吸收 3D 打印公差 +/-0.2~0.3、LCD 排针插装 + φ4 孔配 M3 的位置偏差、\n'
     '    以及偏心量推算误差。取舍：理想装配下四周露出 <=0.5 mm 极窄黑边，\n'
     '    但绝不遮挡显示内容；宁可露黑边，不可切亮区（用户 11-08 明确）。\n'
     '  ★ 偏心量 WIN_OFFSET_X=-2.75 仍是规格书 + 实物图推算值，未实测；\n'
     '    打样前量「亮区左缘→模块左缘 L」与「亮区右缘→模块右缘 R」，(L-R)/2 即该值。\n'
     '\n'
     'Rev G 相对 Rev F 的修正（用户 11-08 提供实物商品图）：', 1),

    ('LCD_AA_STD_W, LCD_AA_STD_L = 48.96, 73.44              # 3.5" 320x480 通用 AA',
     'LCD_AA_STD_W, LCD_AA_STD_L = 48.96, 73.44              # 3.5" 320x480 通用 AA\n'
     'LCD_AA_X, LCD_AA_Y = 73.44, 48.96                    # 用户实测确认；外壳坐标 X 长边 / Y 短边', 1),

    ('# ---------------- 显示区开窗（Rev G：偏心屏对位） ----------------\n'
     '# 模块长边沿 Xo、短边沿 Yo（屏幕正视、天线朝上）。\n'
     '# AA 中心相对模块/外壳中心偏左约 2.75 mm；短边方向对称，无 Y 偏移。\n'
     'WIN_OFFSET_X = -2.75                          # 负 = 显示区偏左（远离右侧宽黑边）\n'
     'WIN_CX = OX + PCB_PY / 2 + WIN_OFFSET_X      # 49.85（Rev F 为 52.60）\n'
     'WIN_CY = OY + PCB_PX / 2                     # 33.50，不变\n'
     'WIN_R = 1.5\n'
     'WIN_A_W, WIN_A_H = 69.00, 47.60    # A 版：保守压边（AA 73.44x48.96，压边 2.22/0.68）\n'
     'WIN_B_W, WIN_B_H = 72.00, 47.60    # B 版：贴 AA（压边 0.72/0.68）',
     '# ---------------- 显示区开窗（Rev H：单版本 + 按实测 A.A 放大让位） ----------------\n'
     '# 模块长边沿 Xo、短边沿 Yo（屏幕正视、天线朝上）。\n'
     '# AA 中心相对模块/外壳中心偏左约 2.75 mm；短边方向对称，无 Y 偏移。\n'
     'WIN_OFFSET_X = -2.75                          # 负 = 显示区偏左（远离右侧宽黑边）\n'
     'WIN_CX = OX + PCB_PY / 2 + WIN_OFFSET_X      # 49.85（Rev F 为 52.60）\n'
     'WIN_CY = OY + PCB_PX / 2                     # 33.50，不变\n'
     'WIN_R = 1.5\n'
     'WIN_W = 74.40                                 # 实测 A.A 73.44 + 2 x 0.48 让位\n'
     'WIN_H = 50.00                                 # 实测 A.A 48.96 + 2 x 0.52 让位\n'
     'WIN_CLEAR_X = (WIN_W - LCD_AA_X) / 2          # 0.48  单边让位（X）\n'
     'WIN_CLEAR_Y = (WIN_H - LCD_AA_Y) / 2          # 0.52  单边让位（Y）', 1),
], forbid=("WIN_A_W", "WIN_B_W", "WIN_A_H", "WIN_B_H"))


# ============================================================ build_v2.py
apply("build_v2.py", blocks=[
    # --- 单一上盖 ---
    ('top_a = build_top(P.WIN_A_W, P.WIN_A_H)\n'
     'top_b = build_top(P.WIN_B_W, P.WIN_B_H)\n'
     'base = build_base()',
     'top = build_top(P.WIN_W, P.WIN_H)\n'
     'base = build_base()', 1),
    ('for name, mesh in [("ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl", top_a),\n'
     '                   ("ESP32S3_LCD_全覆盖外壳_上盖_B版_3D打印.stl", top_b),\n'
     '                   ("ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl", base)]:',
     'for name, mesh in [("ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl", top),\n'
     '                   ("ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl", base)]:', 1),
    # --- 窗口矩形 + A.A 参考矩形 ---
    ('WIN_A = (P.WIN_CX - P.WIN_A_W / 2, P.WIN_CY - P.WIN_A_H / 2,\n'
     '         P.WIN_CX + P.WIN_A_W / 2, P.WIN_CY + P.WIN_A_H / 2)',
     'WIN = (P.WIN_CX - P.WIN_W / 2, P.WIN_CY - P.WIN_H / 2,\n'
     '       P.WIN_CX + P.WIN_W / 2, P.WIN_CY + P.WIN_H / 2)\n'
     'LCD_AA = (P.WIN_CX - P.LCD_AA_X / 2, P.WIN_CY - P.LCD_AA_Y / 2,\n'
     '          P.WIN_CX + P.LCD_AA_X / 2, P.WIN_CY + P.LCD_AA_Y / 2)', 1),
    # --- 上盖加工图标注 ---
    ('DIMH(m, WIN_A[0], WIN_A[2], P.H, f"{P.WIN_A_W:.2f} (A版)", 7)',
     'DIMH(m, WIN[0], WIN[2], P.H, f"{P.WIN_W:.2f} 显示窗", 7)', 1),
    ('T(m, f"上盖俯视 1:1  (单位 mm)  窗口按 A 版 {P.WIN_A_W:.2f} x {P.WIN_A_H:.2f}", 0, -30, 3.6)\n'
     'T(m, f"B 版窗口 {P.WIN_B_W:.2f} x {P.WIN_B_H:.2f}（其余相同），见 B 版 STL", 0, -35, 2.8, "NOTE")',
     'T(m, f"上盖俯视 1:1  (单位 mm)  显示窗 {P.WIN_W:.2f} x {P.WIN_H:.2f}（按实测 A.A 放大让位）", 0, -30, 3.6)\n'
     'T(m, f"实测 LCD A.A {P.LCD_AA_X:.2f} x {P.LCD_AA_Y:.2f}；窗口四周各让位 '
     '{P.WIN_CLEAR_X:.2f} / {P.WIN_CLEAR_Y:.2f}，请勿缩小", 0, -35, 2.8, "NOTE")', 1),
    ('T(m, f"Rev G 偏心屏：显示窗中心 X={P.WIN_CX:.2f} / Y={P.WIN_CY:.2f}"\n'
     '     f"（相对外壳中心左移 {-P.WIN_OFFSET_X:.2f}），窗口左缘 X={WIN_A[0]:.2f}；请勿居中",\n'
     '  0, P.H + 32, 2.8, "ANT")',
     'T(m, f"Rev H 偏心屏：显示窗中心 X={P.WIN_CX:.2f} / Y={P.WIN_CY:.2f}"\n'
     '     f"（相对外壳中心左移 {-P.WIN_OFFSET_X:.2f}），窗口左缘 X={WIN[0]:.2f}；请勿居中",\n'
     '  0, P.H + 32, 2.8, "ANT")\n'
     'T(m, f"单版本：窗口 {P.WIN_W:.2f} x {P.WIN_H:.2f} 比实测 A.A {P.LCD_AA_X:.2f} x '
     '{P.LCD_AA_Y:.2f} 四周各放大 {P.WIN_CLEAR_X:.2f} / {P.WIN_CLEAR_Y:.2f}",\n'
     '  0, P.H + 37, 2.8, "ANT")', 1),
    ('wa, wb = WIN_A[0] * SC, WIN_A[2] * SC',
     'wa, wb = WIN[0] * SC, WIN[2] * SC', 1),
    # --- 技术说明 ---
    ('    "1. 上盖为不透明全覆盖件，仅开显示区窗口；屏幕黑边（右侧宽于左侧）被顶板压住。",\n'
     '    "2. 窗口 A 版 69.00x47.60（保守压边）；B 版 72.00x47.60（贴 AA 73.44x48.96）。",\n'
     '    "2b.【Rev G 偏心屏对位】ATK-MD0350 显示区不居中：右侧黑边宽、左侧窄，上下对称。",',
     '    "1. 上盖为不透明全覆盖件，仅开显示区窗口；屏幕黑边（右侧宽于左侧）被顶板压住。",\n'
     '    "2. 显示窗 74.40x50.00，按实测 LCD A.A 73.44x48.96 四周各放大 0.48/0.52 让位；",\n'
     '    "   原 A/B 双版窗口均小于 A.A（会切掉亮区像素），已作废，本版只剩一个上盖。",\n'
     '    "2b.【偏心屏对位】ATK-MD0350 显示区不居中：右侧黑边宽、左侧窄，上下对称。",', 1),
    ('    "   只露显示区，四周黑边由完整不透明顶板压住。依据 LCM 规格书 OUTLINE 84.69x55.26",',
     '    "   除 <=0.5mm 装配让位外，四周黑边由完整不透明顶板压住。依据规格书 OUTLINE 84.69x55.26",', 1),
    ('vol_top = top_a.volume / 1000', 'vol_top = top.volume / 1000', 1),
    # --- 下单说明【零】整段 ---
    ('  【零、打样前必测两项：亮区尺寸 + 偏心量】\n'
     '  1) 点亮屏幕，用游标卡尺量「发光显示区」的宽 x 高：\n'
     '    - 约 70.46 x 49.07 mm 或更小 → 发【上盖_A版】STL（窗口 69.00 x 47.60，黑边全包住）\n'
     '    - 约 73.44 x 48.96 mm        → 发【上盖_B版】STL（窗口 72.00 x 47.60）\n'
     '  2) 量偏心：显示区左缘到模块左缘 = L，显示区右缘到模块右缘 = R。\n'
     '     ★ Rev G 已按 (L-R)/2 = -2.75 mm（显示区偏左、右侧黑边宽）把窗口中心\n'
     '       从外壳中心 X=52.60 左移到 X=49.85，Y=33.50 不变；上下黑边对称故不调 Y。\n'
     '       依据：LCM 规格书 OUTLINE 84.69x55.26 / LCD A.A 73.44x48.96 长边尺寸链\n'
     '       偏心 2.77 mm；你发的实物商品图逐像素换算 2.52 mm，取 2.75。\n'
     '       窗口仍只露显示区，四周黑边由完整不透明顶板压住（已确认）。\n'
     '     若实测偏移不同：改 params_v2.py 的 WIN_OFFSET_X 一行，\n'
     '     重跑 build_v2.py / make_pdf_v2.py / make_views.py / build_step.py /\n'
     '     make_preview.py / freecadcmd build_fcstd.py 即可同步全部交付物。\n'
     '  两版只有窗口长度不同，其余完全一致。底座两版通用。\n'
     '\n'
     '  【必测第二项：高度】',
     '  【零、Rev H 显示窗：单版本 + 按实测 A.A 放大让位】\n'
     '  ★ 已实测确认 LCD A.A（发光显示区）= 73.44 x 48.96 mm，本版据此定窗。\n'
     '  ★ 删除原 A / B 双版本：原 A 版 69.00x47.60 依据 EDA 封装可视框，\n'
     '    比实测 A.A 窄 4.44 mm；原 B 版 72.00x47.60 仍窄 1.44 mm，\n'
     '    两者都会切掉亮区边缘像素，已全部作废。本目录只剩一个上盖 STL。\n'
     '  ★ 现窗口 {P.WIN_W:.2f} x {P.WIN_H:.2f} mm（四角 R{P.WIN_R:.1f}），\n'
     '    四周各比 A.A 放大 {P.WIN_CLEAR_X:.2f} / {P.WIN_CLEAR_Y:.2f} mm，\n'
     '    用于吸收 3D 打印公差、LCD 排针插装与 φ4 孔配 M3 的位置偏差、\n'
     '    以及偏心量推算误差。取舍：理想装配下四周会露出 <=0.5 mm 极窄黑边，\n'
     '    但绝不遮挡显示内容。请转告商家：不要按旧版习惯把窗口缩小或移回居中。\n'
     '  ★ 偏心量仍待实测：显示区左缘到模块左缘 = L，右缘到模块右缘 = R。\n'
     '    当前 WIN_OFFSET_X = {P.WIN_OFFSET_X:.2f}（窗口中心 X={P.WIN_CX:.2f}，\n'
     '    外壳中心 52.60），由规格书尺寸链 2.77 mm 与实物图像素 2.52 mm 推算，未实测。\n'
     '    若实测 (L-R)/2 不同：改 params_v2.py 的 WIN_OFFSET_X 一行，\n'
     '    重跑 build_v2.py / make_pdf_v2.py / make_views.py / build_step.py /\n'
     '    make_preview.py / freecadcmd build_fcstd.py 即可同步全部交付物。\n'
     '\n'
     '  【打样前必测：整机高度】', 1),
    ('  【LCD 屏固定：两种方案，本版按 A 出图】',
     '  【LCD 屏固定：两种方案，本版按方案 A 出图】', 1),
    # --- 【一】发给商家文件 ---
    ('     发给商家（2 个 STL，一次下单）：\n'
     '       ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl   （或 B 版，二选一）\n'
     '       ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl',
     '     发给商家（2 个 STL，一次下单）：\n'
     '       ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl\n'
     '       ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl', 1),
    # --- 【二】复制给商家的一段话 ---
    ('  请勿擅自缩小窗口；顶板天线区不要开洞、不要加支撑。',
     '  窗口四周已按实测 A.A 放大让位以吸收装配偏差，请勿擅自缩小或移回居中；\n'
     '  顶板天线区不要开洞、不要加支撑。', 1),
    # --- 【七】文件清单整块 ---
    ('  ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl   A 版上盖（保守窗口）\n'
     '  ESP32S3_LCD_全覆盖外壳_上盖_B版_3D打印.stl   B 版上盖（标准 AA 窗口）\n'
     '  ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl       底座（两版通用）',
     '  ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl        上盖（唯一版本，窗口 74.40x50.00）\n'
     '  ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl         底座', 1),
    ('  ESP32S3_LCD_全覆盖外壳_上盖_A版_可编辑.step    STEP 实体（同 A 版 STL）\n'
     '  ESP32S3_LCD_全覆盖外壳_上盖_B版_可编辑.step    STEP 实体（同 B 版 STL）',
     '  ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step          STEP 实体（同上盖 STL）', 1),
    ('  【STEP 实体文件说明】4 个 .step 是 AP214 BREP 解析实体（圆角是真圆弧、',
     '  【STEP 实体文件说明】3 个 .step 是 AP214 BREP 解析实体（圆角是真圆弧、', 1),
    # --- geom dict 窗口键 ---
    ('    WIN_A=list(WIN_A), WIN_B=[P.WIN_CX - P.WIN_B_W/2, P.WIN_CY - P.WIN_B_H/2,\n'
     '                              P.WIN_CX + P.WIN_B_W/2, P.WIN_CY + P.WIN_B_H/2],\n'
     '    WIN_A_W=P.WIN_A_W, WIN_A_H=P.WIN_A_H, WIN_B_W=P.WIN_B_W, WIN_B_H=P.WIN_B_H,',
     '    WIN=list(WIN), LCD_AA=list(LCD_AA),\n'
     '    WIN_W=P.WIN_W, WIN_H=P.WIN_H,\n'
     '    LCD_AA_W=P.LCD_AA_X, LCD_AA_H=P.LCD_AA_Y,\n'
     '    WIN_CLEAR_X=P.WIN_CLEAR_X, WIN_CLEAR_Y=P.WIN_CLEAR_Y,', 1),
], globals_=[
    ("WIN_A", "WIN"),
    ("Rev G", "Rev H"),
    ('REV="G"', 'REV="H"'),
    ("上盖_A版_3D打印.stl", "上盖_3D打印.stl"),
    ("上盖_B版_3D打印.stl", "上盖_3D打印.stl"),
    ("上盖_A版_可编辑.step", "上盖_可编辑.step"),
    ("上盖_B版_可编辑.step", "上盖_可编辑.step"),
    ("top_a", "top"),
    ("装配体 STEP 内含 3 个独立实体：上盖 A 版 / 底座 / PCB 参考板，",
     "装配体 STEP 内含 3 个独立实体：上盖 / 底座 / PCB 参考板，"),
    ("内含上盖 A 版 / 底座 /", "内含上盖 / 底座 /"),
    ("几何不变；改宏里 TOP_FILE 一行可换 B 版。", "几何不变。"),
    ("底座（两版通用）", "底座"),
], forbid=("WIN_B", "上盖_A版", "上盖_B版", "A 版上盖", "B 版上盖",
           "上盖 A 版", "可换 B 版", "top_b", "Rev G"))


# ============================================================ make_pdf_v2.py
apply("make_pdf_v2.py", blocks=[
    ('T("显示区窗口 AA", P(wx + 3, wy + wh / 2)[0], P(wx + 3, wy + wh / 2)[1], 7, REDC)\n'
     'T("屏幕黑边被顶板压住", P(wx + 3, wy + wh / 2 - 5)[0],\n'
     '  P(wx + 3, wy + wh / 2 - 5)[1], 6, GRAY)',
     'T("显示窗 = A.A + 让位", P(wx + 3, wy + wh / 2)[0], P(wx + 3, wy + wh / 2)[1], 7, REDC)\n'
     'T("四周各放大 0.5，不切亮区", P(wx + 3, wy + wh / 2 - 5)[0],\n'
     '  P(wx + 3, wy + wh / 2 - 5)[1], 6, GRAY)', 1),
    ('DIMH(P(wx, 0)[0], P(wx + ww, 0)[0], OY + H + 6, f"{G[\'WIN_A_W\']:.2f} (A版窗口)")',
     'DIMH(P(wx, 0)[0], P(wx + ww, 0)[0], OY + H + 6, f"{G[\'WIN_W\']:.2f} 显示窗")', 1),
    ('DIMV(P(0, wy)[1], P(0, wy + wh)[1], OX + W + 8, f"{G[\'WIN_A_H\']:.2f}")',
     'DIMV(P(0, wy)[1], P(0, wy + wh)[1], OX + W + 8, f"{G[\'WIN_H\']:.2f}")', 1),
    ('T("上盖俯视 1:1（窗口按 A 版）", OX, OY - 22, 9, INK)',
     'T("上盖俯视 1:1（单版本显示窗 · A.A 放大让位）", OX, OY - 22, 9, INK)', 1),
    ('T("A / B 版窗口对照", IX, 184, 9, BLUE)\n'
     'rows = [["版本", "窗口尺寸", "依据", "适用"],\n'
     '        ["A", "69.00 × 47.60", "EDA封装可视框 70.46×49.07", "≤70.46"],\n'
     '        ["B", "72.00 × 47.60", "通用 AA 73.44×48.96", "≈73.44"]]\n'
     'colx = [IX, IX + 14, IX + 42, IX + 110]\n'
     'for r, row in enumerate(rows):\n'
     '    y = 176 - r * 7\n'
     '    RECT(IX, y - 2, 132, 7, GRAY, 0.25, fill=(LIGHT if r == 0 else None))\n'
     '    for j, v in enumerate(row):\n'
     '        T(v, colx[j] + 1, y, 6.3 if r else 6.8, INK if r else BLUE)\n'
     'T("打样前点亮屏幕：量发光区宽高选 A/B，并量左右偏心。", IX, 152, 6.8, REDC)\n'
     'T("其余几何两版完全相同；底座通用。", IX, 146.5, 6.8, INK)',
     'T("显示窗 vs 实测 LCD A.A", IX, 184, 9, BLUE)\n'
     'rows = [["项目", "宽 X", "高 Y", "说明"],\n'
     '        ["A.A", "73.44", "48.96", "实测发光区"],\n'
     '        ["窗口", "74.40", "50.00", "四周 +0.5"],\n'
     '        ["让位", "0.48", "0.52", "不切亮区"]]\n'
     'colx = [IX, IX + 34, IX + 68, IX + 100]\n'
     'for r, row in enumerate(rows):\n'
     '    y = 176 - r * 6\n'
     '    RECT(IX, y - 2, 132, 6, GRAY, 0.25, fill=(LIGHT if r == 0 else None))\n'
     '    for j, v in enumerate(row):\n'
     '        T(v, colx[j] + 1, y, 6.3 if r else 6.8, INK if r else BLUE)\n'
     'T("窗口比 A.A 大：宁露极窄黑边，不切亮区。", IX, 148, 6.6, REDC)\n'
     'T("偏心量 -2.75 仍为推算值，打样前实测。", IX, 142.5, 6.6, REDC)', 1),
    ('    f"窗口 {G[\'WIN_A_W\']:.2f}×{G[\'WIN_A_H\']:.2f} R{G[\'WIN_R\']:.1f}；中心 X={G[\'WIN_CX\']:.2f}",\n'
     '    f"偏心屏：窗口左移 {-G[\'WIN_OFFSET_X\']:.2f} 对准显示区，黑边全部压住",',
     '    f"窗口 {G[\'WIN_W\']:.2f}×{G[\'WIN_H\']:.2f} R{G[\'WIN_R\']:.1f}；中心 X={G[\'WIN_CX\']:.2f}",\n'
     '    f"实测 A.A {G[\'LCD_AA_W\']:.2f}×{G[\'LCD_AA_H\']:.2f}，四周让位 {G[\'WIN_CLEAR_X\']:.2f}/{G[\'WIN_CLEAR_Y\']:.2f}",\n'
     '    f"偏心屏：窗口左移 {-G[\'WIN_OFFSET_X\']:.2f} 对准显示区，宁露黑边不切亮区",', 1),
    ('FOOTER("注：窗口按 A 版绘制；B 版仅长度 72.00 不同。Rev G 窗口已左移 2.75 对准偏心屏，打样前请实测。")',
     'FOOTER("注：Rev H 已删除 A/B 双版本；唯一窗口 74.40×50.00 按实测 A.A 放大让位，左移 2.75 对准偏心屏。")', 1),
    ('FOOTER("注：Rev G 四边开口统一 Z 4.00~14.20 平齐且含插线余量；顶板完整无镂空、显示窗左移 2.75 对准偏心屏。")',
     'FOOTER("注：Rev H 四边开口统一 Z 4.00~14.20 平齐且含插线余量；顶板完整无镂空；显示窗按实测 A.A 放大让位。")', 1),
], globals_=[
    ("WIN_A", "WIN"), ("Rev G", "Rev H"), ("EN-G", "EN-H"),
], forbid=("WIN_A", "WIN_B", "A / B", "Rev G", "EN-G"))


# ============================================================ make_views.py
apply("make_views.py", blocks=[
    ('TC(f"{ww:.2f} × {wh:.2f} (A 版)", FX + (wx + ww / 2) * S,\n'
     '   FY + (wy + wh / 2) * S - 3, 7, REDC)\n'
     'TC("屏幕黑边被顶板压住", FX + (wx + ww / 2) * S,\n'
     '   FY + (wy + wh / 2) * S - 10, 6.5, GRAY)',
     'TC(f"{ww:.2f} × {wh:.2f}（A.A + 让位）", FX + (wx + ww / 2) * S,\n'
     '   FY + (wy + wh / 2) * S - 3, 7, REDC)\n'
     'TC("四周各放大 0.5，不切亮区", FX + (wx + ww / 2) * S,\n'
     '   FY + (wy + wh / 2) * S - 10, 6.5, GRAY)', 1),
    ('    (f"显示窗 {G[\'WIN_A_W\']:.2f}×{G[\'WIN_A_H\']:.2f} R{G[\'WIN_R\']:.1f}（A 版）", REDC),\n'
     '    (f"窗口中心 X={G[\'WIN_CX\']:.2f}/Y={G[\'WIN_CY\']:.2f}，偏心屏左移 {-G[\'WIN_OFFSET_X\']:.2f}", REDC),\n'
     '    (f"顶板无镂空：仅显示窗 + Φ{RSTD:.1f} 复位孔；黑边全压住", GREEN),',
     '    (f"显示窗 {G[\'WIN_W\']:.2f}×{G[\'WIN_H\']:.2f} R{G[\'WIN_R\']:.1f}（唯一版本）", REDC),\n'
     '    (f"实测 A.A {G[\'LCD_AA_W\']:.2f}×{G[\'LCD_AA_H\']:.2f}，四周让位 {G[\'WIN_CLEAR_X\']:.2f}/{G[\'WIN_CLEAR_Y\']:.2f}", REDC),\n'
     '    (f"窗口中心 X={G[\'WIN_CX\']:.2f}/Y={G[\'WIN_CY\']:.2f}，偏心屏左移 {-G[\'WIN_OFFSET_X\']:.2f}", REDC),\n'
     '    (f"顶板无镂空：仅显示窗 + Φ{RSTD:.1f} 复位孔；宁露黑边不切亮区", GREEN),', 1),
    ('    "   屏幕黑边（右侧明显宽于左侧）被顶板压住，窗口已左移 2.75 对准亮区。",',
     '    "   窗口按实测 A.A 四周放大 0.5，宁露极窄黑边也不切亮区；已左移 2.75。",', 1),
    ('dt("ESP32S3-LCD-EN-G-VIEW  Rev G  |  单位 mm  1:1  |  四边开口平齐 / 显示窗偏心对位",',
     'dt("ESP32S3-LCD-EN-H-VIEW  Rev H  |  单位 mm  1:1  |  四边开口平齐 / 显示窗按 A.A 放大让位",', 1),
], globals_=[
    ("WIN_A", "WIN"), ("Rev G", "Rev H"), ("EN-G", "EN-H"),
], forbid=("WIN_A", "WIN_B", "（A 版）", "Rev G", "EN-G"))


# ============================================================ build_step.py
apply("build_step.py", blocks=[
    ('  ESP32S3_LCD_全覆盖外壳_上盖_A版_可编辑.step\n'
     '  ESP32S3_LCD_全覆盖外壳_上盖_B版_可编辑.step',
     '  ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step', 1),
    ('    top_a = build_top(P.WIN_A_W, P.WIN_A_H)\n'
     '    top_b = build_top(P.WIN_B_W, P.WIN_B_H)\n'
     '    base = build_base()',
     '    top = build_top(P.WIN_W, P.WIN_H)\n'
     '    base = build_base()', 1),
    ('        (top_a, "ESP32S3_LCD_全覆盖外壳_上盖_A版_可编辑.step",\n'
     '         "ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl"),\n'
     '        (top_b, "ESP32S3_LCD_全覆盖外壳_上盖_B版_可编辑.step",\n'
     '         "ESP32S3_LCD_全覆盖外壳_上盖_B版_3D打印.stl"),',
     '        (top, "ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step",\n'
     '         "ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl"),', 1),
    ('    cq.Compound.makeCompound([top_a, base, pcb]).exportStep(assy_path)',
     '    cq.Compound.makeCompound([top, base, pcb]).exportStep(assy_path)', 1),
    # parts 从 3 件缩为 2 件，装配体期望体积里底座索引由 2 变 1
    ('                   + ref.get(parts[2][2], {}).get("volume_cm3", 0)',
     '                   + ref.get(parts[1][2], {}).get("volume_cm3", 0)', 1),
], globals_=[
    ("WIN_A", "WIN"), ("Rev G", "Rev H"),
], forbid=("WIN_A", "WIN_B", "上盖_A版", "上盖_B版", "top_a", "top_b", "Rev G"))


# ============================================================ make_preview.py
apply("make_preview.py", blocks=[
    ('"""Rev G 预览图：上盖俯视（标出偏心窗口位置）+ 等距 3D。\n'
     '\n'
     '窗口中心由外壳中心 52.60 左移到 49.85 后，俯视图里能直观看到\n'
     '窗口相对外壳居中线偏左，右侧留出的顶板压边更宽。\n'
     '"""',
     '"""Rev H 预览图：上盖俯视（实测 A.A 虚线 + 放大让位窗口实线）+ 等距 3D。\n'
     '\n'
     '灰色虚线 = 实测 LCD A.A 73.44×48.96；红色实线 = 唯一显示窗 74.40×50.00，\n'
     '四周各放大 0.48/0.52 mm 让位。窗口中心左移 2.75 对准偏心屏。\n'
     '"""', 1),
    ('STL = os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl")',
     'STL = os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl")', 1),
    ('    wx, wy, ww, wh = WIN\n'
     '    # Rev F 旧窗口（居中）作对比，直观看出左移量\n'
     '    old_wx = P.W / 2 - P.WIN_A_W / 2\n'
     '    ax.add_patch(FancyBboxPatch(\n'
     '        (old_wx, wy), ww, wh,\n'
     '        boxstyle=f"round,pad=0,rounding_size={P.WIN_R}",\n'
     '        fill=False, ec="#94a1ad", ls="--", lw=1.3))',
     '    wx, wy, ww, wh = WIN\n'
     '    # 实测 LCD A.A 参考矩形（虚线），直观看出四周让位量\n'
     '    aax = P.WIN_CX - P.LCD_AA_X / 2\n'
     '    aay = P.WIN_CY - P.LCD_AA_Y / 2\n'
     '    ax.add_patch(FancyBboxPatch(\n'
     '        (aax, aay), P.LCD_AA_X, P.LCD_AA_Y,\n'
     '        boxstyle=f"round,pad=0,rounding_size={P.WIN_R}",\n'
     '        fill=False, ec="#4f8f6d", ls="--", lw=1.6))', 1),
    ('    ax.text(0, -14.5,\n'
     '            "灰色虚线框 = Rev F 居中旧窗口；红色实线框 = Rev G 偏心新窗口",\n'
     '            color="#5a6d7d", fontsize=9.5)',
     '    ax.text(0, -14.5,\n'
     '            "绿色虚线框 = 实测 LCD A.A 73.44×48.96；红色实线框 = 显示窗 '
     '74.40×50.00（四周各放大 0.48/0.52 让位）",\n'
     '            color="#5a6d7d", fontsize=9.5)', 1),
    ('    ax.text(0, P.H + 8,\n'
     '            f"Rev G 上盖俯视 · 显示窗已左移对准偏心屏 · 顶板完整无镂空 · 单位 mm",',
     '    ax.text(0, P.H + 8,\n'
     '            f"Rev H 上盖俯视 · 单版本窗口按实测 A.A 放大让位 · 顶板完整无镂空 · 单位 mm",', 1),
    ('    ax.set_title("Rev G 上盖等距视图 · 窗口偏心对位 · 顶板完整",',
     '    ax.set_title("Rev H 上盖等距视图 · 窗口按 A.A 放大让位 · 顶板完整",', 1),
], globals_=[
    ("WIN_A", "WIN"), ("Rev G", "Rev H"),
], forbid=("WIN_A", "WIN_B", "上盖_A版", "上盖_B版", "Rev G"))


# ============================================================ build_fcstd.py
apply("build_fcstd.py", blocks=[
    ('  TopCover_A   上盖 A 版（打印件）', '  TopCover     上盖（打印件）', 1),
    ('TOP_FILE = "ESP32S3_LCD_全覆盖外壳_上盖_A版_可编辑.step"\n'
     '# TOP_FILE = "ESP32S3_LCD_全覆盖外壳_上盖_B版_可编辑.step"',
     'TOP_FILE = "ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step"', 1),
    ('    doc = App.newDocument("ESP32S3_LCD_Enclosure_RevG")\n'
     '    doc.Label = "ESP32S3_LCD Enclosure Rev G"',
     '    doc = App.newDocument("ESP32S3_LCD_Enclosure_RevH")\n'
     '    doc.Label = "ESP32S3_LCD Enclosure Rev H"', 1),
    ('    add(doc, "TopCover_A", "上盖 A 版（打印件）",',
     '    add(doc, "TopCover", "上盖（打印件）",', 1),
], forbid=("TopCover_A", "上盖_A版", "上盖_B版", "RevG", "Rev G"))


# ============================================================ FreeCAD 宏
apply(os.path.join("deliverables", "FreeCAD_一键生成工程.FCMacro"), blocks=[
    ('内含上盖 A 版 / 底座 / PCB 参考板 3 个命名实体。',
     '内含上盖 / 底座 / PCB 参考板 3 个命名实体。', 1),
    ('想用 B 版上盖：把下面 TOP_FILE 改成 B 版文件名再执行一次即可。\n', '', 1),
    ('TOP_FILE = "ESP32S3_LCD_全覆盖外壳_上盖_A版_可编辑.step"\n'
     '# TOP_FILE = "ESP32S3_LCD_全覆盖外壳_上盖_B版_可编辑.step"',
     'TOP_FILE = "ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step"', 1),
    ('    doc = App.newDocument("ESP32S3_LCD_Enclosure_RevG")\n'
     '    doc.Label = "ESP32S3_LCD 全覆盖外壳 Rev G"',
     '    doc = App.newDocument("ESP32S3_LCD_Enclosure_RevH")\n'
     '    doc.Label = "ESP32S3_LCD 全覆盖外壳 Rev H"', 1),
    ('    add_part(doc, "TopCover_A", "上盖（A 版，打印件）",',
     '    add_part(doc, "TopCover", "上盖（打印件）",', 1),
], forbid=("TopCover_A", "上盖_A版", "上盖_B版", "RevG", "Rev G"))


# ============================================================ 清理旧 A/B 实体文件
OLD = [
    "ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl",
    "ESP32S3_LCD_全覆盖外壳_上盖_B版_3D打印.stl",
    "ESP32S3_LCD_全覆盖外壳_上盖_A版_可编辑.step",
    "ESP32S3_LCD_全覆盖外壳_上盖_B版_可编辑.step",
]
for name in OLD:
    p = os.path.join(DELIV, name)
    if os.path.isfile(p):
        os.remove(p)
        print("removed obsolete:", name)
print("PATCH V7 DONE")

