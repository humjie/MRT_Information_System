# Hu Ming Jie U2420530K MA5

import turtle
import sys
from functools import partial

##### getting data

# read in data from MRT.txt and store in MRT_data
def get_MRT_data():
    MRT_data = {}
    try:
        with open("MRT.txt", "r") as file:
            for line_num, line in enumerate(file):
                if line_num == 2:
                    for name in line.strip().split(";"):
                        MRT_data[name] = []
                    MRT_data["code_pair"] = []
                    MRT_data["name_pair"] = []
                if line_num > 2 and line != "\n":
                    temp_data_list = line.strip().split(";")
                    temp_data_list[1] = temp_data_list[1].split(" <-> ")

                    # add two more data, which are code pair and name pair into the dictionary
                    code_pair = []
                    name_pair = []
                    for i in range(2):
                        code = ""
                        name = ""
                        for c in temp_data_list[1][i]:
                            if c != " ":
                                code += c
                            elif c == " ":
                                name = temp_data_list[1][i][len(code)+1:]
                                break
                        code_pair.append(code)
                        name_pair.append(name)
                    temp_data_list.append(code_pair)
                    temp_data_list.append(name_pair)

                    keys_list = list(MRT_data.keys())
                    for key in keys_list:
                        MRT_data[key].append(temp_data_list[keys_list.index(key)])

    # exit the program if can't find the file          
    except FileNotFoundError:
        sys.exit("MRT.txt file not found! Please add the file in same directory before running the program.")

    # add speed into MRT_data
    speed = {"North-South": 41, "East-West": 43, "Circle": 36, "Thomson-East Coast": 40, "North East": 34, "Downtown": 38}
    MRT_data["Speed"] = [speed[i] for i in MRT_data["Line"]]

    return MRT_data

# read in data from FareStructure.txt and store in Fare_data
def get_Fare_data():
    Fare_data = {"Adult Fare": {"Distance": [], "Card Fare Per Ride (cents)": []}, "Senior Citizen / Persons with Disabilities Fare": {"Distance": [], "Card Fare Per Ride (cents)": []}, "Student Fare": {"Distance": [], "Card Fare Per Ride (cents)": []}}
    try:
        with open("FareStructure.txt", "r") as file:
            lines = file.readlines()
            lines.pop(0)
            fare_key_list = [key for key in Fare_data]
            key = -1
            current_key = ""
            while key < 3:
                if lines[0] == "\n":
                    key += 1
                    if key >= 3:
                        break
                    current_key = fare_key_list[key]
                    for _ in range(3):
                        lines.pop(0)
                    continue
                else:
                    distance, fare = lines[0].strip().split(";")
                    Fare_data[current_key]["Distance"].append(distance)
                    Fare_data[current_key]["Card Fare Per Ride (cents)"].append(fare)
                    lines.pop(0)

    except FileNotFoundError:
        sys.exit("FareStructure.txt file not found! Please add the file in same directory before running the program.")

    return Fare_data

# classify stations by lines
def get_line_data(MRT_data):
    line_data = {}
    for index in MRT_data["No."]:
        index = int(index) - 1
        line = MRT_data["Line"][index]
        station_pair = MRT_data["Station Pair"][index]
        if line not in line_data:
            line_data[line] = [station_pair[0][:2], index, 0, []]
        line_data[line][2] += 1
        if station_pair[0] not in line_data[line][3]:
            line_data[line][3].append(station_pair[0])
        if station_pair[1] not in line_data[line][3]:
            line_data[line][3].append(station_pair[1])

    return line_data

# list out codes for each station
def get_station_names_codes_list(line_data):
    station_names_codes_list = {}

    for line in line_data.values():
        stations = line[3]
        for station in stations:
            code, name = station.split(' ', 1)
            if name not in station_names_codes_list:
                station_names_codes_list[name] = [code]
            elif code not in station_names_codes_list[name]:
                station_names_codes_list[name].append(code)

    return station_names_codes_list



##### functions for the program

# create the main buttons at the left side
def create_button(label, x, y, stretch_wid=2, stretch_len=6):
    b = turtle.Turtle()
    b.speed(0)
    b.penup()
    b.goto(x, y)
    b.shape("square")
    b.shapesize(stretch_wid, stretch_len)
    b.fillcolor("lightblue")
    b.hideturtle()
    b.stamp()

    bt = turtle.Turtle()
    bt.speed(0)
    bt.penup()
    bt.hideturtle()
    bt.goto(x, y - 10)
    bt.write(label, align="center", font=("Arial", 14, "bold"))

# create the minor buttons that occur when press certain main buttons
def create_temp_button(label, x, y, stretch_wid=2, stretch_len=6):
    global buttons_temp
    b = turtle.Turtle()
    b.speed(0)
    b.penup()
    b.goto(x, y)
    b.shape("square")
    b.shapesize(stretch_wid, stretch_len)
    b.fillcolor("lightblue")
    b.hideturtle()
    b.stamp()
    buttons_temp.append(b)

    bt = turtle.Turtle()
    bt.speed(0)
    bt.penup()
    bt.hideturtle()
    bt.goto(x, y - 10)
    bt.write(label, align="center", font=("Arial", 14, "bold"))
    buttons_temp.append(bt)

# clear minor buttons when click main buttons
def clear_temp_buttons():
    global buttons_temp
    for button in buttons_temp:
        button.clear()
        button.hideturtle()
    buttons_temp = []

# set buttons boundary to bind it with onclick to detect click
def set_buttons_boundary(mode, button_label, x_min, x_max, y_min, y_max):
    global buttons_boundary
    global buttons_mode_list
    
    if mode not in buttons_mode_list:
        buttons_mode_list[mode] = []
    if button_label not in buttons_mode_list[mode]:
        buttons_mode_list[mode].append(button_label)
        buttons_boundary[button_label] = {
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max
        }

# delete onclick binding of minor buttons when change to other sections
def change_buttons_mode(mode):
    global screen
    global buttons_boundary
    global buttons_mode_list
    current_buttons_boundary = buttons_boundary.copy()
    for button_name in current_buttons_boundary.copy():
        if button_name not in buttons_mode_list[mode] and button_name not in buttons_mode_list["main"]:
            del current_buttons_boundary[button_name]

    screen.onclick(partial(on_click, buttons_boundary=current_buttons_boundary))

# detect mouse click
def on_click(x, y, buttons_boundary):
    for button_name, coordinate in buttons_boundary.copy().items():
        if coordinate["x_min"] <= x <= coordinate["x_max"] and coordinate["y_min"] <= y <= coordinate["y_max"]:
            activate_functions(button_name)

# activate respective functions when buttons clicked
def activate_functions(button_name):
    global buttons_mode_list
    global b
    global bt
    if button_name in buttons_mode_list["main"]:
        clear_temp_buttons()
        clear_section_temp_list()
        change_buttons_mode("main")
        reset_bg()

    # perform different tasks according to the button clicked
    if button_name == "Information":
        func_information()
    elif button_name == "MRT map":
        func_mrt_map()
    elif button_name == "Station list":
        func_station_list()
    elif button_name == "Check station":
        func_check_station()
    elif button_name == "Check train":
        func_check_train()
    elif button_name == "Result":
        func_result()
    elif button_name == "Exit":
        func_exit()
    elif button_name == "Circle":
        clear_section_temp_list()
        func_list_out_function("Circle")
    elif button_name == "Downtown":
        clear_section_temp_list()
        func_list_out_function("Downtown")
    elif button_name == "East-West":
        clear_section_temp_list()
        func_list_out_function("East-West")
    elif button_name == "North East":
        clear_section_temp_list()
        func_list_out_function("North East")
    elif button_name == "North-South":
        clear_section_temp_list()
        func_list_out_function("North-South")
    elif button_name == "Thomson-East Coast":
        clear_section_temp_list()
        func_list_out_function("Thomson-East Coast")
    elif button_name == "Input station":
        clear_section_temp_list()
        func_input_station("Input station")
    elif button_name == "Check line":
        clear_section_temp_list()
        func_display_station("Check line")
    elif button_name == "Check time":
        clear_section_temp_list()
        func_display_station("Check time")
    elif button_name == "Start Station":
        clear_section_temp_list()
        func_input("Start Station")
    elif button_name == "End Station": 
        clear_section_temp_list()
        func_input("End Station")
    elif button_name == "Start Time":
        clear_section_temp_list()
        func_input("Start Time")
    elif button_name == "1":
        clear_section_temp_list()
        func_display_result("1")
    elif button_name == "2":
        clear_section_temp_list()
        func_display_result("2")
    elif button_name == "3":
        clear_section_temp_list()
        func_display_result("3")
    elif button_name == "4":
        clear_section_temp_list()
        func_display_result("4")
    elif button_name == "5":
        clear_section_temp_list()
        func_display_result("5")
    elif button_name == "6":
        clear_section_temp_list()
        func_display_result("6")

# show program info
def func_information():
    global buttons_temp
    global main_screen_start_x
    global main_screen_start_y
    text = ["This is a Singapore MRT system information checking program.",
            "Users are able to check different information of the MRT system. Functions are listed below.",
            " ",
            "Main buttons functions:",
            "- \"Information\": Read info of this program (current page).",
            "- \"MRT map\": Check the complete MRT map.",
            "- \"Station list\": Check the stations list by choosing a specific MRT line.",
            "- \"Check station\": (1) Check the stations name/codes/lines by input station name or station code.",
            "                              (2) Check MRT line that the given station on.",
            "                              (3) Check first and last train time for the given station.",
            "- \"Check train\": Input your Start Station, End Station and Start Time, and get certain information in \"Result\".",
            "- \"Result\": After input your Start Station, End Station and Start Time in \"Check train\",",
            "                  you are able to check different information by pressing 1 - 6.",
            "                  (1) Find and display the best route between two stations.",
            "                  (2) Display the distance and the time of travel between the two stations.",
            "                  (3) Check the availability of train and whether it is able to arrive the destination before last train time.",
            "                  (4) Display MRT lines and interchange stations that the users will passed through.",
            "                  (5) Display different fare for different age groups.",
            "                  (6) Show all information at once.",
            "- \"Exit\": Exit the program."]
    
    text_x = main_screen_start_x + 100
    text_y = 275
    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    buttons_temp.append(writer)
    for line in text:
        writer.goto(text_x, text_y)
        writer.write(line, align="left", font=("Arial", 14, "normal"))
        text_y -= 30

# show complete mrt map
def func_mrt_map():
    global screen
    global main_screen_start_x
    global main_screen_start_y
    global buttons_temp

    try:
        screen.register_shape("MRT Map.gif")
        img_turtle = turtle.Turtle()
        img_turtle.shape("MRT Map.gif")
        img_turtle.penup()
        img_turtle.goto(100, 0)
        buttons_temp.append(img_turtle)

    # prompt if can't find the file
    except:
        screen.bgpic("nopic")
        screen.bgcolor("#FFFFE0")
        text = ["MRT Map.gif not found. Please save it in same",
                "directory with program and reopen the program."]
        text_x = main_screen_start_x + 550
        text_y = main_screen_start_y // 4
        writer = turtle.Turtle()
        writer.speed(0)
        writer.penup()
        writer.hideturtle()
        buttons_temp.append(writer)
        for line in text:
            writer.goto(text_x, text_y)
            writer.write(line, align="center", font=("Arial", 14, "normal"))
            text_y -= 30

# reset background when press main buttons
def reset_bg():
    global screen
    screen.bgpic("nopic")
    screen.bgcolor("#FFFFE0")

# show stations list by choosing lines
def func_station_list():
    button_width = 200
    global button_height
    global button_spacing
    global main_screen_start_x
    global main_screen_start_y
    x = main_screen_start_x + 135
    global button_start_y
    global line_data

    # write description
    text = ["Choose a line by pressing the buttons to list out all stations in that line"]
    text_x = x - 100
    text_y = 340
    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    buttons_temp.append(writer)
    for line in text:
        writer.goto(text_x, text_y)
        writer.write(line, align="left", font=("Arial", 10, "normal"))
        text_y -= 15

    # make buttons for users to choose lines
    for i in range(len(line_data)):
        button_x = x
        button_y = button_start_y - i * button_spacing
        button_label = list(line_data.keys())[i]
        x_min = button_x - button_width/2
        x_max = button_x + button_width/2
        y_min = button_y - button_height/2
        y_max = button_y + button_height/2

        set_buttons_boundary("Station list", button_label, x_min, x_max, y_min, y_max)
        create_temp_button(button_label, button_x, button_y, stretch_len=10)
    change_buttons_mode("Station list")

# list out stations when lines are choosed
def func_list_out_function(line_name):
    global line_data
    global main_screen_start_x
    global main_screen_start_y
    global screen_width
    global screen_height
    global section_temp_list
    line_list = line_data[line_name][3]

    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    section_temp_list.append(writer)

    max_line = 20
    spacing_x = 300
    spacing_y = 30
    start_x = main_screen_start_x + 350
    start_y = screen_height // 3
    
    for i, station in enumerate(line_list):
        col = i // max_line
        row = i % max_line
        x = start_x + col * spacing_x
        y = start_y - row * spacing_y
        writer.goto(x, y)
        writer.write(station, align="left", font=("Arial", 14, "normal"))

# clear stations list when another line is choosed
def clear_section_temp_list():
    global section_temp_list
    for i in section_temp_list:
        i.clear()
        i.hideturtle()
    section_temp_list = []

# create description and buttons when Check station was clicked
def func_check_station():
    global buttons_temp
    global main_screen_start_x
    global main_screen_start_y
    button_width = 20 * 7
    global button_height
    global button_spacing
    x = main_screen_start_x + 105
    global button_start_y

    # write description for different queries
    text = ["Input a station to (1) check what MRT line is the given station on",
            "(2) check the first and last train time for the given station.",
            "",
            "\"Input station\": Press to input station name (eg. Dhoby Ghaut) or station code (eg. CC1).",
            "\"Check line\": Press to check (1).",
            "\"Check time\": Press to check (2)."]
    
    text_x = main_screen_start_x + 35
    text_y = 330
    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    buttons_temp.append(writer)
    for line in text:
        writer.goto(text_x, text_y)
        writer.write(line, align="left", font=("Arial", 10, "normal"))
        text_y -= 15

    # create buttons for different queries
    buttons_list = ["Input station", "Check line", "Check time"]
    for i in range(len(buttons_list)):
        button_x = x
        button_y = button_start_y - i * button_spacing - 100
        x_min = button_x - button_width/2
        x_max = button_x + button_width/2
        y_min = button_y - button_height/2
        y_max = button_y + button_height/2

        set_buttons_boundary("Check station", buttons_list[i], x_min, x_max, y_min, y_max)
        create_temp_button(buttons_list[i], button_x, button_y, stretch_len=7)
    change_buttons_mode("Check station")
    func_input_station("a")

# Write out the current input station
def func_input_station(input_type):
    global check_station_input
    global main_screen_start_x
    global button_start_y
    global buttons_temp

    if input_type in check_station_input:
        check_station_input[input_type] = turtle.textinput("Input station", f"Press to input station name (eg. Dhoby Ghaut) or station code (eg. CC1):")
        clear_temp_buttons()
        func_check_station()
        func_input_station("a")

    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    buttons_temp.append(writer)

    button_x = main_screen_start_x + 200
    button_y = button_start_y - 110
    writer.goto(button_x, button_y)
    writer.write(f"Current input: {check_station_input["Input station"]}", align="left", font=("Arial", 14, "normal"))

# display station information or train time information based on the buttons clicked by users
def func_display_station(check_type):
    global check_station_input
    global main_screen_start_x
    global section_temp_list
    global button_start_y
    input_station = check_station_input["Input station"]
    station, codes_list, lines_list, times_text_list = find_stations(input_station)
    text = []

    text_x = main_screen_start_x + 200
    text_y = button_start_y - 210
    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    section_temp_list.append(writer)

    # if input invalid
    if station == "invalid" or station == "":
            text = ["Please enter a valid input!"]

    # if users click check line
    elif check_type == "Check line":
            codes_text = ""
            for code in codes_list:
                if code != codes_list[-1]:
                    codes_text += f"{code} / "
                else:
                    codes_text += f"{code}"

            lines_text = ""
            for line in lines_list:
                if line != lines_list[-1]:
                    lines_text += f"{line} / "
                else:
                    lines_text += f"{line}"

            text = [f"Station: {station}",
                    f"Codes: {codes_text}",
                    f"Lines: {lines_text}"]
    
    # if user click check time
    elif check_type == "Check time":
        text_y = button_start_y - 310
        text = times_text_list

    # write out the information after changing text list above
    for line in text:
        writer.goto(text_x, text_y)
        writer.write(line, align="left", font=("Arial", 14, "normal"))
        text_y -= 30

# find stations information based on the input
def find_stations(input_station):
    global station_names_codes_list
    global MRT_data

    station = ""
    codes_list = []
    lines_list = []
    times_text_list = []

    # Check if the input is a station code
    for name, codes in station_names_codes_list.items():
        if input_station in codes or input_station == name:
            station = name
            codes_list = codes
            break
        else:
            station = "invalid"
    
    # if valid, start to search information
    if station != "invalid":
        for name_pair in MRT_data["name_pair"]:
            if station in name_pair:
                index = MRT_data["name_pair"].index(name_pair)
                line = MRT_data["Line"][index]
                if line not in lines_list:
                    lines_list.append(line)
                
                if station == name_pair[0]:
                    next_station = name_pair[1]
                    station_code = MRT_data["code_pair"][index][0]
                    next_station_code = MRT_data["code_pair"][index][1]
                    first = MRT_data["First"][index]
                    last = MRT_data["Last"][index]
                elif station == name_pair[1]:
                    next_station = name_pair[0]
                    station_code = MRT_data["code_pair"][index][1]
                    next_station_code = MRT_data["code_pair"][index][0]
                    first = MRT_data["First opp"][index]
                    last = MRT_data["Last opp"][index]
                
                times_text_list.append(f"{station_code} {station} -> {next_station_code} {next_station} : first train time is {first}, last train time is {last}.")

    return station, codes_list, lines_list, times_text_list

# create input buttons and prompt for Check Train
def func_check_train():
    global buttons_temp
    button_width = 200
    x_spacing = 350
    global button_height
    global main_screen_start_x
    global main_screen_start_y
    button_label_list = ["Start Station", "End Station", "Start Time"]

    # create buttons
    for i in range(len(button_label_list)):
        button_x = main_screen_start_x + 200 + i * x_spacing
        button_y = main_screen_start_y // 2 - 250
        button_label = button_label_list[i]
        x_min = button_x - button_width/2
        x_max = button_x + button_width/2
        y_min = button_y - button_height/2
        y_max = button_y + button_height/2

        set_buttons_boundary("Check train", button_label, x_min, x_max, y_min, y_max)
        create_temp_button(button_label, button_x, button_y, stretch_len=10)
    change_buttons_mode("Check train")

    # create description
    text = ["Input your Start Station, End Station and Start Time by pressing the respective button. ",
        "For Start Station and End Station, please enter the station code (e.g., CC1, DT8, etc.). ",
        "You may check the station code in 'Station List'.", 
        "For Start Time, please enter the time in 24-hour HHMM format (e.g., 1430).",
        "Current input are shown above the buttons."]
    text_x = main_screen_start_x + 200 + x_spacing
    text_y = main_screen_start_y // 2
    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    buttons_temp.append(writer)
    for line in text:
        writer.goto(text_x, text_y)
        writer.write(line, align="center", font=("Arial", 14, "normal"))
        text_y -= 30
    func_input("a")

# popout input window and print out input information
def func_input(input_type):
    global check_train_input
    if input_type in check_train_input:
        check_train_input[input_type] = turtle.textinput(f"Input {input_type}", f"Please enter {input_type}:")

    x_spacing = 350
    global button_height
    global main_screen_start_x
    global main_screen_start_y
    button_label_list = ["Start Station", "End Station", "Start Time"]

    # print out the input value
    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    section_temp_list.append(writer)

    for i, button_label in enumerate(button_label_list):
        button_x = main_screen_start_x + 200 + i * x_spacing
        button_y = main_screen_start_y // 2 - 200
        writer.goto(button_x, button_y)
        writer.write(check_train_input[button_label], align="center", font=("Arial", 20, "normal"))

# check whether the users input is valid
def func_result():
    global check_train_input
    global station_names_codes_list
    global main_screen_start_x
    global main_screen_start_y
    global buttons_temp
    global _start_name
    global _end_name
    station_names_list = []
    station_codes_list = [[],[]]
    for name in station_names_codes_list:
        station_names_list.append(name)
        for code in station_names_codes_list[name]:
            station_codes_list[0].append(code)
            station_codes_list[1].append(name)

    text = ""

    
    if check_train_input["Start Station"] == "" or check_train_input["End Station"] == "" or check_train_input["Start Time"] == "" or check_train_input["Start Station"] == None or check_train_input["End Station"] == None or check_train_input["Start Time"] == None:
        text = "Please input Start Station, End Station and Start Time in \"Check Train\"."
    elif check_train_input["Start Station"] not in station_codes_list[0]:
        text = "Invalid Start Station, please input again in \"Check Train\"."
    elif check_train_input["End Station"] not in station_codes_list[0]:
        text = "Invalid End Station, please input again in \"Check Train\"."
    elif len(check_train_input["Start Time"]) != 4:
        text = "Invalid Start Time, please input again in \"Check Train\"."
    elif len(check_train_input["Start Time"]) == 4:
        num = check_train_input["Start Time"]
        hour = int(num[:2])
        min = int(num[2:])
        if hour < 24:
            if min > 59:
                text = "Invalid Start Time, please input again in \"Check Train\"."
            else:
                _start_name = station_codes_list[1][station_codes_list[0].index(check_train_input["Start Station"])]
                _end_name = station_codes_list[1][station_codes_list[0].index(check_train_input["End Station"])]
            
                if _start_name == _end_name:
                    text = "Please input a different start and end station in \"Check Train\"."
        elif hour > 23:
            text = "Invalid Start Time, please input again in \"Check Train\"."
    
    # if valid, print out the buttons and description
    if text != "":
        text_x = main_screen_start_x + 500
        text_y = main_screen_start_y // 2 - 200
        writer = turtle.Turtle()
        writer.speed(0)
        writer.penup()
        writer.hideturtle()
        buttons_temp.append(writer)
        writer.goto(text_x, text_y)
        writer.write(text, align="center", font=("Arial", 14, "normal"))
    elif text == "":
        func_show_result_buttons(_start_name, _end_name)

# show informations based on users input
def func_show_result_buttons(start_name, end_name):
    global buttons_temp
    global main_screen_start_x
    global main_screen_start_y
    button_width = 40
    global button_height
    global button_spacing
    x = main_screen_start_x + 50
    global button_start_y
    queries = [1, 2, 3, 4, 5, 6]

    # explain different queries
    text = ["Press 1-6 to access different queries by refering to the given start & end station and start time.",
            "1: Find and display the best route between two stations.",
            "2: Display the distance and the time of travel between the two stations.",
            "3: Check the availability of train and whether it is able to arrive the destination before last train time.",
            "4: Display MRT lines and interchange stations that the users will passed through.",
            "5: Display different fare for different age groups.",
            "6: Show all information at once."]
    text_x = main_screen_start_x + 35
    text_y = 330
    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    buttons_temp.append(writer)
    for line in text:
        writer.goto(text_x, text_y)
        writer.write(line, align="left", font=("Arial", 10, "normal"))
        text_y -= 15

    # create buttons for different queries
    for i in range(len(queries)):
        button_x = x
        button_y = button_start_y - i * button_spacing - 100
        x_min = button_x - button_width/2
        x_max = button_x + button_width/2
        y_min = button_y - button_height/2
        y_max = button_y + button_height/2

        set_buttons_boundary("Result", str(queries[i]), x_min, x_max, y_min, y_max)
        create_temp_button(str(queries[i]), button_x, button_y, stretch_len=2)
    change_buttons_mode("Result")

    # print the input that users entered previously
    start_x = main_screen_start_x + 150
    start_y = 180
    _writer = turtle.Turtle()
    _writer.speed(0)
    _writer.penup()
    _writer.hideturtle()
    buttons_temp.append(_writer)

    global check_train_input
    text_start_x = start_x
    text_start_y = start_y
    start_code = check_train_input["Start Station"]
    end_code = check_train_input["End Station"]
    start_time = check_train_input["Start Time"]
    text_input = [f"Start Station: {start_code} {start_name}",
                  f"End Station: {end_code} {end_name}",
                  f"Start Time: {start_time}",]
    for line in text_input:
        _writer.goto(text_start_x, text_start_y)
        _writer.write(line, align="left", font=("Arial", 14, "normal"))
        text_start_y -= 30

# display different information based on the buttons clicked
def func_display_result(query):
    global check_train_input
    global MRT_data
    global lines_colour
    global buttons_temp
    global main_screen_start_x
    global main_screen_start_y
    global _start_name
    global _end_name
    start_name = _start_name
    end_name = _end_name

    start_time = check_train_input["Start Time"]
    path = get_shortest_path(start_name, end_name)
    total_time_used = get_total_time_used(path, end_name)
    total_distance = get_distance(path)

    lines = []
    interchange_stations = []
    previous_line = ""

    # check the passed lines and interchange stations
    for i in range(len(path) - 1):
        current = path[i]
        next = path[i + 1]

        for j, pair in enumerate(MRT_data["name_pair"]):
            if [current, next] == pair or [next, current] == pair:
                current_line = MRT_data["Line"][j]
                break

        if i > 0:
            if current_line != previous_line:
                interchange_stations.append(current)
        
        lines.append(current_line)
        previous_line = current_line

    # get text for different queries
    text_operating_time = check_train_time(start_name, end_name, start_time, total_time_used, path)
    text_fare = get_fare(total_distance)
    text_distance_and_time = [f"Total distance travelled: {total_distance} km", f"Total time used: {total_time_used} minutes"]
    text_summary = get_summary(path, lines, interchange_stations)    
    
    d = turtle.Turtle()
    d.speed(0)
    d.penup()
    d.hideturtle()
    d.pensize(3)
    section_temp_list.append(d)
    start_x = main_screen_start_x + 250
    start_y = -50

    writer = turtle.Turtle()
    writer.speed(0)
    writer.penup()
    writer.hideturtle()
    section_temp_list.append(writer)

    # print out the mrt line
    def query_1():
        _start_x = start_x - 80
        _start_y = 80
        spacing_x = 100
        spacing_y = 50
        color = lines_colour[lines[0]]
        d.color(color)
        d.goto(_start_x, _start_y)
        d.dot(20, color)
        d.goto(_start_x, _start_y - 30)
        d.write(path[0], align="center", font=("Arial", 8, "normal"))
        px = _start_x
        py = _start_y

        for i in range(1, len(path)):
            station = path[i]
            line = lines[i - 1]
            color = lines_colour[line]
            d.color(color)

            row = i // 8
            row = i // 8
            col = i % 8
            if row % 2 == 0:
                x = _start_x + col * spacing_x
            else:
                x = _start_x + (7 - col) * spacing_x
            y = _start_y - row * spacing_y

            d.goto(x, y)
            if station not in interchange_stations:
                d.dot(20, color)
            else:
                d.dot(20, "black")
            d.goto(x, y - 30)
            d.write(station, align="center", font=("Arial", 8, "normal"))
            
            d.color(color)
            d.goto(px, py)
            d.pendown()
            d.goto(x, y)
            d.penup()
            px = x
            py = y

    # show distance and time
    def query_2():
        text_start_x = start_x - 100
        text_start_y = 80
        for line in text_distance_and_time:
            writer.goto(text_start_x, text_start_y)
            writer.write(line, align="left", font=("Arial", 14, "normal"))
            text_start_y -= 30

    # show operating time
    def query_3():
        text_start_x = start_x - 100
        text_start_y = -20
        for line in text_operating_time:
            writer.goto(text_start_x, text_start_y)
            writer.write(line, align="left", font=("Arial", 14, "normal"))
            text_start_y -= 30

    # show line and interchange stations
    def query_4():
        text_start_x = start_x - 100
        text_start_y = -20
        writer.goto(text_start_x, text_start_y)
        writer.write(text_summary, align="left", font=("Arial", 14, "normal"))

        _start_x = start_x - 80
        _start_y = -80
        spacing_x = 100
        spacing_y = 50
        color = lines_colour[lines[0]]
        d.color(color)
        d.goto(_start_x, _start_y)
        d.dot(20, color)
        d.goto(_start_x, _start_y - 30)
        d.write(path[0], align="center", font=("Arial", 8, "normal"))
        px = _start_x
        py = _start_y

        for i in range(1, len(path)):
            station = path[i]
            line = lines[i - 1]
            color = lines_colour[line]
            d.color(color)

            row = i // 8
            row = i // 8
            col = i % 8
            if row % 2 == 0:
                x = _start_x + col * spacing_x
            else:
                x = _start_x + (7 - col) * spacing_x
            y = _start_y - row * spacing_y

            d.goto(x, y)
            if station not in interchange_stations:
                d.dot(20, color)
            else:
                d.dot(20, "black")
            d.goto(x, y - 30)
            d.write(station, align="center", font=("Arial", 8, "normal"))
            
            d.color(color)
            d.goto(px, py)
            d.pendown()
            d.goto(x, y)
            d.penup()
            px = x
            py = y

    # show fare
    def query_5():
        text_start_x = start_x - 100
        text_start_y = -220
        for line in text_fare:
            writer.goto(text_start_x, text_start_y)
            writer.write(line, align="left", font=("Arial", 14, "normal"))
            text_start_y -= 30

    # show all
    def query_6():
        text_start_x = start_x + 300
        text_start_y = 180
        for line in text_operating_time:
            writer.goto(text_start_x, text_start_y)
            writer.write(line, align="left", font=("Arial", 14, "normal"))
            text_start_y -= 30
        
        text_start_x = start_x - 100
        text_start_y = start_y + 100
        for line in text_distance_and_time:
            writer.goto(text_start_x, text_start_y)
            writer.write(line, align="left", font=("Arial", 14, "normal"))
            text_start_y -= 30
        
        text_start_x  = start_x + 300
        text_start_y = start_y + 100
        for line in text_fare:
            writer.goto(text_start_x, text_start_y)
            writer.write(line, align="left", font=("Arial", 14, "normal"))
            text_start_y -= 30
        
        text_start_x = start_x - 100
        text_start_y = start_y - 50
        writer.goto(text_start_x, text_start_y)
        writer.write(text_summary, align="left", font=("Arial", 14, "normal"))

        _start_x = start_x - 80
        _start_y = start_y - 100
        spacing_x = 100
        spacing_y = 50
        color = lines_colour[lines[0]]
        d.color(color)
        d.goto(_start_x, _start_y)
        d.dot(20, color)
        d.goto(_start_x, _start_y - 30)
        d.write(path[0], align="center", font=("Arial", 8, "normal"))
        px = _start_x
        py = _start_y

        for i in range(1, len(path)):
            station = path[i]
            line = lines[i - 1]
            color = lines_colour[line]
            d.color(color)

            row = i // 8
            row = i // 8
            col = i % 8
            if row % 2 == 0:
                x = _start_x + col * spacing_x
            else:
                x = _start_x + (7 - col) * spacing_x
            y = _start_y - row * spacing_y

            d.goto(x, y)
            if station not in interchange_stations:
                d.dot(20, color)
            else:
                d.dot(20, "black")
            d.goto(x, y - 30)
            d.write(station, align="center", font=("Arial", 8, "normal"))
            
            d.color(color)
            d.goto(px, py)
            d.pendown()
            d.goto(x, y)
            d.penup()
            px = x
            py = y

    if query == "1":
        query_1()
    elif query == "2":
        query_2()
    elif query == "3":
        query_3()
    elif query == "4":
        query_4()
    elif query == "5":
        query_5()
    elif query == "6":
        query_6()

# use BFS to find shortest path
def get_shortest_path(start_name, end_name):
    global MRT_data

    adjacent_list = {}
    for i in MRT_data["name_pair"]:
        if i[0] not in adjacent_list:
            adjacent_list[i[0]] = []
        if i[1] not in adjacent_list:
            adjacent_list[i[1]] = []
        if i[0] not in adjacent_list[i[1]]:
            adjacent_list[i[1]].append(i[0])
        if i[1] not in adjacent_list[i[0]]:
            adjacent_list[i[0]].append(i[1])

    start = start_name
    end = end_name
    possible_path = [[start]]
    visited_locations = [start]

    # choose path to expand
    while True:
        path = possible_path.pop(0)
        current = path[-1]
        if current == end:
            found_path = path.copy()
            break
        neighbours = adjacent_list[current]

        for neighbour in neighbours:
            if neighbour in visited_locations:
                pass
            else:
                visited_locations.append(neighbour)
                new_path = path.copy()
                new_path.append(neighbour)
                possible_path.append(new_path)
    return found_path

# calculate total time used
def get_total_time_used(found_path, end_name):
    global MRT_data
    global check_train_input
    end = end_name

    total_time_used = 0
    for i in found_path:
        if i == end:
            break
        else:
            if [i, found_path[found_path.index(i)+1]] in MRT_data["name_pair"]:
                index = MRT_data["name_pair"].index([i, found_path[found_path.index(i)+1]])
            else:
                index = MRT_data["name_pair"].index([found_path[found_path.index(i)+1], i])
            total_time_used += (float(MRT_data["Distance"][index]) / float(MRT_data["Speed"][index]) * 60)
    return round(total_time_used, 2)

# check whether can arrive destination before last train, also return the train time
def check_train_time(start_name, end_name, start_time, total_time_used, path):
    global MRT_data
    first = path[0]
    second = path[1]
    second_last = path[-2]
    last = path[-1]
    start_first_train_label = ""
    start_last_train_label = ""
    end_last_train_label = ""
    first_name_pair = []
    last_name_pair = []

    for i, pair in enumerate(MRT_data["name_pair"]):
        if [first, second] == pair:
            start_first_train_label = "First"
            start_last_train_label = "Last"
            first_name_pair = pair
            break
        elif [second, first] == pair:
            start_first_train_label = "First opp"
            start_last_train_label = "Last opp"
            first_name_pair = pair
            break
    for i, pair in enumerate(MRT_data["name_pair"]):
        if [second_last, last] == pair:
            end_last_train_label = "Last"
            last_name_pair = pair
            break
        elif [last, second_last] == pair:
            end_last_train_label = "Last opp"
            last_name_pair = pair
            break

    start_hour = int(start_time[:2])
    start_minute = int(start_time[2:])
    start_time_in_minutes = start_hour * 60 + start_minute
    arrival_time_in_minutes = start_time_in_minutes + int(round(total_time_used))
    arrival_hour = (arrival_time_in_minutes // 60) % 24
    arrival_minute = arrival_time_in_minutes % 60

    start_first_train_time = MRT_data[start_first_train_label][MRT_data["name_pair"].index(first_name_pair)]
    start_first_train_hour = int(start_first_train_time[:2])
    start_first_train_minute = int(start_first_train_time[2:])
    start_first_train_time_in_minutes = start_first_train_hour * 60 + start_first_train_minute

    start_last_train_time = MRT_data[start_last_train_label][MRT_data["name_pair"].index(first_name_pair)]
    start_last_train_hour = int(start_last_train_time[:2])
    start_last_train_minute = int(start_last_train_time[2:])
    start_last_train_time_in_minutes = start_last_train_hour * 60 + start_last_train_minute
    if start_last_train_hour < start_first_train_hour:
        start_last_train_time_in_minutes += 24 * 60

    end_last_train_time = MRT_data[end_last_train_label][MRT_data["name_pair"].index(last_name_pair)]
    end_last_train_hour = int(end_last_train_time[:2])
    end_last_train_minute = int(end_last_train_time[2:])
    end_last_train_time_in_minutes = end_last_train_hour * 60 + end_last_train_minute
    if end_last_train_hour < start_first_train_hour:
        end_last_train_time_in_minutes += 24 * 60

    text = []
    if start_time_in_minutes < start_first_train_time_in_minutes or start_time_in_minutes > start_last_train_time_in_minutes:
        text.append(f"No train available at {start_name} at {start_time}!")
    elif arrival_time_in_minutes > end_last_train_time_in_minutes:
        text.append(f"The train will not arrive at {end_name} before the last train time {end_last_train_time}")
    else:
        text.append(f"The train is running and will arrive at {end_name} at {arrival_hour:02}{arrival_minute:02}.")
    text.append(f"Start station: first train {start_first_train_time}, last train {start_last_train_time}")
    text.append(f"Last station: last train {end_last_train_time}")

    return text

# calculate fare
def get_fare(total_distance):
    global Fare_data
    fare_results = {}

    for fare_category in Fare_data:
        distance = Fare_data[fare_category]["Distance"]
        fares = Fare_data[fare_category]["Card Fare Per Ride (cents)"]
        total_distance = float(total_distance)
        fare_in_cents = 0

        for i, bracket in enumerate(distance):
            if "Up to" in bracket:
                max_distance = float(bracket.split(" ")[-2])
                if total_distance <= max_distance:
                    fare_in_cents = int(fares[i])
                    break
            elif "Over" in bracket:
                min_distance = float(bracket.split(" ")[-2])
                if total_distance > min_distance:
                    fare_in_cents = int(fares[i])
                    break
            else:
                mid_distance = bracket.replace(" km", "").split(" - ")
                min_distance = float(mid_distance[0])
                max_distance = float(mid_distance[1])
                if min_distance <= total_distance <= max_distance:
                    fare_in_cents = int(fares[i])
                    break
        fare_in_dollars = fare_in_cents / 100
        fare_results[fare_category] = fare_in_dollars
        
    text = ["Fare:",
            f"Adult ${fare_results["Adult Fare"]}",
            f"Senior Citizen / Persons with Disabilities ${fare_results["Senior Citizen / Persons with Disabilities Fare"]}",
            f"Student ${fare_results["Student Fare"]}"]

    return text

# find total distance travelled
def get_distance(path):
    global MRT_data
    total_distance = 0.0

    for i in range(len(path) - 1):
        current = path[i]
        next = path[i + 1]

        if [current, next] in MRT_data["name_pair"]:
            index = MRT_data["name_pair"].index([current, next])
        elif [next, current] in MRT_data["name_pair"]:
            index = MRT_data["name_pair"].index([next, current])

        total_distance += float(MRT_data["Distance"][index])

    return round(total_distance, 2)

# get summary text
def get_summary(path, lines, interchange_stations):
    text = f"{path[0]} -> {lines[0]}"

    for i in range(1, len(path) - 1):
        station = path[i]
        if station in interchange_stations:
            next_line = lines[i]
            text += f" -> {station} -> {next_line}"

    text += f" -> {path[-1]}"
    return text

# close the program
def func_exit():
    turtle.bye()




##### main program that setup the turtle window and let everything start to loop

# get data
MRT_data = get_MRT_data()
Fare_data = get_Fare_data()
line_data = get_line_data(MRT_data)
station_names_codes_list = get_station_names_codes_list(line_data)

# create turtle screen
screen = turtle.Screen()
screen.title("MRT Information System")
screen.setup(width=1.0, height=1.0)
screen.bgcolor("#FFFFE0")
screen_width = screen.window_width()
screen_height = screen.window_height()

# create neccessary data dictionary or list
buttons_data = ["Information", "MRT map", "Station list", "Check station", "Check train", "Result", "Exit"]
buttons_boundary = {}
buttons_mode_list = {}
buttons_temp = []
section_temp_list = []
check_train_input = {"Start Station" : "", "End Station" : "", "Start Time" : ""}
check_station_input = {"Input station": ""}
lines_colour = {"Circle": "#fa9e0d", "Downtown": "#005ec4", "East-West": "#009645", "North East": "#9900aa", "North-South": "#d42e12", "Thomson-East Coast": "#9d5b25"}
_start_name = ""
_end_name = ""

# set up coordinates
button_width = 20 * 7
button_height = 20 * 2
button_x = -screen_width // 2 + 100
button_spacing = 100
button_start_y = screen_height // 3
main_screen_width = screen_width - 200
main_screen_height = screen_height
main_screen_start_x = -screen_width // 2 + 200
main_screen_start_y = screen_height // 2

# draw line to separate main buttons and screen
d = turtle.Turtle()
d.speed(0)
d.penup()
d.hideturtle()
d.goto(button_x + 100, button_start_y + 300)
d.pendown()
d.goto(button_x + 100, button_start_y - 900)
d.penup()

# create main buttons at the left side
for i in range(len(buttons_data)):
    x = button_x
    y = button_start_y - i * button_spacing
    x_min = x - button_width/2
    x_max = x + button_width/2
    y_min = y - button_height/2
    y_max = y + button_height/2
    set_buttons_boundary("main", buttons_data[i], x_min, x_max, y_min, y_max)
    create_button(buttons_data[i], x, y, stretch_len=7)
change_buttons_mode("main")

# show program info when program is launched
func_information()

# keep screen open
screen.mainloop()