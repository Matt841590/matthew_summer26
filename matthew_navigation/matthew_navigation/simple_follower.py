import rclpy
import math
import os
import numpy as np
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from nav_msgs.msg import Odometry
# - importing message type for initial pose and destinations
from geometry_msgs.msg import PoseStamped
# - simplecommander for publishing stuff without race conditions
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
# - importing stuff so I can visualize points
from visualization_msgs.msg import Marker, MarkerArray
from builtin_interfaces.msg import Duration
from geometry_msgs.msg import Point
# - importing DBScan to sort points into clusters
from sklearn.cluster import DBSCAN
from sensor_msgs.msg import LaserScan
# - tf stuff to chnage frames
import tf2_ros
from geometry_msgs.msg import TransformStamped
from geometry_msgs.msg import PoseStamped

class SimpleFollower(Node):
    def __init__(self):
        super().__init__("simple_follower")

        # - basic navigator to publish destination poses
        self.nav = BasicNavigator()

        # - point publisher
        self.point_publisher = self.create_publisher(MarkerArray, 'visualization_marker_array', 10)

        # - subscriber to /scan
        self.scan_subscriber = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_subscriber_callabck,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        # - subscriber to /odom
        self.odom_subscriber = self.create_subscription(
            Odometry,
            "/odom",
            self.odom_subscriber_callabck,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )  

        # - odometry related things
        self.new_odom = False
        self.no_wait = False
        self.robot_position = Odometry()

        # - dict to hold (x,y) values of objects that i know of
        self.object_holder = {}

        # - dict to hold previous known position
        self.previous_position_holder = {}

        # - dict to hold number of frames an object has been missed
        self.missed_frames = {}

        # - average displacement holder
        self.average_dispacment_holder = {}

        # - set of ID's that have had an object match to them
        self.matched_ids = set()

        # - holder to track if an object is moving
        self.is_moving_holder = {}

        # - distance something has to be inside of to be considered a match
        self.max_dist = 0.4

        # - tf stuff
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # - misc stuff
        self.first = True
        self.num_objects = 0


    def odom_subscriber_callabck(self, msg):
        # - populating robot_position
        self.robot_position.pose.pose.position.x = msg.pose.pose.position.x
        self.robot_position.pose.pose.position.y = msg.pose.pose.position.y
        self.robot_position.pose.pose.position.z = msg.pose.pose.position.z

        self.robot_position.pose.pose.orientation.x = msg.pose.pose.orientation.x
        self.robot_position.pose.pose.orientation.y = msg.pose.pose.orientation.y
        self.robot_position.pose.pose.orientation.z = msg.pose.pose.orientation.z
        self.robot_position.pose.pose.orientation.w = msg.pose.pose.orientation.w
        # - updating condition boolean
        self.new_odom = True
        self.no_wait = True


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

    # - publishes each centroid as a Marker in Rviz so I can see them :)
    def publish_centroid(self, object_holder):
        # marker = Marker()

        # marker.header.frame_id = "base_link"   # or "odom"
        # marker.header.stamp = self.get_clock().now().to_msg()

        # # Lifetime of 3 seconds
        # marker.lifetime = Duration(sec=5, nanosec=0)

        # marker.ns = "points"
        # marker.id = id

        # marker.type = Marker.SPHERE   # or CUBE, POINTS, etc.
        # marker.action = Marker.ADD

        # # your x,y point
        # marker.pose.position.x = -centroid[0]
        # marker.pose.position.y = centroid[1]
        # marker.pose.position.z = 0.0

        # marker.pose.orientation.w = 1.0

        # marker.scale.x = 0.2
        # marker.scale.y = 0.2
        # marker.scale.z = 0.2

        # marker.color.r = 1.0
        # marker.color.g = 0.0
        # marker.color.b = 0.0
        # marker.color.a = 1.0
        if not self.new_odom:
            if not self.no_wait:
                self.get_logger().info(f'/scan publisher is waiting on /odom data')
                self.no_wait = True
                return
            else:
                return

        # - text array to publish at the end
        text_array = MarkerArray()

        for key,centroid in object_holder.items():

            if key not in self.matched_ids:
                continue

            # Text marker
            text = Marker()
            text.header.frame_id = "map"
            text.ns = "object_labels"
            text.id = key
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD

            # Lifetime of 3 seconds
            text.lifetime = Duration(sec=5, nanosec=0)

            text.pose.position.x = -centroid[0] - self.robot_position.pose.pose.position.x
            text.pose.position.y = centroid[1] + self.robot_position.pose.pose.position.y
            text.pose.position.z = 0.3

            text.pose.orientation.x = self.robot_position.pose.pose.orientation.x
            text.pose.orientation.y = self.robot_position.pose.pose.orientation.y
            text.pose.orientation.z = self.robot_position.pose.pose.orientation.z
            text.pose.orientation.w = self.robot_position.pose.pose.orientation.w

            text.scale.z = 0.20  # text height in meters

            text.pose.orientation.w = 1.0

            # - compute distance to change color of things that are "moving"
            # x_comp = ((centroid[0] - self.previous_position_holder[key][0])**2)
            # y_comp = ((centroid[1] - self.previous_position_holder[key][1])**2)
            # distance = math.sqrt(x_comp + y_comp)

            # - if displacment big enough, change color
            if self.average_dispacment_holder[key] > 0.01:
                self.is_moving_holder[key] = True
                text.color.r = 0.0
                text.color.g = 1.0
                text.color.b = 0.0
                text.color.a = 1.0
            else:
                self.is_moving_holder[key] = False
                text.color.r = 0.0
                text.color.g = 0.0
                text.color.b = 1.0
                text.color.a = 1.0

            text.text = str(key)

            # - appending
            text_array.markers.append(text)

        #self.point_publisher.publish(marker)
        self.point_publisher.publish(text_array)
    
    # - subscriber to /scan callabck
    def scan_subscriber_callabck(self, msg):
        # - set of ID's that have been matched, used to prune old objects and prevent duplication
        self.matched_ids = set()

        # - capture the distances and angles
        distances = np.array(msg.ranges)
        angles_rad = msg.angle_min + np.arange(len(distances)) * msg.angle_increment

        # - filter out points that are too far
        max_tracking_distance = 0.75 
        valid_mask = (distances > msg.range_min) & (distances < max_tracking_distance) & np.isfinite(distances)
        
        distances = distances[valid_mask]
        angles_rad = angles_rad[valid_mask]

        # - checking that some points, in fact, got scanned
        if len(distances) == 0:
            self.get_logger().info('No valid point/angle pairs read at all!')
            return

        # - convert polar to cartesian
        x_m = distances * np.cos(angles_rad)
        y_m = distances * np.sin(angles_rad)
        points = np.column_stack((x_m, y_m))

        # - holder for map frame points
        map_points = np.empty((len(points), 2))

        # - stole this transform implementation
        for i in range(len(points)):
            pt = PoseStamped()
            pt.header.frame_id = "base_link"
            pt.header.stamp = self.get_clock().now().to_msg()

            pt.pose.position.x = float(points[i][0])
            pt.pose.position.y = float(points[i][1])
            pt.pose.position.z = 0.0

            pt.pose.orientation.w = 1.0

            map_pt = self.tf_buffer.transform(
                pt,
                "map",
                timeout=rclpy.duration.Duration(seconds=0.1)
            )

            map_points[i, 0] = map_pt.pose.position.x
            map_points[i, 1] = map_pt.pose.position.y

        # - use DBScan to sort them into objects
        #self.get_logger().info('Running DBScan on points')
        db = DBSCAN(eps=0.12, min_samples=5).fit(map_points)
        labels = db.labels_

        # - extract a centroid for each object
        current_centroids = []
        for label in set(labels):

            # - ignoring noise
            if label == -1:
                continue
            cluster = points[labels == label]
            current_centroids.append(cluster.mean(axis=0))

        # - compare centroids trying to find the closest one
        for centroid in current_centroids:
            # - first time, adding all of the centroids
            if self.first:
                self.object_holder[self.num_objects] = centroid
                self.missed_frames[self.num_objects] = 0
                self.previous_position_holder[self.num_objects] = centroid
                self.average_dispacment_holder[self.num_objects] = 0.0
                self.is_moving_holder[self.num_objects] = False
                self.num_objects += 1
                self.get_logger().info(f'New point (setup): point number {self.num_objects} at {centroid}')
                
            # - comparing previous centroids
            else:
                new_key = -1
                best_distance = 999999.99999

                # - determining min distance
                for key, value in self.object_holder.items():

                    if key in self.matched_ids:
                        continue

                    new_distance = math.sqrt((value[0]-centroid[0])**2 + (value[1]-centroid[1])**2)

                    if new_distance < best_distance:
                        best_distance = new_distance
                        new_key = key

                # - adding a new item
                if new_key == -1 or best_distance >= self.max_dist:
                    self.object_holder[self.num_objects] = centroid
                    self.missed_frames[self.num_objects] = 0
                    self.previous_position_holder[self.num_objects] = centroid
                    self.average_dispacment_holder[self.num_objects] = 0.0
                    self.is_moving_holder[self.num_objects] = False
                    self.get_logger().info(f'New point (runtime): point number {self.num_objects} at {centroid}')
                    self.num_objects += 1
                    self.matched_ids.add(new_key)
                
                # - updating an old item
                else:
                    self.previous_position_holder[new_key] = self.object_holder[new_key]
                    self.object_holder[new_key] = centroid
                    self.missed_frames[new_key] = 0
                    self.matched_ids.add(new_key)

                    # - computing the distance between the previous point and the current one
                    x_disp = self.object_holder[new_key][0] - self.previous_position_holder[new_key][0]
                    y_disp = self.object_holder[new_key][1] - self.previous_position_holder[new_key][1]
                    distance = math.sqrt(x_disp**2 + y_disp**2)

                    # - averaging with the previous displacment with an 80/20 preference to the old
                    self.average_dispacment_holder[new_key] = (0.8 * self.average_dispacment_holder[new_key] + 0.2 * distance)
                    #self.get_logger().info(f'Updated point: {new_key} with displacment {(self.average_dispacment_holder[new_key] + distance) / 2}')
                    #self.get_logger().info(f'Updated point: {new_key} at {centroid}')

        # - making sure it only goes through first time setup once
        self.first = False

        # - publishing visual points to represent the centroids
        # for i in range(len(self.object_holder)):
        #     self.get_logger().info(f'Publishing RViz marker for point {i} at {self.object_holder[i]}')
        #     self.publish_centroid(i, self.object_holder[i])
        self.publish_centroid(self.object_holder)

        # - determining the number of moving objects
        true_count = 0
        moving_object_index = -1
        for key in self.object_holder.keys():
            if self.is_moving_holder[key] == True:
                true_count += 1
                moving_object_index = key
        
        # - if only one thing is moving, follow it!
        if true_count == 1:
            self.get_logger().info(f'object {moving_object_index} is moving!')
            #self.publish_destination_pose(-self.object_holder[moving_object_index][0],self.object_holder[moving_object_index][1])

        # - else, freeze and print an error!
        elif true_count > 1:
            self.get_logger().info(f'too much movement!')


        # - TODO: set all objects in the map frame, not the base_link frame
        # - TODO: compensate for robot moving such that when it moves it doesnt think all of the objects are moving

        

    
# - main
def main(args=None):
    rclpy.init(args=args)
    simple_follower = SimpleFollower()

    # - publishing initial pose
    simple_follower.publish_inital_pose(-0.1110, 0.021468)

    # - spinning 
    rclpy.spin(simple_follower)

# - entry point
if __name__ == '__main__':
    main()