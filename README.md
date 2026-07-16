# matthew_summer26

# SOURCES
## Makerspet (Everything outside of the folder matthew_summer26)
 - https://github.com/kaiaai/kaiaai
   - this contains the code needed to connect to the robot and several cool pre-built implementations to explore

 - https://makerspet.com/product/arduino-ros2-self-driving-robot-120mm-build-pack/
   - This is where you get the hardware and printed parts/STL files

## frontier_exploration_ros2_iron
 - https://github.com/Matt841590/frontier_exploration_ros2_iron
   - this is my personal fork off of the original implementation (The orignal does not work with Ros2 Iron)
   - Original repo: https://github.com/mertgulerx/frontier_exploration_ros2

## Tutorials I used
- https://roboticsbackend.com/ros2-nav2-generate-a-map-with-slam_toolbox/
  - shows how to generate a map using lidar

- https://roboticsbackend.com/ros2-nav2-tutorial/
  - shows how to compell the robot to autonomoulsy navigate inside a map using Lidar, SLAM, nav2

# RUNTIME INSTRUCTIONS
**NOTE: A RUNNING instance of Docker (Desktop or CLI) is required to run all projects inside this repo**

Docker can be installed at https://docs.docker.com/engine/install/

## Running Makerspet Pre-Built packages
- All Makerspet Pre-Builts will run properly when built according to directions at https://github.com/kaiaai/kaiaai
- All Makerspet Pre-Builts can be run from the root level of the docker container, eg :#/
  - Ex: root@da15bf37667e:/# ros2 launch kaiaai_bringup physical.launch.py
- all packages require that the physical bringup is running in another terminal
  - This is what conencts your computer to the physical robot!

## Running my projects
- All of my projects can only be run from /ros_ws/src/matthew_summer26
- All of my projects require "colcon build" to be run at least once per container 
  - When a new container builds off of the dockerfile it does not colcon build
  - When using an old container (Re-opening it VSCode) you should not need to rebuild
  - colcon build is what ROS2 uses to build all fo the nodes and conenct topics between them
- All my projects require running "source install/setup.bash" upon reaching my directory in a new terminal
  - This must also be done after each time you run "colcon build"
  - This makes it so that the terminal sees the most up to date version of the nodes
- All of my projects require that the physical bringup (kaiaai_bringup physical.launch.py) is running in a nother terminal
  - This is what conencts your computer to the physical robot!

# MY PROJECTS
## Teleop
- This project was a simple, easy-to-use teleop utility built to support the needs of my other projects
- open 2 terminals (herefater refered to as T1 and T2)
  - In T1: ros2 launch kaiaai_bringup physical.launch.py
  - In T2: cd /ros_ws/src/matthew_summer26
  - In T2: ros2 run matthew_teleop teleop
**Note: This assumes you have built and sourced properly**

## Basic Mapping
- This project is a basic manual mapping tutorial, using Nav2 and SLAM to create a map
- open 5 terminals (refered to as T1 - T5)
  - In T1: ros2 launch kaiaai_bringup physical.launch.py
    - Allows your machine to communicate witht the robot and populates part of the TF tree
  - In T2: ros2 launch nav2_bringup navigation_launch.py params_file:=/ros_ws/src/matthew_summer26/nav2_config.yaml
    - This starts the standard Nav2 navigation stack, but with a custom paramaters file configured for the specifics of the robot I was using
    - TODO: Do I actually need this?
  - In T3: ros2 launch slam_toolbox online_async_launch.py
    - This starts slam_toolbox which allows the robot to both create a map, determine its location inisde the map, and populates part of the TF tree
  - In T4: ros2 run rviz2 rviz2 -d /opt/ros/iron/share/nav2_bringup/rviz/nav2_default_view.rviz
    - This starts the default viewer of Rviz whoch is handy to see the map that the robot is making while it makes it
  - In T5: cd /ros_ws/src/matthew_summer26
  - In T5: ros2 run matthew_teleop teleop
    - This starts the telop used to drive the robot around so it can build the map

To save your map, "ros2 run nav2_map_server map_saver_cli -f my_map"

## Autonomous Mapping + Exploration
- this project is a basic autonomous mapping tutorial using Nav2 and slam
- open 5 terminals
  - T1 - T4 will be identical to Basic mapping (see above)
  - In T5: cd ros_ws/src/matthew_summer26/frontier_exploration_ros2_iron
  - In T5: ros2 launch frontier_exploration_ros2 frontier_explorer.launch.py
    - This program autonomoulsy assigns goals for the robot to move to based on the knowledge of the map it currently has 

## Autonomous Goto Pose
**This project assumes a pre-built map that lives in ros_ws/src/matthew_summer26/maps**
- This project is a patrolling utility, making your robot autonomoulsy navigate a set of points in a loop in a pre-built map
- open 5 terminals
  - In T1: ros2 launch kaiaai_bringup physical.launch.py
    - this is the robot's bringup that lets it talk with your computer
  - In T2: ros2 launch nav2_bringup localization_launch.py \
    map:=/ros_ws/src/matthew_summer26/maps/baseline_map.yaml \
    use_sim_time:=false \
    params_file:=/ros_ws/src/matthew_summer26/nav2_config.yaml
    - This launches Nav2's AMCL utiltiy, publishing the map on /map and localizing the robot in it
    - This also has a custom confied params file modified for the robot I was using
  - In T3: ros2 launch nav2_bringup navigation_launch.py \
    use_sim_time:=false \
    params_file:=/ros_ws/src/matthew_summer26/nav2_config.yaml
    - This launches Nav2's navigation stack, allowing it to accept waypoints and go to them
    - This also has a custom confied params file modified for the robot I was using
  - In T4: ros2 run rviz2 rviz2 -d $(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz
    - This is just an RViz window to help the user visualize what is going on
  - In T5: cd ros_ws/src/matthew_summer26
  - In T5: ros2 run matthew_navigation loop
    - This is my custom-made "follow a set of arbitrary points that arbitrarily make a loop" utility
    - Useful for patroling an area on a timer or something similar

## Movement Detection via Lidar
**This project is not yet complete and is therefore subject to change**
- This project's end goal is to enable a robot with only a lidar to track movment in its environment and follow it at a short distance
- As it stands, this project is a Ros2-powered program that turns /scan data into a list of "seen objects" and can determine when one or multiple are moving
- Open 5 terminals
  - T1 - T4 will be identical to Autonomous GoTO Pose (see above)
    - I open and provide all of these utilities so that the TF tree is complete and the final goal isnt missing any infastructure
  - In T5: cd ros_ws/src/matthew_summer26
  - In T5: ros2 run matthew_navigation follow
    - This utility will, as of 7/16/2026 allow a robot recieving /scan data to track moving objects
    - However, when the robot attempts to follow a moving object, the map gets warped and the location of the objects drifts heavily as a result
    - TODO: try making the "close enough" radius really big?
    - TODO: try smoothing the Lidar to be less noisy?