import heapq
import random
import time
import multiprocessing
import pygame
import math


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class ai_agent():
    mapinfo = []
    MOVING_SIZE = 8

    def __init__(self):
        self.mapinfo = []
        self.screen_rect = pygame.Rect(0, 0, 480, 416)

    # rect:					[left, top, width, height]
    # rect_type:			0:empty 1:brick 2:steel 3:water 4:grass 5:froze
    # castle_rect:			[12*16, 24*16, 32, 32]
    # mapinfo[0]: 			bullets [rect, direction, speed]]
    # mapinfo[1]: 			enemies [rect, direction, speed, type]]
    # enemy_type:			0:TYPE_BASIC 1:TYPE_FAST 2:TYPE_POWER 3:TYPE_ARMOR
    # mapinfo[2]: 			tile 	[rect, type] (empty don't be stored to mapinfo[2])
    # mapinfo[3]: 			player 	[rect, direction, speed, Is_shielded]]
    # shoot:				0:none 1:shoot
    # move_dir:				0:Up 1:Right 2:Down 3:Left 4:None
    # keep_action:			0:The tank work only when you Update_Strategy.
    #                       1:the tank keep do previous action until new Update_Strategy.

    # def Get_mapInfo:		fetch the map infomation
    # def Update_Strategy	Update your strategy


    def operations(self, p_mapinfo, c_control):

        while True:
            # -----your ai operation,This code is a random strategy,please design your ai !!-----------------------
            self.Get_mapInfo(p_mapinfo)
            # if self.mapinfo[1]:
            #     sorted_enemy = sorted(self.mapinfo[1],
            #                           key=lambda x: self.calculate_distance(x[0], self.mapinfo[3][0][0]), reverse=True)
            #     print self.mapinfo[1]
            #     print sorted_enemy
            #     print

            enemy_rect_list = self.mapinfo[1]
            # activate a_star when enemy appear
            if enemy_rect_list:
                print 'enemy found!'
                player_rect = self.mapinfo[3][0][0]
                enemy_rect = self.mapinfo[1][0][0]
                player_speed = self.mapinfo[3][0][2]
                dir_cmd = self.a_star(player_rect, enemy_rect, player_speed)
                if self.should_fire(player_rect, enemy_rect_list):
                    shoot = 1
                else:
                    shoot = 0
                if dir_cmd:
                    self.Update_Strategy(c_control, shoot, dir_cmd[0], 1)
                # for cmd in dir_cmd:
                #     if self.should_fire(player_rect, enemy_rect_list):
                #         shoot = 1
                #     else:
                #         shoot = 0
                #     self.Update_Strategy(c_control, shoot, cmd, 0)

                    # # print self.mapinfo[3]
                    # time.sleep(0.001)

                    # q = 0
                    # for i in range(10000000):
                    #     q += 1
                    # -----------
                    # self.Update_Strategy(c_control, shoot, move_dir, keep_action)
                    # ------------------------------------------------------------------------------------------------------

    def Get_mapInfo(self, p_mapinfo):
        if p_mapinfo.empty() != True:
            try:
                self.mapinfo = p_mapinfo.get(False)
            except Queue.Empty:
                skip_this = True

    def Update_Strategy(self, c_control, shoot, move_dir, keep_action):
        if c_control.empty() == True:
            c_control.put([shoot, move_dir, keep_action])
            return True
        else:
            return False

    def should_fire(self, player_rect, enemy_rect_list):
        for enemy_rect in enemy_rect_list:
            player_center_x, player_center_y = player_rect.center
            enemy_top = enemy_rect[0].top
            enemy_bottom = enemy_rect[0].bottom
            enemy_left = enemy_rect[0].left
            enemy_right = enemy_rect[0].right
            if (player_center_x >= enemy_left and player_center_x <= enemy_right) \
                    or (player_center_y >= enemy_top and player_center_y <= enemy_bottom):
                return True

    # A* algorithm, return a series of command to reach enemy
    def a_star(self, start_rect, goal_rect, speed):
        print 'trigger a*'
        start = (start_rect.left, start_rect.top)
        goal = (goal_rect.left, goal_rect.top)

        # initialise frontier
        frontier = PriorityQueue()
        came_from = {}
        cost_so_far = {}

        # put start into frontier
        frontier.put(start, 0)
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current_left, current_top = frontier.get()
            current = (current_left, current_top)

            # goal test
            temp_rect = pygame.Rect(current_left, current_top, 26, 26)
            if self.is_goal(temp_rect, goal_rect):
                break

            # try every neighbour
            for next in self.find_neighbour(current_top, current_left, speed):
                # calculate new cost
                new_cost = cost_so_far[current] + speed

                # update if next haven't visited or cost more
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        # build path

        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()

        # build command
        dir_cmd = []
        current = start
        for pos in path:
            current_left, current_top = current
            pos_left, pos_top = pos
            # up
            if pos_top < current_top:
                dir_cmd.append(0)
            # down
            elif pos_top > current_top:
                dir_cmd.append(2)
            # left
            elif pos_left < current_left:
                dir_cmd.append(3)
            # right
            elif pos_left > current_left:
                dir_cmd.append(1)
            current = pos

        return dir_cmd

    def manhattan_distance(self, a, b):
        x1, y1 = a
        x2, y2 = b
        return abs(x1 - x2) + abs(y1 - y2)

    def euclidean_distance(self, a, b):
        x1, y1 = a
        x2, y2 = b
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # heuristic func, use euclidean dist
    def heuristic(self, a, b):
        return self.manhattan_distance(a, b)

    # return True when two rects collide
    def is_goal(self, rect1, rect2):
        return rect1.colliderect(rect2)

    # return [(top,left)]
    # each time move 2px (speed)
    def find_neighbour(self, top, left, speed):

        # Rect(left, top, width, height)
        allowable_move = []

        # move up
        new_top = top - speed
        new_left = left
        if not (new_top < 0):
            move_up = True
            temp_rect = pygame.Rect(new_left, new_top, 26, 26)

            # check collision with bullet
            for bullet in self.mapinfo[0]:
                if temp_rect.colliderect(bullet[0]):
                    move_up = False
                    break

            # check collision with tile
            for tile in self.mapinfo[2]:
                # not a grass tile
                if tile[1] != 4:
                    if temp_rect.colliderect(tile[0]):
                        move_up = False
                        break

            if move_up:
                allowable_move.append((new_left, new_top))

        # move right
        new_top = top
        new_left = left + speed
        if not (new_left > (416 - 26)):
            move_right = True
            temp_rect = pygame.Rect(new_left, new_top, 26, 26)

            # check collision with bullet
            for bullet in self.mapinfo[0]:
                if temp_rect.colliderect(bullet[0]):
                    move_right = False
                    break

            # check collision with tile
            for tile in self.mapinfo[2]:
                # not a grass tile
                if tile[1] != 4:
                    if temp_rect.colliderect(tile[0]):
                        move_right = False
                        break

            if move_right:
                allowable_move.append((new_left, new_top))

        # move down
        new_top = top + speed
        new_left = left
        if not (new_top > (416 - 26)):
            move_down = True
            temp_rect = pygame.Rect(new_left, new_top, 26, 26)

            # check collision with bullet
            for bullet in self.mapinfo[0]:
                if temp_rect.colliderect(bullet[0]):
                    move_down = False
                    break

            # check collision with tile
            for tile in self.mapinfo[2]:
                # not a grass tile
                if tile[1] != 4:
                    if temp_rect.colliderect(tile[0]):
                        move_down = False
                        break

            if move_down:
                allowable_move.append((new_left, new_top))

        # move left
        new_top = top
        new_left = left - speed
        if not (new_left < 0):
            move_left = True
            temp_rect = pygame.Rect(new_left, new_top, 26, 26)

            # check collision with bullet
            for bullet in self.mapinfo[0]:
                if temp_rect.colliderect(bullet[0]):
                    move_left = False
                    break

            # check collision with tile
            for tile in self.mapinfo[2]:
                # not a grass tile
                if tile[1] != 4:
                    if temp_rect.colliderect(tile[0]):
                        move_left = False
                        break

            if move_left:
                allowable_move.append((new_left, new_top))

        return allowable_move
