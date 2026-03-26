# Copyright (c) 2022-2026, The Matterix Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Script to control Genie G2 robot without Matterix framework."""

import os
print(os.path.dirname(__file__))

import argparse
from typing import Optional

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Genie G2 Robot Control")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(headless=args_cli.headless)
simulation_app = app_launcher.app

import math
import torch

from isaaclab.assets import Articulation
from isaaclab.sim import SimulationContext
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
import isaaclab.sim as sim_utils


# 启动仿真
sim = SimulationContext()

# 创建机器人配置 - 使用 Isaac Lab 原生 API
robot_cfg = ArticulationCfg(
    prim_path="/World/Robot",
    spawn=sim_utils.UsdFileCfg(
        usd_path="d:/Beginning with Embodied/Matterix/source/matterix_assets/data/robots/genie-G2/robot_fix.usda",  # 替换为实际路径
        activate_contact_sensors=False,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=0.5,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(-0.5, 0, 0.0),  # 提高初始高度，避免与地面碰撞
        rot=(1.0, 0.0, 0.0, 0.0),
        joint_pos={
            "idx21_arm_l_joint1": 0.0,
            "idx22_arm_l_joint2": 0.0,
            "idx23_arm_l_joint3": 0.0,
            "idx24_arm_l_joint4": 0.0,
            "idx25_arm_l_joint5": 0.0,
            "idx26_arm_l_joint6": 0.0,
            "idx27_arm_l_joint7": 0.0,
        },
        joint_vel={
            "idx21_arm_l_joint1": 0.0,
            "idx22_arm_l_joint2": 0.0,
            "idx23_arm_l_joint3": 0.0,
            "idx24_arm_l_joint4": 0.0,
            "idx25_arm_l_joint5": 0.0,
            "idx26_arm_l_joint6": 0.0,
            "idx27_arm_l_joint7": 0.0,
        }
    ),
    actuators={
        "left_arm": ImplicitActuatorCfg(
            joint_names_expr=[".*_arm_l_joint.*"],  # 匹配所有左臂关节
            stiffness=100.0,
            damping=10.0,
        ),
        "right_arm": ImplicitActuatorCfg(
            joint_names_expr=[".*_arm_r_joint.*"],  # 匹配所有右臂关节
            stiffness=100.0,
            damping=10.0,
        ),
        "left_gripper": ImplicitActuatorCfg(
            joint_names_expr=[".*_gripper_l_.*"],  # 匹配所有左手爪关节
            stiffness=0.0,
            damping=0.0,
        ),
        "right_gripper": ImplicitActuatorCfg(
            joint_names_expr=[".*_gripper_r_.*"],  # 匹配所有右手爪关节
            stiffness=0.0,
            damping=0.0,
        ),
        "body": ImplicitActuatorCfg(
            joint_names_expr=[".*body.*",".*head.*"],  # 匹配所有躯干和头部关节
            stiffness=1000.0,
            damping=80.0,
        ),
    },
)

# 创建地面
ground_cfg = sim_utils.GroundPlaneCfg(
    size=(10.0, 10.0),
)
ground_cfg.func("/World/defaultGroundPlane", ground_cfg)

# 创建灯光
light_cfg = sim_utils.DomeLightCfg(
    intensity=1000.0,
    color=(0.9, 0.9, 1.0),
)
light_cfg.func("/World/Light", light_cfg)

# 实例化机器人
robot = Articulation(robot_cfg)
sim.reset()

print("=" * 80)
print("Genie G2 机器人控制 - Isaac Lab 原生 API")
print("=" * 80)
print(f"关节数量：{robot.num_joints}")
print(f"关节名称：{robot.joint_names}")

# # 设置仿真步长
# sim.set_step_size(1 / 60)

# 运行仿真循环
count = 0
period = 120  # 每 120 步更新一次（2 秒@60Hz）

while simulation_app.is_running():
    # 获取机器人状态
    robot.update(1/60)
    print(robot.)
    
    # 周期性更新目标关节位置
    if count % period == 0:
        phase = (count // period) % 4

        # phase = 3
        
        if phase == 0:
            # 手臂抬起
            target_positions = torch.tensor([[
                0.0,   # idx21_arm_l_joint1
                0.5,   # idx22_arm_l_joint2
                -0.5,  # idx23_arm_l_joint3
                0.0,   # idx24_arm_l_joint4
                0.0,   # idx25_arm_l_joint5
                0.0,   # idx26_arm_l_joint6
                0.0,   # idx27_arm_l_joint7
            ]], device=robot.device)
            
            joint_ids = [
                robot.find_joints("idx21_arm_l_joint1")[0][0],
                robot.find_joints("idx22_arm_l_joint2")[0][0],
                robot.find_joints("idx23_arm_l_joint3")[0][0],
                robot.find_joints("idx24_arm_l_joint4")[0][0],
                robot.find_joints("idx25_arm_l_joint5")[0][0],
                robot.find_joints("idx26_arm_l_joint6")[0][0],
                robot.find_joints("idx27_arm_l_joint7")[0][0],
            ]
            
        elif phase == 1:
            # 手臂向前伸展
            target_positions = torch.tensor([[
                0.0,
                0.0,
                0.0,
                -0.8,
                0.0,
                0.0,
                0.0,
            ]], device=robot.device)
            
            joint_ids = [
                robot.find_joints("idx21_arm_l_joint1")[0][0],
                robot.find_joints("idx22_arm_l_joint2")[0][0],
                robot.find_joints("idx23_arm_l_joint3")[0][0],
                robot.find_joints("idx24_arm_l_joint4")[0][0],
                robot.find_joints("idx25_arm_l_joint5")[0][0],
                robot.find_joints("idx26_arm_l_joint6")[0][0],
                robot.find_joints("idx27_arm_l_joint7")[0][0],
            ]
            
        elif phase == 2:
            # 手臂向右转
            target_positions = torch.tensor([[
                0.5,
                0.3,
                -0.3,
                -0.5,
                0.0,
                0.0,
                0.0,
            ]], device=robot.device)
            
            joint_ids = [
                robot.find_joints("idx21_arm_l_joint1")[0][0],
                robot.find_joints("idx22_arm_l_joint2")[0][0],
                robot.find_joints("idx23_arm_l_joint3")[0][0],
                robot.find_joints("idx24_arm_l_joint4")[0][0],
                robot.find_joints("idx25_arm_l_joint5")[0][0],
                robot.find_joints("idx26_arm_l_joint6")[0][0],
                robot.find_joints("idx27_arm_l_joint7")[0][0],
            ]
            
        else:
            # 回到初始位置
            target_positions = torch.tensor([[
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]], device=robot.device)
            
            joint_ids = [
                robot.find_joints("idx21_arm_l_joint1")[0][0],
                robot.find_joints("idx22_arm_l_joint2")[0][0],
                robot.find_joints("idx23_arm_l_joint3")[0][0],
                robot.find_joints("idx24_arm_l_joint4")[0][0],
                robot.find_joints("idx25_arm_l_joint5")[0][0],
                robot.find_joints("idx26_arm_l_joint6")[0][0],
                robot.find_joints("idx27_arm_l_joint7")[0][0],
            ]
        
        # 设置手臂关节目标位置
        robot.set_joint_position_target(target_positions, joint_ids)
        
        # 稳定躯干 - 保持躯干关节在初始位置
        torso_joint_names = [name for name in robot.joint_names if 'body' in name.lower() or 'head' in name.lower()]
        if torso_joint_names:
            torso_joint_ids = [robot.find_joints(name)[0][0] for name in torso_joint_names]
            torso_targets = torch.zeros((1, len(torso_joint_ids)), device=robot.device)
            robot.set_joint_position_target(torso_targets, torso_joint_ids)
        
        print(f"\n[Step {count}] 执行动作相位 {phase}")
        for i, joint_id in enumerate(joint_ids):
            joint_name = robot.joint_names[joint_id]
            print(f"  {joint_name}: {target_positions[0, i]:.3f}")
        
        if torso_joint_names:
            print(f"  躯干稳定：{len(torso_joint_names)} 个关节锁定")
    
    # 步进仿真
    sim.step()
    count += 1

simulation_app.close()