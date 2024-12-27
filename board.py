import pygame
import random

# Constants
TILE_SIZE = 50
GRID_WIDTH = 15
GRID_HEIGHT = 15
SIDE_PANEL_WIDTH = 150
BOTTOM_BAR_HEIGHT = TILE_SIZE * 2
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE + BOTTOM_BAR_HEIGHT
FONT_SIZE = 36
BG_COLOR = (255, 255, 255)
TILE_COLOR = (200, 200, 200)
TEXT_COLOR = (0, 0, 0)
GRID_COLOR = (0, 0, 0)
POOL_TEXT_COLOR = (50, 50, 50)

LETTER_DISTRIBUTION = {
    "A": 13, "B": 3, "C": 3, "D": 6, "E": 18, "F": 3,
    "G": 4, "H": 3, "I": 12, "J": 2, "K": 2, "L": 5,
    "M": 3, "N": 8, "O": 11, "P": 3, "Q": 2, "R": 9,
    "S": 6, "T": 9, "U": 6, "V": 3, "W": 3, "X": 2,
    "Y": 3, "Z": 2
}

class TilePool:
    def __init__(self):
        self.pool = [letter for letter, count in LETTER_DISTRIBUTION.items() for _ in range(count)]
        random.shuffle(self.pool)

    def draw_tile(self):
        if self.pool:
            return self.pool.pop()
        return None

    def draw_counter(self, screen, font):
        counter_text = f"Tiles: {len(self.pool)}"
        text = font.render(counter_text, True, POOL_TEXT_COLOR)
        screen.blit(text, (GRID_WIDTH * TILE_SIZE + 20, 20))

    def dump_tiles(self, letter):
        if len(self.pool) >= 3:
            self.pool.append(letter)
            random.shuffle(self.pool)
            return [self.draw_tile() for _ in range(3)]
        return []

class PlayerBar:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.letters = []

    def draw(self):
        y = GRID_HEIGHT * TILE_SIZE
        for i, letter in enumerate(self.letters):
            x = i * TILE_SIZE
            pygame.draw.rect(self.screen, TILE_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
            text = self.font.render(letter, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
            self.screen.blit(text, text_rect)

    def add_tiles(self, letters):
        self.letters.extend(letters)

    def remove_tile(self, index):
        if 0 <= index < len(self.letters):
            return self.letters.pop(index)
        return None

class GameBoard:
    def __init__(self, screen):
        self.screen = screen
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.font = pygame.font.Font(None, FONT_SIZE)

    def draw_grid(self):
        for x in range(0, GRID_WIDTH * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, GRID_HEIGHT * TILE_SIZE))
        for y in range(0, GRID_HEIGHT * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (GRID_WIDTH * TILE_SIZE, y))

    def draw_tiles(self):
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if self.grid[row][col]:
                    letter = self.grid[row][col]
                    x = col * TILE_SIZE
                    y = row * TILE_SIZE
                    pygame.draw.rect(self.screen, TILE_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                    text = self.font.render(letter, True, TEXT_COLOR)
                    text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                    self.screen.blit(text, text_rect)

    def place_tile(self, row, col, letter):
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            self.grid[row][col] = letter

    def clear_grid(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Main game loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Banangrams Game")
    clock = pygame.time.Clock()
    pool = TilePool()
    player_bar = PlayerBar(screen)
    board = GameBoard(screen)

    # Initialize with 15 tiles
    player_bar.add_tiles([pool.draw_tile() for _ in range(15)])

    dragged_tile = None
    dragging = False
    drag_offset_x = drag_offset_y = 0

    running = True
    while running:
        screen.fill(BG_COLOR)
        board.draw_grid()
        board.draw_tiles()
        pool.draw_counter(screen, board.font)
        player_bar.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    if y > GRID_HEIGHT * TILE_SIZE:
                        index = x // TILE_SIZE
                        if 0 <= index < len(player_bar.letters):
                            dragged_tile = player_bar.remove_tile(index)
                            dragging = True
                            drag_offset_x = x % TILE_SIZE
                            drag_offset_y = y % TILE_SIZE
                    elif event.button == 3:  # Right click to trigger DUMP
                        if player_bar.letters:
                            dumped_letter = player_bar.letters.pop(0)
                            player_bar.add_tiles(pool.dump_tiles(dumped_letter))
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    x, y = event.pos
                    col, row = x // TILE_SIZE, y // TILE_SIZE
                    if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
                        board.place_tile(row, col, dragged_tile)
                    else:
                        player_bar.add_tiles([dragged_tile])
                    dragged_tile = None
                    dragging = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
