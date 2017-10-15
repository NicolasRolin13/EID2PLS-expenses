


def get_zero_point_three_decimal():
    return Decimal("0.3")


def get_zero_point_one_decimal():
    return Decimal("0.1")


def don_t_do_that_to_calculate_square_root_it_s_awfull(number_for_witch_i_want_the_square_root):

    tic = time.time()
    for wannabe_square_root in range(number_for_witch_i_want_the_square_root):
        result_dict = defaultdict(list)
        result_dict[wannabe_square_root**2] = wannabe_square_root

    time_taken_for_the_calculus = time.time() - tic

    return result_dict[number_for_witch_i_want_the_square_root], time_taken_for_the_calculus


def just_to_compare_to_newton_algorithm(number_for_witch_i_want_the_square_root):
    tic = time.time()

    x = number_for_witch_i_want_the_square_root
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + number_for_witch_i_want_the_square_root // x) // 2

    time_taken_for_the_calculus = time.time() - tic
    return x, time_taken_for_the_calculus