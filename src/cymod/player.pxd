from libcpp cimport bool

cdef class Player :
    cdef public int player_num
    cdef public int score

    cdef public bool[3] reds
    cdef public bool[3] opened_reds
    cdef public int[38] hand
    cdef public int[20] opened_hand
    cdef public int[30] discarded_tiles
    cdef public int i_dt
    cdef public int[30] discarded_state
    cdef public int i_ds
    cdef public int[30] same_turn_furiten_tiles
    cdef public int i_stft
    cdef public int[38] discarded_tiles_hist
    cdef public int[38] furiten_tiles
    cdef public bool has_stealed
    cdef public bool has_declared_ready
    cdef public bool has_declared_double_ready
    cdef public bool has_right_to_one_shot
    cdef public bool is_ready
    cdef public bool is_nagashi_mangan
    cdef public bool wins

    cdef public int opened_sets_num
    cdef public int kans_num
    cdef public int players_wind
    cdef public int last_got_tile
    cdef public int last_discarded_tile

    cdef public int shanten_num_of_kokushi
    cdef public int shanten_num_of_chiitoi
    cdef public int shanten_num_of_normal
    cdef public int shanten_num_of_temp
    cdef public int sets_num
    cdef public int pairs_num
    cdef public int tahtsu_num
    cdef public int[10] hand_composition
    cdef public int i_hc
    cdef public int dragons_num
    cdef public int winds_num
    cdef public int[38] pb_hand

    cpdef void init_game(self)
    cpdef void init_subgame(self, int rotations_num)
    cdef list effective_tiles_of_normal(self)
    cdef int calc_shanten_num_of_normal(self, int tile=*)
    cdef void pick_out_mentsu(self, int i , int[38] hand)
    cdef void pick_out_tahtsu(self, int i, int[38] hand)
    cdef list is_not_alone_tiles(self)
    cpdef void score_points(self, int points)
    cpdef void declare_ready(self, bool is_first_turn)
    cpdef void get_tile(self, int tile)
    cpdef int discard_tile(self, game, players)
    cpdef tuple discard_tile_when_player_has_declared_ready(self, game, players, int player_num)
    cpdef bool check_hand_is_ready(self, shanten_calculator)
    cdef bool has_used_up_winning_tile(self)
    cpdef bool check_nagashi_mangan(self)
    cpdef void add_furiten_tile(self, int tile)
    cpdef void add_same_turn_furiten_tile(self, int tile)
    cpdef void reset_same_turn_furiten(self)
    cpdef put_back_opened_hand(self)
    cpdef bool decide_win(self, game, int ron_tile=*)
    cpdef tuple can_steal(self, int tile, int i)
    cpdef bool can_declare_ready(self, game)
    cpdef bool can_win(self, game, int ron_tile=*)
    cdef bool is_furiten(self, bool is_chiitoi, bool is_kokushi, bool is_normal, int ron_tile)
    cdef bool has_yaku(self, game, bool ron, int ron_tile)
    cdef bool has_yaku_based_on_tiles(self, int prevailing_wind, bool ron, int ron_tile)
    cdef bool pick_out_mentsu2(self, int[38] hand, int prevailing_wind, bool ron, int ron_tile)
    cpdef void proc_ankan(self, int tile)
    cpdef tuple proc_kakan(self, int tile)
    cpdef void proc_daiminkan(self, int tile, int pos)
    cpdef int proc_pon(self, int tile, int pos)
    cpdef tuple proc_chii(self, int org_tile, int tile1, int tile2)
    cpdef void add_to_discard_tiles_after_stealing(self, int tile)
    cpdef list can_kakan(self, game)
    cpdef list can_ankan(self, game)
    cpdef tuple decide_to_kan(self, game, players)
    cpdef tuple decide_action(self, game, players)
    cpdef convert_tile_for_print(self, int tile)
    cpdef void print_hand(self)

