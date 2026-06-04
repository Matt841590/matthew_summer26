# matthew_summer26

## Setup instructions

### VsCode setup

-goto settings, enter git repository managers and change everything to look as such:

![alt text](image.png)

-goto your version control system button on the sidebar, and select "pick a repo" (or whatever) and select "matthew_summer26"

### How to run Makerspet packages

to run makerspet packages, simply use the commands given from their resources and type them at the root level (at :/#)

Ex : root@da15bf37667e:/# ros2 launch kaiaai_bringup physical.launch.py

### How to run MY packages

to run My packages, cd to "ros_ws/src/matthew_summer26/" and then run as usual

## My Packages

> **NOTE: ALL OF MY PACKAGES REQUIRE THE PHYSICAL BRINGUP FROM MAKERSPET TO BE RUNNING IN A SEPERATE TERMINAL!**

### Matthew Teleop -

a simple package meant to provide basic teleop functionality 

to run: "ros2 run matthew_teleop teleop"  

Ex : root@da15bf37667e:/ros_ws/src/matthew_summer26# ros2 run matthew_teleop teleop

## Mapping 

### Instructions

info from: https://roboticsbackend.com/ros2-nav2-generate-a-map-with-slam_toolbox/

- Open 5 terminals (T1 - T5)
- In T1 run "ros2 launch kaiaai_bringup physical.launch.py"
- - this is the package that publishes all of the TF's besides those for map (inhereted from Makerspet)

- In T2 run "ros2 launch nav2_bringup navigation_launch.py"
- - This starts a pre-built Nav2 navigation stack (TODO: Make my own?)

- In T3 run "ros2 launch slam_toolbox online_async_launch.py"
- - this is a pre-built configuration of slam_toolbox (TODO: make my own?)

- In T4 run "ros2 run rviz2 rviz2 -d /opt/ros/iron/share/nav2_bringup/rviz/nav2_default_view.rviz"
- - this is a pre-built rViz configuration (TODO: make my own?)

- In T5 run "ros2 run matthew_teleop teleop" 
- - requires that you are in ros_ws/src/matthew_summer26 and do both colcon build and source install/setup.bash first