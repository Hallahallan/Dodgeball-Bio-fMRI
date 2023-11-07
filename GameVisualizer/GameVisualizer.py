import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
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

    fig, ax = plt.subplots()

    game_pos_data = pos_data.getGamePos(start_time, end_time)

    blue_data = pos_data.positionList(True, game_pos_data)
    purple_data = pos_data.positionList(False, game_pos_data)
    run_lenght = len(blue_data)
    plot_color = [colorFader("green", "red", n/run_lenght) for n in range(run_lenght)]
    blue_color = [colorFader("blue", "yellow", n/run_lenght) for n in range(run_lenght)]
    purple_color = [colorFader("purple", "orange", n/run_lenght) for n in range(run_lenght)]
    
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


player_data = PlayerData(getLogData("PlayerData"))
position_data = PositionData(getLogData("Position"))
results_data = getLogData("Results")

showRun(position_data, player_data, 0, True, True)

print(f"Number of games: {player_data.numGames()}")
#print(position_data.pos_list[0])
#print(player_data.getStartEndTimes(0))

