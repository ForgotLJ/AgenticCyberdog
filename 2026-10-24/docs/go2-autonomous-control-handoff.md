# Go2 自主运动实验：启动提示词与技术交接

更新：2026-10-24。对象：本次连接的 `unitree@192.168.123.18`，不是小米 CyberDog，也不是仅凭 10 月 20 日记录描述的另一台狗。

用途：让狗上 Codex 直接继承已有工作，减少重复询问和重复开发，开展有实际运动效果的自主实验。编写本文没有执行新的运动。

## 1. 直接发给 Codex 的启动提示词

下面整段可以复制。**发送者应确保其中“实验人员在场、持遥控器、场地与线缆已准备好”符合当次现场事实。** 它是本轮授权声明，不把上次现场条件自动延续到下次。

```text
你现在是这台 Unitree Go2 的现场实验工程师。请阅读
/home/unitree/agentic_go2/research_handoff/go2-autonomous-control-handoff.md，
并复用同目录下的脚本、官方接口资料和原始实验记录。

本轮任务：建立可重复的机身运动控制，先解决历史“正向指令却向后移动”
与里程计不一致的问题，再完成一次有外部依据的前进约 0.5 m、停止、
小角度转向；成功后重复验证，并保存可复用的执行接口和实验结论。
如果我另行给出具体任务，以我的最新任务为准。

现场授权：我和实验人员在场，已准备空旷平整区域和网线余量；有人持有
已配对的遥控器，了解 L2+B 阻尼停止，并持续观察狗，能在异常时及时介入。
请把这视为本轮已给出的现场准备和运动授权，不要每次动作重新询问。
人员接管是补充停止手段，不是瞬时停止、永不失效或不存在碰撞的保证。

你可以直接读状态、取图像、查本机 SDK、写和修改实验脚本、运行程序，
并执行本轮范围内的起立、停止、平地短距离平移和小角度转向。
授权范围采用本文第 2 节。可以自主选择 SDK 高层接口、控制参数、
感知方法和排障实验，不需要逐条动作取得许可。

行为要求：
1. 开始时做一次简短的状态刷新。复用已验证事实；只有出现新故障、
   更换硬件或版本变化，才重查相关部分。不要重装已工作的依赖。
2. 实际运动前用一句话说清方向、速度上限、持续时间/位移目标和停止条件，
   然后执行。告知不等于等待我回复；不要以“是否继续”结束每个步骤。
3. 每个运动实验必须能回答一个具体问题。方向和停止行为核对后，应采用
   看得出效果的运动段，例如约半米；不要反复用 0.4 秒动作代替任务进展。
4. 未知参数不是停止全部工作的理由。能通过查询、图像、日志或有界实验
   获得的信息，优先自行获取。只在缺少关键现场事实、超出授权范围，
   或异常无法在现有范围内解决时提出一个具体问题。
5. 遇到失败，停止当前动作，解释证据并自主选择下一项有区分力的排查。
   不要重复同一失败动作，也不要把返回码 0 写成实际完成任务。
6. 已知本机有方向异常，不能直接复跑旧脚本来“完成半米”。先针对
   控制来源、避障改写、模式切换和观察坐标设计最少必要的诊断；
   可以在本轮范围内做有新依据的验证动作，不要停留在泛泛分析。
7. 停止机制由狗上的本地进程负责，不能依赖我回复、LLM完成思考或 SSH
   一直连接。保留独立动作期限和遥控接管；现场人员介入后立即让出控制。
8. 每轮给出：你做了什么、机器人实际怎样运动、证据在哪里、下一步是什么。
   任务完成后交付可运行入口、参数、已知限制，而不只是长篇建议。

请直接开始，不要再次询问“是否允许控制机器狗”。
```

这段提示词改变的是授权表达和工作节奏，不会修改 Codex 的系统权限或替代实际停止逻辑。可以调整任务句；不要通过虚构“已标定”“已验证正向控制”来促使 agent 行动。

## 2. 本轮实验范围与自主决策

下列数值是**本提示词建议采用的实验范围**，不是厂商极限，也不是全部实测通过的性能。发送上面的提示词即采用此范围；若现场另有具体限制，以现场限制为准。

| 项目 | 本轮范围 |
|---|---|
| 运动类型 | 平整地面上的起立、普通停止、短距离机身平移、小角度转向 |
| 平移指令 | 平面速度合量不超过 0.30 m/s；方向可自主选择，但先核对实际响应 |
| 转向指令 | 角速度不超过 0.30 rad/s；单段目标不超过约 30° |
| 单段动作 | 本地硬截止时间不超过 4 s；达到目标或出现异常可提前停止 |
| 位移目标 | 方向核对后以约 0.5 m 为首个目标；实际占用区还须包含启动、停止距离与可能反向运动 |
| 连续工作 | 可以自主运行多轮观察—动作—评估；每段结束检查停止和新状态，无需逐轮人工确认 |
| 控制来源 | 同一时间一个非零速度发送者；清理自己的旧发送进程，不能乱停厂商服务 |
| 避障与遥控 | 保留避障和物理遥控响应；可以核对/设置当前高层 API 命令来源并在结束时恢复 |
| 本轮之外 | 直接关节力矩/电机控制、跳跃翻滚、楼梯与高处、主动碰撞、关闭避障、屏蔽遥控、永久更改厂商服务 |

不必每次问的问题：是否能读状态、拍照、查询接口、修改自己的脚本、执行范围内的下一段动作、记录结果。

需要停止当前运动的问题：人或动物进入运动区、网线拉紧、现场发出停止指令、明显失衡、状态失联、实际运动方向与计划不符。先停止，再利用已有数据排查；若下一次实验仍在已准备区域和授权范围内，不必重新申请整轮许可。

遇到未知相机内参可继续定性观察；遇到无法确认前后区域是否可用，不能只靠猜测增加行程。两者不是同一种阻塞。

## 3. 本机已知环境与入口

以下为 2026-10-24 观察记录；开机、重连或新任务时刷新动态状态即可，不必重复安装和全盘探索。

| 项目 | 本机记录 |
|---|---|
| SSH | Windows 别名 `go2`；`unitree@192.168.123.18:22`；已配置公钥登录 |
| 工程目录 | `/home/unitree/agentic_go2` |
| 本资料包 | `/home/unitree/agentic_go2/research_handoff` |
| 板载系统 | ARM64、Ubuntu 20.04.5、L4T R35.3.1、glibc 2.31、Python 3.8.10、约 16 GB RAM |
| SDK 源码 | `/home/unitree/unitree_sdk2_python` |
| 本机 SDK 提交 | `432dd0655d0c88c301d53762c932ce88ebc35563`，本文整理时重新核对过 |
| Python 依赖 | CycloneDDS、numpy、cv2 已能导入；本机此前无需修正 CYCLONEDDS_HOME |
| DDS | 在狗上运行 SDK：domain `0`、网卡 `eth0` |
| 网络 | 电脑以太网 `192.168.123.99/24`；板载机 `.18`；`.161` 是另一个设备地址，不能当同一个 SSH 主机 |
| Codex | `/home/unitree/.local/bin/codex`，0.164.0，ChatGPT 已登录；桌面端 SSH 已确认 connected |
| 外网 | 电脑代理经 SSH 反向转发到狗的 `127.0.0.1:17890`；依赖电脑、VPN和隧道运行 |
| 环境加载 | `. /home/unitree/agentic_go2/codex-env.sh`；`.bashrc`/`.profile` 已配置自动加载 |

不要照搬 10 月 20 日的 `/home/unitree/cyclonedds/install` 修复：那是另一份环境记录。本机曾配置 `/home/unitree/cyclonedds_ws/install`，且直接导入成功，以当前可用环境为准。

远程启动故障已经解决：`.bashrc` 原来无条件 `read choose` 询问 ROS1/ROS2，导致 Codex 交互登录 shell 超时。现在只有 stdin/stdout 都是终端时才显示菜单。不要恢复为无条件等待输入。

系统时间曾为 1970，已校正；重启后如 TLS 失败先看 `date -u`，不关闭证书校验。最近真实模型测试返回 `GO2_CODEX_OK`；这不代表所有 MCP 连接器都正常。

## 4. 已经做过的实机实验：不要从头再来

| 项目 | 结果与证据等级 |
|---|---|
| DDS 状态 | `rt/lowstate` 约 500 Hz；`rt/sportmodestate` 约 300 Hz；`rt/lf/sportmodestate` 约 20 Hz，短时实测回调频率 |
| 高层服务 | `CheckMode()` 曾返回 `form=0, name=mcf`；避障 `SwitchGet()` 返回 true；Sport API `1.0.0.1` |
| 图像 | `VideoClient.GetImageSample()` 两次成功，能解码成 1920×1080 图像；采集时间与缓存行为未验证 |
| 遥控停止 | 本机已测试 L2+B；现场人员报告下沉/趴下并保持不动；日志出现按键 544 / `0x220`、状态 100→1001 |
| 起立 | `StandUp()` 返回 0，状态 1001→1002；机载 body_height 约 0.07→0.33 m |
| 运动 A | `+0.15 m/s`、0.4 s、8 次发送；现场报告“蛄蛹了一下”；机载平面净位移约 0.016 m；不足以证明低速死区 |
| 运动 B | `+0.30 m/s`、最多 4 s、目标里程计投影 0.55 m；80 次发送均返回 0；最终到时停止，目标未达 |
| B 的实际方向 | 现场明确报告“先向前一小步，后朝后部运动约半米”；机载投影却约 +0.080 m。这是方向失败与测量不一致，不是前进成功 |
| B 的停止收尾 | 独立停止进程到期触发，终止发送者；零速度、Sport StopMove、恢复遥控来源均返回 0；不把回执当外部静止证明 |

**当前没有已验证可重复的“前进半米”控制器。** 原因尚未定位，不应直接把速度取负号，也不能认定 0.30 m/s 是必然有效的最低速度。

10 月 20 日另一份记录中，0.12/0.20 m/s 效果差、0.30 m/s 曾达到约 1.011 m；可作为排查线索，不能覆盖本机最新失败证据。官方避障文档也没有建立“0.30 m/s 最小速度”的结论。

遥控停止已经实际测试过，不需要把重复测试 L2+B 当成每个任务的前置仪式。重新配对、更换遥控器、更新固件或出现停止故障时再针对变化核验。

## 5. 接口速查：优先直接使用本机 SDK

### 5.1 初始化与状态订阅

```python
from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_, SportModeState_
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.go2.obstacles_avoid.obstacles_avoid_client import ObstaclesAvoidClient
from unitree_sdk2py.go2.video.video_client import VideoClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

ChannelFactoryInitialize(0, "eth0")  # 在狗上执行；每个进程初始化一次
# client = SportClient(); client.SetTimeout(0.3); client.Init()
# sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
# sub.Init(callback, 10)
```

订阅回调快速缓存状态与 `time.monotonic()` 接收时间，不在回调里做模型推理。`client.Init()` 不代表服务已经在线；`SetTimeout()` 是 RPC 超时，不是运动期限。

| 数据 | 建议用途 | 已知限制 |
|---|---|---|
| `position[3]`、`velocity[3]`、`yaw_speed` | 记录运动估计与变化 | 本机曾与实际方向/位移矛盾；坐标和漂移未验证 |
| `imu_state.rpy`、`body_height` | 姿态与支撑状态观察 | 高度字段不是整机外形高度；四元数顺序另查，不凭数组猜测 |
| `error_code` | 当前 MCF 状态机 | 当前固件借用此字段；100 并非自动意味着故障 |
| `wireless_remote`（LowState） | 检测现场输入与接管意图 | 现成脚本有解析；看见按键不等于已证明每种模式下的物理响应 |
| `bms_state`、`power_v`、`motor_state` | 电量与关节状态 | 电量58%是较早快照，不是当前值；20个电机状态槽位不等于20个实际关节 |
| `range_obstacle`、`foot_position_body` | 只有验证有效后才能用于几何推断 | 本次读数全零，不能当作无障碍或足端位于身体原点 |

本固件已核对的状态：`100` 灵动、`1001` 阻尼、`1002` 站立锁定、`1013` 平衡站立。不要用旧 `mode` 字段单独解释新状态机。

### 5.2 运动、停止与控制来源

| 接口 | 语义 / 返回 | 本机使用情况 |
|---|---|---|
| `SportClient.StandUp()` | 起立，返回服务 code | 已成功；从阻尼起立后到1002 |
| `SportClient.StopMove()` | 普通停止请求，等待服务回复 | 已使用；还观察到1002→100，不能当完全无模式影响的操作 |
| `SportClient.Move(vx, vy, vyaw)` | 机身速度意图；m/s、rad/s；无回复发送 | 已查客户端；本机可靠运动效果未独立建立 |
| `SportClient.BalanceStand()` / `StandDown()` / `Damp()` | 改变支撑/状态 | 方法存在；不是与StopMove可随意互换的操作 |
| `ObstaclesAvoidClient.SwitchGet()` | `(code, enabled)` | 已读到 true |
| `ObstaclesAvoidClient.SwitchSet(on)` | 改变避障开关 | 本轮保留开启；不要为让狗动而盲目关闭 |
| `UseRemoteCommandFromApi(True)` | 选择 API 遥控速度来源 | 两次实验使用；结束调用False恢复来源 |
| `ObstaclesAvoidClient.Move(vx, vy, vyaw)` | 速度意图；载荷x/y/yaw、mode=0；无回复 | 本机两次实验使用，方向失败仍待定位 |
| `MoveToIncrementPosition(...)` | mode=1，官方描述增量位置 | 源码存在；单位/坐标/完成与停止行为需针对本机核对 |
| `MoveToAbsolutePosition(...)` | mode=2，官方描述世界系目标 | 源码存在；本机定位未可信，不能当现成精确定位器 |
| `MotionSwitcherClient.CheckMode()` | 当前运动控制模式查询 | 已查到mcf；无需为了查询就切换模式 |

`Move()` 的 0 返回码仅证明客户端发送成功。它不返回实际位移；`Move(0.3,0,0)` 不是前进 0.3 m。`ObstaclesAvoidClient` **没有** `StopMove()`。

官方避障文档的范围为 x ±1.5 m/s、y ±1 m/s、yaw ±1.57 rad/s；这里仅用于理解接口，不作为本轮实验限额。API来源设为True后才能用该避障Move路径。不要在活跃运动时混用两套速度发送者。

### 5.3 图像与雷达

`VideoClient.GetImageSample()` → `(code, data)`；data为压缩图像字节，`bytes(data)` 保存、OpenCV解码。它不直接给RGB张量、内参或可信采集时间。

```python
# 已初始化DDS；此片段只取图像，不运动。
from pathlib import Path
video = VideoClient()
video.SetTimeout(3.0)
video.Init()
code, data = video.GetImageSample()
if code != 0 or not data:
    raise RuntimeError(("image_request_failed", code))
Path("front.jpg").write_bytes(bytes(data))
```

官方描述的后续可探索数据：

| DDS话题 | 官方说明 | 本机验证状态 |
|---|---|---|
| `rt/utlidar/cloud` | 原始PointCloud2，frame `utlidar_lidar` | 本次尚未完成订阅验证 |
| `rt/utlidar/cloud_deskewed` | 去畸变PointCloud2，frame `odom` | 尚未完成；它依赖里程计，不能天然作为独立位置真值 |
| `rt/utlidar/range_info` | 前/左/右障碍距离，详见缓存官方文档 | 尚未完成；核对时间、frame、缺失值再使用 |
| `rt/api/sport/request`、`rt/api/obstacles_avoid/request` | SDK RPC 请求通道，类型见本机 `unitree_api.msg.dds_.Request_` | 可做被动命令来源诊断；尚未实现，不要把监听示例变成重放器 |

现有状态/相机已通过 SDK 工作。先用它们，不必为了得到一张图或一次速度控制先修好整个 ROS2 系统。

## 6. 身体和世界信息：有参考值，不冒充本机标定

| 参数 | 官方产品/模型参考 |
|---|---|
| 站立整机长×宽×高 | 0.70×0.31×0.40 m；约15 kg含电池 |
| 趴卧整机长×宽×高 | 0.76×0.31×0.20 m |
| 髋关节相对base原点 | FL `[+0.1934,+0.0465,0]`；FR `[+0.1934,-0.0465,0]`；RL `[-0.1934,+0.0465,0]`；RR `[-0.1934,-0.0465,0]` m |
| 大腿、小腿连接长度 | 各0.213 m；髋到大腿横向偏移左右为±0.0955 m |
| front_camera相对base | xyz `[0.32715,-0.00003,0.04297]` m；模型rpy `[0,0,0]` |
| IMU相对base | xyz `[-0.02557,0,0.04232]` m |
| radar相对base | xyz `[0.28945,0,-0.046825]` m；模型rpy `[0,2.8782,0]` rad |

这些数值来自官方产品页和固定版本展开URDF，尚未匹配本机加装件或完成实测。髋位置不是脚接地点；相机link不是已标定光学frame；整机宽度不是腿摆动包络。base碰撞盒宽仅0.0935 m，绝不能把它当整只狗宽度。

方向描述使用“相机/雷达端”和“尾部/电池端”，而不是“朝我这里”。计划采用body x前、y左、z上、正yaw左转；目前实际响应未核对成功，不能只凭这个约定判断动作正确。

相机内参K、畸变、光学外参、当前位置原点、里程计重置规则、真实足端与摆腿包络都未知。先构建足以支撑任务的局部认知：头尾朝向、可通行区域、附近障碍、线缆方向、最近动作的实际响应；不必等完整SLAM才动，也不要给无依据的厘米级距离。

建议每次观察记录：图像路径/接收时刻、姿态/状态新鲜度、控制来源、可用区域、障碍证据、最近动作的命令与观测差异。未知项写unknown，而不是填0。机载推断与现场人员观察分别保存。

## 7. 现成脚本和证据在哪里

相对路径均相对本资料包 `/home/unitree/agentic_go2/research_handoff`：

| 文件/目录 | 作用 |
|---|---|
| `scripts/observe_go2_readonly.py` | 已运行的5秒状态订阅、模式/服务查询、两张前视图采集；可直接复用 |
| `scripts/go2_bounded_probe.py` | 有界运动实验骨架；发送与停止分别在狗上独立进程中运行；默认dry-run |
| `scripts/test_go2_bounded_probe.py` | 现有6项离线检查；不导入实际运动接口，不等于实机正确性证明 |
| `evidence/go2-motion-20261024-jnzrahy8/` | 运动A：`motion.json`、`commands.jsonl`、`stop.json`、`metrics.json` |
| `evidence/go2-motion-20261024-c0x0tdhc/` | 运动B：`motion.json`、`commands.jsonl`、`stop.json` |
| `evidence/go2-stopcheck-20261024-asvqe6lv/stopcheck.json` | 已完成的遥控软停止观察，供继承验证事实 |
| `evidence/go2-stand-20261024-o28tk0t3/stand.json` | 起立记录 |
| `evidence/go2-observe-20261024-bkuyc7sf/` | 初始观察JSON和两张前视图；不是当前场景 |
| `reference/` | 缓存的官方运动V2、避障、雷达、里程计和遥控文档 |
| `reference/earlier-pack/` | 10月23日接口与几何参考、robot_profile.json；其“未实测”字段是早期快照 |

Windows本地工程：`D:\Project\AgenticCyberDog`；此文档为 `docs/go2-autonomous-control-handoff.md`。原始远端 `/tmp/go2-*` 已归档到资料包，不必依赖临时目录长期保留。

旧脚本的复用边界：

- 可复用：DDS订阅、单调时钟、独立发送/停止进程、JSON日志、接管/恢复框架。
- 不能直接信任：用初始IMU yaw投影里程计来证明前进距离；正vx等于实际前进；避障Move按原意执行。
- 旧脚本使用 `UseRemoteCommandFromApi(True)` 后调用 `Sport.StopMove()`，再等待约0.8秒后发速度。这套模式/来源组合是待检查变量，不能预先写成正确答案。
- 它只实现正vx段，没有实现通用转向和侧移；需要扩展时修改这套骨架，不要声称已有完整网关。
- `--soft-stop-evidence` 要求JSON顶层含 `soft_stop_mode_1001_observed` 与 `remote_key_combo_l2_b_observed` 两个字段。原始stopcheck日志不保证符合这个schema；如生成适配文件，应从原始证据和已记录现场观察派生，并记录来源，而不是虚构新测试。
- 旧阈值包括状态接收年龄0.2秒、站立高度0.2–0.45 m等。这是脚本参数而非厂商规范；依据实际采样调整并记录原因，不能为让失败消失而一概删除检查。
- 独立停止进程降低上层阻塞的影响，但没有覆盖掉电、全部进程故障或全部控制链路故障；未验证的故障场景仍标未验证。

只读刷新入口（不会运动）：

```bash
cd /home/unitree/agentic_go2/research_handoff
timeout -s INT -k 3s 20s python3 scripts/observe_go2_readonly.py
python3 scripts/go2_bounded_probe.py --speed 0.3 --duration 3
```

第二条仅展示dry-run参数，不能用其成功输出宣布运控可用。运动入口需要先针对已知方向失败调整/验证，不在本交接中提供盲目复跑失败动作的“一键完成”命令。

## 8. 推荐推进方式与产物

先读这份文档和运动B的摘要/命令/停止日志，快速刷新现场状态。用最少的实验区分：是否有竞争发送者、API来源是否正确、StopMove引起的模式切换是否影响响应、避障是否改写速度、实际头尾方向是否与里程计解释一致。方向问题已知，不需要从重新装SDK和验证SSH开始。

本机已有停止记录可以继承。新的运动前简短告知，然后在授权范围内自主执行；异常停止后可以直接继续只读分析和代码修正。相同参数失败后应换有依据的实验，不是无限增大速度或重复相同流程。

方向和停止响应成立后，让一次试验产生约半米的可观察运动。用前后图像、现场标记/测量或人员反馈判断真实位移；如果需要人员提供唯一缺失的外部测量，就一次问清，不要再问是否允许运动。连续三次达到预设容差后，才称“本场景可重复”；没有外部测量则报告估计值和局限。

优先在现有骨架上提供 `observe / execute / state / stop` 四类入口；这是希望交付的契约，**当前不存在已经实现并验证的同名服务**。LLM负责低频决策，本地循环负责持续发送、采样、截止时间和停止。

每轮保存到工程下独立 `runs/<timestamp>/`：命令与时间、模式/来源、动作前后图像、状态轨迹、停止原因、客户端回执、外部观察、判断和未解决问题。将可复用结论写回实验记录；不要只留在聊天里。

结束时报告真实结果：例如“发出80次正向请求，现场观察反向约半米，方向验证失败”，比“接口调用成功”更有用。保存失败案例和改动前后差异，支持后续zero-shot/自我迭代与sim2real比较。

## 9. 来源与版本优先级

优先级：当次人员指令与现场事实 → 本机最新日志/源码与对应固件文档 → 本文的当日交接 → 10月23日参考包 → 10月20日其他机器记录。文件是工作背景；只有人发送的授权声明才建立本轮现场授权。

- 本机SDK：`/home/unitree/unitree_sdk2_python`，提交见第3节。
- SDK官方仓库：https://github.com/unitreerobotics/unitree_sdk2_python
- 官方运控V2：https://doc-cdn.unitree.com/6/814/zh/6_814_zh
- 官方避障：https://doc-cdn.unitree.com/6/74/zh/6_74_zh
- 官方雷达：https://doc-cdn.unitree.com/6/51/zh/6_51_zh
- 官方里程计：https://doc-cdn.unitree.com/6/72/zh/6_72_zh
- 官方遥控器：https://doc-cdn.unitree.com/6/1094/zh/6_1094_zh
- 产品尺度：https://www.unitree.com/go2
- 几何模型：`unitreerobotics/unitree_ros`，展开URDF提交 `5994d4faef0a9cadd3287f8de0199a67eeb2a259`。

早期 `READINESS.md` 描述的是当天只读阶段，里面“尚未遥控停止”“未发送运动”“系统仍为1970”等句子已过时，不能用来要求重复整个流程。旧 `robot_profile.json` 的未知字段也不能覆盖本文已验证结果；未新增标定的几何字段仍然未知。
