import pygame
from .config import *
from .engine import *


class Choice(list): pass
class Check(list): pass


class InteractionManager:

    def __init__(self, master):

        self.master = master
        master.interaction_manager = self
        self.screen = pygame.display.get_surface()

        self.interact_button = pygame.image.load("graphics/ui/interact_button.png").convert_alpha()
        self.interact_button_rect = self.interact_button.get_rect()

        self.interactions = []
        self.active = None
        self.dialogue_obj = None

    def activate_text(self, key, obj):

        self.dialogue_obj = DialogueObject(self.master, key, obj)

    def pressed_interact(self):
        if self.active is not None:
            self.master.sounds["UI_Select"].play()
            self.active[1].interacted(self.active[0])

    def update(self):

        if self.interactions and self.dialogue_obj is None:

            self.active = min(self.interactions, key=lambda t: dist_sq((t[2][0]+t[2][2]/2, t[2][1]+t[2][3]/2), self.master.player.rect.center))
            # active = (name, obj, rect)

            name_surf = self.master.font_1.render(self.active[0], False, (255, 255, 255))

            self.interact_button_rect.midbottom = self.master.player.rect.midtop
            self.screen.blit(self.interact_button,self.master.player.rect.midtop -\
                        pygame.Vector2(self.interact_button.get_width()/2, self.interact_button.get_height()+name_surf.get_height()) +\
                        self.master.offset)
            # self.screen.blit(self.interact_button, self.interact_button_rect.topleft + self.master.offset)
            self.screen.blit(name_surf, self.master.player.rect.midtop -\
                pygame.Vector2(name_surf.get_width()/2, name_surf.get_height()) + self.master.offset)

            self.interactions.clear()

        else: self.active = None

        if self.dialogue_obj is not None:

            if self.dialogue_obj.update():
                self.active = None
                self.dialogue_obj = None
                self.master.player.in_control = True
                self.dialogue_obj = None
                self.interactions.clear()
                return
            self.dialogue_obj.draw()


            # key, obj = self.is_interacting
            # texts = obj.interaction_text_dict[key]
            # curr_text = texts["init"]
            # line = curr_text[self.page_index]

class DialogueObject:

    def __init__(self, master, obj_key, obj):

        self.master = master
        self.obj_key = obj_key
        self.key = "init"
        self.text_pos = (W/2, H-60) # midbottom
        self.obj = obj
        self.screen = pygame.display.get_surface()
        self.page_index = 0
        self.letter_index = 0
        self.full_line_shown = False

        self.in_multi_choice = False
        self.multi_c_index = 0

        self.letter_increment_timer = CustomTimer(True)
        self.letter_increment_timer.start(40, 0)

        self.the_text = obj.interaction_text_dict[obj_key]

        self.check_mcq_type()

        master.player.in_control = False

    def draw(self):

        if self.in_multi_choice:
            # self.master.debug("mc:", (self.multi_c_index, self.the_text[self.key][self.page_index]))
            
            for i, choice in enumerate(self.the_text[self.key][self.page_index][::-1]):
                text_surf = self.master.font_1.render(choice, False, (255, 255, 255))
                pos = (self.text_pos[0], self.text_pos[1] - (i*20)) - pygame.Vector2(text_surf.get_width()/2, text_surf.get_height())
                self.screen.blit(text_surf, pos)
                if self.multi_c_index == len(self.the_text[self.key][self.page_index]) - i - 1:
                    pygame.draw.line(self.screen, (80, 80, 80), (pos[0], pos[1]+text_surf.get_height()-2), (pos[0]+text_surf.get_width(), pos[1]+text_surf.get_height()-2), 2)

        else:
            text = self.the_text[self.key][self.page_index]
            cross_text = text if self.full_line_shown else text[:self.letter_index]
            text_surf = self.master.font_1.render(cross_text, False, (255, 255, 255), wraplength=W//2)
            self.screen.blit(text_surf, (self.text_pos[0], self.text_pos[1]) \
                            - pygame.Vector2(text_surf.get_width()/2, 40))

    def update(self):

        for event in pygame.event.get((pygame.KEYDOWN)):

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_e,):
                    self.master.sounds["UI_Select"].play()
                    if self.in_multi_choice:
                        pass
                        self.key = self.the_text[self.key][self.page_index][self.multi_c_index]
                        self.obj.select_choice(self.obj_key, self.key)
                        self.page_index = 0
                        self.full_line_shown = False
                        self.in_multi_choice = False
                        self.letter_index = 0
                        if self.check_mcq_type(): return True
                    elif self.full_line_shown:
                        self.page_index += 1
                        self.full_line_shown = False
                        self.letter_index = 0
                        if self.page_index == len(self.the_text[self.key]):
                            return True
                        self.check_mcq_type()

                    else:
                        self.full_line_shown = True

                if self.in_multi_choice:
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        self.master.sounds["UI_Hover"].play()
                        self.multi_c_index -= 1
                        if self.multi_c_index < 0:
                            self.multi_c_index = len(self.the_text[self.key][self.page_index])-1
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.master.sounds["UI_Hover"].play()
                        self.multi_c_index += 1
                        if self.multi_c_index >= len(self.the_text[self.key][self.page_index]):
                            self.multi_c_index = 0

        if self.letter_increment_timer.check() and not self.full_line_shown and not self.in_multi_choice:
            self.letter_index += 1
            self.master.sounds["SFX_Text"].play()
            if self.letter_index == len(self.the_text[self.key][self.page_index]):
                self.letter_index = 0
                self.full_line_shown = True

    def check_mcq_type(self):

        try:
            text = self.the_text[self.key][self.page_index]
        except Exception:
            return True
        if isinstance(text, Check):
            self.key = self.obj.interaction_logic_check(self.obj_key, self.key, text)
            self.page_index = 0
            if self.page_index == len(self.the_text[self.key]):
                return True
        elif isinstance(text, Choice):
            self.in_multi_choice = True
            self.multi_c_index = 0

