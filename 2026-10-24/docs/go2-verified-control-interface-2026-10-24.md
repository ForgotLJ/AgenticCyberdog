# Go2 当前控制入口与验证边界

最新补充：v8直接前进已实现0.496米，但状态速度保护触发，不能标为严格验收通过。v9准备提速候选仅本地，未上传/实机验证。今天已按用户要求结束，详见[收尾与续接](go2-day-end-2026-10-24.md)。下文四段验收后的接口仍是已部署历史版本。

更新：2026-10-24四段验收结束后。供狗上Agent续接使用；本文是接口和证据，不是新增运动授权。

## 能力状态

| 能力 | 当前证据 | 可作出的结论 |
| --- | --- | --- |
| 经典步态直接Sport左10° | +10.963°，全程最大平移2.7736厘米，停止/模式/避障恢复通过 | 单次通过 |
| 同配置右10° | −10.299°，全程最大平移2.5475厘米，停止/模式/避障恢复通过 | 单次通过 |
| 避障开启前进0.5米 | 历史0.522/0.517米通过；最新79条请求无下游非零速度，进度不足1毫米 | 间歇成功，尚不稳定 |
| 前进→左转→前进 | 最新在首个前进段停止 | 未通过 |

数据来自里程计/IMU，不是外部测量真值；不要把发送返回0当成实际运动。

## 转向入口

代码目录：`/home/unitree/agentic_go2/body_control/runs/20261024-classic-turn-candidate/`。

默认查看固定计划，不初始化DDS：

```bash
python3 /home/unitree/agentic_go2/body_control/runs/20261024-classic-turn-candidate/go2_control.py --turn left
```

在当前任务已获对应物理运动授权、现场条件和当段图像/几何检查成立后，单次执行：

```bash
python3 /home/unitree/agentic_go2/body_control/runs/20261024-classic-turn-candidate/go2_control.py \
  --execute --allow-temporary-avoidance-off --allow-classic-mode \
  --turn left --out /home/unitree/agentic_go2/body_control/runs/NEW_UNIQUE_TURN
```

右转把`left`改为`right`。目录必须全新，不自动重试；批次内传`--stop-root BATCH_DIRECTORY`保留整批遥控接管锁定。

固定契约：起始状态100且静止、原避障开启；独立看门狗就绪后识别自己的Sport来源，暂时关规划避障，再调用ClassicWalk(True)，确认新鲜2010静止持续至少0.15秒后发送纯yaw ±0.25 rad/s。非零最多2.5秒，准备及动作总期限4秒，目标10°，3厘米平移触发，原姿态/速度/新鲜度/故障/遥控保护保留。StopMove后要求回到原100、确认静止、释放输入并恢复避障。

`diagnostic_result.json`是转向最终验收：`passed`、`signed_yaw_deg`、`max_displacement_including_braking_m`、`stop_confirmed`、`classic_mode_confirmed`、`original_fsm_restored`、`original_avoidance_restored`。需要等最终文件及执行进程结束，不能仅看较早的`summary.json`。

运动中的软件停止可创建当前执行目录或批次目录的`STOP`文件；看门狗监测并收尾。它不替代实体遥控接管，也不保证设备/系统失效时仍有效。

## 前进和组合

原前进入口及`efficient_freeze.json`保持不变，不将其本轮失败自动改写为“修复”。最新四段调度器`acceptance_batch.py`的原始批次已经终止，不能沿用之前授权重启。不要扩大速度、期限、位移阈值，或把转向暂时关规划避障的授权扩展到前进。

## 状态与官方语义

使用官方V2的`SportModeState.error_code`：100为灵动，2010为经典，1001为阻尼；不要按旧文档单独解释`mode=0`。实时服务API版本`1.0.0.1`不是精确固件版本。`Move`采用no-reply，发送成功不代表执行；以实际状态和最终停止证据判定。

避免每次重读所有源码和重复探测：先看本文件、当前任务授权和对应最新结果，再核对冻结哈希及一次新鲜现场观测。只有出现具体失败证据才回到原始日志。

报告：`/home/unitree/agentic_go2/body_control/runs/20261024-classic-left-once/README.md`及`/home/unitree/agentic_go2/body_control/runs/20261024-classic-four-stage/README.md`。
