# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1

#
# @file agents.py
#
# @author Ducastel Matéo & Steimetz Tangui
#

from __future__ import print_function
import random
import copy
import sys


class Agent:
    """
    The base class for various flavors of the agent.
    This an implementation of the Strategy design pattern.
    """

    def init(self, gridSize):
        raise Exception("Invalid Agent class, init() not implemented")

    def think(self, percept, isTraining=False):
        raise Exception("Invalid Agent class, think() not implemented")


def pause(text):
    if sys.version_info.major >= 3:
        input(text)


class DummyAgent(Agent):
    """
    An example of simple Wumpus hunter brain: acts randomly...
    """
    isLearningAgent = False

    def init(self, gridSize):
        pass

    def think(self, percept):
        return random.choice(['shoot', 'grab', 'left', 'right', 'forward', 'forward'])

#######
# Exercise: Rational Agent
#######


class RationalAgent(Agent):
    """
    Your smartest Wumpus hunter brain.
    """
    isLearningAgent = False

    def init(self, gridSize):
        self.state = State(gridSize)
        self.current_path = []
        " *** YOUR CODE HERE ***"

    def print_world(self):
        self.state.print_world()

    def get_random_valid_action(self):
        newX, newY = self.state.get_forward_position(
            self.state.posx, self.state.posy, self.state.direction)
        print(newX, newY)
        print(self.state.worldmap[newX][newY])
        if self.state.worldmap[newX][newY] in [PITP, WUMPUSPITP, WUMPUSP, WALL]:
            return LEFT
        return FORWARD

    def find_action(self):
        # action = actionsDict.get(input(), LEFT)
        # return action
        if self.state.can_shoot_wumpus():
            return SHOOT
        if self.state.goldIsFound and not self.state.goldIsGrabbed:
            return GRAB
        if self.state.can_climb():
            return CLIMB
        if not self.current_path:
            self.current_path = self.extract_actions(self.search(self.state))
            if not self.current_path:
                print(self.state.undiscoveredPlaces)
                print("ALL PLACES EXPLORED")
                exit()
        print(self.current_path)
        return self.current_path.pop(0)

    def think(self, percept):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """
        """
        GAME IS:
        deterministic,
        not perfect information,
        zero sum,
        asynchronous
        """

        self.state.update_state_from_percepts(percept)
        self.state.set_position_wumpus_if_one_option_left()

        self.print_world()
        for i in range(3):
            print()

        action = self.find_action()

        print(action)

        self.state.update_state_from_action(action)
        return action

    def extract_actions(self, search_result):
        return [action for _, action in search_result if action is not None]

    def search(self, state):
        """
        A* Search.
        It returns the path as a list of boards (states).
        """
        from utils import PriorityQueue
        # Create initial priority queue with the initial board
        open_list = PriorityQueue()
        h = self.my_heuristic_to_get_goal_point(state)
        open_list.push([(state, None)], h)
        # Keep already visited positions
        closed_list = set([state])

        while not open_list.isEmpty():
            # Get the path at the top of the queue + the related cost
            current_path, cost = open_list.pop()
            # Get the board board of that path
            current_state = current_path[-1][0]

            # Check if we have reached the goal
            if current_state.is_goal():
                print("GOAL IS ", (current_state.posx, current_state.posy), " ",
                      current_state.get_cell(current_state.posx, current_state.posy))
                return current_path
            else:
                # Check where we can go from here
                next_boards = current_state.get_successors()
                # Add the new paths (one step longer) to the queue
                for board, action in next_boards:
                    if board not in closed_list:  # Avoid loop!
                        closed_list.add(board)
                        h = self.my_heuristic_to_get_goal_point(board)
                        open_list.push(
                            (current_path + [(board, action)]), h + len(current_path) + 1)
        return []

    def turning_cost(self, state, endx, endy):
        if state.is_forward((endx, endy)):
            return 0
        if state.direction % 2:  # y
            return 1 if state.is_forward_direction(1, state.posy, endy) else 2
        return 1 if state.is_forward_direction(0, state.posx, endx) else 2

    def my_heuristic_to_get_goal_point(self, state):
        goal_points = state.get_goal_points()
        array = [abs(state.posx - x) + abs(state.posy - y) + self.turning_cost(state, x, y) for (x, y)
                 in goal_points]
        return min(array)


STARTX = 1
STARTY = 1
WALL = '#'
UNKNOWN = '?'
WUMPUSP = 'w'
WUMPUS = 'W'
PITP = 'p'
PIT = 'P'
WUMPUSPITP = 'x'
SAFE = ' '
VISITED = '.'
GOLD = 'G'

RIGHT = 'right'
LEFT = 'left'
FORWARD = 'forward'
CLIMB = 'climb'
SHOOT = 'shoot'
GRAB = 'grab'

actionsDict = {'l': LEFT, 'f': FORWARD, 's': SHOOT}

DIRECTIONTABLE = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # North, East, South, West

directionDict = {
    0: "Up",
    1: "Right",
    2: "Down",
    3: "Left",
}


class State():
    def __init__(self, gridSize):
        self.size = gridSize
        self.worldmap = [[((y in [0, gridSize - 1] or x in [0, gridSize - 1]) and WALL) or UNKNOWN
                          for x in range(gridSize)] for y in range(gridSize)]
        self.pits_p = {}
        self.pits = []
        self.direction = 1
        self.posx = STARTX
        self.posy = STARTY
        self.wumpus_p = set()
        self.wumpusIsKilled = False
        self.wumpusPosition = None
        self.wumpusIsFound = False
        self.goldIsGrabbed = False
        self.goldIsFound = False
        self.isWin = False
        self.arrowInventory = 1
        self.undiscoveredPlaces = set()
        self.undiscoveredPlaces.add((1, 1))

    def __str__(self) -> str:
        return f'{self.posx} {self.posy} {directionDict.get(self.direction)}'

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self):
        return hash((self.posx, self.posy, self.direction))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.posx == other.posx and self.posy == other.posy and self.direction == other.direction

    def print_world(self):
        """
        For debugging purpose.
        """
        for y in range(self.size):
            for x in range(self.size):
                if self.posx == x and self.posy == y:
                    print("C ", end=' ')
                else:
                    print(self.get_cell(x, y) + " ", end=' ')
            print()

    def current_point(self):
        return (self.posx, self.posy)

    def get_cell(self, x, y):
        return self.worldmap[x][y]

    def set_cell(self, x, y, value):
        self.worldmap[x][y] = value

    def set_cell_tuple(self, point, value):
        self.set_cell(point[0], point[1], value)

    def get_cell_neighbors(self, x, y):
        return [(x + dx, y + dy) for (dx, dy) in DIRECTIONTABLE]

    def get_forward_position(self, x, y, direction):
        (dx, dy) = DIRECTIONTABLE[direction]
        return (x + dx, y + dy)

    def from_direction_to_action(self, direction):
        if direction == self.direction:
            return FORWARD
        elif direction == (self.direction + 1) % 4:
            return RIGHT
        elif direction == (self.direction + 2) % 4:
            return RIGHT
        else:
            return LEFT

    def from_action_to_direction(self, action):
        if action == RIGHT:
            return (self.direction + 1) % 4
        return (self.direction - 1) % 4

    def get_points_from_coord(self, x, y):
        return [(x + dx, y + dy)
                for (dx, dy) in DIRECTIONTABLE]

    def get_valid_points(self):
        return [(self.posx + dx, self.posy + dy)
                for (dx, dy) in DIRECTIONTABLE if self.worldmap[self.posx + dx][self.posy + dy] != WALL]

    def get_valid_points_from_coord(self, x, y):
        return [(x + dx, y + dy)
                for (dx, dy) in DIRECTIONTABLE if self.worldmap[x + dx][y + dy] != WALL]

    def is_at_start(self):
        return self.posx == STARTX and self.posy == STARTY

    def is_forward_direction(self, axis, start, goal):
        if DIRECTIONTABLE[self.direction][axis] == 0:
            return goal == start
        if DIRECTIONTABLE[self.direction][axis] > 0:
            return goal >= start
        return goal <= start

    def is_forward(self, position):
        return self.is_forward_direction(0, self.posx, position[0]) and self.is_forward_direction(1, self.posy, position[1])

    def can_shoot_wumpus(self):
        if not self.wumpusIsFound or self.wumpusIsKilled:
            return False
        return self.is_forward(self.wumpusPosition)

    def set_position_wumpus_if_one_option_left(self):
        if self.wumpusIsFound:
            return
        if len(self.wumpus_p) == 1:
            self.wumpusIsFound = True
            self.wumpusPosition = list(self.wumpus_p)[0]
            self.set_cell_tuple(self.wumpusPosition, WUMPUS)
            for (x, y) in list(self.wumpus_p):
                if (x, y) != self.wumpusPosition:
                    self.remove_wumpus_from_cell(x, y)

    def check_pit_certain(self, pitx, pity):
        for (x, y) in self.get_valid_points_from_coord(pitx, pity):
            if self.get_cell(x, y) == VISITED:
                ok = True
                for (ox, oy) in self.get_valid_points_from_coord(x, y):
                    if (ox, oy) != (pitx, pity) and self.get_cell(ox, oy) in [UNKNOWN, PIT, PITP, WUMPUSPITP, WUMPUS, WUMPUSP]:
                        ok = False
                        break
                if ok:
                    return True
        return False

    def update_pit(self, pitx, pity, curx, cury):
        if (pitx, pity) not in self.pits:
            if not self.pits_p.get((pitx, pity)):
                self.pits_p[(pitx, pity)] = set()
            self.pits_p[(pitx, pity)].add((curx, cury))
            if self.check_pit_certain(pitx, pity):
                self.pits.append((pitx, pity))
                self.worldmap[pitx][pity] = PIT
                self.pits_p.pop((pitx, pity))
                self.wumpus_p.discard((pitx, pity))

    def remove_wumpus_from_cell(self, x, y):
        self.wumpus_p.discard((x, y))
        if self.get_cell(x, y) == WUMPUSPITP:
            self.set_cell(x, y, PITP)
        else:
            self.set_cell(x, y, SAFE)
            self.undiscoveredPlaces.add((x, y))

    def update_wumpus(self):
        valid_points = self.get_valid_points()
        for (wump_x, wump_y) in list(self.wumpus_p):
            if (wump_x, wump_y) not in valid_points:
                self.remove_wumpus_from_cell(wump_x, wump_y)
        self.set_position_wumpus_if_one_option_left()

    def update_state_from_percepts(self, percept):
        """
        Updates the current environment with regards to the percept information.
        """
        if percept.scream:
            self.wumpusIsKilled = True
            if self.wumpusIsFound:
                self.set_cell(
                    self.wumpusPosition[0], self.wumpusPosition[1], VISITED)
            else:
                for (x, y) in list(self.wumpus_p):
                    self.remove_wumpus_from_cell(x, y)

        if self.wumpusIsFound:
            percept.stench = False

        if self.worldmap[self.posx][self.posy] != VISITED:
            self.undiscoveredPlaces.discard((self.posx, self.posy))
            self.worldmap[self.posx][self.posy] = VISITED
            if self.pits_p.get((self.posx, self.posy)):
                self.pits_p.pop((self.posx, self.posy))
            self.wumpus_p.discard((self.posx, self.posy))

            if percept.glitter:
                self.worldmap[self.posx][self.posy] = GOLD
                self.goldIsFound = True

            if not percept.stench and not percept.breeze:
                for (x, y) in self.get_valid_points():
                    if self.worldmap[x][y] not in [VISITED, GOLD, WUMPUS]:
                        self.worldmap[x][y] = SAFE
                        self.undiscoveredPlaces.add((x, y))
                        self.wumpus_p.discard((x, y))

            if percept.stench and not self.wumpusIsKilled and not self.wumpusIsFound and percept.breeze:
                self.update_wumpus()
                for (x, y) in self.get_valid_points():
                    if self.worldmap[x][y] in [PITP, WUMPUSPITP, UNKNOWN]:
                        self.update_pit(x, y, self.posx, self.posy)
                    if self.worldmap[x][y] == UNKNOWN:
                        self.worldmap[x][y] = WUMPUSPITP if not self.wumpusIsFound else PITP
                        self.wumpus_p.add((x, y))
                return

            if percept.stench and not self.wumpusIsKilled and not self.wumpusIsFound:
                self.update_wumpus()
                if not self.wumpusIsFound:
                    for (x, y) in self.get_valid_points():
                        if self.worldmap[x][y] == UNKNOWN and not self.wumpusIsFound:
                            self.worldmap[x][y] = WUMPUSP
                            self.wumpus_p.add((x, y))
                        if self.worldmap[x][y] == PITP:
                            self.worldmap[x][y] = SAFE
                            self.undiscoveredPlaces.add((x, y))

            if percept.stench and self.wumpusIsFound:
                for (x, y) in self.get_valid_points():
                    if (self.worldmap[x][y] == UNKNOWN) or (self.worldmap[x][y] == PITP and not percept.breeze):
                        self.worldmap[x][y] = SAFE
                        self.undiscoveredPlaces.add((x, y))

            if percept.breeze:
                for (x, y) in self.get_valid_points():
                    if self.worldmap[x][y] == UNKNOWN:
                        self.worldmap[x][y] = PITP
                    if self.get_cell(x, y) in [WUMPUSPITP, WUMPUSP] and not percept.stench:
                        self.remove_wumpus_from_cell(x, y)
                    if self.worldmap[x][y] in [PITP, WUMPUSPITP]:
                        self.update_pit(x, y, self.posx, self.posy)

    def update_state_from_action(self, action):
        if action in (RIGHT, LEFT):
            self.direction = self.from_action_to_direction(action)
            return
        if action == FORWARD:
            (self.posx, self.posy) = self.get_forward_position(
                self.posx, self.posy, self.direction)
            return
        if action == CLIMB:
            self.isWin = True
            return
        if action == SHOOT:
            self.arrowInventory = 0
            return
        if action == GRAB and self.worldmap[self.posx][self.posy] == GOLD:
            self.goldIsGrabbed = True
            self.worldmap[self.posx][self.posy] = VISITED
            return

    def is_successor(self, state, pitps):
        current_point = state.worldmap[state.posx][state.posy]
        is_safe = current_point in [SAFE, VISITED]
        is_pitp_with_no_safe = len(state.undiscoveredPlaces) == 0 and current_point == PITP and (
            state.posx, state.posy) in pitps
        is_wump_no_other_choice = current_point in [WUMPUSP, WUMPUSPITP] and (
            (len(state.undiscoveredPlaces) == 0 and len(state.pits_p) == 0))
        return is_safe or is_pitp_with_no_safe or is_wump_no_other_choice

    def get_successors(self):
        successors = []
        best_pitps = self.get_best_pitps()
        for action in [FORWARD, LEFT, RIGHT]:
            state_copy = copy.deepcopy(self)
            state_copy.update_state_from_action(action)
            if self.is_successor(state_copy, best_pitps):
                successors.append((state_copy, action))
        return successors

    def get_min_len_pitp(self):
        return min(len(self.pits_p[(x, y)]) for x, y in self.pits_p.keys())

    def get_best_pitps(self):
        if len(self.pits_p) == 0:
            return list(self.wumpus_p)
        min_l = self.get_min_len_pitp()
        return [(x, y) for x, y in self.pits_p.keys() if len(self.pits_p[(x, y)]) == min_l]

    def get_interesting_wumpus_points(self):
        safe_around_wp = [(x, y) for (wx, wy) in self.wumpus_p for (
            x, y) in self.get_valid_points_from_coord(wx, wy) if self.get_cell(x, y) in [SAFE]]
        if len(safe_around_wp) > 0:
            return safe_around_wp
        return []

    def get_goal_points(self):
        if self.goldIsGrabbed:
            if self.wumpusIsKilled or not self.undiscoveredPlaces:
                return [(STARTX, STARTY)]
            interesting_points = self.get_interesting_wumpus_points()
            if interesting_points:
                return interesting_points
            return self.undiscoveredPlaces
        if not self.undiscoveredPlaces:
            return self.get_best_pitps()
        return self.undiscoveredPlaces

    def is_goal(self):
        if self.goldIsGrabbed and self.wumpusIsFound and not self.wumpusIsKilled:
            return self.can_shoot_wumpus()
        return self.current_point() in self.get_goal_points()

    def can_climb(self):
        return self.goldIsGrabbed and self.is_at_start() and (self.wumpusIsKilled or (not self.wumpusIsFound and not self.undiscoveredPlaces))
