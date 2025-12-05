import unittest
from tictactoe import TicTacToe   # <-- поправь имя файла под своё

class TestTicTacToe(unittest.TestCase):

    def setUp(self):
        self.game = TicTacToe()

    # --- базовые состояния ---
    def test_initial_state(self):
        self.assertEqual(self.game.current_player, 'X')
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)
        self.assertEqual(self.game.get_board_state(),
                         [[' ', ' ', ' '],
                          [' ', ' ', ' '],
                          [' ', ' ', ' ']])

    def test_is_valid_move(self):
        self.assertTrue(self.game.is_valid_move(0, 0))
        self.game[(0, 0)] = 'X'
        self.assertFalse(self.game.is_valid_move(0, 0))
        self.assertFalse(self.game.is_valid_move(-1, 0))
        self.assertFalse(self.game.is_valid_move(10, 10))

    # --- setitem ошибки ---
    def test_setitem_wrong_index(self):
        with self.assertRaises(ValueError):
            self.game["WAT"] = 'X'
        with self.assertRaises(ValueError):
            self.game[(1,)] = 'X'

    def test_setitem_invalid_cell(self):
        self.game[(0, 0)] = 'X'
        with self.assertRaises(ValueError):
            self.game[(0, 0)] = 'X'

    def test_setitem_wrong_symbol(self):
        with self.assertRaises(ValueError):
            self.game[(0, 0)] = "Z"

    def test_setitem_wrong_turn(self):
        self.game[(0, 0)] = 'X'
        with self.assertRaises(ValueError):
            self.game[(1, 1)] = 'X'

    # --- смена хода ---
    def test_turn_switch(self):
        self.game[(0, 0)] = 'X'
        self.assertEqual(self.game.current_player, 'O')
        self.game[(1, 1)] = 'O'
        self.assertEqual(self.game.current_player, 'X')

    # --- победы ---
    def test_win_row(self):
        self.game[(0, 0)] = 'X'
        self.game[(1, 0)] = 'O'
        self.game[(0, 1)] = 'X'
        self.game[(1, 1)] = 'O'
        self.game[(0, 2)] = 'X'
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'X')

    def test_win_col(self):
        self.game[(0, 0)] = 'X'
        self.game[(0, 1)] = 'O'
        self.game[(1, 0)] = 'X'
        self.game[(1, 1)] = 'O'
        self.game[(2, 0)] = 'X'
        self.assertEqual(self.game.winner, 'X')

    def test_win_main_diagonal(self):
        self.game[(0, 0)] = 'X'
        self.game[(0, 1)] = 'O'
        self.game[(1, 1)] = 'X'
        self.game[(0, 2)] = 'O'
        self.game[(2, 2)] = 'X'
        self.assertEqual(self.game.winner, 'X')

    def test_win_anti_diagonal(self):
        self.game[(0, 2)] = 'X'
        self.game[(0, 0)] = 'O'
        self.game[(1, 1)] = 'X'
        self.game[(1, 0)] = 'O'
        self.game[(2, 0)] = 'X'
        self.game[(2, 0)] = 'X'
        self.game[(2, 0)] = 'X'

    # --- ничья ---
    def test_draw(self):
        # X O X
        # X X O
        # O X O
        moves = [
            ('X', (0, 0)), ('O', (0, 1)),
            ('X', (0, 2)), ('O', (1, 2)),
            ('X', (1, 1)), ('O', (2, 0)),
            ('X', (1, 0)), ('O', (2, 2)),
            ('X', (2, 1)),
        ]

        for symbol, (r, c) in moves:
            self.assertEqual(self.game.current_player, symbol)
            self.game[(r, c)] = symbol

        self.assertTrue(self.game.game_over)
        self.assertIsNone(self.game.winner)

    # --- make_move ---
    def test_make_move_valid(self):
        ok = self.game.make_move(0, 0)
        self.assertTrue(ok)
        self.assertEqual(self.game[(0, 0)], 'X')

    def test_make_move_invalid(self):
        self.game[(0, 0)] = 'X'
        self.assertFalse(self.game.make_move(0, 0))

    def test_make_move_out_of_bounds(self):
        self.assertFalse(self.game.make_move(10, 10))

    # --- reset ---
    def test_reset(self):
        self.game[(0, 0)] = 'X'
        self.game.reset()
        self.assertEqual(self.game.current_player, 'X')
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)
        self.assertEqual(self.game.board,
                         [[' ', ' ', ' '],
                          [' ', ' ', ' '],
                          [' ', ' ', ' ']])

    # --- строковое представление ---
    def test_str_representation(self):
        self.game[(0, 0)] = 'X'
        txt = self.game.str()
        self.assertIn("X |   |  ", txt)
        self.assertIn("---", txt)


if __name__ == "__main__":
    unittest.main()
