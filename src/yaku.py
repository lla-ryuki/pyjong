from typing import List
from mytypes import TileType, BlockType

# 平和 pinfu
def no_points_hand(temp: List[int], winning_tile: int , prevailing_wind: int, players_wind: int) -> bool :
    runs_num = 0
    for i in range(0,10,2) :
        if temp[i] == BlockType.PAIR :
            if temp[i+1] == prevailing_wind or temp[i+1] == players_wind or temp[i+1] >= 35 : return False
        elif temp[i] != BlockType.CLOSED_RUN : return False
        else :
            runs_num += 1
            if (temp[i+1] == winning_tile - 2 and temp[i+1] % 10 >= 2) or (temp[i+1] == winning_tile and temp[i+1] % 10 < 7) : both_sides = True
    if runs_num == 4 and both_sides : return True
    return False


# 断么 tannyao
def all_simples(hand: List[int]) -> bool :
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif i % 10 in {1, 9} or i > 30 : return False
    return True


# 一盃口 iipeikou
def one_set_of_identical_sequences(temp: List[int]) -> bool :
    if two_sets_of_identical_sequences(temp) : return False
    check = [0] * 30
    for i in range(0,10,2) :
        if temp[i] == BlockType.CLOSED_RUN : check[temp[i+1]] += 1
    for i in range(1,30) :
        if check[i] == 0 : continue
        elif check[i] >= 2 : return True
    return False


# 場風 bakaze
def prevailing_wind(hand: List[int], prevailing_wind: int) -> bool :
    if hand[prevailing_wind] > 2 : return True
    else : return False


# 自風 jikaze
def players_wind(hand: List[int], players_wind: int) -> bool :
    if hand[players_wind] >= 3 : return True
    return False


# 白 haku
def white_dragon(hand: List[int]) -> bool :
    if hand[35] >= 3 : return True
    return False


# 發 hatsu
def green_dragon(hand: List[int]) -> bool :
    if hand[36] >= 3 : return True
    return False


# 中 chun
def red_dragon(hand: List[int]) -> bool :
    if hand[37] >= 3 : return True
    return False


# 混全帯么九 chanta
def terminal_or_honor_in_each_set(temp: List[int]) -> bool :
    honor, run = False, False
    for i in range(0,10,2) :
        if temp[i] == BlockType.PAIR :
            if not((temp[i+1] % 10) in {1, 9} or temp[i+1] > 30) : return False
            if temp[i+1] > 30 : honor = True
        elif temp[i] in BlockType.RUNS :
            if not((temp[i+1] % 10) in {1, 7}) : return False
            run = True
        elif temp[i] in (BlockType.TRIPLETS | BlockType.KANS) :
            if not((temp[i+1] % 10) in [1,9] or temp[i+1] > 30) : return False
            if temp[i+1] > 30 : honor = True
    return honor and run


# 三色同順 sansyokudoujun
def three_color_straight(temp: List[int]) -> bool :
    check = [0] * 30
    for i in range(0,10,2) :
        if temp[i] in BlockType.RUNS : check[temp[i+1]] += 1
    for i in range(1,10) :
        if check[i] != 0 and check[i+10] != 0 and check[i+20] != 0 : return True
    return False


# 一気通貫 ikkitsuukan
def straight(temp: List[int]) -> bool :
    check = [False] * 9
    for i in range(0,10,2) :
        if temp[i] == BlockType.CLOSED_RUN or temp[i] == BlockType.OPENED_RUN :
            if temp[i+1] in {1, 4, 7, 11, 14, 17, 21, 24, 27} : check[i] = True
    if (check[0] and check[1] and check[2]) or \
       (check[3] and check[4] and check[5]) or \
       (check[6] and check[7] and check[8]) : return True

    return False


# 対々和 toitoi
def all_triplet_hand(temp: List[int]) -> bool :
    for i in range(0,10,2) :
        if temp[i] == BlockType.CLOSED_RUN or temp[i] == BlockType.OPENED_RUN : return False
    return True


# 三色同刻 sansyokudoukou
def three_color_triplets(temp: List[int]) -> bool :
    check = [False] * 30
    for i in range(0,10,2) :
        if temp[i] in (BlockType.TRIPLETS | BlockType.KANS) and i < 30 : check[temp[i+1]] = True
    for i in range(1,10) :
        if check[i] and check[i+10] and check[i+20] : return True
    return False


# 混老頭 honroutou
def all_terminals_and_honors(hand: List[int]) -> bool :
    honor = False
    terminal = False
    for i in range(1,38) :
        if hand[i] == 0 : continue
        if not(i % 10 in {1,9}) and i < 30 : return False
        elif i % 10 in {1,9} : terminal = True
        elif i > 30 : honor = True
    return honor and terminal


# 三槓子 sankantsu
def three_kans(temp: List[int]) -> bool :
    kans_num = 0
    for i in range(0,10,2) :
        if temp[i] in BlockType.KANS : kans_num += 1
    if kans_num == 3 : return True
    return False


# 三暗刻 sannkannkou
def three_closed_triplets(temp: List[int]) -> bool :
    closed_triprets_num = 0
    for i in range(0,10,2) :
        if temp[i] in {BlockType.CLOSED_TRIPLET, BlockType.CLOSED_KAN} : closed_triprets_num += 1
    if closed_triprets_num >= 3 : return True
    return False


# 小三元 syousangen
def little_three_dragons(hand: List[int]) -> bool :
    dragon_pair = False
    dragons_num = 0
    for i in TileType.DRAGONS :
        if hand[i] == 2 and dragon_pair is False : dragon_pair = True
        elif hand[i] >= 3  : dragons_num += 1
    if dragons_num == 2 and dragon_pair : return True
    return False


# 二盃口 ryanpeikou
def two_sets_of_identical_sequences(temp: List[int]) -> bool :
    check = [0] * 30
    identical_sequence_num = 0
    for i in range(0,10,2) :
        if temp[i] == BlockType.CLOSED_RUN : check[temp[i+1]] += 1
    for i in range(1,30) :
        if check[i] == 0 : continue
        elif check[i] >= 2 and check[i] < 4 : identical_sequence_num += 1
        elif check[i] == 4 : identical_sequence_num += 2
    if identical_sequence_num >= 2 : return True
    return False


# 混一色 honitsu
def half_flush(hand: List[int]) -> bool :
    suit = 0
    honor = False
    for i in range(1,38) :
        if hand[i] == 0 : continue
        suit = i // 10
        break
    for i in range(1,30) :
        if hand[i] == 0 : continue
        elif (i // 10) != suit : return False
    for i in range(31, 38) :
        if hand[i] > 0 :
            honor = True
            break
    return honor


# 純全帯么九 junchanta
def terminal_in_each_set(temp: List[int]) -> bool :
    run = False
    for i in range(0,10,2) :
        if temp[i] == BlockType.PAIR :
            if not(temp[i+1] % 10 in [1,9] and temp[i+1] < 30): return False
        elif temp[i] in BlockType.RUNS :
            if not((temp[i+1] % 10) in [1, 7]) : return False
            run = True
        elif temp[i] in (BlockType.TRIPLETS | BlockType.KANS) :
            if not(temp[i+1] % 10 in [1,9] and temp[i+1] < 30) : return False
    return run


# 清一色 chinitsu
def flush(hand: List[int]) -> bool :
    suit = 0
    for i in range(1,30) :
        if hand[i] != 0 :
            suit = i // 10
            break
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif (i // 10) != suit : return False
    return True


