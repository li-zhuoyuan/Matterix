# Copyright (c) 2022-2026, The Matterix Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for the Agibot-G2 robot

"""
from matterix_assets import MATTERIX_ASSETS_DATA_DIR

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.controllers.differential_ik_cfg import DifferentialIKControllerCfg
from isaaclab.envs import mdp
from isaaclab.envs.mdp.actions.actions_cfg import DifferentialInverseKinematicsActionCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.sensors import FrameTransformerCfg, OffsetCfg
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAACLAB_NUCLEUS_DIR
from isaaclab_tasks.manager_based.manipulation.stack.mdp import franka_stack_events

from ..matterix_articulation import MatterixArticulationCfg

from isaaclab.markers.config import FRAME_MARKER_CFG  # isort: skip

##
# Configuration
##

marker_cfg = FRAME_MARKER_CFG.copy()
marker_cfg.markers["frame"].scale = (0.1, 0.1, 0.1)
marker_cfg.prim_path = "/Visuals/FrameTransformer"


@configclass
class GENIE_G2_INST_CFG(MatterixArticulationCfg):
    spawn = sim_utils.UsdFileCfg(
        usd_path=f"{MATTERIX_ASSETS_DATA_DIR}/robots/genie-G2/robot.usd",
        activate_contact_sensors=False,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=0,
        ),
    )

    init_state = ArticulationCfg.InitialStateCfg(
        pos=(-0.5, 0, 0),
        joint_pos={
            "idx21_arm_l_joint1": 0.0,
            "idx22_arm_l_joint2": -0.569,
            "idx23_arm_l_joint3": 0.0,
            "idx24_arm_l_joint4": -2.000,
            "idx25_arm_l_joint5": 0.0,
            "idx26_arm_l_joint6": 0.0,
            "idx27_arm_l_joint7": 0.741,
        },
    )
    actuators = {
        "left_arm": ImplicitActuatorCfg(
            joint_names_expr=["idx2[1-7]_arm_l_joint[1-7]"],  # 匹配左臂关节
            stiffness=100.0,
            damping=10.0,
        ),
        "right_arm": ImplicitActuatorCfg(
            joint_names_expr=["idx6[1-7]_arm_r_joint[1-7]"],
            stiffness=100.0,
            damping=10.0,
        ),
        "left_gripper": ImplicitActuatorCfg(
            joint_names_expr=["idx3[1-9]_gripper_l_inner_joint[0-9]"],  # 根据实际需要
            stiffness=2000.0,
            damping=100.0,
        ),
        "right_gripper": ImplicitActuatorCfg(
            joint_names_expr=["idx7[1-9]_gripper_r_inner_joint[0-9]"],
            stiffness=2000.0,
            damping=100.0,
        ),
    }

    sensors = {
        "ee_frame": FrameTransformerCfg(
            prim_path="/base_link",
            debug_vis=False,
            visualizer_cfg=marker_cfg,
            target_frames=[
                FrameTransformerCfg.FrameCfg(
                    prim_path="/gripper_l_base_link",
                    name="end_effector",
                ),
            ],
        ),

        "grasping_frame": FrameTransformerCfg(
            prim_path="/base_link",
            debug_vis=False,
            visualizer_cfg=marker_cfg,
            target_frames=[
                FrameTransformerCfg.FrameCfg(
                    prim_path="/gripper_l_base_link",
                    name="grasping_frame",
                    offset=OffsetCfg(pos=(0.0, 0.0, 0.1034), rot=(0.0, 1.0, 0.0, 0.0)),
                ),
            ],
        ),
    }

    action_terms = {
        "arm_action": mdp.JointPositionActionCfg(joint_names=["idx2[1-7]_arm_l_joint[1-7]"], scale=0.5, use_default_offset=True),
        "gripper_action": mdp.JointPositionActionCfg(
            joint_names=["idx3[1-9]_gripper_l_inner_joint[0-9]"], scale=0.5, use_default_offset=True
        ),
    }

    semantic_tags = [("class", "robot")]

@configclass
class GENIE_G2_INST_HIGH_PD_CFG(GENIE_G2_INST_CFG):
    # Override `spawn` by copying and modifying the nested rigid_props
    spawn = GENIE_G2_INST_CFG().spawn.copy()
    spawn.rigid_props.disable_gravity = True

    # Copy and modify actuators
    actuators = GENIE_G2_INST_CFG().actuators.copy()
    actuators["left_arm"] = actuators["left_arm"].copy()
    actuators["left_arm"].stiffness = 100.0
    actuators["left_arm"].damping = 10.0

    actuators["right_arm"] = actuators["right_arm"].copy()
    actuators["right_arm"].stiffness = 100.0
    actuators["right_arm"].damping = 10.0
