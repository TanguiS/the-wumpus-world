start_x, start_y = 3, 0

direction = 3

size = 4

goal_x, goal_y = 2, 0

DIRECTIONTABLE = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def is_forward_x():
    if DIRECTIONTABLE[direction][0] == 0:
        return goal_x == start_x
    if DIRECTIONTABLE[direction][0] > 0:
        return goal_x >= start_x
    return goal_x <= start_x


def is_forward_y():
    if DIRECTIONTABLE[direction][1] == 0:
        return goal_y == start_y
    if DIRECTIONTABLE[direction][1] > 0:
        return goal_y >= start_y
    return goal_y <= start_y


def is_forward():
    return is_forward_x() and is_forward_y()


print(is_forward())
