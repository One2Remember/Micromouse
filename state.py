import location

# class containing state
class State:

    # loc is the physical location this state occupies taken as a list of [x, y] coordinates (ints)
    # parent is the adjacent state that generated this state (a State ref)
    # action is the action the parent took to reach this state, encoded as the 'turn' taken before moving forward
    #   turn can be 0 - no turn, 1 - turn right, 2 - turn around, 3 - turn left, or -1 if null action (see default)
    def __init__(self, loc, parent=None, action=None, cur_dir=None):
        self.location = loc
        if parent is None:
            self.parent = self
        else:
            self.parent = parent
        if action is None:
            self.action = -1
        else:
            self.action = action
        if cur_dir is None:
            self.cur_dir = 0
        else:
            self.cur_dir = cur_dir

    def set_loc(self, loc):
        self.location = loc

    def set_par(self, par):
        self.parent = par

    def set_act(self, act):
        self.action = act

    def set_cur_dir(self, cur_dir):
        self.cur_dir = cur_dir

    def is_goal(self):
        return self.location.position == [7, 7] or self.location.position == [7, 8] \
               or self.location.position == [8, 7] or self.location.position == [8, 8]

