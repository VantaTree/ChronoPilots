import pygame
from modules import *
import asyncio

class Master:

    def __init__(self):

        self.app:App
        # self.debug:Debug
        self.dt:float
        self.offset:pygame.Vector2

        self.font_d = pygame.font.Font("fonts/PixelOperator.ttf", 11)
        self.font_1 = pygame.font.Font("fonts/PixelOperator.ttf", 14)
        self.font = pygame.font.Font("fonts/PixelOperator-Bold.ttf", 18)
        self.font_big = pygame.font.Font("fonts/PixelOperator.ttf", 32)

    
class App:

    MAIN_MENU = 0
    IN_GAME = 1

    TRANSITION = 2

    INTRO_CUTSCENE = 4
    P1_TO_P2_CUTSCENE = 5
    P2_TO_P3_CUTSCENE = 6
    P3_TO_P4_CUTSCENE = 7
    WON_CUTSCENE = 8
    LOST_CUTSCENE = 9
    GAME_FINISH = 10

    def __init__(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode((W, H), pygame.SCALED)
        pygame.display.set_caption("Chrono Pilots")
        # icon = pygame.image.load("graphics/icon.png").convert()
        # pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()

        self.state = self.MAIN_MENU

        self.master = Master()
        SoundSet(self.master)
        self.master.app = self
        self.debug = Debug(self.screen, font=self.master.font_d, offset=4)
        self.master.debug = self.debug
        self.game = Game(self.master)
        self.main_menu = MainMenu(self.master)
        self.cutscene = FiFo(self.master, "intro")
        Music(self.master)
        Ambience(self.master)

    async def run(self):
        
        while True:

            pygame.display.update()

            self.master.dt = self.clock.tick(FPS) / 16.667
            if self.master.dt > 10: self.master.dt = 10
            self.debug("FPS:", round(self.clock.get_fps(), 2))
            self.debug("Offset:", (round(self.master.offset.x, 2), round(self.master.offset.y, 2)))
            self.debug("Music:", self.master.music.current_track)
            self.debug("Ambie:", self.master.ambience.current_track)

            for event in pygame.event.get((pygame.QUIT)):
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            await asyncio.sleep(0)

            self.master.music.run()
            self.master.ambience.run()
            self.run_states()
            self.debug.draw()

    def run_states(self):

        if self.state == self.INTRO_CUTSCENE:
            if self.cutscene.run():
                self.state = self.IN_GAME
        elif self.state == self.P1_TO_P2_CUTSCENE:
            if self.cutscene.run():
                self.state = self.IN_GAME
                self.game.change_pilot(2)
        elif self.state == self.P2_TO_P3_CUTSCENE:
            if self.cutscene.run():
                self.state = self.IN_GAME
                self.game.change_pilot(3)
        elif self.state == self.P3_TO_P4_CUTSCENE:
            if self.cutscene.run():
                self.state = self.IN_GAME
                self.cutscene = None
                self.game.change_pilot(4)
        elif self.state == self.WON_CUTSCENE:
            if self.cutscene.run():
                self.state = self.GAME_FINISH
        elif self.state == self.LOST_CUTSCENE:
            if self.cutscene.run():
                self.state = self.GAME_FINISH
        elif self.state == self.GAME_FINISH:

            self.screen.fill(0x0)

            text = self.master.font_big.render("Thanks For Playing!", False, "white")
            rect = text.get_rect(center=(W/2, H/2))
            self.screen.blit(text, rect)

            text = self.master.font_1.render("Reload Game To Replay", False, "white")
            rect = text.get_rect(midbottom=(W/2, H-10))
            self.screen.blit(text, rect)

        elif self.state == self.TRANSITION:
            if self.cutscene.run():
                self.state = self.IN_GAME
                self.cutscene = None
        elif self.state == self.MAIN_MENU:
            self.main_menu.run()
            pass
        elif self.state == self.IN_GAME:
            self.game.run()

if __name__ == "__main__":

    app = App()
    # app.run()
    asyncio.run(app.run())
