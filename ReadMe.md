# delta_robot_Camera_Calibration
# To Calibrate Delta Robot using Cam-in-hand method follow these instructions:
## First Step
Print 0_Calibration Pattern.pdf on A4 paper

Find the Delta Robot Coordinates of the center of these circles
>[!NOTE]
> Make sure the circle grid will be visible in the camera

Save them in a numpy file

Here the numpy file is named "Matrices\forward_coordinates_2010-04-27_(1, 52, 11).npy"
## Second Step
Run 1_Camera_Circle_detection.py

Use a camera in the delta robot hand for that

Move the delta robot to different heights and press "s" in the image window to save camera coordinates

Repeat this step for different heights
## Third Step
Run 2_Camera_coordinates_sorter.ipynb to create and sort camera and robot coordinates

## Forth Step
Run 3_psudo_inverse_code.ipynb, its result will be in Matrices\values.npy

## Read More:
[Generating a general culturing microorganism pattern using a delta parallel robot and cam-in-hand calibration method
](https://doi.org/10.1109/ICRoM60803.2023.10412424)

[From Bricks to Bots: Automated Collision-Aware Sequence Planning for LEGO Reconstruction with a Two-Finger Gripper](https://doi.org/10.1109/ICCIA65044.2024.10768173)


## Related repos:
[Trajectory Planning Experimental Comparison Study](https://github.com/Arvin-Mohammadi/Delta-Robot-Trajectory-Planning-V3)

