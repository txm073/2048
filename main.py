import pygame
import ctypes
import os, sys
import random

getscreensize = ctypes.windll.user32.GetSystemMetrics
vector_add = lambda vec1, vec2: (vec1[0] + vec2[0], vec1[1] + vec2[1])
vector_sub = lambda vec1, vec2: (vec1[0] - vec2[0], vec1[1] - vec2[1])

def _gen(): 
    i = 0
    while True:
        yield i
        i += 1

gen = _gen()


class Window:

    def __init__(self): 
        self.center = lambda self, p0, p1: (p1[0] // 2 - p0[0] // 2, p1[1] // 2 - p0[1] // 2)
        self.screen_width, self.screen_height = getscreensize(0), getscreensize(1)
        self.win_width, self.win_height = int(self.screen_width // 2.2), int(self.screen_height // 1.2)
        self.win = pygame.display.set_mode((self.win_width, self.win_height))
        self.clock = pygame.time.Clock()
        self.fps = 120
        self.board_size = min(self.win_width, self.win_height) - 100
        self.light_grey = (89, 82, 72)
        self.grey = (135, 128, 130)
        self.green = (0, 244, 0)

    def run(self):
        pygame.display.set_caption("2048")
        self.board = Board(self.board_size, self)
        self.board_pos = (-1, -1)
        self.current_tile_direction = None
        self.running = True
        while self.running:
            
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    
                        

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
        self.board.draw_tiles()
        self.win.blit(self.board, (x, y))

    def in_bounding_box(self, mouse_pos, x, y, width, height):
        return mouse_pos[0] in range(x, x + width) and mouse_pos[1] in range(y, y + height)

    def map_to_surface(self, surface_pos, mouse_pos):
        return mouse_pos[0] - surface_pos[0], mouse_pos[1] - surface_pos[1]


class Board(pygame.Surface):

    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, 1)
    DOWN = (0, -1)

    def __init__(self, size, parent):   
        super(Board, self).__init__((size, size))
        
        self.size = size
        self.parent = parent
        self.fill(self.parent.light_grey)
        self.old_pos = None
        self.selected = None
        self.border_size = int(self.size * 0.1) // 5
        self.square_size = int(self.size * 0.9) // 4
        self.tiles = {}
        self.tile_colors = {}
        self.squares = {}
        for i in range(4):
            for j in range(4):
                x, y = self._map_to_board(i, j)
                square = Square(self.square_size, (i, j), (x, y), self)
                square.fill(self.parent.grey)
                self.squares[(i, j)] = square
                self.blit(square, (x, y))
        self.create_tile(4, (2, 1))

    def draw_squares(self):
        for i in range(4):
            for j in range(4):
                square = self.squares[(i, j)]
                self.blit(square, square.board_pos)

    def create_tile(self, num, pos):
        color = self.tile_colors.get(num, self.parent.green)
        tile = Tile(num, pos, color, self.square_size)
        self.tiles[pos] = tile

    def draw_tiles(self):
        for pos, tile in self.tiles.items():
            self.draw_tile(pos, tile)

    def draw_tile(self, pos, tile):
        x = pos[0] * self.square_size + (pos[0] + 1) * self.border_size
        y = pos[1] * self.square_size + (pos[1] + 1) * self.border_size
        self.blit(tile, (x, y))

    def animate_tile(self, startpos, endpos):
        pass

    def move_tiles(self, direction):
        for pos, tile in self.sort_tiles(direction):
            new_pos = pos
            while self._valid_board_pos(new_pos):
                new_pos = self._vec_op(new_pos, direction)
            print(f"moving from {pos} to {new_pos}")

    def merge_tiles(self, direction):
        pass

    def sort_tiles(self, direction):
        sorted_tiles = []
        for i in range(4):
            for j in range(4):
                pos = (i, j) if direction[0] == 0 else (j, i)
                tile = self.tiles.get(pos)
                if tile is None:
                    continue
                sorted_tiles.append((pos, tile))
        if 1 in direction:
            sorted_tiles.reverse()
        return sorted_tiles

    def _map_to_board(self, i, j):
        x = self.border_size if not i else i * self.square_size + (i + 1) * self.border_size
        y = self.border_size if not j else j * self.square_size + (j + 1) * self.border_size
        return x, y

    def _valid_board_pos(self, pos):
        return pos[0] in range(0, 4) and pos[1] in range(0, 4)

    def _vec_op(self, v1, v2, op=lambda a, b: a + b):
        return [op(v1[i], v2[i]) for i in range(min(len(v1), len(v2)))]


class Square(pygame.Surface):

    def __init__(self, size, pos, board_pos, parent):
        super(Square, self).__init__((size, size))
        
        self.size = size
        self.pos = pos
        self.board_pos = board_pos
        self.parent = parent


class Tile(pygame.Surface):

    def __init__(self, num, pos, color, size):
        super(Tile, self).__init__((size, size))
        self.num = num
        self.pos = pos
        self.color = color
        self.size = size
        self.fill(self.color)


if __name__ == "__main__":
    win = Window()
    win.run()