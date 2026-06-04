"""
Name: matthew_teleop_node.py
Purpose: A node meant to provide basic teleop functionality 
"""
# - imports
import termios
import os
import tty
import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# - node class
class TelopNode(Node):
    # - init
    def __init__(self):
        # - recursive init
        super().__init__("teleop_node")

        # - publisher
        self.twist_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # - timer for the publisher
        self.timer_period = 0.2 
        self.twist_timer = self.create_timer(self.timer_period, self.timer_callback)

        # - memeber variables
            # - max speeds
        self.linear_max_speed = 0.22
        self.angular_max_speed = 0.44

            # - starting speeds
        self.linear_speed = 0.0
        self.angular_speed = 0.0

            # - step sizes
        self.linear_step = 0.02
        self.angular_step = 0.04
    
        # - print operating instrucitons and starting state
        self.get_logger().info('Use w/x to change velocity in the fowrds/back direction')
        self.get_logger().info('Use a/d to change velocity in the CCW/CW direction')
        self.get_logger().info('Use s to stop')
        self.get_logger().info(f'Current linear velocity: {self.linear_speed}')
        self.get_logger().info(f'Current angular velocity: {self.angular_speed}')

    # - helper to read keyboard
    def get_key(self):
        # - get fd and save state
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)

        # - try block to guarntee return to good state
        try:
            # - pull the most recently pressed chracter
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            # - restore terminal state
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch

    # - timer callback
    def timer_callback(self):
        # - print instructions and current state again
        self.get_logger().info('Use w/x to change velocity in the fowrds/back direction')
        self.get_logger().info('Use a/d to change velocity in the CCW/CW direction')
        self.get_logger().info('Use s to stop')
        self.get_logger().info(f'Current linear velocity: {self.linear_speed}')
        self.get_logger().info(f'Current angular velocity: {self.angular_speed}')

        # - make Twist object
        msg = Twist()

        # - read key from helper function
        key = self.get_key()

        # - python case (match) statment to chnage values
        match key:
            # - increase forwards
            case 'w':
                speed = self.linear_speed + self.linear_step
                if abs(speed) >= self.linear_max_speed:
                    speed = self.linear_max_speed
                self.linear_speed = speed

            # - increase backwards
            case 'x':
                speed = self.linear_speed - self.linear_step
                if abs(speed) >= self.linear_max_speed:
                    speed = -1 * self.linear_max_speed
                self.linear_speed = speed

            # - increase CCW
            case 'a':
                speed = self.angular_speed + self.angular_step
                if abs(speed) >= self.angular_max_speed:
                    speed = self.angular_max_speed
                self.angular_speed = speed

            # - increase CW
            case 'd':
                speed = self.angular_speed - self.angular_step
                if abs(speed) >= self.angular_max_speed:
                    speed = -1 * self.angular_max_speed
                self.angular_speed = speed

            # - Emergency Stop
            case 's':
                self.angular_speed = 0.0
                self.linear_speed = 0.0

        # - round speeds to 2 decimal places (prevents funny rounding error)
        self.linear_speed = round(self.linear_speed, 2)
        self.angular_speed = round(self.angular_speed, 2)

        # - publish the speeds
        msg.linear.x = self.linear_speed
        msg.angular.z = self.angular_speed * 5

        self.twist_publisher.publish(msg)

# - main
def main(args=None):
    # - build node
    rclpy.init(args=args)
    teleop_node = TelopNode()
    
    # - spin node
    rclpy.spin(teleop_node)

    # - kill node
    teleop_node.destroy_node()
    rclpy.shutdown()

# - thing that runs main (entry point?)
if __name__ == '__main__':
    main()