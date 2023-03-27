import tkinter as tk
from PIL import Image, ImageTk
from random import randint
from time import sleep
import math

# game is going to be in 1920x1080 resolution
# screen made up of square that are 60x60
# this means that there will be 32 columns and 18 rows
GAME_WIDTH = int(1920)
GAME_HEIGHT = int(1080)
TILE_SIZE = 60
# Base images from: https://dpaige1991.itch.io/colored-cars
# Images used are slightly edited by me (Awab Akram)
CAR_IMAGE_LIST_RIGHT = ["./assets/WhiteCarRight.png", "./assets/RedCarRight.png",
                        "./assets/BlueCarRight.png", "./assets/OrangeCarRight.png", "./assets/GreenCarRight.png"]
CAR_IMAGE_LIST_LEFT = ["./assets/WhiteCarLeft.png", "./assets/RedCarLeft.png",
                       "./assets/BlueCarLeft.png", "./assets/OrangeCarLeft.png", "./assets/GreenCarLeft.png"]

bg_colour = "#e06377"

Controls = ['<Up>', '<Down>', '<Left>', '<Right>', '<p>', '<b>', '<s>', 'l']
score = 0
level = 1
player = None
rows = None
game_over = False
game_loop_after = None
gameFrame = None
gameCanvas = None
score_text = None
level_text = None
paused = False
pause_label = None
bossed = False
boss_key_label = None
saving = False
save_box = None
loading = False
load_box = None
leaderboard_label = None

invincibility = False
point_multiplier = 1


class Rectangle():
    """Class to represent a basic rectangle, 
    this will be used as I imagine everything as squares/rectangles"""

    def __init__(self, x, y, width, height, default_pic: tk.PhotoImage):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.prev_x = x
        self.prev_y = y
        self.current_image = default_pic
        self.label = tk.Label()

    def paint(self, canvas: tk.Canvas):
        """Method to actually show the rectangle on screen"""
        self.label.destroy()
        self.label = tk.Label(canvas, image=self.current_image)
        self.label.place(x=self.x, y=self.y)

    def intersects(self, other_rectangle):
        """Checks if this rectangle is interecting with a given other rectangle"""
        # check if theyre intersecting
        # If this's left edge is to the right of the other's right edge and
        # If this's right edge is to the left of the other's left edge and
        # If this's top edge is below other's bottom edge and
        # If this's bottom edge is above other's top edge
        if self.x < other_rectangle.x + other_rectangle.width and self.x + self.width > other_rectangle.x and self.y < other_rectangle.y + other_rectangle.height and self.y + self.height > other_rectangle.y:
            intersecting = True
        else:
            intersecting = False
        return intersecting


class Player(Rectangle):
    """Class to represent the player"""

    def __init__(self, x, y, width, height, default_pic: tk.PhotoImage):
        super().__init__(x, y, width, height, default_pic)
        # Images from: https://artsybarrels.itch.io/cute-character-base
        # Load looking down image
        image_down = Image.open("./assets/lookingDown.png")
        self.image_down = ImageTk.PhotoImage(image_down)
        # Load looking up image
        image_up = Image.open("./assets/lookingUp.png")
        self.image_up = ImageTk.PhotoImage(image_up)
        # Load looking left image
        image_left = Image.open("./assets/lookingLeft.png")
        self.image_left = ImageTk.PhotoImage(image_left)
        # Load looking right image
        image_right = Image.open("./assets/lookingright.png")
        self.image_right = ImageTk.PhotoImage(image_right)

    def move(self, control_pressed):
        """Method to handle the movement of the player"""
        global score, point_multiplier
        if control_pressed == 'Up':
            if not (self.y - TILE_SIZE < 0):
                self.prev_y = self.y
                self.y -= TILE_SIZE
                self.current_image = self.image_up
                score += level * point_multiplier
        if control_pressed == 'Down':
            if not (self.y + TILE_SIZE + self.height > GAME_HEIGHT):
                self.prev_y = self.y
                self.y += TILE_SIZE
                self.current_image = self.image_down
                score -= level * point_multiplier
        if control_pressed == 'Left':
            if not (self.x - TILE_SIZE < 0):
                self.prev_x = self.x
                self.x -= TILE_SIZE
                self.current_image = self.image_left
        if control_pressed == 'Right':
            if not (self.x + TILE_SIZE + self.width > GAME_WIDTH):
                self.prev_x = self.x
                self.x += TILE_SIZE
                self.current_image = self.image_right


class Car(Rectangle):
    """Class to represent a car"""

    def __init__(self, x, y, width, height, default_pic: tk.PhotoImage, speed):
        super().__init__(x, y, width, height, default_pic)
        self.speed = speed

    def move(self):
        """Function to gangle the movement of the car"""
        self.prev_x = self.x
        self.x += self.speed
        # if its moving to the left
        if self.speed < 0:
            # if it goes off the screen, bounce it back to the start position
            if self.x < 0:
                self.x = GAME_WIDTH
        elif self.speed > 0:
            if self.x > GAME_WIDTH:
                self.x = 0


class Row():
    """Represents 1 row in the game, 
    row can be either a 'Grass' row or a 'Road' row"""

    def generate_car(self):
        """Generates a single car based on the other attributes of the row"""
        y = self.y
        width = 60
        height = 40
        if self.direction == "L-R":
            x = 0
            rng_car_pic = randint(0, len(CAR_IMAGE_LIST_RIGHT)-1)
            image = tk.PhotoImage(file=CAR_IMAGE_LIST_RIGHT[rng_car_pic])
            speed = self.row_speed
            self.cars.append(Car(x, y, width, height, image, speed))
        elif self.direction == "R-L":
            x = GAME_WIDTH
            rng_car_pic = randint(0, len(CAR_IMAGE_LIST_LEFT)-1)
            image = tk.PhotoImage(file=CAR_IMAGE_LIST_LEFT[rng_car_pic])
            speed = -1 * self.row_speed
            self.cars.append(Car(x, y, width, height, image, speed))

    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.cars = []
        # determine type of row
        if type is None:
            row_type_number = randint(0, 100)
            # > if i want to make it go hard to easy, < if i want it normal
            if row_type_number < (level*2):
                self.row_type = "Road"
            else:
                self.row_type = "Grass"
        else:
            self.row_type = type

        # Load appropriate image
        if self.row_type == "Road":
            image_row = Image.open("./assets/Road.png")
        elif self.row_type == "Grass":
            image_row = Image.open("./assets/Grass.png")
        self.image = ImageTk.PhotoImage(image_row)

        # detrmine row direction
        if self.row_type != "Grass":
            direction_num = randint(0, 1)
            if direction_num == 0:
                self.direction = "R-L"
            else:
                self.direction = "L-R"

        if self.row_type == "Road":
            # Determine number of cars
            # cars are maxxed out to 5 - could be between 1 and 5 per row
            max_cars = level
            if max_cars > 5:
                max_cars = 5
            self.num_of_cars = randint(1, max_cars)
            self.row_speed = randint(2, level * 2)

            # generate the first car
            self.generate_car()

    def paint(self, canvas: tk.Canvas):
        """Draws the row."""
        # tk.Label(canvas,image=self.image).place(x=self.x,y=self.y)
        canvas.create_image(self.x, self.y, image=self.image, anchor="nw")

    def paint_cars(self, canvas: tk.Canvas):
        """Paints all of the cars in the row"""
        for car in self.cars:
            car.paint(canvas)

    def move_cars(self):
        """Moves every car in the row"""
        for car in self.cars:
            car.move()

    def check_for_new_car(self):
        """This method decides whether or not a new car should be generated"""
        if self.row_type == "Grass":
            return
        # only generate a car if its not hit the max for the row
        if len(self.cars) < self.num_of_cars:
            if self.direction == "L-R":
                if self.cars[-1].x > TILE_SIZE*2:
                    rng_car = randint(0, 1000)
                    if rng_car < (level*2):
                        self.generate_car()
            elif self.direction == "R-L":
                if self.cars[-1].x < GAME_WIDTH - TILE_SIZE*2:
                    rng_car = randint(0, 1000)
                    if rng_car < (level*2):
                        self.generate_car()


def switch_frames(old_frame: tk.Frame, new_frame: tk.Frame):
    """switches from one frame to another"""
    old_frame.pack_forget()
    new_frame.config(background=bg_colour)
    new_frame.pack(fill="both", expand=True)


def bind_controls(Window: tk.Tk):
    """Binds all of the controls to move the player"""
    Window.bind(Controls[0], lambda event: player.move("Up"))
    Window.bind(Controls[1], lambda event: player.move("Down"))
    Window.bind(Controls[2], lambda event: player.move("Left"))
    Window.bind(Controls[3], lambda event: player.move("Right"))
    Window.bind(Controls[4], lambda event: pause())
    Window.bind(Controls[5], lambda event: boss_key())
    Window.bind(Controls[6], lambda event: save())
    Window.bind(Controls[7], lambda event: load())


def setup_rows():
    """Sets up all of the rows. Saves them to a list called rows
    the top row is at index 0 of the list"""
    rows = []
    rows.append(Row(0, 0, "Grass"))
    for i in range(1, 17):
        rows.append(Row(0, (i*TILE_SIZE), None))
    rows.append(Row(0, 1020, "Grass"))
    return rows


def check_next_level():
    """Checks if the player is on the top row, indicating a new level should be generated"""
    global player, level
    if player.y < 60:
        level += 1
        reset_board()


def reset_board():
    """Completely resets the whole game grid, including reseting the rows, the cars within the rows and the player position, also updates the level and score"""
    global player, rows, score_text, level_text
    # destroy all of the cars in the rows first
    for row in rows:
        for car in row.cars:
            car.label.destroy()
    # setup the rows again
    rows = setup_rows()
    for row in rows:
        row.paint(gameCanvas)
    # reset player position
    player.y = 1030
    player.x = 960
    # reset the score and level displays
    gameCanvas.delete(score_text)
    gameCanvas.delete(level_text)
    score_text = gameCanvas.create_text(
        100, 20, text=f"Score: {score}", font=("Comic Sans MS", 20))
    level_text = gameCanvas.create_text(
        1800, 20, text=f"Level: {level}", font=("Comic Sans MS", 20))


def check_for_collisions():
    """Checks for collisions between the player and any cars in the row that the player is currently in"""
    global player, rows, game_over
    row_num = math.trunc(player.y / TILE_SIZE)
    for car in rows[row_num].cars:
        if player.intersects(car):
            game_over = True


def game_over_handler():
    """Handles the game over screen as well as writing to the leaderboard if nessicarry"""
    gameCanvas.destroy()
    game_over_label = tk.Label(gameFrame, text="Game Over!", font=(
        "Arial", 40), foreground="red", background="black")
    # game_over_label.place(x=(GAME_WIDTH/2 - game_over_label.winfo_width()/2),y=(GAME_HEIGHT/2 - game_over_label.winfo_height()/2))
    game_over_label.pack(side="top", pady=(GAME_HEIGHT/2, 0))
    enter_name_label = tk.Label(gameFrame, text="Enter name: ", font=(
        "Arial", 20), foreground="white", background="black")
    name_box = tk.Entry(gameFrame, font=("Arial", 20))
    enter_name_label.pack(side="top", pady=(25, 0))
    name_box.pack(side="top", pady=(5, 5))
    back_to_main_menu_button = tk.Button(gameFrame, text="Back to main menu", font=("Comic Sans MS", 15),
                                         foreground="pink", background="azure", command=lambda: back_to_main_menu(name_box.get()))
    back_to_main_menu_button.pack(side="top")


def back_to_main_menu(name: str):
    """Checks if the leaderboard must be updated, updates it if it does, and then goes back to the main menu"""
    global score
    update_leaderboard(score, name)
    switch_frames(gameFrame, Main_Menu_Frame)


def update_leaderboard(score: int, name: str):
    """Main Method to update leaderboard at the end of the game"""
    # open the leaderboard file and read the current names on it
    file = open("Leaderboard.txt")
    lines = file.readlines()
    file.close
    # split up the cores and the names so that they can be sorted by score,
    # have to make sure that the names are still associated with the appropiate score
    for i in range(len(lines)):
        lines[i] = lines[i].split(',')
    new_lines = []
    for line in lines:
        save_tupple = (int(line[0]), line[1].rstrip('\n'))
        new_lines.append(save_tupple)
    # add the new score into the mix
    new_lines.append((score, name))
    # sort the scores
    new_lines.sort(key=lambda a: a[0], reverse=True)
    # write the top 5 scores back to the file
    file = open("Leaderboard.txt", "w")
    for i in range(0, 5):
        save_string = f"{new_lines[i][0]},{new_lines[i][1]}\n"
        file.write(save_string)
    file.close()


def game_loop():
    """Main loop for game"""
    global score_text, level_text, game_loop_after
    if game_over is True:
        game_over_handler()
        game_loop_after.after_cancel()
    else:
        for row in rows:
            row.check_for_new_car()
            row.move_cars()
            row.paint_cars(gameCanvas)
        if invincibility is False:
            check_for_collisions()
        check_next_level()
        player.paint(gameCanvas)
    game_loop_after = Window.after(40, game_loop)


def run_game():
    """Method to start the game for the first time"""
    global score, level, player, rows, gameCanvas, gameFrame, score_text, level_text
    # bind the controls:
    bind_controls(Window)
    # Make a new game frame and game canvas
    gameFrame = tk.Frame(Window, height=1080, width=1920)
    gameCanvas = tk.Canvas(gameFrame, height=1080, width=1920)
    gameFrame.config(background="black")
    gameCanvas.config(background="black")
    # Hide the main menu page, show the game frame
    switch_frames(Main_Menu_Frame, gameFrame)
    gameCanvas.pack(fill="both", expand=True)
    # Button to end the game voluntarily
    end_game_button = tk.Button(gameCanvas, text="End Game", font=(
        "Comic Sans MS", 15), foreground="#622569", background="#b8a9c9", width=20, command=lambda: game_over_handler())
    end_game_button.place(x=400, y=5)
    # Button to go to main menu
    main_menu_button_game = tk.Button(gameCanvas, text="Main Menu", font=(
        "Comic Sans MS", 15), foreground="#622569", background="#b8a9c9", width=20, command=lambda: switch_frames(gameFrame, Main_Menu_Frame))
    main_menu_button_game.place(x=1200, y=5)
    # reset the score and level
    score = 0
    level = 1
    # Make the player
    player_img = tk.PhotoImage(file="./assets/lookingDown.png")
    player = Player(960, 1030, 32, 32, player_img)
    # set up the rows for the game
    rows = setup_rows()
    for row in rows:
        row.paint(gameCanvas)
    # display score and level
    score_text = gameCanvas.create_text(
        100, 20, text=f"Score: {score}", font=("Comic Sans MS", 20))
    level_text = gameCanvas.create_text(
        1800, 20, text=f"Level: {level}", font=("Comic Sans MS", 20))
    # enter the game loop
    game_loop()


def pause():
    """Method to pause the game"""
    global paused, pause_label
    paused = not paused
    if paused == True:
        Window.after_cancel(game_loop_after)
        Window.unbind(Controls[0])
        Window.unbind(Controls[1])
        Window.unbind(Controls[2])
        Window.unbind(Controls[3])
        pause_image = tk.PhotoImage(file="./assets/Pause.png")
        pause_label = tk.Label(gameCanvas, image=pause_image)
        pause_label.photo = pause_image
        pause_label.place(x=GAME_WIDTH/2 - 25, y=GAME_HEIGHT/2 - 25)
    else:
        pause_label.destroy()
        game_loop()
        bind_controls(Window)


def boss_key():
    """Method for the Boss key functionality"""
    global bossed, boss_key_label
    bossed = not bossed
    if bossed == True:
        Window.after_cancel(game_loop_after)
        Window.unbind(Controls[0])
        Window.unbind(Controls[1])
        Window.unbind(Controls[2])
        Window.unbind(Controls[3])
        boss_image = tk.PhotoImage(file="./assets/BossKeyPic.png")
        boss_key_label = tk.Label(gameCanvas, image=boss_image)
        boss_key_label.photo = boss_image
        boss_key_label.place(x=0, y=0)
    else:
        boss_key_label.destroy()
        game_loop()
        bind_controls(Window)


def save():
    """Handles the saving of the files
    files are saved in the format score,level"""
    global saving, save_box
    if saving is False:
        saving = True
        save_box = tk.Entry(gameCanvas, font=("Comic Sans MS", 15))
        save_box.place(x=GAME_WIDTH/2, y=GAME_HEIGHT /
                       2 + 100, width=200, height=50)
    else:
        saving = False
        file_name = save_box.get().rstrip('s')
        save_box.destroy()
        file = open(f"./savefiles/{file_name}.txt", "w")
        file.write(F"{score},{level}")
        file.close()


def load():
    """Handles the loading of the files
    files are saved in the format score,level"""
    global loading, load_box, score, level
    if loading == False:
        loading = True
        load_box = tk.Entry(gameCanvas, font=("Comic Sans MS", 15))
        load_box.place(x=GAME_WIDTH/2, y=GAME_HEIGHT /
                       2 + 100, width=200, height=50)
    else:
        loading = False
        file_name = load_box.get().rstrip('l')
        load_box.destroy()
        file = open(f"./savefiles/{file_name}.txt", "r")
        line = file.readline()
        file.close()
        split_line = line.split(',')
        score = int(split_line[0])
        level = int(split_line[1])
        reset_board()


def load_leaderboard():
    """Handles the loading of the leaderboard"""
    global leaderboard_label
    output_string = "Score: Name\n"
    file = open("Leaderboard.txt")
    lines = file.readlines()
    file.close
    for i in range(len(lines)):
        lines[i] = lines[i].split(',')
    new_lines = []
    for line in lines:
        save_tupple = (int(line[0]), line[1].rstrip('\n'))
        new_lines.append(save_tupple)
    nl_char = '\n'
    for pair in new_lines:
        output_string += f"{pair[0]}: {pair[1]}{nl_char}"
    leaderboard_label = tk.Label(Leaderboard_Frame, text=output_string, font=(
        "Comic Sans MS", 40), background=bg_colour)
    leaderboard_label.place(x=700, y=200)


def change_background_colour(new_colour):
    """Changes the background colour of the menu to the pecified colour"""
    global bg_colour
    bg_colour = new_colour
    Change_Background_Colour_Frame.config(background=bg_colour)


def process_cheat_code(code):
    """Method to check if any valid cheat codes have been entered, and activate the relevant cheats when they are entered"""
    global invincibility, point_multiplier
    if code == "Invincibility":
        invincibility = not invincibility
    if code == "Double Points":
        if point_multiplier == 2:
            point_multiplier = 1
        else:
            point_multiplier = 2
    if code == "Triple Points":
        if point_multiplier == 3:
            point_multiplier = 1
        else:
            point_multiplier = 3
    if code == "Half Points":
        if point_multiplier == 0.5:
            point_multiplier = 1
        else:
            point_multiplier = 0.5


# Making the window
Window = tk.Tk()
Window.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT}")
Window.attributes("-fullscreen", True)

# Main Menu Frame
Main_Menu_Frame = tk.Frame(Window, height=GAME_HEIGHT, width=GAME_WIDTH)
Main_Menu_Frame.config(background=bg_colour)
title_image = tk.PhotoImage(file="./assets/TitleImage.png")
title_image_label = tk.Label(Main_Menu_Frame, image=title_image)
Play_Button = tk.Button(Main_Menu_Frame, text="Play Game", font=("Comic Sans MS", 20),
                        foreground="#622569", background="#b8a9c9", width=20, command=lambda: run_game())
Main_Menu_Frame.pack(fill="both", expand=True)
title_image_label.pack(side="top", pady=(250, 0))
Play_Button.pack(side="top")
leaderboard_button = tk.Button(Main_Menu_Frame, text="Leaderboard", font=("Comic Sans MS", 20), foreground="#622569",
                               background="#b8a9c9", width=20, command=lambda: switch_frames(Main_Menu_Frame, Leaderboard_Frame))
leaderboard_button.pack(side="top")
Settings_button = tk.Button(Main_Menu_Frame, text="Settings", font=("Comic Sans MS", 20), foreground="#622569",
                            background="#b8a9c9", width=20, command=lambda: switch_frames(Main_Menu_Frame, Settings_Frame))
Settings_button.pack(side="top")

# Leaderboard Frame
Leaderboard_Frame = tk.Frame(Window, height=GAME_HEIGHT, width=GAME_WIDTH)
Leaderboard_Frame.config(background=bg_colour)
leaderboard_label = tk.Label(Leaderboard_Frame, text="Score: Name", font=(
    "Comic Sans MS", 40), background=bg_colour)
leaderboard_label.place(x=700, y=200)
load_leaderboard_button = tk.Button(Leaderboard_Frame, text="Load Leaderboard", font=(
    "Comic Sans MS", 20), foreground="#622569", background="#b8a9c9", width=20, command=lambda: load_leaderboard())
load_leaderboard_button.place(x=30, y=20)
Main_Menu_button = tk.Button(Leaderboard_Frame, text="Main Menu", font=("Comic Sans MS", 20), foreground="#622569",
                             background="#b8a9c9", width=20, command=lambda: switch_frames(Leaderboard_Frame, Main_Menu_Frame))
Main_Menu_button.place(x=1500, y=20)

# Settings Frame
Settings_Frame = tk.Frame(Window, height=GAME_HEIGHT, width=GAME_WIDTH)
Settings_Frame.config(background=bg_colour)
Main_Menu_button_settings = tk.Button(Settings_Frame, text="Main Menu", font=(
    "Comic Sans MS", 20), foreground="#622569", background="#b8a9c9", width=20, command=lambda: switch_frames(Settings_Frame, Main_Menu_Frame))
change_background_colour_button = tk.Button(Settings_Frame, text="Change Background Colour", font=(
    "Comic Sans MS", 20), foreground="#622569", background="#b8a9c9", width=20, command=lambda: switch_frames(Settings_Frame, Change_Background_Colour_Frame))
cheat_code_entry = tk.Entry(Settings_Frame, font=(
    "Comic Sans MS", 30), foreground="#622569", background="#b8a9c9")
cheat_code_button = tk.Button(Settings_Frame, text="Submit cheat code", font=(
    "Comic Sans MS", 20), foreground="#622569", background="#b8a9c9", width=20, command=lambda: process_cheat_code(cheat_code_entry.get()))
Main_Menu_button_settings.pack(side="top", pady=(300, 50))
change_background_colour_button.pack(side="top")
cheat_code_entry.pack(side="top", pady=(20, 10))
cheat_code_button.pack(side="top")

# Change background colour Frame
Change_Background_Colour_Frame = tk.Frame(
    Window, height=GAME_HEIGHT, width=GAME_WIDTH)
Change_Background_Colour_Frame.config(background=bg_colour)
Settings_button_Change_colour = tk.Button(Change_Background_Colour_Frame, text="Settings", font=(
    "Comic Sans MS", 20), foreground="#622569", background="#b8a9c9", width=20, command=lambda: switch_frames(Change_Background_Colour_Frame, Settings_Frame))
Change_bg_Red = tk.Button(Change_Background_Colour_Frame, text="Red", font=("Comic Sans MS", 20),
                          foreground="#622569", background="#b8a9c9", width=20, command=lambda: change_background_colour("#e06377"))
Change_bg_Blue = tk.Button(Change_Background_Colour_Frame, text="Blue", font=(
    "Comic Sans MS", 20), foreground="#622569", background="#b8a9c9", width=20, command=lambda: change_background_colour("#5b9aa0"))
Change_bg_Yellow = tk.Button(Change_Background_Colour_Frame, text="Yellow", font=(
    "Comic Sans MS", 20), foreground="#622569", background="#b8a9c9", width=20, command=lambda: change_background_colour("#FCCE00"))
Change_bg_Green = tk.Button(Change_Background_Colour_Frame, text="Green", font=(
    "Comic Sans MS", 20), foreground="#622569", background="#b8a9c9", width=20, command=lambda: change_background_colour("#738926"))
Settings_button_Change_colour.pack(side="top", pady=(300, 50))
Change_bg_Red.pack(side="top")
Change_bg_Blue.pack(side="top")
Change_bg_Yellow.pack(side="top")
Change_bg_Green.pack(side="top")

# Game frame
gameFrame = tk.Frame(Window, height=1080, width=1920)
gameCanvas = tk.Canvas(gameFrame, height=1080, width=1920)
gameFrame.config(background="black")
gameCanvas.config(background="black")


Window.mainloop()
