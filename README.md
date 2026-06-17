# matthew_summer26

# SOURCES
## Everything makerspet (outside of the package matthew_summer26)

https://github.com/makerspet

## frontier_exploration_ros2_iron (inside matthew_summer26)

This is my personal fork off of https://github.com/mertgulerx/frontier_exploration_ros2 that fixes some specific issues I was having

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

## Manual Mapping 

### Instructions

info from: https://roboticsbackend.com/ros2-nav2-generate-a-map-with-slam_toolbox/

- Open 5 terminals (T1 - T5)
- In T1 run "ros2 launch kaiaai_bringup physical.launch.py"
- - this is the package that publishes all of the TF's besides those for map (inhereted from Makerspet)

- In T2 run "ros2 launch nav2_bringup navigation_launch.py params_file:=/ros_ws/src/matthew_summer26/nav2_config.yaml"
- - This starts a pre-built Nav2 navigation stack (TODO: Make my own?)

- In T3 run "ros2 launch slam_toolbox online_async_launch.py"
- - this is a pre-built configuration of slam_toolbox (TODO: make my own?)

- In T4 run "ros2 run rviz2 rviz2 -d /opt/ros/iron/share/nav2_bringup/rviz/nav2_default_view.rviz"
- - this is a pre-built rViz configuration (TODO: make my own?)

- In T5 run "ros2 run matthew_teleop teleop" 
- - requires that you are in ros_ws/src/matthew_summer26 and do both colcon build and source install/setup.bash first

## Autonomous Mapping + Exploration
 T1-T4 are the same

 T5 - /ros_ws/src/matthew_summer26/frontier_exploration_ros2_iron# ros2 launch frontier_exploration_ros2 frontier_explorer.launch.py

 after colcon build and stuff

## MAKERSPET Autonomous Mapping Stack
- T1: physical bringup (same as above)
- T2: ros2 launch kaiaai_bringup navigation.launch.py slam:=True
- T3: ros2 launch explore_lite explore.launch.py

## To save a map
- ros2 run nav2_map_server map_saver_cli -f my_map


## For GoTo Pose (with extant map, assumes it lives in matthew_summer26/maps)
- T1: ros2 launch kaiaai_bringup physical.launch.py
- - This is the pre-built robot bringup

- T2: ros2 launch nav2_bringup localization_launch.py \
    map:=/ros_ws/src/matthew_summer26/maps/baseline_map.yaml \
    use_sim_time:=false \
    params_file:=/ros_ws/src/matthew_summer26/nav2_config.yaml
- - This publishes the map and localises the robot in it using AMCL 

- T3: ros2 launch nav2_bringup navigation_launch.py \
    use_sim_time:=false \
    params_file:=/ros_ws/src/matthew_summer26/nav2_config.yaml
- - This is the basic Nav2 "go to this place from where you are" utility

- T4: ros2 run rviz2 rviz2 -d $(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz 
- - This is just a RVIZ window

- T5: ros2 run matthew_navigation loop 
- - this is my custom "make a loop, hitting all of these points" utility
- - must do colcon build and source install/setup.bash in matthew_naviagtion

## Initial pose (~beside where I usually sit)
    x: -0.1110

    y: 0.021468

    to get abother point: ros2 topic echo /amcl_pose --once 

## For movement detection (chasing?)
 - T5: ros2 run matthew_navigation follow
 - - This is an implementation of https://github.com/gabe-ochoa/lidar-tracking that should allow me to follow
