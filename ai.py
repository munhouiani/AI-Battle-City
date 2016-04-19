import random
import time
import multiprocessing
import Queue


class ai_agent():
    mapinfo = []

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

    # def Get_mapInfo:		fetch the map infomation
    # def Update_Strategy	Update your strategy

    def operations(self, p_mapinfo, c_control):

        while True:
            # -----your ai operation,This code is a random strategy,please design your ai !!-----------------------

            # print self.mapinfo[3]
            # self.Get_mapInfo(p_mapinfo)

            print self.mapinfo[3]
            # time.sleep(0.001)

            q = 0
            for i in range(10000000):
                q += 1

            # print self.mapinfo[2]

            shoot = random.randint(0, 1)
            move_dir = random.randint(0, 4)
            # -----------

            self.Update_Strategy(c_control, shoot, 4)
        # ------------------------------------------------------------------------------------------------------

    def Get_mapInfo(self, p_mapinfo):
        if p_mapinfo.empty() != True:
            try:
                self.mapinfo = p_mapinfo.get(False)
            except Queue.Empty:
                skip_this = True

    def Update_Strategy(self, c_control, shoot, move_dir):
        if c_control.empty() == True:
            c_control.put([shoot, move_dir])

    def A_Star(self, player_rect, enemy_rect):
        player_top = player_rect.y
        player_left = player_rect.x

        enermy_top = enemy_rect.y
        enermy_left = enemy_rect.x

        # initialise frontier
        frontier = Queue.PriorityQueue()
        # PriorityQueue(priority, item)
        frontier.put((0, [player_left, player_top]))
        came_from = {}
        cost_so_far = {}
        came_from[[player_left, player_top]] = None
        cost_so_far[[player_left, player_top]] = 0

        while not frontier.empty():
            current = frontier.get()[1]

            current_top = current[0]
            current_left = current[1]

            # goal test
            if current_top




    def Find_neighbour(self, top, left, tank_size, moving_size):
        allowable_move = []

        topleft = [left, top]
        topright = [left + tank_size, top]
        bottomleft = [left, top + tank_size]
        bottomright = [left + tank_size, top + tank_size]

        # move up
        up = True
        # search through tile list
        for rect in self.mapinfo[2]:
            if topleft[1] - moving_size <= rect[0].bottomleft[1] \
                    or topleft[1] - moving_size <= rect[0].bottomright[1] \
                    or topright[1] - moving_size <= rect[0].bottomleft[1] \
                    or topright[1] - moving_size <= rect[0].bottomright[1]:
                up = False
                break

        if up:
            allowable_move.append('up')

        # move down
        down = True
        # search through tile list
        for rect in self.mapinfo[2]:
            if bottomleft[1] + moving_size >= rect[0].topleft[1] \
                    or bottomleft[1] + moving_size >= rect[0].topright[1] \
                    or bottomright[1] + moving_size >= rect[0].topleft[1] \
                    or bottomright[1] + moving_size >= rect[0].topright[1]:
                down = False
                break

        if down:
            allowable_move.append('down')

        # move left
        left = True
        # search through tile list
        for rect in self.mapinfo[2]:
            if topleft[0] - moving_size <= rect[0].topright[0] \
                    or topleft[0] - moving_size <= rect[0].bottomright[0] \
                    or bottomleft[0] - moving_size <= rect[0].topright[0] \
                    or bottomleft[0] - moving_size <= rect[0].bottomright[0]:
                left = False
                break

        if left:
            allowable_move.append('left')

        # move right
        right = True
        # search through tile list
        for rect in self.mapinfo[2]:
            if topright[0] + moving_size <= rect[0].topleft[0] \
                    or topright[0] + moving_size <= rect[0].bottomleft[0] \
                    or bottomright[0] + moving_size <= rect[0].topleft[0] \
                    or bottomright[0] + moving_size <= rect[0].bottomleft[0]:
                right = False
                break
        if right:
            allowable_move.append('right')

        return allowable_move
