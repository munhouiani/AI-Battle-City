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
    MOVING_SIZE = 16
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
            # print self.mapinfo[3]
            # time.sleep(0.001)
            player_top = self.mapinfo[3][0][0].top
            player_left = self.mapinfo[3][0][0].left
            moving_speed = self.mapinfo[3][0][2]
            if self.mapinfo[1]:
                dir_cmd = self.A_Star(self.mapinfo[3][0][0], self.mapinfo[1][0][0])
                for i in range(0, self.MOVING_SIZE / moving_speed):
                    self.Update_Strategy(c_control, 0, dir_cmd[0], 0)
            # q = 0
            # for i in range(10000000):
            #     q += 1
            #
            # shoot = random.randint(0, 1)
            # move_dir = random.randint(0, 4)
            # keep_action = 0
            keep_action = 1
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

    def A_Star(self, player_rect, enemy_rect):

        player_top = player_rect.top
        player_left = player_rect.left

        enermy_top = enemy_rect.top
        enermy_left = enemy_rect.left

        start_pos =(player_left, player_top)
        # initialise frontier
        frontier = PriorityQueue()
        frontier.put(start_pos, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start_pos] = None
        cost_so_far[start_pos] = 0

        while not frontier.empty():
            current_pos = frontier.get()

            current_top = current_pos[1]
            current_left = current_pos[0]

            # goal test
            current_rect = pygame.Rect(current_left, current_top, player_rect.width, player_rect.height)
            if current_rect.colliderect(enemy_rect):
                break

            # search from neighbour
            for move in self.Find_neighbour(current_top, current_left, player_rect.width, player_rect.height,
                                            self.MOVING_SIZE):
                if move == 'up':
                    next_top = 0 if current_top - self.MOVING_SIZE < 0 else current_top - self.MOVING_SIZE
                    next_left = current_left

                elif move == 'down':
                    next_top = 416 if current_top + self.MOVING_SIZE > 416 else current_top + self.MOVING_SIZE
                    next_left = current_left
                elif move == 'left':
                    next_top = current_top
                    next_left = 0 if current_left - self.MOVING_SIZE < 0 else current_left - self.MOVING_SIZE
                elif move == 'right':
                    next_top = current_top
                    next_left = 480 if current_left + self.MOVING_SIZE > 480 else current_left + self.MOVING_SIZE

                # treat all cost from one move to another as moving size
                next_pos = (next_left, next_top)
                new_cost = cost_so_far[current_pos] + self.MOVING_SIZE
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    # heuristic cost is the euclidean distance from current to next
                    heuristic_cost = math.sqrt((current_top - next_top) ** 2 + (current_left - next_left) ** 2)
                    priority = new_cost + heuristic_cost
                    frontier.put(next_pos, priority)
                    came_from[next_pos] = current_pos

        # construct path
        # current_pos = goal_pos
        path = [current_pos]
        while current_pos != (player_left, player_top):
            current_pos = came_from[current_pos]
            path.append(current_pos)
        path.reverse()

        dir_cmd = []
        current_pos = start_pos
        for pos in path:
            current_left = current_pos[0]
            current_top = current_pos[1]
            pos_left = pos[0]
            pos_top = pos[1]
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
            current_pos = pos
        return dir_cmd

    def Find_neighbour(self, top, left, width, height, moving_size):
        allowable_move = []

        # rect [top, left, width, height]

        # move up
        if top > 0:
            move_up = True
            temp_rect = pygame.Rect(left, 0 if top - moving_size < 0 else top - moving_size, width, height)
            # check collision
            # collide with bullet
            for bullet in self.mapinfo[0]:
                if temp_rect.colliderect(bullet[0]):
                    move_up = False
                    break
            # collide with enemy
            for enemy in self.mapinfo[1]:
                if temp_rect.colliderect(enemy[0]):
                    move_up = False
                    break
            # collide with tile
            for tile in self.mapinfo[2]:
                if temp_rect.colliderect(tile[0]):
                    move_up = False
                    break
            if move_up:
                allowable_move.append('up')

        # move down
        if top < 416:
            move_down = True
            temp_rect = pygame.Rect(left, 416 if top + moving_size > 416 else top + moving_size, width, height)
            # check collision
            # collide with bullet
            for bullet in self.mapinfo[0]:
                if temp_rect.colliderect(bullet[0]):
                    move_down = False
                    break
            # collide with enemy
            for enemy in self.mapinfo[1]:
                if temp_rect.colliderect(enemy[0]):
                    move_down = False
                    break
            # collide with tile
            for tile in self.mapinfo[2]:
                if temp_rect.colliderect(tile[0]):
                    move_down = False
                    break
            if move_down:
                allowable_move.append('down')

        # move left
        if left > 0:
            move_left = True
            temp_rect = pygame.Rect(0 if left - moving_size < 0 else left - moving_size, top, width, height)
            # check collision
            # collide with bullet
            for bullet in self.mapinfo[0]:
                if temp_rect.colliderect(bullet[0]):
                    move_left = False
                    break
            # collide with enemy
            for enemy in self.mapinfo[1]:
                if temp_rect.colliderect(enemy[0]):
                    move_left = False
                    break
            # collide with tile
            for tile in self.mapinfo[2]:
                if temp_rect.colliderect(tile[0]):
                    move_left = False
                    break
            if move_left:
                allowable_move.append('left')

        # move right
        if left < 480:
            move_right = True
            temp_rect = pygame.Rect(480 if left + moving_size > 480 else left + moving_size, top, width, height)
            # check collision
            # collide with bullet
            for bullet in self.mapinfo[0]:
                if temp_rect.colliderect(bullet[0]):
                    move_right = False
                    break
            # collide with enemy
            for enemy in self.mapinfo[1]:
                if temp_rect.colliderect(enemy[0]):
                    move_right = False
                    break
            # collide with tile
            for tile in self.mapinfo[2]:
                if temp_rect.colliderect(tile[0]):
                    move_right = False
                    break
            if move_right:
                allowable_move.append('right')

        return allowable_move
