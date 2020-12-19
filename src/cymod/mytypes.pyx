cdef class TileType :
    cdef readonly int[3] REDS      = [0, 10, 20]                   # 赤の牌番号（0:赤5萬, 10, 赤5筒, 20:赤5索）
    cdef readonly int[4] BLANKS    = [0, 10, 20, 30]               # handで使わない番号
    cdef readonly int[3] FIVES     = [5, 15, 25]                   # 各種5の牌の牌番号
    cdef readonly int[3] NINES     = [9, 19, 29]                   # 各種9の牌の牌番号
    cdef readonly int[6] GREENS    = [22, 23, 24, 26, 28, 36]      # 索子の緑 緑一色用
    cdef readonly int[6] TERMINALS = [1, 11, 21, 9, 19, 29]        # 端牌
    cdef readonly int[4] WINDS     = [31, 32, 33, 34]              # 風牌
    cdef readonly int[3] DRAGONS   = [35, 36, 37]                  # 白, 發, 中
    cdef readonly int[7] HONORS    = [31, 32, 33, 34, 35, 36, 37]  # 字牌


cdef class BlockType :
    cdef readonly int OPENED_RUN = 1        # チー
    cdef readonly int CLOSED_RUN = 2        # 順子
    cdef readonly int OPENED_TRIPLET = 3    # ポン
    cdef readonly int CLOSED_TRIPLET = 4    # 暗刻
    cdef readonly int OPENED_KAN = 5        # 明槓（大明槓, 加槓）
    cdef readonly int CLOSED_KAN = 6        # 暗槓
    cdef readonly int PAIR = 7              # 対子

    cdef readonly int[2] RUNS      = [OPENED_RUN, CLOSED_RUN]
    cdef readonly int[2] TRIPLETS  = [OPENED_TRIPLET, CLOSED_TRIPLET]
    cdef readonly int[2] KANS      = [OPENED_KAN, CLOSED_KAN]


cdef class ActionType :
    cdef readonly int STEAL_RUN = 1        # チー
    cdef readonly int STEAL_TRIPLET = 2    # ポン
    cdef readonly int STEAL_KAN = 3        # 明槓
    cdef readonly int ADDED_KAN = 4        # 加槓
    cdef readonly int CLOSED_KAN = 5       # 暗槓
