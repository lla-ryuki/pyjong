import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './'))

from mytypes import TileType, BlockType
from libcpp cimport bool


# 九連宝燈
cdef bool nine_gates(int[38] hand) :
    cdef int i, suit, n_tile

    suit, n_tile = 0, 0
    for i in range(31,38) :
        if hand[i] > 0 : return False
    if hand[1] > 0 : suit = 0
    elif hand[11] > 0 : suit = 1
    elif hand[21] > 0 : suit = 2
    else : return False
    for i in range(1,10) :
        n_tile += hand[i]
        if i == 1 or i == 9:
            if hand[i + (suit * 10)] < 3 : return False
        else :
            if hand[i + (suit * 10)] < 1 : return False
    if n_tile > 14 : return False
    return True


# 大喜四
cdef bool big_four_winds(int[38] hand) :
    cdef int i
    for i in range(31, 35) :
        if hand[i] < 3 : return False
    return True


# 小喜四
cdef bool small_four_winds(int[38] hand) :
    cdef int i, wind_triplet_num
    cdef bool pair

    pair = False
    wind_triplet_num = 0
    for i in range(31, 35) :
        if pair is False and hand[i] == 2 : pair = True
        elif hand[i] >= 3 : wind_triplet_num += 1
    if wind_triplet_num == 3 and pair : return True
    return False


# 四暗刻
cdef bool four_closed_triplets(bool player_stealed,  bool ron , int[38] hand, int winning_tile) :
    cdef int i, closed_triplet_num
    cdef bool pair

    if player_stealed or ron : return False
    closed_triplet_num = 0
    pair = False
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif hand[i] == 1 : return False
        elif hand[i] == 2 and pair : return False
        elif (hand[i] == 2) and (pair is False) and (i != winning_tile) : pair = True
        elif hand[i] >= 3 : closed_triplet_num += 1
    if closed_triplet_num == 4 and pair : return True
    return False


# 四暗刻単騎
cdef bool four_closed_triplets_of_single_tile_wait(bool player_stealed, int winning_tile, int[38] hand) :
    cdef int i, closed_triplet_num
    cdef bool pair

    if player_stealed : return False
    closed_triplet_num = 0
    pair = False
    for i in range(1, 38) :
        if hand[i] == 0 : continue
        elif hand[i] == 1 : return False
        elif hand[i] == 2 and i != winning_tile : return False
        elif hand[i] == 2 and i == winning_tile : pair = True
        elif hand[i] >= 3 : closed_triplet_num += 1
    if closed_triplet_num == 4 and pair : return True
    return False


# 字一色
cdef bool all_honors(int[38] hand) :
    cdef int i
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif i < 30 : return False
    return True


# 緑一色
cdef bool all_green(int[38] hand) :
    cdef int i
    for i in range(1, 38) :
        if hand[i] == 0 : continue
        elif i in TileType.GREENS : continue
        else : return False
    return True


# 大三元
cdef bool big_three_dragons(int[38] hand) :
    if hand[35] >= 3 and hand[36] >= 3 and hand[37] >= 3 : return True
    return False


# 清老頭
cdef bool all_terminals(int[38] hand) :
    cdef int i
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif i in TileType.TERMINALS : continue
        else : return False
    return True


# 四槓子
cdef bool four_kans(int[20] opened_hand) :
    cdef int i, kans_num
    kans_num = 0
    for i in range(0,20,5) :
        if opened_hand[i] in BlockType.KANS : kans_num += 1
    if kans_num == 4 : return True
    return False


