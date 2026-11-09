# 数据字典

## `escape_time_summary.csv`（12 行）

| 字段 | 含义 |
|---|---|
| `tau` | 横向 Gaussian 方差参数 |
| `sample_size` | 每份独立数据集的样本数 `n` |
| `datasets` | 该条件的数据集数（40） |
| `mode_threshold` | 描述性绝对高模态阈值（0.4） |
| `population_high_mode_multiplier` | 总体局部谱中的 `3*tau` |
| `hit_count`, `hit_fraction` | 严格终态前命中数和比例 |
| `terminal_state_hit_count` | 恰在返回终态首次越阈的数量 |
| `hit_fraction_wilson95_low/high` | 命中比例的 Wilson 95% 区间端点 |
| `median_hit_iteration_given_hit` | 严格终态前命中数据集的条件中位迭代数；无命中时为空 |
| `median_hit_bootstrap95_low/high` | 条件中位数的 5,000 次数据集 bootstrap 百分位区间 |
| `hit_iteration_q25/q75` | 命中迭代数的四分位数 |
| `mean_stabilization_iteration` | 重复指派检测调用序号的均值 |
| `candidate_log_n_slope` | 原探索性候选预测的数值列；不作为课程稿定理或作图依据 |

## `escape_time_by_dataset.csv`（480 行）

每行对应一个 `(tau, sample_size, replicate)` 数据集。包括首个命中迭代、严格终态前/终态命中布尔标记、重复标签检测序号、首次更新振幅和返回终态振幅。空的 `first_hit_iteration` 表示未观察到阈值命中。

## `escape_time_trajectories.csv`

每行对应一个数据集在一个更新步的有符号及绝对高模态投影振幅，并附该组阈值。它是合成数据算法轨迹，不含个人或真实个体数据。

## `escape_time_metadata.json`

记录实验设计、阈值选择历史、随机种子、软件版本、停止规则、统计不确定性计算方式和生成文件列表。`runtime_seconds` 是原始运行记录，不是未来机器上的耗时保证。
