# --- UI.py: IMPORTS ---
import pygame

# --- UI.py: PYGAME INIT & SHARED FONT ---
pygame.init()
font = pygame.font.SysFont("Arial", 16)

# --- UI.py: CLASS -- TextBox ---
class TextBox:
    def __init__(self, x, y, w, h, start_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(start_val)
        self.label = label
        self.active = False
        self.val = float(start_val)
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

    def commit(self):
        self.committed_val = self.val

    def is_dirty(self):
        return self.val != self.committed_val


# --- UI.py: CLASS -- Slider ---
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


# --- UI.py: CLASS -- Button ---
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, (50, 200, 50) if self.text == "PLAY" else (200, 50, 50),
                         self.rect, border_radius=5)
        text_surf = font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 15, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# --- UI.py: CLASS -- RunButton ---
class RunButton:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.enabled = False
        self.color_disabled = (160, 160, 160)
        self.color_enabled  = (220, 120, 20)
        self.color_hover    = (255, 150, 30)
        self.text_color     = (255, 255, 255)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos) and self.enabled
        color = self.color_hover if is_hovered else (self.color_enabled if self.enabled else self.color_disabled)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        line1 = font.render("Run With", True, self.text_color)
        line2 = font.render("New Values", True, self.text_color)
        surface.blit(line1, (self.rect.x + (self.rect.width - line1.get_width()) // 2,
                              self.rect.y + 6))
        surface.blit(line2, (self.rect.x + (self.rect.width - line2.get_width()) // 2,
                              self.rect.y + 22))
        if not self.enabled:
            pygame.draw.rect(surface, (120, 120, 120), self.rect, 1, border_radius=5)

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# --- UI.py: CLASS -- ZoomButton ---
class ZoomButton:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label

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


# --- UI.py: WIDGET INSTANCES ---
ui_x = 575

text_boxes = {
    "viscosity": TextBox(ui_x, 40,  200, 30, 0.00089, "Viscosity (Pa.s)"),
    "density":   TextBox(ui_x, 110, 200, 30, 1000.0,  "Liquid Density (kg/m^3)"),
    "radius":    TextBox(ui_x, 180, 200, 30, 1.0,     "Radius (m)"),
    "mass":      TextBox(ui_x, 250, 200, 30, 1.0,     "Mass (kg)"),
    "drop_h":    TextBox(ui_x, 320, 200, 30, 0.0,     "Drop Height (m)")
}

time_slider  = Slider(20, 540, 420, 0, 100, 0, "Timeline Scrubber")
play_btn     = Button(ui_x, 530, 80, 40, "PAUSE")
run_new_btn  = RunButton(ui_x, 390, 200, 42)
zoom_in_btn  = ZoomButton(460, 10, 40, 28, "+")
zoom_out_btn = ZoomButton(505, 10, 40, 28, "-")

# Zoom label position (read during rendering in main.py)
ZOOM_LABEL_X = 420
ZOOM_LABEL_Y = 10