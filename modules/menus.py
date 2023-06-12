import pygame
from .config import *


class Button():
    def __init__(self, master, pos, action, button_list, text_color='white'):

        self.pos = pos
        self.action = action
        self.master = master
        self.screen = pygame.display.get_surface()
        self.text_color = text_color
        self.mouse_hover = False
        self.hover_sound_played = False


        self.image = self.master.font.render(action.upper(), False, self.text_color)
        self.rect = self.image.get_rect(center=pos)
        self.detection_rect = self.rect.inflate(10,10)

        self.underline = pygame.Surface((self.image.get_width(), 1))
        self.underline.fill(self.text_color)
        self.underline_rect = self.underline.get_rect(midtop=(self.rect.midbottom))

        self.shadow = self.master.font.render(action.upper(), False, (105, 75, 105))
        self.shadow.set_alpha(200)
        

        button_list.append(self)

    def interact(self, mouse_pos, click=False):

        if click and self.mouse_hover:
            if self.action not in ("start", "resume"):
                self.master.sounds["UI_Select"].play()

            return self.action
        self.mouse_hover = self.detection_rect.collidepoint(mouse_pos)
        if self.mouse_hover:
            if not self.hover_sound_played:
                self.hover_sound_played = True
                self.master.sounds["UI_Hover"].play()
        else:self.hover_sound_played = False

    def draw(self):
        
        if not self.mouse_hover:
            self.screen.blit(self.shadow, (self.rect.left-2, self.rect.top+2))
        else:
            self.screen.blit(self.underline, self.underline_rect)

        self.screen.blit(self.image, self.rect)


class MainMenu():

    def __init__(self, master):
        self.master = master
        self.master.main_menu = self
        self.screen = pygame.display.get_surface()
        self.x_shift = 0
        self.title_surf = self.master.font_big.render('Chrono Pilots', False, (235, 192, 72))
        self.title_rect = self.title_surf.get_rect(midtop=(W/2, 40))
        self.title_shadow = self.master.font_big.render('Chrono Pilots', False, (255, 212, 92))
        self.title_shadow.set_alpha(100)
        self.buttons:list[Button] = []
        self.create_buttons()
        
    def create_buttons(self):

        col = (252, 205, 146)
        Button(self.master, (W//2, H*0.5), 'start', self.buttons, col)
        Button(self.master, (W//2, H*0.6), 'fullscreen', self.buttons, col)
        Button(self.master, (W//2, H*0.7), 'quit', self.buttons, col)

    def update(self):

        self.x_shift += 0.5*self.master.dt
        self.x_shift %= W
        
        for event in pygame.event.get((pygame.MOUSEBUTTONDOWN)):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                for button in self.buttons:
                    action = button.interact(event.pos, click=True)
                    if action == 'start':
                        # self.master.music.change_track("in_game")
                        self.master.sounds["SFX_Spawn"].play()
                        self.master.app.state = self.master.app.INTRO_CUTSCENE
                    elif action == 'fullscreen':
                        pygame.display.toggle_fullscreen()
                    elif action == 'quit':
                        pygame.quit()
                        raise SystemExit
                    if action is not None:
                        return

    def draw(self):

        self.screen.fill(0x4C0805)

        self.screen.blit(self.title_shadow, (self.title_rect.x-2, self.title_rect.y+2))
        self.screen.blit(self.title_surf, self.title_rect)

        for button in self.buttons:
            button.draw()
            button.interact(pygame.mouse.get_pos())

    def run(self):
        self.update()
        self.draw()


class PauseMenu():

    def __init__(self, master):
        self.master = master
        self.master.pause_menu = self

        self.screen = pygame.display.get_surface()
        # self.bg = self.screen.copy()
        self.bg_overlay = pygame.Surface(self.screen.get_size())
        # self.bg_overlay.fill(0xb5737c)
        self.bg_overlay.set_alpha(150)

        self.buttons:list[Button] = []
        self.create_buttons()
        
    def create_buttons(self):

        Button(self.master, (W//2, H*0.4), 'resume', self.buttons)
        Button(self.master, (W//2, H*0.5), 'fullscreen', self.buttons)
        Button(self.master, (W//2, H*0.6), 'quit', self.buttons)

    def open(self):
        self.bg = pygame.transform.gaussian_blur(self.screen, 5, False)
        self.master.sounds["UI_Pause"].play()

    def update(self):
        
        for event in pygame.event.get((pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.master.game.paused = False
                self.master.sounds["UI_Return"].play()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                for button in self.buttons:
                    action = button.interact(event.pos, click=True)
                    if action == 'resume':
                        self.master.game.paused = False
                        self.master.sounds["UI_Return"].play()
                    elif action == 'fullscreen':
                        pygame.display.toggle_fullscreen()
                    elif action == 'quit':
                        pygame.quit()
                        raise SystemExit
                    if action is not None:
                        return
    def draw(self):

        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.bg_overlay, (0, 0))

        for button in self.buttons:
            button.draw()
            button.interact(pygame.mouse.get_pos())
            