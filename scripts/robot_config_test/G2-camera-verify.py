"""
诊断脚本：检查USD中摄像头prim的类型
"""

import os
import sys

# 设置环境变量
os.environ["ENABLE_CAMERAS"] = "1"

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from isaaclab.app import AppLauncher
import argparse

parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(headless=args_cli.headless, enable_cameras=True)
simulation_app = app_launcher.app

from isaaclab.sim import SimulationContext
import isaaclab.sim as sim_utils
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.actuators import ImplicitActuatorCfg
from pxr import Usd, UsdGeom

# 启动仿真
sim = SimulationContext()

robot_usd_path = os.path.join(
    project_root,
    "source/matterix_assets/data/robots/genie/G2_place_workpiece/robot.usda"
)

print(f"加载USD: {robot_usd_path}")

# 创建机器人配置
robot_cfg = ArticulationCfg(
    prim_path="/World/Robot",
    spawn=sim_utils.UsdFileCfg(
        usd_path=robot_usd_path,
        activate_contact_sensors=False,
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(-0.5, 0, 1.0),
    ),
    actuators={
        "left_arm": ImplicitActuatorCfg(
            joint_names_expr=[".*_arm_l_joint.*"],
            stiffness=1000.0,
            damping=200.0,
        ),
    },
)

# 创建地面和灯光
ground_cfg = sim_utils.GroundPlaneCfg(size=(10.0, 10.0))
ground_cfg.func("/World/defaultGroundPlane", ground_cfg)

light_cfg = sim_utils.DomeLightCfg(intensity=1000.0, color=(0.9, 0.9, 1.0))
light_cfg.func("/World/Light", light_cfg)

# 实例化机器人
from isaaclab.assets import Articulation
robot = Articulation(robot_cfg)
sim.reset()

# 运行几步仿真
for _ in range(5):
    sim.step(render=True)

# 检查摄像头prim
print("\n" + "="*80)
print("检查USD中的摄像头prim")
print("="*80)

camera_paths = [
    "/World/Robot/gripper_l_base_link/Left_Camera",
    "/World/Robot/gripper_r_base_link/Right_Camera",
]

stage = sim.stage

for cam_path in camera_paths:
    print(f"\n路径: {cam_path}")
    
    prim = stage.GetPrimAtPath(cam_path)
    
    if not prim.IsValid():
        print(f"  ✗ Prim不存在！")
        continue
    
    print(f"  ✓ Prim存在")
    print(f"  - Prim类型: {prim.GetTypeName()}")
    print(f"  - 是否是UsdGeom.Camera: {prim.IsA(UsdGeom.Camera)}")
    
    # 尝试转换为Camera
    try:
        cam_api = UsdGeom.Camera(prim)
        if cam_api:
            print(f"  ✓ 成功转换为UsdGeom.Camera")
            
            # 获取相机参数
            focal_length = cam_api.GetFocalLengthAttr().Get()
            horiz_aperture = cam_api.GetHorizontalApertureAttr().Get()
            vert_aperture = cam_api.GetVerticalApertureAttr().Get()
            
            print(f"  - Focal Length: {focal_length}")
            print(f"  - Horizontal Aperture: {horiz_aperture}")
            print(f"  - Vertical Aperture: {vert_aperture}")
        else:
            print(f"  ✗ 无法转换为UsdGeom.Camera")
    except Exception as e:
        print(f"  ✗ 转换失败: {e}")
    
    # 列出所有属性
    print(f"\n  Prim的所有属性:")
    for attr in prim.GetAttributes():
        print(f"    - {attr.GetName()}: {attr.Get()}")

print("\n" + "="*80)
print("诊断完成")
print("="*80)

simulation_app.close()