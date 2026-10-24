# v9 准备流程精简候选（仅本地）

基于v8直接Sport半米入口，运动参数及独立watchdog保持不变。将父进程观测与子进程启动重叠，删除固定1秒等待；连续0.5秒通道检查在启动期间完成。图像/原始点云归档通过`--capture-evidence`按需启用，实时通道检查始终运行。删除归档额外0.8秒等待，仅输出最终一行结果。

验证：4项`test_fast_prepare`通过；全部Python文件语法检查通过。无线及有线SSH超时，尚未上传，机器人端回归测试和prepare-only计时未完成，没有实机执行。不能称为已验证的提速版本。

未来同步后，先在机器人上运行只读准备（不会调用Move或切换模式/避障）：

```bash
python3 go2_control.py --prepare-only --out /home/unitree/agentic_go2/body_control/runs/NEW_FAST_PREPARE
```

原执行入口仍保留既有显式参数；本文不授权执行。不要复跑历史终止的批次。下一步应先验证准备耗时，避免继续堆叠诊断版本。
