# Pygame remake of my old Minesweeper clone
# Same assets and mostly the same logic
# (c) Marley Sudbury 2019

import pygame
import random
import time
import sys
from tile import Tile
from counter import Counter
from text_box import TextBox
from pathlib import Path


class Game:
    def __init__(self):
        pygame.init()

        self.W_WIDTH = 600
        self.W_HEIGHT = 500
        self.game_display = pygame.display.set_mode(
            (self.W_WIDTH, self.W_HEIGHT))

        pygame.display.set_caption("Minesweeper")

        self.TILE_SIZE = 21
        self.game_state = "MENU"
        self.game_mode = "EASY"
        self.stop = False

        self.images = {}
        self.image_path = Path("data")
        pygame.mixer.init()
        self.sounds = {}
        self.sound_path = Path("data/tunes")
        self.load_data_initial()
        # TODO: Get a propper icon
        # pygame.display.set_icon(self.images["FLAGGED"])
        self.background = self.images["ИГРАТЬ"]

        self.cols = 0
        self.rows = 0
        self.mines = 0
        self.grid_x = 0
        self.grid_y = 0
        self.tiles = []
        self.timer = False
        self.start = False
        self.start_time = 0
        self.time = Counter(self, 30, 15, 0, 0, 0)
        self.mine_left = Counter(self, 30 + (15 * 5), 15, 0, 0, 0)

        self.loaded = {
            "играть": False,
            "правила": False,
            "gamemode": False,
            "game": False
        }

        # Used to determine juiciness
        self.tiles_cleared = 0

        self.won = False
        self.lost = False

        self.load_fonts()
        """self.sounds["music"].play(-1)"""
        """self.sounds["explosion1"].play()"""

        self.load_leaderboard()

        self.box = None

        # Should the current box.get_value() be returned?
        self.return_value = False

        # Global variables for the options menu
        self.display_done = False  # Display DONE overlay
        self.mute = False

        self.clock = pygame.time.Clock()
        self.clock.tick(60)

        # Process paramaters
        arguments = [a.upper() for a in sys.argv]

        try:
            t_index = arguments.index("-TOUCH")
            self.TILE_SIZE = 33
        except ValueError:
            print("Not touch enabled")
        try:
            q_index = arguments.index("-QUICK")
            self.game_mode = "EASY"
            if len(arguments) > q_index + 1:
                if arguments[q_index+1] in ["MEDIUM", "HARD"]:
                    self.game_mode = arguments[q_index+1]
            self.goto_game()
        except ValueError:
            print("Not quicklaunch")

    def loop(self):
        """The game loop."""
        while not self.stop:
            pygame.event.pump()
            self.handle_events()
            pos = pygame.mouse.get_pos()
            if self.game_state == "MENU":
                if pos[0] > 300:
                    if pos[1] < 190:
                        self.background = self.images["ИГРАТЬ"]
                    elif 190 <= pos[1] < 230:
                        self.background = self.images["ПРАВИЛА"]
                    """elif 230 <= pos[1] < 275:
                        self.background = self.images["OPTIONS"]
                    elif 275 <= pos[1]:
                        self.background = self.images["LEADERBOARD"]"""
                else:
                    self.background = self.images["ИГРАТЬ"]
            elif self.game_state == "ИГРАТЬ":
                if pos[1] < 187:
                    self.background = self.images["GAME_1"]
                elif 187 <= pos[1] < 230:
                    self.background = self.images["GAME_2"]
                elif 230 <= pos[1] < 274:
                    self.background = self.images["GAME_3"]
                """elif 274 <= pos[1] < 316:
                    self.background = self.images["GAME_4"]
                else:
                    self.background = self.images["GAME_5"]"""
            elif self.game_state == "PLAYING":
                current_time = time.time()
                if current_time - self.start_time >= 1 and self.timer:
                    self.start_time = current_time
                    self.time.increment()
                self.background = self.images["GAME_BG"]
            elif self.game_state == "ПРАВИЛА":
                self.background = self.images["STORY_SCREEN"]
                if not self.display_done:
                    if 450 < pos[1]:
                        self.background = self.images["RETURN_TO_MENU"]
            """elif self.game_state == "OPTIONS":
                if not self.display_done:
                    if pos[1] < 210:
                        self.background = self.images["RESET_LEADERBOARD"]
                    elif 210 <= pos[1] < 300:
                        self.background = self.images["MUTE_SOUND"]
                    else:
                        self.background = self.images["RETURN_TO_MENU"]
            elif self.game_state == "LEADERBOARD":
                self.background = self.images["GAME_BG"]"""

            if self.return_value:
                self.update_leaderboard()

            # Draw
            self.game_display.blit(self.background, (0, 0))
            if self.game_state == "PLAYING":
                self.display_tiles()
                self.display_counters()
                if self.lost:
                    self.game_display.blit(self.images["LOSE"], (0, 0))
                elif self.won:
                    self.game_display.blit(self.images["WIN"], (0, 0))
            """elif self.game_state == "LEADERBOARD":
                self.display_leaderboard()
            if self.game_state == "OPTIONS":
                if self.mute:
                    self.game_display.blit(self.images["MUTED"], (0, 0))
                else:
                    self.game_display.blit(self.images["UNMUTED"], (0, 0))
                if self.display_done:
                    self.game_display.blit(self.images["DONE_OVERLAY"], (0, 0))"""

            if self.box != None:
                self.box.draw(self)
            pygame.display.update()
        pygame.quit()
        quit()

    def goto_menu(self):
        self.game_state = "MENU"

    def goto_gamemode(self):
        if not self.loaded["gamemode"]:
            self.load_data_gamemode()
        self.game_state = "ИГРАТЬ"

    def goto_game(self):
        if not self.loaded["game"]:
            self.load_data_game()
        self.game_state = "PLAYING"
        self.start_game()

    """def goto_options(self):
        if not self.loaded["options"]:
            self.load_data_options()
        self.game_state = "OPTIONS"
        self.sounds["vn"].play()"""

    def goto_story(self):
        if not self.loaded["правила"]:
            self.load_data_story()
        self.game_state = "ПРАВИЛА"

    """def goto_leaderboard(self):
        # The only data needed is the game background
        if not self.loaded["game"]:
            self.load_data_game()
        self.game_state = "LEADERBOARD"""

    def update_leaderboard(self):
        self.return_value = False
        if self.game_mode == "EASY":
            if self.time.get_val() < int(self.leaderboard[0][1]):
                self.leaderboard[0][0] = self.box.get_val()
                self.leaderboard[0][1] = "{:0>3}".format(self.time.get_val())
        if self.game_mode == "MEDIUM":
            if self.time.get_val() < int(self.leaderboard[1][1]):
                self.get_name()
                self.leaderboard[1][0] = self.box.get_val()
                self.leaderboard[1][1] = "{:0>3}".format(self.time.get_val())
        if self.game_mode == "HARD":
            if self.time.get_val() < int(self.leaderboard[2][1]):
                self.get_name()
                self.leaderboard[2][0] = self.box.get_val()
                self.leaderboard[2][1] = "{:0>3}".format(self.time.get_val())

        self.box = None

        """self.sounds["winMusic"].stop()
        self.sounds["gameOver"].stop()
        self.sounds["music"].play(-1)"""

        self.timer = False
        self.lost = False
        self.won = False
        self.time.set_val(0)

        self.save_leaderboard()
        self.goto_leaderboard()

    def load_leaderboard(self):
        self.leaderboard = {}
        lb_file = open('data/leader.txt')
        text = lb_file.read().split('\n')
        for i in range(0, len(text)):
            self.leaderboard[i] = text[i].split(',')

        lb_file.close()

    def save_leaderboard(self):
        text = ''
        for i in range(0, 4):
            text += '{},{}\n'.format(self.leaderboard[i][0],
                                     self.leaderboard[i][1])
        lb_file = open('data/leader.txt', 'w')
        lb_file.write(text)
        lb_file.close()

    def reset_leaderboard(self):
        text = '???,999\n???,999\n???,999\n???,0'
        lb_file = open('data/leader.txt', 'w')
        lb_file.write(text)
        lb_file.close()
        self.load_leaderboard()

    def display_leaderboard(self):
        easy = self.font.render('{:<12}{:<10}{}'.format(
            'Easy', self.leaderboard[0][0], self.leaderboard[0][1]), True, (255, 0, 0))
        medium = self.font.render(
            '{:<12}{:<10}{}'.format('Medium', self.leaderboard[1][0], self.leaderboard[1][1]), True, (255, 0, 0))
        hard = self.font.render('{:<12}{:<10}{}'.format(
            'Hard', self.leaderboard[2][0], self.leaderboard[2][1]), True, (255, 0, 0))
        concentric = self.font.render(
            '{:<12}{}{:>10}'.format('Concentric', self.leaderboard[3][0], ' stage ' + self.leaderboard[3][1]), True, (255, 0, 0))
        self.game_display.blit(easy, (50, 90))
        self.game_display.blit(medium, (50, 120))
        self.game_display.blit(hard, (50, 150))
        '''self.game_display.blit(concentric, (50, 180))'''

    def get_name(self):
        self.box = TextBox(self.W_WIDTH/2-65/2, self.W_HEIGHT/2-45/2, 65, 45)

    def win(self):
        # TODO: refactor the heck out of this plz
        self.won = True
        self.timer = False
        if self.game_mode == "EASY":
            if self.time.get_val() < int(self.leaderboard[0][1]):
                self.get_name()
        if self.game_mode == "MEDIUM":
            if self.time.get_val() < int(self.leaderboard[1][1]):
                self.get_name()
        if self.game_mode == "HARD":
            if self.time.get_val() < int(self.leaderboard[2][1]):
                self.get_name()
        '''if self.game_mode == "CONCENTRIC":
            print("hmm")'''

        for row in self.tiles:
            for tile in row:
                if tile.covered and not tile.mine:
                    tile.covered = False
        """self.sounds["music"].stop()
        self.sounds["winMusic"].play(-1)"""
        saying = random.randint(0, 3)
        """if saying == 0:
            self.sounds["finesweeping"].play()
        elif saying == 1:
            self.sounds["goodjob"].play()
        else:
            self.sounds["youdidit"].play()"""

    def lose(self):
        self.lost = True
        self.timer = False
        for row in self.tiles:
            for tile in row:
                if tile.mine and tile.covered:
                    tile.covered = False
        """self.sounds["music"].stop()
        self.sounds["gameOver"].play(-1)
        self.sounds["explosion1"].play()
        self.sounds["scream"].play()"""
        saying = random.randint(0, 2)
        """if saying == 0:
            self.sounds["grr"].play()
        else:
            self.sounds["merloc"].play()"""

    def clearing(self, t):
        (i, j) = t
        if i == 0 and j == 0:
            # Top left
            adjacent = [(i, j+1), (i+1, j+1), (i+1, j)]
        elif i == 0 and j == self.cols - 1:
            # Top right
            adjacent = [(i, j-1),
                        (i+1, j-1), (i+1, j)]
        elif i == self.rows - 1 and j == 0:
            # Bottom left
            adjacent = [(i-1, j), (i-1, j+1),
                        (i, j+1)]
        elif i == self.rows - 1 and j == self.cols - 1:
            # Bottom right
            adjacent = [(i-1, j-1), (i-1, j),
                        (i, j-1)]
        elif i == 0:
            # Top row
            adjacent = [(i, j-1), (i, j+1),
                        (i+1, j-1), (i+1, j), (i+1, j+1)]
        elif i == self.rows - 1:
            # Bottom row
            adjacent = [(i-1, j-1), (i-1, j), (i-1, j+1),
                        (i, j-1), (i, j+1)]
        elif j == 0:
            # Left column
            adjacent = [(i-1, j), (i-1, j+1),
                        (i, j+1),
                        (i+1, j), (i+1, j+1)]
        elif j == self.cols - 1:
            # Right column
            adjacent = [(i-1, j-1), (i-1, j),
                        (i, j-1),
                        (i+1, j-1), (i+1, j)]
        else:
            # Otherwise
            adjacent = [(i-1, j-1), (i-1, j), (i-1, j+1),
                        (i, j-1), (i, j+1),
                        (i+1, j-1), (i+1, j), (i+1, j+1)]

        if self.tiles[i][j].adj == 0:
            for tile in adjacent:
                if self.tiles[tile[0]][tile[1]].covered and not self.tiles[tile[0]][tile[1]].flagged:
                    self.tiles_cleared += 1
                    self.tiles[tile[0]][tile[1]].covered = False
                    self.clearing(tile)

    def display_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.draw()

    def display_counters(self):
        self.time.draw()
        self.mine_left.draw()

    def start_game(self):
        self.start = True

        if self.game_mode == "EASY":
            self.rows = 9
            self.cols = 9
            self.mines = 10
        elif self.game_mode == "MEDIUM":
            self.rows = 16
            self.cols = 16
            self.mines = 40
        elif self.game_mode == "HARD":
            self.rows = 20
            self.cols = 27
            self.mines = 101
        """elif self.game_mode == "CUSTOM":
            self.rows = 24
            self.cols = 32
            self.mines = 256"""

        self.mine_left.set_val(self.mines)

        self.grid_x = (self.W_WIDTH / 2) - ((self.cols * self.TILE_SIZE)/2)
        self.grid_y = (self.W_HEIGHT / 2) - \
            ((self.rows * self.TILE_SIZE)/2) + 28

        self.tiles = []

        for i in range(0, self.rows):
            new_row = []
            for j in range(0, self.cols):
                new_row.append(
                    Tile(self, self.grid_x + (self.TILE_SIZE * j), self.grid_y + (self.TILE_SIZE * i)))
            self.tiles.append(new_row)

    def click_grid(self, type):
        pos = pygame.mouse.get_pos()
        if self.tiles[0][0].x <= pos[0] <= self.tiles[0][self.cols-1].x + self.TILE_SIZE and self.tiles[0][0].y <= pos[1] <= self.tiles[self.rows-1][self.cols-1].y + self.TILE_SIZE:
            # User has clicked inside tile grid
            the_tile = None
            tuple_cov = (0, 0)
            for i, row in enumerate(self.tiles):
                for j, tile in enumerate(row):
                    if tile.x <= pos[0] <= tile.x + self.TILE_SIZE and tile.y <= pos[1] <= tile.y + self.TILE_SIZE:
                        the_tile = tile
                        tuple_cov = (i, j)

            if self.start:
                (i, j) = tuple_cov
                self.place_mines(i, j)
                self.count_adjacent()
                self.start = False
                self.timer = True
                self.start_time = time.time()
            if type == 1:
                # Uncover tile if not flagged
                if not the_tile.flagged:
                    the_tile.covered = False
                    if the_tile.mine:
                        the_tile.exploded = True
                        self.lose()
                    else:
                        self.tiles_cleared = 0
                        self.clearing(tuple_cov)
                        """if self.tiles_cleared > 10:
                            self.sounds["juicy"].play()"""
            else:
                # Toggle flag (unless it is already uncovered)
                if the_tile.covered:
                    # the_tile.flagged = not the_tile.flagged
                    if the_tile.flagged and not the_tile.unsure:
                        the_tile.unsure = True
                        self.mine_left.increment()
                    elif the_tile.flagged:
                        the_tile.flagged = False
                        the_tile.unsure = False
                    else:
                        the_tile.flagged = True
                        self.mine_left.decrement()
                        if self.mine_left.get_val() == 0:
                            correct = True
                            for row in self.tiles:
                                for tile in row:
                                    if tile.mine and not tile.flagged or not tile.mine and tile.flagged and not tile.unsure:
                                        correct = False
                            if correct:
                                self.win()

    def place_mines(self, i, j):
        mine_to_place = self.mines
        while mine_to_place > 0:
            row = random.randint(0, self.rows-1)
            col = random.randint(0, self.cols-1)
            if not self.tiles[row][col].mine and row != i and col != j:
                self.tiles[row][col].mine = True
                mine_to_place -= 1

    def count_adjacent(self):
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if i == 0 and j == 0:
                    # Top left corner
                    tile.adj += self.check_neighbour(i, j, [4, 5, 6])
                elif i == 0 and j == self.cols - 1:
                    # Top right corner
                    tile.adj += self.check_neighbour(i, j, [6, 7, 8])
                elif i == self.rows - 1 and j == 0:
                    # Bottom left corner
                    tile.adj += self.check_neighbour(i, j, [2, 3, 4])
                elif i == self.rows - 1 and j == self.cols - 1:
                    # Bottom right corner
                    tile.adj += self.check_neighbour(i, j, [1, 2, 8])
                elif i == 0:
                    # Top side
                    tile.adj += self.check_neighbour(
                        i, j, [4, 5, 6, 7, 8])
                elif i == self.rows - 1:
                    # Bottom side
                    tile.adj += self.check_neighbour(
                        i, j, [1, 2, 3, 4, 8])
                elif j == 0:
                    # Left hand side
                    tile.adj += self.check_neighbour(
                        i, j, [2, 3, 4, 5, 6])
                elif j == self.cols - 1:
                    # Right hand side
                    tile.adj += self.check_neighbour(
                        i, j, [1, 2, 6, 7, 8])
                else:
                    # Tile with eight neighbours
                    tile.adj += self.check_neighbour(i, j)

    def check_neighbour(self, i, j, n=[1, 2, 3, 4, 5, 6, 7, 8]):
        # 1 to 8 clockwise from top left to left
        total = 0
        if 1 in n and self.tiles[i-1][j-1].mine:
            total += 1
        if 2 in n and self.tiles[i-1][j].mine:
            total += 1
        if 3 in n and self.tiles[i-1][j+1].mine:
            total += 1
        if 4 in n and self.tiles[i][j+1].mine:
            total += 1
        if 5 in n and self.tiles[i+1][j+1].mine:
            total += 1
        if 6 in n and self.tiles[i+1][j].mine:
            total += 1
        if 7 in n and self.tiles[i+1][j-1].mine:
            total += 1
        if 8 in n and self.tiles[i][j-1].mine:
            total += 1
        return total

    def handle_events(self):
        """Handles events since the last loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Play relevant sound effect
                """if event.button == 1:
                    self.sounds["click"].play()
                else:
                    self.sounds["rClick"].play()"""

                # The bastard's done a click
                if self.game_state == "MENU":
                    # The user has clicked in the menu!
                    if self.background == self.images["ИГРАТЬ"]:
                        self.goto_gamemode()
                    elif self.background == self.images["ПРАВИЛА"]:
                        self.goto_story()
                    """elif self.background == self.images["OPTIONS"]:
                        self.goto_options()
                    else:
                        self.goto_leaderboard()"""
                elif self.game_state == "ИГРАТЬ":
                    if self.background == self.images["GAME_1"]:
                        self.game_mode = "EASY"
                    elif self.background == self.images["GAME_2"]:
                        self.game_mode = "MEDIUM"
                    elif self.background == self.images["GAME_3"]:
                        self.game_mode = "HARD"
                    """else:
                        self.game_mode = "CUSTOM"""

                    self.goto_game()
                elif self.game_state == "PLAYING" and not self.won and not self.lost:
                    self.click_grid(event.button)
                """elif self.game_state == "OPTIONS":
                    if self.display_done:
                        self.display_done = False
                    elif self.background == self.images["RESET_LEADERBOARD"]:
                        self.reset_leaderboard()
                        self.display_done = True
                    elif self.background == self.images["MUTE_SOUND"]:
                        # pygame.mixer.stop()
                        if pygame.mixer.get_num_channels() > 0:
                            pygame.mixer.set_num_channels(0)
                            self.mute = True
                        else:
                            pygame.mixer.set_num_channels(8)
                            self.sounds["music"].play(-1)
                            self.mute = False

                        print("Shhh")
                        self.display_done = True
                    elif self.background == self.images["RETURN_TO_MENU"]:
                        self.goto_menu()"""
            if event.type == pygame.KEYDOWN:
                if self.box != None:
                    if event.key == pygame.K_ESCAPE:
                        self.box = None
                    elif event.key == pygame.K_RETURN:
                        self.return_value = True
                    else:
                        self.box.key_response(event)
                elif event.key == pygame.K_ESCAPE:
                    self.display_done = False
                    # Sound effect
                    saying = random.randint(0, 2)
                    if saying == 0:
                        self.sounds["thechildren"].play()
                    else:
                        self.sounds["work"].play()

                    if self.game_state == "MENU":
                        self.stop = True
                    elif self.game_state == "PLAYING":
                        """if self.won or self.lost:
                            self.sounds["winMusic"].stop()
                            self.sounds["gameOver"].stop()
                            self.sounds["music"].play(-1)"""

                        self.timer = False
                        self.lost = False
                        self.won = False
                        self.time.set_val(0)
                        self.goto_gamemode()
                    else:
                        self.goto_menu()
                elif event.key == pygame.K_r and self.game_state == "PLAYING":
                    """if self.won or self.lost:
                        self.sounds["winMusic"].stop()
                        self.sounds["gameOver"].stop()
                        self.sounds["music"].play(-1)

                    self.sounds["scream"].play()"""
                    self.timer = False
                    self.lost = False
                    self.won = False
                    self.time.set_val(0)
                    self.goto_game()

    def load_data_initial(self):
        # Menu options
        self.images["ИГРАТЬ"] = pygame.image.load(
            str(self.image_path / "play1.png")).convert_alpha()
        self.images["ПРАВИЛА"] = pygame.image.load(
            str(self.image_path / "rule.png")).convert_alpha()
        """self.images["OPTIONS"] = pygame.image.load(
            str(self.image_path / "options.png")).convert_alpha()
        self.images["LEADERBOARD"] = pygame.image.load(
            str(self.image_path / "leaderboard.png")).convert_alpha()"""

        """Loads all sounds for the game."""

        # Music
        """self.sounds["music"] = pygame.mixer.Sound(
            str(self.sound_path / "music.ogg"))
        self.sounds["music"].set_volume(0.2)"""

        # Utterances of K_ESCAPE
        # "Think of the children"
        """self.sounds["thechildren"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "thechildren.ogg"))
        # "Get back to work"
        self.sounds["work"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "work.ogg"))

        # Left click "Ugh"
        self.sounds["click"] = pygame.mixer.Sound(
            str(self.sound_path / "click.ogg"))
        # Right click "Brrrrring"
        self.sounds["rClick"] = pygame.mixer.Sound(
            str(self.sound_path / "flag.ogg"))"""

        # Boom!
        """self.sounds["explosion1"] = pygame.mixer.Sound(
            str(self.sound_path / "explosion-01.ogg"))
        self.sounds["explosion1"].set_volume(0.2)"""

    def load_data_gamemode(self):
        # Game type selection
        self.images["GAME_1"] = pygame.image.load(
            str(self.image_path / "gameMode1.png")).convert_alpha()
        self.images["GAME_2"] = pygame.image.load(
            str(self.image_path / "gameMode2.png")).convert_alpha()
        self.images["GAME_3"] = pygame.image.load(
            str(self.image_path / "gameMode3.png")).convert_alpha()
        self.images["GAME_4"] = pygame.image.load(
            str(self.image_path / "gameMode4.png")).convert_alpha()
        self.images["GAME_5"] = pygame.image.load(
            str(self.image_path / "gameMode5.png")).convert_alpha()

        self.loaded["gamemode"] = True

    def load_data_game(self): #время
        # Counter
        self.images["-"] = pygame.image.load(
            str(self.image_path / "nums" / "-.png")).convert_alpha()
        self.images[0] = pygame.image.load(
            str(self.image_path / "nums" / "0.png")).convert_alpha()
        self.images[1] = pygame.image.load(
            str(self.image_path / "nums" / "1.png")).convert_alpha()
        self.images[2] = pygame.image.load(
            str(self.image_path / "nums" / "2.png")).convert_alpha()
        self.images[3] = pygame.image.load(
            str(self.image_path / "nums" / "3.png")).convert_alpha()
        self.images[4] = pygame.image.load(
            str(self.image_path / "nums" / "4.png")).convert_alpha()
        self.images[5] = pygame.image.load(
            str(self.image_path / "nums" / "5.png")).convert_alpha()
        self.images[6] = pygame.image.load(
            str(self.image_path / "nums" / "6.png")).convert_alpha()
        self.images[7] = pygame.image.load(
            str(self.image_path / "nums" / "7.png")).convert_alpha()
        self.images[8] = pygame.image.load(
            str(self.image_path / "nums" / "8.png")).convert_alpha()
        self.images[9] = pygame.image.load(
            str(self.image_path / "nums" / "9.png")).convert_alpha()

        # поле
        self.images["GAME_BG"] = pygame.image.load(
            str(self.image_path / "blank.png")).convert_alpha()
        self.images["COVERED"] = pygame.image.load(
            str(self.image_path / "tiles" / "COVtile.png")).convert_alpha()
        self.images["COVERED"] = pygame.transform.scale(
            self.images["COVERED"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["FLAGGED"] = pygame.image.load(
            str(self.image_path / "tiles" / "FLAtile.png")).convert_alpha()
        self.images["FLAGGED"] = pygame.transform.scale(
            self.images["FLAGGED"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["UNCOVERED"] = pygame.image.load(
            str(self.image_path / "tiles" / "UNCtile.png")).convert_alpha()
        self.images["UNCOVERED"] = pygame.transform.scale(
            self.images["UNCOVERED"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["MINE"] = pygame.image.load(
            str(self.image_path / "tiles" / "MINtile.png")).convert_alpha()
        self.images["MINE"] = pygame.transform.scale(
            self.images["MINE"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["EXPLODED"] = pygame.image.load(
            str(self.image_path / "tiles" / "EXPtile.png")).convert_alpha()
        self.images["EXPLODED"] = pygame.transform.scale(
            self.images["EXPLODED"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["QUESTION"] = pygame.image.load(
            str(self.image_path / "tiles" / "QUEtile.png")).convert_alpha()
        self.images["QUESTION"] = pygame.transform.scale(
            self.images["QUESTION"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["T_1"] = pygame.image.load(
            str(self.image_path / "tiles" / "1.png")).convert_alpha()
        self.images["T_1"] = pygame.transform.scale(
            self.images["T_1"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["T_2"] = pygame.image.load(
            str(self.image_path / "tiles" / "2.png")).convert_alpha()
        self.images["T_2"] = pygame.transform.scale(
            self.images["T_2"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["T_3"] = pygame.image.load(
            str(self.image_path / "tiles" / "3.png")).convert_alpha()
        self.images["T_3"] = pygame.transform.scale(
            self.images["T_3"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["T_4"] = pygame.image.load(
            str(self.image_path / "tiles" / "4.png")).convert_alpha()
        self.images["T_4"] = pygame.transform.scale(
            self.images["T_4"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["T_5"] = pygame.image.load(
            str(self.image_path / "tiles" / "5.png")).convert_alpha()
        self.images["T_5"] = pygame.transform.scale(
            self.images["T_5"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["T_6"] = pygame.image.load(
            str(self.image_path / "tiles" / "6.png")).convert_alpha()
        self.images["T_6"] = pygame.transform.scale(
            self.images["T_6"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["T_7"] = pygame.image.load(
            str(self.image_path / "tiles" / "7.png")).convert_alpha()
        self.images["T_7"] = pygame.transform.scale(
            self.images["T_7"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["T_8"] = pygame.image.load(
            str(self.image_path / "tiles" / "8.png")).convert_alpha()
        self.images["T_8"] = pygame.transform.scale(
            self.images["T_8"], (self.TILE_SIZE, self.TILE_SIZE))
        self.images["WIN"] = pygame.image.load(
            str(self.image_path / "won.png")).convert_alpha()
        self.images["LOSE"] = pygame.image.load(
            str(self.image_path / "lost.png")).convert_alpha()

        """self.sounds["winMusic"] = pygame.mixer.Sound(
            str(self.sound_path / "success.ogg"))
        self.sounds["winMusic"].set_volume(0.2)
        self.sounds["gameOver"] = pygame.mixer.Sound(
            str(self.sound_path / "gameover.ogg"))

        self.sounds["juicy"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "juice.ogg"))

        # Winning remarks
        # "That's some mighty fine minesweeping"
        self.sounds["finesweeping"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "finesweeping.ogg"))
        # "Good job corpral"
        self.sounds["goodjob"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "goodjob.ogg"))
        # "You did it"
        self.sounds["youdidit"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "youdidit.ogg"))

        # Losing remarks
        # "Grrrrr"
        self.sounds["grr"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "grr.ogg"))
        # "Kraklglslask"
        self.sounds["merloc"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "merloc.ogg"))

        # Restart or game over "Aghhh"
        self.sounds["scream"] = pygame.mixer.Sound(
            str(self.sound_path / "scream.ogg"))"""

        self.loaded["game"] = True

    def load_data_options(self):
        # Options options
        '''self.images["RESET_LEADERBOARD"] = pygame.image.load(
            str(self.image_path / "options1.png")).convert_alpha()
        self.images["MUTE_SOUND"] = pygame.image.load(
            str(self.image_path / "options2.png")).convert_alpha()'''
        self.images["RETURN_TO_MENU"] = pygame.image.load(
            str(self.image_path / "rules.png")).convert_alpha()
        self.images["DONE_OVERLAY"] = pygame.image.load(
            str(self.image_path / "done.png")).convert_alpha()
        self.images["MUTED"] = pygame.image.load(
            str(self.image_path / "muted.png")).convert_alpha()
        self.images["UNMUTED"] = pygame.image.load(
            str(self.image_path / "unmuted.png")).convert_alpha()

        # "Vape Naysh y'all", options screen
        """self.sounds["vn"] = pygame.mixer.Sound(
            str(self.sound_path / "voice" / "vn.ogg"))"""

        self.loaded["options"] = True

    # def load_data_leaderboard(self):
    #     # Leaderboard
    #     self.images["LEADERBOARD_SCREEN"] = pygame.image.load(
    #         str(self.image_path / "blank.png")).convert_alpha()
    #     self.loaded["leaderboard"] = True

    def load_data_story(self):
        # Story
        self.images["STORY_SCREEN"] = pygame.image.load(
            str(self.image_path / "storyS.png")).convert_alpha()
        self.loaded["story"] = True

    def load_fonts(self):
        """Loads the fonts required for the game."""
        # TODO: make this cope with missing fonts!
        if 'andalemonottf' in pygame.font.get_fonts():
            self.font = pygame.font.SysFont('andalemonottf', 24)
        else:
            self.font = pygame.font.SysFont('lucidaconsole', 24)


if __name__ == "__main__":
    game = Game()
    game.loop()
