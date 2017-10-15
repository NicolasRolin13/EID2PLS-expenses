

def test_stupid_algo_don_t_fail_on_zero():
    square_root_i_want_to_calculate = 0
    result_1, time_taken_stupid_algo = don_t_do_that_to_calculate_square_root_it_s_awfull(
        square_root_i_want_to_calculate)

    assert result_1 == []


def test_good_algorithm_is_faster():

    square_root_i_want_to_calculate = 1787569
    result_1, time_taken_stupid_algo = don_t_do_that_to_calculate_square_root_it_s_awfull(square_root_i_want_to_calculate)

    result_1, time_taken_newton = just_to_compare_to_newton_algorithm(square_root_i_want_to_calculate)

    assert time_taken_newton < time_taken_stupid_algo


def test_decimal_is_more_reliable_than_floats():
    zero_point_three_decimal = get_zero_point_three_decimal()
    tree_times_zero_point_one_decimal = 3 * get_zero_point_one_decimal()

    assert zero_point_three_decimal == tree_times_zero_point_one_decimal

