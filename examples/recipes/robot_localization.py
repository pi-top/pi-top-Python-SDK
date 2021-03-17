from pitop import Pitop
from time import sleep

"""
Each marker is a paper cube placed on the floor like this:
   +--------+
  /        /|
 /        / |
+--------+  |
|        |  |
|        |  +
|        | /
|        |/
+--------+
Top and bottom faces are blank
Each of the 4 side faces has a unique aruco tag on it from the OpenCV "DICT_4X4_50" set. 
If looking down at the cube the tag IDs go in this order when cube "angle" is 0 in reference to world coordinate frame:

          tag n
         -------
        |       |
    n+3 |       | n+1
        |       |
         -------
           n+2
       
e.g. if I set the cube angle to be 90 degrees then looking down at in (within world coordinate frame) would look like:
(positive rotation is counter clockwise)
           n+1
         -------
        |       |
  tag n |       | n+2
        |       |
         -------
           n+3
       
"""
square_2x2 = {
    """
    2x2 meter grid of markers
    0 <-----2m------> 1
    ^                 ^
    |                 |
    2m                2m
    |                 |
    v                 v
    3 <-----2m------> 2
    
    """
    "marker_0": {
        "position": [0, 0, 0],  # [x, y, angle]
        "tag_ids": [0, 1, 2, 3]  # n=0
    },
    "marker_1": {
        "position": [2, 0, 0],
        "tag_ids": [4, 5, 6, 7]
    },
    "marker_2": {
        "position": [2, 2, 0],
        "tag_ids": [8, 9, 10, 11]
    },
    "marker_3": {
        "position": [0, 2, 0],
        "tag_ids": [12, 13, 14, 15]
    }
}


bobbie = Pitop.from_file("bobbie.json")
# map = bobbie.localization.map.from_file("square_2x2.json")  # optional
bobbie.localization.start(x_start=0, y_start=0, angle_start=0, map=square_2x2)  # optional start position and map

bobbie.drive.left(0.3, turn_radius=0.3)

angle = 0
while angle < 180:
    position = bobbie.localization.position
    x = position.x
    y = position.y
    angle = position.angle
    print(f'x: {x:.2f} | y: {y:.2f} | angle: {angle:.2f}')
    sleep(0.25)


# below method should fail if localization.start has not been called
bobbie.drive.to_position(x=0.25, y=0.1, angle=180)  # blocks until complete

position = bobbie.localization.position
x = position.x
y = position.y
angle = position.angle
print(f'x: {x:.2f} | y: {y:.2f} | angle: {angle:.2f}')
