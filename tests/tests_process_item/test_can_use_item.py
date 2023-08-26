import unittest

from poke_battle_sim import Pokemon, Trainer, Battle
from poke_battle_sim.util.process_item import can_use_item


def get_default_battle():
    pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
    pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
    trainer_1 = Trainer('Ash', [pokemon_1, pokemon_2])

    pokemon_3 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
    pokemon_4 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
    trainer_2 = Trainer('Misty', [pokemon_3, pokemon_4])

    return Battle(trainer_1, trainer_2)


class TestCanUseItem(unittest.TestCase):

    def test_can_use_heal_item(self):
        battle = get_default_battle()
        battle.start()

        battle.t1.current_poke.cur_hp = 50
        result = can_use_item(battle.t1, battle, "oran-berry", "0")

        self.assertTrue(result)

    def test_can_use_heal_item_with_full_health(self):
        battle = get_default_battle()
        battle.start()

        result = can_use_item(battle.t1, battle, "oran-berry", "0")

        self.assertFalse(result)

    def test_can_use_item_with_invalid_target_pos(self):
        battle = get_default_battle()
        battle.start()

        battle.t1.current_poke.cur_hp = 50
        result = can_use_item(battle.t1, battle, "oran-berry", "BULBASAUR")

        self.assertFalse(result)

    def test_can_use_item_on_current_pokemon_with_embargo(self):
        battle = get_default_battle()
        battle.start()

        battle.t1.current_poke.embargo_count = 1
        battle.t1.current_poke.cur_hp = 50
        result = can_use_item(battle.t1, battle, "oran-berry", "0")

        self.assertFalse(result)

    def test_can_use_item_on_team_pokemon_with_embargo(self):
        battle = get_default_battle()
        battle.start()

        battle.t1.current_poke.embargo_count = 1
        battle.t1.poke_list[1].cur_hp = 50
        result = can_use_item(battle.t1, battle, "oran-berry", "1")

        self.assertFalse(result)

    def test_use_item_with_move_selected(self):
        battle = get_default_battle()
        battle.start()

        battle.t1.current_poke.moves[0].cur_pp = 15
        result = can_use_item(battle.t1, battle, "leppa-berry", "0", "0")

        self.assertTrue(result)

    def test_restore_pp_with_full_pp(self):
        battle = get_default_battle()
        battle.start()

        result = can_use_item(battle.t1, battle, "leppa-berry", "0", "0")

        self.assertFalse(result)

    def test_use_item_without_move(self):
        battle = get_default_battle()
        battle.start()

        battle.t1.current_poke.moves[0].cur_pp = 15
        result = can_use_item(battle.t1, battle, "leppa-berry", "0")

        self.assertFalse(result)

    def test_use_item_with_invalid_move(self):
        battle = get_default_battle()
        battle.start()

        battle.t1.current_poke.moves[0].cur_pp = 15
        result = can_use_item(battle.t1, battle, "leppa-berry", "0", "tackle")

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
