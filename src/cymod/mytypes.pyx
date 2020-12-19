cdef class TileType :
    cdef readonly int[3] REDS
    cdef readonly int[4] BLANKS
    cdef readonly int[3] FIVES
    cdef readonly int[3] NINES
    cdef readonly int[6] GREENS
    cdef readonly int[6] TERMINALS
    cdef readonly int[4] WINDS
    cdef readonly int[3] DRAGONS
    cdef readonly int[7] HONORS

    REDS      = [0, 10, 20]                   # 赤の牌番号（0:赤5萬, 10, 赤5筒, 20:赤5索）
    BLANKS    = [0, 10, 20, 30]               # handで使わない番号
    FIVES     = [5, 15, 25]                   # 各種5の牌の牌番号
    NINES     = [9, 19, 29]                   # 各種9の牌の牌番号
    GREENS    = [22, 23, 24, 26, 28, 36]      # 索子の緑 緑一色用
    TERMINALS = [1, 11, 21, 9, 19, 29]        # 端牌
    WINDS     = [31, 32, 33, 34]              # 風牌
    DRAGONS   = [35, 36, 37]                  # 白, 發, 中
    HONORS    = [31, 32, 33, 34, 35, 36, 37]  # 字牌


cdef class BlockType :
    cdef readonly int OPENED_RUN
    cdef readonly int CLOSED_RUN
    cdef readonly int OPENED_TRIPLET
    cdef readonly int CLOSED_TRIPLET
    cdef readonly int OPENED_KAN
    cdef readonly int CLOSED_KAN
    cdef readonly int PAIR

    cdef readonly int[2] RUNS
    cdef readonly int[2] TRIPLETS
    cdef readonly int[2] KANS

    OPENED_RUN = 1        # チー
    CLOSED_RUN = 2        # 順子
    OPENED_TRIPLET = 3    # ポン
    CLOSED_TRIPLET = 4    # 暗刻
    OPENED_KAN = 5        # 明槓（大明槓, 加槓）
    CLOSED_KAN = 6        # 暗槓
    PAIR = 7              # 対子

    RUNS      = [OPENED_RUN, CLOSED_RUN]
    TRIPLETS  = [OPENED_TRIPLET, CLOSED_TRIPLET]
    KANS      = [OPENED_KAN, CLOSED_KAN]



cdef class ActionType :
    cdef readonly int STEAL_RUN
    cdef readonly int STEAL_TRIPLET
    cdef readonly int STEAL_KAN
    cdef readonly int ADDED_KAN
    cdef readonly int CLOSED_KAN

    STEAL_RUN = 1        # チー
    STEAL_TRIPLET = 2    # ポン
    STEAL_KAN = 3        # 明槓
    ADDED_KAN = 4        # 加槓
    CLOSED_KAN = 5       # 暗槓
