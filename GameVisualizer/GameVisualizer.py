import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
from datetime import datetime, timedelta
from math import cos, sin, pi


# year-month-day_hour-minutes-seconds : "yyyy-MM-dd_HH-mm-ss"
date = "2023-11-07_16-38-05"  # time to invest

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


def showRunWithSliderTime(pos_data: PositionData, player_data: PlayerData, game_num: int = 0, see_angles:bool = True) -> None:
    start_time, end_time = player_data.getStartEndTimes(game_num) # TODO change so gamne num 0 starts with event "S" instead of "ResetScene"
    duration = (end_time-start_time).total_seconds()
    shadow_time = 2 # how many seconds will show around the time set on the time slider
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

    game_pos_data_future = pos_data.getGamePos(start_time, start_time+timedelta(0, shadow_time+2))
    game_pos_data_past = [game_pos_data_future[0]]

    blue_data_future = pos_data.positionList(True, game_pos_data_future)
    purple_data_future = pos_data.positionList(False, game_pos_data_future)
    blue_data_past = pos_data.positionList(True, game_pos_data_past)
    purple_data_past = pos_data.positionList(False, game_pos_data_past)

    future_lenght = len(blue_data_future)
    past_lenght = len(blue_data_past)

    plot_color = [colorFader("green", "red", n/future_lenght) for n in range(future_lenght)]
    blue_future_color = [colorFader("blue", "white", n/future_lenght) for n in range(future_lenght)]
    purple_future_color = [colorFader("purple", "white", n/future_lenght) for n in range(future_lenght)]
    blue_past_color = [colorFader("blue", "white", n/past_lenght) for n in range(past_lenght)]
    purple_past_color = [colorFader("purple", "white", n/past_lenght) for n in range(past_lenght)]

    sc_blue_future = ax.scatter(
        [x for x, _, _ in blue_data_future][::-1],
        [y for _, y, _ in blue_data_future][::-1],
        color=blue_future_color[::-1],
        marker="o",
    )
    sc_purple_future = ax.scatter(
        [x for x, _, _ in purple_data_future][::-1],
        [y for _, y, _ in purple_data_future][::-1],
        color=purple_future_color[::-1],
        marker="o",
    )
    sc_blue_past = ax.scatter(
        [x for x, _, _ in blue_data_past],
        [y for _, y, _ in blue_data_past],
        color=blue_past_color,
        marker="o",
    )
    sc_purple_past = ax.scatter(
        [x for x, _, _ in purple_data_past],
        [y for _, y, _ in purple_data_past],
        color=purple_past_color,
        marker="o",
    )

    if see_angles:
        arrow_length = 1
        qv_blue = ax.quiver(
            [x for x, _, _ in blue_data_future],
            [y for _, y, _ in blue_data_future],
            [arrow_length*sin(r*pi/180) for _, _, r in blue_data_future],
            [arrow_length*cos(r*pi/180) for _, _, r in blue_data_future],
            angles="xy",
            color=plot_color,
            headwidth="3",
            label="Player"
        )
        qv_purple = ax.quiver(
            [x for x, _, _ in purple_data_future], 
            [y for _, y, _ in purple_data_future],
            [arrow_length*sin(r*pi/180) for _, _, r in purple_data_future],
            [arrow_length*cos(r*pi/180) for _, _, r in purple_data_future],
            angles="xy",
            color=plot_color,
            headwidth="8",
            label="Agent"
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
        game_pos_data_future = pos_data.getGamePos(current_time, new_end_time)
        game_pos_data_past = pos_data.getGamePos(new_start_time, current_time)

        blue_data_future = pos_data.positionList(True, game_pos_data_future)
        purple_data_future = pos_data.positionList(False, game_pos_data_future)
        blue_data_past = pos_data.positionList(True, game_pos_data_past)
        purple_data_past = pos_data.positionList(False, game_pos_data_past)

        future_lenght = len(blue_data_future)
        past_lenght = len(blue_data_past)
        
        # Make color for the positions
        #plot_color = [colorFader("green", "red", n/future_lenght) for n in range(future_lenght)]
        blue_future_color = [colorFader("blue", "white", n/future_lenght) for n in range(future_lenght)]
        purple_future_color = [colorFader("purple", "white", n/future_lenght) for n in range(future_lenght)]
        blue_past_color = [colorFader("white", "blue",  n/past_lenght) for n in range(past_lenght)]
        purple_past_color = [colorFader("white", "purple",  n/past_lenght) for n in range(past_lenght)]

        # Set new points in plot
        sc_blue_future.set_offsets(
            [[x, y] for x, y in zip([x for x, _, _ in blue_data_future][::-1], [y for _, y, _ in blue_data_future][::-1])]
        )
        sc_blue_future.set_color(blue_future_color[::-1])
        sc_purple_future.set_offsets(
            [[x, y] for x, y in zip([x for x, _, _ in purple_data_future][::-1], [y for _, y, _ in purple_data_future][::-1])]
        )
        sc_purple_future.set_color(purple_future_color[::-1])
        sc_blue_past.set_offsets(
            [[x, y] for x, y in zip([x for x, _, _ in blue_data_past], [y for _, y, _ in blue_data_past])]
        )
        sc_blue_past.set_color(blue_past_color)
        sc_purple_past.set_offsets(
            [[x, y] for x, y in zip([x for x, _, _ in purple_data_past], [y for _, y, _ in purple_data_past])]
        )
        sc_purple_past.set_color(purple_past_color)

        fig.canvas.draw_idle()
    
    time_slider.on_changed(update_time)

    plt.show()



player_data = PlayerData(getLogData("PlayerData"))
position_data = PositionData(getLogData("Position"))
results_data = getLogData("Results")

#showRun(position_data, player_data, 0, True, False)
showRunWithSliderTime(position_data, player_data, 0, False)

print(f"Number of games: {player_data.numGames()}")
#print(position_data.pos_list[0])
#print(player_data.getStartEndTimes(0)) 

