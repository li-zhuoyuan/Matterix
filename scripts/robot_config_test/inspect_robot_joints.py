# 文件：scripts/inspect_robot_joints.py

import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Inspect Robot Joints")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(headless=args_cli.headless)
simulation_app = app_launcher.app

from isaaclab.assets import Articulation
from isaaclab.sim import SimulationContext
from isaaclab.actuators import ImplicitActuatorCfg
from matterix_assets import MATTERIX_ASSETS_DATA_DIR

# 启动仿真
sim = SimulationContext()

# 创建机器人配置（临时）
from isaaclab.assets.articulation import ArticulationCfg
import isaaclab.sim as sim_utils

robot_cfg = ArticulationCfg(
    prim_path= "/World/envs/env_0/Robot", #"/World/Robot",  # 添加：机器人在场景中的路径
    spawn=sim_utils.UsdFileCfg(
        usd_path=f"{MATTERIX_ASSETS_DATA_DIR}/robots/genie/G1_omnipicker/robot.usda", #G2/robot_fix.usda",  # 使用固定的机器人模型
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0, 0, 2.0),
    ),
    actuators={  # 添加：驱动器配置
        "all_joints": ImplicitActuatorCfg(
            joint_names_expr=[".*"],  # 匹配所有关节
            stiffness=100.0,
            damping=10.0,
        ),
    },
    soft_joint_pos_limit_factor=10.0,  # 使用完整的关节限制范围
)

# 实例化机器人
robot = Articulation(robot_cfg)
sim.reset()

# 打印关节信息
print("=" * 80)
print("机器人关节信息")
print("=" * 80)

print(f"\n关节数量：{robot.num_joints}")
print(f"\n所有关节名称：")
for i, name in enumerate(robot.joint_names):
    print(f"  [{i}] {name}")

print(f"\n关节默认位置：{robot.data.default_joint_pos}")

# 获取连杆信息
print(f"\n连杆数量：{robot.num_bodies}")
print(f"连杆名称：{robot.body_names}")

print(robot.data.joint_pos_limits)
print(robot.data.joint_pos_limits.shape)
print(robot.data.joint_vel_limits)
print(robot.data.joint_vel_limits.shape)

# 保持窗口打开以便在 Isaac Sim 中查看
while simulation_app.is_running():
    sim.render()

simulation_app.close()