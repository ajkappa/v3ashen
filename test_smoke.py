import os
os.environ['SDL_VIDEODRIVER']='dummy'
import ashenveil as game

game.reset_game(4)
assert game.state == 'battle'
assert len(game.enemies) == 3
initial = game.enemies[0].hp
game.do_action('attack')
assert game.enemies[0].hp < initial
# Cycle through all heroes so the enemy phase is exercised.
for _ in range(4):
    if game.state != 'battle': break
    game.do_action('guard')
assert game.round_no >= 2, game.round_no
# Spell resource and healing path
m = game.heroes[1].mana
game.active = 1
game.do_action('spell')
assert game.heroes[1].mana < m
print('SMOKE_OK', game.round_no, game.state, len(game.log))
