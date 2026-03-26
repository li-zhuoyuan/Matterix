# 文件：scripts/verify_genie_walking_config.py

import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Verify Genie G2 Walking Config")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(headless=args_cli.headless)
simulation_app = app_launcher.app

from matterix_assets.robots.genie_G2 import GENIE_G2_INST_WALKING_CFG

cfg = GENIE_G2_INST_WALKING_CFG()

print("=" * 60)
print("GENIE_G2_INST_WALKING_CFG 传感器检查")
print("=" * 60)

print(f"\n配置的传感器：")
for name, sensor_cfg in cfg.sensors.items():
    print(f"  - {name}")
    for frame in sensor_cfg.target_frames:
        print(f"    └── {frame.name} @ {frame.prim_path}")

# 检查必需传感器
required_sensors = ["ee_frame", "grasping_frame"]
for sensor in required_sensors:
    if sensor in cfg.sensors:
        print(f"\n✓ {sensor}: 已配置")
    else:
        print(f"\n✗ {sensor}: 缺失！需要添加")

print("\n" + "=" * 60)

simulation_app.close()