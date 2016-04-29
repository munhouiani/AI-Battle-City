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
    # castle rect
    castle = pygame.Rect(12 * 16, 24 * 16, 32, 32)

    def __init__(self):
        self.mapinfo = []

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
            player_rect = self.mapinfo[3][0][0]
            sorted_enemy = sorted(self.mapinfo[1],
                                  key=lambda x: self.manhattan_distance((x[0].left, x[0].top), (12 * 16, 24 * 16)))

            # activate a_star when enemy appear
            if sorted_enemy:
                # print 'enemy found!'
                enemy_rect = sorted_enemy[0][0]
                dir_cmd = self.a_star(player_rect, enemy_rect, 6)

                inline_dir = self.inline_with_enemy(player_rect, enemy_rect)
                shoot = 0
                if inline_dir is not False:
                    shoot = 1
                    self.Update_Strategy(c_control, shoot, inline_dir, 1)
                    # time.sleep(pygame.time.Clock().tick(50) * 0.001)
                print dir_cmd
                if dir_cmd is not None:
                    self.Update_Strategy(c_control, shoot, dir_cmd, 1)
                    if self.mapinfo[0]:
                        self.bullet_avoidance(self.mapinfo[3][0], self.mapinfo[0], c_control)
                    # time.sleep(pygame.time.Clock().tick(50) * 0.001)
                    # ------------------------------------------------------------------------------------------------------

    def Get_mapInfo(self, p_mapinfo):
        if p_mapinfo.empty() != True:
            try:
                self.mapinfo = p_mapinfo.get(False)
            except Queue.Empty:
                skip_this = True

    def Update_Strategy(self, c_control, shoot, move_dir, keep_action):
        if c_control.empty() == True:
            c_control.put([shoot, move_dir])
            return True
        else:
            return False

    def should_fire(self, player_rect, enemy_rect_info_list):
        for enemy_rect_info in enemy_rect_info_list:
            if self.inline_with_enemy(player_rect, enemy_rect_info[0]):
                return True

    # A* algorithm, return a series of command to reach enemy
    def a_star(self, start_rect, goal_rect, speed):
        # print 'trigger a*'
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
            for next in self.find_neighbour(current_top, current_left, speed, goal_rect):
                # calculate new cost
                new_cost = cost_so_far[current] + speed

                # update if next haven't visited or cost more
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        # build path
        # dir_cmd = []
        # while current != start:
        #     parent = came_from[current]
        #     parent_left, parent_top = parent
        #     current_left, current_top = current
        #     # up
        #     if current_top < parent_top:
        #         dir_cmd.append(0)
        #     # down
        #     elif current_top > parent_top:
        #         dir_cmd.append(2)
        #     # left
        #     elif current_left < parent_left:
        #         dir_cmd.append(3)
        #     # right
        #     elif current_left > parent_left:
        #         dir_cmd.append(1)
        #     current = came_from[current]
        # dir_cmd.reverse()

        # return the first move is enough
        next = None
        dir_cmd = None
        while current != start:
            next = current
            current = came_from[current]

        if next:
            next_left, next_top = next
            current_left, current_top = current
            # up
            if current_top > next_top:
                dir_cmd = 0
            # down
            elif current_top < next_top:
                dir_cmd = 2
            # left
            elif current_left > next_left:
                dir_cmd = 3
            # right
            elif current_left < next_left:
                dir_cmd = 1
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
        # center_x1, center_y1 = rect1.center
        # if rect1.colliderect(rect2) and \
        #         ((rect2.left <= center_x1 <= rect2.left + rect2.width) \
        #                  or (rect2.top <= center_y1 <= rect2.top + rect2.height)):
        #     return True
        # else:
        #     return False
        return rect1.colliderect(rect2)
        # return self.inline_with_enemy(rect1, rect2) or rect1.colliderect(rect2)
        if self.inline_with_enemy(rect1, rect2) is not False or rect1.colliderect(rect2):
            return True
        else:
            return False

    # return [(top,left)]
    # each time move 2px (speed)
    def find_neighbour(self, top, left, speed, goal_rect):

        # Rect(left, top, width, height)
        allowable_move = []

        # move up
        new_top = top - speed
        new_left = left
        if not (new_top < 0):
            move_up = True
            temp_rect = pygame.Rect(new_left, new_top, 26, 26)

            # check collision with enemy except goal
            for enemy in self.mapinfo[1]:
                if enemy[0] is not goal_rect:
                    if temp_rect.colliderect(enemy[0]):
                        move_up = False
                        break

            # check collision with bullet
            # for bullet in self.mapinfo[0]:
            #     if temp_rect.colliderect(bullet[0]):
            #         move_up = False
            #         break

            # check collision with tile
            if move_up:
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

            # check collision with enemy except goal
            for enemy in self.mapinfo[1]:
                if enemy[0] is not goal_rect:
                    if temp_rect.colliderect(enemy[0]):
                        move_right = False
                        break

            # check collision with bullet
            # for bullet in self.mapinfo[0]:
            #     if temp_rect.colliderect(bullet[0]):
            #         move_right = False
            #         break

            # check collision with tile
            if move_right:
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

            # check collision with enemy except goal
            for enemy in self.mapinfo[1]:
                if enemy[0] is not goal_rect:
                    if temp_rect.colliderect(enemy[0]):
                        move_down = False
                        break

            # check collision with bullet
            # for bullet in self.mapinfo[0]:
            #     if temp_rect.colliderect(bullet[0]):
            #         move_down = False
            #         break

            # check collision with
            if move_down:
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

            # check collision with enemy except goal
            for enemy in self.mapinfo[1]:
                if enemy[0] is not goal_rect:
                    if temp_rect.colliderect(enemy[0]):
                        move_left = False
                        break

            # check collision with bullet
            # for bullet in self.mapinfo[0]:
            #     if temp_rect.colliderect(bullet[0]):
            #         move_left = False
            #         break

            # check collision with tile
            if move_left:
                for tile in self.mapinfo[2]:
                    # not a grass tile
                    if tile[1] != 4:
                        if temp_rect.colliderect(tile[0]):
                            move_left = False
                            break

            if move_left:
                allowable_move.append((new_left, new_top))

        return allowable_move

    def inline_with_enemy(self, player_rect, enemy_rect):
        # horizontal inline
        if enemy_rect.top <= player_rect.centery <= enemy_rect.bottom:
            # enemy on left
            if enemy_rect.right <= player_rect.left:
                # check any tile in between
                for tile in self.mapinfo[2]:
                    # not a grass or water tile
                    if tile[1] != 4 or tile[1] != 3:
                        # tile is between player and enemy
                        if enemy_rect.right <= tile[0].left and tile[0].right <= player_rect.left:
                            if tile[0].top <= player_rect.centery <= tile[0].bottom:
                                return False
                return 3
            # enemy on right
            elif player_rect.right <= enemy_rect.right:
                # check any tile in between
                for tile in self.mapinfo[2]:
                    # not a grass or water tile
                    if tile[1] != 4 or tile[1] != 3:
                        # tile is between player and enemy
                        if player_rect.right <= tile[0].left and tile[0].right <= enemy_rect.left:
                            if tile[0].top <= player_rect.centery <= tile[0].bottom:
                                return False
                return 1
        # vertically inline
        elif enemy_rect.left <= player_rect.centerx <= enemy_rect.right:
            # enemy on top
            if enemy_rect.bottom <= player_rect.top:
                # check any tile in between
                for tile in self.mapinfo[2]:
                    # not a grass or water tile
                    if tile[1] != 4 or tile[1] != 3:
                        # tile is between player and enemy
                        if enemy_rect.bottom <= tile[0].top and tile[0].bottom <= player_rect.top:
                            if tile[0].left <= player_rect.centerx <= tile[0].right:
                                return False
                return 0
            # enemy on bottom
            elif player_rect.bottom <= enemy_rect.top:
                # check any tile in between
                for tile in self.mapinfo[2]:
                    # not a grass or water tile
                    if tile[1] != 4 or tile[1] != 3:
                        # tile is between player and enemy
                        if player_rect.bottom <= tile[0].top and tile[0].bottom <= enemy_rect.top:
                            if tile[0].left <= player_rect.centerx <= tile[0].right:
                                return False
                return 2
        return False

    def bullet_avoidance(self, player_info, bullet_info_list, c_control):

        return False



        # player_direction = player_info[1]
        # player_rect = player_info[0]
        # for bullet_info in bullet_info_list:
        #     bullet_direction = bullet_info[1]
        #     bullet_rect = bullet_info[0]
        #
        #     # bullet on left hand size and direction to right
        #     if bullet_rect.right <= player_rect.left \
        #             and bullet_direction == 1 \
        #             and bullet_rect.bottom >= player_rect.top and bullet_rect.top <= player_rect.bottom:  # bullet can shoot player
        #
        #         should_avoid = True
        #         # check if tile in between
        #         for tile_info in self.mapinfo[2]:
        #             # not a grass or water tile
        #             if tile_info[1] != 4 or tile_info[1] != 3:
        #                 tile_rect = tile_info[0]
        #                 # tile is between player and bullet
        #                 if bullet_rect.right <= tile_rect.left and tile_rect.right <= player_rect.right:
        #                     # tile can block bullet
        #                     if bullet_rect.bottom >= tile_rect.top and bullet_rect.top <= tile_rect.bottom:
        #                         should_avoid = False
        #                         break
        #         if should_avoid:
        #             # player can shoot
        #             if bullet_rect.top <= player_rect.centery <= bullet_rect.bottom:
        #                 self.Update_Strategy(c_control, 1, 3, 1)
        #             # run
        #             else:
        #                 # run up
        #                 if not(player_rect.top-2 < 0):
        #                     move_up = True
        #                     new_left = player_rect.left
        #                     new_top = player_rect.top - 2
        #                     temp_rect = pygame.Rect(new_left, new_top, 26, 26)
        #
        #                     # check collision with enemy except goal
        #                     if move_up:
        #                         for enemy in self.mapinfo[1]:
        #                             if temp_rect.colliderect(enemy[0]):
        #                                 move_up = False
        #                                 break
        #
        #                     # check collision with bullet
        #                     if move_up:
        #                         for bullet in self.mapinfo[0]:
        #                             if temp_rect.colliderect(bullet[0]):
        #                                 move_up = False
        #                                 break
        #
        #                     # check collision with tile
        #                     if move_up:
        #                         for tile in self.mapinfo[2]:
        #                             # not a grass tile
        #                             if tile[1] != 4:
        #                                 if temp_rect.colliderect(tile[0]):
        #                                     move_up = False
        #                                     break
        #                     if move_up:
        #                         self.Update_Strategy(c_control, 0, 0, 1)
        #                     else:
        #                         self.Update_Strategy(c_control, 0, 2, 1)
        #                 # else run down
        #                 else:
        #                     self.Update_Strategy(c_control, 0, 2, 1)
        #
        #     # bullet on right hand size and direction to left
        #     elif player_rect.right <= bullet_rect.left \
        #             and bullet_direction == 6 \
        #             and bullet_rect.bottom >= player_rect.top and bullet_rect.top <= player_rect.bottom:  # bullet can shoot player
        #
        #         should_avoid = True
        #         # check if tile in between
        #         for tile_info in self.mapinfo[2]:
        #             # not a grass or water tile
        #             if tile_info[1] != 4 or tile_info[1] != 3:
        #                 tile_rect = tile_info[0]
        #                 # tile is between player and bullet
        #                 if player_rect.right <= tile_rect.left and tile_rect.right <= bullet_rect.right:
        #                     # tile can block bullet
        #                     if bullet_rect.bottom >= tile_rect.top and bullet_rect.top <= tile_rect.bottom:
        #                         should_avoid = False
        #                         break
        #         if should_avoid:
        #             # player can shoot
        #             if bullet_rect.top <= player_rect.centery <= bullet_rect.bottom:
        #                 self.Update_Strategy(c_control, 1, 3, 1)
        #             # run
        #             else:
        #                 # run up
        #                 if not (player_rect.top - 2 < 0):
        #                     move_up = True
        #                     new_left = player_rect.left
        #                     new_top = player_rect.top - 2
        #                     temp_rect = pygame.Rect(new_left, new_top, 26, 26)
        #
        #                     # check collision with enemy except goal
        #                     if move_up:
        #                         for enemy in self.mapinfo[1]:
        #                             if temp_rect.colliderect(enemy[0]):
        #                                 move_up = False
        #                                 break
        #
        #                     # check collision with bullet
        #                     if move_up:
        #                         for bullet in self.mapinfo[0]:
        #                             if temp_rect.colliderect(bullet[0]):
        #                                 move_up = False
        #                                 break
        #
        #                     # check collision with tile
        #                     if move_up:
        #                         for tile in self.mapinfo[2]:
        #                             # not a grass tile
        #                             if tile[1] != 4:
        #                                 if temp_rect.colliderect(tile[0]):
        #                                     move_up = False
        #                                     break
        #                     if move_up:
        #                         self.Update_Strategy(c_control, 0, 0, 1)
        #                     else:
        #                         self.Update_Strategy(c_control, 0, 2, 1)
        #                 # else run down
        #                 else:
        #                     self.Update_Strategy(c_control, 0, 2, 1)
