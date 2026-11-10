# -*- coding: utf-8 -*-
"""用本机 FreeCAD 1.1.4 的命令行内核生成可直接双击打开的 .FCStd 工程文件。

运行：
  "C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe" build_fcstd.py

生成的文档含 3 个命名实体对象：
  TopCover     上盖（打印件）
  Base         底座（打印件）
  PCB_Reference  PCB 参考板（不打印，用于检查间隙）

FreeCADCmd 是纯控制台模式，没有 GuiDocument（颜色 / 相机），
几何与对象名完整；着色版可运行 FreeCAD_一键生成工程.FCMacro 补上。
"""
import os
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "deliverables")

TOP_FILE = "ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step"
BASE_FILE = "ESP32S3_LCD_全覆盖外壳_底座_可编辑.step"
ASSY_FILE = "ESP32S3_LCD_全覆盖外壳_装配体_含PCB参考.step"
OUT_FILE = "ESP32S3_LCD_外壳工程.FCStd"


def read_shape(path):
    """读 STEP 返回 TopoShape；FreeCAD 1.1 的 Part.read 支持 STEP。"""
    if not os.path.isfile(path):
        raise RuntimeError("missing STEP: %s" % path)
    try:
        return Part.read(path)
    except Exception:
        tmp = App.newDocument("_step_tmp")
        Part.insert(path, tmp.Name)
        shapes = [o.Shape for o in tmp.Objects if hasattr(o, "Shape")]
        result = Part.makeCompound(shapes)
        App.closeDocument(tmp.Name)
        return result


def single_solid(shape, tag):
    solids = shape.Solids
    if len(solids) != 1:
        raise RuntimeError("%s: expect 1 solid, got %d" % (tag, len(solids)))
    return solids[0]


def find_pcb(assy):
    """PCB 参考板 Z 范围 3.4~5.0；上盖 2.4~25.1，底座 0~3.4。"""
    for s in assy.Solids:
        bb = s.BoundBox
        if abs(bb.ZMin - 3.4) < 0.05 and abs(bb.ZMax - 5.0) < 0.05:
            return s
    return None


def add(doc, name, label, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    return obj


def main():
    print("FreeCAD:", App.Version()[0], App.Version()[1])
    print("GuiUp:", App.GuiUp)

    doc = App.newDocument("ESP32S3_LCD_Enclosure_RevI")
    doc.Label = "ESP32S3_LCD Enclosure Rev I"

    add(doc, "TopCover", "上盖（打印件）",
        single_solid(read_shape(os.path.join(OUT_DIR, TOP_FILE)), "top"))
    add(doc, "Base", "底座（打印件）",
        single_solid(read_shape(os.path.join(OUT_DIR, BASE_FILE)), "base"))

    pcb = find_pcb(read_shape(os.path.join(OUT_DIR, ASSY_FILE)))
    if pcb is not None:
        add(doc, "PCB_Reference", "PCB 参考板（不打印，仅检查间隙）", pcb)
    else:
        print("WARNING: PCB reference solid not found")

    doc.recompute()
    out = os.path.join(OUT_DIR, OUT_FILE)
    doc.saveAs(out)
    print("saved:", out)

    for obj in doc.Objects:
        sh = obj.Shape
        bb = sh.BoundBox
        print("  %s | solids=%d valid=%s vol=%.2f cm3 | "
              "X %.2f~%.2f Y %.2f~%.2f Z %.2f~%.2f"
              % (obj.Name, len(sh.Solids), sh.isValid(), sh.Volume / 1000.0,
                 bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))

    App.closeDocument(doc.Name)

    # 回读验证：确认 .FCStd 能被 FreeCAD 重新打开且几何完好
    again = App.openDocument(out)
    objs = [o for o in again.Objects if hasattr(o, "Shape")]
    print("REOPEN: %d objects" % len(objs))
    ok = len(objs) == 3 and all(
        len(o.Shape.Solids) == 1 and o.Shape.isValid() for o in objs)
    print("REOPEN CHECK:", "PASS" if ok else "FAIL")
    App.closeDocument(again.Name)
    print("DONE", "PASS" if ok else "FAIL")


main()
