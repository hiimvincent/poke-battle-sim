import unittest

from poke_battle_sim import Pokemon


class TestPokemon(unittest.TestCase):

    def test_initialize_pokemon_with_id(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])

        self.assertEqual(pokemon.id, 25)
        self.assertEqual(pokemon.name, 'pikachu')
        self.assertEqual(pokemon.nickname, 'PIKACHU')
        self.assertEqual(pokemon.gender, 'male')
        self.assertEqual(pokemon.level, 22)
        self.assertEqual(pokemon.types, ('electric', ''))
        self.assertEqual(pokemon.cur_hp, 100)
        self.assertEqual(pokemon.max_hp, 100)
        self.assertEqual(pokemon.stats_actual, [100, 100, 100, 100, 100, 100])
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_name(self):
        pokemon = Pokemon("PiKaChU", 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])

        self.assertEqual(pokemon.id, 25)
        self.assertEqual(pokemon.name, 'pikachu')
        self.assertEqual(pokemon.nickname, 'PIKACHU')
        self.assertEqual(pokemon.gender, 'male')
        self.assertEqual(pokemon.level, 22)
        self.assertEqual(pokemon.types, ('electric', ''))
        self.assertEqual(pokemon.cur_hp, 100)
        self.assertEqual(pokemon.max_hp, 100)
        self.assertEqual(pokemon.stats_actual, [100, 100, 100, 100, 100, 100])
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_none_moveset(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, None, 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with no moveset")

    def test_initialize_pokemon_without_moves(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, [], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with no moveset")

    def test_initialize_pokemon_with_too_much_moves(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['pound', 'karate-chop', 'double-slap', 'comet-punch', 'mega-punch'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with too much moves")

    def test_initialize_pokemon_with_duplicate_move(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle', 'tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid moveset")

    def test_initialize_pokemon_with_bad_id(self):
        with self.assertRaises(Exception) as context:
            Pokemon(10400, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid name or id")

    def test_initialize_pokemon_with_bad_name(self):
        with self.assertRaises(Exception) as context:
            Pokemon('a_non_existing_pokemon_name', 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid name or id")

    def test_initialize_pokemon_with_bad_gender(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'neutral', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid gender")

    def test_initialize_pokemon_with_no_stats(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid stats")

    def test_initialize_pokemon_with_insuffisent_stats_actual(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid stats")

    def test_initialize_pokemon_with_too_low_stat(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', stats_actual=[0, 100, 100, 100, 100, 100])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid stats")

    def test_initialize_pokemon_with_cur_hp(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[150, 100, 100, 100, 100, 100], cur_hp=100)

        self.assertEqual(pokemon.id, 25)
        self.assertEqual(pokemon.name, 'pikachu')
        self.assertEqual(pokemon.nickname, 'PIKACHU')
        self.assertEqual(pokemon.gender, 'male')
        self.assertEqual(pokemon.level, 22)
        self.assertEqual(pokemon.types, ('electric', ''))
        self.assertEqual(pokemon.cur_hp, 100)
        self.assertEqual(pokemon.max_hp, 150)
        self.assertEqual(pokemon.stats_actual, [150, 100, 100, 100, 100, 100])
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_too_much_cur_hp(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100], cur_hp=150)
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid hp value")

    def test_initialize_pokemon_with_ev_iv_nature(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[0, 0, 0, 0, 0, 0], nature="quirky")

        self.assertEqual(pokemon.id, 25)
        self.assertEqual(pokemon.name, 'pikachu')
        self.assertEqual(pokemon.nickname, 'PIKACHU')
        self.assertEqual(pokemon.gender, 'male')
        self.assertEqual(pokemon.level, 22)
        self.assertEqual(pokemon.types, ('electric', ''))
        self.assertEqual(pokemon.cur_hp, 28)
        self.assertEqual(pokemon.max_hp, 28)
        self.assertEqual(pokemon.stats_actual, [28, 32, 26, 30, 27, 48])
        self.assertEqual(pokemon.ivs, [16, 16, 16, 16, 16, 16])
        self.assertEqual(pokemon.evs, [0, 0, 0, 0, 0, 0])
        self.assertEqual(pokemon.nature, 'quirky')
        self.assertEqual(pokemon.nature_effect, (4, 4))
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_iv_only(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], nature="quirky")
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid evs or ivs")

    def test_initialize_pokemon_with_ev_only(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', evs=[50, 50, 50, 50, 50, 50], nature="quirky")
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid evs or ivs")

    def test_initialize_pokemon_without_nature(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[50, 50, 50, 50, 50, 50])
        self.assertEqual(str(context.exception), "Attempted to create Pokemon without providing its nature")

    def test_initialize_pokemon_with_invalid_nature(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[50, 50, 50, 50, 50, 50], nature="a_nature_that_does_not_exist")
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid nature")

    def test_initialize_pokemon_with_too_much_iv(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 32, 16, 16, 16, 16], evs=[50, 50, 50, 50, 50, 50], nature="quirky")
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid ivs")

    def test_initialize_pokemon_with_too_much_ev(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[10, 253, 10, 10, 10, 10], nature="quirky")
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid evs")

    def test_initialize_pokemon_with_too_much_total_ev(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[248, 252, 11, 0, 0, 0], nature="quirky")
        self.assertEqual(str(context.exception), "Attempted to create Pokemon with invalid evs")

    def test_initialize_pokemon_with_held_item(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100], item="oran-berry")

        self.assertEqual(pokemon.id, 25)
        self.assertEqual(pokemon.name, 'pikachu')
        self.assertEqual(pokemon.nickname, 'PIKACHU')
        self.assertEqual(pokemon.gender, 'male')
        self.assertEqual(pokemon.o_item, 'oran-berry')
        self.assertEqual(pokemon.level, 22)
        self.assertEqual(pokemon.types, ('electric', ''))
        self.assertEqual(pokemon.cur_hp, 100)
        self.assertEqual(pokemon.max_hp, 100)
        self.assertEqual(pokemon.stats_actual, [100, 100, 100, 100, 100, 100])
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_none_held_item(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100], item=None)

        self.assertEqual(pokemon.id, 25)
        self.assertEqual(pokemon.name, 'pikachu')
        self.assertEqual(pokemon.nickname, 'PIKACHU')
        self.assertEqual(pokemon.gender, 'male')
        self.assertIsNone(pokemon.o_item)
        self.assertEqual(pokemon.level, 22)
        self.assertEqual(pokemon.types, ('electric', ''))
        self.assertEqual(pokemon.cur_hp, 100)
        self.assertEqual(pokemon.max_hp, 100)
        self.assertEqual(pokemon.stats_actual, [100, 100, 100, 100, 100, 100])
        self.assertIsNone(pokemon.trainer)


if __name__ == '__main__':
    unittest.main()
