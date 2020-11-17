import base64
import random

seed = "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"

MTRAND_N = 624
SEED_SIZE = 4993

s_tiles = [
    "<1m>", "<2m>", "<3m>", "<4m>", "<5m>", "<6m>", "<7m>", "<8m>", "<9m>",
    "<1p>", "<2p>", "<3p>", "<4p>", "<5p>", "<6p>", "<7p>", "<8p>", "<9p>",
    "<1s>", "<2s>", "<3s>", "<4s>", "<5s>", "<6s>", "<7s>", "<8s>", "<9s>",
    "<東>", "<南>", "<西>", "<北>", "<白>", "<發>", "<中>" ]


if __name__ == "__main__" :
    # mt_seed = base64.b64decode(seed)
    # rt_seed = ""
    # for i in range(MTRAND_N) :
    #     rt_seed += (mt_seed[4*i]<<24)|(mt_seed[4*i+1]<<16)|(mt_seed[4*i+2]<<8)|mt_seed[4*i+3];

    random.seed(seed)

    wall = [i for i in range(136)]


