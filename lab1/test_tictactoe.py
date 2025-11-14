import unittest
from tictactoe import TicTacToe


class TestTicTacToe(unittest.TestCase):

    def test_init(self):
        game = TicTacToe(3)
        self.assertEqual(game.current_player, 'X')
        self.assertFalse(game.game_over)
        self.assertEqual(game.winner, None)
        self.assertEqual(len(game.board), 3)

    def test_get_set_item_valid_move(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        self.assertEqual(game[(0, 0)], 'X')

    def test_setitem_invalid_index_type(self):
        game = TicTacToe()
        with self.assertRaises(ValueError):
            game[0] = 'X'

    def test_setitem_out_of_bounds(self):
        game = TicTacToe()
        with self.assertRaises(ValueError):
            game[(5, 5)] = 'X'

    def test_setitem_invalid_value(self):
        game = TicTacToe()
        with self.assertRaises(ValueError):
            game[(0, 0)] = 'A'

    def test_wrong_player_move(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'  
        with self.assertRaises(ValueError):
            game[(1, 1)] = 'X' 

    def test_is_valid_move(self):
        game = TicTacToe()
        self.assertTrue(game.is_valid_move(0, 0))
        game[(0, 0)] = 'X'
        self.assertFalse(game.is_valid_move(0, 0))

    def test_row_win(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        game[(1, 0)] = 'O'
        game[(0, 1)] = 'X'
        game[(1, 1)] = 'O'
        game[(0, 2)] = 'X'
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, 'X')

    def test_column_win(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        game[(0, 1)] = 'O'
        game[(1, 0)] = 'X'
        game[(1, 1)] = 'O'
        game[(2, 0)] = 'X'
        self.assertEqual(game.winner, 'X')

    def test_main_diag_win(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        game[(0, 1)] = 'O'
        game[(1, 1)] = 'X'
        game[(0, 2)] = 'O'
        game[(2, 2)] = 'X'
        self.assertEqual(game.winner, 'X')

    def test_second_diag_win(self):
        game = TicTacToe()
        game[(0, 2)] = 'X'
        game[(0, 0)] = 'O'
        game[(1, 1)] = 'X'
        game[(1, 0)] = 'O'
        game[(2, 0)] = 'X'
        self.assertTrue(game.game_over)

    def test_draw(self):
        game = TicTacToe()
        moves = [
            (0, 0, 'X'), (0, 1, 'O'), (0, 2, 'X'),
            (1, 1, 'O'), (1, 0, 'X'), (1, 2, 'O'),
            (2, 1, 'X'), (2, 0, 'O'), (2, 2, 'X'),
        ]
        for r, c, p in moves:
            game[(r, c)] = p
        self.assertTrue(game.game_over)
        self.assertIsNone(game.winner)

    def test_move_after_game_over(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        game[(1, 0)] = 'O'
        game[(0, 1)] = 'X'
        game[(1, 1)] = 'O'
        game[(0, 2)] = 'X' 

        with self.assertRaises(ValueError):
            game[(2, 2)] = 'O'

    def test_make_move_success(self):
        game = TicTacToe()
        ok = game.make_move(0, 0)
        self.assertTrue(ok)
        self.assertEqual(game[(0, 0)], 'X')

    def test_make_move_invalid(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        self.assertFalse(game.make_move(0, 0)) 

    def test_make_move_out_of_bounds(self):
        game = TicTacToe()
        self.assertFalse(game.make_move(5, 5))
    def test_get_board_state_returns_copy(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        state = game.get_board_state()

        self.assertEqual(state[0][0], 'X')
        state[0][0] = 'O'

     
        self.assertEqual(game[(0, 0)], 'X')

    def test_reset_clears_board(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        game[(1, 1)] = 'O'
        game.game_over = True
        game.winner = 'X'

        game.reset()

        for row in range(game.size):
            for col in range(game.size):
                self.assertEqual(game[(row, col)], ' ')

        self.assertEqual(game.current_player, 'X')
        self.assertFalse(game.game_over)
        self.assertIsNone(game.winner)

    def test_str_format(self):
        game = TicTacToe()
        game[(0, 0)] = 'X'
        game[(0, 1)] = 'O'
        game[(0, 2)] = 'X'

        string_repr = game.str()

        expected = (
            "X | O | X\n"
            "---------\n"
            "  |   |  \n"
            "---------\n"
            "  |   |  "
        )

        self.assertEqual(string_repr, expected)

    def test_interactive_loop_not_run(self):
        game = TicTacToe()
        self.assertIsInstance(game, TicTacToe)



if __name__ == "__main__":
    unittest.main()
