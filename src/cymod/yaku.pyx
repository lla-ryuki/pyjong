from mytypes import TileType, BlockType
from libcpp cimport bool

# 平和 pinfu
cdef bool no_points_hand(int[:] temp, int winning_tile, int prevailing_wind, int players_wind) :
    cdef int i, runs_num
    cdef bool both_sides

    runs_num = 0
    both_sides = False
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
cdef bool all_simples(int[:] hand) :
    cdef int i
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif i % 10 in {1, 9} or i > 30 : return False
    return True


# 一盃口 iipeikou
cdef bool one_set_of_identical_sequences(int[:] temp) :
    cdef int i
    cdef int[30] check

    if two_sets_of_identical_sequences(temp) : return False
    check = [0] * 30
    for i in range(0,10,2) :
        if temp[i] == BlockType.CLOSED_RUN : check[temp[i+1]] += 1
    for i in range(1,30) :
        if check[i] == 0 : continue
        elif check[i] >= 2 : return True
    return False


# 場風 bakaze
cdef bool bakaze(int[:] hand, int prevailing_wind) :
    if hand[prevailing_wind] > 2 : return True
    return False


# 自風 jikaze
cdef bool jikaze(int[:] hand, int players_wind) :
    if hand[players_wind] >= 3 : return True
    return False


# 白 haku
cdef bool white_dragon(int[:] hand) :
    if hand[35] >= 3 : return True
    return False


# 發 hatsu
cdef bool green_dragon(int[:] hand) :
    if hand[36] >= 3 : return True
    return False


# 中 chun
cdef bool red_dragon(int[:] hand) :
    if hand[37] >= 3 : return True
    return False


# 混全帯么九 chanta
cdef bool terminal_or_honor_in_each_set(int[:] temp) :
    cdef bool honor, run
    cdef int i

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
cdef bool three_color_straight(int[:] temp) :
    cdef int i
    cdef int[30] check

    check = [0] * 30
    for i in range(0,10,2) :
        if temp[i] in BlockType.RUNS : check[temp[i+1]] += 1
    for i in range(1,10) :
        if check[i] != 0 and check[i+10] != 0 and check[i+20] != 0 : return True
    return False


# 一気通貫 ikkitsuukan
cdef bool straight(int[:] temp) :
    cdef int i
    cdef bool[9] check

    check = [False] * 9
    for i in range(0,10,2) :
        if temp[i] in {BlockType.CLOSED_RUN, BlockType.OPENED_RUN} and \
           temp[i+1] in {1, 4, 7, 11, 14, 17, 21, 24, 27} : check[(temp[i+1]-1)//3] = True
    if (check[0] and check[1] and check[2]) or \
       (check[3] and check[4] and check[5]) or \
       (check[6] and check[7] and check[8]) : return True
    return False


# 対々和 toitoi
cdef bool all_triplet_hand(int[:] temp) :
    cdef int i
    for i in range(0,10,2) :
        if temp[i] == BlockType.CLOSED_RUN or temp[i] == BlockType.OPENED_RUN : return False
    return True


# 三色同刻 sansyokudoukou
cdef bool three_color_triplets(int[:] temp) :
    cdef int i
    cdef bool[30] check

    check = [False] * 30
    for i in range(0,10,2) :
        if temp[i+1] < 30 and temp[i] in (BlockType.TRIPLETS | BlockType.KANS) : check[temp[i+1]] = True
    for i in range(1,10) :
        if check[i] and check[i+10] and check[i+20] : return True
    return False


# 混老頭 honroutou
cdef bool all_terminals_and_honors(int[:] hand) :
    cdef bool honor, terminal
    cdef int i

    honor, terminal  = False, False
    for i in range(1,38) :
        if hand[i] == 0 : continue
        if not(i % 10 in {1,9}) and i < 30 : return False
        elif i % 10 in {1,9} : terminal = True
        elif i > 30 : honor = True
    return honor and terminal


# 三槓子 sankantsu
cdef bool three_kans(int[:] temp) :
    cdef int i, kans_num

    kans_num = 0
    for i in range(0,10,2) :
        if temp[i] in BlockType.KANS : kans_num += 1
    if kans_num == 3 : return True
    return False


# 三暗刻 sannkannkou
cdef bool three_closed_triplets(int[:] temp) :
    cdef int i, closed_triprets_num

    closed_triprets_num = 0
    for i in range(0,10,2) :
        if temp[i] in {BlockType.CLOSED_TRIPLET, BlockType.CLOSED_KAN} : closed_triprets_num += 1
    if closed_triprets_num >= 3 : return True
    return False


# 小三元 syousangen
cdef bool little_three_dragons(int[:] hand) :
    cdef int i, dragons_num
    cdef bool dragon_pair

    dragon_pair = False
    dragons_num = 0
    for i in TileType.DRAGONS :
        if hand[i] == 2 and dragon_pair is False : dragon_pair = True
        elif hand[i] >= 3  : dragons_num += 1
    if dragons_num == 2 and dragon_pair : return True
    return False


# 二盃口 ryanpeikou
cdef bool two_sets_of_identical_sequences(int[:] temp) :
    cdef int i, identical_sequence_num
    cdef int[30] check

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
cdef bool half_flush(int[:] hand) :
    cdef int i, suit
    cdef bool honor

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
cdef bool terminal_in_each_set(int[:] temp) :
    cdef int i
    cdef bool run

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
cdef bool flush(int[:] hand) :
    cdef int i, suit

    suit = 0
    for i in range(1,30) :
        if hand[i] != 0 :
            suit = i // 10
            break
    for i in range(1,38) :
        if hand[i] == 0 : continue
        elif (i // 10) != suit : return False
    return True

