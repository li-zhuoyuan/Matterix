# Copyright (c) 2022-2026, The Matterix Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""ChassisMove action - move mobile base by controlling wheel joints for GENIE-G2."""

from __future__ import annotations

import torch
from typing import ClassVar

from .._compat import configclass
from ..primitive_action import PrimitiveAction, PrimitiveActionCfg
from ..robot_action_spaces import ActionSpaceInfo
from ..scene_data import SceneData


@configclass
class ChassisMoveCfg(PrimitiveActionCfg):
    """Configuration for ChassisMove action.
    
    Inherits base fields (agent_assets, timeout) from PrimitiveActionCfg.
    
    Attributes:
        velocity_command: Velocity command (vx, vy, wz) in m/s and rad/s.
                         - vx: forward/backward velocity (m/s)
                         - vy: lateral velocity (m/s)
                         - wz: angular velocity around z-axis (rad/s)
        action_space_info: Action space metadata for joint control.
    """
    
    velocity_command: tuple[float, float, float] | None = None
    action_space_info: ActionSpaceInfo | None = None
    
    def __post_init__(self):
        """Post-initialization checks."""
        super().__post_init__()
        if self.velocity_command is None:
            self.velocity_command = (0.0, 0.0, 0.0)


class ChassisMove(PrimitiveAction):
    """Move the chassis by sending commands to wheel joints.
    
    This action converts velocity commands to joint position targets.
    Suitable for differential drive, omnidirectional, and other mobile bases.
    
    For GENIE-G2 with 4 wheels (each with 2 joints):
    - Joint 1: Steering/rotation joint
    - Joint 2: Drive/rotation joint
    
    The action uses a simple kinematic model to convert velocity commands
    to individual wheel speeds.
    """
    
    cfg_type: ClassVar[type] = ChassisMoveCfg
    
    def __init__(
        self,
        agent_assets: str | list[str],
        velocity_command: tuple[float, float, float] | None = None,
        timeout: float = 5.0,
        action_space_info: ActionSpaceInfo | None = None,
    ):
        """
        Args:
            agent_assets: Name(s) of articulated asset(s) acting as agents.
            velocity_command: Velocity command (vx, vy, wz).
            timeout: Max time (in seconds) before timeout.
            action_space_info: Action space metadata for joint control.
        """
        super().__init__(agent_assets, timeout, action_space_info)
        
        self._velocity_command_init = velocity_command or (0.0, 0.0, 0.0)
        self._velocity_command = None  # Will be set in set_execution_params
        
        # Time tracking
        self._elapsed_time = 0.0
    
    def set_execution_params(self, num_envs: int, device: str | torch.device, dt: float) -> None:
        """Set execution parameters and initialize tensors."""
        super().set_execution_params(num_envs, device, dt)
        
        # Move velocity command to correct device
        self._velocity_command = torch.tensor(
            self._velocity_command_init, 
            dtype=torch.float32, 
            device=self.device
        ).unsqueeze(0).expand(num_envs, -1)
    
    def _compute_action_impl(self, scene_data: SceneData, env_ids: torch.Tensor):
        """Compute chassis action for controlled asset.
        
        Converts velocity commands to joint position targets.
        Uses a simple kinematic model (can be customized for specific chassis).
        
        Args:
            scene_data: Complete scene state container.
            env_ids: Indices of active environments.
        
        Returns:
            (action_tensor, action_dim_mask):
                - action_tensor: Shape (num_envs, num_joints) - joint position targets
                - action_dim_mask: Shape (num_joints,) - which joints this action controls
        """
        # Get number of joints
        if self.action_space_info is None or self.action_space_info.joint_indices is None:
            raise ValueError(
                "ChassisMove requires action_space_info with joint_indices. "
                "Please provide action_space_info when creating the action."
            )
        
        num_joints = len(self.action_space_info.joint_indices)
        
        # Create action tensor (num_envs, num_joints)
        action_tensor = torch.zeros(self.num_envs, num_joints, device=self.device)
        
        # Get velocity commands
        vx = self._velocity_command[:, 0]  # forward velocity (m/s)
        vy = self._velocity_command[:, 1]  # lateral velocity (m/s)
        wz = self._velocity_command[:, 2]  # angular velocity (rad/s)
        
        # ========== GENIE-G2 四轮差速驱动模型 ==========
        # Assumptions:
        # - Each wheel has 2 joints: joint1 (steering), joint2 (drive)
        # - 4 wheels: front-left, front-right, rear-left, rear-right
        # - Joint order: [FL1, RL1, FR1, RR1, FL2, RL2, FR2, RR2]
        
        wheel_base = 0.5  # Distance between left and right wheels (meters)
        wheel_radius = 0.1  # Wheel radius (meters)
        
        # Calculate target velocity for each wheel
        # Front-left wheel
        v_fl = vx - wz * wheel_base / 2
        # Front-right wheel
        v_fr = vx + wz * wheel_base / 2
        # Rear-left wheel
        v_rl = vx - wz * wheel_base / 2
        # Rear-right wheel
        v_rr = vx + wz * wheel_base / 2
        
        # Convert linear velocity to angular velocity (wheel drive joints)
        omega_fl = v_fl / wheel_radius
        omega_fr = v_fr / wheel_radius
        omega_rl = v_rl / wheel_radius
        omega_rr = v_rr / wheel_radius
        
        # Fill action tensor
        # Assuming joint order: [FL1, RL1, FR1, RR1, FL2, RL2, FR2, RR2]
        # joint1 is steering, joint2 is drive
        action_tensor[:, 4] = omega_fl   # Front-left drive joint
        action_tensor[:, 5] = omega_fr   # Front-right drive joint
        action_tensor[:, 6] = omega_rl   # Rear-left drive joint
        action_tensor[:, 7] = 0 #omega_rr   # Rear-right drive joint
        
        # Steering joints set to 0 (can be extended for steerable wheels)
        action_tensor[:, 0] = 0.0   # Front-left steering joint
        action_tensor[:, 1] = 0.0   # Front-right steering joint
        action_tensor[:, 2] = 0.0   # Rear-left steering joint
        action_tensor[:, 3] = 0.0   # Rear-right steering joint
        
        # Create action mask (all joints controlled)
        action_dim_mask = torch.ones(num_joints, dtype=torch.bool, device=self.device)
        
        # Update elapsed time
        self._elapsed_time += self.dt
        
        # Check timeout
        if self._elapsed_time >= self.timeout:
            self._env_success_mask[:] = True
        
        return action_tensor, action_dim_mask
    
    def _reset_impl(self, env_ids: torch.Tensor | None = None) -> None:
        """Reset action state when environments are reset."""
        if env_ids is None:
            env_ids = slice(None)
        
        self._elapsed_time = 0.0
        self._env_success_mask[env_ids] = False
    
    @classmethod
    def from_cfg(cls, cfg: ChassisMoveCfg):
        """Create ChassisMove action from configuration."""
        return cls(
            agent_assets=cfg.agent_assets,
            velocity_command=cfg.velocity_command,
            timeout=cfg.timeout,
            action_space_info=cfg.action_space_info,
        )