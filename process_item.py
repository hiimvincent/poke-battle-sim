from __future__ import annotations
import pokemon as pk
import battlefield as bf
import battle as bt
from poke_sim import PokeSim
from move import Move
import random
import global_settings as gs
import global_data as gd
import process_move as pm
import trainer as tr

def use_item(trainer: tr.Trainer, battle: bt.Battle, item: str, move: str = None):
    poke = trainer.current_poke
    if item not in gd.USABLE_ITEM_CHECK:
        return

    battle._add_text(trainer.name + ' used one ' + pm._cap_name(item) + '!')
    if item == 'potion':
        poke.heal(20)
    elif item == 'antidote':
        pm._cure_nv_status(gs.POISONED, poke, battle)
    elif item == 'burn-heal':
        pm._cure_nv_status(gs.BURNED, poke, battle)
    elif item == 'ice-heal':
        pm._cure_nv_status(gs.FROZEN, poke, battle)
    elif item == 'awakening':
        pm._cure_nv_status(gs.ASLEEP, poke, battle)
    elif item == 'paralyz-heal':
        pm._cure_nv_status(gs.PARALYZED, poke, battle)
    elif item == 'full-restore':
        poke.heal(poke.max_hp)
        pm._cure_nv_status(poke.nv_status, poke, battle)
        pm._cure_confusion(poke, battle)
    elif item == 'max-potion':
        poke.heal(poke.max_hp)
    elif item == 'hyper-potion':
        poke.heal(200)
    elif item == 'super-potion':
        poke.heal(50)
    elif item == 'full-heal':
        pm._cure_nv_status(poke.nv_status, poke, battle)
        pm._cure_confusion(poke, battle)
    elif item == 'revive':
        if not poke.is_alive:
            poke.is_alive = True
            poke.heal(poke.max_hp // 2)
    elif item == 'max-revive':
        if not poke.is_alive:
            poke.is_alive = True
            poke.heal(poke.max_hp)
    elif item == 'fresh-water':
        poke.heal(50)
    elif item == 'soda-pop':
        poke.heal(60)
    elif item == 'lemonade':
        poke.heal(80)
    elif item == 'moomoo-milk':
        poke.heal(100)
    elif item == 'energypowder':
        poke.heal(50)
    elif item == 'energy-root':
        poke.heal(200)
    elif item == 'heal-powder':
        pm._cure_nv_status(poke.nv_status, poke, battle)
        pm._cure_confusion(poke, battle)
    elif item == 'revival-herb':
        if not poke.is_alive:
            poke.is_alive = True
            poke.heal(poke.max_hp)
    elif item == 'ether':
        if move and isinstance(move, str):
            poke.restore_pp(move, 10)
    elif item == 'max-ether':
        if move and isinstance(move, str):
            poke.restore_pp(move, 999)
    elif item == 'elixir':
        poke.restore_all_pp(10)
    elif item == 'max-elixir':
        poke.restore_all_pp(999)
    elif item == 'lava-cookie':
        pm._cure_nv_status(poke.nv_status, poke, battle)
        pm._cure_confusion(poke, battle)
    elif item == 'berry-juice':
        poke.heal(20)
    elif item == 'old-gateau':
        pm._cure_nv_status(poke.nv_status, poke, battle)
        pm._cure_confusion(poke, battle)
    elif item == 'guard-spec.':
        if not trainer.mist:
            battle._add_text(trainer.name + '\'s team became shrouded in mist!')
            trainer.mist = 5
    elif item == 'dire-hit':
        poke.crit_stage += 2
        if poke.crit_stage > 4:
            poke.crit_stage = 4
        battle._add_text(poke.nickname + ' is getting pumped!')
    elif item == 'x-attack':
        pm._give_stat_change(poke, battle, gs.ATK, 1, forced=True)
    elif item == 'x-defense':
        pm._give_stat_change(poke, battle, gs.DEF, 1, forced=True)
    elif item == 'x-speed':
        pm._give_stat_change(poke, battle, gs.SPD, 1, forced=True)
    elif item == 'x-accuracy':
        pm._give_stat_change(poke, battle, gs.ACC, 1, forced=True)
    elif item == 'x-special':
        pm._give_stat_change(poke, battle, gs.SP_ATK, 1, forced=True)
    elif item == 'x-sp.-def':
        pm._give_stat_change(poke, battle, gs.SP_DEF, 1, forced=True)
    elif item == 'blue-flute':
        pm._cure_nv_status(gs.ASLEEP, poke, battle)
    elif item == 'yellow-flute':
        pm._cure_confusion(poke, battle)
    elif item == 'red-flute':
        pm._cure_infatuation(poke, battle)
    elif item == 'cheri-berry':
        pm._cure_nv_status(gs.PARALYZED, poke, battle)
    elif item == 'chesto-berry':
        pm._cure_nv_status(gs.ASLEEP, poke, battle)
    elif item == 'pecha-berry':
        pm._cure_nv_status(gs.POISONED, poke, battle)
    elif item == 'rawst-berry':
        pm._cure_nv_status(gs.BURNED, poke, battle)
    elif item == 'aspear-berry':
        pm._cure_nv_status(gs.FROZEN, poke, battle)
    elif item == 'leppa-berry':
        if move and isinstance(move, str):
            poke.restore_pp(move, 10)
    elif item == 'oran-berry':
        poke.heal(10)
    elif item == 'persim-berry':
        pm._cure_confusion(poke, battle)
    elif item == 'lum-berry':
        pm._cure_nv_status(poke.nv_status, poke, battle)
        pm._cure_confusion(poke, battle)
    elif item == 'sitrus-berry':
        poke.heal(30)