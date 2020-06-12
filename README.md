# Micromouse
Python implementation of [micromouse](https://en.wikipedia.org/wiki/Micromouse) maze solving algorithms for use with [mackarone's mms applet](https://github.com/mackorone/mms). Soon, this will be used as the base for software which will live onboard an autonomous micromouse for use in IEEE's Region 6 Central Area Micromouse Competition which was going to be hosted at CSU East Bay Spring 2020, but has been indefinitely postponed due to Covid-19. Currently, the code is fully functional with mackarone's applet and can map, solve, and run every maze efficiently

## Demonstration
[YouTube demonstration of my source in action can be found here!](https://youtu.be/6y4nrnfZ1k0)

## Source Description

### API.py
Contains mackorone's mms API so that my program can interface with their applet

### location.py
Contains a class, "Location" which contains all data to track a specific square in the maze (coordinates, which walls it has, if it has been visited), along with some helpful methods (like checking if movement is possible between it and another location object)

### state.py
Contains a class, "State" which contains all data to track a virtual state for calculating the fastest path through the maze. The state consists of a location object, the parent object which generated it, and the action the parent took to generate the child. Main performs a breadth first search in the state space to find the solution state, then uses that solution state to execute an optimal solution to the micromouse maze solving problem

### main.py
Contains the main program which utilizes a recursive depth first search algorithm to map an mms maze. So far it can solve all of mackorone's mazes (though perhaps not as quickly as I'd like), and once the entire searchable portion of the maze has been visited and the mouse has returned to the home position, it will use a breadth first search to find the fastest route then execute that solution  

**Note: this does use global variables for simplifying various function calls from requiring additional positional arguments**
