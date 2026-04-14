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

from isaaclab.controllers.differential_ik_cfg import DifferentialIKControllerCfg


# 启动仿真
sim = SimulationContext()

# 创建机器人配置 - 使用 Isaac Lab 原生 API
robot_cfg = ArticulationCfg(
    prim_path="/World/Robot",
    spawn=sim_utils.UsdFileCfg(
        usd_path="d:/Beginning with Embodied/Matterix/source/matterix_assets/data/robots/genie/G1_omnipicker/robot.usda",  # 替换为实际路径
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
            joint_names_expr=["idx2[1-7]_arm_l_joint[1-7]"],  # 匹配所有左臂关节
            stiffness=1000.0,
            damping=200.0,
        ),
        "right_arm": ImplicitActuatorCfg(
            joint_names_expr=[".*_arm_r_joint.*"],  # 匹配所有右臂关节
            stiffness=1000.0,
            damping=200.0,
        ),
        "left_gripper": ImplicitActuatorCfg(
            joint_names_expr=[".*_gripper_l_.*"],  # 匹配所有左手爪关节
            stiffness=200.0,
            damping=40.0,
        ),
        "right_gripper": ImplicitActuatorCfg(
            joint_names_expr=[".*_gripper_r_.*"],  # 匹配所有右手爪关节
            stiffness=200.0,
            damping=40.0,
        ),
        # "body": ImplicitActuatorCfg(
        #     joint_names_expr=[".*body.*",".*head.*"],  # 匹配所有躯干和头部关节
        #     stiffness=1000.0,
        #     damping=80.0,
        # ),
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
print("Genie G1 机器人控制 - Isaac Lab 原生 API")
print("=" * 80)
print(f"关节数量：{robot.num_joints}")
print(f"关节名称：{robot.joint_names}")

# # 设置仿真步长
# sim.set_step_size(1 / 60)

# 运行仿真循环
count = 0
period = 120  # 每 120 步更新一次（2 秒@60Hz）

# 初始化变量
joint_ids = [
                robot.find_joints("idx21_arm_l_joint1")[0][0],
                robot.find_joints("idx22_arm_l_joint2")[0][0],
                robot.find_joints("idx23_arm_l_joint3")[0][0],
                robot.find_joints("idx24_arm_l_joint4")[0][0],
                robot.find_joints("idx25_arm_l_joint5")[0][0],
                robot.find_joints("idx26_arm_l_joint6")[0][0],
                robot.find_joints("idx27_arm_l_joint7")[0][0],
            ]
print(robot.data.joint_pos_limits[0, joint_ids])
gripper_joint_ids = [
                robot.find_joints("idx39_gripper_l_inner_joint0")[0][0],
                robot.find_joints("idx31_gripper_l_inner_joint1")[0][0],
                robot.find_joints("idx32_gripper_l_inner_joint3")[0][0],
                robot.find_joints("idx33_gripper_l_inner_joint4")[0][0],
                robot.find_joints("idx49_gripper_l_outer_joint0")[0][0],
                robot.find_joints("idx41_gripper_l_outer_joint1")[0][0],
                robot.find_joints("idx42_gripper_l_outer_joint3")[0][0],
                robot.find_joints("idx43_gripper_l_outer_joint4")[0][0],
]
print(robot.data.joint_pos_limits[0, gripper_joint_ids])
print(robot.data.joint_effort_limits[0, gripper_joint_ids])

gripper_target_pos = None
target_positions = None
torso_joint_names = []

while simulation_app.is_running():
    # 周期性更新目标关节位置
    if count % period == 0:
        phase_gripper = (count // period) % 2

        if phase_gripper == 0:
            gripper_target_pos = torch.tensor([[
                0.0,#2.0,
                0.0,#-0.7854,
                0.0,#0.1745,
                0.0,#0.0349,
                0.0,#2.0,
                0.7854,
                0.0,#0.1745,
                0.0,#0.0349,
            ]], device=robot.device)  # 张开
        
        else:
            gripper_target_pos = torch.tensor([[
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]], device=robot.device)  # 夹紧

        phase = (count // period) % 4
        
        if phase == 0:
            # 手臂抬起
            target_positions = torch.tensor([[
                -1.5,   # idx21_arm_l_joint1
                -0.5,   # idx22_arm_l_joint2
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
                -1.5,
                -1.0,
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
                -1.5,
                -0.3,
                0.0,
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
        # 设置手爪关节目标位置
        robot.set_joint_position_target(gripper_target_pos, gripper_joint_ids)
        
        # 稳定躯干 - 保持躯干关节在初始位置
        # torso_joint_names = [name for name in robot.joint_names if 'body' in name.lower() or 'head' in name.lower()]
        # if torso_joint_names:
        #     torso_joint_ids = [robot.find_joints(name)[0][0] for name in torso_joint_names]
        #     torso_targets = torch.zeros((1, len(torso_joint_ids)), device=robot.device)
        #     robot.set_joint_position_target(torso_targets, torso_joint_ids)

        # 将控制数据写入仿真
        robot.write_data_to_sim()
    
    # 步进仿真
    sim.step()
    
    # 在仿真步进后读取状态和力矩
    if count % period == 0 and target_positions is not None:
        # for i, joint_id in enumerate(joint_ids):
        #     joint_name = robot.joint_names[joint_id]
        #     print(f"  {joint_name}:exp: {target_positions[0, i]:.3f}  fdb: {robot.data.joint_pos[0, joint_id]:.3f}")
        
        # if torso_joint_names:
        #     print(f"  躯干稳定：{len(torso_joint_names)} 个关节锁定")

        print("Joint efforts (arm_l):", robot.data.applied_torque[0, joint_ids].cpu().numpy())
        print("Joint efforts (gripper_l):", robot.data.applied_torque[0, gripper_joint_ids].cpu().numpy())

    count += 1

simulation_app.close()