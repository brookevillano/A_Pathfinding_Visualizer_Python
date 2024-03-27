import pygame
import math
from queue import PriorityQueue

WIDTH = 800 
INSTRUCTION_PANEL_WIDTH = 200      
TOTAL_WIDTH = WIDTH + INSTRUCTION_PANEL_WIDTH
WIN = pygame.display.set_mode((TOTAL_WIDTH, WIDTH))           # setting up the display
pygame.display.set_caption("A* Pathfinding Algorithm") # display caption

RED = (255, 0, 0)               # already looked at node
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)         # not yet visited node
BLACK = (0, 0, 0)               # barrier node
PURPLE = (128, 0, 128)          # path node
ORANGE = (255, 165 ,0)          # start node
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)      # end node

class Node: 
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width     # to keep track of actual coordinate position on screen
        self.y = col * width     # to keep track of actual coordinate position on screen
        self.color = WHITE       # start with all white cubes
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows 

    def get_position(self): 
        return self.row, self.col 
    
    def is_closed(self):         # check to see if we already looked at this node
        return self.color == RED 

    def is_open(self):           # check to see if its in the open set
        return self.color == GREEN 
    
    def is_barrier(self):        # check to see if the node is a barrier
        return self.color == BLACK

    def is_start(self):          # check to see if it is the start node
        return self.color == ORANGE
    
    def reset(self):             # reset the node's color back to white
        self.color = WHITE

    def is_end(self):            # check to see if it is the end node
        return self.color == TURQUOISE

    def make_closed(self):       # change node to closed, so set color to red
        self.color = RED 
    
    def make_open(self):         # change node to open, so set color to green
        self.color = GREEN
    
    def make_barrier(self):      # change node to barrier, so set color to black
        self.color = BLACK

    def make_start(self):        # change node to start, so set color to orange
        self.color = ORANGE 

    def make_end(self):          # change node to end, so set color to turqouise
        self.color = TURQUOISE

    def make_path(self):         # change node to path, so set color to purple
        self.color = PURPLE 

    def draw(self, win): 
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.width))
    
    def update_neighbors(self, grid):  # to update and check node's neighbors
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # check if we can move DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # check if we can move UP 
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # check if we can move LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # check if we can move LEFT
            self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other): 
        return False

def wrap_text(text, font, max_width):
    """
    Splits the text into lines, ensuring each line does not exceed max_width.
    """
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        # Check width with one additional word
        test_line = current_line + [word]
        test_width = font.size(' '.join(test_line))[0]
        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))  # Add the last line
    return lines

def panel_instructions(win):
    font = pygame.font.SysFont('Arial', 20)
    instructions = [
        "Instructions:", 
        "Left Click to place start point/end point/barriers.", 
        "Right Click to clear cells.", 
        "SPACE to start the A* shortest path finding algorithm.", 
        "C to clear the entire screen."
    ]
    start_y = 20  # Starting Y position of the first line
    max_width = INSTRUCTION_PANEL_WIDTH - 20  # Max width for text
    bullet = "• "  # Define bullet point character
    spacing = 10  # Extra spacing between instructions for better readability

    for instruction in instructions:
        # Prepend bullet points to items, but not to the title
        if instruction != "Instructions:":
            instruction = bullet + instruction
        wrapped_lines = wrap_text(instruction, font, max_width)
        for line in wrapped_lines:
            text_surface = font.render(line, True, BLACK)
            win.blit(text_surface, (WIDTH + 10, start_y))
            start_y += font.get_height() + spacing  # Adjust for line height and extra spacing



def h(p1, p2): 
    # p1 = (#, #)
    x1, y1 = p1     
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw): 
    while current in came_from: 
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):  # my a path find algorithm 
    count = 0 
    open_set = PriorityQueue()          # lets us get the min element pretty fast --> O(1) time
    open_set.put((0, count, start))     # put start node in the open set
    came_from = {}                      # keeps track of where we came from
    g_score = {node: float("inf") for row in grid for node in row} # keeps track of current shortest distance from start node to this node
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row} # keeps track of predicted distance from this node til the end node
    f_score[start] = h(start.get_position(), end.get_position())   

    open_set_hash = {start} # keeps track of all the items that are in priority queue

    while not open_set.empty(): 
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit() 
        
        current = open_set.get()[2]     # gets min node in queue
        open_set_hash.remove(current)   # removes that node from the hash

        if current == end:              # make path
            reconstruct_path(came_from, end, draw)
            start.make_start()
            end.make_end()
            return True 

        for neighbor in current.neighbors:  
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]: # if we found a better g score (shorter distance), update 
                came_from[neighbor] = current    
                g_score[neighbor] = temp_g_score 
                f_score[neighbor] = temp_g_score + h(neighbor.get_position(), end.get_position())
                
                if neighbor not in open_set_hash: 
                    count += 1 
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()

        if current != start: 
            current.make_closed() 

    return False 

def make_grid(rows, width): 
    grid = []
    gap = width // rows # gives us the width of each of our nodes 

    for i in range(rows): 
        grid.append([])
        for j in range(rows): 
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    
    return grid 

def draw_grid(win, rows, width): # draws the grid lines
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width): 
    win.fill(WHITE)             # this fills the entire window with one color each frame 

    for row in grid:            # draws and colors in all of our nodes 
        for node in row: 
            node.draw(win) 
    
    draw_grid(win, rows, width) # then we draw the grid lines on top of the colors
    panel_instructions(win)      # draw the instructions
    pygame.display.update()     # updates the display with what we've drawn 


def get_clicked_position(pos, rows, width):  # gives us the position that we just clicked on 
    gap = width // rows 
    y, x = pos  

    row = y // gap 
    col = x // gap

    return row, col 

def main(win, width): 
    ROWS = 50 

    grid = make_grid(ROWS, width)

    start = None  # start position
    end   = None  # end position
 
    run     = True   # are we running the main loop 

    while run: 
        draw(win, grid, ROWS, width)
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:      # if x button is clicked, stop running app          
                run = False  

            if pygame.mouse.get_pressed()[0]:  # if we click ed left mouse button
                pos = pygame.mouse.get_pos()                   
                row, col = get_clicked_position(pos, ROWS, width)
                node = grid[row][col]

                if not start and node != end: 
                    start = node 
                    start.make_start()
                
                elif not end and node != start: 
                    end = node 
                    end.make_end()
                
                elif node != end and node != start: 
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # if we clicked right mouse button 
                pos = pygame.mouse.get_pos()                   
                row, col = get_clicked_position(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end: 
                    end = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end: 
                    for row in grid: 
                        for node in row: 
                            node.update_neighbors(grid)
                    
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
            
                if event.key == pygame.K_c:
                    start = None 
                    end = None 
                    grid = make_grid(ROWS, width)

    pygame.quit()

pygame.font.init()
main(WIN, WIDTH)