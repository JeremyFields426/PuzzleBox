import os
import math
import shutil
import random
import tkinter
from PIL import Image
import urllib.request


LOWER_BOUNDS = 4
UPPER_BOUNDS = 10
IMAGE_SIZE = (480, 270)

root = tkinter.Tk()
game_screen = None


class Tile:
    tile_objects = []
    tile_positions = []
    moves = 0

    def __init__(self, name, image, row, column):

        self.name = name
        self.image = image
        self.row = row
        self.column = column

        if self.name == "tile_25":
            self.relief = "flat"
        else:
            self.relief = "raised"

        self.tile = tkinter.Button(root, image = self.image, relief = self.relief, command = self.check_movement)
        self.tile.image = self.image
        self.tile.grid(row = self.row, column = self.column)

    @classmethod
    def randomize_tiles(cls, puzzle_size):
        for n in range(puzzle_size ** 2):
            blank_tile = cls.tile_objects[-1]
            blank_tile_row = blank_tile.row
            blank_tile_column = blank_tile.column
            moving_tile = None
            while moving_tile is None:
                    if random.choice(["r", "c"]) == "r":
                        if random.choice(["bottom", "top"]) == "bottom":
                            row = blank_tile_row + 1
                            column = blank_tile_column
                        else:
                            row = blank_tile_row - 1
                            column = blank_tile_column
                    else:
                        if random.choice(["left", "right"]) == "left":
                            row = blank_tile_row
                            column = blank_tile_column - 1
                        else:
                            row = blank_tile_row
                            column = blank_tile_column + 1

                    for tile_obj in cls.tile_objects:
                        if tile_obj.row == row and tile_obj.column == column:
                            moving_tile = tile_obj
                            break

            moving_tile.move_tiles(blank_tile, blank_tile_row, blank_tile_column)

    def check_movement(self):

        blank_tile = Tile.tile_objects[-1]
        blank_tile_row = blank_tile.row
        blank_tile_column = blank_tile.column

        if game_screen.start:
            if self.row + 1 == blank_tile_row and self.column == blank_tile_column:
                self.move_tiles(blank_tile, blank_tile_row, blank_tile_column)
            elif self.row == blank_tile_row and self.column + 1 == blank_tile_column:
                self.move_tiles(blank_tile, blank_tile_row, blank_tile_column)
            elif self.row -1 == blank_tile_row and self.column == blank_tile_column:
                self.move_tiles(blank_tile, blank_tile_row, blank_tile_column)
            elif self.row == blank_tile_row and self.column - 1 == blank_tile_column:
                self.move_tiles(blank_tile, blank_tile_row, blank_tile_column)

            Tile.moves += 1
            game_screen.moves_label["text"] = "Moves: " + str(Tile.moves)
            Tile.check_tiles()

    def move_tiles(self, blank_tile, blank_tile_row, blank_tile_column):

        blank_tile.row = self.row
        blank_tile.column = self.column
        self.row = blank_tile_row
        self.column = blank_tile_column

        self.tile.grid(row = self.row, column = self.column)
        blank_tile.tile.grid(row = blank_tile.row, column = blank_tile.column)

    @classmethod
    def check_tiles(cls):

        count = 0
        for i, tile_obj in enumerate(cls.tile_objects):
            rc = cls.tile_positions[i]
            if tile_obj.row == rc[0] and tile_obj.column == rc[1]:
                count += 1
                if count == len(cls.tile_objects):
                    game_screen.start = False
                    game_screen.game_status_label["text"] = "You Win!"
                    break
            else:
                break


class GameScreen:

    def __init__(self):
        root.title("Puzzle Box Game")

        self.start = False
        self.timer = None
        self.seconds = 0
        self.minutes = 0

        self.title_label = tkinter.Label(root, text = "Puzzle Box Configuration", pady = 5, fg = "purple")
        self.title_label.grid(row = 0, column = 0, columnspan = 3)

        self.puzzle_name_label = tkinter.Label(root, text = "Puzzle Name:", fg = "blue")
        self.puzzle_name_label.grid(row = 1, column = 0)

        self.puzzle_name_entry = tkinter.Entry(root)
        self.puzzle_name_entry.grid(row = 1, column = 2)

        self.URL_label = tkinter.Label(root, text = "URL Address/Image Name:", fg = "blue")
        self.URL_label.grid(row = 2, column = 0)

        self.URL_entry = tkinter.Entry(root)
        self.URL_entry.grid(row = 2, column = 2)

        self.puzzle_size_label = tkinter.Label(root, text = "Puzzle Size:", fg = "blue")
        self.puzzle_size_label.grid(row = 3, column = 0)

        self.puzzle_size_entry = tkinter.Entry(root)
        self.puzzle_size_entry.grid(row = 3, column = 2)

        self.error_label = tkinter.Label(root, fg = "red")
        self.error_label.grid(row = 4, column = 0, columnspan = 3)

        self.enter_button = tkinter.Button(root, text = "Create Puzzle", width = 40, command = main)
        self.enter_button.grid(row = 5, column = 0, columnspan = 3)

        self.puzzle_listbox = tkinter.Listbox(root, width = 28, selectmode = "single", activestyle = "dotbox")
        self.puzzle_listbox.grid(row = 6, column = 0, rowspan = 3, columnspan = 2)

        self.load_puzzle_button = tkinter.Button(root, text = "Load", width = 12, command = self.load_puzzle)
        self.load_puzzle_button.grid(row = 6, column = 2)

        self.remove_puzzle_button = tkinter.Button(root, text = "Remove", width = 12, command = self.remove_puzzle)
        self.remove_puzzle_button.grid(row = 8, column = 2)

        self.moves_label = tkinter.Label(root, text = "Moves: 0")

        self.time_label = tkinter.Label(root, text = "Time: 00:00")

        self.start_button = tkinter.Button(root, text = "Start", width = 13, pady = 10, command = self.start_game)

        self.game_status_label = tkinter.Label(root, text = "", fg = "green")

        self.change_puzzle_button = tkinter.Button(root, text = "Change Puzzle", width = 13, pady = 10,
                                                   command = self.show_config_menu)

    @classmethod
    def show_config_menu(cls):
        global game_screen

        for widget in root.grid_slaves():
            widget.grid_forget()

        Tile.tile_objects = []
        Tile.tile_positions = []
        game_screen = cls()
        game_screen.show_puzzle_list()

    def show_puzzle_list(self):
        if not os.path.isdir("puzzles"):
            os.mkdir("puzzles")
        else:
            self.puzzle_listbox.delete(0, "end")
            for puzzle in os.listdir("puzzles"):
                self.puzzle_listbox.insert("end", puzzle)

    def load_puzzle(self):
        if self.puzzle_listbox.curselection() != ():
            selected_puzzle = self.puzzle_listbox.get(self.puzzle_listbox.curselection())
            self.clear_fields()
            self.puzzle_name_entry.insert(0, selected_puzzle)
            main()

    def remove_puzzle(self):
        if self.puzzle_listbox.curselection() != ():
            selected_puzzle = self.puzzle_listbox.get(self.puzzle_listbox.curselection())
            shutil.rmtree("puzzles" + "/" + selected_puzzle)
            self.show_puzzle_list()

    def clear_fields(self):
        self.puzzle_name_entry.delete(0, "end")
        self.URL_entry.delete(0, "end")
        self.puzzle_size_entry.delete(0, "end")

    def check_fields(self):
        # -1: failure
        # 0: use puzzle name
        # 1: use puzzle name + "puzzle"
        # 2: use url
        # 3: use saved image

        # Checks first field
        if ("puzzle" in self.puzzle_name_entry.get() and \
                os.path.isdir("puzzles" + "/" + self.puzzle_name_entry.get())):
            self.mode = 0
            return True
        if ("puzzle" not in self.puzzle_name_entry.get() and \
                os.path.isdir("puzzles" + "/" +  self.puzzle_name_entry.get() + " " + "puzzle")):
            self.mode = 1
            return True
        if " " in self.puzzle_name_entry.get() or not self.puzzle_name_entry.get().isalpha():
            self.mode = -1
            self.error_label["text"] = "Puzzle name must be just letters (no spaces)"
            return False

        # Checks second field
        try:
            urllib.request.urlretrieve(self.URL_entry.get())
            self.mode = 2
        except (urllib.error.URLError, ValueError):
            if (os.path.isfile(self.URL_entry.get()) or \
                    os.path.isfile("puzzles" + "/" + self.URL_entry.get())):
                self.mode = 3
            else:
                self.mode = -1
                self.error_label["text"] = "URL or image name is invalid"
                return False

        # Checks third field
        if not self.puzzle_size_entry.get().isdigit():
            self.mode = -1
            self.error_label["text"] = "Puzzle size must be a number"
            return False
        elif not LOWER_BOUNDS <= int(self.puzzle_size_entry.get()) <= UPPER_BOUNDS:
            self.mode = -1
            self.error_label["text"] = "Puzzle size must be between " + \
                                       str(LOWER_BOUNDS) + " and " + str(UPPER_BOUNDS) + \
                                       " inclusive"
            return False

        return True

    def get_paths(self):
        if self.mode == 0:
            puzzle_directory_path = "puzzles" + "/" + self.puzzle_name_entry.get()
            puzzle_template_path = puzzle_directory_path + "/" + self.puzzle_name_entry.get()[:-7] + ".gif"
            tile_directory_path = puzzle_directory_path + "/" + "tiles"
        elif self.mode in [1, 2]:
            puzzle_directory_path = "puzzles" + "/" + self.puzzle_name_entry.get() + " " + "puzzle"
            puzzle_template_path = puzzle_directory_path + "/" + self.puzzle_name_entry.get() + ".gif"
            tile_directory_path = puzzle_directory_path + "/" + "tiles"
        elif self.mode == 3:
            puzzle_directory_path = "puzzles" + "/" + self.puzzle_name_entry.get() + " " + "puzzle"
            puzzle_template_path = puzzle_directory_path + "/" + self.URL_entry.get()
            tile_directory_path = puzzle_directory_path + "/" + "tiles"

        return puzzle_directory_path, puzzle_template_path, tile_directory_path

    def get_puzzle_size(self, tile_directory_path):
        if self.mode in [0, 1]:
            tile_amount = int(len(os.listdir(tile_directory_path)))
            puzzle_size = int(math.sqrt(tile_amount))
        elif self.mode in [2, 3]:
            puzzle_size = int(self.puzzle_size_entry.get())

        return puzzle_size

    def scrub_image(self, puzzle_directory_path, puzzle_template_path, tile_directory_path):
        os.mkdir(puzzle_directory_path)
        os.mkdir(tile_directory_path)

        if self.mode == 2:
            urllib.request.urlretrieve(self.URL_entry.get(), puzzle_template_path)
        elif self.mode == 3:
            if (os.path.isfile(self.URL_entry.get())):
                shutil.move(self.URL_entry.get(), puzzle_template_path)
            elif os.path.isfile("puzzles" + "/" + self.URL_entry.get()):
                shutil.move("puzzles" + "/" + self.URL_entry.get(), puzzle_template_path)

    def get_tile_size(self, puzzle_directory_path, puzzle_template):
        puzzle_width, puzzle_height = puzzle_template.size
        if puzzle_width >= puzzle_height:
            puzzle_template = puzzle_template.resize((puzzle_width, puzzle_width))
        else:
            puzzle_template = puzzle_template.resize((puzzle_height, puzzle_height))

        puzzle_template.save(puzzle_directory_path + "/" + "re-sized_template.gif")
        tile_size = puzzle_width / int(self.puzzle_size_entry.get())

        return puzzle_template, tile_size

    def split_image(self, tile_directory_path, puzzle_template, tile_names, puzzle_size, tile_size):
        num_tiles = 0
        for row in range(puzzle_size):
            for column in range(puzzle_size):

                top_left_x = column * tile_size
                top_left_y = row * tile_size
                bottom_right_x = top_left_x + tile_size
                bottom_right_y = top_left_y + tile_size

                bounds = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
                tile_path = tile_directory_path + "/" + tile_names[num_tiles]
                puzzle_template.crop(bounds).save(tile_path)

                num_tiles += 1

        self.clear_tile(tile_path)

    @staticmethod
    def clear_tile(tile_path):
        blank_tile = Image.open(tile_path).convert("RGBA")
        pixels = blank_tile.load()
        for j in range(blank_tile.size[0]):
            for i in range(blank_tile.size[1]):
                pixels[j, i] = (239, 246, 245)
        blank_tile.save(tile_path)

    def show_game_menu(self, puzzle_size):
        for widget in root.grid_slaves():
            widget.grid_forget()

        self.title_label["text"] = "Puzzle Box Game"
        self.title_label.grid(row = 0, column = 0, columnspan = puzzle_size)
        self.moves_label.grid(row = 0, column = 0, columnspan = 2)
        self.time_label.grid(row = 0, column = puzzle_size - 2, columnspan = 2)
        self.start_button.grid(row = 1, column = 0, columnspan = 2)
        self.game_status_label.grid(row = 1, column = 0, columnspan = puzzle_size)
        self.change_puzzle_button.grid(row = 1, column = puzzle_size - 2, columnspan = 2)

    def start_game(self):
        self.start = True
        self.start_button["text"] = "Restart"
        self.game_status_label["text"] = "Game in Progress..."
        self.seconds = 0
        self.minutes = 0
        if self.timer is None:
            self.update_clock()
        else:
            root.after_cancel(self.timer)
            self.update_clock()

        puzzle_size = self.get_puzzle_size(self.get_paths()[2]) ** 2
        Tile.randomize_tiles(puzzle_size)
        Tile.moves = 0
        self.moves_label["text"] = "Moves: " + str(Tile.moves)

    def update_clock(self):
        if self.start:

            self.seconds += 1
            if self.seconds == 60:
                self.minutes += 1
                self.seconds = 0

            if len(str(self.seconds)) == 1:
                seconds = "0" + str(self.seconds)
            else:
                seconds = str(self.seconds)

            if len(str(self.minutes)) == 1:
                minutes = "0" + str(self.minutes)
            else:
                minutes = str(self.minutes)

            self.time_label["text"] = "Time: " + minutes + ":" + seconds
            self.timer = root.after(1000, self.update_clock)


def create_attributes(tile_directory_path, tile_name, puzzle_size):
    tile_num = int(tile_name[5:-4]) - 1
    image = tkinter.PhotoImage(file = tile_directory_path + "/" + tile_name)
    row = 2
    count = 0
    for n in range(tile_num):
        count += 1
        if count % puzzle_size == 0 and n != tile_num:
            row += 1
            count = 0
    column = count % puzzle_size

    Tile.tile_positions += [(row, column)]
    return image, row, column


def create_tile_objects(tile_directory_path, tile_names, puzzle_size):
    for tile_name in tile_names:
        tile_image, tile_row, tile_column = create_attributes(tile_directory_path, tile_name, puzzle_size)
        tile_obj = Tile(tile_name, tile_image, tile_row, tile_column)
        Tile.tile_objects += [tile_obj]


def main():
    if game_screen.check_fields():

        paths = game_screen.get_paths()
        puzzle_directory_path = paths[0]
        puzzle_template_path = paths[1]
        tile_directory_path = paths[2]

        puzzle_size = game_screen.get_puzzle_size(tile_directory_path)
        game_screen.show_game_menu(puzzle_size)

        tile_names = []
        for n in range(puzzle_size ** 2):
            tile_names += ["tile" + "_" + str(n + 1) + ".gif"]

        if game_screen.mode in [0, 1]:
            create_tile_objects(tile_directory_path, tile_names, puzzle_size)

        elif game_screen.mode in [2, 3]:
            # Save an image to to the first directory from either a URL or an image path
            game_screen.scrub_image(puzzle_directory_path, puzzle_template_path, tile_directory_path)
            # Create the image that was saved previously
            puzzle_template = Image.open(puzzle_template_path).resize(IMAGE_SIZE)
            # Change the template to be a perfect square and return the new tile size
            puzzle_template, tile_size = game_screen.get_tile_size(puzzle_directory_path, puzzle_template)
            # Create/save all of the images for the tiles and get their names
            game_screen.split_image(tile_directory_path, puzzle_template, tile_names, puzzle_size, tile_size)
            # Make an instance of the Tile class for all of the tile images
            create_tile_objects(tile_directory_path, tile_names, puzzle_size)
    else:
        game_screen.clear_fields()


GameScreen.show_config_menu()
root.mainloop()
