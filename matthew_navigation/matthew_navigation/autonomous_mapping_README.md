## Autonomous Mapping + Exploration

<img width="2160" height="2962" alt="image" src="https://github.com/user-attachments/assets/2313d5cb-619a-402c-9642-fa32b81f5395" />


(This section was taken from the main README)
    - open 5 terminals (refered to as T1 - T5)
    - In T1: ros2 launch kaiaai_bringup physical.launch.py
        - Allows your machine to communicate witht the robot and populates part of the TF tree
    - In T2: ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false
        - This starts slam_toolbox which allows the robot to both create a map, determine its location inisde the map, and populates part of the TF tree
    - In T3: ros2 run rviz2 rviz2 -d /opt/ros/iron/share/nav2_bringup/rviz/nav2_default_view.rviz
        - This starts the default viewer of Rviz whoch is handy to see the map that the robot is making while it makes it
    - In T4: ros2 launch nav2_bringup navigation_launch.py params_file:=/ros_ws/src/matthew_summer26/nav2_config.yaml
        - This starts the standard Nav2 navigation stack, but with a custom paramaters file configured for the specifics of the robot I was using
    - In T5: cd ros_ws/src/matthew_summer26/frontier_exploration_ros2_iron
    - In T5: ros2 launch frontier_exploration_ros2 frontier_explorer.launch.py
        - This program autonomoulsy assigns goals for the robot to move to based on the knowledge of the map it currently has

<img width="1978" height="1086" alt="image" src="https://github.com/user-attachments/assets/253f83bb-7f66-4199-ab14-fec0a8c60f62" />


https://github.com/user-attachments/assets/24357b84-f305-480d-9f33-39252bfb0626


This project relies on three excellent pieces of software:
- Nav2: Nav2 is the SOTA autonomous navigation package for Ros2. It allows a robot, when properly localized, to navigate from point A to point B in an efficient and direct manner. 

- Slam_toolbox: Slam_toolbox is the SOTA industry-standard "Simultaneous Localization And Mapping" package for Ros2. In this project it provides vital information to the robot, both creating the map itself, and determining where the robot is in the map at any given time

- Rviz: Rviz is a visualization tool that presents a simple, easy to understand visual representation of what the robot sees. It allows the end user to know what the map looks like, where the robot thinks obstacles might be, and where the robot thinks it is in 3-D space

- Frontier_exploration: If SLAM tells the robot where it is, and Nav2 allows it to plan a path to an arbitrary endpoint, Frontier_exploration tells the robot what destination points are most worth chasing, in what order they should be explored, and where to go next when a promising frontier turns into a dead end. 
