import unittest
from unittest.mock import patch

from poke_battle_sim import Pokemon, Trainer, Battle
from poke_battle_sim.util.process_item import use_item


def get_default_battle():
    pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
    pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
    trainer_1 = Trainer('Ash', [pokemon_1, pokemon_2])

    pokemon_3 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
    pokemon_4 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
    trainer_2 = Trainer('Misty', [pokemon_3, pokemon_4])

    return Battle(trainer_1, trainer_2)


class TestUseItem(unittest.TestCase):

    @patch('poke_battle_sim.util.process_item.can_use_item')
    def test_use_item(self, mock_can_use_item):
        battle = get_default_battle()
        battle.start()

        battle.t1.current_poke.cur_hp = 50

        mock_can_use_item.return_value = True
        use_item(battle.t1, battle, "oran-berry", "0")

        expected_current_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Ash used one Oran Berry on BULBASAUR!',
            'BULBASAUR regained health!'
        ]
        self.assertEqual(battle.get_cur_text(), expected_current_text)
        self.assertEqual(battle.t1.current_poke.cur_hp, 60)


if __name__ == '__main__':
    unittest.main()
