# delta_robot_Camera_Calibration
# To Calibrate Delta Robot using Cam-in-hand method follow these instructions:
## First Step
"""
Print 0_Calibration Pattern.pdf On an A4 paper
Find Delta Robot Coordinates of center of these circles
>[!NOTE]
> Make sure the circle grid will be visible in the camera
Save them in a numpy file
here the numpy file is named "Matrices\forward_coordinates_2010-04-27_(1, 52, 11).npy"
"""
## Second Step
```
Run 1_Camera_Circle_detection.py
use a camera in delta robot hand for that
move delta robot in different heights and press "s" in image window to save camera coordinates
repeat this step for different heights
```
## Third Step
Run 2_Camera_coordinates_sorter.ipynb to create and sort camera and robot coordinates

## Forth Step
Run 3_psudo_inverse_code.ipynb its result will be in Matrices\values.npy
