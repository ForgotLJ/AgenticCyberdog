# Unitree Go2 官方与社区仿真环境核查

核查日期：2026-10-24。证据来自官方 GitHub 仓库、当前源码、维护者支持表和发布记录。本次没有安装仿真器、运行控制策略或连接机器人；下文区分“官方支持”“维护者报告验证”和“本机实测”，不把前两者表述为本机跑通。

**结论：Go2 有官方仿真环境，也有公开控制器和维护者真机验证记录的社区方案。** 官方优先考察 `unitree_mujoco` 和 `unitree_rl_lab`；如果想尽快获得能行走并接受高层速度指令的仿真 Go2，可优先考察 `rl_sar`。

最重要的边界是：**Go2 模型、关节级 SDK 仿真、可行走的控制策略、原厂高层运动服务是四件不同的事。** 不能因为模型能加载或有 `SportModeState` 状态消息，就认为真机的 `SportClient.Move()`、避障、相机取流等服务已被完整仿真。

| 方案 | 来源与 Go2 支持证据 | 可以直接利用的部分 | 优势 | 局限及适用判断 |
|---|---|---|---|---|
| **[unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco)** | 宇树官方；有 Go2 MJCF、场景和 C++ / Python / ROS 2 站立示例 | MuJoCo 物理仿真；SDK2 / DDS 的 `LowCmd`、`LowState`、`SportModeState`；简单地形生成工具 | 官方协议适配明确；适合关节控制、控制器调试和 sim-to-real 接口准备；相对完整 Isaac 场景栈更轻 | README 明确说当前主要支持低层开发。默认示例不是完整行走控制器，不能直接视作原厂 SportClient 服务替身；视觉导航的传感器和任务层需另补 |
| **[unitree_rl_lab](https://github.com/unitreerobotics/unitree_rl_lab)** | 宇树官方；明确支持 Go2；源码注册 `Unitree-Go2-Velocity`，有 `deploy/robots/go2/` | Isaac Lab 中的 Go2 速度跟踪训练、回放、控制器部署；配合官方 MuJoCo 做 sim-to-sim | 官方训练与部署路线；训练和机器人动作接口比仅有模型更完整；适合研究步态和底层策略 | 需要 Isaac 环境及模型资产；Go2 部署配置默认指向自己的训练日志目录，本轮未找到仓库自带 Go2 策略权重或 release 权重包。README 的主要部署演示是 G1，不能拿它代替 Go2 实测证据 |
| **[Isaac Lab](https://github.com/isaac-sim/IsaacLab)** | NVIDIA / Isaac Lab 官方框架，非宇树维护；当前源码明确注册 Go2 平地和粗糙地形速度跟踪环境 | 标准化 RL 环境、地形、奖励、训练算法配置和传感器扩展 | 通用机器人学习生态较完整；适合并行训练、系统性控制实验和后续扩展 | 不是 Go2 原厂固件仿真；训练任务不自动等于语言导航任务。不同版本的路径、任务名和接口会变化，要与上层项目固定匹配 |
| **[rl_sar](https://github.com/fan-ziqi/rl_sar)** | 社区项目；维护者支持表明确标注 Go2 在 Gazebo / MuJoCo / 真机可用；有 Go2 配置、策略文件和实机控制代码 | 预训练行走策略、C++ 仿真和部署程序；Gazebo 的 ROS 1 / ROS 2 路径具有 `/cmd_vel` 订阅及导航模式 | **较适合快速做能走的 agent 原型。** 仓库中有 `policy/go2/himloco/himloco.pt` 和 `policy/go2/robot_lab/policy.pt`，不只给空模型；有版本发布和 Docker 支持 | 非宇树官方；“真机可用”是维护者报告，本次未独立复现。它使用自己的运动策略，不能假设与原厂控制器响应相同；Python 版暂停维护，优先按当前 C++ 路线使用；Gazebo 路径依赖 Classic |
| **[VLN-CE-Isaac / NaVILA](https://github.com/yang-zj1026/VLN-CE-Isaac)** | 研究团队公开平台；Go2 导航环境、低层策略、数据入口和评测脚本明确 | 语言指令导航，室内场景，SR / SPL / NE 等指标 | 对当前 agent benchmark 项目最直接；同时具备物理本体和任务集 | 仓库固定 Isaac Sim 4.1.0 / 修改版 Isaac Lab 1.1.0；文档明确提示新版本兼容性未知；它是特定研究协议，不是通用官方 Go2 SDK 模拟器 |

**官方 MuJoCo 的证据最明确，但需补行走控制器。**

官方 README 原文：

> Current version only supports low-level development, mainly used for sim to real verification of controller.

其 C++ 文档提供了 `./unitree_mujoco -r go2 -s scene_terrain.xml` 启动示例，仓库还有 `example/python/stand_go2.py`、`example/cpp/stand_go2.cpp` 和 ROS 2 示例。这里的站立/趴下演示证明了低层接口使用方式；并不等于已经提供完整的导航、行走、避障服务。

源码和文档入口：

- [Go2 模型与场景](https://github.com/unitreerobotics/unitree_mujoco/tree/main/unitree_robots/go2)
- [Go2 Python 低层示例](https://github.com/unitreerobotics/unitree_mujoco/blob/main/example/python/stand_go2.py)
- [官方 RL Lab 的 Go2 训练任务](https://github.com/unitreerobotics/unitree_rl_lab/tree/main/source/unitree_rl_lab/unitree_rl_lab/tasks/locomotion/robots/go2)
- [官方 RL Lab 的 Go2 部署目录](https://github.com/unitreerobotics/unitree_rl_lab/tree/main/deploy/robots/go2)
- [Go2 部署配置：策略目录指向训练日志](https://github.com/unitreerobotics/unitree_rl_lab/blob/main/deploy/robots/go2/config/config.yaml)

**几个容易混淆的项目与版本问题：**

| 项目 / 问题 | 本轮查到的事实 | 判断 |
|---|---|---|
| [unitree_sim_isaaclab](https://github.com/unitreerobotics/unitree_sim_isaaclab) | 是宇树官方，但 README 当前明确介绍的是 G1 / H1-2 任务；本轮目录检索未找到 Go2 专用实现 | 不应因为名称含 Unitree 和 Isaac Lab 就将其列为已支持 Go2 的首选环境；Go2 优先查 `unitree_rl_lab` |
| [unitree_rl_gym](https://github.com/unitreerobotics/unitree_rl_gym) | 官方旧 Isaac Gym 路线，确实有 Go2 训练配置；但当前 `deploy/pre_train/` 和 `deploy/deploy_mujoco/configs/` 查到的是 G1/H1/H1_2，未查到 Go2 对应文件 | 可以研究/复用训练，但不能声称当前仓库已提供 Go2 的整套预训练 sim-to-sim 部署包；新训练项目优先考察 RL Lab |
| [unitree_ros](https://github.com/unitreerobotics/unitree_ros) | 官方 Go2 URDF 和 Gazebo 文件存在；README 明确提示 Gazebo 仿真提供低层关节控制，不包含高层走路控制 | 官方机器人模型与低层仿真基础，不是开箱即用的自主导航系统 |
| [MuJoCo Menagerie Go2](https://github.com/google-deepmind/mujoco_menagerie/tree/main/unitree_go2) | Google DeepMind 维护的模型集合；Go2 MJCF 从宇树公开 URDF 派生，包含简化接触模型 | 可作为可信来源明确的模型资产，不应称作“宇树官方完整控制环境”或“原厂行为等价数字孪生” |
| Isaac Lab 版本匹配 | 查到 [Isaac Lab 3.0.0](https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0) 于 2026-10-20 发布；但 Unitree RL Lab README 仍标注 Isaac Sim 5.1.0 / Isaac Lab 2.3.0 | 不把“最新 Isaac Lab”直接与旧项目拼接；复现宇树项目先按其声明的版本配置，新版本兼容性另外验证 |
| Gazebo Classic | [官方页面](https://classic.gazebosim.org/)标明已于 2025-01 结束生命周期；rl_sar 的 Gazebo 路线使用 Classic | 现有项目仍可复用，但长期新平台要考虑维护成本；不能把 Classic 和新版 Gazebo 当成可直接替换的依赖 |

**对 Agent4CyberDog / Go2 项目的选型建议：**

1. **想最快做 agent 调用速度指令、控制一只会走的虚拟 Go2：优先考察 `rl_sar`。** 使用固定预训练运动策略，把 agent 的前进、转向、停止等工具接到控制层。已核实的 `/cmd_vel` 接口属于其 ROS / Gazebo 路线；若选 MuJoCo 路线，需单独确认或补上 agent 到控制器的适配，不假设两者接口相同。
2. **想保留宇树 SDK2 的低层通信结构：选择 `unitree_mujoco`，另外配一个经过验证的 Go2 控制器。** 官方 `unitree_rl_lab` 有 Go2 训练/部署代码，但仍需准备相应训练结果，不能直接假设已提供现成权重。
3. **想训练或改进步态、地形通过能力：选择 `unitree_rl_lab` 或 Isaac Lab 的 Go2 任务。** 这是控制策略研发路线，工作量高于直接使用已有步态。
4. **想马上做语言导航 benchmark：继续使用 NaVILA / VLN-CE-Isaac 这类已有任务集的平台。** 通用模拟器解决物理和接口，benchmark 还要额外提供固定任务、成功检查及统计协议。

为保证 agent 对比有意义，建议固定低层行走策略，并分别报告仿真控制器与真机原厂控制器的差别。RGB 观察、相机位姿、目标物体、动作超时和任务成功判定也要明确；这些不会因为选了官方物理模拟器就自动齐全。

**最低运行验证应包含：** 加载 Go2；控制器接入并稳定站立；前进和转向指令产生实际位移；归零/停止行为符合定义；需要视觉时能读取有时间戳的图像；重置和重复运行可复现。这是后续安装验证标准，不是本次已经完成的测试。

本轮来源快照位于 `data/go2-simulation-survey-2026-10-24/`，保存了 README、源码片段、仓库目录和发布记录；它们只作为资料核查证据。
