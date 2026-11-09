# 论文第 4 章实验协议

## 研究对象与设计

数据为二维合成 Gaussian 样本，分布为 \(N(0,\operatorname{diag}(1,\tau))\)。参数网格为
`tau = {0.2, 0.5, 0.8}`、`n = {60, 180, 540, 1620}`，每个组合生成 40 份独立数据，共 480 份。伪随机数生成器种子为 `20261105`。每个数据集在生成后按样本均值中心化，并从三中心总体固定构形初始化。聚类容量相等，每簇为 `n/3`。

固定中心时，将每个中心按容量展开成槽位，构造平方距离成本矩阵，再调用 `scipy.optimize.linear_sum_assignment` 求精确容量指派；固定分组后以簇内均值更新中心。相邻两次指派完全相同作为停止判据，最多 100 次指派更新。

## 观测量和阈值

沿归一化高模态 \((1,-2,1)/\sqrt 6\) 计算中心形状投影振幅，以绝对振幅首次达到 `0.4` 作为描述性阈值命中。阈值受更早的探索性模拟启发，并在本次 follow-up 模拟前固定；研究未预注册。它不是理论局部谱的 `1/3` 分界，也没有与理论切空间坐标建立定量对应。

`stabilization_iteration` 记录首次检测到相邻标签重复的指派调用；返回固定点状态是该序号前一轮中心更新。因此严格终态前命中定义为
`first_hit_iteration < stabilization_iteration - 1`；恰在返回终态首次命中则定义为相等。两类事件在逐数据集记录和汇总中分开。

命中比例以 40 份独立数据集为二项试验单位，报告 Wilson 95% 区间。条件命中迭代次数仅在严格终态前发生命中的数据集上定义，报告中位数及 5,000 次数据集 bootstrap 百分位 95% 区间。无命中组不定义条件中位数。

## 输出与论文对应

- `results/lloyd_finite_sample/escape_time_by_dataset.csv`：480 行数据集级首达与终态分类。
- `results/lloyd_finite_sample/escape_time_trajectories.csv`：每份数据逐次形状高模态振幅。
- `results/lloyd_finite_sample/escape_time_summary.csv`：12 组已保存汇总统计，论文图 3、图 4 的唯一绘图数据源。
- `results/lloyd_finite_sample/escape_time_metadata.json`：随机种子、参数、依赖版本及运行元数据。

本仓库的默认复现路径是读取保存 CSV、验证分类与汇总关系并重画图 3、图 4；完整 480 份模拟是可选项，不是复建现有论文图表的前置步骤。
