import pygame, sys, random, math, os
from dataclasses import dataclass

pygame.init()
pygame.joystick.init()
W, H = 1000, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Ashenveil: Le Sanctuaire Fendu')
clock = pygame.time.Clock()

# Palette: dark cavern + readable accents
BG=(12,14,24); PANEL=(25,28,44); PANEL2=(34,37,57); INK=(230,232,244); MUTED=(144,150,174)
GOLD=(228,180,91); RED=(214,83,92); GREEN=(91,202,139); BLUE=(93,168,231); VIOLET=(180,116,226)

font_big=pygame.font.SysFont('dejavusans', 42, bold=True)
font=pygame.font.SysFont('dejavusans', 20)
small=pygame.font.SysFont('dejavusans', 16)
mini=pygame.font.SysFont('dejavusans', 13)

@dataclass
class Hero:
    name: str; role: str; color: tuple; maxhp: int; hp: int; maxmana: int; mana: int; power: int; armor: int; spell: str; desc: str; x: int=0; y: int=0; guard: bool=False; potions: int=2; sprite: str=''

@dataclass
class Enemy:
    name: str; hp: int; maxhp: int; power: int; color: tuple; x: int; y: int; kind: str; sprite: str=''

heroes=[
 Hero('Vesper', 'Lame-ombre', (177,116,226), 115,115,55,55,27,8,'Entaille spectrale','Frappe rapide, critique élevé.',sprite='assets/vesper.png'),
 Hero('Myr', 'Tisseuse', (93,168,231), 90,90,90,90,20,5,'Fil lunaire','Soin de groupe et entrave.',sprite='assets/myr.png'),
 Hero('Orun', 'Gardien', (228,180,91), 155,155,35,35,22,16,'Rempart','Très résistant, protège un allié.',sprite='assets/orun.png'),
 Hero('Nox', 'Chante-sort', (91,202,139), 100,100,110,110,18,6,'Éclat du vide','Magie de zone dévastatrice.',sprite='assets/nox.png'),
]
enemies=[]
state='menu'; player_count=2; active=0; round_no=1; log=[]; selected_target=0; flash=0; victory=False
particles=[]; floaters=[]
BASE_DIR=getattr(sys,'_MEIPASS',os.path.dirname(os.path.abspath(__file__)))
def asset_path(name): return os.path.join(BASE_DIR,'assets',name)
def load_assets():
    assets={'bg':asset_path('sanctuary_bg.png'),'cinder':asset_path('cinder_sister.png')}
    for h in heroes: assets[h.name]=asset_path(os.path.basename(h.sprite))
    loaded={}
    for key,path in assets.items():
        try: loaded[key]=pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError): loaded[key]=None
    return loaded
ART=load_assets()

def controller_count():
    return pygame.joystick.get_count()

def controller_action(button):
    """Convertit les boutons XInput/PlayStation courants en actions du jeu."""
    return {0:'attack', 2:'spell', 1:'guard', 3:'potion'}.get(button)

def handle_controller_button(button):
    global player_count, selected_target, state
    if state=='menu':
        if button==0: reset_game(player_count)       # A / Croix
        elif button==4: player_count=max(2,player_count-1)  # LB / L1
        elif button==5: player_count=min(4,player_count+1)  # RB / R1
    elif state=='battle':
        if button==4: selected_target=(selected_target-1)%max(1,len(enemies))
        elif button==5: selected_target=(selected_target+1)%max(1,len(enemies))
        else:
            action=controller_action(button)
            if action: do_action(action)
    elif state=='end':
        if button==0: reset_game(player_count)

def handle_controller_hat(value):
    global player_count, selected_target
    x,y=value
    if state=='menu':
        if x<0: player_count=max(2,player_count-1)
        elif x>0: player_count=min(4,player_count+1)
    elif state=='battle':
        if x<0: selected_target=(selected_target-1)%max(1,len(enemies))
        elif x>0: selected_target=(selected_target+1)%max(1,len(enemies))

# simple helpers
def text(s, x,y, f=font, col=INK): screen.blit(f.render(s, True, col),(x,y))
def centered(s,y,f=font,col=INK):
    surf=f.render(s,True,col); screen.blit(surf,((W-surf.get_width())//2,y))
def bar(x,y,w,h,val,mx,col):
    pygame.draw.rect(screen,(48,50,70),(x,y,w,h),border_radius=4)
    pygame.draw.rect(screen,col,(x,y,max(0,int(w*val/max(1,mx))),h),border_radius=4)
def addlog(s):
    log.append(s)
    if len(log)>7: log.pop(0)
def fx(x,y,color,kind='hit'):
    count=26 if kind=='spell' else 14
    for _ in range(count):
        angle=random.random()*math.tau; speed=random.uniform(1.5,5.5)
        particles.append([float(x),float(y),math.cos(angle)*speed,math.sin(angle)*speed,random.randint(18,34),color,random.randint(2,5)])
def float_text(s,x,y,color): floaters.append([s,float(x),float(y),color,42])
def update_fx():
    for p in particles[:]:
        p[0]+=p[2]; p[1]+=p[3]; p[3]+=0.08; p[4]-=1
        if p[4]<=0: particles.remove(p)
    for f in floaters[:]:
        f[2]-=0.7; f[4]-=1
        if f[4]<=0: floaters.remove(f)
def draw_fx():
    for x,y,vx,vy,life,col,size in particles:
        pygame.draw.circle(screen,col,(int(x),int(y)),max(1,int(size*life/30)))
    for s,x,y,col,life in floaters:
        surf=font.render(s,True,col); surf.set_alpha(min(255,life*6)); screen.blit(surf,(int(x)-surf.get_width()//2,int(y)))
def reset_game(n):
    global player_count, active, round_no, log, enemies, state, victory, selected_target
    player_count=n; active=0; round_no=1; log=[]; selected_target=0; victory=False
    for h in heroes: h.hp=h.maxhp; h.mana=h.maxmana; h.guard=False; h.potions=2
    enemies=[Enemy('Morne-larve',72,72,15,(177,91,107),710,300,'larve'), Enemy('Veilleur creux',105,105,19,(93,120,174),820,420,'veilleur'), Enemy('Sœur des cendres',130,130,22,(160,91,170),690,500,'sœur',sprite=asset_path('cinder_sister.png'))]
    addlog('Le sanctuaire respire. À vous de jouer.')
    state='battle'

def alive_heroes(): return [h for h in heroes[:player_count] if h.hp>0]
def alive_enemies(): return [e for e in enemies if e.hp>0]
def next_turn():
    global active, round_no
    for step in range(1, player_count + 1):
        candidate=(active+step)%player_count
        if heroes[candidate].hp>0:
            if candidate <= active:
                round_no += 1
                enemy_turns()
                if not alive_heroes(): return
            active=candidate
            return

def enemy_turns():
    global flash
    for e in alive_enemies():
        targets=alive_heroes()
        if not targets: return
        target=random.choice(targets)
        dmg=max(2,e.power-target.armor//3-random.randint(0,5))
        if target.guard: dmg//=2; target.guard=False
        target.hp=max(0,target.hp-dmg)
        addlog(f'{e.name} frappe {target.name} : -{dmg} PV')
        float_text(f'-{dmg}',300,390,RED); fx(300,380,RED)
        flash=8

def do_action(action):
    global active, selected_target, state, victory, flash
    h=heroes[active]
    if h.hp<=0: next_turn(); return
    targets=alive_enemies()
    if action=='attack' and targets:
        e=targets[selected_target%len(targets)]; dmg=max(3,h.power+random.randint(-4,5));
        if h.name=='Vesper' and random.random()<.25: dmg*=2; addlog('Coup critique !')
        e.hp=max(0,e.hp-dmg); addlog(f'{h.name} attaque {e.name} : -{dmg} PV'); float_text(f'-{dmg}',e.x,e.y-55,RED); fx(e.x,e.y,GOLD); flash=5; next_turn()
    elif action=='spell':
        cost=18 if h.name!='Nox' else 26
        if h.mana<cost: addlog('Pas assez de mana.'); return
        h.mana-=cost
        if h.name=='Myr':
            healed=0
            for a in heroes[:player_count]:
                if a.hp>0: a.hp=min(a.maxhp,a.hp+26); healed+=26
            addlog(f'{h.name} tisse un soin : +{healed} PV partagés'); float_text(f'+{healed}',300,400,GREEN); fx(300,390,BLUE,'spell'); next_turn()
        elif h.name=='Orun':
            for a in heroes[:player_count]:
                if a.hp>0: a.guard=True
            addlog('Orun lève le Rempart : dégâts réduits au prochain tour.'); fx(450,350,GOLD,'spell'); next_turn()
        elif h.name=='Nox':
            dmg=25+random.randint(0,10)
            for e in targets: e.hp=max(0,e.hp-dmg)
            addlog(f'Nox déchaîne l’Éclat du vide : -{dmg} à tous'); fx(760,340,VIOLET,'spell'); float_text(f'-{dmg} TOUS',760,250,VIOLET); next_turn()
        else:
            e=targets[selected_target%len(targets)]; dmg=38+random.randint(-4,8); e.hp=max(0,e.hp-dmg)
            addlog(f'Vesper traverse {e.name} : -{dmg} PV'); float_text(f'-{dmg}',e.x,e.y-55,VIOLET); fx(e.x,e.y,VIOLET,'spell'); next_turn()
    elif action=='guard': h.guard=True; addlog(f'{h.name} se met en garde.'); fx(300,365,GREEN,'spell'); next_turn()
    elif action=='potion' and h.potions>0:
        h.potions-=1; h.hp=min(h.maxhp,h.hp+38); addlog(f'{h.name} boit une larme d’ambre : +38 PV'); float_text('+38',300,400,GOLD); fx(300,390,GOLD,'spell'); next_turn()
    if not alive_enemies(): state='end'; victory=True
    elif not alive_heroes(): state='end'; victory=False

def draw_menu():
    screen.fill(BG)
    # ornamental cavern
    for i in range(15):
        x=(i*83+30)%W; pygame.draw.polygon(screen,(22,25,39),[(x,0),(x+35,0),(x+15,100)])
    centered('ASHENVEIL',115,font_big,GOLD); centered('LE SANCTUAIRE FENDU',168,font, MUTED)
    centered('RPG tactique coopératif local • 2 à 4 joueurs',216,font,INK)
    pygame.draw.rect(screen,PANEL,(255,275,490,270),border_radius=12)
    centered('CHOISIR LE NOMBRE DE JOUEURS',305,font,INK)
    for i in range(2,5):
        r=pygame.Rect(330+(i-2)*115,355,85,65)
        pygame.draw.rect(screen,PANEL2 if i!=player_count else (81,62,100),r,border_radius=8)
        centered(str(i),365,font_big,GOLD if i==player_count else INK)
    centered('← / → ou LB / RB pour choisir   •   ENTRÉE ou A pour commencer',465,small,MUTED)
    status=f'{controller_count()} manette(s) détectée(s)' if controller_count() else 'Aucune manette détectée — clavier disponible'
    centered(status,515,mini,GREEN if controller_count() else MUTED)
    centered('Un jeu original inspiré des contes de chevaliers insectes et de cavernes oubliées.',585,mini,MUTED)

def draw_battle():
    now=pygame.time.get_ticks()/1000
    if ART.get('bg'):
        bg=pygame.transform.smoothscale(ART['bg'],(W,H)); screen.blit(bg,(0,0))
        screen.fill((8,10,22,105),special_flags=pygame.BLEND_RGBA_MULT)
    else: screen.fill(BG)
    pygame.draw.rect(screen,(10,12,25,210),(0,0,W,82))
    text(f'CHAMBRE {round_no}',28,18,small,GOLD); text(f'TOUR DE {heroes[active].name.upper()}',28,42,font,heroes[active].color)
    text('TAB / ← → cible   •   A attaque   S sort   G garde   P potion',380,30,small,MUTED)
    # Animated hero lineup with illustrated sprites.
    hero_x=[112,265,418,571]
    for i,h in enumerate(heroes[:player_count]):
        x=hero_x[i]; y=338+int(math.sin(now*3+i)*4)
        if i==active:
            pygame.draw.ellipse(screen,(*h.color,80),(x-58,y+58,116,28),2)
            pygame.draw.circle(screen,(*h.color,55),(x,y-35),78,3)
        if h.guard: pygame.draw.circle(screen,GREEN,(x,y+5),70,3)
        img=ART.get(h.name)
        if img:
            sprite=pygame.transform.smoothscale(img,(145,145)); screen.blit(sprite,(x-72,y-105))
        else: pygame.draw.circle(screen,h.color,(x,y-30),38)
        text(h.name,x-35,y+62,mini,h.color)
    # Enemy silhouettes and boss sprite.
    for i,e in enumerate(enemies[:2]):
        if e.hp<=0: continue
        x=735+i*72; y=265+i*92+int(math.sin(now*2+i)*6)
        pygame.draw.circle(screen,(*e.color,80),(x,y),38)
        pygame.draw.polygon(screen,e.color,[(x,y-35),(x+30,y+24),(x,y+42),(x-30,y+24)])
        text(e.name,x-40,y+48,mini,INK); bar(x-38,y+64,76,7,e.hp,e.maxhp,RED)
    boss=enemies[2]
    if boss.hp>0:
        x=815; y=305+int(math.sin(now*2.5)*5); img=ART.get('cinder')
        if img:
            sprite=pygame.transform.smoothscale(img,(250,250)); screen.blit(sprite,(x-125,y-145))
        if selected_target%len(enemies)==2: pygame.draw.circle(screen,GOLD,(x,y-25),132,3)
        text(boss.name,x-65,y+93,small,(255,155,190)); bar(x-80,y+112,160,10,boss.hp,boss.maxhp,RED)
    # Cards and action dock.
    pygame.draw.rect(screen,(13,15,29,235),(0,505,W,195))
    for i,h in enumerate(heroes[:player_count]):
        x=18+i*190; active_bg=(70,46,82) if i==active else (25,28,45)
        pygame.draw.rect(screen,active_bg,(x,520,178,125),border_radius=10)
        pygame.draw.rect(screen,h.color,(x,520,6,125),border_radius=4)
        text(f'J{i+1}  {h.name}',x+15,532,small,h.color); text(h.role,x+15,555,mini,MUTED)
        bar(x+15,576,145,9,h.hp,h.maxhp,RED); text(f'{h.hp}/{h.maxhp}',x+15,589,mini,INK)
        bar(x+15,610,145,7,h.mana,h.maxmana,BLUE); text(f'MANA {h.mana}',x+15,620,mini,INK)
    h=heroes[active]
    pygame.draw.rect(screen,(40,32,58),(790,520,190,125),border_radius=10)
    text(h.spell,805,534,small,h.color); text('A  ATTAQUE',805,562,mini,INK); text('S  SORT',805,580,mini,BLUE); text('G  GARDE',805,598,mini,GREEN); text('P  POTION',805,616,mini,GOLD)
    draw_fx()
    if flash: pygame.draw.rect(screen,(255,255,255),(0,0,W,H),2)

def draw_end():
    draw_battle(); pygame.draw.rect(screen,(8,9,16,220),(170,150,660,330),border_radius=16)
    centered('SANCTUAIRE VAINCU' if victory else 'LES LUMIÈRES S’ÉTEIGNENT',210,font_big,GOLD if victory else RED)
    centered('La toile du destin a été tissée.' if victory else 'Même les ombres ont besoin de repos.',275,font,INK)
    centered('R pour recommencer  •  ÉCHAP pour le menu',365,small,MUTED)

def main():
    global state, player_count, selected_target, flash
    running=True
    while running:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            if ev.type==pygame.JOYDEVICEADDED:
                try: pygame.joystick.Joystick(ev.device_index).init()
                except pygame.error: pass
            if ev.type==pygame.JOYDEVICEREMOVED:
                pass
            if ev.type==pygame.JOYBUTTONDOWN:
                handle_controller_button(ev.button)
            if ev.type==pygame.JOYHATMOTION:
                handle_controller_hat(ev.value)
            if ev.type==pygame.KEYDOWN:
                if state=='menu':
                    if ev.key==pygame.K_LEFT: player_count=max(2,player_count-1)
                    if ev.key==pygame.K_RIGHT: player_count=min(4,player_count+1)
                    if ev.key in (pygame.K_RETURN,pygame.K_KP_ENTER): reset_game(player_count)
                elif state=='battle':
                    if ev.key==pygame.K_TAB or ev.key==pygame.K_RIGHT: selected_target=(selected_target+1)%max(1,len(enemies))
                    if ev.key==pygame.K_LEFT: selected_target=(selected_target-1)%max(1,len(enemies))
                    if ev.key==pygame.K_a: do_action('attack')
                    if ev.key==pygame.K_s: do_action('spell')
                    if ev.key==pygame.K_g: do_action('guard')
                    if ev.key==pygame.K_p: do_action('potion')
                    if ev.key==pygame.K_ESCAPE: state='menu'
                elif state=='end':
                    if ev.key==pygame.K_r: reset_game(player_count)
                    if ev.key==pygame.K_ESCAPE: state='menu'
        if state=='menu': draw_menu()
        elif state=='battle': draw_battle()
        else: draw_end()
        update_fx()
        if flash: flash-=1
        pygame.display.flip(); clock.tick(30)
    pygame.quit(); sys.exit()

if __name__=='__main__': main()
