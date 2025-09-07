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
