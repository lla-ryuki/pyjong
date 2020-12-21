from libcpp cimport bool

cdef bool nine_gates(int[:])
cdef bool big_four_winds(int[:])
cdef bool small_four_winds(int[:])
cdef bool four_closed_triplets(bool,  bool, int[:], int)
cdef bool four_closed_triplets_of_single_tile_wait(bool, int, int[:])
cdef bool all_honors(int[:])
cdef bool all_green(int[:])
cdef bool big_three_dragons(int[:])
cdef bool all_terminals(int[:])
cdef bool four_kans(int[:])
