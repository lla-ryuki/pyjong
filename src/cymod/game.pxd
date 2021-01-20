from libcpp cimport bool
cdef class Game :
    # attributes
    cdef public players
    cdef public action
    cdef public logger
    cdef public shanten_calculator

    cdef public int rounds_num
    cdef public int rotations_num
    cdef public int counters_num
    cdef public int deposits_num
    cdef public bool is_over

    cdef public int prevailing_wind
    cdef public bool is_abortive_draw
    cdef public bool is_first_turn
    cdef public int[4] pao_info
    cdef public int[5] doras
    cdef public int[5] dora_indicators
    cdef public int[5] uras
    cdef public int[5] ura_indicators
    cdef public list dora_has_opened
    cdef public int[4] rinshan_tiles
    cdef public int[38] appearing_tiles
    cdef public list appearing_red_tiles
    cdef public int[136] wall
    cdef public int remain_tiles_num

    cdef public int i_player
    cdef public int i_wall
    cdef public int i_rinshan
    cdef public int i_first_turn

    cdef public int winning_tile
    cdef public int basic_points
    cdef public bool dealer_wins
    cdef public bool wins_by_ron
    cdef public bool wins_by_tenhou
    cdef public bool wins_by_chiihou
    cdef public bool wins_by_last_tile
    cdef public bool wins_by_chankan
    cdef public bool wins_by_rinshan_kaihou
    cdef public bool wins_by_pao
    cdef public int liability_player

    cdef public int players_wind
    cdef public int[10] temp
    cdef public int fu
    cdef public int han
    cdef public int i_temp
    cdef public int fu_temp
    cdef public int han_temp
    cdef public int yakuman

    cdef public bool win_flag
    cdef public bool ready_flag
    cdef public bool steal_flag
    cdef public bool dora_opens_flag
    cdef public bool rinshan_draw_flag

    cdef public bool pt_mode

    # methods
    cdef void init_game(self)
    cdef bool init_subgame(self)
    cdef void set_wall(self)
    cdef void open_new_dora(self)
    cdef void set_doras(self)
    cdef void set_rinshan_tiles(self)
    cdef int supply_next_tile(self)
    cdef int supply_next_rinshan_tile(self)
    cdef void proc_pon(self, int i_ap, int tile)
    cdef void proc_daiminkan(self, int i_ap, int tile)
    cdef void proc_chii(self, int i_ap, int tile, int tile1, int tile2)
    cdef void preproc_calculating_basic_points(self, int i_winner)
    cdef void proc_ron(self, int i_winner)
    cdef void proc_tsumo(self, int i_winner)
    cdef void proc_win(self)
    cdef void proc_drawn_game(self)
    cdef void proc_nagashi_mangan(self)
    cdef bool check_game_is_over(self, bool dealer_wins)
    cdef void check_player_wins_by_last_tile(self)
    cpdef bool is_last_tile(self)
    cdef void set_winning_tile(self, int tile)
    cdef void set_pao(self, int pao, int i_ap, int i_dp)
    cdef void increment_i_player(self)
    cdef void add_to_appearing_tiles(self, int tile)
    cdef void count_han_of_normal_hand(self, player)
    cpdef void count_han_of_seven_pairs_hand(self, player)
    cpdef int calculate_basic_points(self, player)
    cpdef void analyze_best_composition(self, player)
    cdef void pick_out_mentsu(self, bool has_stealed, int[38] hand)
    cdef void count_han(self, bool has_stealed)
    cdef int calculate_fu(self, bool has_stealed)
    cpdef void proc_draw_phase(self, player)
    cpdef void proc_ready(self, player)
    cdef void proc_ankan(self, int tile)
    cdef void proc_kakan(self, int tile)
    cdef bool proc_action_phase(self)
    cpdef int proc_discard_phase(self, player, bool ready)
    cdef void proc_ron_phase(self, int discarded_tile)
    cdef void check_game_is_abortive_draw(self, int discarded_tile)
    cpdef void proc_steal_phase(self, int discarded_tile)
    cdef void deal_starting_hand(self)
    cdef void play_subgame(self)
    cpdef void play_games(self, int games_num)
    cdef void proc_game_end(self)
    cpdef void print_scores(self, info)
    cpdef void print_win_info(self, int i_winner, int i_player, int han, int fu, int basic_points)
    cpdef void check_RYUUKYOKU_tag(self)
    cpdef bool three_players_win(self)
