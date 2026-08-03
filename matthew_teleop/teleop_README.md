## Teleop
(This section was taken directly from the main README)
- This project was a simple, easy-to-use teleop utility built to support the needs of my other projects
- open two terminals (herefater refered to as T1 and T2)
  - In T1: ros2 launch kaiaai_bringup physical.launch.py
  - In T2: cd /ros_ws/src/matthew_summer26
  - In T2: ros2 run matthew_teleop teleop

## Function Definitions
- TelopNode.__init__()
    - This is the function that gets called when you create a new teleop node object
    - This function is where you go to change:
        - How often to publish new directions to the robot
        - Maximum speed that the robot can move
        - The starting speed the robot will have
        - How much the robot speeds up or slows down each time you press a key

- TelopNode.get_key()
    - This function is a helper directly responsible for reading what key(s) the user has pressed

- TelopNode.timer_callabck()
    - This function runs over and over again based on the frequency specified in __init__
    - This function is responsible for publishing current state information to the user in an easy to read way
    - This funciton recieves the pressed keys from get_key, and is thereofre responsible for:
        - chnaging the linear and angular speed of the robot
        - initiating an immediate emergency stop when instructed by the user

- TelopNode.main()
    - This function is the entry point where the ndoe is created and started
