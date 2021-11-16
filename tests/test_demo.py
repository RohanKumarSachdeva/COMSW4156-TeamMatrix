import unittest
from Gameboard import Gameboard


class Test_TestGameboard(unittest.TestCase):

    def setUp(self):
        self.game = Gameboard()
        self.game.reset_db()

    def tearDown(self):
        del self.game

    def test_invalid_move_p2_not_connected(self):
        """Player 1 tries to move before player 2 joins the game"""

        self.game.player1 = 'red'
        self.assertEqual(self.game.move_player('p1', 3)[0], True)

    def test_invalid_move_p1_not_connected(self):
        """Player 2 tries to move before player 1 picks colour"""

        self.assertEqual(self.game.move_player('p2', 3)[0], True)

    def test_invalid_move_not_turn(self):
        """Player X tries to move when it is not their turn"""

        self.game.player1 = 'red'
        self.game.player2 = 'yellow'

        # Player 1 moves
        self.game.move_player('p1', 3)
        # Player 1 tries to move again
        self.assertEqual(self.game.move_player('p1', 4)[0], True)

        # Now player 2 moves
        self.game.move_player('p2', 3)
        # Player 2 tries to move again
        self.assertEqual(self.game.move_player('p2', 1)[0], True)

    def test_invalid_column_filled(self):
        """Player X tries to fill column which is already full"""

        self.game.player1 = 'red'
        self.game.player2 = 'yellow'

        # Fill the 4rd column
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 3)

        # Now player 1 tries to move on column 4 again
        invalid, reason, winner = self.game.move_player('p1', 3)
        self.assertEqual(invalid, True)

    def test_invalid_move_game_draw(self):
        """Player X tries to move after game has tied"""

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        # Setting board with 41 moves such that the last move
        # on 7th column would lead to a draw
        # Reference Scenario:
        # https://github.com/rishabh20/COMSW4156_Fall_21-ADVANCED-SOFTWARE-ENGINEERING/blob/part2/images/draw_scenario.png

        self.game.board = [[1, 1, 2, 2, 1, 2, 0],
                           [2, 2, 1, 2, 1, 1, 1],
                           [1, 1, 2, 1, 2, 2, 2],
                           [2, 1, 2, 1, 2, 1, 2],
                           [2, 1, 2, 2, 1, 1, 1],
                           [1, 2, 1, 1, 2, 1, 2]]

        for row in self.game.board:
            for index, item in enumerate(row):
                if item == 1:
                    row[index] = self.game.player1
                elif item == 2:
                    row[index] = self.game.player2

        # Set the appropriate values to the Gameboard instance variables
        self.game.current_turn = 'p2'
        self.game.remaining_moves = 1
        # Player 2 plays its move and the game draws
        self.game.move_player('p2', 6)

        # Player 1 tries to move now
        self.assertEqual(self.game.move_player('p1', 4)[0], True)

        # Player 2 tries to move now
        self.assertEqual(self.game.move_player('p2', 2)[0], True)

        # Clear board and retrieve state from db
        self.game = None
        self.game = Gameboard()
        self.game.update_state()
        self.assertEqual(self.game.game_result, 'Draw')
        self.assertEqual(self.game.current_turn, '')

    def test_win_on_last_move(self):
        """Test if game state is properly retrieved when
        player 2 wins on 42nd move"""

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        # Reference Scenario
        # https://github.com/rishabh20/COMSW4156_Fall_21-ADVANCED-SOFTWARE-ENGINEERING/blob/part3/images/win_last_move.png

        self.game.board = \
            [['yellow', 'red', 'yellow', 'red', 'red', 'yellow', 0],
             ['yellow', 'red', 'yellow', 'red', 'yellow', 'red', 'yellow'],
             ['red', 'red', 'yellow', 'yellow', 'red', 'yellow', 'red'],
             ['yellow', 'yellow', 'red', 'red', 'yellow', 'red', 'yellow'],
             ['red', 'red', 'yellow', 'red', 'yellow', 'red', 'yellow'],
             ['yellow', 'red', 'yellow', 'red', 'yellow', 'yellow', 'red']]

        # Set the appropriate values to the Gameboard instance variables
        self.game.current_turn = 'p2'
        self.game.remaining_moves = 1
        # Player 2 plays its move and the game draws
        self.game.move_player('p2', 6)

        # Clear board and retrieve state from db
        self.game = None
        self.game = Gameboard()
        self.game.update_state()
        self.assertEqual(self.game.game_result, 'Player 2')
        self.assertEqual(self.game.current_turn, '')

    def test_invalid_move_game_won(self):
        """Player X tried to move when there is already a winner"""

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        self.game.move_player('p1', 2)
        self.game.move_player('p2', 2)
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 4)
        self.game.move_player('p2', 4)
        # Player 1 makes move on 6th column and connects 4 tokens horizontally
        self.game.move_player('p1', 5)

        invalid, reason, winner = self.game.move_player('p2', 5)
        self.assertEqual((invalid, winner), (True, 'Player 1'))

        invalid, reason, winner = self.game.move_player('p1', 0)
        self.assertEqual((invalid, winner), (True, 'Player 1'))

    def test_happy_path_correct_move(self):
        """
        Test if current move is a valid/happy move
        """

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        # Player 1 makes move on 3rd column
        self.assertEqual(self.game.move_player('p1', 2)[0], False)
        self.assertEqual(self.game.board[5][2], self.game.player1)

        # Player 1 makes move on 4th column
        self.assertEqual(self.game.move_player('p2', 3)[0], False)
        self.assertEqual(self.game.board[5][3], self.game.player2)

    def test_horizontal_win_move_right(self):
        """
        Test if current move leads to winning horizontally
        by placing winning token on right side of 3
        horizontally connected tokens
        """

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        self.game.move_player('p1', 2)
        self.game.move_player('p2', 2)
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 4)
        self.game.move_player('p2', 4)

        # Player 1 makes move on 6th column and connects 4 tokens horizontally
        invalid, reason, winner = self.game.move_player('p1', 5)
        self.assertEqual((invalid, winner), (False, 'Player 1'))

    def test_horizontal_win_move_left(self):
        """
        Test if current move leads to winning horizontally
        by placing winning token on left side of 3
        horizontally connected tokens
        """

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        self.game.move_player('p1', 2)
        self.game.move_player('p2', 2)
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 4)
        self.game.move_player('p2', 4)

        # Player 1 makes move on 2nd column and connects 4 tokens horizontally
        invalid, reason, winner = self.game.move_player('p1', 1)
        self.assertEqual((invalid, winner), (False, 'Player 1'))

    def test_vertical_win_move_top(self):
        """
        Test if current move leads to winning vertically
        by placing winning token on top of 3 vertically
        connected tokens
        """

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        self.game.move_player('p1', 2)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 1)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 0)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 0)

        # Player 2 makes move on 4th column and connects 4 tokens vertically
        invalid, reason, winner = self.game.move_player('p2', 3)
        self.assertEqual((invalid, winner), (False, 'Player 2'))

    def test_diagonal_win_move_bottom_right(self):
        """
        Test if current move leads to winning diagonally
        by placing winning token such that 4 tokens are
        connected in South East direction
        """

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        self.game.move_player('p1', 3)
        self.game.move_player('p2', 2)
        self.game.move_player('p1', 2)
        self.game.move_player('p2', 1)
        self.game.move_player('p1', 1)
        self.game.move_player('p2', 0)
        self.game.move_player('p1', 1)
        self.game.move_player('p2', 0)
        self.game.move_player('p1', 0)
        self.game.move_player('p2', 5)

        # Player 1 makes move on 1st column and connects 4 tokens diagonally
        invalid, reason, winner = self.game.move_player('p1', 0)
        self.assertEqual((invalid, winner), (False, 'Player 1'))

    def test_diagonal_win_move_bottom_left(self):
        """
        Test if current move leads to winning diagonally
        by placing winning token such that 4 tokens are
        connected in South West direction
        """

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        self.game.move_player('p1', 0)
        self.game.move_player('p2', 1)
        self.game.move_player('p1', 1)
        self.game.move_player('p2', 2)
        self.game.move_player('p1', 2)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 2)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 5)

        # Player 1 makes move on 4th column and connects 4 tokens diagonally
        invalid, reason, winner = self.game.move_player('p1', 3)
        self.assertEqual((invalid, winner), (False, 'Player 1'))

    def test_diagonal_win_move_top_right(self):
        """
        Test if current move leads to winning diagonally
        by placing winning token such that 4 tokens are
        connected in North East direction
        """

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        self.game.move_player('p1', 1)
        self.game.move_player('p2', 1)
        self.game.move_player('p1', 2)
        self.game.move_player('p2', 2)
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 2)
        self.game.move_player('p1', 3)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 5)
        self.game.move_player('p2', 3)
        self.game.move_player('p1', 5)

        # Player 2 makes move on 1st column and connects 4 tokens diagonally
        invalid, reason, winner = self.game.move_player('p2', 0)
        self.assertEqual((invalid, winner), (False, 'Player 2'))

    def test_diagonal_win_move_top_left(self):
        """
        Test if current move leads to winning diagonally
        by placing winning token such that 4 tokens are
        connected in North West direction
        """

        self.game.player1 = 'yellow'
        self.game.player2 = 'red'

        self.game.move_player('p1', 2)
        self.game.move_player('p2', 2)
        self.game.move_player('p1', 1)
        self.game.move_player('p2', 1)
        self.game.move_player('p1', 0)
        self.game.move_player('p2', 1)
        self.game.move_player('p1', 0)
        self.game.move_player('p2', 0)
        self.game.move_player('p1', 5)
        self.game.move_player('p2', 0)
        self.game.move_player('p1', 5)

        # Player 2 makes move on 4th column and connects 4 tokens diagonally
        invalid, reason, winner = self.game.move_player('p2', 3)
        self.assertEqual((invalid, winner), (False, 'Player 2'))

    def test_db_persistence(self):
        """Test if state of board is persisted"""

        self.game.player1 = 'red'
        self.game.player2 = 'yellow'
        self.game.move_player('p1', 2)
        self.game.move_player('p2', 4)

        self.game = None
        self.game = Gameboard()
        self.game.update_state()
        self.assertEqual(self.game.player1, 'red')
        self.assertEqual(self.game.player2, 'yellow')
        self.assertEqual(self.game.remaining_moves, 40)
        self.assertEqual(self.game.current_turn, 'p1')


if __name__ == '__main__':
    unittest.main()
