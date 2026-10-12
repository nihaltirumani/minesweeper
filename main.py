import pygame
from random import randint
from sys import exit

def surround(pos):
    result = []
    x = pos[0]
    y = pos[1]
    bombs = 0
    for offsety in range(-1, 2):
            for offsetx in range(-1, 2):
                newx, newy = x + offsetx, y + offsety
                if 0 <= (newy) < COLS and 0 <= (newx) < ROWS:
                    if grid[newy][newx].bomb:
                        bombs += 1
                    elif [newx, newy] not in explored_set and [newx, newy] not in frontier:
                        result.append([newx, newy])
    return result, bombs

def bfs(x, y):
    global frontier, explored_set, game_state
    frontier = [[x,y]]
    explored_set = []
    if grid[frontier[0][1]][frontier[0][0]].bomb:
        game_state = "lost"
    grid[frontier[0][1]][frontier[0][0]].revealed = True
    
    while frontier:
        explored_set.append(frontier[0])
        neighbor_data = surround(frontier[0])
        if neighbor_data[1] == 0:
            frontier.extend(neighbor_data[0])
        grid[frontier[0][1]][frontier[0][0]].revealed = True
        grid[frontier[0][1]][frontier[0][0]].neighbor_bombs = neighbor_data[1]
        del frontier[0] 

def place_bombs(num, clicked_cell):
    bombs = 0
    neighbors = surround(clicked_cell)[0]
    black_list = []
    for item in neighbors:
        black_list.append(grid[item[1]][item[0]])
    black_list.append(grid[clicked_cell[1]][clicked_cell[0]])
    while bombs != num:
        bomb_cell = grid[randint(0, COLS - 1)][randint(0, ROWS - 1)]
        if not (bomb_cell.bomb or bomb_cell in black_list):
            bomb_cell.bomb = True
            bombs += 1

class Cell:
    def __init__(self, bomb, x, y, cell_size):
        self.revealed = False
        self.bomb = bomb
        self.bomb_tile = tiles[4 + randint(0, 3)]
        self.neighbor_bombs = 0
        self.flagged = False
        self.x, self.y = x, y
        self.rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)

    def draw(self, screen):
        if self.revealed:
            if self.neighbor_bombs == 0:
                tile = tiles[(self.x + self.y) % 2]
            else:
                tile = tiles[(self.x + self.y) % 2 * 8 + (7 + self.neighbor_bombs)]
        else:
            if self.flagged:
                tile = tiles[24 + (self.x + self.y) % 2]
            else:
                tile = tiles[2 + (self.x + self.y) % 2]
        if self.bomb and game_state == "lost":
            tile = self.bomb_tile
        screen.blit(tile, self.rect)

def get_frame(sheet, x, y, width, height, scale, color):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), (width * x, height * y, width, height))
    image = pygame.transform.scale_by(image, scale)
    image.set_colorkey(color)

    return image

pygame.init()

screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Minesweeper")
clock = pygame.time.Clock()
cell_size = 50
ROWS = 10
COLS = 8
game_start = False
old_mouse = False
game_state = "playing"

explored_set = []
frontier = []

image = pygame.image.load("spritesheet.png").convert_alpha()
tiles = [get_frame(image, i, j, 100, 100, 0.5, "black") for j in range(4) for i in range(8)]

grid = [[Cell(False, x, y, cell_size) for x in range(ROWS)] for y in range(COLS)]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill('black')

    mouse = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    closed_cells = 0
    for row in grid:
        for cell in row:
            if not cell.revealed: closed_cells += 1
            if cell.rect.collidepoint(mouse_pos) and not cell.revealed:
                if mouse[0] and not cell.flagged and not old_mouse:
                    if not game_start:
                        place_bombs(10, [cell.x , cell.y])
                        game_start = True
                    bfs(cell.x, cell.y)
                elif mouse[2] and not old_mouse:
                    if cell.flagged: cell.flagged = False
                    else: cell.flagged = True
            cell.draw(screen)
    if closed_cells == 10: game_state = "won"
    old_mouse = mouse[0] or mouse[2]

    pygame.display.update()
    clock.tick(60)