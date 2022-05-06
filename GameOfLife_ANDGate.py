import sys
import time #Allows for delay in the simulation's generations to make the simulation more easily watchable
from collections import defaultdict, namedtuple #Tuples are used to store information about the game such as size, alive cells and neighbour information
from copy import deepcopy #Allows for copying the grid tuple without reference; stops changes from affecting the current grid

import pygame #Used to display the graphics for the simulation

Dim = namedtuple("Dimension", ["width", "height"]) #Tuple to contain the game's dimensions in cell count
Grid = namedtuple("Grid", ["dim", "output", "false_a", "false_b", "cells"]) #Tuple for information about the game's grid
Neighbours = namedtuple("Neighbours", ["alive", "dead"]) #Tuple to store information about the states of each cell's neighbours

#Grid for the AND gate. Dimension is 150 cells in both sides, the signal's goal is cell 150/138, and the signal blockers for both inputs
AND_Gate = Grid(Dim(150, 150), (150, 138), (24,15), (74,14),

#Gosper Glider for the A Input, also main signal stream
                                {(22, 8), (12, 7), (36, 7), (17, 9), (11, 8), (1, 9), (25, 4), (2, 8), (16, 7),
                                (25, 10), (21, 6), (23, 9), (14, 6), (36, 6), (22, 7), (14, 12), (17, 8), (11, 10),
                                (25, 9), (35, 7), (1, 8), (18, 9), (22, 6), (21, 8), (23, 5), (12, 11), (17, 10),
                                (11, 9), (35, 6), (25, 5), (2, 9), (13, 6), (13, 12), (15, 9), (16, 11), (21, 7),
#Gosper Glider for the B Input, blocks the blocker stream if active
                                (72, 7), (62, 6), (86, 6), (67, 8), (61, 7), (51, 8), (75, 3), (52, 4), (66, 6),
                                (75, 9), (71, 5), (73, 8), (64, 5), (86, 5), (72, 6), (64, 11), (67, 7), (61, 9),
                                (75, 8), (85, 6), (51, 7), (68, 8), (72, 5), (71, 7), (73, 4), (62, 10), (67, 9),
                                (61, 8), (85, 5), (75, 4), (52, 8), (63, 5), (63, 11), (65, 8), (66, 10), (71, 6),
#Gosper Glider for the blocker stream. Will block A signal is B signal is not true
                                (108, 7), (118, 6), (94, 6), (113, 8), (119, 7), (129, 8), (105, 3), (128, 4), (114, 6),
                                (105, 9), (109, 5), (107, 8), (116, 5), (94, 5), (108, 6), (116, 11), (113, 7), (119, 9),
                                (105, 8), (95, 6), (129, 7), (112, 8), (108, 5), (109, 7), (107, 4), (118, 10), (113, 9),
                                (119, 8), (95, 5), (105, 4), (128, 8), (117, 5), (117, 11), (115, 8), (114, 10), (109, 6),
#Eater structures to block inputs if set to false, and dissolve if inputs are set to true
                                (24, 14), (25, 14), (25, 16), (26, 16), (27,16), (27,17), #Cell (24, 15) is appended if input is false
                                (74, 13), (75, 13), (75, 15), (76, 15), (77, 15), (77, 16)})  #Cell (74, 14) is appended if input is false

#Adds final cell for Input A's eater if set to false
def set_input_a_false(grid: Grid) -> Grid:
    new_grid = deepcopy(grid.cells) #Copies the grid's list of generation 1 cells
    new_grid.add(deepcopy(grid.false_a)) #and adds the final blocker cell to the starting configuration
    return Grid(grid.dim, grid.output, grid.false_a, grid.false_b, new_grid)

#Adds final cell for Input B's eater if set to false
def set_input_b_false(grid: Grid) -> Grid:
    new_grid = deepcopy(grid.cells) #Copies the grid's list of generation 1 cells
    new_grid.add(deepcopy(grid.false_b)) #and adds the final blocker cell to the starting configuration
    return Grid(grid.dim, grid.output, grid.false_a, grid.false_b, new_grid)

#Gets all the possible neighbouring cells, used when checking each cell's status for each generation
def get_neighbours(grid: Grid, x: int, y: int) -> Neighbours:
    offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), #Each offset represents a possible neighbour's position relative to the current cell's co-ordinates
               (1, 0), (-1, 1), (0, 1), (1, 1)]
    possible_neighbours = {(x + x_add, y + y_add) for x_add, y_add in offsets} #Adds the offsets to the original cell's co-ordinates to get the co-ords for the neighbours
    alive = {(pos[0], pos[1])
             for pos in possible_neighbours if pos in grid.cells} #Checks if each neighbour is alive
    return Neighbours(alive, possible_neighbours - alive) #Returns the total amount of alive neighbours

#This function handles each new iteration of the simulation, including killing and birthing new cells
def iterate_grid(grid: Grid) -> Grid:
    new_cells = deepcopy(grid.cells) #Copies the entire grid's cells. This allows the list of cells to be modified as tuples cannot be directly modified, only appended or replaced.
    death_freq = defaultdict(int) #Dictionary of the frequency of alive cells neighbouring dead cells, used to determine which dead cells should become alive again

    for (x, y) in grid.cells:
        alive_neighbours, dead_neighbours = get_neighbours(grid, x, y)
        if len(alive_neighbours) not in [2, 3]: #If the number of alive neighbours is not 2 or 3, the cell dies
            new_cells.remove((x, y))

        for pos in dead_neighbours: #Adds the cell's number of dead neighbours to the directory.
            death_freq[pos] += 1

    for pos, _ in filter(lambda elem: elem[1] == 3, death_freq.items()): #If an dead cell has exactly 3 neighbours, it becomes alive.
        new_cells.add((pos[0], pos[1]))

    return Grid(grid.dim, grid.output, grid.false_a, grid.false_b, new_cells) #Replaces the old grid with the new grid of cells


def draw_grid(screen: pygame.Surface, grid: Grid) -> None: #Graphically draws what happens each iteration
    cell_width = screen.get_width() / grid.dim.width
    cell_height = screen.get_height() / grid.dim.height #Determines how big each cell should be depending on the size of the window and the grid

    for (x, y) in grid.cells:
        pygame.draw.rect(screen, (255, 255, 255), (x * cell_width, y * cell_height, cell_width, cell_height)) #Draws white cells proportional to the screen's size and cell's location

#Main loop. User inputs their variables and the game begins looping until an outcome is reached
def main():
    grid = AND_Gate #Sets which gate is being used. For this program, there is only the AND gate programmed in
    input_a = (input("Is Input A True or False? "))
    input_b = (input("Is Input B True or False? ")) #User sets whether the inputs should be true or false in the command prompt
    if input_a == ("False") or input_a == ("false"):
        grid = set_input_a_false(grid)
    if input_b == ("False") or input_b == ("false"): #If an input is to be false, it sets up the eater that blocks the input's signal to turn it off
        grid = set_input_b_false(grid)
    fast_flag = (input("Do you wish to speed up the simulation? Yes or No. ")) #Lets the user choose if they want to more clearly watch the simulation

    pygame.init()
    screen = pygame.display.set_mode((600, 400)) #Sets the resolution of the window

    counter = 0 #counter to check how many times the simulation has iterated; after enough loops have passed without a true output, it concludes the signal is blocked and thus is false
    output = 0 #used to check if a true output has been reached to end the simulation early
    while counter < 600 and output == 0: #while a true output has not been reached, but it's too early to conclude as false
        if pygame.QUIT in [e.type for e in pygame.event.get()]:
            sys.exit(0)

        screen.fill((0, 0, 0))
        draw_grid(screen, grid) #draws the current status of the grid. This updates each cycle to animate the simulation
        grid = iterate_grid(grid) #performs the game's life and death logic on the cells to update the grid
        pygame.display.flip()
        if grid.output in grid.cells: #the simulation instantly ends after a true statement
            output = 1
            print("The output is True!")
        counter += 1
        if counter == 600: #after 600 generations without a true output, the game is over. This can be modified for other gates that need more or less time
            print("The output is False!")
        if fast_flag == ("No") or fast_flag == ("no") or fast_flag == ("n"):
            time.sleep(0.05) #sets a short delay between each iteration, otherwise the simulation moves too fast to observe closely
    time.sleep(4) #pauses the window for a few seconds so the user can see the final state before closing
    pygame.quit

if __name__ == "__main__":
    main()
