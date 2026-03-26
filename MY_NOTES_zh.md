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

## About Genie-G2
```bash
================================================================================
机器人关节信息
================================================================================

关节数量：46

所有关节名称：
  [0] idx01_body_joint1
  [1] idx02_body_joint2
  [2] idx111_chassis_lwheel_front_joint1
  [3] idx121_chassis_lwheel_rear_joint1
  [4] idx131_chassis_rwheel_front_joint1
  [5] idx141_chassis_rwheel_rear_joint1
  [6] idx03_body_joint3
  [7] idx112_chassis_lwheel_front_joint2
  [8] idx122_chassis_lwheel_rear_joint2
  [9] idx132_chassis_rwheel_front_joint2
  [10] idx142_chassis_rwheel_rear_joint2
  [11] idx04_body_joint4
  [12] idx05_body_joint5
  [13] idx11_head_joint1
  [14] idx12_head_joint2
  [15] idx21_arm_l_joint1
  [16] idx61_arm_r_joint1
  [17] idx13_head_joint3
  [18] idx22_arm_l_joint2
  [19] idx62_arm_r_joint2
  [20] idx23_arm_l_joint3
  [21] idx63_arm_r_joint3
  [22] idx24_arm_l_joint4
  [23] idx64_arm_r_joint4
  [24] idx25_arm_l_joint5
  [25] idx65_arm_r_joint5
  [26] idx26_arm_l_joint6
  [27] idx66_arm_r_joint6
  [28] idx27_arm_l_joint7
  [29] idx67_arm_r_joint7
  [30] idx31_gripper_l_inner_joint1
  [31] idx41_gripper_l_outer_joint1
  [32] idx71_gripper_r_inner_joint1
  [33] idx81_gripper_r_outer_joint1
  [34] idx32_gripper_l_inner_joint3
  [35] idx42_gripper_l_outer_joint3
  [36] idx72_gripper_r_inner_joint3
  [37] idx82_gripper_r_outer_joint3
  [38] idx33_gripper_l_inner_joint4
  [39] idx43_gripper_l_outer_joint4
  [40] idx73_gripper_r_inner_joint4
  [41] idx83_gripper_r_outer_joint4
  [42] idx39_gripper_l_inner_joint0
  [43] idx49_gripper_l_outer_joint0
  [44] idx79_gripper_r_inner_joint0
  [45] idx89_gripper_r_outer_joint0

关节限位：
  最小位置：tensor([[-1.0600,  0.0000]], device='cuda:0')
  最大位置：tensor([[0.0000, 2.6500]], device='cuda:0')

关节默认位置：tensor([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]],
       device='cuda:0')

连杆数量：56
连杆名称：['base_link', 'body_link1', 'chassis_link', 'body_link2', 'chassis_lwheel_front_link1', 'chassis_lwheel_rear_link1', 'chassis_rwheel_front_link1', 'chassis_rwheel_rear_link1', 'body_link3', 'chassis_lwheel_front_link2', 'chassis_lwheel_rear_link2', 'chassis_rwheel_front_link2', 'chassis_rwheel_rear_link2', 'body_link4', 'body_link5', 'head_base_link', 'head_link1', 'arm_base_link', 'head_link2', 'arm_l_link1', 'arm_r_link1', 'head_link3', 'arm_l_link2', 'arm_r_link2', 'arm_l_link3', 'arm_r_link3', 'arm_l_link4', 'arm_r_link4', 'arm_l_link5', 'arm_r_link5', 'arm_l_link6', 'arm_r_link6', 'arm_l_link7', 'arm_r_link7', 'arm_l_end_link', 'arm_r_end_link', 'gripper_l_base_link', 'gripper_r_base_link', 'gripper_l_inner_link1', 'gripper_l_outer_link1', 'gripper_l_center_link', 'gripper_r_inner_link1', 'gripper_r_outer_link1', 'gripper_r_center_link', 'gripper_l_inner_link3', 'gripper_l_outer_link3', 'gripper_r_inner_link3', 'gripper_r_outer_link3', 'gripper_l_inner_link4', 'gripper_l_outer_link4', 'gripper_r_inner_link4', 'gripper_r_outer_link4', 'gripper_l_inner_link2', 'gripper_l_outer_link2', 'gripper_r_inner_link2', 'gripper_r_outer_link2']
```


## Important Fix
1. ` run_workflow.py ` 强制预加载 Conda 的 DLL
2. 在Conda的`Matterix/Lib/site-packages`中添加了`sitecustomize.py` 进行 DLL正确路径的加载和torch的优先调用(`Windows系统`)

## Personal Workflow

**upstream:** https://github.com/ac-rad/Matterix.git

**origin:**  https://github.com/li-zhuoyuan/Matterix.git