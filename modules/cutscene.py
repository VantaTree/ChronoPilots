import pygame
from .engine import *
from .config import *

CUTSCENE_TEXT = {
    "intro":[
        "Mayday mayday, TEXT LOG #72",
        "The Spaceship is critically damaged, do you hear me?",
        "I am on a direct collision course to Alien Planet 4-5-4-6-P",
        ".......................................................................................................................................................................",
        "Send Help please, I have a family, It... It must not end like this I beg you. Save me of O god of the cosmos.",
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH",
        "F***",
        "Booom Crash Hit Brrrrrrrrrrrr THUD BssSsSsSsSsSsSSSsSssSsSsss..."
    ],
    "p1-2":[
        "TEXT LOG #37",
        "13-6-3069. Exactly 4 years and 2 days ago, this planet was first discovered. It was a complete accident, some idiot managed to crash into the planet.",
        "4-5-4-6-P       END LOG.",
        "Mission Briefing",
        "13-6-3069\nCaptian Less Idiot, After a few years of careful observations we have concluded that planet 4-5-4-6-P is valuable enough. Your job is to scout the area and collect a few key resources, some minerals and some bio matter. We have given you a gun to defend yourself in case of any hostilities, which I doubt there are. Good Luck out there. END.",
        "I am gonna be a Pilot I always dreamed of, onwards and beyond."
    ],
    "p2-3":[
        "17-3-4209",
        "This is no ordinary day. It's the day where everything began, the monster it will consume us all",
        "Mission Briefing",
        "3-9-4200\nCaption Snaily Roach, It is finally time to retrieve that inconceivable resource from planet 4-5-4-6-P. It has been long enough. Your job is to get to the grudges of the deepest part, find the final resource and bring it back safely.",
        "We have equipped your spaceship with advanced fabrication capabilites, espessially with the capability to craft the red magic itself. Good Luck, Be on your way.",
        "And if you precede the result will be gruesome. END.",
        "...",
        "I Caption Snaily Roach have been waiting for this moment for my entire life. Mama kaka I will make you proud. and especially  you Sergant Frog.",
        "It's Wednesday my Dudes."
    ],
    "p3-4":[
        "TEXT LOG #98214",
        "Get the **** over with this, we have had so many failure in the past decade it's such an embarrassment, why can't you guys just get that stupid ****ing peice of shit. ****ing dumbasses.",
        "Mission Briefing",
        "17-3-4209\n Captian kisnip, This is our last hope, we have got nothing, you will have to do with this outdated spaceship, it has everything the first one did. You job is well get that damn thing, you know it everyone knows it.",
        "If we fail this time it's done, humanity will be over that instant.\nWe are counting on you.",
        "Now get out there get the final resource. END.",
        "...It's.Now.Or.Never...",
        "I... I have ne..ver ever been this scared in my entrire life, including if all those red dreams were actually true.",
        "O god of the cosmos save me, do something"
    ],
    "end won":[
        "...",
        "All hail the Entity."
    ],
    "end lost":[
        "DOOMED",
        "...DOOMED...",
        "......DOOMED......",
        "............DOOMED............\n............DOOMED............\n............DOOMED............",
        "............DOOMED............\n............DOOMED............\n............DOOMED............\n............DOOMED............\n............DOOMED............\n............DOOMED............",
        "DOOMED FOREVER"
    ],
    "transition":[],
    "mission_completed":[
        "Mission Completed"
    ],
    "you_died":[
        "You Died!"
    ],
}


class FiFo:
    "fade-in fade-out cutscene"

    def __init__(self, master, type, continue_text=True, text_color=0xFFFFFFFF) -> None:

        self.master = master
        self.screen = pygame.display.get_surface()

        self.black_bg = pygame.Surface(self.screen.get_size())
        self.black_bg.set_alpha(0)

        self.text_color = text_color

        self.type = type
        self.texts = CUTSCENE_TEXT[type]
        self.page_index = 0
        self.alpha = 0
        self.halt = False
        self.skip = False

        self.increment = 1
        self.alpha_speed = 8

        self.letter_index = 0
        self.full_text_shown = False

        self.continue_text = continue_text

        if self.type != "transition":
            if self.continue_text:
                self.bottom_text = self.master.font_1.render("Press E to Continue", False, (255, 255, 255))
                self.bottom_text_rect = self.bottom_text.get_rect(topleft=(5, 5))

            self.letter_increment_timer = CustomTimer(True)
            self.letter_increment_timer.start(40, 0)

    def check_events(self):

        for event in pygame.event.get(pygame.KEYDOWN):
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_e and self.halt:
                    self.master.sounds["UI_Hover"].play()
                    if not self.full_text_shown:
                        self.full_text_shown = True
                    else:
                        self.increment = -1
                        self.halt = False
                        self.full_text_shown = False
                        self.letter_index = 0
                if event.key == pygame.K_ESCAPE:
                    self.skip = True
                    return
                
    def draw(self):
        
        self.screen.fill((180, 0, 0))
        self.screen.blit(self.black_bg, (0, 0))
        if self.increment == 0 and self.type != "transition":
            if self.continue_text:
                self.screen.blit(self.bottom_text, self.bottom_text_rect)

            if self.full_text_shown:
                text = self.texts[self.page_index]
            else:
                text = self.texts[self.page_index][:self.letter_index]
            text_surf = self.master.font.render(text, False, self.text_color, wraplength=int(W/3*2))
            rect = text_surf.get_rect(center=(W/2, H/2))
            self.screen.blit(text_surf, rect)

    def update(self):

        if self.type != "transition" and self.letter_increment_timer.check() and self.halt and not self.full_text_shown:
            self.letter_index += 1
            self.master.sounds["SFX_Text"].play()
            if self.letter_index == len(self.texts[self.page_index]):
                self.full_text_shown = True

        else:
            self.black_bg.set_alpha(int(self.alpha))
            self.alpha += self.alpha_speed*self.increment *self.master.dt
            if self.alpha >= 256:
                self.increment = 0
                self.alpha = 255
                if self.type == "transition":
                    self.increment = -1
                else:
                    self.halt = True
            elif self.alpha < 0:
                if self.type == "transition":
                    return True
                self.alpha = 0
                self.increment = 1
                self.page_index += 1
                if self.page_index == len(self.texts):
                    return True

    def run(self):

        self.check_events()
        if self.skip: return True
        result = self.update()
        self.draw()
        if result:
            self.master.sounds["SFX_Spawn"].play()
        return result
    