import pygame

class TextBox:
    def __init__(self, x, y, w, h, start_val, label, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(start_val)
        self.label = label
        self.active = False
        self.val = float(start_val)
        self.font = font

    def draw(self, surface):
        color = (50, 200, 50) if self.active else (150, 150, 150)
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        lbl_surf = self.font.render(self.label, True, (0, 0, 0))
        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 20))
        
        txt_surf = self.font.render(self.text, True, (0, 0, 0))
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


class Slider: 
    def __init__(self, x, y, w, min_val, max_val, start_val, label, font):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min = min_val
        self.max = max_val
        self.val = start_val
        self.label = label
        self.dragging = False
        self.font = font

    def draw(self, surface):
        pygame.draw.rect(surface, (150, 150, 150), self.rect, border_radius=10)
        
        ratio = 0
        if self.max > self.min:
            ratio = (self.val - self.min) / (self.max - self.min)
            
        knob_x = self.rect.x + int(ratio * self.rect.width)
        pygame.draw.circle(surface, (50, 50, 200), (knob_x, self.rect.centery), 12)
        
        text = self.font.render(f"{self.label}: {int(self.val)}", True, (0, 0, 0))
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
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

    def draw(self, surface):
        bg_color = (50, 200, 50) if self.text == "PLAY" else (200, 50, 50)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 15, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False