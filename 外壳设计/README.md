# ESP32S3-LCD 全覆盖外壳设计（Rev H）

为 **ESP32-S3 + ATK-MD0350 3.5 寸 TFT LCD 底板** 设计的不透明、全覆盖 3D 打印外壳。
当前定稿 **Rev H（2026-11-08）**：上盖顶板完整不镂空，**只保留单一显示窗**，窗口按用户实测的 LCD A.A `73.44 × 48.96` 四周各放大 `0.48 / 0.52 mm` 让位；四边接口统一开口带，天线端从侧壁让位窗伸出壳外；无磁吸，4 颗 M3 螺丝从底部拧紧。

> 打印发给商家用 `.stl`；在 CAD 里看图/改尺寸用 `.step` / `.FCStd`；尺寸依据是 PDF / DXF。
> 完整逐文件索引见同目录 [`文件清单.csv`](文件清单.csv)。

---

## 1. 快速定位

| 我要做什么 | 打开哪个文件 |
|---|---|
| **直接下单打样** | `cad/deliverables/` 里 2 个 `*_3D打印.stl`（唯一上盖 + 底座）+ `ESP32S3_LCD_全覆盖外壳_工程图.pdf` |
| 复制给商家的话、装配顺序、材料禁忌 | `cad/deliverables/给商家的下单说明.txt` |
| 看三视图与全部尺寸 | `cad/deliverables/ESP32S3_LCD_全覆盖外壳_三视图.pdf`（A3，重点看这页） |
| 显示窗与 A.A 的让位关系 | `cad/deliverables/上盖_顶板完整_俯视预览.png`（绿虚线 = A.A，红实线 = 窗口） |
| 实物价格 | `cad/deliverables/外壳实物报价.csv` |
| 用 FreeCAD 打开整套 | `cad/deliverables/ESP32S3_LCD_外壳工程.FCStd`（双击即开，含 3 个命名对象） |
| 在其它 CAD 里改特征 | `cad/deliverables/*_可编辑.step`（AP214 BREP 解析实体） |
| 改尺寸后重出图 | `cad/params_v2.py` → 按第 5 节命令顺序全部重跑 |
| 查历史版本 | `cad/archive_v1/` ~ `archive_v5/`；Rev G 见 git 提交 `9732bd3` |
| 查设计依据/原始资料 | `ref/`（见第 6 节） |

## 2. 目录结构

```
外壳设计/
├── README.md              本说明
├── 文件清单.csv            全量文件索引（分类 / 路径 / 大小 / 用途）
├── .gitignore             局部忽略：__pycache__、*.pyc、*.FCBak 等
├── .gitattributes         锁定 CAD 交换文件行尾，禁止 Git 的 LF/CRLF 自动转换
├── cad/                   外壳建模工作区（脚本按此目录的相对路径运行，勿拆散）
│   ├── deliverables/       ★ 17 个最终交付文件（STL / DXF / PDF / STEP / FCStd / 报价 / 说明）
│   ├── archive_v1 ~ v5/    历次迭代的输出与源码快照（Rev A~F 过程件）
│   ├── preview/            资料 PDF 渲染图、LCM 外形图、用户实物图裁剪
│   ├── preview_v2/         各版 PDF / 三视图 / 3D 预览的目视校验图（含 revh/）
│   ├── params_v2.py        ★ 唯一参数源（尺寸、开窗、螺丝、偏心量、A.A 让位）
│   ├── build_v2.py         STL + DXF + 报价 + 下单说明 + geom_v2.json
│   ├── make_pdf_v2.py      3 页 A4 工程图
│   ├── make_views.py       A3 三视图 PDF / DXF
│   ├── make_preview.py     俯视 / 等距预览 PNG
│   ├── build_step.py       STEP 解析实体（依赖 cadquery / OCP）
│   ├── build_fcstd.py      FreeCADCmd 生成 .FCStd
│   ├── patch_v3~v7.py、patch_views*.py   历次批量修订脚本（一次性，保留备查）
│   ├── build.py / make_pdf.py            Rev A 开放式底座的早期方案
│   ├── geom_v2.json        供 PDF / 三视图读取的几何参数中间产物
│   ├── request.json        最初的原始需求记录
│   └── *.log               构建与分析日志（revg_* / revh_*）
└── ref/                   参考依据与解析中间件
    ├── esp32s3_lcd/        立创 EDA 工程备份解压结果（含 ESP32S3_LCD.epru、project2.json、IMAGE/）
    ├── 输入资料/           用户导出的 PCB PDF + 本项目相关的 2 张用户截图
    ├── crops/ / pcbpdf/    资料 PDF 与 PCB 图的渲染、裁剪、放大图
    └── *.py / *.log        .epru 解析、孔径测量、像素测量脚本与输出
```

## 3. 关键参数（Rev H，单位 mm）

| 项 | 值 |
|---|---|
| 外形 | `105.20 × 67.00 × 16.00`，外圆角 R4.5 |
| 依据 PCB | 板框 `61.80 × 100.00 R2`；4 个安装孔 `Φ4.0`，孔距 `48.70 × 91.34` |
| 壁厚 | 侧壁 1.60 / 底板 2.40 / 顶板 1.80；PCB 到底板内腔单边间隙 1.00 |
| 层叠 Z | PCB 底面 3.40、顶面 5.00；核心板直焊顶面 ≈9.10；LCD 顶面 ≈12.10；顶板内表面 14.20 |
| **实测 LCD A.A** | `73.44 × 48.96`（用户 11-08 游标卡尺实测确认，发光显示区） |
| **显示窗（唯一版本）** | `74.40 × 50.00` R1.5，X `12.65~87.05`、Y `8.50~58.50`；四周各比 A.A **放大** `0.48 / 0.52` |
| 让位目的 | 吸收 3D 打印公差、LCD 排针插装 + `Φ4` 孔配 M3 的位置偏差、偏心量推算误差；**宁露 ≤0.5 极窄黑边，也不切掉亮区像素** |
| 窗口中心 | `X=49.85, Y=33.50`（相对外壳中心**左移 2.75**，`WIN_OFFSET_X = -2.75`，对准偏心屏 A.A） |
| 四边开口带 | 统一 `Z 4.00 ~ 14.20`，天线让位窗与 I2C 插座窗完全平齐；已按带壳插头与线材 `Φ3~5` 留余量 |
| 上边（天线侧） | 天线让位窗 27.00（39.10~66.10）+ 2 段 I2C 合并宽窗 25.10 / 24.90，段间 2.00 加强筋 + 顶板 `Φ4` 复位孔 |
| 下边 / 右边 | 双 Type-C 共用窗 36.00；5V Type-C 18.00、XH2.54-5P 23.00；左边封闭 |
| 固定 | 4 × M3×12 沉头自攻；底座通孔 `Φ3.4`、底面沉孔 `Φ6.5` 深 1.6；上盖 `Φ7` 螺丝柱、柱内 `Φ2.6` 盲底孔 |
| 天线 | 顶板完整不镂空、不透明；天线端由侧壁穿出，外露段不被壳体包住；材料必须绝缘非金属 |
| 磁吸 | **无**（按用户要求全部移除） |

## 4. 版本演进

| 版本 | 主要变化 | 归档 |
|---|---|---|
| Rev A | 开放式低矮底座（65.60×103.80×6.60），无上盖；后被「全覆盖」需求取代 | `cad/archive_v1/`、早期 `build.py` / `make_pdf.py` |
| Rev B | 改为上下盖全覆盖、不透明，只露显示区并压住黑边 | `cad/archive_v2/` |
| Rev C | 增加接口开窗；误把孔径改成 `Φ2`/M2；按用户要求删除磁吸 | `cad/archive_v3/` |
| Rev D | **孔径纠错**：`.epru` 半径 78.7402 mil = 2.000 mm → `Φ4`；用户实测 M3 可用 → 统一 M3、不用 M4 | `cad/archive_v4/` |
| Rev E | 取消 U 形天线敞口（原切除体把顶板挖穿），顶板恢复完整；天线改由侧壁让位窗伸出；新增 A3 三视图 | `cad/archive_v5/` |
| Rev F | 四边统一开口带 `Z 4.00~14.20`、I2C 合并宽窗与线材余量、核心板改为直焊层叠 | `cad/archive_v5/` |
| Rev G | **偏心屏对位**：窗口中心 X 左移 2.75 mm（49.85），Y 不变；A/B 双版窗口 `69.00` / `72.00 × 47.60` | git 提交 `9732bd3`（已被 Rev H 取代） |
| **Rev H** | **删除 A/B 双版本**；用户实测确认 A.A `73.44×48.96`，窗口改为**放大让位** `74.40×50.00`（四周 +0.48/0.52）；只留一个上盖 | `cad/deliverables/`（当前） |

> Rev H 的判断修正：Rev G 的两版窗口都比 A.A 小，"压边"实际压的不是黑边，而是把亮区边缘像素切掉了。既然宁可装配偏差也不遮挡显示内容，窗口应比 A.A 略大而非略小。
> 偏心量依据：LCM 规格书 `OUTLINE 84.69×55.26` / `A.A 73.44×48.96` 长边尺寸链偏心 2.77 mm，短边左右各 3.15 对称；用户实物图逐像素换算 2.52 mm，取 2.75。**打样前务必实测**：量「亮区左缘→模块左缘」= L、「亮区右缘→模块右缘」= R，`(L−R)/2` 即应填的 `WIN_OFFSET_X`（偏左为负）。

## 5. 修改后如何重出全套文件

**依赖**：Python 3.13；`trimesh`、`shapely`、`manifold3d`、`ezdxf`、`reportlab`、`pymupdf`、`matplotlib`、`pillow`、`numpy`、`scipy`；STEP 需要 `cadquery`（含 OCP / OpenCascade）；`.FCStd` 需要本机 FreeCAD 1.1.4 的命令行内核 `C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe`。

工作目录必须是 `cad/`（脚本内全部为相对路径，仓库里保持原目录结构就是为此）：

```bash
cd 外壳设计/cad
python build_v2.py          # STL / DXF / 报价 / 下单说明 / geom_v2.json
python make_pdf_v2.py       # 3 页 A4 工程图
python make_views.py        # A3 三视图 PDF + DXF
python build_step.py        # 3 个 STEP 解析实体（上盖 / 底座 / 装配体）
python make_preview.py      # 俯视 / 等距预览 PNG
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" build_fcstd.py   # .FCStd 工程
```

改任一参数（尤其 `WIN_OFFSET_X`、`WIN_W` / `WIN_H`、`Z_TOP_IN`、开窗宽度）后 **必须六个脚本全部重跑**，否则 STL / STEP / FCStd / PDF / 预览会互相不一致。`build_step.py` 与 `build_v2.py` 共用 `params_v2.py`，几何一致；FreeCAD 宏 `deliverables/FreeCAD_一键生成工程.FCMacro` 只补颜色与视角，不改变几何。
`patch_v7.py` 是 Rev G→H 的**一次性**批量修订记录，不要重复执行。

## 6. 设计依据资料

| 依据 | 位置 |
|---|---|
| ESP32-S3 开发板尺寸与天线位置（63.39×27.94，匹配 U1/U2） | 仓库 `硬件资料/YD-ESP32-S3资料/ESP32-S3-Metric.pdf` |
| LCD 模块机械尺寸、LCM 外形与 AA 可视区 | 仓库 `硬件资料/【正点原子】3.5寸TFT LCD.../3.5寸液晶屏V2规格书.pdf`、`正点原子3.5寸屏ST7796规格书.pdf`；渲染图见 `cad/preview/` |
| **A.A 实测确认（73.44×48.96）** | 用户 11-08 游标卡尺实测，已写入 `cad/params_v2.py` 的 `LCD_AA_X / LCD_AA_Y` |
| PCB 板框、孔位、元件坐标、装配层 | `ref/esp32s3_lcd/ESP32S3_LCD.epru`（立创 EDA 工程备份解压）、`ref/输入资料/PCB_PCB1_1_2026-11-07_用户导出.pdf`、`ref/输入资料/用户截图_PCB图层与装配尺寸.png` |
| 偏心屏实物（左黑边窄、右黑边宽） | `ref/输入资料/用户截图_LCD实物_偏心黑边.png` |
| 解析过程与测量记录 | `ref/*.py`、`ref/*.log`、`ref/crops/`、`ref/pcbpdf/` |

## 7. 打样与报价（只算外壳实物）

PCB 打样、LCD 屏、ESP32 系统板**均已自备，不计入**。整套约 `27.66 cm³`（窗口放大后比 Rev G 少约 0.79 cm³）。

| 方案 | 价格 |
|---|---|
| FDM 经济（上盖 + 底座 + M3 螺丝 + 运费） | ¥40~65；含硅胶脚垫 ¥41~67 |
| SLA 光敏树脂整套 | ¥65~110 |
| 小批量 5 套 FDM | ¥110~170（¥22~34/套） |

淘宝搜：`3D打印服务 代打`、`FDM 3D打印 PETG 定制`、`3D打印 光敏树脂 打样`、`嘉立创3D打印`。
材料：不透明 PLA / PETG / 光敏树脂；**禁止**金属打印、碳纤填充、导电料、金属漆、电镀（会屏蔽 2.4 GHz 天线）。
打样前必测两项：① 偏心量决定 `WIN_OFFSET_X`（当前 −2.75 仍为推算值）；② PCB 顶面到整机最高点须 <9.20 mm。亮区尺寸已实测确认，不再需要选 A/B 版。
**转告商家**：显示窗 `74.40×50.00` 已按实测 A.A 放大让位，请勿擅自缩小窗口或把窗口移回居中。

## 8. 已知限制与注意

- **没有 DWG**：官方 CAD 云端服务当时不可用（`CAD_LLMROUTER_UNAVAILABLE`），交付的是 **DXF R2010 / mm（`INSUNITS=4`）**，可在 AutoCAD / 立创 EDA 里另存为 DWG；DXF 是二维工程图，不含 3D 实体。
- **扩大窗口的取舍**：理想装配下四周会露出 ≤0.5 mm 极窄黑边（左侧原黑边约 2.86、右侧约 8.39，绝大部分仍被顶板压住）；换来的是任何装配偏差下都不会遮挡显示内容。若追求「一丝黑边都不露」，把 `WIN_W/WIN_H` 改回等于或略小于 A.A 即可，但会恢复切亮区风险。
- **打印以 STL 为准**；STEP（AP214 BREP）与 `.FCStd` 用于 CAD 看图、测量、改特征。装配体 STEP / FCStd 里的 `PCB_Reference` 只是间隙检查参考件，**不是打印件**。
- `.FCStd` 由命令行内核生成，不含 GuiDocument（颜色 / 相机）；想要着色版执行 FreeCAD 宏即可。
- 顶板天线区不开洞、不加支撑；天线端朝外或悬出安装面边缘，避免整块金属背板贴近。
- 若此 GitHub 仓库为公开仓库：`ref/esp32s3_lcd/ESP32S3_LCD.epru` 是完整 EDA 工程源数据，`ref/输入资料/` 含 PCB 导出图，请确认是否愿意公开后再推送。
- 会话中的 3 张 SD 卡克隆报错截图与本项目无关，未归档。
