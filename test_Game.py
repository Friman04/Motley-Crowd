import unittest
from Game import Game

class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = Game("config_file_path")

    def test_main(self):
        self.game.main()
        # Add your assertions here

    def test_init_single_game(self):
        self.game.init_single_game()
        # Add your assertions here

    def test_calc_scores(self):
        ans_list = [2, 1, 3, 4, 1]
        score_list = [0, 0, 0, 0, 0]
        self.game.calc_scores(ans_list, score_list)
        # Add your assertions here

    def test_graph(self):
        self.game.graph()
        # Add your assertions here

if __name__ == '__main__':
    unittest.main()