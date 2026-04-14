# Robot INFO
## Genie-G2
```bash
================================================================================
机器人关节信息
================================================================================

关节数量：46

所有关节名称：
  [0] idx01_body_joint1
  [1] idx02_body_joint2
  [2] idx111_chassis_lwheel_front_joint1
  [3] idx121_chassis_lwheel_rear_joint1
  [4] idx131_chassis_rwheel_front_joint1
  [5] idx141_chassis_rwheel_rear_joint1
  [6] idx03_body_joint3
  [7] idx112_chassis_lwheel_front_joint2
  [8] idx122_chassis_lwheel_rear_joint2
  [9] idx132_chassis_rwheel_front_joint2
  [10] idx142_chassis_rwheel_rear_joint2
  [11] idx04_body_joint4
  [12] idx05_body_joint5
  [13] idx11_head_joint1
  [14] idx12_head_joint2
  [15] idx21_arm_l_joint1
  [16] idx61_arm_r_joint1
  [17] idx13_head_joint3
  [18] idx22_arm_l_joint2
  [19] idx62_arm_r_joint2
  [20] idx23_arm_l_joint3
  [21] idx63_arm_r_joint3
  [22] idx24_arm_l_joint4
  [23] idx64_arm_r_joint4
  [24] idx25_arm_l_joint5
  [25] idx65_arm_r_joint5
  [26] idx26_arm_l_joint6
  [27] idx66_arm_r_joint6
  [28] idx27_arm_l_joint7
  [29] idx67_arm_r_joint7
  [30] idx31_gripper_l_inner_joint1
  [31] idx41_gripper_l_outer_joint1
  [32] idx71_gripper_r_inner_joint1
  [33] idx81_gripper_r_outer_joint1
  [34] idx32_gripper_l_inner_joint3
  [35] idx42_gripper_l_outer_joint3
  [36] idx72_gripper_r_inner_joint3
  [37] idx82_gripper_r_outer_joint3
  [38] idx33_gripper_l_inner_joint4
  [39] idx43_gripper_l_outer_joint4
  [40] idx73_gripper_r_inner_joint4
  [41] idx83_gripper_r_outer_joint4
  [42] idx39_gripper_l_inner_joint0
  [43] idx49_gripper_l_outer_joint0
  [44] idx79_gripper_r_inner_joint0
  [45] idx89_gripper_r_outer_joint0

关节限位：
  最小位置：tensor([[-1.0600,  0.0000]], device='cuda:0')
  最大位置：tensor([[0.0000, 2.6500]], device='cuda:0')

关节默认位置：tensor([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]],
       device='cuda:0')

连杆数量：56
连杆名称：['base_link', 'body_link1', 'chassis_link', 'body_link2', 'chassis_lwheel_front_link1', 'chassis_lwheel_rear_link1', 'chassis_rwheel_front_link1', 'chassis_rwheel_rear_link1', 'body_link3', 'chassis_lwheel_front_link2', 'chassis_lwheel_rear_link2', 'chassis_rwheel_front_link2', 'chassis_rwheel_rear_link2', 'body_link4', 'body_link5', 'head_base_link', 'head_link1', 'arm_base_link', 'head_link2', 'arm_l_link1', 'arm_r_link1', 'head_link3', 'arm_l_link2', 'arm_r_link2', 'arm_l_link3', 'arm_r_link3', 'arm_l_link4', 'arm_r_link4', 'arm_l_link5', 'arm_r_link5', 'arm_l_link6', 'arm_r_link6', 'arm_l_link7', 'arm_r_link7', 'arm_l_end_link', 'arm_r_end_link', 'gripper_l_base_link', 'gripper_r_base_link', 'gripper_l_inner_link1', 'gripper_l_outer_link1', 'gripper_l_center_link', 'gripper_r_inner_link1', 'gripper_r_outer_link1', 'gripper_r_center_link', 'gripper_l_inner_link3', 'gripper_l_outer_link3', 'gripper_r_inner_link3', 'gripper_r_outer_link3', 'gripper_l_inner_link4', 'gripper_l_outer_link4', 'gripper_r_inner_link4', 'gripper_r_outer_link4', 'gripper_l_inner_link2', 'gripper_l_outer_link2', 'gripper_r_inner_link2', 'gripper_r_outer_link2']
```

## Genie-G1
```bash
================================================================================
机器人关节信息
================================================================================

关节数量：34

所有关节名称：
  [0] idx01_body_joint1
  [1] idx02_body_joint2
  [2] idx11_head_joint1
  [3] idx12_head_joint2
  [4] idx21_arm_l_joint1
  [5] idx61_arm_r_joint1
  [6] idx22_arm_l_joint2
  [7] idx62_arm_r_joint2
  [8] idx23_arm_l_joint3
  [9] idx63_arm_r_joint3
  [10] idx24_arm_l_joint4
  [11] idx64_arm_r_joint4
  [12] idx25_arm_l_joint5
  [13] idx65_arm_r_joint5
  [14] idx26_arm_l_joint6
  [15] idx66_arm_r_joint6
  [16] idx27_arm_l_joint7
  [17] idx67_arm_r_joint7
  [18] idx31_gripper_l_inner_joint1
  [19] idx41_gripper_l_outer_joint1
  [20] idx71_gripper_r_inner_joint1
  [21] idx81_gripper_r_outer_joint1
  [22] idx32_gripper_l_inner_joint3
  [23] idx42_gripper_l_outer_joint3
  [24] idx72_gripper_r_inner_joint3
  [25] idx82_gripper_r_outer_joint3
  [26] idx33_gripper_l_inner_joint4
  [27] idx43_gripper_l_outer_joint4
  [28] idx73_gripper_r_inner_joint4
  [29] idx83_gripper_r_outer_joint4
  [30] idx39_gripper_l_inner_joint0
  [31] idx49_gripper_l_outer_joint0
  [32] idx79_gripper_r_inner_joint0
  [33] idx89_gripper_r_outer_joint0

关节默认位置：tensor([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
         0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]], device='cuda:0')

连杆数量：42
连杆名称：['base_link', 'body_link1', 'body_link2', 'head_link1', 'arm_base_link', 'head_link2', 'arm_l_base_link', 'arm_r_base_link', 'arm_l_link1', 'arm_r_link1', 'arm_l_link2', 'arm_r_link2', 'arm_l_link3', 'arm_r_link3', 'arm_l_link4', 'arm_r_link4', 'arm_l_link5', 'arm_r_link5', 'arm_l_link6', 'arm_r_link6', 'arm_l_end_link', 'arm_r_end_link', 'gripper_l_base_link', 'gripper_r_base_link', 'gripper_l_inner_link1', 'gripper_l_outer_link1', 'gripper_l_center_link', 'gripper_r_inner_link1', 'gripper_r_outer_link1', 'gripper_r_center_link', 'gripper_l_inner_link3', 'gripper_l_outer_link3', 'gripper_r_inner_link3', 'gripper_r_outer_link3', 'gripper_l_inner_link4', 'gripper_l_outer_link4', 'gripper_r_inner_link4', 'gripper_r_outer_link4', 'gripper_l_inner_link2', 'gripper_l_outer_link2', 'gripper_r_inner_link2', 'gripper_r_outer_link2']
tensor([[[ 0.0000,  0.5500],
         [ 0.0000,  1.5708],
         [-1.5708,  1.5708],
         [-0.3491,  0.5236],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-3.1416,  3.1416],
         [-0.7854,  0.0000],
         [ 0.0000,  0.7854],
         [-0.7854,  0.0000],
         [ 0.0000,  0.7854],
         [-0.1745,  0.1745],
         [-0.1745,  0.1745],
         [-0.1745,  0.1745],
         [-0.1745,  0.1745],
         [-0.0349,  0.0349],
         [-0.0349,  0.0349],
         [-0.0349,  0.0349],
         [-0.0349,  0.0349],
         [-2.0000,  2.0000],
         [-2.0000,  2.0000],
         [-2.0000,  2.0000],
         [-2.0000,  2.0000]]], device='cuda:0')
torch.Size([1, 34, 2])
tensor([[1.0000e-01, 5.0000e-01, 1.0000e+00, 1.0000e+00, 3.1400e+00, 3.1400e+00,
         3.1400e+00, 3.1400e+00, 3.9250e+00, 3.9250e+00, 3.9250e+00, 3.9250e+00,
         3.9250e+00, 3.9250e+00, 3.9250e+00, 3.9250e+00, 3.9250e+00, 3.9250e+00,
         1.7453e+02, 1.7453e+02, 1.7453e+02, 1.7453e+02, 1.7453e+02, 1.7453e+02,
         1.7453e+02, 1.7453e+02, 1.7453e+02, 1.7453e+02, 1.7453e+02, 1.7453e+02,
         1.7453e+02, 1.7453e+02, 1.7453e+02, 1.7453e+02]], device='cuda:0')
torch.Size([1, 34])

