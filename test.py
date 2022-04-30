import pygame

#Initialise pygame

pygame.init()

#Create the screen

screen = pygame.display.set_mode((1200, 700))
screen.set_alpha(None)

#Change the title and the icon

pygame.display.set_caption('The Thoughtful Minds')


#Dots
dot = pygame.Surface((10, 10))
dot.fill((255, 0, 0))

class Dot:
    def __init__(self, pos):
        self.cx, self.cy = pos

    def draw(self):
        screen.blit(dot,(self.cx-8 , self.cy-8))

def text_objects(text,font):
    textSurface = font.render(text, True, (100,100,100))
    return textSurface, textSurface.get_rect()

dots = []
#Running the window
i = 0
running = True
draging = False
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for oPosition in dots:
                if ((oPosition.cx - 8) < mx < (oPosition.cx + 8)) and ((oPosition.cy - 8) < my < (oPosition.cy + 8)):
                    draging = True
                    break

            if i<3:
                # append a new dot at the current mouse position
                dots.append(Dot((mx,my)))
                i += 1
        elif event.type == pygame.MOUSEBUTTONUP:
            draging = False

        elif event.type == pygame.MOUSEMOTION:
            if draging :
                oPosition.cx = mx
                oPosition.cy = my

    # clear the display
    screen.fill((30,30,30))

    # draw all the dots

    if len(dots)>1:
        for i in range(len(dots)-1):
            pygame.draw.line(screen, (50, 50, 50), [dots[i].cx,dots[i].cy],[dots[i+1].cx,dots[i+1].cy],2 )

    for d in dots:
        d.draw()

    if mx < 50 and my < 50:
        pygame.draw.rect(screen,(24,24,24),(0,0,50,50))
    else:
        pygame.draw.rect(screen,(20,20,20),(0,0,50,50))

    text = pygame.font.Font("freesansbold.ttf",25)
    textSurf, textRect = text_objects('–', text)
    textRect.center = (25,25)
    screen.blit( textSurf, textRect )

    if 52 < mx < 102 and my < 50:
        pygame.draw.rect(screen,(24,24,24),(52,0,50,50))
    else:
        pygame.draw.rect(screen,(20,20,20),(52,0,50,50))

    textSurf, textRect = text_objects('+', text)
    textRect.center = (76,25)
    screen.blit( textSurf, textRect )

    # update the dispalay
    pygame.display.flip()