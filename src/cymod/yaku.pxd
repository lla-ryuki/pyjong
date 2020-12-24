from libcpp cimport bool

cdef bool no_points_hand(int[:], int, int, int)
cdef bool all_simples(int[:])
cdef bool one_set_of_identical_sequences(int[:])
cdef bool bakaze(int[:], int)
cdef bool jikaze(int[:], int)
cdef bool white_dragon(int[:])
cdef bool green_dragon(int[:])
cdef bool red_dragon(int[:])
cdef bool terminal_or_honor_in_each_set(int[:])
cdef bool three_color_straight(int[:])
cdef bool straight(int[:])
cdef bool all_triplet_hand(int[:])
cdef bool three_color_triplets(int[:])
cdef bool all_terminals_and_honors(int[:])
cdef bool three_kans(int[:])
cdef bool three_closed_triplets(int[:])
cdef bool little_three_dragons(int[:])
cdef bool two_sets_of_identical_sequences(int[:])
cdef bool half_flush(int[:])
cdef bool terminal_in_each_set(int[:])
cdef bool flush(int[:])