# Micromouse
Python implementation of micromouse maze solving algorithms for use with [mackarone's mms applet](https://github.com/mackorone/mms)

### API.py
Contains mackorone's mms API so that my program can interface with their applet

### location.py
Contains a class, "Location" which contains all data to track a specific square in the maze (coordinates, which walls it has, if it has been visited), along with some helpful methods (like checking if movement is possible between it and another location object)

### main.py
Contains the main program which utilizes a recursive depth first search algorithm to map an mms maze. So far it can solve all of mackorone's mazes (though perhaps not as quickly as I'd like) and will stop once the entire searchable portion of the maze has been visited
**Note: this does use global variables for simplifying various function calls from requiring additional positional arguments**
