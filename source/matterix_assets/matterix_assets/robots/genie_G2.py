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
        # collision_props=sim_utils.CollisionPropertiesCfg(contact_offset=0.005, rest_offset=0.0),
    )
    init_state = ArticulationCfg.InitialStateCfg(
        pos=(-0.5, 0, 0),
    )
    actuators = { # 添加：驱动器配置
        "arm": ImplicitActuatorCfg(
            joint_names_expr=[".*"],  # 匹配所有关节
            stiffness=100.0,
            damping=10.0,
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
    actuators["arm"] = actuators["arm"].copy()
    actuators["arm"].stiffness = 100.0
    actuators["arm"].damping = 10.0



