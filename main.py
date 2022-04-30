import pygame
import ctypes
import os, sys

getscreensize = ctypes.windll.user32.GetSystemMetrics


class Window:

    def __init__(self): 
        self.center = lambda self, p0, p1: (p1[0] // 2 - p0[0] // 2, p1[1] // 2 - p0[1] // 2)
        self.screen_width, self.screen_height = getscreensize(0), getscreensize(1)
        self.win_width, self.win_height = int(self.screen_width // 2.2), int(self.screen_height // 1.2)
        self.win = pygame.display.set_mode((self.win_width, self.win_height))
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.board_size = min(self.win_width, self.win_height) - 100
        self.light_grey = (89, 82, 72)
        self.grey = (135, 128, 130)
        self.green = (0, 244, 0)

    def run(self):
        pygame.display.set_caption("2048")
        self.board = Board(self.board_size, self)
        self.board_pos = (-1, -1)
        self.mouse_pos = (0, 0)
        self.dragging = False
        self.running = True
        while self.running:
            
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_pos = pygame.mouse.get_pos()
                    if self.in_bounding_box(self.mouse_pos, *self.board_pos, self.board_size, self.board_size):
                        result = self.board.process_click(*self.map_to_surface(self.board_pos, self.mouse_pos))
                        if result == "drag":
                            self.dragging = True

                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    self.board.tiles.update(event.rel)

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                    self.mouse_pos = pygame.mouse.get_pos()
                    for tile in self.board.tiles:
                        old_pos = tile.pos
                        new_pos = tile.adjust_pos(self.map_to_surface(self.board_pos, self.mouse_pos))
                        print(f"Moved tile from pos {old_pos} to {new_pos}")

            self.clock.tick(self.fps)
            self.update()
            pygame.display.update()

        pygame.quit()
        sys.exit(0)

    def update(self):
        x, y = self.center(self, (self.board_size, self.board_size), (self.win_width, self.win_height))
        y += 25
        self.board_pos = (x, y)
        self.board.fill(self.light_grey)
        self.board.draw_squares()
        self.board.tiles.draw(self.board)
        self.win.blit(self.board, (x, y))

    def in_bounding_box(self, mouse_pos, x, y, width, height):
        return mouse_pos[0] in range(x, x + width) and mouse_pos[1] in range(y, y + height)

    def map_to_surface(self, surface_pos, mouse_pos):
        return mouse_pos[0] - surface_pos[0], mouse_pos[1] - surface_pos[1]

    def get_direction(self, old, new):
        dx, dy = new[0] - old[0], new[1] - old[1]
        if abs(dx) > abs(dy):
            direction = "E" if dx > 0 else "W"
        else:
            direction = "S" if dy > 0 else "N"
        return direction


class Board(pygame.Surface):

    def __init__(self, size, parent):   
        super(Board, self).__init__((size, size))
        
        self.size = size
        self.parent = parent
        self.fill(self.parent.light_grey)
        self.border_size = int(self.size * 0.1) // 5
        self.square_size = int(self.size * 0.9) // 4
        self.tiles = pygame.sprite.Group(Tile(self.square_size, (0, 0), 64, self))
        self.squares = {}
        for i in range(4):
            for j in range(4):
                x, y = self.map_to_board(i, j)
                square = Square(self.square_size, (i, j), (x, y), self)
                square.fill(self.parent.grey)
                self.squares[(i, j)] = square
                self.blit(square, (x, y))

    def draw_squares(self):
        for i in range(4):
            for j in range(4):
                square = self.squares[(i, j)]
                self.blit(square, square.board_pos)

    def get_clicked_square(self, x, y):
        for i in range(4):
            for j in range(4):
                square = self.squares[(i, j)]
                if self.parent.in_bounding_box((x, y), *square.board_pos, square.size, square.size):
                    return (i, j)

    def move_tiles(self):
        pass

    def process_click(self, x, y):                    
        pos = self.get_clicked_square(x, y)
        if pos is None:
            return
        tile = None
        for t in self.tiles:
            if t.pos == pos:
                tile = t
                break
        if tile is None:
            return
        return "drag"

    def map_to_board(self, i, j):
        x = self.border_size if not i else i * self.square_size + (i + 1) * self.border_size
        y = self.border_size if not j else j * self.square_size + (j + 1) * self.border_size
        return x, y

        
class Square(pygame.Surface):

    def __init__(self, size, pos, board_pos, parent):
        super(Square, self).__init__((size, size))
        
        self.size = size
        self.pos = pos
        self.board_pos = board_pos
        self.parent = parent


class Tile(pygame.sprite.Sprite):
    
    def __init__(self, size, pos, num, parent, *args, **kwargs):
        super(Tile, self).__init__(*args, **kwargs)
        
        self.size = size
        self.pos = pos
        self.num = num
        self.parent = parent
        self.x, self.y = self.parent.map_to_board(*pos)
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def update(self, rel):
        self.rect.move_ip(rel)

    def adjust_pos(self, pos):
        for i in range(4):
            for j in range(4):
                square = self.parent.squares[(i, j)]
                if self.parent.parent.in_bounding_box(pos, *square.board_pos, square.size, square.size):
                    x, y = self.parent.parent.map_to_surface(self.parent.parent.board_pos, self.parent.map_to_board(i, j))
                    self.rect.move(x, y)
                    self.pos = (i, j)
                    return self.pos

    def __repr__(self):
        return f"Tile(pos={self.pos}, num={self.num})"


if __name__ == "__main__":
    window = Window()
    window.run()