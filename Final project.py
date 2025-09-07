from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time  # the standard Python time module

# --- Arena and Camera ---
camera_pos = (0, -800, 400)
GRID_LENGTH = 600

# --- Game State ---
is_game_over = False
score = 0
ammo = 25
wave = 0
MAX_WAVES = 5
game_start_time = 0
game_timer_seconds = 90
final_game_time = 0

# --- Cannon State ---
CANNON_POS = (0, -GRID_LENGTH + 150, 25)
CANNON_BARREL_LENGTH = 80
gun_angle = 0.0
GUN_ROTATION_SPEED = 3.0
last_fire_time = 0
fire_cooldown = 0.25 # Adjusted to seconds

# --- Bullet State ---
bullets = []
BULLET_SPEED = 25.0
BULLET_RADIUS = 8

# --- Target State ---
targets = []
base_target_radius = 45
base_target_speed = 1.5

# --- Power-up State ---
powerups = []
last_powerup_spawn_time = 0
POWERUP_SPAWN_INTERVAL = 10  # Adjusted to seconds
POWERUP_SIZE = 25
rapid_fire_end_time = 0
score_multiplier_shots = 0

# --- Cheat Modes ---
infinite_ammo = False
wallhack_vision = False
auto_aim = False


def end_game(win=False):
    global is_game_over, final_game_time
    # Only capture the time the first time end_game is called
    if not is_game_over:
        is_game_over = True
       
        elapsed_time = time.time() - game_start_time
        final_game_time = max(0, game_timer_seconds - elapsed_time)
    globals()['game_won'] = win

def spawn_target(speed, radius):
    x = random.uniform(-GRID_LENGTH + radius, GRID_LENGTH - radius)
    y = random.uniform(200, GRID_LENGTH - radius)
    targets.append([x, y, radius, radius, [random.uniform(0.5, 1.0) for _ in range(3)], 1 if random.random() < 0.5 else -1, speed])

def start_new_wave():
    global wave
    wave += 1
    if wave > MAX_WAVES:
        end_game(win=True)
        return

    num_targets = wave * 2 + 2
    speed = base_target_speed + (wave * 0.3)
    radius = max(20, base_target_radius - (wave * 4))
    for _ in range(num_targets):
        spawn_target(speed, radius)

def spawn_powerup():
    x = random.uniform(-GRID_LENGTH / 2, GRID_LENGTH / 2)
    y = random.uniform(100, GRID_LENGTH / 2)
    
    powerups.append([random.randint(0, 3), x, y, POWERUP_SIZE, time.time()])

def fire_bullet():
    global ammo, bullets, gun_angle
        
    if not infinite_ammo:
        if ammo > 0:
            ammo -= 1
        else:
            return
            
    angle_rad = math.radians(gun_angle)
    dir_x = math.cos(angle_rad)
    dir_y = math.sin(angle_rad)

    spawn_x = CANNON_POS[0] + dir_x * CANNON_BARREL_LENGTH
    spawn_y = CANNON_POS[1] + dir_y * CANNON_BARREL_LENGTH
    spawn_z = CANNON_POS[2] + 20
    
    bullets.append([spawn_x, spawn_y, spawn_z, dir_x, dir_y])

def reset_game():
    global score, ammo, is_game_over, wave, gun_angle, game_start_time, bullets, targets, powerups
    global infinite_ammo, wallhack_vision, auto_aim, rapid_fire_end_time, score_multiplier_shots, last_powerup_spawn_time
    global final_game_time
    score, ammo, wave, gun_angle = 0, 25, 0, 0.0
    is_game_over, infinite_ammo, wallhack_vision, auto_aim = False, False, False, False
    rapid_fire_end_time, score_multiplier_shots = 0, 0
    final_game_time = 0
    bullets.clear(); targets.clear(); powerups.clear()
   
    current_time = time.time()
    game_start_time = current_time
    last_powerup_spawn_time = current_time
    start_new_wave()

def draw_border():
    border_width = 10
    glColor3f(0.5, 0.1, 0.1)
    
    glBegin(GL_QUADS)
    # Top border
    glVertex3f(-GRID_LENGTH - border_width, GRID_LENGTH, 1)
    glVertex3f(GRID_LENGTH + border_width, GRID_LENGTH, 1)
    glVertex3f(GRID_LENGTH + border_width, GRID_LENGTH + border_width, 1)
    glVertex3f(-GRID_LENGTH - border_width, GRID_LENGTH + border_width, 1)
    # Bottom border
    glVertex3f(-GRID_LENGTH - border_width, -GRID_LENGTH - border_width, 1)
    glVertex3f(GRID_LENGTH + border_width, -GRID_LENGTH - border_width, 1)
    glVertex3f(GRID_LENGTH + border_width, -GRID_LENGTH, 1)
    glVertex3f(-GRID_LENGTH - border_width, -GRID_LENGTH, 1)
    # Left border
    glVertex3f(-GRID_LENGTH - border_width, -GRID_LENGTH, 1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 1)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 1)
    glVertex3f(-GRID_LENGTH - border_width, GRID_LENGTH, 1)
    # Right border
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 1)
    glVertex3f(GRID_LENGTH + border_width, -GRID_LENGTH, 1)
    glVertex3f(GRID_LENGTH + border_width, GRID_LENGTH, 1)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 1)
    glEnd()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text: glutBitmapCharacter(font, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_hud():
    draw_text(20, 760, f"Score: {score}")
    draw_text(20, 720, f"Ammo: {'INF' if infinite_ammo else str(ammo)}")
    draw_text(20, 680, f"Wave: {wave}/{MAX_WAVES}")
    
    if is_game_over:
        remaining_time = final_game_time
    else:
        
        remaining_time = max(0, game_timer_seconds - (time.time() - game_start_time))
        
    mins, secs = divmod(int(remaining_time), 60)
    draw_text(440, 760, f"Time: {mins:02d}:{secs:02d}")
    
    if infinite_ammo: draw_text(800, 760, "CHEAT: INF AMMO")
    if wallhack_vision: draw_text(800, 720, "CHEAT: WALLHACK")
    if auto_aim: draw_text(800, 680, "CHEAT: AUTO-AIM")
    
    if time.time() < rapid_fire_end_time: draw_text(800, 640, "RAPID FIRE!")
    if score_multiplier_shots > 0: draw_text(800, 600, f"2X SCORE ({score_multiplier_shots})")
    
    if is_game_over:
        win_lose_text = "YOU WIN!" if globals().get('game_won') else "GAME OVER"
        draw_text(420, 450, win_lose_text)
        draw_text(390, 410, "Press 'R' to Restart")

def draw_shapes():
    glColor3f(1, 1, 0)
    for b in bullets:
        glPushMatrix(); glTranslatef(b[0], b[1], b[2]); gluSphere(gluNewQuadric(), BULLET_RADIUS, 10, 10); glPopMatrix()
    for t in targets:
        if wallhack_vision: glColor3f(1, 0.5, 0)
        else: glColor3f(*t[4])
        glPushMatrix(); glTranslatef(t[0], t[1], t[2]); gluSphere(gluNewQuadric(), t[3], 20, 20); glPopMatrix()
    for p in powerups:
     #time.time() and adjusted the sine wave multiplier for seconds
        brightness = 0.6 + 0.4 * math.sin((time.time() - p[4]) * 5)
        colors = [(brightness, brightness, 0), (0, 0, brightness), (brightness, 0, 0), (0, brightness, 0)]
        glPushMatrix(); glColor3f(*colors[p[0]]); glTranslatef(p[1], p[2], p[3])
        if p[0] in [0, 3]: glutSolidCube(POWERUP_SIZE)
        elif p[0] == 1: gluSphere(gluNewQuadric(), POWERUP_SIZE / 1.5, 15, 15)
        else: glRotatef(90, 1, 0, 0); gluCylinder(gluNewQuadric(),POWERUP_SIZE/2,POWERUP_SIZE/2,POWERUP_SIZE*1.5,10,10)
        glPopMatrix()
    glColor3f(0.2, 0.6, 0.9); glPushMatrix(); glTranslatef(-300, 300, 75); glutSolidCube(150); glPopMatrix()
    glColor3f(0.8, 0.8, 0.3); glPushMatrix(); glTranslatef(350, 200, 80); gluSphere(gluNewQuadric(), 80, 20, 20); glPopMatrix()
    glPushMatrix(); glTranslatef(*CANNON_POS); glRotatef(gun_angle, 0, 0, 1)
    glColor3f(0.3, 0.3, 0.4); glutSolidCube(40)
    glColor3f(0.5, 0.5, 0.6); glTranslatef(20, 0, 20); glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 8, 8, CANNON_BARREL_LENGTH, 10, 10); glPopMatrix()

def setupCamera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(70, 1.25, 1, 4000)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    gluLookAt(*camera_pos, 0, 150, 50, 0, 0, 1)

def keyboardListener(key, x, y):
    global gun_angle, infinite_ammo, wallhack_vision, auto_aim
    if not is_game_over:
       if key == b'd': gun_angle -= GUN_ROTATION_SPEED
       if key == b'a': gun_angle += GUN_ROTATION_SPEED
    if key == b'c': infinite_ammo = not infinite_ammo
    if key == b'v': wallhack_vision = not wallhack_vision
    if key == b'b': auto_aim = not auto_aim
    if key == b'r': reset_game()


if __name__ == "__main__":
    main()
