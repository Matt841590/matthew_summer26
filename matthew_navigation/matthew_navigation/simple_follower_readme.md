## Movement Detection via Lidar
(This section was taken directly from the main README)


**This project is not yet complete and is therefore subject to change.**


- As it stands, this project is a Ros2-powered program that turns /scan data into a list of "seen objects" and can determine when one or multiple are moving
- Open 5 terminals
  - T1 - T4 will be identical to Autonomous GoTO Pose (see above)
    - These programs are opened to provide a complete TF tree and the user interface
  - In T5: cd ros_ws/src/matthew_summer26
  - In T5: ros2 run matthew_navigation follow


https://github.com/user-attachments/assets/8910f74d-8a3d-404c-8a24-de19ec1fc713

## Project vision
- The end goal of this is to have the robot track and follow movement in its immediate environment
- The movement tracking part is currently implemented, but the map quickly degenerates when the robot starts moving

## Function Definitions
- simpleFollower.init()
    - this is what gets called when you instantiate the node, holding instances of the many things needed to track the objects and (in theory) follow them

- simpleFollower.odom_callabck
    - this is the callabck that ensures that the robot is always working on up-to-date odom info

- simpleFollower.publish_initial_pose()
    - This publishes a PoseStamped() object that corrsponds to whe starting position and orientation of the robot
    - Without this, the whole Nav2 stack breaks because it cannot compete the TF tree
    - I got the published value experimentally by using the PoseEstimate tool in Rviz to set the robot in (approx) the right spot and then running ros2 run tf2_ros tf2_echo map base_link to see where the robot localised itself to 
    - Given this process, the values I use are not 100% acurate, but they fall well within the ability of AMCL to correct at runtime

- simpleFollower.publish_destination_pose()
    - This publishes a PoseStamped() corresponding to somewhere that I want Nav2 to navigate the robot to
    - This, however, relies on Nav2, meaning that if Nav2 decodes someting cannot be done either correctly (the destinaiton is inside an obstacle) or in error (the robot's map becomes wrong due to something like encoder drift and it THINKS a destination is inside an obstacle) then this node cant really do anything about it

- simpleFollower.publish_centroid()
    - this node takes a pre-built list of "items" and publishes their centroids
    - Initially I was publishing each point individually as a Marker(), but this ran into latency issues. If instead, you publish them as a MarkerArray() you no longer have the latency issues.

- simpleFollower.scan_subscriber_callabck
    - this node slistens directly to /scan, extracting the heading and distance of each point 
    - the extracted data is then fed into a DBScan model, which groups them into discreete objects and, taking the average of all of the points, extracts a centroid for later use
    - Additionaly, it is responsible for determining if something is "moving" by determining the most likley match between a centroid in the set it last saw and an arbitrary centroid in the newest set. If there is consistent displacement, it is probabaly "moving"

- main()
    - This function is where the node spins up and shutdown handling is done
