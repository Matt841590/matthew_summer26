# - all this was taken directly from https://github.com/gabe-ochoa/lidar-tracking

from lidar_tracker import TrackingEngine

engine = TrackingEngine()

# Feed scans as (angle_deg, distance_mm) tuples
frame = engine.process_scan([(0, ), ...])

for obj in frame.objects:
    print(f"Object #{obj.object_id} at ({obj.centroid.x:.0f}, {obj.centroid.y:.0f})mm")

# Get trajectory for a specific object
trail = engine.get_trajectory(obj.object_id)