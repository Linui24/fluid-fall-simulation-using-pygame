import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fluid Dynamics Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# --- UI WIDGET CLASSES ---
class TextBox:
    def __init__(self, x, y, w, h, start_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(start_val)
        self.label = label
        self.active = False
        self.val = float(start_val)
        # [NEW] Track whether this box's value differs from the last-run value
        self.committed_val = float(start_val)

    def draw(self, surface):
        color = (50, 200, 50) if self.active else (150, 150, 150)
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        lbl_surf = font.render(self.label, True, (0, 0, 0))
        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 20))
        
        txt_surf = font.render(self.text, True, (0, 0, 0))
        surface.blit(txt_surf, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event):
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                if self.active:
                    self.active = False
                    self.update_val()
                    changed = True
                    
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.update_val()
                changed = True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text):
                    self.text += event.unicode
        return changed

    def update_val(self):
        if self.text == '' or self.text == '.':
            self.text = '0'
        self.val = float(self.text)
        self.text = str(self.val)

    # [NEW] Mark the current val as "committed" (used after Run With New Values is clicked)
    def commit(self):
        self.committed_val = self.val

    # [NEW] Check whether the current val differs from the committed val
    def is_dirty(self):
        return self.val != self.committed_val


class Slider: 
    def __init__(self, x, y, w, min_val, max_val, start_val, label):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min = min_val
        self.max = max_val
        self.val = start_val
        self.label = label
        self.dragging = False

    def draw(self, surface):
        pygame.draw.rect(surface, (150, 150, 150), self.rect, border_radius=10)
        
        ratio = 0
        if self.max > self.min:
            ratio = (self.val - self.min) / (self.max - self.min)
            
        knob_x = self.rect.x + int(ratio * self.rect.width)
        pygame.draw.circle(surface, (50, 50, 200), (knob_x, self.rect.centery), 12)
        
        text = font.render(f"{self.label}: {int(self.val)}", True, (0, 0, 0))
        surface.blit(text, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_val(event.pos[0])
            return True
        return False

    def update_val(self, mouse_x):
        ratio = max(0, min(1, (mouse_x - self.rect.x) / self.rect.width))
        self.val = int(self.min + ratio * (self.max - self.min))


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, (50, 200, 50) if self.text == "PLAY" else (200, 50, 50), self.rect, border_radius=5)
        text_surf = font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 15, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# [NEW] --- RUN WITH NEW VALUES BUTTON CLASS ---
# This button is grayed out (disabled) until at least one TextBox has a dirty value.
# Once dirty, it lights up in orange and becomes clickable.
class RunButton:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.enabled = False  # Starts disabled; no changes made yet

        # Colors
        self.color_disabled = (160, 160, 160)
        self.color_enabled  = (220, 120, 20)   # Orange: visually distinct from PLAY/PAUSE
        self.color_hover    = (255, 150, 30)
        self.text_color     = (255, 255, 255)

    def draw(self, surface):
        # Check hover only when enabled
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos) and self.enabled

        color = self.color_hover if is_hovered else (self.color_enabled if self.enabled else self.color_disabled)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)

        # Draw label; two lines to fit the button width neatly
        line1 = font.render("Run With", True, self.text_color)
        line2 = font.render("New Values", True, self.text_color)
        surface.blit(line1, (self.rect.x + (self.rect.width - line1.get_width()) // 2,
                              self.rect.y + 6))
        surface.blit(line2, (self.rect.x + (self.rect.width - line2.get_width()) // 2,
                              self.rect.y + 22))

        # Subtle border when disabled so it still reads as a button
        if not self.enabled:
            pygame.draw.rect(surface, (120, 120, 120), self.rect, 1, border_radius=5)

    def handle_event(self, event):
        """Returns True only when the button is enabled and the user clicks it."""
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# [NEW] --- ZOOM BUTTON CLASS ---
# Simple +/- style buttons that adjust the global PIXELS_PER_METER scale.
class ZoomButton:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label   # "+" or "-"

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = (80, 80, 200) if is_hovered else (60, 60, 170)
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        lbl = font.render(self.label, True, (255, 255, 255))
        surface.blit(lbl, (self.rect.x + (self.rect.width  - lbl.get_width())  // 2,
                            self.rect.y + (self.rect.height - lbl.get_height()) // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# --- UI SETUP ---
ui_x = 575

text_boxes = {
    "viscosity": TextBox(ui_x, 40,  200, 30, 0.00089, "Viscosity (Pa.s)"),
    "density":   TextBox(ui_x, 110, 200, 30, 1000.0,  "Liquid Density (kg/m^3)"),
    "radius":    TextBox(ui_x, 180, 200, 30, 1.0,     "Radius (m)"),
    "mass":      TextBox(ui_x, 250, 200, 30, 1.0,     "Mass (kg)"),
    "drop_h":    TextBox(ui_x, 320, 200, 30, 0.0,     "Drop Height (m)")
}

time_slider = Slider(20, 540, 420, 0, 100, 0, "Timeline Scrubber")
play_btn    = Button(ui_x, 530, 80, 40, "PAUSE")

# [NEW] Run With New Values button — placed below the parameter text boxes
run_new_btn = RunButton(ui_x, 390, 200, 42)

# [NEW] Zoom In / Zoom Out buttons — placed in the bottom-left simulation panel
#       alongside the telemetry readout, above the timeline slider area.
zoom_in_btn  = ZoomButton(460, 10, 40, 28, "+")
zoom_out_btn = ZoomButton(505, 10, 40, 28, "-")

# [NEW] Zoom label (static text rendered each frame next to the buttons)
ZOOM_LABEL_X = 420
ZOOM_LABEL_Y = 10


# --- [NEW] VISCOSITY → LIQUID COLOR SYSTEM ---
# Liquid color interpolates on a log10 scale between:
#   Thinnest: Liquid Helium  #a6a6a6  at η = 10^-6 Pa·s  (log = -6)
#   Thickest: Tar / Pitch    #0B1F3A  at η = 10^+6 Pa·s  (log = +6)
# Anything outside that range is clamped to the respective endpoint color.

COLOR_THIN  = (166, 166, 166)   # #a6a6a6 — Liquid Helium
COLOR_THICK = ( 11,  31,  58)   # #0B1F3A — Tar / Pitch

LOG_MIN = -6.0   # log10(10^-6)
LOG_MAX =  6.0   # log10(10^+6)

def viscosity_to_liquid_color(viscosity_pas):
    """
    Maps a viscosity value (Pa·s) to an RGB color using a log10 scale.
    Returns an (R, G, B) tuple.
    """
    # Guard against zero or negative viscosity before taking log
    if viscosity_pas <= 0:
        viscosity_pas = 10 ** LOG_MIN

    log_v = math.log10(viscosity_pas)

    # Clamp to [LOG_MIN, LOG_MAX]
    t = (log_v - LOG_MIN) / (LOG_MAX - LOG_MIN)
    t = max(0.0, min(1.0, t))

    # Linear interpolation between thin and thick colors
    r = int(COLOR_THIN[0] + t * (COLOR_THICK[0] - COLOR_THIN[0]))
    g = int(COLOR_THIN[1] + t * (COLOR_THICK[1] - COLOR_THIN[1]))
    b = int(COLOR_THIN[2] + t * (COLOR_THICK[2] - COLOR_THIN[2]))
    return (r, g, b)


# --- PHYSICS ENGINE STATE ---
# (NO changes below this line until the main loop UI section)
PIXELS_PER_METER = 100.0  # [NEW] This is now a mutable global — zoom adjusts it
gravity      = 9.81
water_world_y = 5.0
dt           = 0.016

history       = []
current_frame = 0
is_playing    = True

def reset_simulation():
    global history, current_frame
    history.clear()
    current_frame = 0
    
    radius_m = text_boxes["radius"].val
    
    initial_state = {
        'y_m':        water_world_y - text_boxes["drop_h"].val - radius_m,
        'v':          0.0,
        'f_net':      0.0,
        'f_buoyancy': 0.0,
        'f_drag':     0.0
    }
    history.append(initial_state)

def calculate_next_frame(state):
    # *** PHYSICS ENGINE — UNTOUCHED ***
    y_m  = state['y_m']
    v    = state['v']
    
    radius_m      = text_boxes["radius"].val
    mass          = text_boxes["mass"].val
    liquid_density = text_boxes["density"].val
    
    if mass <= 0.001: mass = 0.001 
    
    total_volume = (4/3) * math.pi * (radius_m ** 3)
    bottom_y_m   = y_m + radius_m
    
    h_cap_m = 0.0
    if bottom_y_m > water_world_y:
        h_cap_m = bottom_y_m - water_world_y
        if h_cap_m > (2 * radius_m):
            h_cap_m = 2 * radius_m

    if h_cap_m > 0:
        v_submerged = (math.pi * (h_cap_m ** 2) / 3) * (3 * radius_m - h_cap_m)
    else:
        v_submerged = 0.0

    f_weight   = mass * gravity
    f_buoyancy = liquid_density * v_submerged * gravity
    
    drag_coefficient  = 0.47
    cross_section_area = math.pi * (radius_m ** 2)
    f_drag_max = 0.5 * liquid_density * (v ** 2) * drag_coefficient * cross_section_area
    f_drag     = f_drag_max * (v_submerged / total_volume) if total_volume > 0 else 0
    if v < 0: f_drag = -f_drag

    f_net        = f_weight - f_buoyancy - f_drag
    acceleration = f_net / mass

    new_v   = v + acceleration * dt
    new_y_m = y_m + new_v * dt

    return {'y_m': new_y_m, 'v': new_v, 'f_net': f_net,
            'f_buoyancy': f_buoyancy, 'f_drag': f_drag}

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

        # Handle text-box edits
        # [CHANGED] Instead of immediately resetting the simulation on each edit,
        #           we now just mark the RunButton as enabled (dirty check).
        #           The actual reset happens only when RunButton is clicked.
        for key, box in text_boxes.items():
            if box.handle_event(event):
                # Check if any box now differs from its committed value
                pass  # dirty check is done below, outside the event loop

        # [NEW] Update RunButton enabled state each frame based on dirty text boxes
        run_new_btn.enabled = any(box.is_dirty() for box in text_boxes.values())

        # [NEW] Handle Run With New Values button click
        if run_new_btn.handle_event(event):
            # Commit all current values, then reset simulation with them
            for box in text_boxes.values():
                box.commit()
            reset_simulation()
            time_slider.val = 0
            time_slider.max = 0
            run_new_btn.enabled = False  # No longer dirty after reset
            # Resume playing with the new values
            is_playing = True
            play_btn.text = "PAUSE"

        if time_slider.handle_event(event):
            is_playing = False
            play_btn.text = "PLAY"
            current_frame = int(time_slider.val)

        # [NEW] Handle Zoom In button — increase pixels-per-meter, capped at 500
        if zoom_in_btn.handle_event(event):
            PIXELS_PER_METER = min(500.0, PIXELS_PER_METER * 1.25)

        # [NEW] Handle Zoom Out button — decrease pixels-per-meter, floored at 5
        if zoom_out_btn.handle_event(event):
            PIXELS_PER_METER = max(5.0, PIXELS_PER_METER / 1.25)

    if is_playing:
        if current_frame < len(history) - 1:
            history = history[:current_frame + 1]
            
        next_state = calculate_next_frame(history[-1])
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
    y_m      = current_state['y_m']
    v        = current_state['v']
    radius_m = text_boxes["radius"].val

    ball_screen_x = 275
    ball_screen_y = 250
    distance_from_ball_to_water_m = water_world_y - y_m
    # [CHANGED] water_screen_y now uses the mutable PIXELS_PER_METER for zoom support
    water_screen_y = ball_screen_y + (distance_from_ball_to_water_m * PIXELS_PER_METER)

    # [NEW] Compute liquid color from current viscosity setting each frame
    liquid_color = viscosity_to_liquid_color(text_boxes["viscosity"].val)

    if water_screen_y < HEIGHT:
        pygame.draw.rect(screen, liquid_color,
                         (0, int(water_screen_y), 550, HEIGHT - int(water_screen_y)))
    
    # [CHANGED] Ball radius also respects the mutable PIXELS_PER_METER for zoom
    ball_radius_px = max(1, int(radius_m * PIXELS_PER_METER))
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

    # [NEW] Draw Run With New Values button
    run_new_btn.draw(screen)

    # [NEW] Draw Zoom buttons and label
    zoom_lbl = font.render("Zoom:", True, (0, 0, 0))
    screen.blit(zoom_lbl, (ZOOM_LABEL_X, ZOOM_LABEL_Y))
    zoom_in_btn.draw(screen)
    zoom_out_btn.draw(screen)

    # [NEW] Draw current zoom level next to the zoom buttons
    #zoom_level_text = font.render(f"{int(PIXELS_PER_METER)}px/m", True, (60, 60, 60))
    #screen.blit(zoom_level_text, (549, ZOOM_LABEL_Y))

    # --- TELEMETRY DISPLAY (unchanged) ---
    elapsed_seconds = current_frame * dt
    
    display_mass = text_boxes["mass"].val
    if display_mass <= 0.001: display_mass = 0.001
    downward_force = display_mass * gravity
    upward_force   = current_state['f_buoyancy'] + current_state['f_drag']
    
    # [NEW] Build hex string from the live liquid_color for telemetry readout
    lc_hex = "#{:02X}{:02X}{:02X}".format(*liquid_color)

    telemetry_data = [
        f"Ball World Y: {y_m:.2f} m",
        f"Velocity: {v:.2f} m/s",
        f"Time: {elapsed_seconds:.2f} s",
        #f"Downwards Force: {downward_force:.2f} N",
        #f"Upwards Force: {upward_force:.2f} N",
        f"Net Force: {current_state['f_net']:.2f} N",
        #f"Liquid Color: {lc_hex}"    # [NEW] Shows the current liquid color hex
    ]
    
    for i, text in enumerate(telemetry_data):
        img = font.render(text, True, (0, 0, 0))
        screen.blit(img, (10, 10 + (i * 25)))

    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()