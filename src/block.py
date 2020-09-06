from enum import Enum

class Block(Enum) :
    ## 旧版
    # PON = 1
    # CHI = 2
    # ANKAN = 3
    # MINKAN = 4
    # ANKO = 5
    # SYUNTSU = 6
    # TOITSU = 7

    OPENED_RUN = 1        # チー
    CLOSED_RUN = 2        # 順子
    OPENED_TRIPLET = 3    # ポン
    CLOSED_TRIPLET = 4    # 暗刻
    OPENED_KAN = 5        # 明槓（大明槓, 加槓）
    CLOSED_KAN = 6        # 暗槓
    PAIR = 7              # 対子

