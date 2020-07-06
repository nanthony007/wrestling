# module for result enum

import enum


@enum.unique
class Result(enum.IntEnum):
    WIN_DECISION = 1
    WIN_MAJOR = 2
    WIN_TECH = 3
    WIN_FALL = 4
    LOSS_DECISION = -1
    LOSS_MAJOR = -2
    LOSS_TECH = -3
    LOSS_FALL = -4

    def __init__(self, num):
        super().__init__()
        self.win = True if num > 0 else False
        self.bonus = True if num > 1 or num < -1 else False
        self.pin = True if num == 4 else False

    @property
    def text(self):
        #  split string
        x = self.name.split('_')
        return f"{x[0].capitalize()} {x[1].capitalize()}"

    @property
    def team_points(self):
        if self.value == 1:
            return 3
        elif self.value == 2:
            return 4
        elif self.value == 3:
            return 5
        elif self.value == 4:
            return 6
        else:  # loss
            return 0
