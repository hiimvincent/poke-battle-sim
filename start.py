import poke_sim as ps
import pokemon as pk
import trainer as tr
import battle as bt
import random

#
# Move Effect Testing
#

ps.PokeSim.start()
a = ps.PokeSim._move_list[random.randrange(1, 467) - 1][1]
b = ps.PokeSim._move_list[random.randrange(1, 467) - 1][1]
c = ps.PokeSim._move_list[random.randrange(1, 467) - 1][1]
d = ps.PokeSim._move_list[random.randrange(1, 467) - 1][1]
while a in ['pound', 'double-slap']:
    a = ps.PokeSim._move_list[random.randrange(1, 467) - 1][1]
while b in ['pound', 'double-slap', a]:
    b = ps.PokeSim._move_list[random.randrange(1, 467) - 1][1]
m1 = [a, 'pound', 'double-slap', b]
while c in ['scratch', 'fire-punch']:
    c = ps.PokeSim._move_list[random.randrange(1, 467) - 1][1]
while d in ['scratch', 'fire-punch', c]:
    d = ps.PokeSim._move_list[random.randrange(1, 467) - 1][1]
m2 = [c, 'scratch', 'fire-punch', d]
print(m1[0], m1[3])
print(m2[0], m2[3])
pikachu1 = pk.Pokemon(name_or_id="pikachu", level=100, ivs=[31,31,0,10,21,30], evs=[255,0,100,5,5,10],
                     moves=m1, nature="timid", nickname='pikachu1', gender='male', ability=ps.PokeSim._ability_list[random.randrange(len(ps.PokeSim._ability_list))], item=ps.PokeSim._item_list[random.randrange(len(ps.PokeSim._item_list))])

pikachu2 = pk.Pokemon(name_or_id="pikachu", level=100, ivs=[31,31,0,10,21,30], evs=[255,0,100,5,5,10],
                     moves=m1, nature="timid", nickname='pikachu2', gender='male', ability=ps.PokeSim._ability_list[random.randrange(len(ps.PokeSim._ability_list))], item=ps.PokeSim._item_list[random.randrange(len(ps.PokeSim._item_list))])
charizard3 = pk.Pokemon("charizard", level=100, stats_actual=[200,200,200,200,200,200], moves=m1, nickname='charizard3', gender='female', ability=ps.PokeSim._ability_list[random.randrange(len(ps.PokeSim._ability_list))], item=ps.PokeSim._item_list[random.randrange(len(ps.PokeSim._item_list))])
charizard4 = pk.Pokemon("charizard", level=100, stats_actual=[200,200,200,200,200,200], moves=m1, nickname='charizard4', gender='female', ability=ps.PokeSim._ability_list[random.randrange(len(ps.PokeSim._ability_list))], item=ps.PokeSim._item_list[random.randrange(len(ps.PokeSim._item_list))])

charizard1 = pk.Pokemon("charizard", level=100, stats_actual=[200,200,200,200,200,200], moves=m2, nickname='charizard1', gender='female', ability=ps.PokeSim._ability_list[random.randrange(len(ps.PokeSim._ability_list))], item=ps.PokeSim._item_list[random.randrange(len(ps.PokeSim._item_list))])
charizard2 = pk.Pokemon("charizard", level=100, stats_actual=[200,200,200,200,200,200], moves=m2, nickname='charizard2', gender='female', ability=ps.PokeSim._ability_list[random.randrange(len(ps.PokeSim._ability_list))], item=ps.PokeSim._item_list[random.randrange(len(ps.PokeSim._item_list))])

print('p1 ability: ' + pikachu1.ability + ' p1 item: ' + pikachu1.o_item)
print('p2 ability: ' + pikachu2.ability + ' p2 item: ' + pikachu2.o_item)
print('c1 ability: ' + charizard1.ability + ' c1 item: ' + charizard1.o_item)
print('c2 ability: ' + charizard2.ability + ' c2 item: ' + charizard2.o_item)
print('c3 ability: ' + charizard3.ability + ' c3 item: ' + charizard3.o_item)
print('c4 ability: ' + charizard4.ability + ' c4 item: ' + charizard4.o_item)

me = tr.Trainer("player", [pikachu1, pikachu2, charizard3, charizard4])
you = tr.Trainer("enemy", [charizard1, charizard2])
battle = bt.Battle(me, you)
battle.start()

while not battle.winner and me.current_poke and you.current_poke:
    me_moves = me.current_poke.get_available_moves()
    if me_moves:
        me_move = me_moves[random.randrange(0, len(me_moves))].name
    else:
        me_move = ''
    u_moves = you.current_poke.get_available_moves()
    if u_moves:
        u_move = u_moves[random.randrange(0, len(u_moves))].name
    else:
        u_move = ''
    battle.turn(["move", me_move], ["move", u_move])
    print(battle.get_cur_text())

#print(battle.get_all_text())