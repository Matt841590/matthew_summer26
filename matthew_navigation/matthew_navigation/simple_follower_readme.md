## Movement Detection via Lidar

<img width="2160" height="2962" alt="image" src="https://github.com/user-attachments/assets/ca7a9c6e-6e2d-4fe3-ba21-e919996a2371" />


(This section was taken directly from the main README)


**This project is not yet complete and is therefore subject to change.**


- As it stands, this project is a Ros2-powered program that turns /scan data into a list of "seen objects" and can determine when one or multiple are moving
- Open five terminals
  - T1 - T4 will be identical to Autonomous GoTO Pose (see above)
    - These programs are opened to provide a complete TF tree and the user interface
  - In T5: cd ros_ws/src/matthew_summer26
  - In T5: ros2 run matthew_navigation follow
 
<img width="1119" height="912" alt="image" src="https://github.com/user-attachments/assets/9b22c38f-5f5b-4ffd-bbd4-0f7361601d7f" />

https://github.com/user-attachments/assets/8910f74d-8a3d-404c-8a24-de19ec1fc713

## Project vision
- The end goal of this project is to have the robot track and follow movement in its immediate environment
- The movement tracking part is currently implemented, but the map quickly degenerates when the robot starts moving

## Function Definitions
- simpleFollower.init()
    - This is what gets called when you instantiate the node, holding several data structures to keep track of objects, centroids, and how they have moved. 

- simpleFollower.odom_callabck
    - This is the callback that ensures that the robot is always working on up-to-date odom info

- simpleFollower.publish_initial_pose()
    - This publishes a PoseStamped() object that corresponds to the starting position and orientation of the robot
    - Without this, the whole Nav2 stack breaks because it cannot compete the TF tree
    - I obtained the published value experimentally by using the PoseEstimate tool in Rviz to set the robot in the right location and then ran ros2 run tf2_ros tf2_echo map base_link to see where the robot localized itself to 
    - Given this process the values I use are not 100% accurate, but they fall well within the ability of AMCL to correct at runtime

- simpleFollower.publish_destination_pose()
    - This publishes a PoseStamped() corresponding to somewhere that I want Nav2 to navigate the robot to
    - This, however, relies on Nav2, meaning that if Nav2 determines something cannot be done either correctly (the destination is inside an obstacle) or in error (the robot's map becomes inaccurate and it THINKS a destination is inside an obstacle) then this node cannot proceed. 

- simpleFollower.publish_centroid()
    - This node takes a pre-built list of "items" and publishes their centroids
    - Initially I was publishing each centroid individually as a Marker(), but this caused latency issues. If instead, you publish them as a MarkerArray(), the latency issues are resolved.

- simpleFollower.scan_subscriber_callabck
    - This node listens directly to /scan, extracting the heading and distance of each point 
    - The extracted data is then fed into a DBScan model, which groups them into discrete objects and, taking the average of all of the points, extracts a centroid for later use
    - Additionally, it is responsible for determining if something is moving by determining the most likely match between a centroid in the set it last saw and an arbitrary centroid in the newest set. If there is consistent displacement, it is probably moving

- main()
    - This function spins up the node and handles shutdown
