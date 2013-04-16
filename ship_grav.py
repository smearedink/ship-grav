import sys, pygame
import numpy as np
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

ballsound = pygame.mixer.Sound("ping.wav")
wallsound = pygame.mixer.Sound("ping.wav")
#shipsound = pygame.mixer.Sound("spaceship.aiff")

width, height = 1024, 768
size = np.array([width, height])
centre = size/2

white = 255, 255, 255
black = 0, 0, 0

dt = 1.

class Attractor:
    def __init__(self, surface, pos=(0,0), strength=1, radius=10, col=white, inverted=False):
        self.surface = surface
        self.pos = np.array(pos, dtype=float)
        self.strength = float(strength)
        self.radius = radius
        self.col = col
        self.inverted = inverted
        self.mysurf = pygame.Surface((2*self.radius, 2*self.radius))
        self.mysurf.set_colorkey(black)
        self.myrect = pygame.draw.circle(self.mysurf, col,\
            (self.radius, self.radius), self.radius)

    def draw(self, origin=centre):
        topleft_pixel = np.round(self.pos - self.radius - origin + centre)
        self.myrect.left = topleft_pixel[0]
        self.myrect.top = topleft_pixel[1]
        self.surface.blit(self.mysurf, self.myrect)

    def invert(self):
        self.inverted = not self.inverted

class Ship:
    def __init__(self, surface, pos=(0,0), vel=(0,0), col=white):
        self.surface = surface
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.col = col
        self.acc = np.array([0.,0.])
        self.radius = 3
        self.mysurf = pygame.Surface((2*self.radius, 2*self.radius))
        self.mysurf.set_colorkey(black)
        self.myrect = pygame.draw.circle(self.mysurf, col,\
            (self.radius, self.radius), self.radius)

    def update(self, collision_checklist=[]):
        """
        collision_checklist is a list of Attractor objects that you'd like
        to account for collision-wise.  When it doubt, throw it on the list!

        For the moment, this can in principle allow a fast-moving ship to
        pass through an object.
        """
        self.vel += self.acc*dt
        new_pos = self.pos + self.vel*dt
        if new_pos[0] - self.radius < 0:
            #print "you've gone off the left"
            self.vel[0] *= -1
            wallsound.play()
        elif new_pos[0] + self.radius > width:
            #print "you've gone off the right"
            self.vel[0] *= -1
            wallsound.play()
        if new_pos[1] - self.radius < 0:
            #print "you've gone off the top"
            self.vel[1] *= -1
            wallsound.play()
        elif new_pos[1] + self.radius > height:
            #print "you've gone off the bottom"
            self.vel[1] *= -1
            wallsound.play()
        if collision_checklist:
            for attractor in collision_checklist:
                dist = np.sqrt(np.sum((attractor.pos - new_pos)**2))
                min_dist = attractor.radius + self.radius
                if dist < min_dist:
                    pos_update = self.vel*dt
                    # time for some trig
                    a = np.sqrt(np.sum(pos_update**2))
                    b = np.sqrt(np.sum((attractor.pos - self.pos)**2))
                    c = dist
                    R = attractor.radius + self.radius
                    BB = a + (b*b-c*c)/a
                    in_sqrt = BB*BB-4.*(b*b-R*R)
                    if in_sqrt > 0:
                        aa = 0.5*(BB - np.sqrt(BB*BB-4.*(b*b-R*R)))
                    else:
                        aa = 0.5*BB
                        print "hmmmm"
                    dist_factor = (aa-self.radius)/a
                    new_pos = self.pos + dist_factor*self.vel*dt
                    self.resetAcc()
                    self.addAccDueTo(attractor)
                    self.vel += self.acc*dt*dist_factor
                    # need to figure out what to _actually_ do with vel
                    dx = new_pos[0] - attractor.pos[0]
                    dy = new_pos[1] - attractor.pos[1]
                    fac = R/np.sqrt(dx*dx+dy*dy)
                    dx *= fac
                    dy *= fac
                    cos_rot = abs(dy/R)
                    sin_rot = np.sin(np.arccos(cos_rot))
                    sgn = -np.sign(dx*dy)
                    rot_vx = self.vel[0]*cos_rot + sgn*self.vel[1]*sin_rot
                    rot_vy = -sgn*self.vel[0]*sin_rot + self.vel[1]*cos_rot
                    rot_vy *= -1.
                    self.vel[0] = rot_vx*cos_rot - sgn*rot_vy*sin_rot
                    self.vel[1] = sgn*rot_vx*sin_rot + rot_vy*cos_rot
                    ballsound.play()
                    break
        self.pos = new_pos

    def draw(self, origin=centre):
        topleft_pixel = np.round(self.pos - self.radius - origin + centre)
        self.myrect.left = topleft_pixel[0]
        self.myrect.top = topleft_pixel[1]
        self.surface.blit(self.mysurf, self.myrect)

    def addVel(self, vel_x, vel_y):
        self.vel += np.array([vel_x, vel_y])

    def addAcc(self, acc_x, acc_y):
        self.acc += np.array([acc_x, acc_y])

    def addAccDueTo(self, attractor):
        if attractor.inverted: rhat = 1
        else: rhat = -1
        r = attractor.pos - self.pos
        r_signs = np.sign(r)
        r_sq = np.sum(r*r)
        total_acc = 100.*attractor.strength/r_sq
        if r[0] != 0:
            acc_x = -rhat*r_signs[0]*total_acc/np.sqrt((r[1]/r[0])**2 + 1.)
        else: acc_x = 0.
        if r[1] != 0:
            acc_y = -rhat*r_signs[1]*total_acc/np.sqrt((r[0]/r[1])**2 + 1.)
        else: acc_y = 0.
        self.addAcc(acc_x, acc_y)

    def resetAcc(self):
        self.acc = np.array([0., 0.])

screen = pygame.display.set_mode(size)
background = pygame.Surface(size)
background.fill(black)

screen.blit(background, (0,0))

ship = Ship(screen, centre - height/4, (0.,1.5), white)
ship.draw()
att1 = Attractor(screen, centre, strength=20, radius=40, col=white)
att1.draw()
att2 = Attractor(screen, centre+100, strength=15, radius=30, col=white, inverted=True)
att2.draw()
att3 = Attractor(screen, centre+np.array([200, -250]), strength=15, radius=30, col=white, inverted=True)
att3.draw()

atts = [att1, att2, att3]

trails = False
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                pygame.quit()
                sys.exit()
            elif (event.key == pygame.K_t):
                trails = not trails
            elif (event.key == pygame.K_i):
                for att in atts:
                    att.invert()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]\
        or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
        if keys[pygame.K_LEFT]:
            ship.addVel(-0.1, 0.)
        if keys[pygame.K_RIGHT]:
            ship.addVel(0.1, 0.)
        if keys[pygame.K_UP]:
            ship.addVel(0., -0.1)
        if keys[pygame.K_DOWN]:
            ship.addVel(0., 0.1)
        #if shipsound.get_num_channels() == 0:
        #    shipsound.play(-1)
    #elif shipsound.get_num_channels() > 0:
    #else:
    #    shipsound.stop()

    ship.resetAcc()
    for att in atts:
        ship.addAccDueTo(att)
    ship.update(atts)
    if not trails:
        screen.blit(background, (0,0))
        att1.draw()
        att2.draw()
        att3.draw()
    ship.draw()
    pygame.display.flip()
