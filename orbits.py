import sys, pygame
import numpy as np
pygame.init()

width, height = 1024, 768
size = np.array([width, height])
centre = size/2

black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
yellow = 255, 255, 0
orange = 255, 128, 0
cyan = 0, 255, 255
purple = 255, 0, 255

G = 39.4812495 # AU^3 / Msun / yr^2
dt = 0.001 # yr
resolution = 150 # pixels / AU
# speed should be an integer: it tells the program how many loops to go
# through before each screen update (so 1 is the slowest)
speed = 1

class Planet:
    """
    radius in AU
    mass in solar masses
    velocity in AU/yr
    """
    def __init__(self, surface, radius, mass, pos=(0,0), vel=(0,0), col=(255,255,255)):
        self.surface = surface
        self.radius = float(radius)
        self.mass = float(mass)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.col = col

        self.acc = np.array([0.,0.])
        
        self.mysurf = pygame.Surface((radius*2,radius*2))
        self.mysurf.set_colorkey(black)
        self.myrect = pygame.draw.circle(self.mysurf, col,\
            (radius, radius), radius)

#    def move(self, x, y):
#        self.myrect = self.myrect.move([x,y])

    def update(self):
        self.vel += self.acc*dt
        #self.pos += self.vel*dt*resolution + 0.5*self.acc*dt*dt*resolution
        self.pos += self.vel*dt*resolution
        #self.vel += self.acc*dt

    def draw(self, origin=centre):
        topleft_pixel = np.round(self.pos - self.radius - origin + centre)
        self.myrect.left = topleft_pixel[0]
        self.myrect.top = topleft_pixel[1]
        self.surface.blit(self.mysurf, self.myrect)

    def addAccDueTo(self, otherPlanet):
        r = (otherPlanet.pos - self.pos)/resolution
        r_signs = np.sign(r)
        r_sq = np.sum(r*r)
        total_acc = G*otherPlanet.mass/r_sq
        if r[0] != 0:
            acc_x = r_signs[0]*total_acc/np.sqrt((r[1]/r[0])**2 + 1.)
        else: acc_x = 0.
        if r[1] != 0:
            acc_y = r_signs[1]*total_acc/np.sqrt((r[0]/r[1])**2 + 1.)
        else: acc_y = 0.
        self.acc += np.array([acc_x, acc_y])

    def resetAcc(self):
        self.acc = np.array([0., 0.])

def gameprint(surface, text, xx, yy, col=white, size=18):
    font = pygame.font.Font(None, size)
    ren = font.render(text, 1, col)
    surface.blit(ren, (xx, yy))


screen = pygame.display.set_mode(size)

#earth = Planet(screen, 5, 0.01, (centre[0], centre[1]-180), (-0.5,0))
#venus = Planet(screen, 15, 10, centre, (0.,0.))
#moon = Planet(screen, 2, 0.0001, [centre[0], centre[1]-192], (-0.54,0))

sun = Planet(screen, 5, 1., centre, (0.,0.), yellow)
mercury = Planet(screen, 2, 1.65956463e-7, [centre[0]+0.387098*resolution,\
    centre[1]], [0, -10.098], purple)
venus = Planet(screen, 2, 2.44699613e-6, [centre[0],\
    centre[1]+0.723327*resolution], [7.387, 0], green)
earth = Planet(screen, 2, 3.0024584e-6, [centre[0],\
    centre[1]-1.*resolution], [-6.282, 0], cyan)
mars = Planet(screen, 2, 3.22604696e-7, [centre[0]-1.523679*resolution,\
    centre[1]], [0, 5.079], red)
#jupiter = Planet(screen, 2, 9.54265748e-4, [centre[0]+5.204267*resolution,\
#    centre[1]], [0, -2.757], orange)

nemesis = Planet(screen, 5, 1., [0,0], [7., 2.5])

bodies = [sun, mercury, venus, earth, mars]


background = pygame.Surface(size)
background.fill(black)
text_gr = 150
gameprint(background, "+/-: speed", 10, 10, [text_gr]*3, 20)
gameprint(background, "</>: Sun mass", 10, 25, [text_gr]*3, 20)
gameprint(background, "left/right: centre body", 10, 40, [text_gr]*3, 20)
gameprint(background, "B: barycentre", 10, 55, [text_gr]*3, 20)
gameprint(background, "T: trails", 10, 70, [text_gr]*3, 20)
gameprint(background, "esc or Q: quit", 10, 85, [text_gr]*3, 20)
gameprint(background, "N: nemesis!", 10, 100, [text_gr]*3, 20)

counter = 0
origin_body = 0
barycentre = True
trails = False
nemesis_on = False
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_RIGHT:
                screen.blit(background, (0,0))
                barycentre = False
                origin_body = (origin_body+1) % len(bodies)
            elif event.key == pygame.K_LEFT:
                screen.blit(background, (0,0))
                barycentre = False
                origin_body = (origin_body-1) % len(bodies)
            elif event.key == pygame.K_b:
                screen.blit(background, (0,0))
                barycentre = True
            elif event.key == pygame.K_MINUS:
                if speed > 0: speed -= 1
            elif event.key == pygame.K_EQUALS:
                if speed < 20: speed += 1
            elif event.key == pygame.K_t:
                if trails: trails = False
                else: trails = True
            elif event.key == pygame.K_PERIOD:
                sun.mass += 0.2
            elif event.key == pygame.K_COMMA:
                sun.mass -= 0.2
            elif event.key == pygame.K_n:
                if not nemesis_on:
                    bodies.append(nemesis)
                    nemesis_on = True
                    barycentre = False

    if speed:
        for ii in range(len(bodies)):
            bodies[ii].resetAcc()
            for jj in range(len(bodies)):
                if jj != ii:
                    bodies[ii].addAccDueTo(bodies[jj])
        for body in bodies:
            body.update()
        
        counter += 1
        if counter % speed == 0:
            #if not trails: screen.fill(black)
            if not trails: screen.blit(background, (0,0))
            if barycentre:
                origin = np.array([0.,0.])
                total_mass = 0.
                for body in bodies:
                    total_mass += body.mass
                    origin += body.pos*body.mass
                origin /= total_mass
                for body in bodies:
                    body.draw(origin)
            else:
                for body in bodies:
                    body.draw(bodies[origin_body].pos)
            
            pygame.display.flip()
