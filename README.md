# poke-battle-sim

Pokemon Battle Simulator (```poke-battle-sim```) is an open source Python package that provides efficient, customizable simulation of Pokemon battles. Thanks for checking it out.

## Overview

```poke-battle-sim``` emulates the mechanics present in the original Generation IV Pokemon games (Diamond, Pearl, and Platinum) while also providing the ability to modify and expand upon traditional Pokemon battles.

Currently the package supports all content from Gen I to IV including:

- 493 Pokemon
- 467 Moves
- 122 Abilities
- 535 Items

## Installation

```poke-battle-sim``` can be installed through pip using:

```
pip install poke-battle-sim
```

The package is also available on [PyPi](https://pypi.org/project/poke-battle-sim/) and [GitHub](https://github.com/hiimvincent/poke-battle-sim).


## Getting Started

Setting up a battle is as simple as a few lines of code.

```python
import poke_battle_sim as pb

pikachu = pb.Pokemon(...)
ash = pb.Trainer('Ash', [pikachu])

starmie = pb.Pokemon(...)
misty = pb.Trainer('Misty', [starmie])

battle = pb.Battle(ashe, misty)
battle.start()
battle.turn()

print(battle.get_all_text())
```

Check out the ```docs```  and example project for more details.

## Features

```poke-battle-sim``` includes all functionality present in both (Single) Link Battles and (Single) Trainer Battles in the original Gen IV games.

Although this package was developed with large-scale simulation in mind, it can be used with little modification as the backend for Pokemon or Pokemon-style games.

Double Battles or other battle formats introduced in later generations are not currently supported.

## Limitations

Certain mechanics present in the original games were not possible or practical to implement due to hardware-specific and region-specific behavior.

Mechanics not implemented in ```poke-battle-sim``` include:

- Using Nintendo DS audio volume data in damage calculation
- Using terrain-based type and power modifications
- Any glitches in the original games that were patched in subsequent generations

## Credit

This package was created and is managed by Vincent Johnson.

References used during development:

[Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Main_Page)

[PokemonDB](https://pokemondb.net/)

[Serebii.net](https://serebii.net/)

[Pokemon Fan Wiki](https://pokemon.fandom.com/wiki/Pok%C3%A9mon_Wiki)

Supporting packages:

[Black](https://github.com/psf/black) was used to reformat this repository.

[Setuptools](https://github.com/pypa/setuptools) was used to build this package. 

