# Pykemon

Pykemon is a python package for Pokemon that emulates Pokemon battle as seen in the original Pokemon games.

This package is a fork on the original poke-battle-sim package, which can be found on [Github](https://github.com/hiimvincent/poke-battle-sim) and on [PyPI](https://pypi.org/project/poke-battle-sim/).

## Poke-battle-sim

Pokemon Battle Simulator (```poke-battle-sim```) is an open-source Python package that provides efficient, customizable simulation of Pokemon battles. Thanks for checking it out.

### Differences

Here are the distinctions between Pykemon and PokeBattleSim:

#### Features
- Possibility to create a battle with a weather.

#### Fixes
- Pokemons can now be initialized with id.
- Damage calculations now occurs only once.
- A pokemon can now have only one max HP (particularly useful for Shedinja).
- A pokemon can't be used multiple time in a same team anymore.
- Max EVs are decreased to 252 instead of 255, as it may be consider a bug patched in games after the 6th generation.
- Using an unstarted battle now raises a personalized exception.
- The number of moves for Pokemons is now limited to 4.
- Crashes upon using items have been corrected.
- fix messages on cure with natural-cure ability.
- Weather ball move now use rock type on sandstorm.
- Embargo mechanics now cancel item usage as intended.
- Nature Power now launch by default Tri Attack or the move associated with the terrain defined in the battle.
- Earthquake damages are now calculated.
- Stealth Rock is now taken into account.
- Defog now clear all hazards on the attacking pokemon side.

## Overview

Pykemon emulates the mechanics present in the original Generation IV Pokemon games (Diamond, Pearl, and Platinum) while also providing the ability to modify and expand upon traditional Pokemon battles.

Currently the package supports all content from Gen I to IV including:

- 493 Pokemon
- 467 Moves
- 122 Abilities
- 535 Items

## Getting Started

Setting up a battle is as simple as a few lines of code.

```python
import poke_battle_sim as pb

pikachu = pb.Pokemon(...)
ash = pb.Trainer('Ash', [pikachu])

starmie = pb.Pokemon(...)
misty = pb.Trainer('Misty', [starmie])

battle = pb.Battle(ash, misty)
battle.start()
battle.turn(...)

print(battle.get_all_text())
```

Check out the ```docs``` or tests for more details.

## Features

Pykemon includes all functionality present in both (Single) Link Battles and (Single) Trainer Battles in the original Gen IV games.

Although this package was developed with large-scale simulation in mind, it can be used with little modification as the backend for Pokemon or Pokemon-style games.

Double Battles or other battle formats introduced in later generations are not currently supported.

## Limitations

Certain mechanics present in the original games were not possible or practical to implement due to hardware-specific and region-specific behavior.

Mechanics not implemented in ```poke-battle-sim``` include:

- Using Nintendo DS audio volume data in damage calculation
- Using terrain-based type and power modifications
- Any glitches in the original games that were patched in subsequent generations

## Credit

This package was originally created and managed by Vincent Johnson.

References used during development:

[Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Main_Page)

[PokemonDB](https://pokemondb.net/)

[Serebii.net](https://serebii.net/)

[Pokemon Fan Wiki](https://pokemon.fandom.com/wiki/Pok%C3%A9mon_Wiki)

Supporting packages:

[Black](https://github.com/psf/black) was used to reformat this repository.

[Setuptools](https://github.com/pypa/setuptools) was used to build this package. 

