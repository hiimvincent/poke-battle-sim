from __future__ import annotations
from random import randrange

from poke_battle_sim.poke_sim import PokeSim
from poke_battle_sim.core.move import Move

import poke_battle_sim.core.pokemon as pk
import poke_battle_sim.core.trainer as tr
import poke_battle_sim.core.battle as bt
import poke_battle_sim.core.battlefield as bf

import poke_battle_sim.util.process_move as pm

import poke_battle_sim.conf.global_settings as gs
import poke_battle_sim.conf.global_data as gd


def use_item(
    trainer: tr.Trainer,
    battle: bt.Battle,
    item: str,
    item_target_pos: str,
    move_target_pos: str = None,
    text_skip: bool = False,
    can_skip: bool = False
):
    """
    Item actions in turn must be formatted as: ['item', $item, $item_target_pos, $move_target_name?]

    $item refers to the item name
    $item_target_pos refers to the target's position in the trainer's party (0-indexed)
    $move_target_pos is an optional parameter that refers to the target move's position
    in item target's move list (0-indexed)
    """
    if not can_use_item(trainer, battle, item, item_target_pos, move_target_pos):
        if can_skip:
            return
        raise Exception("Trainer attempted to use invalid item on Pokemon")

    poke = trainer.current_poke
    if move_target_pos:
        move = poke.moves[move_target_pos]

    if not text_skip:
        battle.add_text(
            trainer.name
            + " used one "
            + pm.cap_name(item)
            + " on "
            + poke.nickname
            + "!"
        )

    if poke.embargo_count:
        pm._failed(battle)
        return

    if item in gd.HEALING_ITEM_CHECK:
        poke.heal(gd.HEALING_ITEM_CHECK[item])
    elif item == "antidote" or item == "pecha-berry":
        pm.cure_nv_status(gs.POISONED, poke, battle)
    elif item == "burn-heal" or item == "rawst-berry":
        pm.cure_nv_status(gs.BURNED, poke, battle)
    elif item == "ice-heal" or item == "aspear-berry":
        pm.cure_nv_status(gs.FROZEN, poke, battle)
    elif item == "awakening" or item == "chesto-berry":
        pm.cure_nv_status(gs.ASLEEP, poke, battle)
    elif item == "paralyz-heal" or item == "cheri-berry":
        pm.cure_nv_status(gs.PARALYZED, poke, battle)
    elif item == "full-restore":
        poke.heal(poke.max_hp)
        pm.cure_nv_status(poke.nv_status, poke, battle)
        pm.cure_confusion(poke, battle)
    elif item == "max-potion":
        poke.heal(poke.max_hp)
    elif (
        item == "full-heal"
        or item == "heal-powder"
        or item == "lava-cookie"
        or item == "old-gateau"
        or item == "lum-berry"
    ):
        pm.cure_nv_status(poke.nv_status, poke, battle)
        pm.cure_confusion(poke, battle)
    elif item == "revive":
        if not poke.is_alive:
            poke.is_alive = True
            poke.heal(poke.max_hp // 2)
    elif item == "max-revive":
        if not poke.is_alive:
            poke.is_alive = True
            poke.heal(poke.max_hp)
    elif item == "revival-herb":
        if not poke.is_alive:
            poke.is_alive = True
            poke.heal(poke.max_hp)
    elif item == "ether" or item == "leppa-berry":
        poke.restore_pp(move, 10)
    elif item == "max-ether":
        poke.restore_pp(move, 999)
    elif item == "elixir":
        poke.restore_all_pp(10)
    elif item == "max-elixir":
        poke.restore_all_pp(999)
    elif item == "guard-spec.":
        if not trainer.mist:
            battle.add_text(trainer.name + "'s team became shrouded in mist!")
            trainer.mist = 5
    elif item == "dire-hit":
        poke.crit_stage += 2
        if poke.crit_stage > 4:
            poke.crit_stage = 4
        battle.add_text(poke.nickname + " is getting pumped!")
    elif item == "x-attack":
        pm.give_stat_change(poke, battle, gs.ATK, 1, forced=True)
    elif item == "x-defense":
        pm.give_stat_change(poke, battle, gs.DEF, 1, forced=True)
    elif item == "x-speed":
        pm.give_stat_change(poke, battle, gs.SPD, 1, forced=True)
    elif item == "x-accuracy":
        pm.give_stat_change(poke, battle, gs.ACC, 1, forced=True)
    elif item == "x-special":
        pm.give_stat_change(poke, battle, gs.SP_ATK, 1, forced=True)
    elif item == "x-sp.-def":
        pm.give_stat_change(poke, battle, gs.SP_DEF, 1, forced=True)
    elif item == "blue-flute":
        pm.cure_nv_status(gs.ASLEEP, poke, battle)
    elif item == "yellow-flute" or item == "persim-berry":
        pm.cure_confusion(poke, battle)
    elif item == "red-flute":
        pm.cure_infatuation(poke, battle)


def can_use_item(
    trainer: tr.Trainer,
    battle: bt.Battle,
    item: str,
    item_target_pos: str,
    move_target_pos: str = None,
):
    if not isinstance(item, str) or not item in gd.USABLE_ITEM_CHECK:
        return False
    if (
        not isinstance(item_target_pos, str)
        or any([not num.is_digit() for num in item_target_pos])
        or item_target_pos >= len(trainer.poke_list)
    ):
        return False
    poke = trainer.poke_list[int(item_target_pos)]
    if poke.embargo_count:
        return False
    if move_target_pos and (
        any([not num.is_digit() for num in move_target_pos])
        or move_target_pos >= len(poke.moves)
    ):
        return False
    if move_target_pos:
        move = poke.moves[move_target_pos]

    if item in gd.HEALING_ITEM_CHECK:
        return poke.cur_hp < poke.max_hp
    elif item == "antidote" or item == "pecha-berry":
        return poke.nv_status == gs.POISONED
    elif item == "burn-heal" or item == "rawst-berry":
        return poke.nv_status == gs.BURNED
    elif item == "ice-heal" or item == "aspear-berry":
        return poke.nv_status == gs.FROZEN
    elif item == "awakening" or item == "chesto-berry":
        return poke.nv_status == gs.ASLEEP
    elif item == "paralyz-heal" or item == "cheri-berry":
        return poke.nv_status == gs.PARALYZED
    elif item == "revive" or item == "max-revive" or item == "revival-herb":
        return not poke.is_alive
    elif item == "full-restore":
        return poke.cur_hp < poke.max_hp or poke.nv_status or poke.v_status[gs.CONFUSED]
    elif item == "max-potion":
        return poke.cur_hp < poke.max_hp
    elif (
        item == "full-heal"
        or item == "heal-powder"
        or item == "lava-cookie"
        or item == "old-gateau"
        or item == "lum-berry"
    ):
        return poke.nv_status or poke.v_status[gs.CONFUSED]
    elif item == "yellow-flute" or item == "persim-berry":
        return poke.v_status[gs.CONFUSED]
    elif item == "red-flute":
        return not not poke.infatuation
    elif item == "guard-spec.":
        return not trainer.mist
    elif item == "ether" or item == "max-ether" or item == "leppa-berry":
        return move and move.cur_pp < move.max_pp
    elif item == "elixir" or item == "max-elixir":
        return any([move.cur_pp < move.max_pp for move in poke.moves])
    return True


def damage_calc_items(
    attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle, move_data: Move
):
    if (
        not attacker.item in gd.DMG_ITEM_CHECK
        or attacker.has_ability("klutz")
        or attacker.embargo_count
    ):
        return

    item = attacker.item

    if item == "griseous-orb":
        if attacker.name == "giratina" and (
            move_data.type == "dragon" or move_data.type == "ghost"
        ):
            move_data.power = int(move_data.power * 1.2)
    elif item == "adamant-orb":
        if attacker.name == "dialga" and (
            move_data.type == "dragon" or move_data.type == "steel"
        ):
            move_data.power = int(move_data.power * 1.2)
    elif item == "lustrous-orb":
        if attacker.name == "palkia" and (
            move_data.type == "dragon" or move_data.type == "water"
        ):
            move_data.power = int(move_data.power * 1.2)
    elif item == "silver-powder" or item == "insect-plate":
        if move_data.type == "bug":
            move_data.power = int(move_data.power * 1.2)
    elif item == "soul-dew":
        if (attacker.name == "latios" or attacker.name == "latias") and (
            move_data.type == "dragon" or move_data.type == "psychic"
        ):
            move_data.power = int(move_data.power * 1.5)
    elif item == "metal-coat" or item == "iron-plate":
        if move_data.type == "steel":
            move_data.power = int(move_data.power * 1.2)
    elif item == "soft-sand" or item == "earth-plate":
        if move_data.type == "ground":
            move_data.power = int(move_data.power * 1.2)
    elif item == "hard-stone" or item == "stone-plate" or item == "rock-incense":
        if move_data.type == "rock":
            move_data.power = int(move_data.power * 1.2)
    elif item == "miracle-seed" or item == "meadow-plate" or item == "rose-incense":
        if move_data.type == "grass":
            move_data.power = int(move_data.power * 1.2)
    elif item == "blackglasses" or item == "dread-plate":
        if move_data.type == "dark":
            move_data.power = int(move_data.power * 1.2)
    elif item == "black-belt" or item == "fist-plate":
        if move_data.type == "fighting":
            move_data.power = int(move_data.power * 1.2)
    elif item == "magnet" or item == "zap-plate":
        if move_data.type == "electric":
            move_data.power = int(move_data.power * 1.2)
    elif (
        item == "mystic-water"
        or item == "sea-incense"
        or item == "wave-incense"
        or item == "splash-plate"
    ):
        if move_data.type == "water":
            move_data.power = int(move_data.power * 1.2)
    elif item == "sharp-beak" or item == "sky-plate":
        if move_data.type == "flying":
            move_data.power = int(move_data.power * 1.2)
    elif item == "poison-barb" or item == "toxic-plate":
        if move_data.type == "poison":
            move_data.power = int(move_data.power * 1.2)
    elif item == "nevermeltice" or item == "icicle-plate":
        if move_data.type == "ice":
            move_data.power = int(move_data.power * 1.2)
    elif item == "spell-tag" or item == "spooky-plate":
        if move_data.type == "ghost":
            move_data.power = int(move_data.power * 1.2)
    elif item == "twistedspoon" or item == "mind-plate" or item == "odd-incense":
        if move_data.type == "psychic":
            move_data.power = int(move_data.power * 1.2)
    elif item == "charcoal" or item == "flame-plate":
        if move_data.type == "fire":
            move_data.power = int(move_data.power * 1.2)
    elif item == "dragon-fang" or item == "draco-plate":
        if move_data.type == "dragon":
            move_data.power = int(move_data.power * 1.2)
    elif item == "silk-scarf":
        if move_data.type == "normal":
            move_data.power = int(move_data.power * 1.2)
    elif item == "muscle-band":
        if move_data.category == gs.PHYSICAL:
            move_data.power = int(move_data.power * 1.1)
    elif item == "wise-glasses":
        if move_data.category == gs.SPECIAL:
            move_data.power = int(move_data.power * 1.1)
    elif item == "metronome":
        if not attacker.last_successful_move_next:
            attacker.metronome_count = 1
            move_data.power *= int(move_data.power * 1.1)
        elif move_data.name == attacker.last_successful_move_next.name:
            attacker.metronome_count = max(10, attacker.metronome_count + 1)
            move_data.power *= int(
                move_data.power * (1 + (attacker.metronome_count) / 10)
            )
        else:
            attacker.metronome_count = 0


def damage_mult_items(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battle: bt.Battle,
    move_data: Move,
    t_mult: int,
) -> float:
    i_mult = 1

    if (
        attacker.item not in gd.DMG_MULT_ITEM_CHECK
        or attacker.has_ability("klutz")
        or attacker.embargo_count
    ):
        return i_mult

    item = attacker.item

    if item == "expert-belt":
        if t_mult > 1:
            i_mult *= 1.2
    elif item == "life-orb":
        i_mult *= 1.3

    return i_mult


def pre_hit_berries(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battle: bt.Battle,
    move_data: Move,
    t_mult: int,
) -> float:
    p_mult = 1

    if (
        not defender.is_alive
        or not defender.item in gd.PRE_HIT_BERRIES
        or defender.has_ability("klutz")
        or defender.embargo_count
    ):
        return p_mult

    if t_mult > 1 and gd.PRE_HIT_BERRIES[defender.item] == move_data.type:
        _eat_item(defender, battle)
        p_mult = 0.5

    return p_mult


def on_damage_items(poke: pk.Pokemon, battle: bt.Battle, move_data: Move):
    if (
        not poke.is_alive
        or not poke.item in gd.ON_DAMAGE_ITEM_CHECK
        or poke.has_ability("klutz")
        or poke.embargo_count
    ):
        return
    thr = gs.DAMAGE_THRESHOLD
    if poke.has_ability("gluttony"):
        thr *= 2
    if poke.cur_hp >= thr:
        return

    item = poke.item
    _eat_item(poke, battle)

    if item == "liechi-berry":
        pm.give_stat_change(poke, battle, gs.ATK, 1)
    elif item == "ganlon-berry":
        pm.give_stat_change(poke, battle, gs.DEF, 1)
    elif item == "salac-berry":
        pm.give_stat_change(poke, battle, gs.SPD, 1)
    elif item == "petaya-berry":
        pm.give_stat_change(poke, battle, gs.SP_ATK, 1)
    elif item == "apricot-berry":
        pm.give_stat_change(poke, battle, gs.SP_DEF, 1)
    elif item == "lansat-berry":
        poke.crit_stage = min(4, poke.crit_stage + 1)
        battle.add_text(poke.nickname + " is getting pumped!")
    elif item == "starf-berry":
        pm.give_stat_change(poke, battle, randrange(1, 6), 2)
    elif item == "micle-berry":
        poke.next_will_hit = True
    elif item == "custap-berry":
        poke.prio_boost = True
    elif item == "enigma-berry":
        t_mult = pm._calculate_type_ef(poke, move_data)
        if t_mult and t_mult > 1:
            _eat_item(poke, battle)
            poke.heal(max(1, poke.max_hp // 4))


def pre_move_items(poke: pk.Pokemon):
    if (
        not poke.item in gd.PRE_MOVE_ITEM_CHECK
        or poke.has_ability("klutz")
        or poke.embargo_count
    ):
        return

    item = poke.item

    if item == "quick-claw":
        if randrange(5) < 1:
            poke.prio_boost = True


def stat_calc_items(poke: pk.Pokemon):
    if (
        not poke.is_alive
        or not poke.item in gd.STAT_CALC_ITEM_CHECK
        or poke.has_ability("klutz")
        or poke.embargo_count
    ):
        return

    item = poke.item

    if item == "metal-powder":
        if poke.name == "ditto" and not poke.transformed:
            poke.stats_effective[gs.DEF] *= 2
    elif item == "quick-powder":
        if poke.name == "ditto" and not poke.transformed:
            poke.stats_effective[gs.SPD] *= 2
    elif item == "thick-club":
        if poke.name == "cubone" or poke.name == "marowak":
            poke.stats_effective[gs.ATK] *= 2
    elif item == "choice-band":
        poke.stats_effective[gs.ATK] = int(poke.stats_effective[gs.ATK] * 1.5)
        if not poke.locked_move and poke.last_successful_move_next:
            poke.locked_move = poke.last_successful_move_next.name
    elif item == "choice-specs":
        poke.stats_effective[gs.SP_ATK] = int(poke.stats_effective[gs.SP_ATK] * 1.5)
        if not poke.locked_move and poke.last_successful_move_next:
            poke.locked_move = poke.last_successful_move_next.name
    elif item == "choice-scarf":
        poke.stats_effective[gs.SPD] = int(poke.stats_effective[gs.SPD] * 1.5)
        if not poke.locked_move and poke.last_successful_move_next:
            poke.locked_move = poke.last_successful_move_next.name
    elif item == "deepseatooth":
        if poke.name == "clamperl":
            poke.stats_effective[gs.SP_ATK] *= 2
    elif item == "deepseascale":
        if poke.name == "clamperl":
            poke.stats_effective[gs.SP_DEF] *= 2
    elif item == "light-ball":
        if poke.name == "pikachu":
            poke.stats_effective[gs.ATK] *= 2
            poke.stats_effective[gs.SP_ATK] *= 2
    elif item == "iron-ball":
        poke.stats_effective[gs.SPD] //= 2
        poke.grounded = True


def status_items(poke: pk.Pokemon, battle: bt.Battle):
    if (
        not poke.is_alive
        or not poke.item in gd.STATUS_ITEM_CHECK
        or poke.has_ability("klutz")
        or poke.embargo_count
    ):
        return

    item = poke.item

    if item == "cheri-berry":
        if poke.nv_status == gs.PARALYZED:
            _eat_item(poke, battle)
            pm.cure_nv_status(gs.PARALYZED, poke, battle)
    elif item == "chesto-berry":
        if poke.nv_status == gs.ASLEEP:
            _eat_item(poke, battle)
            pm.cure_nv_status(gs.ASLEEP, poke, battle)
    elif item == "pecha-berry":
        if poke.nv_status == gs.POISONED:
            _eat_item(poke, battle)
            pm.cure_nv_status(gs.POISONED, poke, battle)
    elif item == "rawst-berry":
        if poke.nv_status == gs.BURNED:
            _eat_item(poke, battle)
            pm.cure_nv_status(gs.BURNED, poke, battle)
    elif item == "aspear-berry":
        if poke.nv_status == gs.FROZEN:
            _eat_item(poke, battle)
            pm.cure_nv_status(gs.FROZEN, poke, battle)
    elif item == "persim-berry":
        if poke.v_status[gs.CONFUSED]:
            _eat_item(poke, battle)
            pm.cure_confusion(poke, battle)
    elif item == "lum-berry":
        if poke.nv_status or poke.v_status[gs.CONFUSED]:
            _eat_item(poke, battle)
            pm.cure_nv_status(poke.nv_status, poke, battle)
            pm.cure_confusion(poke, battle)
    elif item == "mental-herb":
        if poke.infatuation:
            _consume_item(poke, battle)
            pm.cure_infatuation(poke, battle)
    elif item == "destiny-knot":
        if (
            poke.infatuation
            and poke.enemy.current_poke.is_alive
            and not poke.enemy.current_poke.infatuation
        ):
            pm.infatuate(poke, poke.enemy.current_poke, battle)


def on_hit_items(
    attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle, move_data: Move
):
    if (
        not move_data
        or not defender.item in gd.ON_HIT_ITEM_CHECK
        or defender.has_ability("klutz")
        or defender.embargo_count
    ):
        return

    t_mult = pm._calculate_type_ef(defender, move_data)
    item = defender.item

    if item == "jaboca-berry":
        if move_data.category == gs.PHYSICAL and attacker.is_alive:
            _eat_item(defender, battle)
            attacker.take_damage(max(1, attacker.max_hp // 8))
    elif item == "rowap-berry":
        if move_data.category == gs.SPECIAL and attacker.is_alive:
            _eat_item(defender, battle)
            attacker.take_damage(max(1, attacker.max_hp // 8))
    elif item == "sticky-barb":
        if (
            move_data.name in gd.CONTACT_CHECK
            and attacker.is_alive
            and not attacker.item
        ):
            battle.add_text(
                attacker.nickname + " received " + defender.nickname + "'s Sticky Barb!"
            )
            attacker.give_item("sticky-barb")


def homc_items(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
) -> float:
    i_mult = 1

    if (
        not defender.item in gd.HOMC_ITEM_CHECK
        or defender.has_ability("klutz")
        or defender.embargo_count
    ) and (
        not attacker.item in gd.HOMC_ITEM_CHECK
        or attacker.has_ability("klutz")
        or attacker.embargo_count
    ):
        return i_mult

    if defender.item == "brightpowder" or defender.item == "lax-incense":
        i_mult *= 0.9

    if attacker.item == "wide-lens":
        i_mult *= 1.1
    elif attacker.item == "zoom-lens" and not is_first:
        i_mult *= 1.2

    return i_mult


def end_turn_items(poke: pk.Pokemon, battle: bt.Battle):
    if (
        not poke.is_alive
        or not poke.item in gd.END_TURN_ITEM_CHECK
        or poke.has_ability("klutz")
        or poke.embargo_count
    ):
        return

    item = poke.item

    if item == "oran-berry":
        if poke.cur_hp < poke.max_hp * gs.BERRY_THRESHOLD:
            _eat_item(poke, battle)
            poke.heal(10)
    elif item == "sitrus-berry":
        if poke.cur_hp < poke.max_hp * gs.BERRY_THRESHOLD:
            _eat_item(poke, battle)
            poke.heal(max(1, poke.max_hp // 4))
    elif item == "figy-berry":
        if poke.cur_hp < poke.max_hp * gs.BERRY_THRESHOLD:
            _eat_item(poke, battle)
            poke.heal(max(1, poke.max_hp // 8))
            if not poke.nature or poke.nature in ("modest", "timid", "calm", "bold"):
                pm.confuse(poke, battle)
    elif item == "wiki-berry":
        if poke.cur_hp < poke.max_hp * gs.BERRY_THRESHOLD:
            _eat_item(poke, battle)
            poke.heal(max(1, poke.max_hp // 8))
            if not poke.nature or poke.nature in (
                "adamant",
                "jolly",
                "careful",
                "impish",
            ):
                pm.confuse(poke, battle)
    elif item == "mago-berry":
        if poke.cur_hp < poke.max_hp * gs.BERRY_THRESHOLD:
            _eat_item(poke, battle)
            poke.heal(max(1, poke.max_hp // 8))
            if not poke.nature or poke.nature in ("brave", "quiet", "sassy", "relaxed"):
                pm.confuse(poke, battle)
    elif item == "aguav-berry":
        if poke.cur_hp < poke.max_hp * gs.BERRY_THRESHOLD:
            _eat_item(poke, battle)
            poke.heal(max(1, poke.max_hp // 8))
            if not poke.nature or poke.nature in ("naughty", "rash", "naive", "lax"):
                pm.confuse(poke, battle)
    elif item == "iapapa-berry":
        if poke.cur_hp < poke.max_hp * gs.BERRY_THRESHOLD:
            _eat_item(poke, battle)
            poke.heal(max(1, poke.max_hp // 8))
            if not poke.nature or poke.nature in ("lonely", "mild", "gentle", "hasty"):
                pm.confuse(poke, battle)
    elif item == "leftovers":
        if not poke.cur_hp == poke.max_hp:
            battle.add_text(
                poke.nickname + " restored a little HP using its Leftovers!"
            )
            poke.heal(max(1, poke.max_hp // 16), text_skip=True)
    elif item == "black-sludge":
        if "poison" in poke.types:
            battle.add_text(
                poke.nickname + " restored a little HP using its Black Sludge!"
            )
            poke.heal(max(1, poke.max_hp // 16), text_skip=True)
        elif not poke.has_ability("magic-guard"):
            battle.add_text(poke.nickname + " was hurt by its Black Sludge!")
            poke.take_damage(max(1, poke.max_hp // 8))
    elif item == "toxic-orb":
        if not poke.nv_status:
            pm.give_nv_status(gs.BADLY_POISONED, poke, battle)
    elif item == "flame-orb":
        if not poke.nv_status:
            pm.give_nv_status(gs.BURNED, poke, battle)
    elif item == "sticky-barb":
        battle.add_text(poke.nickname + " was hurt by its Sticky Barb!")
        poke.take_damage(max(1, poke.max_hp // 8))


def post_damage_items(attacker: pk.Pokemon, battle: bt.Battle, dmg: int):
    if (
        attacker.item not in gd.POST_DAMAGE_ITEM_CHECK
        or attacker.has_ability("klutz")
        or attacker.embargo_count
    ):
        return

    if attacker.item == "shell-bell":
        if attacker.is_alive and dmg:
            battle.add_text(
                attacker.nickname + " restored a little HP using its Shell Bell!"
            )
            attacker.heal(max(1, dmg // 8), text_skip=True)
    if attacker.item == "life-orb":
        if attacker.is_alive and dmg:
            battle.add_text(attacker.nickname + " lost some of its HP!")
            attacker.take_damage(max(1, attacker.max_hp // 10))


def _consume_item(poke: pk.Pokemon, battle: bt.Battle):
    battle.add_text(poke.nickname + " used its " + pm.cap_name(poke.item) + "!")


def _eat_item(poke: pk.Pokemon, battle: bt.Battle):
    battle.add_text(poke.nickname + " ate its " + pm.cap_name(poke.item) + "!")
    poke.give_item(None)
