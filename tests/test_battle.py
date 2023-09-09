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
        self.assertEqual(battle.battlefield.get_terrain(), 'other')

    def test_battle_with_terrain(self):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, terrain="water")

        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.battlefield.get_terrain(), 'water')

    def test_battle_with_invalid_terrain(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
            trainer_2 = Trainer('Misty', [pokemon_2])

            Battle(trainer_1, trainer_2, terrain="invalid_terrain")
        self.assertEqual(str(context.exception), "Attempted to create Battle with invalid terrain type")

    def test_battle_with_weather(self):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="rain")

        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.battlefield.weather, 'rain')

    def test_battle_with_invalid_weather(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
            trainer_2 = Trainer('Misty', [pokemon_2])

            Battle(trainer_1, trainer_2, weather="invalid_weather")
        self.assertEqual(str(context.exception), "Attempted to create Battle with invalid weather")

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_battle_with_weather_has_infinite_duration(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 1, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 1, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="rain")
        battle.start()

        expected_battle_text = ['Ash sent out BULBASAUR!', 'Misty sent out CHARMANDER!']

        mock_calculate_crit.return_value = False
        for turn_i in range(1, 12):
            battle.turn(["move", "tackle"], ["move", "tackle"])
            expected_battle_text += [
                'Turn ' + str(turn_i) + ':', 'BULBASAUR used Tackle!', 'CHARMANDER used Tackle!', 'Rain continues to fall.'
            ]
            self.assertEqual(battle.battlefield.weather, 'rain')

        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 11)
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

        def selection_misty(trainer: Trainer):
            trainer.current_poke = trainer.poke_list[-1]
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

        def selection_misty(trainer: Trainer):
            trainer.current_poke = trainer.poke_list[0]

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

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_use_heal_item(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(5, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["item", "oran-berry", "0"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'Ash used one Oran Berry on BULBASAUR!',
            'BULBASAUR regained health!',
            'CHARMELEON used Splash!',
            'But nothing happened!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t1.current_poke.cur_hp, 60)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_use_pp_restore_item(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_1.moves[0].cur_pp = 15
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["item", "leppa-berry", "0", "0"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'Ash used one Leppa Berry on BULBASAUR!',
            'BULBASAUR\'s Tackle\'s pp was restored!',
            'CHARMELEON used Tackle!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)
        self.assertEqual(battle.t1.current_poke.moves[0].cur_pp, 25)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_automatic_use_of_item(self, mock_calculate_crit, mock_calculate_multiplier):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=60, item="oran-berry")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 300, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        self.assertEqual(pokemon_1.item, 'oran-berry')
        self.assertEqual(pokemon_1.o_item, 'oran-berry')
        self.assertEqual(pokemon_1.h_item, 'oran-berry')

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'CHARMELEON used Tackle!',
            'BULBASAUR used Tackle!',
            'BULBASAUR ate its Oran Berry!',
            'BULBASAUR regained health!'
        ]

        self.assertIsNone(pokemon_1.item)
        self.assertEqual(pokemon_1.o_item, 'oran-berry')
        self.assertIsNone(pokemon_1.h_item)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t1.current_poke.cur_hp, 43)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_automatic_use_of_item_not_working_on_potion(self, mock_calculate_crit, mock_calculate_multiplier):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=60, item="potion")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 300, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        self.assertEqual(pokemon_1.item, 'potion')
        self.assertEqual(pokemon_1.o_item, 'potion')
        self.assertEqual(pokemon_1.h_item, 'potion')

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'CHARMELEON used Tackle!',
            'BULBASAUR used Tackle!'
        ]

        self.assertEqual(pokemon_1.item, 'potion')
        self.assertEqual(pokemon_1.o_item, 'potion')
        self.assertEqual(pokemon_1.h_item, 'potion')

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t1.current_poke.cur_hp, 33)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_switch_out(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1, pokemon_2])

        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_3])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["other", "switch"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'Ash sent out IVYSAUR!',
            'CHARMELEON used Tackle!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)
        self.assertEqual(battle.t1.current_poke, pokemon_2)

    def test_switch_out_with_one_pokemon_in_team(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_2 = Trainer('Misty', [pokemon_2])

            battle = Battle(trainer_1, trainer_2)
            battle.start()

            battle.turn(["other", "switch"], ["move", "tackle"])
        self.assertEqual(str(context.exception), "Trainer attempted make an invalid switch out")

    def test_switch_out_with_trapped_pokemon(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1, pokemon_2])

            pokemon_3 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_2 = Trainer('Misty', [pokemon_3])

            battle = Battle(trainer_1, trainer_2)
            battle.start()

            pokemon_1.trapped = True

            battle.turn(["other", "switch"], ["move", "tackle"])
        self.assertEqual(str(context.exception), "Trainer attempted to switch out Pokemon that's trapped")

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_natural_cure_healing_on_switch_out(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100], ability="natural-cure")
        pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_1.nv_status = 5
        pokemon_1.nv_counter = 2
        trainer_1 = Trainer('Ash', [pokemon_1, pokemon_2])

        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_3])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["other", "switch"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'Ash sent out IVYSAUR!',
            'CHARMELEON used Tackle!'
        ]

        self.assertEqual(pokemon_1.nv_status, 0)
        self.assertEqual(pokemon_1.nv_counter, 0)
        self.assertEqual(pokemon_2.nv_status, 0)
        self.assertEqual(pokemon_2.nv_counter, 0)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)
        self.assertEqual(battle.t1.current_poke, pokemon_2)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_weather_ball_water_type(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["weather-ball"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["rain-dance"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "weather-ball"], ["move", "rain-dance"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Rain Dance!',
            'It started to rain!',
            'BULBASAUR used Weather Ball!',
            "It's super effective!",
            'Rain continues to fall.'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_weather_ball_rock_type(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["weather-ball"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["sandstorm"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "weather-ball"], ["move", "sandstorm"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Sandstorm!',
            'A sandstorm brewed',
            'BULBASAUR used Weather Ball!',
            "It's super effective!",
            'The sandstorm is raging.',
            'CHARMANDER is buffeted by the Sandstorm!',
            'BULBASAUR is buffeted by the Sandstorm!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_weather_ball_clear_weather(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["weather-ball"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(92, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "weather-ball"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out GASTLY!',
            'Turn 1:',
            'GASTLY used Tackle!',
            'BULBASAUR used Weather Ball!',
            "It doesn't affect GASTLY"
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_fire_blast(self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss, mock_status):
        pokemon_1 = Pokemon(1, 22, ["fire-blast"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "fire-blast"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Fire Blast!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 88)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_default_natural_power(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_status
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Tri Attack!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 81)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_natural_power_in_building(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_status
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "building")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Tri Attack!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 81)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_natural_power_in_sand(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "sand")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Earthquake!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 53)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._flinch')
    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_natural_power_in_cave(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss, mock_flinch
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "cave")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Rock Slide!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 64)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_natural_power_in_tall_grass(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "tall-grass")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Seed Bomb!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 86)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_natural_power_in_water(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "water")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Hydro Pump!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 49)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_natural_power_in_snow(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss, mock_status
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "snow")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Blizzard!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 88)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_natural_power_in_ice(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_status
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "ice")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Ice Beam!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 90)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_earthquake(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["earthquake"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "earthquake"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Earthquake!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 53)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_earthquake_in_digging_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["earthquake"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["dig"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "earthquake"], ["move", "dig"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER burrowed its way under the ground!',
            'BULBASAUR used Earthquake!',
            "It's super effective!"
        ]

        self.assertEqual(pokemon_2.cur_hp, 10)
        self.assertEqual(pokemon_1.moves[0].power, 100)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_stealth_roc(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["stealth-rock"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2, pokemon_3])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "stealth-rock"], ["move", "tackle"])
        battle.turn(["move", "stealth-rock"], ["other", "switch"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Tackle!',
            'BULBASAUR used Stealth Rock!',
            "Pointed stones float in the air around Misty's team!",
            'Turn 2:',
            'Misty sent out CHARMELEON!',
            'Pointed stones dug into CHARMELEON!',
            'BULBASAUR used Stealth Rock!',
            'But, it failed!'
        ]

        self.assertEqual(pokemon_3.cur_hp, 75)

        self.assertEqual(battle.t1.stealth_rock, 0)
        self.assertEqual(battle.t2.stealth_rock, 1)
        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 2)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    def test_defog_stealth_roc(self):
        pokemon_1 = Pokemon(1, 22, ["defog"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["stealth-rock"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        battle.turn(["move", "defog"], ["move", "stealth-rock"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Stealth Rock!',
            "Pointed stones float in the air around Ash's team!",
            'BULBASAUR used Defog!',
            "CHARMANDER's evasion fell!"
        ]

        self.assertEqual(battle.t1.stealth_rock, 0)
        self.assertEqual(battle.t2.stealth_rock, 0)
        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    def test_defog_remove_fog(self):
        pokemon_1 = Pokemon(1, 22, ["defog"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="fog")
        battle.start()

        battle.turn(["move", "defog"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Splash!',
            'But nothing happened!',
            'BULBASAUR used Defog!',
            "CHARMANDER's evasion fell!"
        ]

        self.assertEqual(battle.battlefield.weather, "clear")
        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_rapid_spin_stealth_roc(self, mock_calculate_crit, mock_calculate_multiplier):
        pokemon_1 = Pokemon(1, 22, ["rapid-spin"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["stealth-rock"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "rapid-spin"], ["move", "stealth-rock"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Stealth Rock!',
            "Pointed stones float in the air around Ash's team!",
            'BULBASAUR used Rapid Spin!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 88)

        self.assertEqual(battle.t1.stealth_rock, 0)
        self.assertEqual(battle.t2.stealth_rock, 0)
        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_surf(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["surf"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "surf"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Surf!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 58)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_surf_in_diving_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["surf"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["dive"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "surf"], ["move", "dive"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER hid underwater!',
            'BULBASAUR used Surf!',
            "It's super effective!"
        ]

        self.assertEqual(pokemon_2.cur_hp, 19)
        self.assertEqual(pokemon_1.moves[0].power, 90)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._generate_2_to_5')
    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_whirlpool(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss, mock_turns
    ):
        pokemon_1 = Pokemon(1, 22, ["whirlpool"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        mock_turns.return_value = 2
        battle.turn(["move", "whirlpool"], ["move", "tackle"])

        self.assertEqual(pokemon_2.cur_hp, 75)
        self.assertEqual(pokemon_2.binding_poke, pokemon_1)
        self.assertEqual(pokemon_2.binding_type, "Whirlpool")
        self.assertEqual(pokemon_2.v_status[3], 1)

        battle.turn(["move", "whirlpool"], ["move", "tackle"])

        self.assertEqual(pokemon_2.cur_hp, 50)
        self.assertIsNone(pokemon_2.binding_poke)
        self.assertIsNone(pokemon_2.binding_type)

        battle.turn(["move", "whirlpool"], ["move", "tackle"])

        self.assertEqual(pokemon_2.cur_hp, 25)
        self.assertEqual(pokemon_2.binding_poke, pokemon_1)
        self.assertEqual(pokemon_2.binding_type, "Whirlpool")
        self.assertEqual(pokemon_2.v_status[3], 1)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Whirlpool!',
            "It's super effective!",
            'CHARMANDER was trapped in the vortex!',
            'CHARMANDER used Tackle!',
            'CHARMANDER is hurt by Whirlpool!',
            'Turn 2:',
            'BULBASAUR used Whirlpool!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'CHARMANDER is hurt by Whirlpool!',
            'Turn 3:',
            'BULBASAUR used Whirlpool!',
            "It's super effective!",
            'CHARMANDER was trapped in the vortex!',
            'CHARMANDER used Tackle!',
            'CHARMANDER is hurt by Whirlpool!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 3)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_whirlpool_in_diving_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss
    ):
        pokemon_1 = Pokemon(1, 22, ["whirlpool"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["dive"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "whirlpool"], ["move", "dive"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER hid underwater!',
            'BULBASAUR used Whirlpool!',
            "It's super effective!",
            'CHARMANDER was trapped in the vortex!',
            'CHARMANDER is hurt by Whirlpool!'
        ]

        self.assertEqual(battle.get_all_text(), expected_battle_text)

        self.assertEqual(pokemon_2.cur_hp, 60)
        self.assertEqual(pokemon_1.moves[0].power, 35)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_low_kick_in_diving_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["low-kick"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["dive"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "low-kick"], ["move", "dive"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER hid underwater!',
            'BULBASAUR used Low Kick!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 94)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_gust(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["gust"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "gust"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Gust!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.cur_hp, 90)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_gust_in_air_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss
    ):
        pokemon_1 = Pokemon(1, 22, ["gust"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["bounce"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "gust"], ["move", "bounce"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER sprang up!',
            'BULBASAUR used Gust!'
        ]

        self.assertEqual(battle.get_all_text(), expected_battle_text)

        self.assertEqual(pokemon_2.cur_hp, 81)
        self.assertEqual(pokemon_1.moves[0].power, 40)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_struggle(self, mock_calculate_crit, mock_calculate_multiplier):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_1.moves[0].cur_pp = 0
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "tackle"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR has no moves left!',
            'BULBASAUR used Struggle!',
            'BULBASAUR is hit with recoil!',
            'CHARMANDER used Splash!',
            'But nothing happened!'
        ]

        self.assertEqual(pokemon_1.cur_hp, 75)
        self.assertEqual(pokemon_1.cur_hp, 75)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.last_move.name, 'splash')
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._flinch')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_stomp(
            self, mock_calculate_crit, mock_calculate_multiplier, _
    ):
        pokemon_1 = Pokemon(1, 22, ["stomp"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "stomp"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Stomp!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(pokemon_2.evasion_stage, 0)
        self.assertEqual(pokemon_2.cur_hp, 84)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_stomp_in_minimized_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision
    ):
        pokemon_1 = Pokemon(1, 22, ["stomp"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["minimize"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 76
        battle.turn(["move", "stomp"], ["move", "minimize"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Minimize!',
            "CHARMANDER's evasion rose!",
            'BULBASAUR used Stomp!'
        ]

        self.assertEqual(pokemon_2.evasion_stage, 1)
        self.assertEqual(pokemon_2.cur_hp, 70)
        self.assertEqual(pokemon_1.moves[0].power, 65)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_stomp_in_other_evasion_move_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision
    ):
        pokemon_1 = Pokemon(1, 22, ["stomp"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["double-team"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 76
        battle.turn(["move", "stomp"], ["move", "double-team"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Double Team!',
            "CHARMANDER's evasion rose!",
            'BULBASAUR used Stomp!',
            'CHARMANDER avoided the attack!'
        ]

        self.assertEqual(pokemon_2.evasion_stage, 1)
        self.assertEqual(pokemon_2.cur_hp, 100)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_absorb(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["absorb"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "absorb"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'SQUIRTLE used Splash!',
            'But nothing happened!',
            'BULBASAUR used Absorb!',
            "It's super effective!",
            "SQUIRTLE had it's energy drained!"
        ]

        self.assertEqual(pokemon_1.cur_hp, 59)
        self.assertEqual(pokemon_2.cur_hp, 82)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_crit')
    def test_absorb_on_heal_block(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["absorb"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["heal-block"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "absorb"], ["move", "heal-block"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'SQUIRTLE used Heal Block!',
            'BULBASAUR was prevented from healing!',
            'BULBASAUR used Absorb!',
            "It's super effective!"
        ]

        self.assertEqual(pokemon_1.cur_hp, 50)
        self.assertEqual(pokemon_2.cur_hp, 82)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    def test_leech_seed(self, mock_calculate_hit_or_miss):
        pokemon_1 = Pokemon(1, 22, ["leech-seed"], "male", stats_actual=[100, 100, 100, 100, 100, 100], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "leech-seed"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'BULBASAUR used Leech Seed!',
            'SQUIRTLE was seeded!',
            'SQUIRTLE used Splash!',
            'But nothing happened!',
            "SQUIRTLE's health is sapped by Leech Seed!",
            'BULBASAUR regained health!'
        ]

        self.assertEqual(pokemon_1.cur_hp, 62)
        self.assertEqual(pokemon_2.cur_hp, 88)
        self.assertEqual(pokemon_2.v_status[2], 1)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    def test_leech_seed_on_heal_block(self, mock_calculate_hit_or_miss):
        pokemon_1 = Pokemon(1, 22, ["leech-seed"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["heal-block"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "leech-seed"], ["move", "heal-block"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'SQUIRTLE used Heal Block!',
            'BULBASAUR was prevented from healing!',
            'BULBASAUR used Leech Seed!',
            'SQUIRTLE was seeded!',
            "SQUIRTLE's health is sapped by Leech Seed!"
        ]

        self.assertEqual(pokemon_1.cur_hp, 50)
        self.assertEqual(pokemon_2.cur_hp, 88)
        self.assertEqual(pokemon_2.v_status[2], 1)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    def test_aqua_ring(self):
        pokemon_1 = Pokemon(1, 22, ["aqua-ring"], "male", stats_actual=[100, 100, 100, 100, 100, 100], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        battle.turn(["move", "aqua-ring"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'BULBASAUR used Aqua Ring!',
            'BULBASAUR surrounded itself with a veil of water!',
            'SQUIRTLE used Splash!',
            'But nothing happened!',
            "A veil of water restored BULBASAUR's HP!"
        ]

        self.assertEqual(pokemon_1.cur_hp, 56)
        self.assertEqual(pokemon_2.cur_hp, 100)
        self.assertEqual(pokemon_1.v_status[8], 1)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)

    def test_aqua_ring_on_heal_block(self):
        pokemon_1 = Pokemon(1, 22, ["aqua-ring"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["heal-block"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        battle.turn(["move", "aqua-ring"], ["move", "heal-block"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'SQUIRTLE used Heal Block!',
            'BULBASAUR was prevented from healing!',
            'BULBASAUR used Aqua Ring!',
            'BULBASAUR surrounded itself with a veil of water!'
        ]

        self.assertEqual(pokemon_1.cur_hp, 50)
        self.assertEqual(pokemon_2.cur_hp, 100)
        self.assertEqual(pokemon_1.v_status[8], 1)

        self.assertTrue(battle.battle_started)
        self.assertEqual(battle.t1, trainer_1)
        self.assertEqual(battle.t2, trainer_2)
        self.assertEqual(battle.turn_count, 1)
        self.assertIsNone(battle.winner)
        self.assertEqual(battle.get_all_text(), expected_battle_text)


if __name__ == '__main__':
    unittest.main()
