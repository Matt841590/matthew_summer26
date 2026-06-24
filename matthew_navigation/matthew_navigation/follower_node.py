import rclpy
import math
import os
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
# - importing stuff so I can visualize points
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

class MovementFollowerNode(Node):
    def __init__(self):
        super().__init__("movement_follower_node")

        # - basic navigator to publish destination poses
        self.nav = BasicNavigator()

        # - tracking engine
        self.engine = TrackingEngine(
            cluster_eps_mm=100.0,       # Tighter grouping radius
            cluster_min_samples=6,      # Requires denser point clusters
            max_cluster_radius_mm=300.0 # Rejects tracking massive objects/walls
        )

        # - point publisher
        self.point_publisher = self.create_publisher(Marker, 'visualization_marker', 10)

        # - subscriber to /scan
        self.scan_subscriber = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_subscriber_callabck,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        self.scan_subscriber # - so it doesnt scream about unused variables

        # - holder for lidar values, first is the object id and second is the displacements it has been in the past
        self.object_list = []

    def publish_point(self,x,y):
        marker = Marker()

        marker.header.frame_id = "base_link"   # or "odom"
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = "points"
        marker.id = 0

        marker.type = Marker.SPHERE   # or CUBE, POINTS, etc.
        marker.action = Marker.ADD

        # your x,y point
        marker.pose.position.x = x / 1000
        marker.pose.position.y = y / 1000
        marker.pose.position.z = 0.0

        marker.pose.orientation.w = 1.0

        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2

        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0

        self.point_publisher.publish(marker)


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
        # - capture distances
        distances = np.array(msg.ranges)
        # - capture angles (in RADIANS from ROS)
        angles_rad = msg.angle_min + np.arange(len(distances)) * msg.angle_increment

        max_tracking_distance = 1.5  # Only look at things within 1.5 meters
        
        # - updated filtering criteria using your manual cutoff
        valid_mask = (distances > msg.range_min) & (distances < max_tracking_distance) & np.isfinite(distances)
        distances = distances[valid_mask]
        angles_rad = angles_rad[valid_mask]
        
        distances_mm = distances * 1000.0

        # 1. CONVERT RADIANS TO DEGREES
        angles_deg = np.degrees(angles_rad)

        # 2. Zip them together as (angle_deg, distance_mm)
        angle_dist_tuples = np.column_stack((angles_deg, distances_mm))

        if len(angle_dist_tuples) == 0:
            self.get_logger().warn("All points filtered out this frame!")
            return

        # 3. Pass to the tracking engine
        frame = self.engine.process_scan(angle_dist_tuples)
        

        # - printing what I found
        for obj in frame.objects:
            self.get_logger().info(f"Engine detected {len(frame.objects)} unique objects this frame.")
            while len(self.object_list) <= obj.object_id:
                self.object_list.append([])

            self.get_logger().info(f"Object {obj.object_id} now at ({round(obj.centroid.x,1)}, {round(obj.centroid.y)})mm")
            
            # The library outputs centroids in Cartesian mm, so dividing by 1000 here is still correct for RViz
            self.publish_point(obj.centroid.x, obj.centroid.y)
            
            del_x, del_y = self.compute_delta(frame, obj, self.object_list)
            self.get_logger().info(f"Object {obj.object_id} delta: ({round(del_x,1)}, {round(del_y,1)})mm")

        # os.system("clear")


        # - for object in frame
            # - while object is moving (is_moving returns true)
                # - follow object


    # - determines the average (x,y) of an object
    def calculate_average_position(self, points):
        average_x = 0.0
        average_y = 0.0
        num_points = 0
        for point in points:
            average_x += point[0]
            average_y += point[1]
            num_points +=1
        
        return (average_x/num_points, average_y/num_points)
        



    def compute_delta(self, frame, object, object_list):
        # - append current location (I know this is bad, dont care)
        object_list[object.object_id].append((object.centroid.x,object.centroid.y))

        # - compute average position based on previous timestamps in (x,y)
        hist_x, hist_y = self.calculate_average_position(object_list[object.object_id])
        #self.get_logger().info(f'object {object.object_id} was at ({round(hist_x,1)}, {round(hist_y,1)})')

        # - compute current position (in x,y)
        # - obj.centroid.x:.0f}, {obj.centroid.y:.0f (from above code)

        # - determine distance between historic and current position
        x_diff = hist_x - object.centroid.x
        y_diff = hist_y - object.centroid.y 
        #self.get_logger().info(f'object {object.object_id} delta: ({round(x_diff,1)}, {round(y_diff,1)})')
        distance = math.sqrt(x_diff**2 + y_diff**2)
        #self.get_logger().info(f'object {object.object_id} has moved ({round(distance,1)})')
        return (x_diff, y_diff)
        

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