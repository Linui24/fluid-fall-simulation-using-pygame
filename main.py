import pygame
import ui
import physics

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fluid Dynamics Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# --- UI SETUP ---
ui_x = 575
text_boxes = {
    "viscosity": ui.TextBox(ui_x, 40, 200, 30, 0.00089, "Viscosity (Pa.s)", font),
    "density": ui.TextBox(ui_x, 110, 200, 30, 1000.0, "Liquid Density (kg/m^3)", font),
    "radius": ui.TextBox(ui_x, 180, 200, 30, 1.0, "Radius (m)", font),
    "mass": ui.TextBox(ui_x, 250, 200, 30, 1.0, "Mass (kg)", font),
    "drop_h": ui.TextBox(ui_x, 320, 200, 30, 0.0, "Drop Height (m)", font)
}

time_slider = ui.Slider(20, 540, 420, 0, 100, 0, "Timeline Scrubber", font)
play_btn = ui.Button(ui_x, 530, 80, 40, "PAUSE", font)

# --- SIMULATION STATE ---
PIXELS_PER_METER = 100.0
history = []
current_frame = 0
is_playing = True

def reset_simulation():
    global history, current_frame
    history.clear()
    current_frame = 0
    
    radius_m = text_boxes["radius"].val
    
    initial_state = {
        'y_m': physics.water_world_y - text_boxes["drop_h"].val - radius_m,
        'v': 0.0,
        'f_net': 0.0,
        'f_buoyancy': 0.0,
        'f_drag': 0.0
    }
    history.append(initial_state)

reset_simulation()

# --- MAIN LOOP ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        any_box_active = any(box.active for box in text_boxes.values())
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not any_box_active:
            is_playing = not is_playing
            play_btn.text = "PAUSE" if is_playing else "PLAY"

        if play_btn.handle_event(event):
            is_playing = not is_playing
            play_btn.text = "PAUSE" if is_playing else "PLAY"

        for key, box in text_boxes.items():
            if box.handle_event(event):
                reset_simulation()
                time_slider.val = 0
                time_slider.max = 0
                
        if time_slider.handle_event(event):
            is_playing = False
            play_btn.text = "PLAY"
            current_frame = int(time_slider.val)

    if is_playing:
        if current_frame < len(history) - 1:
            history = history[:current_frame + 1]
            
        next_state = physics.calculate_next_frame(
            state=history[-1],
            radius_m=text_boxes["radius"].val,
            mass=text_boxes["mass"].val,
            liquid_density=text_boxes["density"].val
        )
        history.append(next_state)
        current_frame += 1

    time_slider.max = max(0, len(history) - 1)
    if is_playing:
        time_slider.val = current_frame

    # --- RENDERING ---
    screen.fill((220, 220, 220)) 

    if current_frame >= len(history):
        current_frame = len(history) - 1
        
    current_state = history[current_frame]
    y_m = current_state['y_m']
    v = current_state['v']
    radius_m = text_boxes["radius"].val

    ball_screen_x = 275
    ball_screen_y = 250
    distance_from_ball_to_water_m = physics.water_world_y - y_m
    water_screen_y = ball_screen_y + (distance_from_ball_to_water_m * PIXELS_PER_METER)

    if water_screen_y < HEIGHT:
        pygame.draw.rect(screen, (100, 150, 200), (0, int(water_screen_y), 550, HEIGHT - int(water_screen_y)))
    
    pygame.draw.circle(screen, (200, 50, 50), (ball_screen_x, ball_screen_y), int(radius_m * PIXELS_PER_METER))

    # UI Panels
    pygame.draw.rect(screen, (240, 240, 240), (550, 0, 250, HEIGHT))
    pygame.draw.line(screen, (150, 150, 150), (550, 0), (550, HEIGHT), 2)
    pygame.draw.rect(screen, (240, 240, 240), (0, 500, 550, 100))
    pygame.draw.line(screen, (150, 150, 150), (0, 500), (550, 500), 2)

    for box in text_boxes.values():
        box.draw(screen)
    time_slider.draw(screen)
    play_btn.draw(screen)

    # --- TELEMETRY DISPLAY ---
    elapsed_seconds = current_frame * physics.dt
    
    telemetry_data = [
        f"Ball World Y: {y_m:.2f} m",
        f"Velocity: {v:.2f} m/s",
        f"Time: {elapsed_seconds:.2f} s",
        f"Net Force: {current_state['f_net']:.2f} N"
    ]
    
    for i, text in enumerate(telemetry_data):
        img = font.render(text, True, (0, 0, 0))
        screen.blit(img, (10, 10 + (i * 25)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()