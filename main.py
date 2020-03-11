import time
from typing import List, Tuple

import API
import sys
import location
from queue import LifoQueue

MAZE_WIDTH = 16
MAZE_HEIGHT = 16

# for tracking global direction
# 0 = North
# 1 = East
# 2 = South
# 3 = West
cur_direction = 0

# for tracking global position in maze as [x, y], initialized to [0, 0]
cur_position = [0, 0]

# for tracking all maze data, create 2d array of Locations
maze = [[location.Location([i, j]) for j in range(0, MAZE_WIDTH)] for i in range(0, MAZE_HEIGHT)]

# location object stack for tracking locations that may need to be explored
loc_stack = LifoQueue()

# direction stack for easy backtracking through maze when a dead end is found
dir_stack = LifoQueue()


# update position (-1 is move backward, 1 is move forward), currently only ever moves forward
def update_position(move_direction=1):
    global cur_position
    if cur_direction == 0:    # facing north
        cur_position[1] = cur_position[1] + move_direction
    elif cur_direction == 1:  # facing east
        cur_position[0] = cur_position[0] + move_direction
    elif cur_direction == 2:  # facing south
        cur_position[1] = cur_position[1] - move_direction
    elif cur_direction == 3:  # facing west
        cur_position[0] = cur_position[0] - move_direction


# update direction (-1 is left, 1 is right)
def update_direction(turn_direction):
    global cur_direction  # we are modifying global current direction
    cur_direction = (cur_direction + turn_direction) % 4


# given a list of bools representing walls, return string representing state (for debugging)
# example:
#   INPUT: bool_list = [True, False, True, False] means walls to the north and south but not east or west
#   OUTPUT: "YNYN" encodes the same data in string form
# def wall_bools_to_string(bool_list):
#     my_string = ""
#     for i in range(0, 4):  # for iterating through all four walls
#         if bool_list[i]:  # if wall at position i is True set char to 'W' for wall
#             my_string = my_string + 'Y'
#         else:  # else set to 'N' for no wall
#             my_string = my_string + 'N'
#     return my_string


# returns list of walls around current state
# example:
#   OUTPUT: [False, True, False, True] means walls to the north and south but not east or west
def get_walls():
    walls = [False, False, False, False]
    walls[cur_direction] = API.wallFront()  # is there a wall in front
    walls[(cur_direction + 1) % 4] = API.wallRight()  # is there a wall to the right
    walls[(cur_direction + 2) % 4] = False  # no wall from direction we came from
    walls[(cur_direction + 3) % 4] = API.wallLeft()  # is there a wall to the left
    if cur_position == [0, 0]:  # if first square, mark bottom wall as there
        walls[2] = True
    return walls


# marks a given node that it has been visited (usually takes cur_position)
def mark_visited_api(pos=cur_position):
    API.setColor(pos[0], pos[1], "G")
    API.setText(pos[0], pos[1], "hit")  # drop string containing info on square

# for printing to mms console
def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()


# take all actions to move forward and update belief state
def move_forward():
    API.moveForward()  # move forward in maze
    update_position(+1)  # update current position


# take all actions to turn left and update belief state
def turn_left():
    API.turnLeft()
    update_direction(-1)  # we are turning left


# take all actions to turn right and update belief state
def turn_right():
    API.turnRight()
    update_direction(+1)  # we are turning right

# take all actions to turn around
def turn_around():
    turn_right()
    turn_right()

# change direction to specific direction
def set_dir(_dir):
    if _dir == cur_direction:  # if already facing correct direction
        return
    if _dir == (cur_direction + 1) % 4:  # if need to turn right once
        turn_right()
        return
    if _dir == (cur_direction + 2) % 4:  # if need to turn around
        turn_right()
        turn_right()
        return
    turn_left()  # if need to turn left once
    return


# turn toward an adjacent location object
def turn_toward(loc):
    _dir = cur_direction
    # find direction of adjacent location
    if cur_position[0] == loc.position[0]:  # if two locations have the same x coordinate
        if cur_position[1] - loc.position[1] == 1:  # if i am above next location, turn south
            _dir = 2
        else:  # otherwise i must be below next location
            _dir = 0
    else:  # two directions have the same y coordinate
        if cur_position[0] - loc.position[0] == 1:  # if i am to the right of location, turn west
            _dir = 3
        else:  # i must be to the left of the location
            _dir = 1
    set_dir(_dir)


# maps maze in depth first search using loc_stack, takes dir = 0, 1, 2, or 3 for N, E, S, W
def dfs_map_maze():
    cur_loc = maze[cur_position[0]][cur_position[1]]  # create new ref to current location object for easier reference

    if not cur_loc.visited:  # if current location has not been visited
        cur_loc.set_visited(True)  # mark location as visited
        cur_loc.set_walls(get_walls())  # set wall locations
        mark_visited_api(cur_position)  # mark current position in API

        # if i have no north wall and north location is not visited, put it on loc_stack to explore later
        if not cur_loc.walls[0] and not maze[cur_position[0]][cur_position[1] + 1].visited:
            loc_stack.put(maze[cur_position[0]][cur_position[1] + 1])

        # if i have no east wall and east location is not visited, put it on loc_stack to explore later
        if not cur_loc.walls[1] and not maze[cur_position[0] + 1][cur_position[1]].visited:
            loc_stack.put(maze[cur_position[0] + 1][cur_position[1]])

        # if i have no south wall and south location is not visited, put it on loc_stack to explore later
        if not cur_loc.walls[2] and not maze[cur_position[0]][cur_position[1] - 1].visited:
            loc_stack.put(maze[cur_position[0]][cur_position[1] - 1])

        # if i have no west wall and west location is not visited, put it on loc_stack to explore later
        if not cur_loc.walls[3] and not maze[cur_position[0] - 1][cur_position[1]].visited:
            loc_stack.put(maze[cur_position[0] - 1][cur_position[1]])

    while True:  # do while loop to get next available position if it exists and has not been visited already
        if loc_stack.empty():  # if loc_stack is empty, return
            return
        next_loc = loc_stack.get()  # take the first location off of the loc_stack
        if not next_loc.visited:
            break

    # if I can move to that location from where I am, save current direction, turn toward new location, and move forward
    if cur_loc.can_move_to(next_loc):
        dir_stack.put(cur_direction)  # save current direction for backtracking
        turn_toward(next_loc)
        move_forward()
    # otherwise, put it back on the loc_stack, move backward, restore my direction from when I was last there
    else:
        loc_stack.put(next_loc)
        turn_around()
        move_forward()
        set_dir(dir_stack.get())    # restore last direction when at this location
    dfs_map_maze()  # try to move again

def main():
    log("Running...")
    dfs_map_maze()  # start facing north at initial position
    log("Done!")


if __name__ == "__main__":
    main()
