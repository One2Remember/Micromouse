# class containing location: all data associated with a square
class Location:
    def __init__(self, pos=None):
        self.walls = [False, False, False, False]
        self.position = [-1, -1]
        self.visited = False
        if pos is not None:
            self.position[0] = pos[0]
            self.position[1] = pos[1]

    # takes position as ordered pair list [x,y]
    def set_position(self, pos):
        self.position[0] = pos[0]
        self.position[1] = pos[1]

    # takes walls as list of 4 booleans, eg: [True, False, True, False]
    def set_walls(self, walls):
        self.walls[0] = walls[0]
        self.walls[1] = walls[1]
        self.walls[2] = walls[2]
        self.walls[3] = walls[3]

    # takes boolean
    def set_visited(self, vis):
        self.visited = vis

    # two positions must be adjacent with no walls between
    def can_move_to(self, loc):
        # loc is north of self and self has no north wall OR
        # loc is to the east of self and self has no east wall OR
        # loc is to the south of self and self has no south wall OR
        # loc is to the west of self and self has no west wall OR
        return (loc.position[0] == self.position[0] and loc.position[1] - self.position[1] == +1 and not self.walls[0])\
            or (loc.position[1] == self.position[1] and loc.position[0] - self.position[0] == +1 and not self.walls[1])\
            or (loc.position[0] == self.position[0] and loc.position[1] - self.position[1] == -1 and not self.walls[2])\
            or (loc.position[1] == self.position[1] and loc.position[0] - self.position[0] == -1 and not self.walls[3])
