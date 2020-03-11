import sys
from queue import LifoQueue, Queue
import API
import location
import state

MAZE_WIDTH = 16
MAZE_HEIGHT = 16

# for tracking global direction
# 0 = North
# 1 = East
# 2 = South
# 3 = West
cur_direction = 0

# for tracking global 'physical' position in maze as [x, y], initialized to [0, 0]
cur_position = [0, 0]

# for tracking 'virtual' position when

# for tracking all maze data, create 2d array of Locations
maze = [[location.Location([i, j]) for j in range(0, MAZE_WIDTH)] for i in range(0, MAZE_HEIGHT)]

# location object stack for tracking locations that may need to be explored during mapping
loc_stack = LifoQueue()

# direction stack for easy backtracking through maze when a dead end is found during mapping
dir_stack = LifoQueue()

# action stack for processing optimal sequence of actions to find goal state
act_stack = LifoQueue()

# state object stack for unexplored nodes during breadth first search
frontier = Queue()


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


# marks a given node that it has been visited (usually takes cur_position, but can take any position)
def mark_visited_api(pos=None):
    if pos is None:
        pos = cur_position
    API.setColor(pos[0], pos[1], "G")
    API.setText(pos[0], pos[1], "hit")  # drop string containing info on square


# marks a given node that it is part of the solution path (usually takes cur_position)
def mark_solution_api(pos=None):
    if pos is None:
        pos = cur_position
    API.setColor(pos[0], pos[1], "B")
    API.setText(pos[0], pos[1], "Sol")

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


# maps maze in depth first search using loc_stack
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
        if loc_stack.empty():  # if loc_stack is empty, backtrack to initial position then return
            if not cur_position == [0, 0]:
                set_dir((dir_stack.get() + 2) % 4)  # turn around
                move_forward()
                dfs_map_maze()  # try to move again
            return
        next_loc = loc_stack.get()  # otherwise, take locations off of the loc_stack until we get an unvisited one
        if not next_loc.visited:
            break

    # if I can move to that location from where I am, turn toward new location, save that direction, and move forward
    if cur_loc.can_move_to(next_loc):
        turn_toward(next_loc)
        dir_stack.put(cur_direction)  # save current direction for backtracking on the direction stack
        move_forward()
    else:   # put the target location back on the loc_stack, back up one square, then try again
        loc_stack.put(next_loc)
        set_dir((dir_stack.get() + 2) % 4)  # turn toward last position
        move_forward()
    dfs_map_maze()  # try to move again


# defines breadth-first-search for finding optimal route to maze center
def find_bfs_shortest_path():
    # initialize all locations to unvisited
    for i in range(0, MAZE_HEIGHT):
        for j in range(0, MAZE_WIDTH):
            maze[i][j].visited = False;
    first_state = state.State(maze[0][0])  # generate initial state: parent is self, action is null
    frontier.put(first_state)   # push first state to queue
    # while queue is not empty
    while not frontier.empty():
        next_state = frontier.get()  # dequeue next state
        # mark state location as visited
        maze[next_state.location.position[0]][next_state.location.position[1]].set_visited(True)
        if next_state.is_goal():  # if it is goal
            return next_state    # return it
        # provide new references to my location and possible adjacent locations for easier reference in code below
        my_loc = next_state.location
        if not my_loc.walls[0]:
            north_loc = maze[my_loc.position[0]][my_loc.position[1] + 1]
        if not my_loc.walls[1]:
            east_loc  = maze[my_loc.position[0] + 1][my_loc.position[1]]
        if not my_loc.walls[2]:
            south_loc = maze[my_loc.position[0]][my_loc.position[1] - 1]
        if not my_loc.walls[3]:
            west_loc  = maze[my_loc.position[0] - 1][my_loc.position[1]]

        # if the position north has not been visited and I can reach it, generate a new state representing the new
        # location, with this location as its parent, and and the proper number of turns needed to reach it
        if not my_loc.walls[0] and my_loc.can_move_to(north_loc) and not north_loc.visited:
            # create a new state where i move from my_location to the north
            north_state = state.State(north_loc, next_state, (0 - next_state.cur_dir) % 4, 0)
            frontier.put(north_state)  # add it to the frontier queue

        # if the position east has not been visited and I can reach it, generate a new state representing the new
        # location, with this location as its parent, and and the proper number of turns needed to reach it
        if not my_loc.walls[1] and my_loc.can_move_to(east_loc) and not east_loc.visited:
            # create a new state where i move from my_location east
            east_state = state.State(east_loc, next_state, (1 - next_state.cur_dir) % 4, 1)
            frontier.put(east_state)  # add it to the frontier queue

        # if the position south has not been visited and I can reach it, generate a new state representing the new
        # location, with this location as its parent, and and the proper number of turns needed to reach it
        if not my_loc.walls[2] and my_loc.can_move_to(south_loc) and not south_loc.visited:
            # create a new state where i move from my_location south
            south_state = state.State(south_loc, next_state, (2 - next_state.cur_dir) % 4, 2)
            frontier.put(south_state)  # add it to the frontier queue

        # if the position west has not been visited and I can reach it, generate a new state representing the new
        # location, with this location as its parent, and and the proper number of turns needed to reach it
        if not my_loc.walls[3] and my_loc.can_move_to(west_loc) and not west_loc.visited:
            # create a new state where i move from my_location west
            west_state = state.State(west_loc, next_state, (3 - next_state.cur_dir) % 4, 3)
            frontier.put(west_state)  # add it to the frontier queue

# takes a solution state and uses it to physically traverse the maze - this constitutes the fastest possible run
def execute_shortest_path(sol):
    while sol.parent is not sol:    # while i have not reached the home position
        act_stack.put(sol.action)   # push action to stack
        sol = sol.parent    # traverse up to parent
    while not act_stack.empty():    # pop off actions from the stack and execute them in the maze
        act = act_stack.get()
        mark_solution_api()  # mark my square as part of the solution on the maze
        if act is 1:
            turn_right()
        elif act is 3:
            turn_left()
        move_forward()


def main():
    log("Running...")
    dfs_map_maze()  # start and end facing north at initial position after maze has been mapped
    solution = find_bfs_shortest_path()  # find the shortest path to solution using breadth first search
    execute_shortest_path(solution)   # execute the shortest path solution once found
    log("Done!")


if __name__ == "__main__":
    main()
