## Autonomous Goto Pose
(This section is taken directly from the projects main README)
**This project assumes a pre-built map that lives in ros_ws/src/matthew_summer26/maps**

**This project is not yet complete and is therefore subject to change**

- This project is a patrolling utility, making your robot autonomoulsy navigate a set of points in a loop in a pre-built map
- open five terminals
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
    - to get abother point: ros2 topic echo /amcl_pose --once
    - or ros2 run tf2_ros tf2_echo map base_link

## Function Descriptions
- LoopPublisher.init()
    - This is what is called when you instantiate a new copy of the node

- LoopPublisher.publish_initial_pose()
    - This publishes a PoseStamped() object that corrsponds to whe starting position and orientation of the robot
    - Without this, the whole Nav2 stack breaks because it cannot compete the TF tree
    - I got the published value experimentally by using the PoseEstimate tool in Rviz to set the robot in (approx) the right spot and then running ros2 run tf2_ros tf2_echo map base_link to see where the robot localised itself to 
    - Given this process, the values I use are not 100% acurate, but they fall well within the ability of AMCL to correct at runtime

- LoopPublisher.publish_destination_pose()
    - This publishes a PoseStamped() corresponding to somewhere that I want Nav2 to navigate the robot to
    - This, however, relies on Nav2, meaning that if Nav2 decodes someting cannot be done either correctly (the destinaiton is inside an obstacle) or in error (the robot's map becomes wrong due to something like encoder drift and it THINKS a destination is inside an obstacle) then this node cant really do anything about it

- main()
    - This function is where the user can specify the number and (x,y) of destination points, as well as the starting position 