# Personal Notes
## How to make it run？

**运行命令**
```bash
# 启动环境
conda activate Matterix

# 加载MATTERIX_PATH
$env:MATTERIX_PATH = "D:\Beginning with Embodied\Matterix"

# 运行程序
python scripts/run_workflow.py --task Matterix-Test-G2-Lift-Beaker-v1 --workflow pickup_beaker --num_envs 1
```

## About Matterix
### ActionConfig
* `CompositionalActionCfg` -- 组合基本动作或其他组合动作来实现复杂任务
* `PrimitiveActionCfg` -- 基本动作,是任务规划的最小执行单元，会被状态机（StateMachine）依次调用，直接转换为机器人的底层控制指令。
* `MoveToPose` -- 移动到指定位置,需要`action_space_info`来解析动作张量中位置和方向对应的维度索引。

### Information
 * `matterix_tasks`
 
 其中的test_dev_tasks中存放了各个任务，需要在__init__.py中进行Gym的id注册，例如：

 ```python
gym.register(
    id="Matterix-Test-Beaker-Lift-Franka-v1",
    entry_point="matterix.envs:MatterixBaseEnv",
    kwargs={
        "env_cfg_entry_point": test_franka_beaker_lift.FrankaBeakerLiftEnvTestCfg,
    },
    disable_env_checker=True,
)
 ```
 其中的参数FrankaBeakerLiftEnvTestCfg中定义了workflow


## Important Fix
1. ` run_workflow.py ` 强制预加载 Conda 的 DLL
2. 在Conda的`Matterix/Lib/site-packages`中添加了`sitecustomize.py` 进行 DLL正确路径的加载和torch的优先调用(`Windows系统`)

## Personal Workflow

**upstream:** https://github.com/ac-rad/Matterix.git

**origin:**  https://github.com/li-zhuoyuan/Matterix.git