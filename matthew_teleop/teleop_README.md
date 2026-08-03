## Teleop
(This section was taken directly from the main README)
- This project was a simple, easy-to-use teleop utility built to support the needs of my other projects
- open 2 terminals (herefater refered to as T1 and T2)
  - In T1: ros2 launch kaiaai_bringup physical.launch.py
  - In T2: cd /ros_ws/src/matthew_summer26
  - In T2: ros2 run matthew_teleop teleop
 
<img width="986" height="653" alt="image" src="https://github.com/user-attachments/assets/5faad3fc-5adf-40db-b39f-0f24a058d80a" />

## Function Definitions
- TeleopNode.__init__()
    - This is the function that creates a new Telop_Node object
    - This function allows the user to change:
        - How often to publish new directions to the robot
        - Maximum speed that the robot can move
        - The starting speed the robot will have
        - How much the robot speeds up or slows down each time you press a key

- TeleopNode.get_key()
    - This function is a helper directly responsible for reading what key(s) the user has pressed

- TeleopNode.timer_callabck()
    - This function runs over and over again based on the frequency specified in __init__
    - This function is responsible for publishing current state information to the user in an easy to read way
    - This funciton recieves the pressed keys from get_key, and is thereofre responsible for:
        - Changing the linear and angular speed of the robot
        - Initiating an immediate emergency stop when instructed by the user

- TeleopNode.main()
    - This function is the entry point where the ndoe is created and started
