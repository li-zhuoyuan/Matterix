# Copyright (c) 2022-2026, The Matterix Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Run a workflow using the MATteRIX state machine system.

The state machine orchestrates sequential actions across parallel environments on the GPU.

Usage:
    ./matterix.sh -p scripts/run_workflow.py --task Matterix-Test-Beaker-Lift-Franka-v1 --workflow pickup_beaker
    ./matterix.sh -p scripts/run_workflow.py --num_envs 32
"""

"""Launch Omniverse Toolkit first."""

import argparse

from isaaclab.app import AppLauncher

# Parse arguments
parser = argparse.ArgumentParser(description="Run state machine workflows for MATteRIX environments.")
parser.add_argument(
    "--disable_fabric",
    action="store_true",
    default=False,
    help="Disable fabric and use USD I/O operations.",
)
parser.add_argument(
    "--num_envs",
    type=int,
    default=1,
    help="Number of parallel environments to simulate.",
)
parser.add_argument(
    "--task",
    type=str,
    default="Matterix-Test-Beaker-Lift-Franka-v1",
    help="Environment/task name.",
)
parser.add_argument("--workflow", type=str, default="pickup_beaker", help="Name of the workflow to run.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

# Launch omniverse app
app_launcher = AppLauncher(headless=args_cli.headless)
simulation_app = app_launcher.app

"""Rest everything else."""

import gymnasium as gym
import torch

import matterix_tasks  # noqa: F401
from matterix_sm import StateMachine

from isaaclab_tasks.utils.parse_cfg import parse_env_cfg


def main():
    # Parse configuration
    env_cfg = parse_env_cfg(
        args_cli.task,
        device=args_cli.device,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
    )

    # Validate workflow exists
    if not hasattr(env_cfg, "workflows") or not env_cfg.workflows:
        raise ValueError(f"No workflows defined for {args_cli.task}!")

    if args_cli.workflow not in env_cfg.workflows:
        available = list(env_cfg.workflows.keys())
        raise ValueError(
            f"Workflow '{args_cli.workflow}' not found. Available workflows: {available}. "
            f"Use 'python scripts/list_workflows.py --task {args_cli.task}' to see details."
        )

    # Extract workflow actions
    workflow_value = env_cfg.workflows[args_cli.workflow]
    if isinstance(workflow_value, dict):
        description = workflow_value.get("description", "No description")
        actions = workflow_value.get("actions", [])
    else:
        description = getattr(workflow_value, "description", "No description")
        actions = [workflow_value]

    print(f"\nTask: {args_cli.task}")
    print(f"Workflow: '{args_cli.workflow}'")
    print(f"Description: {description}\n")

    # Create environment and state machine
    env = gym.make(args_cli.task, cfg=env_cfg).unwrapped
    env.reset()

    # Create state machine with required parameters from environment
    sm = StateMachine(num_envs=env.num_envs, dt=env.step_dt, device=env.device)
    sm.set_action_sequence(actions)

    episode_count = 0

    # import omni.usd

    # # 获取 USD 舞台和机器人 Prim 路径（根据您的场景调整）
    # stage = omni.usd.get_context().get_stage()
    # robot_prim_path = "/World/envs/env_0/Articulations_robot"   # 请确认路径正确

    # # 获取机器人对象
    # robot = env.scene.articulations["robot"]
    # # 轮子关节索引列表
    # wheel_indices = [2, 3, 4, 5, 7, 8, 9, 10]   # 根据您的关节索引调整

    # for idx in wheel_indices:
    #     joint_name = robot.joint_names[idx]
    #     joint_prim = stage.GetPrimAtPath(f"{robot_prim_path}/joints/{joint_name}")
    #     if joint_prim.IsValid():
    #         # 设置限位为 ±1000 弧度（足够大，允许连续旋转）
    #         lower_attr = joint_prim.GetAttribute("physics:lowerLimit")
    #         upper_attr = joint_prim.GetAttribute("physics:upperLimit")
    #         if not lower_attr:
    #             lower_attr = joint_prim.CreateAttribute("physics:lowerLimit", float)
    #         if not upper_attr:
    #             upper_attr = joint_prim.CreateAttribute("physics:upperLimit", float)
    #         lower_attr.Set(-1000.0)
    #         upper_attr.Set(1000.0)

    #         # 如果存在锁定属性，确保解锁
    #         locked_attr = joint_prim.GetAttribute("physics:locked")
    #         if locked_attr:
    #             locked_attr.Set(False)

    #         print(f"Updated limits for {joint_name}: [-1000, 1000]")
    #     else:
    #         print(f"Prim for {joint_name} not found")

    # # 获取机器人对象
    # robot = env.scene.articulations["robot"]

    # # ========== 临时禁用执行器 ==========
    # # 将执行器的 stiffness 和 damping 设为 0，避免干扰
    # for actuator in robot.actuators.values():
    #     actuator.stiffness = 0.0
    #     actuator.damping = 50.0
    # # ==================================

    # # 直接设置关节速度（绕过执行器）
    # wheel_indices = [2, 3, 4, 5, 7, 8, 9, 10]
    # target_vel = torch.zeros(robot.num_joints, device=robot.device)
    # target_vel[wheel_indices] = 1.0
    # robot.set_joint_velocity_target(target_vel.unsqueeze(0))  # 注意方法名

    # # 运行几步，观察位置变化
    # for i in range(60):
    #     env.sim.step()
    #     pos = robot.data.joint_pos[0, wheel_indices].cpu().numpy()
    #     vel = robot.data.joint_vel[0, wheel_indices].cpu().numpy()
    #     print(f"Step {i}: pos {pos}, vel {vel}")

    # Main simulation loop
    while simulation_app.is_running():
        with torch.inference_mode():
            obs, _ = env.reset()
            sm.reset()
            episode_count += 1
            step_count = 0

            print(f"\n{'=' * 80}")
            print(f"EPISODE {episode_count}")
            print(f"{'=' * 80}\n")

            # Run until workflow completes or fails
            while not (sm.action_sequence_success | sm.action_sequence_failure).all():
                action = sm.step(obs).to(env.device)
                obs, _, _, _, _ = env.step(action)
                wheel_indices = [2, 3, 4, 5, 7, 8, 9, 10] # chassis id
                print("Joint positions (first env):", obs["articulations"]["robot__joint_pos"][0, wheel_indices])
                print("Joint velocities (first env):", obs["articulations"]["robot__joint_vel"][0, wheel_indices])
                # 获取所有关节的力矩
                robot = env.scene.articulations["robot"]
                joint_efforts = robot.data.applied_torque  # shape: (num_envs, num_joints)
                # 打印轮子关节的力矩
                print("Joint efforts (wheel):", joint_efforts[0, wheel_indices])
                step_count += 1

                # Print status every 50 steps
                if step_count % 50 == 0:
                    sm.print_status(step=step_count, episode=episode_count)

            # Episode finished
            sm.print_status(step=step_count, episode=episode_count)

    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
