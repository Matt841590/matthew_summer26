import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
# - importing message type for initial pose and destinations
from geometry_msgs.msg import PoseStamped
# - simplecommander for publishing stuff without race conditions
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
# - importing stuff for the movement follower library
import numpy as np
from sensor_msgs.msg import LaserScan
from lidar_tracker import TrackingEngine

class MovementFollowerNode(Node):
    def __init__(self):
        super().__init__("movement_follower_node")

        # - basic navigator to publish destination poses
        self.nav = BasicNavigator()

        # - tracking engine
        self.engine = TrackingEngine()

        # - subscriber to /scan
        self.scan_subscriber = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_subscriber_callabck,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        self.scan_subscriber # - so it doesnt scream about unused variables

        # - holder for lidar values, first is the object id and second is the displacements it has been in the past
        self.objects_list[][]

    # - init pose 
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

    # - goto pose
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

        result = self.nav.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            self.get_logger().info('Goal was canceled!')
        elif result == TaskResult.FAILED:
            self.get_logger().info('Goal failed!')
    
    # - subscriber to /scan callabck
    def scan_subscriber_callabck(self, msg):
        #self.get_logger().info(f'Got Lidar scan!')
        # - capture distances
        distances = np.array(msg.ranges)
        # - capture anfles
        angles = msg.angle_min + np.arange(len(distances)) * msg.angle_increment

        # - filtering and changing units of measure
        valid_mask = (distances > 0.0) & (distances > msg.range_min) & (distances < msg.range_max)
        distances = distances[valid_mask]
        angles = angles[valid_mask]
        distances_mm = distances * 1000.0

        # - zip them together
        angle_dist_tuples = np.column_stack((angles, distances_mm))

        # - checking to be sure I didnt discard everything
        if len(angle_dist_tuples) == 0:
            self.get_logger().warn("All points filtered out this frame!")

        # - get frames
        frame = self.engine.process_scan(angle_dist_tuples)

        # - printing what I found
        for obj in frame.objects:
            self.get_logger().info(f"Object #{obj.object_id} at ({obj.centroid.x:.0f}, {obj.centroid.y:.0f})mm")
            self.is_moving(frame, obj, obj.object_id, self.objects_list)

        # - for object in frame
            # - while object is moving (is_moving returns true)
                # - follow object

    # - I did not make this, stole it from somewhere
    def calculate_ema(self, data, alpha):
        # alpha is the smoothing factor (between 0 and 1)
        # Higher alpha = reacts faster to new data; Lower alpha = smoother
        x_ema = np.zeros(len(data))
        y_ema = np.zeros(len(data))
        x_ema[0] = data[0][0] # Initialize first element
        y_ema[0] = data[0][1]
        
        for i in range(1, len(data)):
            x_ema[i] = alpha * data[i][0] + (1 - alpha) * x_ema[i-1]
            y_ema[i] = alpha * data[i][1] + (1 - alpha) * y_ema[i-1]
        ema = np.column_stack((x_ema, y_ema))
        return ema

    # - also stole parts of this
    def calculate_average_dist(self, ema):
        x_ema = ema[:, 0]  # Grab every row, but only column 0 (X)
        y_ema = ema[:, 1]  # Grab every row, but only column 1 (Y)
        x_avg = x_ema[0]- (np.sum(x_ema) / len(x_ema))
        y_avg = y_ema[0] - (np.sum(y_ema) / len(y_ema))
        return (x_avg, y_avg)


    def is_moving(self, frame, object, object_id):
        # - setting alpha (soothing factor)
        # - higher -> reacts faster, lower -> smoother
        alpha = 0.05

        # - extract trail
        trail = self.engine.get_trajectory(object.object_id)

        # - extract # points <= 10
        if len(trail) < 10:
            num_points = len(trail)
        else:
            num_points = 10

        # - extract num_points 
        relevant_points = np.zeros((num_points, 2))
        for i in range(num_points):
            relevant_points[i] = (trail[i - num_points].x,trail[i - num_points].y)

        # - calculate and judge ema
        ema = self.calculate_ema(relevant_points, alpha)
        average_dist = self.calculate_average_dist(ema)

        # - informing user
        self.get_logger().info(f'Object {object_id} has moved {round((average_dist[0]+average_dist[1])/2,3)} in the last cycle')

        # - saving true value of average movement
        current_movment = (average_dist[0]+average_dist[1])/2

        # - extract average past movment from object_list with empty list safety
        if len(object_list) == 0 or len(object_list[object_id]) == 0:
            past_movment = 0.0
        else
            past_movment = sum(object_list[object_id]) / len(object_list[object_id])

        # - adding current movement
        object_list[object_id].append(current_movment)

        # - informing the user
        self.get_logger().info(f'Object {object_id} has an average past movement of {past_movment}')

        # - returning false if there are less than 3 scans
        if len(object_list[object_id] < 3):
            self.get_logger().info(f"Less than 3 scans for onbject {object_id}")
            return false

        # - if current > 1.5*past movment, then I think it is moving
        if (current_movment > 1.5 * past_movment):
            self.get_logger().info(f"Object {object_id} has moved!")
            return true
        else:
            return false

# - main
def main(args=None):
    rclpy.init(args=args)
    movement_follower_node = MovementFollowerNode()

    # - publishing intital pose
    movement_follower_node.publish_inital_pose(-0.1110, 0.021468)

    # - spin
    rclpy.spin(movement_follower_node)

# - entry point
if __name__ == '__main__':
    main()