# FIX BUG HERE #
import torch
import os
import sys
import ctypes

# --- [核心修复] 强制预加载 Conda 的 DLL ---
# 目的：在 Isaac Sim 或 h5py 加载任何 DLL 之前，先锁定正确的 zlib/blosc 版本

if os.name == 'nt': # 在 Windows 上执行
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if not conda_prefix:
        # 如果 CONDA_PREFIX 没设置，尝试从当前 python.exe 路径推断
        import pathlib
        exe_path = pathlib.Path(sys.executable)
        if 'envs' in exe_path.parts:
            idx = exe_path.parts.index('envs')
            conda_prefix = str(pathlib.Path(*exe_path.parts[:idx+2]))
    
    if conda_prefix:
        conda_bin = os.path.join(conda_prefix, "Library", "bin")
        if os.path.isdir(conda_bin):
            # 1. 使用官方 API 添加搜索目录 (优先级最高)
            try:
                os.add_dll_directory(conda_bin)
                print(f"[FIX] Added DLL directory: {conda_bin}")
            except Exception as e:
                print(f"[WARN] add_dll_directory failed: {e}")

            # 2. 【关键步骤】显式预加载关键 DLL
            # 这样即使 Isaac Sim 试图加载自己的 dll，也会发现这些已经被加载了
            dlls_to_preload = ['zlib.dll', 'blosc2.dll', 'blosc.dll', 'hdf5.dll', 'libaec.dll']
            loaded_count = 0
            for dll_name in dlls_to_preload:
                dll_path = os.path.join(conda_bin, dll_name)
                if os.path.exists(dll_path):
                    try:
                        ctypes.CDLL(dll_path)
                        print(f"[FIX] Pre-loaded: {dll_name}")
                        loaded_count += 1
                    except OSError as e:
                        # 忽略已经加载的情况或其他非致命错误
                        pass
            
            if loaded_count > 0:
                print(f"[SUCCESS] Successfully pre-loaded {loaded_count} critical DLLs from Conda.")
            else:
                print(f"[WARN] No critical DLLs found in {conda_bin}. Check your installation.")
        else:
            print(f"[ERROR] Conda bin directory not found: {conda_bin}")
    else:
        print("[ERROR] Could not determine Conda prefix. Please ensure 'conda activate Matterix' was run.")
# ----------------------------------------


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
