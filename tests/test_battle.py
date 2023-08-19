import unittest
from unittest.mock import patch

from poke_battle_sim import Trainer, Pokemon, Battle


class TestPokemon(unittest.TestCase):

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_simple_battle(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        self.assertFalse(battle.battle_started)
        battle.start()
        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.turn_count, 0)

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'CHARMANDER fainted!',
            'Ash has defeated Misty!'
        ]

        self.assertEqual(battle.last_move.name, 'tackle')
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertEqual(battle.winner, trainer_1)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_critical_in_simple_battle(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = True
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'A critical hit!',
            'CHARMANDER fainted!',
            'Ash has defeated Misty!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.last_move.name, 'tackle')
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertEqual(battle.winner, trainer_1)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_default_trainer_selection(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_4 = Pokemon(6, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2, pokemon_3, pokemon_4])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'CHARMANDER fainted!',
            'Misty sent out CHARMELEON!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.last_move.name, 'tackle')
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_trainer_selection_initialization(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        def selection_misty(battle: Battle):
            misty = battle.t2
            misty.current_poke = misty.poke_list[-1]
        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_4 = Pokemon(6, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2, pokemon_3, pokemon_4], selection_misty)

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'CHARMANDER fainted!',
            'Misty sent out CHARIZARD!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.last_move.name, 'tackle')
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)


if __name__ == '__main__':
    unittest.main()
