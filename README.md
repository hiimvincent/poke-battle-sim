# poke-battle-sim

Pokemon Battle Simulator (poke-battle-sim) is an open source Python package that provides efficient, customizable simulation of Pokemon battles. Thanks for checking it out.

## Overview

Poke-battle-sim models, as closely as possible, the mechanics present in the classic Generation IV Pokemon games (Diamond, Pearl, and Platinum). 

Currently the package supports all content from Gen I to IV including:

- 493 Pokemon
- 467 Moves
- 122 Abilities
- 535 Items

## Getting Started

Setting up a battle is a simple as a few lines of code.

```python
import poke_battle_sim as pb

pikachu = pb.Pokemon(...)
ash = pb.Trainer(“Ash”, [pikachu])

starmie = pb.Pokemon(...)
misty = pb.Trainer(‘Misty, [starmie])

battle = pb.Battle(ashe, misty)
battle.start()
battle.turn()

print(battle.get_all_text())
```

Checkout the documentation and examples for more details.

## Features

Poke-battle-sim includes all functionality present in both (Single) Link Battles and (Single) Trainer Battles in the original Gen IV games.

Although this package was developed with large-scale simulation in mind, it can be used with little modification as the backend for Pokemon or Pokemon-style games.

Double Battles or other battle formats introduced in later generations are not currently supported.

## Limitations

Certain mechanics present in the original games were not possible or practical to implement due to hardware-specific and region-specific behavior.

Mechanics not implemented in PokeBattleSim include:

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



