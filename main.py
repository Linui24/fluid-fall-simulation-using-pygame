# --- main.py: IMPORTS ---
import pygame
import physics                      # module ref needed to mutate physics.PIXELS_PER_METER
from physics import (
    gravity, water_world_y, dt,
    history, current_frame, is_playing,
    viscosity_to_liquid_color, reset_simulation, calculate_next_frame
)
from UI import (
    font, text_boxes, time_slider, play_btn, run_new_btn,
    zoom_in_btn, zoom_out_btn, ZOOM_LABEL_X, ZOOM_LABEL_Y
)
# NOTE: pygame.init() was already called inside UI.py -- no need to repeat it.

# --- main.py: WINDOW SETUP ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fluid Dynamics Simulation")
clock = pygame.time.Clock()

# --- main.py: INITIAL SIMULATION RESET ---
reset_simulation(text_boxes)

# --- main.py: MAIN LOOP ---
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
                pass  # dirty check handled below

        run_new_btn.enabled = any(box.is_dirty() for box in text_boxes.values())

        if run_new_btn.handle_event(event):
            for box in text_boxes.values():
                box.commit()
            reset_simulation(text_boxes)
            time_slider.val = 0
            time_slider.max = 0
            run_new_btn.enabled = False
            is_playing = True
            play_btn.text = "PAUSE"

        if time_slider.handle_event(event):
            is_playing = False
            play_btn.text = "PLAY"
            current_frame = int(time_slider.val)

        # ADAPTATION NOTE for zoom:
        # PIXELS_PER_METER lives in physics.py, so mutate it via the module object,
        # not via the locally-imported name (that would only update main.py's copy).
        if zoom_in_btn.handle_event(event):
            physics.PIXELS_PER_METER = min(500.0, physics.PIXELS_PER_METER * 1.25)

        if zoom_out_btn.handle_event(event):
            physics.PIXELS_PER_METER = max(5.0, physics.PIXELS_PER_METER / 1.25)

    if is_playing:
        if current_frame < len(history) - 1:
            history = history[:current_frame + 1]
        next_state = calculate_next_frame(history[-1], text_boxes)
        history.append(next_state)
        current_frame += 1

    time_slider.max = max(0, len(history) - 1)
    if is_playing:
        time_slider.val = current_frame

    # --- main.py: RENDERING ---
    screen.fill((220, 220, 220))

    if current_frame >= len(history):
        current_frame = len(history) - 1

    current_state = history[current_frame]
    y_m      = current_state['y_m']
    v        = current_state['v']
    radius_m = text_boxes["radius"].val

    ball_screen_x = 275
    ball_screen_y = 250
    distance_from_ball_to_water_m = water_world_y - y_m
    water_screen_y = ball_screen_y + (distance_from_ball_to_water_m * physics.PIXELS_PER_METER)

    liquid_color = viscosity_to_liquid_color(text_boxes["viscosity"].val)

    if water_screen_y < HEIGHT:
        pygame.draw.rect(screen, liquid_color,
                         (0, int(water_screen_y), 550, HEIGHT - int(water_screen_y)))

    ball_radius_px = max(1, int(radius_m * physics.PIXELS_PER_METER))
    pygame.draw.circle(screen, (200, 50, 50),
                       (ball_screen_x, ball_screen_y), ball_radius_px)

    # UI Panels
    pygame.draw.rect(screen, (240, 240, 240), (550, 0, 250, HEIGHT))
    pygame.draw.line(screen, (150, 150, 150), (550, 0), (550, HEIGHT), 2)
    pygame.draw.rect(screen, (240, 240, 240), (0, 500, 550, 100))
    pygame.draw.line(screen, (150, 150, 150), (0, 500), (550, 500), 2)

    for box in text_boxes.values():
        box.draw(screen)

    time_slider.draw(screen)
    play_btn.draw(screen)
    run_new_btn.draw(screen)

    zoom_lbl = font.render("Zoom:", True, (0, 0, 0))
    screen.blit(zoom_lbl, (ZOOM_LABEL_X, ZOOM_LABEL_Y))
    zoom_in_btn.draw(screen)
    zoom_out_btn.draw(screen)

    # --- main.py: TELEMETRY DISPLAY ---
    elapsed_seconds = current_frame * dt

    display_mass = text_boxes["mass"].val
    if display_mass <= 0.001: display_mass = 0.001
    downward_force = display_mass * gravity
    upward_force   = current_state['f_buoyancy'] + current_state['f_drag']

    lc_hex = "#{:02X}{:02X}{:02X}".format(*liquid_color)

    telemetry_data = [
        f"Ball World Y: {y_m:.2f} m",
        f"Velocity: {v:.2f} m/s",
        f"Time: {elapsed_seconds:.2f} s",
        #f"Downwards Force: {downward_force:.2f} N",
        #f"Upwards Force: {upward_force:.2f} N",
        f"Net Force: {current_state['f_net']:.2f} N",
        #f"Liquid Color: {lc_hex}"
    ]

    for i, text in enumerate(telemetry_data):
        img = font.render(text, True, (0, 0, 0))
        screen.blit(img, (10, 10 + (i * 25)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
