from typing import List
from pymod.mytypes import TileType, BlockType

# 九連宝燈
def nine_gates(hand: List[int]) -> bool :
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
def big_four_winds(hand: List[int]) -> bool :
    for i in range(31, 35) :
        if hand[i] < 3 : return False
    return True


# 小喜四
def small_four_winds(hand: List[int]) -> bool :
    wind_pair_num = False
    wind_triplet_num = 0
    for i in range(31, 35) :
        if wind_pair_num is False and hand[i] == 2 : wind_pair_num = True
        elif hand[i] >= 3 : wind_triplet_num += 1
    if wind_triplet_num == 3 and wind_pair_num is True : return True
    else : return False


# 四暗刻
def four_closed_triplets( player_stealed: bool,  ron: bool , hand: List[int], winning_tile: int) -> bool :
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
def four_closed_triplets_of_single_tile_wait( player_stealed: bool , winning_tile: int, hand: List[int]) -> bool :
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
def all_honors(hand: List[int]) -> bool :
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif i < 30 : return False
    return True


# 緑一色
def all_green(hand: List[int]) -> bool :
    for i in range(1, 38) :
        if hand[i] == 0 : continue
        elif i in TileType.GREENS : continue
        else : return False
    return True


# 大三元
def big_three_dragons(hand: List[int]) :
    if hand[35] >= 3 and hand[36] >= 3 and hand[37] >= 3 : return True
    return False


# 清老頭
def all_terminals(hand: List[int]) :
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif i in TileType.TERMINALS : continue
        else : return False
    return True


# 四槓子
def four_kans(opened_hand: List[int]) :
    kan_num = 0
    for i in range(0,20,5) :
        if opened_hand[i] in BlockType.KANS : kan_num += 1
    if kan_num == 4 : return True
    return False


