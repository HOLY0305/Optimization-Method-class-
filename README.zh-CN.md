# 固定容量 Lloyd 课程论文复现材料

[English](README.md) | [简体中文](README.zh-CN.md)

本仓库提供课程论文《固定容量 Lloyd 算法的优化建模与局部稳定性分析》第 4 章所用代码和已保存的合成数据结果。默认流程可以校验逐数据集记录，并从已保存的汇总 CSV 重画论文中的两张实验统计图；无需重新运行 480 组模拟。

完整的单栏课程论文 PDF 和论文中的六张图也已收录在 [paper/](paper/)：可[下载完整论文](paper/PAPER_LLOYD_COURSE_P10_1.pdf)。六张图均提供可编辑 SVG 和 300 dpi PNG 版本。

## 环境

- Python 3.13.9（记录的模拟运行使用此版本）
- 安装固定版本依赖：

```powershell
python -m pip install -r requirements.txt
```

绘图脚本需要支持中文的字体。记录运行的 Windows 环境使用 Microsoft YaHei；在其他系统上，请安装可用的中文字体，或修改绘图脚本中的字体设置。

## 快速复现已保存结果

在仓库根目录依次运行：

```powershell
python checks/verify_saved_results.py
python scripts/plot_paper_figures.py
```

第一条命令校验 480 条逐数据集记录、严格终态前命中与终态命中的分类边界，以及 12 组汇总结果。它不会重新运行 Lloyd，也不会重新计算置信区间。

第二条命令读取 `results/lloyd_finite_sample/escape_time_summary.csv`，在 `figures/lloyd_finite_sample/` 下生成命中比例图 `fig03_empirical_hit_fraction` 和条件命中迭代次数图 `fig04_conditional_hit_iterations`，每张图均输出 PNG 和 SVG。

## 可选：重新运行完整模拟

如需根据固定随机种子重新生成实验数据，可运行：

```powershell
python experiments/lloyd_finite_sample/escape_time_study.py
```

该脚本会运行 480 份独立数据，并覆盖 `results/lloyd_finite_sample/` 下的 CSV 与元数据。归档运行约耗时 597 秒，实际时间取决于硬件和软件环境。完整的逐数据集记录、轨迹和汇总 CSV 总大小小于 300 kB。重新模拟后，可以再次运行上面的校验和绘图命令。

## 仓库内容

```text
checks/        校验已保存的逐数据集记录和汇总结果
docs/          实验协议与数据字典
experiments/   Lloyd 模拟程序及共享实现
figures/       第 4 章实验图表（PNG 与 SVG）
paper/         完整单栏论文 PDF 与六张论文插图源文件
results/       逐数据集记录、轨迹、汇总 CSV 和元数据
scripts/       根据已保存汇总数据绘制论文图表
```

参数网格、停止规则、事件计数、随机种子、置信区间、数据字段及其与论文的对应关系，见 [`docs/PAPER_EXPERIMENT_PROTOCOL.md`](docs/PAPER_EXPERIMENT_PROTOCOL.md) 和 [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md)。

## 数据说明与研究范围

数据为二维 Gaussian 合成样本及其算法轨迹，不含个人数据。阈值 `0.4` 受早期探索性模拟启发，并在本次后续模拟前固定；研究未预注册该阈值。它是描述性指标，不等同于局部谱分析中的 `1/3` 分界。

默认复现流程只校验已保存结果并重画图表，不声称独立重跑了完整模拟，也不把有限样本结果作为总体局部稳定性结论的证明。仓库 paper/ 目录保存完整单栏课程论文和六张最终插图；实验复现代码与已保存的合成结果对应第 4 章；较早的探索性分析及与本文无关的高阶研究输出不在此仓库中。

Python 源代码采用 MIT 许可证，见 [`LICENSE`](LICENSE)。论文 PDF、合成数据、图表和文档采用 CC BY 4.0，见 [`DATA_LICENSE.md`](DATA_LICENSE.md)。
