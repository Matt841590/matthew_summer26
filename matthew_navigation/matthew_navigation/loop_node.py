import rclpy
from rclpy.node import Node
# - importing message type for initial pose and destinations
from geometry_msgs.msg import PoseStamped
# - simplecommander for publishing stuff without race conditions
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

class LoopPublisher(Node):
    def __init__(self):
        super().__init__("loop_publisher_node")
        self.nav = BasicNavigator()

    def publish_inital_pose(self, x, y):
        # - build the msg object
        msg = PoseStamped()

        # - populate the msg object
        # - populate header
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'

        # - populate body (position)
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = 0.0

        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = 0.0
        msg.pose.orientation.w = 1.0

        # - publish the msg object
        self.get_logger().info(f'Attempting to publish starting point {x}, {y}')
        self.nav.setInitialPose(msg)
        self.nav.waitUntilNav2Active()
        self.get_logger().info(f'Published point {x}, {y}')

    def publish_destination_pose(self, x, y):
        # - build the msg object
        msg = PoseStamped()

        # - populate the msg object
        # - populate header
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'

        # - populate body (position)
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = 0.0

        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = 0.0
        msg.pose.orientation.w = 1.0

        # - publish the msg object
        self.get_logger().info(f'Attempting to publish destination point {x}, {y}')
        self.nav.goToPose(msg)
        while not self.nav.isTaskComplete():
            feedback = self.nav.getFeedback()
            # - self.get_logger().info(f'Feedback: {feedback}')
        # - self.get_logger().info(f'Published point {x}, {y} or failed trying, see feedback')

        result = self.nav.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            self.get_logger().info('Goal was canceled!')
        elif result == TaskResult.FAILED:
            self.get_logger().info('Goal failed!')

# - main
def main(args=None):
    rclpy.init(args=args)
    loop_publisher = LoopPublisher()

    # - list of poses to iterate through
    # - 0: by couch
    # - 1: by back wall
    # - 2: by trunk
    # - 3: by closet
    # - 4: NEW by oven
    # - 5: NEW by barstool
    # - 6: NEW on problematic rug
    # - 7: origin
    x_list = [2.30066, 3.432117, 2.6698, -1.8398, -3.994846, -3.85524, -1.74305, -0.745320, 0.330082, -0.1110]
    y_list = [-0.12961, 2.647237, 6.3336, 2.10395, 2.5412556, 0.589211, 0.299801, 2.172579, 1.843161, 0.021468]

    # - publishing intital pose
    loop_publisher.publish_inital_pose(-0.1110, 0.021468)

    # - publishing destination points sequentially
    for i in range(len(x_list)):
        # 1. Send the goal and wait for Nav2 to accept it
        goal_future = loop_publisher.publish_destination_pose(x_list[i], y_list[i])

    rclpy.shutdown()

# - entry point to main
if __name__ == '__main__':
    main()
    