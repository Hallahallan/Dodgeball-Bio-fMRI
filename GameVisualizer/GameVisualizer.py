import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons
import numpy as np
from datetime import datetime, timedelta
from math import cos, sin, pi



# year-month-day_hour-minutes-seconds : "yyyy-MM-dd_HH-mm-ss"
date = "2023-11-22_13-58-01"  # time to plot #  2023-11-09_17-40-48
game_type = "neat" # neat or fsm ...
game_num = 2 # won't matter if show_all_games = True
show_all_games = False

timestamp_format = "%H:%M:%S.%f"


def getLogData(name) -> str:
    """
    Returns the log data from one log file from the time of date, as a string
    name - PlayerData , Position or Results
    """
    log_path = "Assets/Dodgeball/Logs"

    part_path = ""
    if name == "PlayerData":
        part_path = "Player_Data"
    else:
        part_path = name
    full_path = log_path + "/" + name + "/GameLog_" + part_path + "_" + date + ".txt"

    f = open(full_path, "r")
    data = f.read()
    f.close()
    return data


class PositionData:
    def __init__(self, pos_data: str) -> None:
        self.pos_list = []

        iterator = iter(pos_data.splitlines())
        next(iterator)  # Skip first line
        for pos_line in iterator:
            self.pos_list.append(self.Position(pos_line))

    class Position:
        def __init__(self, position_line) -> None:
            data = position_line.replace("(", "").replace(")", "").split(",")
            self.timestamp = datetime.strptime(data[0], timestamp_format)
            self.pos_blue_x = float(data[1])
            self.pos_blue_y = float(data[2])
            self.rotation_blue = float(data[3])
            self.pos_purple_x = float(data[4])
            self.pos_purple_y = float(data[5])
            self.rotation_purple = float(data[6])

        def getBlueData(self) -> tuple:
            """
            Return tuple with x, y and rotation
            """
            return tuple((self.pos_blue_x, self.pos_blue_y, self.rotation_blue))

        def getPurpleData(self) -> tuple:
            """
            Return tuple with x, y and rotation
            """
            return tuple((self.pos_purple_x, self.pos_purple_y, self.rotation_purple))

        def __str__(self) -> str:
            return ", ".join(
                [
                    self.timestamp.strftime(timestamp_format),
                    "(" + str(self.pos_blue_x),
                    str(self.pos_blue_y) + ")",
                    str(self.rotation_blue),
                    "(" + str(self.pos_purple_x),
                    str(self.pos_purple_y) + ")",
                    str(self.rotation_purple),
                ]
            )

    def positionList(self, getBlue: bool, position_list: list = None) -> list:
        result_list = []

        if position_list is None:
            position_list = self.pos_list

        if getBlue:
            for pos in position_list:
                result_list.append(pos.getBlueData())
        else:
            for pos in position_list:
                result_list.append(pos.getPurpleData())
        return result_list
    
    def getGamePos(self, start_time: datetime, end_time: datetime) -> list:
        return list(filter(lambda pos: pos.timestamp >= start_time and pos.timestamp <= end_time, self.pos_list))
    
class PlayerData:
    def __init__(self, player_data: str) -> None:
        self.event_list = []

        iterator = iter(player_data.splitlines())
        next(iterator)  # Skip first line
        for event_line in iterator:
            self.event_list.append(self.Event(event_line))

    class Event:
        def __init__(self, event: str) -> None:
            data = event.split(",")
            self.timestamp = datetime.strptime(data[0], timestamp_format)
            self.event_type = data[1]
            self.balls_left = int(data[2])
            self.player_lives = int(data[3])
            self.enemy_lives = int(data[4])
            self.corner = int(data[5])

        def isResetSceneEvent(self) -> bool:
            return self.event_type == "ResetScene"

    def numGames(self) -> int:
        return len(list(filter(lambda event: event.isResetSceneEvent(), self.event_list))) -1
    
    def getStartEndTimes(self, game_num: int = 0) -> tuple:
        """
        Get start and end times for a game.
        game_num=0 -> times for first game
        """
        if game_num > self.numGames():
            raise Exception(f"Number of games is {self.numGames()}, cannot get times for game number {game_num}")
        
        reset_scene_list = list(filter(lambda event: event.isResetSceneEvent(), self.event_list))

        return reset_scene_list[game_num].timestamp, reset_scene_list[game_num+1].timestamp

def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


def drawBoard(fig, ax):
    corners = [(8.9, -20), (34.9, -20), (34.9, -73.9), (8.9, -73.6)] 
    bushes = [
        [(18.8, -64.5), (17.7, -64.5), (16.6, -64.5), (15.5, -64.5), (14.4, -64.5), (13.3, -64.5)],
        [(32.0, -64.5), (30.9, -64.5), (29.8, -64.5), (28.7, -64.5), (27.6, -64.5), (26.5, -64.5)],
        [(18.3, -54.6), (17.5, -55.4), (16.7, -56.2), (16.0, -57.0), (15.2, -57.8), (14.4, -58.5)],
        [(29.8, -58.5), (29.0, -57.8), (28.2, -57.0), (27.5, -56.2), (26.7, -55.4), (25.9, -54.6)],
        [(18.8, -42.8), (18.0, -42.0), (17.2, -41.2), (16.5, -40.5), (15.7, -39.7), (14.9, -38.9)],
        [(29.3, -38.9), (28.5, -39.7), (27.7, -40.5), (27.0, -41.2), (26.2, -42.0), (25.4, -42.8)],
        [(18.8, -31.9), (17.7, -31.9), (16.6, -31.9), (15.5, -31.9), (14.4, -31.9), (13.3, -31.9)],
        [(32.0, -31.7), (30.9, -31.7), (29.8, -31.7), (28.7, -31.7), (27.6, -31.7), (26.5, -31.7)],
    ]

    x_delta = 0
    y_delta = 0
    if game_type == "neat":
        y_delta = 34

    #print(f"Bushes (num={len(bushes)}): {sorted(bushes, key=lambda x : x[1])}")

    boarder_and_bush_color = "#78B16A"

    for i in range(len(corners)):
        plt.plot([corners[i-1][0]+x_delta, corners[i][0]+x_delta], [corners[i-1][1]+y_delta, corners[i][1]+y_delta], c=boarder_and_bush_color)

    for i in range(len(bushes)):
        plt.plot([x+x_delta for x, _ in bushes[i]], [y+y_delta for _, y in bushes[i]], c=boarder_and_bush_color)


def drawEvents(fig, ax, pos_data:list, player_data:PlayerData):
    event_labels = ["EnemyThrewBall", "PlayerThrewBall", "HitEnemy", "TookDamage"]
    event_markers = {"EnemyThrewBall":"^", "PlayerThrewBall":"o", "HitEnemy":"+", "TookDamage":"X"}
    values = [True for _ in event_labels]

    # xposition, yposition, width and height
    ax_check = plt.axes([0.05, 0.6, 0.3, 0.3])
    plt.chxbox = CheckButtons(ax_check, event_labels, values)

    lines = []

    event_pos_dict = {}
    for event in event_labels:
        event_pos_dict[event] = []

    for event in player_data.event_list:
        if event.timestamp >= pos_data[0].timestamp and event.timestamp <= pos_data[-1].timestamp and event.event_type in event_labels:
            #print("Enemy" in event.event_type, event.event_type)
            enemy = "Enemy" in event.event_type # Check if need position of enemy/AI or player/human

            # Join event with closest position
            closest_pos = None
            time_diff = None

            for pos in pos_data:
                if closest_pos is None:
                    closest_pos=pos
                    time_diff=abs(event.timestamp - pos.timestamp)
                else:
                    if abs(event.timestamp - pos.timestamp) < time_diff:
                        closest_pos=pos
                        time_diff=abs(event.timestamp - pos.timestamp)
                # if time_diff<0.05:
                #     break
            
            event_pos_dict[event.event_type].append([closest_pos.pos_blue_x, closest_pos.pos_blue_y] if not enemy else [closest_pos.pos_purple_x, closest_pos.pos_purple_y])
    
    for event_type in event_pos_dict.keys():
        p, = ax.plot(
            [x for x, _ in event_pos_dict[event_type]],
            [y for _, y in event_pos_dict[event_type]],
            marker=event_markers[event_type],
            markersize=8,
            linewidth=0,
            label=event_type,
            alpha=0.7
        )
        lines.append(p)


    def onClick(label):
        index = event_labels.index(label)
        lines[index].set_visible(not lines[index].get_visible())
        fig.canvas.draw_idle()
    
    plt.chxbox.on_clicked(onClick)


def showRun(pos_data: PositionData, player_data: PlayerData, game_num: int = 0, see_angles:bool = True, only_agent:bool = False) -> None:
    start_time, end_time = player_data.getStartEndTimes(game_num)
    duration = (end_time-start_time).total_seconds()
    print(duration)

    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.25)

    # Slider to adjust the shown positions (dependent on the time) 
    ax_time = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    time_slider = Slider(
        ax=ax_time, 
        label=f"Time",
        valmin=0,
        valmax=duration,
        valinit=0
    )

    def update_time(val):
        # line.set_ydata(f(t, amp_slider.val, freq_slider.val))
        # fig.canvas.draw_idle()
        
        fig.canvas.draw_idle()
    time_slider.on_changed(update_time)

    game_pos_data = pos_data.getGamePos(start_time, end_time)

    blue_data = pos_data.positionList(True, game_pos_data)
    purple_data = pos_data.positionList(False, game_pos_data)
    run_lenght = len(blue_data)
    plot_color = [colorFader("green", "red", n/run_lenght) for n in range(run_lenght)]
    blue_color = [colorFader("blue", "blue", n/run_lenght) for n in range(run_lenght)]
    purple_color = [colorFader("purple", "purple", n/run_lenght) for n in range(run_lenght)]

    if not only_agent:
        ax.scatter(
            [x for x, _, _ in blue_data],
            [y for _, y, _ in blue_data],
            color=blue_color,
            marker="o",
        )
    ax.scatter(
        [x for x, _, _ in purple_data],
        [y for _, y, _ in purple_data],
        color=purple_color,
        marker="o",
    )
    if see_angles:
        arrow_length = 1
        if not only_agent:
            ax.quiver(
                [x for x, _, _ in blue_data],
                [y for _, y, _ in blue_data],
                [arrow_length*sin(r*pi/180) for _, _, r in blue_data],
                [arrow_length*cos(r*pi/180) for _, _, r in blue_data],
                angles="xy",
                color=plot_color,
                headwidth="3",
                label="Player"
            )
        ax.quiver(
            [x for x, _, _ in purple_data], 
            [y for _, y, _ in purple_data],
            [arrow_length*sin(r*pi/180) for _, _, r in purple_data],
            [arrow_length*cos(r*pi/180) for _, _, r in purple_data],
            angles="xy",
            color=plot_color,
            headwidth="8",
            label="Agent"
        )
    plt.show()


def showFullRunWithSliderTime(pos_data: PositionData, player_data: PlayerData, game_num: int = 0) -> None:
    # purple - machine agent
    # blue - human agent

    start_time, end_time = player_data.getStartEndTimes(game_num) # TODO change so gamne num 0 starts with event "S" instead of "ResetScene"
    duration = (end_time-start_time).total_seconds()
    shadow_time = 2 # how many seconds will show around the time set on the time slider
    light_blue = "#A4A7DD" # "#ABCBD1"
    dark_blue = "#000AC3" # "#00638F"
    blue_edge_color = "#FFFFFF"
    light_purple = "#CCBE86" # "#D3BCE2"
    dark_purple = "#C39C00" # "#410084"
    purple_edge_color = "#000000"
    line_width = 1
    blue_arrow_size = 0.3
    purple_arrow_size = 0.1
    arrow_length = 10


    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.25, left=0.45)

    drawBoard(fig, ax)

    # Slider to adjust the shown positions (dependent on the time) 
    ax_time = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    time_slider = Slider(
        ax=ax_time, 
        label=f"Time",
        valmin=0,
        valmax=duration,
        valinit=0
    )

    game_pos_data_all = pos_data.getGamePos(start_time, end_time)
    game_pos_data_past = [game_pos_data_all[0]]

    blue_data_all = pos_data.positionList(True, game_pos_data_all)
    purple_data_all = pos_data.positionList(False, game_pos_data_all)
    blue_data_past = pos_data.positionList(True, game_pos_data_past)
    purple_data_past = pos_data.positionList(False, game_pos_data_past)

    drawEvents(fig, ax, game_pos_data_all, player_data)

    past_lenght = shadow_time*10

    while len(blue_data_past)<past_lenght:
        blue_data_past.append(blue_data_past[0])
    while len(purple_data_past)<past_lenght:
        purple_data_past.append(purple_data_past[0])

    all_lenght = len(blue_data_all)
    past_lenght = len(blue_data_past)

    blue_all_color = [light_blue for n in range(all_lenght)]
    purple_all_color = [light_purple for n in range(all_lenght)]
    blue_past_color = [colorFader(dark_blue, light_blue, n/past_lenght) for n in range(past_lenght)]
    purple_past_color = [colorFader(dark_purple, light_purple, n/past_lenght) for n in range(past_lenght)]

    
    qv_blue = ax.quiver(
        [x for x, _, _ in blue_data_all],
        [y for _, y, _ in blue_data_all],
        [arrow_length*sin(r*pi/180) for _, _, r in blue_data_all],
        [arrow_length*cos(r*pi/180) for _, _, r in blue_data_all],
        angles="xy",
        color=blue_all_color,
        headwidth="3",
        label="Player",
        alpha=0.5,
        sizes=[blue_arrow_size*5 for _ in blue_data_all]
    )
    qv_purple = ax.quiver(
        [x for x, _, _ in purple_data_all], 
        [y for _, y, _ in purple_data_all],
        [arrow_length*sin(r*pi/180) for _, _, r in purple_data_all],
        [arrow_length*cos(r*pi/180) for _, _, r in purple_data_all],
        angles="xy",
        color=purple_all_color,
        headwidth="8",
        label="Agent",
        alpha=0.5,
        sizes=[purple_arrow_size*5 for _ in purple_data_all]
    )


    qv_blue_past = ax.quiver(
        [x for x, _, _ in blue_data_past],
        [y for _, y, _ in blue_data_past],
        [arrow_length*sin(r*pi/180) for _, _, r in blue_data_past],
        [arrow_length*cos(r*pi/180) for _, _, r in blue_data_past],
        angles="xy",
        color=blue_past_color,
        edgecolor=blue_edge_color,
        linewidth=line_width,
        headwidth="3",
        label="Player",
        sizes=[blue_arrow_size for _ in blue_data_past]
    )
    qv_purple_past = ax.quiver(
        [x for x, _, _ in purple_data_past],
        [y for _, y, _ in purple_data_past],
        [arrow_length*sin(r*pi/180) for _, _, r in purple_data_past],
        [arrow_length*cos(r*pi/180) for _, _, r in purple_data_past],
        angles="xy",
        color=purple_past_color,
        edgecolor=purple_edge_color,
        linewidth=line_width,
        headwidth="8",
        label="Agent",
        sizes=[purple_arrow_size for _ in purple_data_past]
    )
    
    def update_time(val):
        current_time = start_time+timedelta(0, val) # set new current time depending on value of slider

        # Set what start time and end time to show
        new_start_time = current_time+timedelta(0, -shadow_time)
        new_end_time = current_time+timedelta(0, shadow_time)

        if new_start_time < start_time:
            new_start_time = start_time
        if new_end_time > end_time:
            new_end_time = end_time

        # Get positions from the times
        game_pos_data_past = pos_data.getGamePos(new_start_time, current_time)

        blue_data_past = pos_data.positionList(True, game_pos_data_past)
        purple_data_past = pos_data.positionList(False, game_pos_data_past)
        
        past_lenght = shadow_time*10

        if len(blue_data_past)!=past_lenght:
            if len(blue_data_past)==0:
                return
            while len(blue_data_past) < past_lenght:
                blue_data_past.append(blue_data_past[0])
            while len(blue_data_past) > past_lenght:
                blue_data_past.pop(-1)
        if len(purple_data_past)!=past_lenght:
            if len(purple_data_past)==0:
                return
            while len(purple_data_past) < past_lenght:
                purple_data_past.append(purple_data_past[0])
            while len(purple_data_past) > past_lenght:
                purple_data_past.pop(-1)
        
        blue_past_color = [colorFader(light_blue, dark_blue,  n/past_lenght) for n in range(past_lenght)]
        purple_past_color = [colorFader(light_purple, dark_purple,  n/past_lenght) for n in range(past_lenght)]

        # Set new points in plot
        # Update blue (human)
        qv_blue_past.set_offsets(
            [[x, y] for x, y in zip([x for x, _, _ in blue_data_past], [y for _, y, _ in blue_data_past])]
        )
        qv_blue_past.set_color(blue_past_color)
        qv_blue_past.set_edgecolor(blue_edge_color)
        qv_blue_past.set_UVC(
            [arrow_length*sin(r*pi/180) for _, _, r in blue_data_past],
            [arrow_length*cos(r*pi/180) for _, _, r in blue_data_past],
        )
        qv_blue_past.set_sizes([blue_arrow_size for _ in blue_data_past])

        # Update purple (AI agent)
        qv_purple_past.set_offsets(
            [[x, y] for x, y in zip([x for x, _, _ in purple_data_past], [y for _, y, _ in purple_data_past])]
        )
        qv_purple_past.set_color(purple_past_color)
        qv_purple_past.set_edgecolor(purple_edge_color)
        qv_purple_past.set_UVC(
            [arrow_length*sin(r*pi/180) for _, _, r in purple_data_past],
            [arrow_length*cos(r*pi/180) for _, _, r in purple_data_past],
        )
        qv_purple_past.set_sizes([purple_arrow_size for _ in purple_data_past])

        # Update plot
        fig.canvas.draw_idle()
    
    time_slider.on_changed(update_time)


    # xposition, yposition, width and height
    # ax_check = plt.axes([0.05, 0.5, 0.3, 0.3])
    ax.legend(bbox_to_anchor=(-0.2, 0.5))
    plt.show()



player_data = PlayerData(getLogData("PlayerData"))
position_data = PositionData(getLogData("Position"))
results_data = getLogData("Results")

#showRun(position_data, player_data, 0, True, False)
#showFullRunWithSliderTime(position_data, player_data, game_num, False)

print(f"Number of games: {player_data.numGames()}")
#print(position_data.pos_list[0])
#print(player_data.getStartEndTimes(0)) 

if show_all_games:
    for i in range(player_data.numGames()):
        showFullRunWithSliderTime(position_data, player_data, i)
else:
    showFullRunWithSliderTime(position_data, player_data, game_num)
