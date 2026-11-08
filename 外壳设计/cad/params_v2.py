# -*- coding: utf-8 -*-
"""ESP32S3_LCD 全覆盖外壳 Rev I —— 统一设计参数 (单位 mm)

Rev I 相对 Rev H 的修正（用户 11-08 确认「不用 M3 固定 LCD，屏幕左侧没有过孔」）：
  ★【结构硬伤修复】ATK-MD0350 用户手册图 3.1：模块 PCB 底板 56.41 x 97.92，
    两个安装孔只在 ALIENTEK 一端、孔距 48.64；短边余量每侧 (56.41-48.64)/2=3.885。
    PCB 同侧两孔距 48.695，与 48.64 只差 0.055 mm → LCD 两孔对准 PCB 一端两孔。
    LCD 板 97.92 长 < PCB 100 长，故 LCD 板【完全落在 PCB 板框投影内】：
    孔心到板端按 2.53 / 3.94 两种读法，LCD 板 py 分别为 0.27~98.19 / 1.68~99.60，
    四角 φ4 孔（py=4.317 与 95.66）全部在板内；左端为实心板、无让位孔。
    Rev A~H 的「4 颗 M3 从底面穿过 PCB φ4 孔 → 拧进上盖柱」因此装不上：
    螺杆在 Z≈5.0~12.1 段被 LCD 板挡死。缩小柱径 / 换 M2 / 去掉 LCD 螺丝都无效。
  ★【连接点移出 LCD 投影】外形每边 +3.00：GAP 1.00→4.00、EDGE 2.60→5.60，
    105.20x67.00 → 111.20x73.00（高度 16.00 不变，PCB 仍居中）。
    4 个连接柱移到外壳四角（柱心距角 3.50，Φ6.0），位于 PCB 板框之外；
    因 LCD 板完全在 PCB 板框内，柱与 LCD 板绝无干涉。
    核算：柱心到 PCB 板框 R2 圆角实体净距 3.80 ≥ 柱半径 3.00，余量 0.80 mm；
    柱圆完全落在 R4.5 外圆角轮廓内（4.41 ≤ 4.50）。
  ★【PCB 固定改定位销】PCB 四角 φ4 孔不再穿螺丝，改由底座 4 个 Φ3.8x1.6
    定位销（Z 3.40~5.00）水平定位；底座原 4 个 Φ7 支撑台保留托住 PCB 底面。
    4 颗 M3x12 只连接上盖与底座的四角柱，不再经过 PCB / LCD。
  ★ 顶板内表面 Z=14.20 与 LCD 板顶（约 12.1）留约 2.1 mm；
    若装配后觉得晃，在顶板内侧贴 1~2 mm 泡棉垫即可（不写进模型）。
  ★ 所有绝对坐标统一 +3.00（SHIFT），显示窗 / 各接口相对 PCB 的位置不变。
  ★ 修正参数错误：LCD_MODULE_L 83.36 → 97.92（83.36 不是模块板长）。

Rev H 相对 Rev G 的修正（用户 11-08 实测确认 LCD A.A）：
  ★【删除 A/B 双版本】用户实测确认 LCD A.A（发光显示区）= 73.44 x 48.96 mm。
    Rev G 的 A 版窗口 69.00x47.60（依据 EDA 封装可视框 70.46x49.07）比实测
    A.A 窄 4.44 mm，B 版 72.00x47.60 仍窄 1.44 mm —— 两者都在切掉亮区边缘像素。
    现废弃两版，只保留唯一上盖。
  ★【窗口改为放大让位】窗口 74.40 x 50.00，四周各比 A.A 放大 0.48 / 0.52 mm，
    用于吸收 3D 打印公差、LCD 排针插装偏差与偏心量推算误差。
    取舍：理想装配下四周露出 <=0.5 mm 极窄黑边，但绝不遮挡显示内容。
  ★ 偏心量 WIN_OFFSET_X=-2.75 仍是规格书 + 实物图推算值，未实测。

Rev G 相对 Rev F：偏心屏显示窗对位，窗口中心 X 左移 2.75（Y 不变）。

Rev F 相对 Rev E：四边所有开口统一开口带 Z 4.00~14.20；按带壳插头与线材
  外径加宽合并窗；ESP32 核心板直焊 PCB；顶板完整无镂空。

Rev E：顶板不再 U 形镂空，天线改由侧壁让位窗伸出；新增 A3 三视图。
Rev D：孔径纠错 φ4.0（非 φ2.0）、统一 M3、取消磁吸。

坐标约定（屏幕正视、天线朝上 = PCB 左旋 90° 后的视角）：
  外壳坐标 (Xo, Yo)：原点在左下角，Xo 向右，Yo 向上（Yo 大端 = 天线侧 / 上边）
  PCB 原始坐标 (px, py)：px 沿 61.8 短边，py 沿 100 长边（工程内 mil × 0.0254）
  映射：Xo = py + OX ,  Yo = px + OY
"""
import math

# ---------------- PCB / 屏幕实测依据 ----------------
PCB_PX, PCB_PY, PCB_R = 61.8, 100.0, 2.0
MIL2MM = 0.0254
PCB_HOLES_PXPY = [(5.715, 4.317), (54.41, 4.317),
                  (5.715, 95.66), (54.41, 95.66)]      # 4 x φ4 安装孔
PCB_HOLE_D = 4.0                                        # 半径 78.7402 mil ×2
LCD_MODULE_W, LCD_MODULE_L = 56.41, 97.92               # 手册图 3.1 模块 PCB 底板
LCD_MOUNT_HOLES = 2                                     # 仅 ALIENTEK 一端 2 孔，距 48.64
LCD_MOUNT_PITCH = 48.64
LCD_AA_STD_W, LCD_AA_STD_L = 48.96, 73.44              # 3.5" 320x480 通用 AA
LCD_AA_X, LCD_AA_Y = 73.44, 48.96                     # 用户实测确认；外壳坐标 X 长边 / Y 短边
LCD_FRAME_W, LCD_FRAME_L = 49.07, 70.46                 # 工程 TFT3.5'_C 封装内可视框

# ---------------- 外壳外形（Rev I：每边 +3.00） ----------------
SHIFT = 3.00                  # 所有绝对坐标相对 Rev H 的平移量
GAP = 4.0                     # PCB 到内壁单边间隙（Rev H 为 1.0）
T_WALL = 1.6                  # 侧壁厚
EDGE = GAP + T_WALL           # 5.6 单边外扩
W = PCB_PY + 2 * EDGE         # 111.20  外壳宽（Xo 方向）
H = PCB_PX + 2 * EDGE         # 73.00   外壳高（Yo 方向）
R_OUT = 4.5                   # 外圆角
R_IN = 2.9                    # 内腔圆角
OX = OY = EDGE                # PCB 原点在外壳坐标中的偏移 5.6

T_BASE = 2.4                  # 底座底板厚
Z_PCB_BOT = 3.4               # PCB 底面（= 底板 2.4 + 支撑台 1.0）
Z_PCB_TOP = 5.0               # PCB 顶面 (t=1.6)
Z_TOP_IN = 14.2               # 顶板内表面
T_TOP = 1.8                   # 顶板厚
H_TOTAL = Z_TOP_IN + T_TOP    # 16.00 总高
H_CAVITY = Z_TOP_IN - T_BASE  # 11.80 内腔净高

# ---------------- 螺丝（M3，无磁吸） ----------------
SCREW_HOLE_D = 3.4            # 底座通孔（M3 杆 φ3.0 + 0.4 间隙）
SCREW_CS_D, SCREW_CS_DEPTH = 6.5, 1.6   # 底部沉头孔（M3 沉头 φ6.0~6.5）
POST_D = 6.0                  # 上盖连接柱外径（Rev I：Φ7→Φ6，柱在 PCB 板框外）
POST_PILOT_D = 2.6            # M3 自攻底孔
POST_Z0, POST_Z1 = Z_PCB_BOT, Z_TOP_IN + 0.2   # 3.4 ~ 14.4（与底座台顶对接）
POST_PILOT_Z1 = Z_TOP_IN - 0.4                 # 13.8 盲孔底（不贯穿顶板）

# 四角连接柱位（PCB 板框外；LCD 板完全在 PCB 板框内，故与屏无干涉）
SCREW_C = 3.50
SCREW_POS = [(SCREW_C, SCREW_C), (SCREW_C, H - SCREW_C),
             (W - SCREW_C, SCREW_C), (W - SCREW_C, H - SCREW_C)]

# PCB 定位：底座 Φ7 支撑台 + Φ3.8 定位销穿过 PCB 四角 φ4 孔
BASE_BOSS_D = 7.0
LOCATOR_D = 3.8
LOCATOR_Z0, LOCATOR_Z1 = Z_PCB_BOT, Z_PCB_TOP   # 3.4 ~ 5.0

# ---------------- 显示区开窗（Rev H：单版本 + 按实测 A.A 放大让位） ----------------
# 模块长边沿 Xo、短边沿 Yo（屏幕正视、天线朝上）。
# AA 中心相对模块/外壳中心偏左约 2.75 mm；短边方向对称，无 Y 偏移。
WIN_OFFSET_X = -2.75                          # 负 = 显示区偏左（远离右侧宽黑边）
WIN_CX = OX + PCB_PY / 2 + WIN_OFFSET_X      # 52.85（Rev H 为 49.85）
WIN_CY = OY + PCB_PX / 2                     # 36.50（Rev H 为 33.50）
WIN_R = 1.5
WIN_W = 74.40                                 # 实测 A.A 73.44 + 2 x 0.48 让位
WIN_H = 50.00                                 # 实测 A.A 48.96 + 2 x 0.52 让位
WIN_CLEAR_X = (WIN_W - LCD_AA_X) / 2          # 0.48  单边让位（X）
WIN_CLEAR_Y = (WIN_H - LCD_AA_Y) / 2          # 0.52  单边让位（Y）

# ---------------- 统一开口带（Rev F） ----------------
OPEN_Z0 = 4.00
OPEN_Z1 = Z_TOP_IN                 # 14.20
RIB_W = 2.00                      # 上边两道加强筋宽

# ---------------- 天线让位（上边 / Yo 大端） ----------------
ANT_X0, ANT_X1 = 39.10 + SHIFT, 66.10 + SHIFT   # 42.10 ~ 69.10，宽 27.00
ANT_Y0 = H - T_WALL - 0.2               # 71.20：让位窗在俯视图上的 y 起点（仅侧壁）
ANT_SLOT_Z0, ANT_SLOT_Z1 = OPEN_Z0, OPEN_Z1
RESET_POS = (40.59 + SHIFT, 62.42 + SHIFT)      # (43.59, 65.42) SW1 复位键
RESET_HOLE_D = 4.0

# ---------------- 接口开槽（Rev F：合并宽窗 + 线材余量） ----------------
I2C_X = [v + SHIFT for v in (18.35, 31.31, 73.90, 86.86)]
I2C_SLOT_W = 12.0
I2C_GROUPS = [(12.00 + SHIFT, 37.10 + SHIFT),
              (68.10 + SHIFT, 93.00 + SHIFT)]   # (15.00,40.10) / (71.10,96.00)
DUAL_USBC_X0, DUAL_USBC_X1 = 34.00 + SHIFT, 70.00 + SHIFT   # 37.00 ~ 73.00
RIGHT_5V_Y0, RIGHT_5V_Y1 = 11.00 + SHIFT, 29.00 + SHIFT     # 14.00 ~ 32.00
RIGHT_XH_Y0, RIGHT_XH_Y1 = 32.00 + SHIFT, 55.00 + SHIFT     # 35.00 ~ 58.00

# 线材余量依据：XH2.54-4P 带扣插头 ≈ 13~15 宽；Type-C 注塑壳 ≈ 12~16 宽，
# 线材 Φ3~5、折弯再需 3~5。开口带 10.20 高，各窗宽度均含余量。

def slots():
    s = []
    # --- 上边 Yo 大端（天线侧）：2 段合并 I2C 宽窗 ---
    for i, (a, b) in enumerate(I2C_GROUPS, 1):
        s.append((f"I2C-G{i}", (a, H - T_WALL - 0.2, b, H + 2.0),
                  OPEN_Z0, OPEN_Z1,
                  f"2x XH2.54-4P 合并窗（含带壳插头 / 线材余量）"))
    # --- 下边 Yo 小端：核心板直焊，自带 2 个 Type-C 共用窗 ---
    s.append(("DUAL-USBC", (DUAL_USBC_X0, -2.0, DUAL_USBC_X1, 1.8),
              OPEN_Z0, OPEN_Z1,
              "ESP32 核心板 2 个 Type-C（UART / USB）共用窗"))
    # --- 右边 Xo 大端：5V Type-C 输出 + XH2.54-5P ---
    s.append(("5V-USBC", (W - T_WALL - 0.2, RIGHT_5V_Y0, W + 2.0, RIGHT_5V_Y1),
              OPEN_Z0, OPEN_Z1, "5V Type-C 输出口 (USB1)"))
    s.append(("XH-5P", (W - T_WALL - 0.2, RIGHT_XH_Y0, W + 2.0, RIGHT_XH_Y1),
              OPEN_Z0, OPEN_Z1, "XH2.54-5P (CN3)，兼容 H2 3P / H3 2P"))
    return s


SLOTS = slots()

# 关键器件位置（外壳坐标），供图纸标注
PARTS = {k: (x + SHIFT, y + SHIFT) for k, (x, y) in {
    "CN5/I2C-1": (18.35, 56.56), "CN2/I2C-2": (31.31, 56.56),
    "CN1/I2C-3": (73.90, 56.56), "CN4/I2C-4": (86.86, 56.56),
    "SW1/RESET": (40.59, 62.42),
    "USB1/5V":   (97.41, 20.30), "CN3/XH-5P": (95.01, 43.09),
    "H3/2P":     (91.34, 36.67), "H2/3P":     (91.54, 48.09),
}.items()}

HOLES = [(py + OX, px + OY) for px, py in PCB_HOLES_PXPY]   # PCB 四角 φ4 孔位
ANT_CENTER = (52.6 + SHIFT, 64.5 + SHIFT)                  # (55.60, 67.50)
