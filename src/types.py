class ConstMeta(type):
    def __setattr__(self, name, value):
        if name in self.__dict__: raise TypeError(f'Can\'t rebind const ({name})')
        else: self.__setattr__(name, value)

class TileType(metaclass=ConstMeta) :
    REDS      = {0, 10, 20}                   # 赤の牌番号（0:赤5萬, 10, 赤5筒, 20:赤5索）
    BLANKS    = {0, 10, 20, 30}               # handで使わない番号
    FIVES     = {5, 15, 25}                   # 各種5の牌の牌番号
    NINES     = {9, 19, 29}                   # 各種9の牌の牌番号
    GREENS    = {22, 23, 24, 26, 28, 36}      # 索子の緑 緑一色用
    TERMINALS = {1, 11, 21, 9, 19, 29}        # 端牌
    WINDS     = {31, 32, 33, 34}              # 風牌
    DRAGONS   = {35, 36, 37}                  # 白, 發, 中
    HONORS    = {31, 32, 33, 34, 35, 36, 37}  # 字牌

class BlockType(metaclass=ConstMeta) :
    OPENED_RUN = 1        # チー
    CLOSED_RUN = 2        # 順子
    OPENED_TRIPLET = 3    # ポン
    CLOSED_TRIPLET = 4    # 暗刻
    OPENED_KAN = 5        # 明槓（大明槓, 加槓）
    CLOSED_KAN = 6        # 暗槓
    PAIR = 7              # 対子

    RUNS      = {OPENED_RUN, CLOSED_RUN}
    TRIPLETS  = {OPENED_TRIPLET, CLOSED_TRIPLET}
    KANS      = {OPENED_KAN, CLOSED_KAN}

