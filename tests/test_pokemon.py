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


if __name__ == '__main__':
    unittest.main()
