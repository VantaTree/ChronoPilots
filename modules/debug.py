import pygame

class Debug:

    def __init__(self, display, font_size=12, offset=6, surf_enabled=False, font=None):

        self.screen = display
        self.surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.debug_list:list = list()
        self.font_size = font_size
        self.offset = offset
        if font is None:
            self.font = pygame.font.SysFont(None, self.font_size)
        else: self.font = font
        self.surf_enabled = surf_enabled
        self.on = True

    def __call__(self, name, value):
        
        if not self.on: return
        self.debug_list.append(name + str(value))

    def draw(self):

        if not self.on: return

        if self.surf_enabled:
            self.screen.blit(self.surface, (0, 0))
            self.surface.fill((0, 0, 0, 0))

        text_surf = self.font.render("\n".join(self.debug_list), False, (255,255,255), (0, 0, 0))
        self.screen.blit(text_surf, (self.offset, self.offset))

        self.debug_list.clear()
