import pygame
import random
import math

# Constants
TILE_SIZE = 50
GRID_WIDTH = 16
GRID_HEIGHT = 16
SIDE_PANEL_WIDTH = 150
BOTTOM_BAR_HEIGHT = TILE_SIZE * 2
DUMP_AREA_HEIGHT = TILE_SIZE
BUTTON_HEIGHT = 50
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE + BOTTOM_BAR_HEIGHT + DUMP_AREA_HEIGHT + BUTTON_HEIGHT
FONT_SIZE = 36
BG_COLOR = (255, 255, 255)
TILE_COLOR = (200, 200, 200)
DUMP_COLOR = (220, 120, 120)
BUTTON_COLOR = (100, 200, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
GRID_COLOR = (0, 0, 0)
POOL_TEXT_COLOR = (50, 50, 50)
BG_COLOR_TOP = (234, 163, 255)
BG_COLOR_BOTTOM = (41, 71, 102)
TILE_SHADOW_COLOR = (98, 131, 166)
TILE_BORDER_COLOR = (15, 36, 59)

LETTER_DISTRIBUTION = {
    "A": 13, "B": 3, "C": 3, "D": 6, "E": 18, "F": 3,
    "G": 4, "H": 3, "I": 12, "J": 2, "K": 2, "L": 5,
    "M": 3, "N": 8, "O": 11, "P": 3, "Q": 2, "R": 9,
    "S": 6, "T": 9, "U": 6, "V": 3, "W": 3, "X": 2,
    "Y": 3, "Z": 2
}

def draw_gradient_background(screen):
    for y in range(WINDOW_HEIGHT):
        color = (
            BG_COLOR_TOP[0] + (BG_COLOR_BOTTOM[0] - BG_COLOR_TOP[0]) * y // WINDOW_HEIGHT,
            BG_COLOR_TOP[1] + (BG_COLOR_BOTTOM[1] - BG_COLOR_TOP[1]) * y // WINDOW_HEIGHT,
            BG_COLOR_TOP[2] + (BG_COLOR_BOTTOM[2] - BG_COLOR_TOP[2]) * y // WINDOW_HEIGHT,
        )
        pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))

class Tile:
    def __init__(self, letter, x, y):
        if not isinstance(letter, str):  # Ensure letter is a string
            raise ValueError(f"Invalid letter: {letter}")
        self.letter = letter
        self.x = float(x)  # Use float for smooth movement
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.speed = 15

    def draw(self, screen, font):
        # Shadow
        pygame.draw.rect(screen, TILE_SHADOW_COLOR, (int(self.x) + 4, int(self.y) + 4, TILE_SIZE, TILE_SIZE), border_radius=8)
        # Tile
        pygame.draw.rect(screen, TILE_COLOR, (int(self.x), int(self.y), TILE_SIZE, TILE_SIZE), border_radius=8)
        pygame.draw.rect(screen, TILE_BORDER_COLOR, (int(self.x), int(self.y), TILE_SIZE, TILE_SIZE), 2, border_radius=8)
        # Letter
        text = font.render(self.letter, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(int(self.x) + TILE_SIZE // 2, int(self.y) + TILE_SIZE // 2))
        screen.blit(text, text_rect)

    def move_towards_target(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)
        if distance > self.speed:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
        else:
            self.x = self.target_x
            self.y = self.target_y


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
        self.tiles = []

    def draw(self):
        # Determine the number of rows required for the current number of tiles
        num_tiles_per_row = (WINDOW_WIDTH - SIDE_PANEL_WIDTH) // TILE_SIZE
        num_rows = math.ceil(len(self.tiles) / num_tiles_per_row)
        
        for i, tile in enumerate(self.tiles):
            row = i // num_tiles_per_row
            col = i % num_tiles_per_row
            x = col * TILE_SIZE
            y = GRID_HEIGHT * TILE_SIZE + DUMP_AREA_HEIGHT + BUTTON_HEIGHT + row * TILE_SIZE
            tile.target_x = x
            tile.target_y = y
            tile.move_towards_target()
            tile.draw(self.screen, self.font)

    def add_tiles(self, items):
        for item in items:
            if isinstance(item, Tile):
                # Reset the tile's target position to the player bar area
                tile_width = TILE_SIZE
                tile_height = TILE_SIZE
                num_tiles_per_row = (WINDOW_WIDTH - SIDE_PANEL_WIDTH) // TILE_SIZE
                num_tiles = len(self.tiles)
                row = num_tiles // num_tiles_per_row
                col = num_tiles % num_tiles_per_row
                x = col * TILE_SIZE
                y = GRID_HEIGHT * TILE_SIZE + DUMP_AREA_HEIGHT + BUTTON_HEIGHT + row * TILE_SIZE
                item.target_x = x
                item.target_y = y
                self.tiles.append(item)
            elif isinstance(item, str):
                # Create a new Tile from the letter
                x = 0  # Initial x position (will be set dynamically during drawing)
                y = GRID_HEIGHT * TILE_SIZE + DUMP_AREA_HEIGHT + BUTTON_HEIGHT
                self.tiles.append(Tile(item, x, y))
            else:
                raise ValueError(f"Invalid item in add_tiles: {item}")

    def remove_tile(self, index):
        if 0 <= index < len(self.tiles):
            return self.tiles.pop(index)
        return None

    def clear(self):
        self.tiles = []

    def get_tile_at_position(self, x, y):
        for i, tile in enumerate(self.tiles):
            if tile.x <= x < tile.x + TILE_SIZE and tile.y <= y < tile.y + TILE_SIZE:
                return i, tile
        return None, None


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
                    tile = self.grid[row][col]  # Get the Tile object
                    if isinstance(tile, Tile):  # Ensure it's a Tile object
                        tile.draw(self.screen, self.font)

    def place_tile(self, row, col, tile):
        if isinstance(tile, Tile) and 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            if self.grid[row][col] is None:  # Ensure the cell is empty
                tile.target_x = col * TILE_SIZE
                tile.target_y = row * TILE_SIZE
                tile.x = tile.target_x
                tile.y = tile.target_y
                self.grid[row][col] = tile
                return True
        return False

    def remove_tile(self, row, col):
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            tile = self.grid[row][col]
            self.grid[row][col] = None
            return tile
        return None

    def clear_board(self):
        tiles = []
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if self.grid[row][col]:
                    tiles.append(self.grid[row][col])
                    self.grid[row][col] = None
        return tiles


class DumpArea:
    def __init__(self, screen):
        self.screen = screen
        self.rect = pygame.Rect(0, GRID_HEIGHT * TILE_SIZE, GRID_WIDTH * TILE_SIZE, DUMP_AREA_HEIGHT)

    def draw(self):
        pygame.draw.rect(self.screen, DUMP_COLOR, self.rect)
        font = pygame.font.Font(None, FONT_SIZE)
        text = font.render("Dump Area", True, TEXT_COLOR)
        text_rect = text.get_rect(center=self.rect.center)
        self.screen.blit(text, text_rect)

    def is_in_area(self, pos):
        return self.rect.collidepoint(pos)

class ResetButton:
    def __init__(self, screen):
        self.screen = screen
        self.rect = pygame.Rect(GRID_WIDTH * TILE_SIZE // 2 - 100, GRID_HEIGHT * TILE_SIZE + DUMP_AREA_HEIGHT + 10, 200, BUTTON_HEIGHT)

    def draw(self):
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.rect)
        font = pygame.font.Font(None, FONT_SIZE)
        text = font.render("Reset Board", True, BUTTON_TEXT_COLOR)
        text_rect = text.get_rect(center=self.rect.center)
        self.screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Main game loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Theo B's Banana Solitaire for the Chronically Alone")
    clock = pygame.time.Clock()
    pool = TilePool()
    player_bar = PlayerBar(screen)
    board = GameBoard(screen)
    dump_area = DumpArea(screen)
    reset_button = ResetButton(screen)

    # Initialize with 15 tiles
    initial_tiles = [pool.draw_tile() for _ in range(21)]
    player_bar.add_tiles(initial_tiles)

    dragged_tile = None
    dragging = False
    drag_offset_x = drag_offset_y = 0
    dragged_from_board = False
    original_position = None  # To store original position if placement fails

    running = True
    while running:
        screen.fill(BG_COLOR)
        draw_gradient_background(screen)
        board.draw_grid()
        board.draw_tiles()
        dump_area.draw()
        reset_button.draw()
        pool.draw_counter(screen, board.font)
        player_bar.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    if reset_button.is_clicked((x, y)):  # Handle Reset Button
                        cleared_tiles = board.clear_board()
                        letters = [tile.letter for tile in cleared_tiles if isinstance(tile, Tile)]
                        player_bar.add_tiles(letters)
                    elif y > GRID_HEIGHT * TILE_SIZE + DUMP_AREA_HEIGHT + BUTTON_HEIGHT:
                        # Clicked within the player bar area
                        index, tile = player_bar.get_tile_at_position(x, y)
                        if tile:
                            dragged_tile = player_bar.remove_tile(index)
                            dragging = True
                            dragged_from_board = False
                            drag_offset_x = x - tile.x
                            drag_offset_y = y - tile.y
                    else:
                        # Clicked within the board area
                        col, row = x // TILE_SIZE, y // TILE_SIZE
                        if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT and board.grid[row][col]:
                            dragged_tile = board.remove_tile(row, col)
                            dragging = True
                            dragged_from_board = True
                            # Calculate offset within the tile
                            drag_offset_x = x - (col * TILE_SIZE)
                            drag_offset_y = y - (row * TILE_SIZE)
                            original_position = (row, col)
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    x, y = event.pos
                    if dump_area.is_in_area((x, y)):  # Dump the tile
                        dumped_tiles = pool.dump_tiles(dragged_tile.letter)
                        player_bar.add_tiles(dumped_tiles)
                        dragged_tile = None
                        dragging = False
                        dragged_from_board = False
                        original_position = None
                    else:
                        # Attempt to place the tile on the board
                        col, row = x // TILE_SIZE, y // TILE_SIZE
                        placed = False
                        if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
                            placed = board.place_tile(row, col, dragged_tile)
                            if placed:
                                # Successfully placed on the board
                                pass
                            else:
                                # Failed to place on the board (cell occupied)
                                if dragged_from_board and original_position:
                                    original_row, original_col = original_position
                                    # Attempt to return to original position
                                    placed_back = board.place_tile(original_row, original_col, dragged_tile)
                                    if not placed_back:
                                        # If returning to original position fails, add to player bar
                                        player_bar.add_tiles([dragged_tile])
                                else:
                                    # Add back to player bar
                                    player_bar.add_tiles([dragged_tile])
                        else:
                            # Outside the board, add back to player bar
                            player_bar.add_tiles([dragged_tile])
                        # Reset dragging state
                        dragged_tile = None
                        dragging = False
                        dragged_from_board = False
                        original_position = None

        # Move tiles towards their target positions
        for tile in player_bar.tiles:
            tile.move_towards_target()
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if board.grid[row][col]:
                    board.grid[row][col].move_towards_target()

        # Draw the dragged tile
        if dragging and dragged_tile:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dragged_tile.x = mouse_x - drag_offset_x
            dragged_tile.y = mouse_y - drag_offset_y
            dragged_tile.draw(screen, board.font)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
