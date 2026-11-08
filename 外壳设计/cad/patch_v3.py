# -*- coding: utf-8 -*-
"""把 Rev B 脚本批量修订为 Rev C：M3→M2、去磁吸、天线敞口 24.5→27.0、版本号。"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))

GLOBAL = [
    # 变量名中性化（先长后短）
    ("M3_CS_DEPTH", "SCREW_CS_DEPTH"),
    ("M3_HOLE_D", "SCREW_HOLE_D"),
    ("M3_CS_D", "SCREW_CS_D"),
    # 螺丝规格
    ("M3×12", "M2×10"), ("M3x12", "M2x10"),
    ("M3*12", "M2*10"),
    ("M3 自攻螺丝", "M2 自攻螺丝"),
    ("M3 沉头螺丝", "M2 沉头螺丝"),
    ("M3 沉头", "M2 沉头"),
    ("M3 螺丝", "M2 螺丝"),
    # 直径（按 M2 与 φ2 PCB 孔）
    ("Φ7", "Φ5"), ("Φ2.6", "Φ1.6"), ("Φ3.4", "Φ2.4"), ("Φ6.5", "Φ4.4"),
    ("4× Φ4 孔", "4× φ2 孔"), ("4x Φ4 孔", "4x φ2 孔"),
    ("4×Φ4", "4×φ2"), ("4× Φ4", "4× φ2"), ("4x Φ4", "4x φ2"),
    ("Φ4 孔", "φ2 孔"),
    ("深 1.6 沉孔", "深 1.2 沉孔"),
    # BOM / 报价
    ('"5", "硅胶脚垫"', '"4", "硅胶脚垫"'),
    ("遮住螺丝头/磁铁孔", "遮住螺丝头"),
    # 天线敞口加宽
    ("24.50 天线敞口", "27.00 天线敞口"),
    ("24.5 mm 宽天线敞口", "27.0 mm 宽天线敞口"),
    ("天线敞口 24.5 mm", "天线敞口 27.0 mm"),
    ("24.5 mm", "27.0 mm"),
    ("24.50", "27.00"),
    # 版本
    ("Rev B", "Rev C"),
    ("ESP32S3-LCD-EN-B", "ESP32S3-LCD-EN-C"),
]

# 行级：包含关键词 → 用新文本替换整行（保留前导空白）；None = 删除该行
CONTAINS = [
    ("底座（平板 + 4 支撑台 + 4 沉孔，可选磁吸）", "底座（平板 + 4 支撑台 + 4 沉孔）"),
    ("【六、天线与磁吸】", "【六、天线净空】"),
    ("天线净空与磁吸", 'T("天线净空", IX, 184, 9, BLUE)'),
    ("近场 20mm 内禁金属", 'T("近场 20mm 内禁金属 / 覆铜", IX, 176, 6.6, REDC)'),
    ("4 螺丝柱 + 4 磁吸孔", 'T("4 个螺丝柱距天线中心 >45mm", IX, 144, 6.2, INK)'),
    ("壳体绝缘塑料不屏蔽；最大风险", 'T("壳体绝缘塑料不屏蔽；天线端朝外或悬出边缘", IX, 137, 6.4, REDC)'),
    ("4 个螺丝柱与 4 个磁吸孔距天线中心", "4 个螺丝柱距天线中心均 >45 mm，远超 2.4GHz 近场 20 mm。"),
    ("建议天线端朝外或悬出安装面；若常吸铁面", "建议天线端朝外或悬出安装面边缘。"),
    ("4. 天线投影 20mm 内禁止金属件", "4. 天线投影 20mm 内禁止金属件、覆铜；4 个螺丝柱距天线中心均 >45mm。"),
    ('FOOTER("注：4 个螺丝柱与 PCB', 'FOOTER("注：4 个螺丝柱与 PCB 4×φ2 孔同轴；靠 4 颗 M2 螺丝从底部固定。")'),
    ("红实线 Φ2.4 通孔", 'T("红实线 Φ2.4 通孔 / 蓝虚线 Φ4.4 沉孔 / 灰虚线 Φ5 支撑台",'),
    ("磁吸孔为可选项", 'T("靠 4 颗 M2 螺丝固定；可加脚垫遮螺丝头", IX, 100, 6.6, GREEN)'),
    ('["合计 · 含可选件"', '["合计 · 含脚垫", "再加脚垫", "1台", "", "42~68", ""],'),
    ("MAG_POS=P.MAG_POS, PARTS=P.PARTS,", "PARTS=P.PARTS,"),
    ("MAG_D=P.MAG_D, ANT_CENTER", "ANT_CENTER=list(P.ANT_CENTER),"),
    ("硅胶脚垫 Φ8 x4（可选）", "硅胶脚垫 Φ8 x4（可选）     搜：硅胶脚垫 圆形 自粘 8mm"),
    # 删除类
    ("for x, y in P.MAG_POS:", None),
    ("cuts.append(cyl(P.MAG_D", None),
    ("for x, y in MAG:", None),
    ('CIRCLE(BX + x, BY + y, G["MAG_D"]', None),
    ("MAG = G[", None),
    ("钕铁硼", None),
    ("磁吸沉孔", None),
    ("去掉磁铁", None),
    ("吸铁板", None),
    ("磁吸孔", None),
    ("磁铁", None),
    ("磁吸", None),
]

for fn in ("build_v2.py", "make_pdf_v2.py"):
    path = os.path.join(HERE, fn)
    src = open(path, encoding="utf-8").read()
    counts = {}
    for a, b in GLOBAL:
        n = src.count(a)
        if n:
            src = src.replace(a, b)
            counts[a] = n
    out, dropped = [], 0
    for line in src.split("\n"):
        hit = False
        for key, repl in CONTAINS:
            if key in line:
                if repl is None:
                    dropped += 1
                else:
                    indent = re.match(r"\s*", line).group(0)
                    out.append(indent + repl)
                hit = True
                break
        if not hit:
            out.append(line)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print(f"=== {fn}: 全局替换 {sum(counts.values())} 处 / 行级删除 {dropped} 行 ===")
    for k, v in counts.items():
        print(f"   {k!r} -> {v}")
    # 残留检查
    left = [(i + 1, l.strip()) for i, l in enumerate(out)
            if re.search(r"磁吸|磁铁|钕铁硼|M3|Φ7|Φ8|Φ3\.4|Φ6\.5|Φ2\.6|Φ4 孔", l)]
    print("   残留可疑行:", left[:15] if left else "无")
