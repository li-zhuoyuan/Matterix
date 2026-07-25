"""
详细诊断USD摄像头配置
"""

import os
import sys

os.environ["ENABLE_CAMERAS"] = "1"

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(headless=False, enable_cameras=True)
simulation_app = app_launcher.app

from isaaclab.sim import SimulationContext
from isaaclab.assets import Articulation
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
import isaaclab.sim as sim_utils
from pxr import Usd, UsdGeom, Sdf

# 启动仿真
sim = SimulationContext()

robot_usd_path = os.path.join(
    project_root,
    "source/matterix_assets/data/robots/genie/G2_place_workpiece/robot.usda"
)

print(f"加载机器人: {robot_usd_path}\n")

# 创建地面和灯光
ground_cfg = sim_utils.GroundPlaneCfg(size=(10.0, 10.0))
ground_cfg.func("/World/defaultGroundPlane", ground_cfg)

light_cfg = sim_utils.DomeLightCfg(intensity=1000.0, color=(0.9, 0.9, 1.0))
light_cfg.func("/World/Light", light_cfg)

# 创建机器人
robot_cfg = ArticulationCfg(
    prim_path="/World/Robot",
    spawn=sim_utils.UsdFileCfg(usd_path=robot_usd_path),
    init_state=ArticulationCfg.InitialStateCfg(pos=(-0.5, 0, 1.0)),
    actuators={
        "left_arm": ImplicitActuatorCfg(
            joint_names_expr=[".*_arm_l_joint.*"],
            stiffness=1000.0,
            damping=200.0,
        ),
    },
)

robot = Articulation(robot_cfg)
sim.reset()

# 获取stage
stage = sim.stage

print("="*80)
print("检查摄像头Prim详细信息")
print("="*80)

camera_paths = [
    "/World/Robot/gripper_l_base_link/Left_Camera",
    "/World/Robot/gripper_r_base_link/Right_Camera",
]

for cam_path in camera_paths:
    print(f"\n{'='*80}")
    print(f"路径: {cam_path}")
    print(f"{'='*80}")
    
    prim = stage.GetPrimAtPath(cam_path)
    
    if not prim.IsValid():
        print("  ✗ Prim不存在！")
        continue
    
    print(f"  ✓ Prim存在")
    print(f"  - Prim名称: {prim.GetName()}")
    print(f"  - Prim类型: {prim.GetTypeName()}")
    print(f"  - 是否是UsdGeom.Camera: {prim.IsA(UsdGeom.Camera)}")
    
    # 检查Camera API
    try:
        cam_api = UsdGeom.Camera(prim)
        if cam_api:
            print(f"  ✓ 成功获取UsdGeom.Camera API")
            
            # 获取所有相机属性
            attrs = {
                'focalLength': cam_api.GetFocalLengthAttr(),
                'horizontalAperture': cam_api.GetHorizontalApertureAttr(),
                'verticalAperture': cam_api.GetVerticalApertureAttr(),
                'focusDistance': cam_api.GetFocusDistanceAttr(),
                'projection': cam_api.GetProjectionAttr(),
            }
            
            print(f"\n  相机参数:")
            for name, attr in attrs.items():
                if attr.IsValid():
                    value = attr.Get()
                    print(f"    - {name}: {value} (时间采样: {attr.GetTimeSamples()})")
                else:
                    print(f"    - {name}: 无效")
        else:
            print(f"  ✗ 无法获取Camera API")
    except Exception as e:
        print(f"  ✗ 获取Camera API失败: {e}")
    
    # 检查所有属性和元数据
    print(f"\n  所有USD属性:")
    for attr in prim.GetAttributes():
        attr_name = attr.GetName()
        attr_value = attr.Get()
        attr_type = attr.GetTypeName()
        
        # 只显示关键属性
        if any(key in attr_name.lower() for key in ['aperture', 'focal', 'visibility', 'clip']):
            print(f"    - {attr_name} ({attr_type}): {attr_value}")
    
    # 检查metadata
    print(f"\n  USD Metadata:")
    for key in ['hidden', 'kind']:
        metadata = prim.GetMetadata(key)
        if metadata is not None:
            print(f"    - {key}: {metadata}")
    
    # 检查是否被隐藏
    visibility_attr = prim.GetAttribute('visibility')
    if visibility_attr.IsValid():
        visibility = visibility_attr.Get()
        print(f"\n  ⚠ Visibility属性: {visibility}")
        if visibility == 'invisible':
            print(f"     → 这是问题所在！摄像头被设置为不可见！")

print("\n" + "="*80)
print("诊断完成")
print("="*80)

simulation_app.close()