import unittest
from unittest.mock import patch

from poke_battle_sim import Trainer, Pokemon, Battle


class TestBattle(unittest.TestCase):

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
    def test_critical_damage(self, mock_calculate_crit):
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
    def test_no_pp_on_all_moves(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle", "thunder"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(len(pokemon_1.moves), 2)
        pokemon_1.moves[0].cur_pp = 0
        pokemon_1.moves[1].cur_pp = 0
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR has no moves left!',
            'BULBASAUR used Struggle!',
            'CHARMANDER fainted!',
            'Ash has defeated Misty!'
        ]

        self.assertEqual(battle.last_move.name, 'struggle')
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertEqual(battle.winner, trainer_1)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    def test_no_pp_on_the_selected_move(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle", "thunder"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            self.assertEqual(len(pokemon_1.moves), 2)
            pokemon_1.moves[0].cur_pp = 0
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
            trainer_2 = Trainer('Misty', [pokemon_2])

            battle = Battle(trainer_1, trainer_2)
            battle.start()

            battle.turn(["move", "tackle"], ["move", "tackle"])
        self.assertEqual(str(context.exception), "Trainer 1 attempted to use move not in Pokemon's moveset")

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

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_invalid_pokemon_selection_trainer(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        def selection_misty(battle: Battle):
            misty = battle.t2
            misty.current_poke = misty.poke_list[0]

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
            'Misty sent out CHARMELEON!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.last_move.name, 'tackle')
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    def test_battle_turn_without_start_battle(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
            trainer_2 = Trainer('Misty', [pokemon_2])

            battle = Battle(trainer_1, trainer_2)
            battle.turn(["move", "tackle"], ["move", "tackle"])
        self.assertEqual(str(context.exception), "Cannot use turn on Battle that hasn't started")

    def test_launch_battle_with_trainer_already_in_battle(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_2 = Trainer('Misty', [pokemon_2])

            pokemon_3 = Pokemon(7, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_3 = Trainer('Red', [pokemon_3])

            battle_1 = Battle(trainer_1, trainer_2)
            battle_1.start()

            battle_2 = Battle(trainer_1, trainer_3)
            battle_2.start()

        self.assertEqual(str(context.exception), "Attempted to create Battle with Trainer already in battle")


if __name__ == '__main__':
    unittest.main()
