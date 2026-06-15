import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
# - importing message type for initial pose
from geometry_msgs/msg import PoseWithCovarianceStamped
# - importing message for goto pose
from nav2_msgs.action import NavigateToPose

class LoopPublisher(Node):
    def __init__(self):
        super().__init__("loop_publisher_node")
        self.intital_pose_publisher = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.destination_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def publish_inital_pose(self, x, y)
        msg = PoseWithCovarianceStamped()

        # - setting the frame
        msg.header.frame_id = 'map'
        msg.header.stamp = node.get_clock().now().to_msg()

        # - setting the pose itself
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        # - TODO: determine if I need to touch orientation

        # - setting a basic covarience
        msg.pose.covariance = [0.0] * 36
        msg.pose.covariance[0] = 0.25
        msg.pose.covariance[7] = 0.25
        msg.pose.covariance[35] = 0.06

        # - publishing 
        self.intital_pose_publisher.publish(msg)

    def publish_destination_pose(self, x, y)
        # - making and populating the goal msg
        msg = NavigateToPose.Goal()


# - main
def main(args=None):
    rclpy.__init__(args=args):
    loop_publisher = LoopPublisher()
    rclpy.spin(loop_publisher)

# - entry point to main
if __name__ == '__main__':
    main()
    