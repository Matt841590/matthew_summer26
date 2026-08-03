## Basic Mapping
(This section is taken from the main README)
- This project is a basic manual mapping tutorial, using Nav2 and SLAM to create a map
- Open five terminals (refered to as T1 - T5)
  - In T1: ros2 launch kaiaai_bringup physical.launch.py
    - Allows your machine to communicate witht the robot and populates part of the TF tree
  - In T2: ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false
    - This starts slam_toolbox which allows the robot to both create a map, determine its location inisde the map, and populates part of the TF tree
  - In T3: ros2 run rviz2 rviz2 -d /opt/ros/iron/share/nav2_bringup/rviz/nav2_default_view.rviz
    - This starts the default viewer of Rviz whoch is handy to see the map that the robot is making while it makes it
  - In T4: cd /ros_ws/src/matthew_summer26, then In T4: ros2 run matthew_teleop teleop
    - This starts the telop used to drive the robot around so it can build the map

  OR 

  - In T4: Ros2 run teleop_twist_keyboard teleop_twist_keyboard
    - This is the ros2 provided teleop script for keyboards
   
https://github.com/user-attachments/assets/609cb32c-2d5c-47ae-aed9-5b04bb33fabc

This project is powered by two excellent, pre-extant software packages as described below. 

- Slam_toolbox: Slam_toolbox is the SOTA industry-standard "Simultaneous Localization And Mapping" package for Ros2. In this project it provides vital information to the robot, both creating the map itself, and determining where the robot is in the map at any given time

- Rviz: Rviz is a visualization tool that presents a simple, easy to understand visual representation of what the robot sees. It allows the end user to know what the map looks like, where the robot thinks obstacles might be, and where the robot thinks it is in 3-D space
