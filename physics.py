import math


PIXELS_PER_METER = 100.0   # Mutable -- zoom in main.py adjusts this
gravity       = 9.81
water_world_y = 5.0
dt            = 0.016

history       = []
current_frame = 0
is_playing    = True

# --- VISCOSITY COLOR CONSTANTS ---
COLOR_THIN  = (166, 166, 166)   # #a6a6a6 -- Liquid Helium
COLOR_THICK = ( 11,  31,  58)   # #0B1F3A -- Tar / Pitch
LOG_MIN = -6.0
LOG_MAX =  6.0

# --- viscosity_to_liquid_color ---
def viscosity_to_liquid_color(viscosity_pas):
    """
    Maps a viscosity value (Pa.s) to an RGB color on a log10 scale.
    Returns an (R, G, B) tuple.
    """
    if viscosity_pas <= 0:
        viscosity_pas = 10 ** LOG_MIN
    log_v = math.log10(viscosity_pas)
    t = (log_v - LOG_MIN) / (LOG_MAX - LOG_MIN)
    t = max(0.0, min(1.0, t))
    r = int(COLOR_THIN[0] + t * (COLOR_THICK[0] - COLOR_THIN[0]))
    g = int(COLOR_THIN[1] + t * (COLOR_THICK[1] - COLOR_THIN[1]))
    b = int(COLOR_THIN[2] + t * (COLOR_THICK[2] - COLOR_THIN[2]))
    return (r, g, b)

# --- FUNCTION -- reset_simulation ---
#     reset_simulation(text_boxes)
def reset_simulation(text_boxes):
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

# --- FUNCTION -- calculate_next_frame ---
#     calculate_next_frame(state, text_boxes)
def calculate_next_frame(state, text_boxes):
    y_m  = state['y_m']
    v    = state['v']

    radius_m       = text_boxes["radius"].val
    mass           = text_boxes["mass"].val
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

    drag_coefficient   = 0.47
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