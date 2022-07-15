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
        for vec in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            print(f"Sorted for vector {vec}:", self.board.iter_tiles(vec), end="\n")
        self.current_tile_direction = None
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
                        self.board.process_click(*self.map_to_surface(self.board_pos, self.mouse_pos), "press")

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = pygame.mouse.get_pos()
                    if self.in_bounding_box(self.mouse_pos, *self.board_pos, self.board_size, self.board_size):
                        self.board.process_click(*self.map_to_surface(self.board_pos, self.mouse_pos), "release")         

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
        for tile in self.board.iter_tiles(self.current_tile_direction):
            tile.update(self.current_tile_direction)
        self.board.tiles.draw(self.board)
        self.win.blit(self.board, (x, y))

    def in_bounding_box(self, mouse_pos, x, y, width, height):
        return mouse_pos[0] in range(x, x + width) and mouse_pos[1] in range(y, y + height)

    def map_to_surface(self, surface_pos, mouse_pos):
        return mouse_pos[0] - surface_pos[0], mouse_pos[1] - surface_pos[1]


class Board(pygame.Surface):

    def __init__(self, size, parent):   
        super(Board, self).__init__((size, size))
        
        self.size = size
        self.parent = parent
        self.fill(self.parent.light_grey)
        self.old_pos = None
        self.selected = None
        self.border_size = int(self.size * 0.1) // 5
        self.square_size = int(self.size * 0.9) // 4
        self.tiles = pygame.sprite.Group()
        self.tileboard = {}
        self.squares = {}
        for i in range(4):
            for j in range(4):
                x, y = self.map_to_board(i, j)
                square = Square(self.square_size, (i, j), (x, y), self)
                square.fill(self.parent.grey)
                self.squares[(i, j)] = square
                self.tileboard[(i, j)] = None
                self.blit(square, (x, y))
                if random.randint(1, 4) == 1:
                    self.create_tile(i, j)

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

    def get_direction(self, old, new):
        dx, dy = vector_sub(new, old)
        if bool(dx) ^ bool(dy) == 0:
            return (0, 0)
        dx = int(dx / abs(dx or dy))
        dy = int(dy / abs(dx or dy))
        return (dx, dy)

    def process_click(self, x, y, mode):                    
        pos = self.get_clicked_square(x, y)
        if pos is None:
            return
        if mode == "press":
            for tile in self.tiles:
                if tile.pos == pos:
                    break
            self.old_pos = pos
        else:
            self.parent.current_tile_direction = self.get_direction(self.old_pos, pos)
            for tile in self.tiles:
                tile.move(self.parent.current_tile_direction)

    def map_to_board(self, i, j):
        x = self.border_size if not i else i * self.square_size + (i + 1) * self.border_size
        y = self.border_size if not j else j * self.square_size + (j + 1) * self.border_size
        return x, y

    def create_tile(self, i, j):
        tile = Tile(self.square_size, (i, j), 64, self)
        self.tileboard[(i, j)] = tile
        self.tiles.add(tile)

    def sort_tiles(self, mode, reverse):
        tiles = []
        for i in range(4):
            for j in range(4):
                tile = self.tileboard[(i, j) if mode == "rows" else (j, i)]
                if tile is None:
                    continue
                tiles.append(tile)
        if reverse:
            tiles.reverse()
        return tiles

    def iter_tiles(self, direction):
        if direction == (1, 0):
            return self.sort_tiles("cols", True)
        elif direction == (-1, 0):
            return self.sort_tiles("cols", False)
        elif direction == (0, 1):
            return self.sort_tiles("rows", True)
        return self.sort_tiles("rows", False)


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
        self.image.fill(tuple([random.randint(0, 255) for i in range(3)]))
        self.rect = self.image.get_rect(x=self.x, y=self.y)
        self.axis_move = None
        self.target = None
        self.step = 12
        self.n_steps = -1

    def move(self, vec):
        if all(vec):
            return 

        idx = not list(vec).index(0)
        new_pos = vector_add(self.pos, vec)

        if new_pos[idx] not in range(4):
            return            
        self.parent.tileboard[self.pos] = None
        self.pos = new_pos    
        self.parent.tileboard[self.pos] = self
        self.axis_move = "x" if not idx else "y"
        self.target = self.parent.map_to_board(*self.pos)
        self.n_steps = abs(self.parent.map_to_board(*vec)[idx] // self.step)
        
    def update(self, direction):
        if self.axis_move is None or self.target is None:
            return
        
        if self.n_steps == 0:
            try:
                print(self.pos, direction)
                adjacent = self.parent.tileboard[vector_add(self.pos, direction)]
                if adjacent is None:
                    self.rect.x, self.rect.y = self.target
                    self.move(direction)
                    return
            except KeyError:
                pass
            self.rect.x, self.rect.y = self.target
            self.axis_move = None
            self.target = None
            return

        rect_pos = getattr(self.rect, self.axis_move)
        if direction in [(0, 1), (1, 0)]:
            setattr(self.rect, self.axis_move, rect_pos + self.step)
        else: 
            setattr(self.rect, self.axis_move, rect_pos - self.step)
        self.n_steps -= 1

    def __repr__(self):
        return f"Tile(pos={self.pos}, num={self.num})"


if __name__ == "__main__":
    window = Window()
    window.run()