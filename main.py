import pygame
from random import randint
from sys import exit

class Minesweeper:
    def __init__(self, diffuculty):
        pygame.init()

        self.restart(diffuculty) 

    def restart(self, diffuculty):
        if diffuculty == "easy": 
            self.ROWS = 8
            self.COLS = 10
            self.WIDTH = 450
            self.HEIGHT = 360
            self.total_flags = 10
        elif diffuculty == "medium": 
            self.ROWS = 14
            self.COLS = 18
            self.WIDTH = 540
            self.HEIGHT = 420
            self.total_flags = 40
        elif diffuculty == "hard": 
            self.ROWS = 20
            self.COLS = 24
            self.WIDTH = 600
            self.HEIGHT = 500
            self.total_flags = 99

        self.cell_size = self.WIDTH / self.COLS 
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT + 50))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()

        self.image = pygame.image.load("spritesheet.png").convert_alpha()
        self.tiles = [self.get_frame(self.image, i, j, 100, 100, self.cell_size/100, (0, 0, 0)) for j in range(4) for i in range(8)]
        self.grid = [[Cell(False, x, y, self.cell_size, self.tiles[4 + randint(0, 3)]) for x in range(self.COLS)] for y in range(self.ROWS)]
        self.game_start = False
        self.old_mouse1 = False
        self.old_mouse2 = False
        self.game_state = "playing"
        self.explored_set = []
        self.frontier = []
        self.diffuculty = diffuculty
        self.enable_button = False

        self.font1 = pygame.font.Font(None, 50)

        self.pop_up_pos = ((self.WIDTH - 400) / 2, (self.HEIGHT - 300) / 2 + 50, 400, 300)

        self.score_label = self.font1.render("Your score:", True, (255, 255, 255))
        self.score_label_rect = self.score_label.get_rect(topleft = (50 + self.pop_up_pos[0],30 + self.pop_up_pos[1]))

        self.high_score_label = self.font1.render("High score:", True, (255, 255, 255))
        self.high_score_label_rect = self.score_label.get_rect(topleft = (50 + self.pop_up_pos[0], 120 + self.pop_up_pos[1]))
        self.high_score_count = self.font1.render("000", True, (255, 255, 255))
        self.high_score_count_rect = self.high_score_count.get_rect(center = (self.WIDTH//2, 180 + self.pop_up_pos[1]))

        self.retry_label = self.font1.render("Play again", True, (62, 95, 228))
        self.retry_label_rect = self.retry_label.get_rect(center = (self.WIDTH//2, 250 + self.pop_up_pos[1]))
        self.retry_button = pygame.Rect(self.WIDTH//2 - 100, 225 + self.pop_up_pos[1], 200, 50)

        self.UI1 = pygame.image.load("UI1.png").convert_alpha()
        self.UI1_rect = self.UI1.get_rect(topleft = (10, 10)) 

        self.flag_icon = pygame.image.load("flag.png").convert_alpha()
        self.flag_icon = pygame.transform.scale_by(self.flag_icon, 0.5)
        self.flag_icon_rect = self.flag_icon.get_rect(topleft = (175, 5)) 

        self.clock_icon = pygame.image.load("clock.png").convert_alpha()
        self.clock_icon_rect = self.clock_icon.get_rect(topleft = (300, 5))

        self.flags = self.total_flags
        self.timer = 0
        self.high_score = 0
        self.game_start_timestamp = pygame.time.get_ticks()

    def surround(self, pos):
        result = []
        x = pos[0]
        y = pos[1]
        bombs = 0
        for offsety in range(-1, 2):
            for offsetx in range(-1, 2):
                newx, newy = x + offsetx, y + offsety
                if 0 <= (newy) < self.ROWS and 0 <= (newx) < self.COLS:
                    if self.grid[newy][newx].bomb:
                        bombs += 1
                    elif (newx, newy) not in self.explored_set and (newx, newy) not in self.frontier:
                        result.append((newx, newy))
        return result, bombs

    def bfs(self, x, y):
        self.frontier = [(x, y)]
        if self.grid[self.frontier[0][1]][self.frontier[0][0]].bomb:self.game_state = "lost"
        self.grid[self.frontier[0][1]][self.frontier[0][0]].revealed = True
        
        while self.frontier:
            self.explored_set.append(self.frontier[0])
            neighbor_data = self.surround(self.frontier[0])
            if neighbor_data[1] == 0:
                self.frontier.extend(neighbor_data[0])
            self.grid[self.frontier[0][1]][self.frontier[0][0]].revealed = True
            self.grid[self.frontier[0][1]][self.frontier[0][0]].neighbor_bombs = neighbor_data[1]
            del self.frontier[0] 

    def place_bombs(self, num, clicked_cellx,  clicked_celly):
        bombs = 0
        neighbors = self.surround((clicked_cellx,  clicked_celly))[0]
        black_list = []
        for item in neighbors:
            black_list.append(self.grid[item[1]][item[0]])
        black_list.append(self.grid[clicked_celly][clicked_cellx])
        while bombs != num:
            bomb_cell = self.grid[randint(0, self.ROWS - 1)][randint(0, self.COLS - 1)]
            if not (bomb_cell.bomb or bomb_cell in black_list):
                bomb_cell.bomb = True
                bombs += 1

    def get_frame(self, sheet, x, y, width, height, scale, color):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(sheet, (0, 0), (width * x, height * y, width, height))
        image = pygame.transform.scale_by(image, scale)
        image.set_colorkey(color)
        return image

    def handle_event(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    def main(self):
        self.screen.fill((72, 160, 246))

        mouse = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        closed_cells = 0
        for row in self.grid:
            for cell in row:
                if not cell.revealed: closed_cells += 1
                if cell.rect.collidepoint(mouse_pos) and not cell.revealed and self.game_state == "playing":
                    if mouse[0] and not cell.flagged and not self.old_mouse1:
                        if not self.game_start:
                            self.place_bombs(self.total_flags, cell.x, cell.y)
                            self.game_start = True
                        self.bfs(cell.x, cell.y)
                    elif mouse[2] and not self.old_mouse2:
                        if cell.flagged:
                            cell.flagged = False
                            self.flags += 1
                        else:
                            cell.flagged = True
                            self.flags -= 1
                cell.draw(self.screen, self.game_state, self.tiles) 
        if closed_cells == self.total_flags:self.game_state = "won"

        if self.UI1_rect.collidepoint(mouse_pos) and self.game_state == "playing" and not mouse[0] and self.old_mouse1:
            if mouse_pos[0] > 10 + 60:self.restart("hard")
            elif mouse_pos[0] > 10 + 30:self.restart("medium")
            elif mouse_pos[0] > 10:self.restart("easy")
        if not self.game_state == "playing" and not self.enable_button and not mouse[0]: self.enable_button = True

        if not self.game_start: self.game_start_timestamp = pygame.time.get_ticks()
        if self.game_state == "playing": self.timer = int((pygame.time.get_ticks() - self.game_start_timestamp) // 1000)

        self.timer_label = self.font1.render(f"{self.timer:03}", True, (255, 255, 255))
        self.timer_label_rect = self.timer_label.get_rect(topleft = (350, 10))
        self.flag_count_label = self.font1.render(str(self.flags), True, (255, 255, 255))
        self.flag_count_label_rect = self.flag_count_label.get_rect(topleft = (225, 10))
        #UI blit
        self.screen.blit(self.UI1, self.UI1_rect)

        self.screen.blit(self.flag_icon, self.flag_icon_rect)
        self.screen.blit(self.flag_count_label, self.flag_count_label_rect)
        
        self.screen.blit(self.clock_icon, self.clock_icon_rect)
        self.screen.blit(self.timer_label, self.timer_label_rect)

        if not self.game_state == "playing":
            if self.high_score < self.timer and self.game_state == "won": self.high_score = self.timer
            
            self.score_count_rect = self.timer_label.get_rect(center = (self.WIDTH//2 , 90 + self.pop_up_pos[1]))
            self.high_score_count = self.font1.render(f"{self.high_score:03}", True, (255, 255, 255))

            #bliting
            pygame.draw.rect(self.screen, (62, 95, 228), self.pop_up_pos, border_radius=40)
            pygame.draw.rect(self.screen, (0, 0, 0), self.pop_up_pos, border_radius=40, width=2)
            self.screen.blit(self.score_label, self.score_label_rect)
            self.screen.blit(self.timer_label, self.score_count_rect)
            self.screen.blit(self.high_score_count, self.high_score_count_rect)
            self.screen.blit(self.high_score_label, self.high_score_label_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), self.retry_button, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), self.retry_button, border_radius=10, width=2)
            self.screen.blit(self.retry_label, self.retry_label_rect)

            if self.retry_button.collidepoint(mouse_pos) and mouse[0] and not self.old_mouse1 and self.enable_button:self.restart(self.diffuculty)

        self.old_mouse1 = mouse[0]
        self.old_mouse2 = mouse[2]
 
    def run(self):
        while True:
            self.handle_event()
            self.main()
            pygame.display.update()
            self.clock.tick(60)

class Cell:
    def __init__(self, bomb, x, y, cell_size, bomb_tile):
        self.revealed = False
        self.bomb = bomb
        self.bomb_tile = bomb_tile
        self.neighbor_bombs = 0
        self.flagged = False
        self.x, self.y = x, y
        self.rect = pygame.Rect(x * cell_size, y * cell_size + 50, cell_size, cell_size)

    def draw(self, screen, game_state, tiles):
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

game = Minesweeper("medium")
game.run()