"""
G2 Robot Left Wrist Camera Access Script
Directly access and capture images from Left_Camera in robot.usda
Compatible with Isaac Sim 5.1.0
"""


import os
import sys

# Critical: Set environment variable before any Isaac Lab imports
os.environ["ENABLE_CAMERAS"] = "1"

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
from isaaclab.app import AppLauncher

# Parse command line arguments
parser = argparse.ArgumentParser(description="G2 Robot Left Camera Access")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

# Launch application (force enable cameras)
app_launcher = AppLauncher(headless=False, enable_cameras=True)
simulation_app = app_launcher.app

import torch
import numpy as np
from PIL import Image

from isaaclab.assets import Articulation
from isaaclab.sim import SimulationContext
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.sensors.camera import CameraCfg
from isaaclab.sensors import Camera
import isaaclab.sim as sim_utils

# --------------------- Helper Functions ---------------------
def save_image(data: torch.Tensor, filename: str, output_dir: str = "./img"):
    """Save image to specified directory"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to numpy array
    img_np = data.cpu().numpy() if isinstance(data, torch.Tensor) else data
    
    filepath = os.path.join(output_dir, filename)
    
    # Handle RGB images [H, W, 3]
    if len(img_np.shape) == 3 and img_np.shape[2] == 3:
        if img_np.dtype != np.uint8:
            if img_np.max() <= 1.0:
                img_np = (img_np * 255).astype(np.uint8)
            else:
                img_np = img_np.astype(np.uint8)
        Image.fromarray(img_np).save(filepath)
        print(f"  ✓ RGB image saved: {filepath}")
    
    # Handle depth images [H, W]
    elif len(img_np.shape) == 2:
        depth_min, depth_max = img_np.min(), img_np.max()
        if depth_max > depth_min:
            depth_normalized = ((img_np - depth_min) / (depth_max - depth_min) * 255).astype(np.uint8)
        else:
            depth_normalized = np.zeros_like(img_np, dtype=np.uint8)
        Image.fromarray(depth_normalized).save(filepath)
        print(f"  ✓ Depth image saved: {filepath}")

# --------------------- Main Script ---------------------
def main():
    print("="*80)
    print("G2 Robot Left Wrist Camera Access (Isaac Sim 5.1.0)")
    print("="*80)
    
    # Initialize simulation context
    sim = SimulationContext()
    
    # Robot USD path
    robot_usd_path = os.path.join(
        project_root,
        "source/matterix_assets/data/robots/genie/G2_place_workpiece/robot.usda"
    )
    if not os.path.exists(robot_usd_path):
        raise FileNotFoundError(f"Robot model file not found: {robot_usd_path}")
    
    print(f"\nLoading robot model: {robot_usd_path}")
    
    # Ground plane
    ground_cfg = sim_utils.GroundPlaneCfg(size=(10.0, 10.0))
    ground_cfg.func("/World/defaultGroundPlane", ground_cfg)
    
    # Lighting
    light_cfg = sim_utils.DomeLightCfg(intensity=1000.0, color=(0.9, 0.9, 1.0))
    light_cfg.func("/World/Light", light_cfg)
    
    # Robot configuration - include camera spawn config directly
    robot_cfg = ArticulationCfg(
        prim_path="/World/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=robot_usd_path,
            activate_contact_sensors=False,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=False),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True,
                solver_position_iteration_count=8,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(-0.5, 0, 0.0),
            rot=(1.0, 0.0, 0.0, 0.0),
        ),
        actuators={
            "left_arm": ImplicitActuatorCfg(
                joint_names_expr=[".*_arm_l_joint.*"],
                stiffness=1000.0,
                damping=200.0,
            ),
        },
    )
    
    # Instantiate robot
    print("Instantiating robot...")
    robot = Articulation(robot_cfg)
    
    # Reset simulation
    print("\nResetting simulation...")
    sim.reset()
    
    # Start simulation play
    print("Starting simulation play...")
    sim.play()
    
    # Fix camera visibility BEFORE creating Camera sensor
    camera_prim_path = "/World/Robot/gripper_l_base_link/Left_Camera"
    print(f"\nFixing camera visibility at: {camera_prim_path}")
    
    stage = sim.stage
    camera_prim = stage.GetPrimAtPath(camera_prim_path)
    
    if not camera_prim.IsValid():
        raise RuntimeError(f"Camera prim not found at path: {camera_prim_path}")
    
    visibility_attr = camera_prim.GetAttribute("visibility")
    current_visibility = visibility_attr.Get()
    print(f"  Current visibility: {current_visibility}")
    
    if current_visibility == "invisible":
        print("  Setting visibility to 'inherited'...")
        visibility_attr.Set("inherited")
        print(f"  ✓ Visibility updated")
    
    # Run a few steps to ensure visibility change takes effect
    for _ in range(5):
        sim.step(render=True)
    
    # Now configure Camera sensor to use the EXISTING prim
    # Use spawn=None to avoid creating a new prim
    print("\nConfiguring camera sensor to use existing USD camera...")
    
    try:
        camera_cfg = CameraCfg(
            prim_path=camera_prim_path,
            width=1280,
            height=1056,
            update_period=0.1,
            data_types=["rgb", "distance_to_image_plane"],
            spawn=None,  # Do NOT spawn a new camera, use existing one
        )
        left_camera = Camera(camera_cfg)
        print(f"  ✓ Camera sensor configured")
    except Exception as cfg_err:
        print(f"  ✗ Camera configuration failed: {cfg_err}")
        print("  Trying alternative approach with minimal config...")
        
        # Fallback: create camera with minimal configuration
        camera_cfg = CameraCfg(
            prim_path=camera_prim_path,
            update_period=0.1,
            data_types=["rgb"],
        )
        left_camera = Camera(camera_cfg)
        print(f"  ✓ Camera sensor configured (fallback mode)")
    
    # Wait for camera initialization
    print("\nWaiting for camera initialization...")
    max_steps = 100
    initialized = False
    for i in range(max_steps):
        sim.step(render=True)
        
        if left_camera.is_initialized:
            print(f"  ✓ Left camera initialized at Step {i}")
            initialized = True
            break
        
        if i % 20 == 0:
            print(f"    Step {i}: is_initialized = {left_camera.is_initialized}")
    
    if not initialized:
        print(f"  ✗ Camera not initialized after {max_steps} steps")
        raise RuntimeError("Camera initialization failed")
    
    # Reset camera
    print("\nResetting camera...")
    try:
        left_camera.reset()
        print(f"  ✓ Left camera reset successful")
    except Exception as e:
        print(f"  ⚠ Left camera reset warning: {e}")

    # Capture and save images
    print("\n" + "="*80)
    print("Starting image capture...")
    print("="*80)
    
    num_captures = 5
    capture_interval = 30
    
    for capture_idx in range(num_captures):
        print(f"\n--- Capturing frame {capture_idx + 1}/{num_captures} ---")
        for step in range(capture_interval):
            sim.step(render=True)
        
        try:
            camera_data = left_camera.data.output
            
            # Save RGB image
            if "rgb" in camera_data:
                rgb_data = camera_data["rgb"][0]
                save_image(rgb_data, f"left_wrist_rgb_frame_{capture_idx}.png", output_dir="./img")
            
            # Save depth image
            if "distance_to_image_plane" in camera_data:
                depth_data = camera_data["distance_to_image_plane"][0]
                save_image(depth_data, f"left_wrist_depth_frame_{capture_idx}.png", output_dir="./img")
                
        except Exception as e:
            print(f"  ✗ Camera data retrieval failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"Image capture complete! Total frames captured: {num_captures}")
    print(f"Images saved to: ./img folder")
    print("="*80)
    
    # Cleanup - delete camera sensor before closing app
    print("\nCleaning up...")
    try:
        del left_camera
        print("  ✓ Camera sensor deleted")
    except Exception as e:
        print(f"  ⚠ Camera cleanup warning: {e}")
    
    simulation_app.close()

if __name__ == "__main__":
    main()