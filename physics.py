import math

gravity = 9.81
water_world_y = 5.0
dt = 0.016

def calculate_next_frame(state, radius_m, mass, liquid_density):
    y_m = state['y_m']
    v = state['v']
    
    if mass <= 0.001: 
        mass = 0.001 
    
    total_volume = (4/3) * math.pi * (radius_m ** 3)
    bottom_y_m = y_m + radius_m
    
    h_cap_m = 0.0
    if bottom_y_m > water_world_y:
        h_cap_m = bottom_y_m - water_world_y
        if h_cap_m > (2 * radius_m):
            h_cap_m = 2 * radius_m

    if h_cap_m > 0:
        v_submerged = (math.pi * (h_cap_m ** 2) / 3) * (3 * radius_m - h_cap_m)
    else:
        v_submerged = 0.0

    f_weight = mass * gravity
    f_buoyancy = liquid_density * v_submerged * gravity
    
    drag_coefficient = 0.47
    cross_section_area = math.pi * (radius_m ** 2)
    f_drag_max = 0.5 * liquid_density * (v ** 2) * drag_coefficient * cross_section_area
    f_drag = f_drag_max * (v_submerged / total_volume) if total_volume > 0 else 0
    if v < 0: 
        f_drag = -f_drag

    f_net = f_weight - f_buoyancy - f_drag
    acceleration = f_net / mass

    new_v = v + acceleration * dt
    new_y_m = y_m + new_v * dt

    return {
        'y_m': new_y_m, 
        'v': new_v, 
        'f_net': f_net, 
        'f_buoyancy': f_buoyancy, 
        'f_drag': f_drag
    }