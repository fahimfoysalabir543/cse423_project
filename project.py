from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random
import math

# Camera variables
cam_dis = 500
cam_angle = -90
cam_height = 900
first_person = False

# Player/Gun variables
player_angle = -90
player_x = 0
player_y = 0
gun_angle = 0
player_speed = 15
rotation_speed = 10
fovY = 500
grid_len = 1200
totalmeat= 0
totalwood=0
totalnarco=0
riding= False
riding1=False
riding2=False


# Game state
life = 20
score = 0
miss = 0
gameover = False
water= False
trap1= False
kill=False
knock=False
axe=True
axe_swinging= False
axe_swing_angle=0
axe_swing_speed=4
axe_max_swing=-120
obstacle=[]

# Obstacles state
obstacles_built = False

def ensure_obstacles_static():
    """Populate obstacle list with known static geometry if empty.
    Prevents movement-through-objects even if draw order hasn't run yet.
    """
    global obstacle
    if obstacle:
        return
    # Trees
    obstacle.extend([
        (-500, 200, 50),
        (-900, 700, 30),
        (900, -900, 50),
        (-1000, -1000, 30),
        (1000, 900, 30),
    ])
    # Mountains
    obstacle.extend([
        (900, 100, 200),
        (900, 0, 150),
    ])
    # Static narco
    obstacle.append((900, -400, 120))

def will_collide_with_obstacles(nx, ny, obj_radius):
    """Return True if the circle at (nx, ny) with radius obj_radius intersects any obstacle."""
    ensure_obstacles_static()
    for ox, oy, orad in obstacle:
        dx = nx - ox
        dy = ny - oy
        if math.hypot(dx, dy) < (obj_radius + orad):
            return True
    return False

def resolve_position_against_obstacles(x, y, obj_radius):
    """Push the circle (x, y, r) out of intersecting obstacles by minimum distance.
    Keeps gameplay logic intact while preventing tunneling through static geometry.
    """
    ensure_obstacles_static()
    for ox, oy, orad in obstacle:
        dx = x - ox
        dy = y - oy
        d = math.hypot(dx, dy)
        min_d = obj_radius + orad
        if d == 0:
            # Rare: exactly centered. Nudge out along X.
            x += min_d + 0.01
            continue
        if d < min_d:
            # Push out along the normal by the overlap
            push = (min_d - d) + 0.01
            x += dx / d * push
            y += dy / d * push
    return x, y

# Cheat features
cheat = False

autocamgun = False

unconsc_count=4
consc_count=0

# Enemy positions
enemy_positions = []
enemy_positions2 = []

# Bullets
bullets = []
bullspeed = 5
bullmaxlife = 200
bullsize = 10

# Enemy / collision sizes
enemy_rad = 50

player_rad = 40

# Enemy movement
enemy_speed = .3

# For pulsation
frame_count = 0

# Cheat behavior parameters
cheat_rotspeed = 1
cheat_firecooldown = 18
cheat_firetimer = 0
cheat_aimangle = 12
cheat_maxdist = 1200

#trap
trap1={
    'trapset':False,
    'trapact':False,
    'trapx':0,
    'trapy':0
}


trap2={
    'trapset':False,
    'trapact':False,
    'trapx':0,
    'trapy':0
}


narcopos=[]
for i in range(50):
        x=random.randint(800,980)
        y=random.randint(-500,-300)
        narcopos.append((x,y))


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1600, 0, 1000)  # left, right, bottom, top

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_texts():
    global life, score, miss, gameover, cheat, autocamgun
    if gameover:
        draw_text(20, 700, f"Game is Over. Your Score is {score}.")
        draw_text(20, 730, "Press R to RESTART the Game.")
    else:
        draw_text(10, 640, f"Player Life Remaining: {life}")
        draw_text(10, 620, f"Game Score: {score}")
        draw_text(10, 600, f"Player Bullets Missed: {miss}")


def draw_grids_and_walls():
    # Draw the grid
    # Reset obstacles each frame so they don't accumulate
    global obstacle
    obstacle.clear()


    glColor3f(0.98, 0.92, 0.67)


    glBegin(GL_QUADS)
    glVertex3f(-grid_len, -grid_len, 0)
    glVertex3f(-grid_len, grid_len, 0)
    glVertex3f(grid_len, grid_len, 0)
    glVertex3f(grid_len, -grid_len, 0)
    glEnd()


    glColor3f(0, .6, 1)
    glBegin(GL_QUADS)
    glVertex3f(-grid_len, -850, 1)
    glVertex3f(-grid_len, -650, 1)
    glVertex3f(0, -650, 1)
    glVertex3f(0, -850, 1)
    glEnd()

    glColor3f(0, .6, 1)
    glBegin(GL_QUADS)
    glVertex3f(0, -1100, 1)
    glVertex3f(0, -650, 1)
    glVertex3f(300, -650, 1)
    glVertex3f(300, -1100, 1)
    glEnd()

    m = grid_len

    # Left wall
    glColor3f(0, .6, 1)
    glBegin(GL_QUADS)
    glVertex3f(-m, -m, 0)
    glVertex3f(-m, m, 0)
    glVertex3f(-m-2000, m+2000, -300)
    glVertex3f(-m-2000, -m-2000, -300)

    glEnd()

    # Right wall
    glColor3f(0, .6, 1)
    glBegin(GL_QUADS)
    glVertex3f(m, -m, 0)
    glVertex3f(m, m, 0)
    glVertex3f(m+2000, m+2000, -300)
    glVertex3f(m+2000, -m-2000,-300)
    glEnd()

    # Bottom wall
    glColor3f(0, .6, 1)
    glBegin(GL_QUADS)
    glVertex3f(-m, -m, 0)
    glVertex3f(m, -m, 0)
    glVertex3f(m+2000, -m-2000, -300)
    glVertex3f(-m-2000, -m-2000, -300)
    glEnd()

    # Top wall
    glColor3f(0, .6, 1)
    glBegin(GL_QUADS)
    glVertex3f(-m, m, 0)
    glVertex3f(m, m, 0)
    glVertex3f(m+2000, m+2000, -300)
    glVertex3f(-m-2000, m+2000, -300)
    glEnd()

    #tree1
    glPushMatrix()
    glColor3f(0, 1, 0)
    glTranslatef(-500,200, 300)
    gluSphere(gluNewQuadric(), 120, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(.8, .3, 0)
    glTranslatef(-500, 200, 0)
    gluCylinder(gluNewQuadric(), 50, 10, 300, 10, 10)
    glPopMatrix()
    obstacle.append((-500,200,50))


    #tree2
    glPushMatrix()
    glColor3f(0, 1, 0)
    glTranslatef(-900,700, 300)
    gluSphere(gluNewQuadric(), 100, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(.8, .3, 0)
    glTranslatef(-900, 700, 0)
    gluCylinder(gluNewQuadric(), 30, 10, 300, 10, 10)
    glPopMatrix()
    obstacle.append((-900,700,30))

    #tree3
    glPushMatrix()
    glColor3f(0, 1, 0)
    glTranslatef(900,-900, 300)
    gluSphere(gluNewQuadric(), 90, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(.8, .3, 0)
    glTranslatef(900, -900, 0)
    gluCylinder(gluNewQuadric(), 50, 10, 300, 10, 10)
    glPopMatrix()
    obstacle.append((900,-900,50))

    #tree4
    glPushMatrix()
    glColor3f(0, 1, 0)
    glTranslatef(-1000,-1000, 300)
    gluSphere(gluNewQuadric(), 100, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(.8, .3, 0)
    glTranslatef(-1000, -1000, 0)
    gluCylinder(gluNewQuadric(), 30, 10, 300, 10, 10)
    glPopMatrix()
    obstacle.append((-1000,-1000,30))

    #tree5
    glPushMatrix()
    glColor3f(0, 1, 0)
    glTranslatef(1000,900, 300)
    gluSphere(gluNewQuadric(), 100, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(.8, .3, 0)
    glTranslatef(1000, 900, 0)
    gluCylinder(gluNewQuadric(), 30, 10, 300, 10, 10)
    glPopMatrix()
    obstacle.append((1000,900,30))


    #mountains

    glPushMatrix()
    glColor3f(0.694, 0.671, 0.604)
    glTranslatef(900, 100, 0)
    gluCylinder(gluNewQuadric(), 200, 30, 500, 10, 10)
    glPopMatrix()

    obstacle.append((900,100,200))

    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(900, 100, 470)
    gluSphere(gluNewQuadric(), 30, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.694, 0.671, 0.604)
    glTranslatef(900, 0, 0)
    gluCylinder(gluNewQuadric(), 150, 30, 400, 10, 10)
    glPopMatrix()
    obstacle.append((900,0,150))

    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(900, 0, 370)
    gluSphere(gluNewQuadric(), 30, 20, 20)
    glPopMatrix()

    #sky
    glPushMatrix()
    glColor3f(0, .8, 1)
    glTranslatef(0,0, 50)
    gluSphere(gluNewQuadric(), 2500, 20, 20)
    glPopMatrix()



    #Narco
    glPushMatrix()
    glColor3f(0, 1, 0)
    glTranslatef(900,-400, -50)
    gluSphere(gluNewQuadric(), 120, 20, 20)
    glPopMatrix()
    obstacle.append((900,-400,120))

    for i in narcopos:
        x=i[0]
        y=i[1]
        disx= 900-x
        disy=-400-y
        dis=math.hypot(disx, disy)

        glPushMatrix()
        glColor3f(.5, 0, .5)
        if dis<25:
            glTranslatef(0,0, 25)

        if dis<20:
            glTranslatef(0,0, 5)


        if dis>30:
            glTranslatef(0,0, -10)

        if dis>35:
            glTranslatef(0,0, -10)

        if dis>45:
            glTranslatef(0,0, -10)


        glTranslatef(x,y, 80)
        gluSphere(gluNewQuadric(), 7, 20, 20)
        glPopMatrix()

    if trap1['trapset']:
        glColor3f(.8, .3, 0)
        glBegin(GL_QUADS)
        glVertex3f(trap1['trapx']-100, trap1['trapy']+100, 0)
        glVertex3f(trap1['trapx']-100, trap1['trapy']+100, 100)
        glVertex3f(trap1['trapx']+100, trap1['trapy']+100, 100)
        glVertex3f(trap1['trapx']+100,trap1['trapy']+100, 0)
        glEnd()

        glBegin(GL_QUADS)
        glVertex3f(trap1['trapx']-100, trap1['trapy']+100, 170)
        glVertex3f(trap1['trapx']-100, trap1['trapy']+100, 200)
        glVertex3f(trap1['trapx']+100, trap1['trapy']+100, 200)
        glVertex3f(trap1['trapx']+100,trap1['trapy']+100, 170)
        glEnd()

        glColor3f(.8, .3, 0)
        glBegin(GL_QUADS)
        glVertex3f(trap1['trapx']-100, trap1['trapy']+300, 0)
        glVertex3f(trap1['trapx']-100, trap1['trapy']+300, 200)
        glVertex3f(trap1['trapx']-100, trap1['trapy']+100, 200)
        glVertex3f(trap1['trapx']-100,trap1['trapy']+100, 0)
        glEnd()

        if not trap1['trapact']:
            glColor3f(.8, .3, 0)
            glBegin(GL_QUADS)
            glVertex3f(trap1['trapx']+100, trap1['trapy']+300, 195)
            glVertex3f(trap1['trapx']+100, trap1['trapy']+300, 400)
            glVertex3f(trap1['trapx']-100, trap1['trapy']+300, 400)
            glVertex3f(trap1['trapx']-100,trap1['trapy']+300, 195)
            glEnd()

        else:

            glColor3f(.8, .3, 0)
            glBegin(GL_QUADS)
            glVertex3f(trap1['trapx']+100, trap1['trapy']+300, 0)
            glVertex3f(trap1['trapx']+100, trap1['trapy']+300, 200)
            glVertex3f(trap1['trapx']-100, trap1['trapy']+300, 200)
            glVertex3f(trap1['trapx']-100,trap1['trapy']+300, 0)
            glEnd()

        glColor3f(.8, .3, 0)
        glBegin(GL_QUADS)
        glVertex3f(trap1['trapx']+100, trap1['trapy']+100, 0)
        glVertex3f(trap1['trapx']+100, trap1['trapy']+100, 200)
        glVertex3f(trap1['trapx']+100, trap1['trapy']+300, 200)
        glVertex3f(trap1['trapx']+100,trap1['trapy']+300, 0)
        glEnd()


def draw_player():
    global axe_x, axe_y
    # Prevent player overlapping with obstacles before rendering
    global player_x, player_y
    player_x, player_y = resolve_position_against_obstacles(player_x, player_y, player_rad)
    glPushMatrix()
    glTranslatef(player_x, player_y, 0)
    if riding1:
        glTranslatef(0, 0, 25)

    elif riding2:
        glTranslatef(0, 0, 100)

    if riding2 and (player_x>grid_len+40 or player_x<-grid_len-40 or player_y>grid_len+50 or player_y<-grid_len-40) or (player_x>-1200 and player_x<20 and player_y>-830 and player_y<-630) or (player_x>20 and player_x<280 and player_y>-1070 and player_y<-630):
        glTranslatef(0,0,-100)
    if gameover and water:
        glTranslatef(0, 0, -60)
        glRotatef(50, 1, 0, 0)
    elif gameover and not water:
        glRotatef(90, 1, 0, 0)
    else:
        glRotatef(player_angle, 0, 0, 1)
        glRotatef(gun_angle, 0, 0, 1)

    glScalef(0.5, 0.5, 0.5)
    # BOTTOM CUBE
    glPushMatrix()
    glColor3f(0.5, 0.5, 0)
    glTranslatef(0, 30, 60)
    glutSolidCube(60)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.5, 0.5, 0)
    glTranslatef(0, -30, 60)
    glutSolidCube(60)
    glPopMatrix()

    # TOP CUBE
    glPushMatrix()
    glColor3f(0.5, 0.5, 0)
    glTranslatef(0, -30, 120)
    glutSolidCube(60)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.5, 0.5, 0)
    glTranslatef(0, 30, 120)
    glutSolidCube(60)
    glPopMatrix()

    # HEAD
    glPushMatrix()
    glColor3f(0, 0, 0)
    glTranslatef(0, 0, 180)
    gluSphere(gluNewQuadric(), 30, 20, 20)
    glPopMatrix()

    # legs
    glPushMatrix()
    glColor3f(0, 0, 1)
    glTranslatef(0, 30, 0)
    if riding:
        glTranslatef(0, 65, 0)
        glRotatef(70, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 20, 68, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -30, 0)
    if riding:
        glTranslatef(0, -65, 0)
        glRotatef(-70, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 20, 80, 10, 10)
    glPopMatrix()

    # hands
    glPushMatrix()
    glColor3f(1, 0.8, 0.6)
    glTranslate(0, 50, 140)
    glRotatef(-90, 0, 1, 0)
    if axe:
        glRotatef(-axe_swing_angle, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 20, 10, 80, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)
    glTranslate(0, -50, 140)
    glRotatef(-90, 0, 1, 0)
    if axe:
        glRotatef(-axe_swing_angle, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 20, 10, 80, 10, 10)
    glPopMatrix()

    # GUN
    if kill:
        glPushMatrix()
        glColor3f(0.5, 0.5, 0.5)
        glTranslate(0, 0, 135)
        glRotatef(-90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 30, 10, 120, 10, 10)
        glPopMatrix()

    elif knock:
        glPushMatrix()
        glColor3f(0.2, 0.08, 0.22)
        glTranslate(0, 0, 135)
        glRotatef(-90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 10, 10, 140, 10, 10)
        glPopMatrix()

    elif axe:
        axe_x=player_x
        axe_y=player_y
        glPushMatrix()

        glTranslatef(0, 0, 135)
        glRotatef(-90, 0, 1, 0)
        glRotatef(-axe_swing_angle, 0, 1, 0)
        #Handle
        glPushMatrix()
        glColor3f(0.4, 0.25, 0.1)
        gluCylinder(gluNewQuadric(), 8, 8, 140, 10, 10)
        glPopMatrix()

        #Blade
        glPushMatrix()
        glColor3f(0.7, 0.7, 0.7)
        glTranslatef(-10, 0, 130)
        glScalef(1.5, 0.4, 0.8)
        glutSolidCube(40)
        glPopMatrix()

        glPopMatrix()




    glPopMatrix()



def initialize_enemies():
    global enemy_positions
    enemy_positions = []
    margin = 100
    for i in range(2):
        x,y=_random_enemy_pos(margin)
        enemy_positions.append({
            'x': x,
            'y': y,
            'life':2,
            'speed': .2,
            'consc':1,
            'meat': 2,
            'count':0,
            'agro': False,
            'trap':False,
            'tame': False,
            'ride': False
        })


    global enemy_positions2, t3dino

    enemy_positions2 = []

    for _ in range(2):
        x, y = _random_enemy_pos(100)

        angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(angle)
        dy = math.sin(angle)

        enemy_positions2.append({
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'life':3,
            'consc':2,
            'count':0,
            'meat': 3,
            'speed': .3,
            'agro': False,
            'trap':False,
            'tame': False,
            'ride': False,
            'drown': False,
            'timer': random.randint(2000, 5000)
        })

    t3x, t3y = _random_enemy_pos(100)

    t3angle = random.uniform(0, 2 * math.pi)
    t3dx = math.cos(t3angle)
    t3dy = math.sin(t3angle)

    t3dino={
        'x': t3x,
        'y': t3y,
        'dx': t3dx,
        'dy':t3dy,
        'agro': False,
        'life':20,
        'speed': .2,
        'drown': False,
        'timer': random.randint(2000, 5000)
    }

def _random_enemy_pos(margin=100):
    while True:
        x = random.randint(-grid_len + margin, grid_len - margin)
        y = random.randint(-grid_len + margin, grid_len - margin)
        if math.hypot(x - player_x, y - player_y) > 1000:
            if all(math.hypot(x - ox, y - oy) > (enemy_rad + orad ) for (ox, oy, orad) in obstacle):
                return (x, y)


def draw_enemies():
    global frame_count,t3dino,enemy_position, consc_count
    # Resolve enemy collisions with static obstacles before drawing
    for enemy in enemy_positions:
        enemy['x'], enemy['y'] = resolve_position_against_obstacles(enemy['x'], enemy['y'], enemy_rad)

    for enemy in enemy_positions2:
        enemy['x'], enemy['y'] = resolve_position_against_obstacles(enemy['x'], enemy['y'], enemy_rad)

    try:
        t3dino['x'], t3dino['y'] = resolve_position_against_obstacles(t3dino['x'], t3dino['y'], enemy_rad * 2)
    except Exception:
        pass
    for enemy in enemy_positions:
        if enemy['ride']:
            enemy['x']=player_x
            enemy['y']=player_y

        ex = enemy['x']
        ey = enemy['y']
        if enemy['count']<=0 and enemy['consc']==0:
            enemy['consc']=1
            consc_count-=1


        glPushMatrix()
        glTranslatef(ex, ey, 0)
        if enemy['ride']:
            glRotatef(player_angle, 0, 0, 1)
            glRotatef(gun_angle, 0, 0, 1)

    # glScalef(scale, scale, scale)

        glPushMatrix()
        glColor3f(1, 0, 0)
        if enemy['tame']:
            glColor3f(0, 1, 0)
        glTranslate(0, 0, 20)
        gluSphere(gluNewQuadric(), enemy_rad * 0.7, 20, 20)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, 0, 0)
        if enemy['consc']<=0:
            glTranslate(0, -50, 20)
        elif enemy['ride']:
            glTranslate(-40, 0, 35)

        else:
            glTranslate(0, 0, 70)
        gluSphere(gluNewQuadric(), enemy_rad * 0.4, 20, 20)
        glPopMatrix()

        glPopMatrix()

        if enemy['count']>0:
            enemy['count']= max(0,enemy['count']-1)

    for enemy in enemy_positions2:
        ex = enemy['x']
        ey = enemy['y']
        if enemy['ride']:
            enemy['x']=player_x
            enemy['y']=player_y
        if enemy['count']<=0 and enemy['consc']==0:
            enemy['consc']=2
            consc_count-=1

        #scale = 1 + 0.12 * math.sin(frame_count * 0.02)
        glPushMatrix()
        glTranslatef(ex, ey, 0)
        if enemy['drown']:
            glTranslatef(0,0,-100)
        if enemy['ride'] and (player_x>grid_len+40 or player_x<-grid_len-40 or player_y>grid_len+50 or player_y<-grid_len-40) or (player_x>-1200 and player_x<20 and player_y>-830 and player_y<-630) or (player_x>20 and player_x<280 and player_y>-1070 and player_y<-630):
            glTranslatef(0,0,-100)
        if enemy['ride']:
            glRotatef(player_angle, 0, 0, 1)
            glRotatef(gun_angle, 0, 0, 1)
       # glScalef(scale, scale, scale)

        glPushMatrix()
        glColor3f(0, 1, 0)
        if enemy['agro'] and not enemy['tame']:
            glColor3f(1, 0, 0)
        glTranslate(0, 0, 50)
        gluSphere(gluNewQuadric(), enemy_rad * 1.3, 20, 20)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, 0, 0)
        if enemy['consc']<=0:
            glTranslate(0, -80, 20)

        elif enemy['ride']:
            glTranslate(-80, 0, 50)
        else:
            glTranslate(0, 0, 140)
        gluSphere(gluNewQuadric(), enemy_rad * 0.6, 20, 20)
        glPopMatrix()

        glPopMatrix()
        if enemy['count']>0:
            enemy['count']= max(0,enemy['count']-1)



    ex = t3dino['x']
    ey = t3dino['y']

    #scale = 1 + 0.12 * math.sin(frame_count * 0.02)
    glPushMatrix()
    glTranslatef(ex, ey, 0)
    if t3dino['drown']:
        glTranslatef(0,0,-100)
    # glScalef(scale, scale, scale)

    glPushMatrix()
    glColor3f(.8, 1, .7)
    if t3dino['agro']:
            glColor3f(0, 0, 0)
    glTranslate(0, 0, 50)
    gluSphere(gluNewQuadric(), enemy_rad * 2, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(.4, .8, .3)
    if t3dino['agro']:
            glColor3f(1, 0, 0)
    glTranslate(0, 0, 200)
    gluSphere(gluNewQuadric(), enemy_rad * .7, 20, 20)
    glPopMatrix()

    glPopMatrix()


def draw_bullets():
    for b in bullets:
        glPushMatrix()
        glColor3f(1, 0, 0)
        if knock:
            glColor3f(.5, 0, .5)
        glTranslatef(b['x'], b['y'], 100)
        if riding1:
            glTranslatef(0, 0, 20)
        elif riding2:
            glTranslatef(0, 0, 40)
        glutSolidCube(bullsize)
        glPopMatrix()


def spawn_bullet():
    ang_deg = player_angle + gun_angle
    ang = math.radians(ang_deg)

    forward_x = -math.cos(ang)
    forward_y = -math.sin(ang)

    muzzle_offset = 90
    bx = player_x + forward_x * muzzle_offset
    by = player_y + forward_y * muzzle_offset

    bullets.append({
        'x': bx,
        'y': by,
        'dx': forward_x,
        'dy': forward_y,
        'speed': bullspeed,
        'life': 0
    })



def update_enemies(delta_frames=1):
    global enemy_positions, t3dino,trap1, enemy_positions2, enemy_speed, consc_count
    new_positions = []

    for enemy in enemy_positions:
        ex = enemy['x']
        ey = enemy['y']
        if enemy['consc']>0 and not enemy['ride']:

            vx = player_x - ex
            vy = player_y - ey
            dist = math.hypot(vx, vy)
            if not enemy['tame']:
                if dist > 1e-6:
                    nx = vx / dist
                    ny = vy / dist
                else:
                    nx, ny = 0, 0
            else:
                if dist > 150:
                    nx = vx / dist
                    ny = vy / dist
                else:
                    nx, ny = 0, 0
            ex += nx * enemy['speed'] * delta_frames
            ey += ny * enemy['speed'] * delta_frames
            if ex>trap1['trapx']-100 and ex<trap1['trapx']+100 and ey>trap1['trapy']+100 and ey<trap1['trapy']+300 and trap1['trapset']:
                trap1['trapact']=True
                enemy['trap']= True
            if trap1['trapact'] and enemy['trap']:
                ex = max(trap1['trapx']-100 , min(trap1['trapx']+100, ex))
                ey = max(trap1['trapy']+100 , min(trap1['trapy']+300, ey))


            enemy['x']=ex
            enemy['y']=ey
            if (ex>grid_len+40 or ex<-grid_len-40 or ey>grid_len+50 or ey<-grid_len-40) or (ex>-1200 and ex<20 and ey>-830 and ey<-630) or (ex>20 and ex<280 and ey>-1070 and ey<-630) :
                x,y=_random_enemy_pos(120)
                enemy['x'] = x
                enemy['y'] = y
                enemy['trap'] =False
                enemy['life'] = 2
                enemy['consc'] = 1
                enemy['meat'] = 2
                enemy['count'] = 0
                enemy['agro'] = False
                enemy['trap'] = False
                enemy['tame'] = False
                enemy['ride'] = False



    global enemy_positions2


    for enemy in enemy_positions2:
        ex= enemy['x']
        ey= enemy['y']
        if enemy['drown']:
            enemy['speed']= 0.1
        if enemy['consc']>0 and not enemy['ride']:

            vx = player_x - enemy['x']
            vy = player_y - enemy['y']
            dist = math.hypot(vx, vy)
            if dist < 500:
                enemy['agro']= True
            # Move enemy
            if enemy['agro'] and not enemy['tame']:
                if dist > 1e-6:
                    nx = vx / dist
                    ny = vy / dist
                else:
                    nx, ny = 0, 0

                ex += nx * enemy['speed'] * delta_frames
                ey += ny * enemy['speed'] * delta_frames
                if ex>trap1['trapx']-100 and ex<trap1['trapx']+100 and ey>trap1['trapy']+100 and ey<trap1['trapy']+300 and trap1['trapset']:
                    trap1['trapact']=True
                    enemy['trap']= True
                if trap1['trapact'] and enemy['trap']:
                    ex = max(trap1['trapx']-100 , min(trap1['trapx']+100, ex))
                    ey = max(trap1['trapy']+100 , min(trap1['trapy']+300, ey))

                enemy['x']=ex
                enemy['y']=ey
                if (ex>grid_len+40 or ex<-grid_len-40 or ey>grid_len+50 or ey<-grid_len-40) or (ex>-1200 and ex<20 and ey>-830 and ey<-630) or (ex>20 and ex<280 and ey>-1070 and ey<-630) :
                    enemy['drown']= True
                else:
                    enemy['drown']= False
                    enemy['speed']= 0.3

            elif enemy['tame']:
                if dist > 200:
                    nx = vx / dist
                    ny = vy / dist
                else:
                    nx, ny = 0, 0
                ex += nx * enemy['speed'] * delta_frames
                ey += ny * enemy['speed'] * delta_frames

                enemy['x']=ex
                enemy['y']=ey
                if (ex>grid_len+40 or ex<-grid_len-40 or ey>grid_len+50 or ey<-grid_len-40) or (ex>-1200 and ex<20 and ey>-830 and ey<-630) or (ex>20 and ex<280 and ey>-1070 and ey<-630) :
                    enemy['drown']= True
                else:
                    enemy['drown']= False
                    enemy['speed']= 0.3


            else:
                enemy['x'] += enemy['dx'] * enemy['speed'] * delta_frames
                enemy['y'] += enemy['dy'] * enemy['speed'] * delta_frames
                if (ex>grid_len+40 or ex<-grid_len-40 or ey>grid_len+50 or ey<-grid_len-40) or (ex>-1200 and ex<20 and ey>-830 and ey<-630) or (ex>20 and ex<280 and ey>-1070 and ey<-630) :
                    enemy['drown']= True

                else:
                    enemy['drown']= False
                    enemy['speed']= 0.3

                # Countdown direction timer
                enemy['timer'] -= 1

                # Change direction when timer expires
                if enemy['timer'] <= 0:
                    angle = random.uniform(0, 2 * math.pi)
                    enemy['dx'] = math.cos(angle)
                    enemy['dy'] = math.sin(angle)
                    enemy['timer'] = random.randint(2000, 5000)

                # Keep enemy inside grid
                enemy['x'] = max(-grid_len , min(grid_len , enemy['x']))
                enemy['y'] = max(-grid_len , min(grid_len , enemy['y']))

                if enemy['x']>grid_len - 50 or enemy['x']<-grid_len + 50:
                    #enemy['timer'] =0
                    enemy['timer'] = random.randint(2000, 5000)
                    enemy['dx'] = -1*(enemy['x']/abs(enemy['x']))
                    enemy['dy'] = 0

                if enemy['y']>grid_len - 50 or enemy['y']<-grid_len + 50:
                    enemy['timer'] = random.randint(2000, 5000)
                    enemy['dx'] = 0
                    enemy['dy'] = -1*(enemy['y']/abs(enemy['y']))

    #type3 dino
    ex= t3dino['x']
    ey= t3dino['y']

    vx = player_x - t3dino['x']
    vy = player_y - t3dino['y']
    dist = math.hypot(vx, vy)

    if t3dino['agro']:
            t3dino['speed']= 0.5
            if t3dino['drown']:
                t3dino['speed']= 0.2
            if dist > 1e-6:
                nx = vx / dist
                ny = vy / dist
            else:
                nx, ny = 0, 0
            ex += nx * t3dino['speed'] * delta_frames
            ey += ny * t3dino['speed'] * delta_frames

            t3dino['x']=ex
            t3dino['y']=ey
            if (ex>grid_len+40 or ex<-grid_len-40 or ey>grid_len+50 or ey<-grid_len-40) or (ex>-1200 and ex<20 and ey>-830 and ey<-630) or (ex>20 and ex<280 and ey>-1070 and ey<-630) :
                    t3dino['drown']= True
                    t3dino['speed']= 0.2

            else:
                    t3dino['drown']= False
                    t3dino['speed']= 0.5

    else:
        t3dino['x'] += t3dino['dx'] * t3dino['speed'] * delta_frames
        t3dino['y'] += t3dino['dy'] * t3dino['speed'] * delta_frames

        if (ex>grid_len+40 or ex<-grid_len-40 or ey>grid_len+50 or ey<-grid_len-40) or (ex>-1200 and ex<20 and ey>-830 and ey<-630) or (ex>20 and ex<280 and ey>-1070 and ey<-630) :
                    t3dino['drown']= True
                    t3dino['speed']= 0.1
        else:
                    t3dino['drown']= False
                    t3dino['speed']= 0.2

        # Countdown direction timer
        t3dino['timer'] -= 1

        # Change direction when timer expires
        if t3dino['timer'] <= 0:
            angle = random.uniform(0, 2 * math.pi)
            t3dino['dx'] = math.cos(angle)
            t3dino['dy'] = math.sin(angle)
            t3dino['timer'] = random.randint(2000, 5000)

        # Keep t3dino inside grid
        t3dino['x'] = max(-grid_len , min(grid_len , t3dino['x']))
        t3dino['y'] = max(-grid_len , min(grid_len , t3dino['y']))

        if t3dino['x']>grid_len - 50 or t3dino['x']<-grid_len + 50:
            #t3dino['timer'] =0
            t3dino['timer'] = random.randint(2000, 5000)
            t3dino['dx'] = -1*(t3dino['x']/abs(t3dino['x']))
            t3dino['dy'] = 0

        if t3dino['y']>grid_len - 50 or t3dino['y']<-grid_len + 50:
            t3dino['timer'] = random.randint(2000, 5000)
            t3dino['dx'] = 0
            t3dino['dy'] = -1*(t3dino['y']/abs(t3dino['y']))


def update_bullandcoll():
    global bullets, enemy_positions, score, miss, life, gameover, consc_count, t3dino
    new_bullets = []

    hit_enemy_indices = set()

    for bi, b in enumerate(bullets):
        # Move bullet
        b['x'] += b['dx'] * b['speed']
        b['y'] += b['dy'] * b['speed']
        b['life'] += 1

        # collision with enemies
        hit = False
        for enemy in enemy_positions:
            ex = enemy['x']
            ey = enemy['y']
            dist_sq = (b['x'] - ex) ** 2 + (b['y'] - ey) ** 2
            effective_enemy_radius = enemy_rad * 0.7
            if dist_sq <= (effective_enemy_radius + bullsize) ** 2:
                hit = True
                enemy['agro']= True

                if kill:
                    enemy['life']= max(0,enemy['life']-1)
                    if enemy['life']<=0:
                        x,y=_random_enemy_pos(120)
                        enemy['x'] = x
                        enemy['y'] = y
                        enemy['trap'] =False
                        enemy['life'] = 2
                        enemy['consc'] = 1
                        enemy['meat'] = 2
                        enemy['count'] = 0
                        enemy['agro'] = False
                        enemy['trap'] = False
                        enemy['tame'] = False
                        enemy['ride'] = False

                        score += 1
                        break
                elif knock:
                    enemy['consc']= max(0,enemy['consc']-1)
                    if enemy['consc']<=0 and enemy['count']==0:
                        consc_count+=1
                        enemy['count']=10000


        for enemy in enemy_positions2:
            ex = enemy['x']
            ey = enemy['y']
            dist_sq = (b['x'] - ex) ** 2 + (b['y'] - ey) ** 2
            effective_enemy_radius = enemy_rad * 0.8
            if dist_sq <= (effective_enemy_radius + bullsize) ** 2:
                hit = True
                enemy['agro']= True

                if kill:
                    enemy['life']= max(0,enemy['life']-1)
                    if enemy['life']<=0:
                        angle = random.uniform(0, 2 * math.pi)
                        dx = math.cos(angle)
                        dy = math.sin(angle)
                        x,y=_random_enemy_pos(120)
                        enemy['x'] = x
                        enemy['y'] = y
                        enemy['dx'] = dx
                        enemy['dy'] = dy
                        enemy['trap'] =False
                        enemy['life'] = 3
                        enemy['consc'] = 2
                        enemy['meat'] = 3
                        enemy['count'] = 0
                        enemy['agro'] = False
                        enemy['trap'] = False
                        enemy['tame'] = False
                        enemy['ride'] = False

                        score += 1
                        break
                elif knock:
                    enemy['consc']= max(enemy['consc']-1, 0)
                    if enemy['consc']<=0 and enemy['count']==0:
                        consc_count+=1
                        enemy['count']=10000

        ex = t3dino['x']
        ey = t3dino['y']

        dist_sq = (b['x'] - ex) ** 2 + (b['y'] - ey) ** 2
        effective_enemy_radius = enemy_rad * 0.7
        if dist_sq <= (effective_enemy_radius + bullsize) ** 2:
            hit = True
            t3dino['agro']= True

            if kill:
                t3dino['life']= max(0,t3dino['life']-1)
                if t3dino['life']<=0:
                    pass


        out_of_bounds = abs(b['x']) > grid_len + \
            300 or abs(b['y']) > grid_len + 300
        if hit:
            continue
        elif b['life'] > bullmaxlife or out_of_bounds:
            miss += 1

            if miss >= 10:
                gameover = True
            continue
        else:
            new_bullets.append(b)

    bullets = new_bullets

    for enemy in enemy_positions:
        if enemy['consc']>0 and not enemy['tame']:
            ex = enemy['x']
            ey = enemy['y']
            dist = math.hypot(ex - player_x, ey - player_y)
            if dist <= (enemy_rad * 0.8 + player_rad):
                life -= enemy['life']
                x,y=_random_enemy_pos(120)
                enemy['x'] = x
                enemy['y'] = y
                enemy['trap'] =False
                enemy['life'] = 2
                enemy['consc'] = 1
                enemy['meat'] = 2
                enemy['count'] = 0
                enemy['agro'] = False
                enemy['trap'] = False
                enemy['tame'] = False
                enemy['ride'] = False
                print(f"Player hit! life={life}")
                if life <= 0:
                    gameover = True
    for enemy in enemy_positions2:
        if enemy['consc']>0 and enemy['agro'] and not enemy['tame']:
            ex = enemy['x']
            ey = enemy['y']
            dist = math.hypot(ex - player_x, ey - player_y)
            if dist <= (enemy_rad * 0.8 + player_rad):
                life -= enemy['life']
                x,y=_random_enemy_pos(120)
                angle = random.uniform(0, 2 * math.pi)
                dx = math.cos(angle)
                dy = math.sin(angle)
                enemy['dx'] = dx
                enemy['dy'] = dy
                enemy['x'] = x
                enemy['y'] = y
                enemy['trap'] =False
                enemy['life'] = 3
                enemy['consc'] = 2
                enemy['meat'] = 3
                enemy['count'] = 0
                enemy['agro'] = False
                enemy['trap'] = False
                enemy['tame'] = False
                enemy['ride'] = False
                print(f"Player hit! life={life}")
                if life <= 0:
                    gameover = True

    if t3dino['agro']:
            ex = t3dino['x']
            ey = t3dino['y']
            dist = math.hypot(ex - player_x, ey - player_y)
            if dist <= (enemy_rad * 1 + player_rad):
                life -= t3dino['life']
                if life <= 0:
                    gameover = True



    while len(enemy_positions) < 2:
        x,y=_random_enemy_pos(100)
        enemy_positions.append({
            'x': x,
            'y': y,
            'life':2,
            'consc':1,
            'meat': 2,
            'agro': False,
            'trap':False,
            'tame': False,
            'ride': False
        })


def autofirerotate():
    global gun_angle, cheat_firetimer, bullets, enemy_positions2, cheat, consc_count, player_x, player_y, player_angle
    global cheat_rotspeed, cheat_maxdist, bullspeed
    if consc_count>=unconsc_count:
        cheat=not cheat
        gun_angle=0
        cheat_firetimer=0

    # Rotate the gun continuously
    gun_angle += cheat_rotspeed
    gun_angle %= 360

    if cheat_firetimer > 0:
        cheat_firetimer -= 1
        return

    current_absolute_angle = (player_angle + gun_angle) % 360

    for enemy in enemy_positions:
        if enemy['consc']!=0 and not enemy['tame']:
            ex=enemy['x']
            ey=enemy['y']
            dist = math.hypot(ex - player_x, ey - player_y)
            if dist > cheat_maxdist or dist == 0:
                continue

            dx = ex - player_x
            dy = ey - player_y

            target_rad = math.atan2(-dy, -dx)
            target_deg = math.degrees(target_rad) % 360

            angle_diff = abs(target_deg - current_absolute_angle)

            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            if angle_diff < (cheat_rotspeed * 0.8):
                norm = math.hypot(dx, dy)
                exact_dx = dx / norm
                exact_dy = dy / norm

                muzzle_offset = 90
                bx = player_x + exact_dx * muzzle_offset
                by = player_y + exact_dy * muzzle_offset

                bullets.append({'x': bx,'y': by,'dx': exact_dx,'dy': exact_dy,'speed': bullspeed,'life': 0})
                cheat_firetimer = 10
                break

    for enemy in enemy_positions2:
        if enemy['consc']!=0 and not enemy['tame']:
            ex=enemy['x']
            ey=enemy['y']
            dist = math.hypot(ex - player_x, ey - player_y)
            if dist > cheat_maxdist or dist == 0:
                continue

            dx = ex - player_x
            dy = ey - player_y

            target_rad = math.atan2(-dy, -dx)
            target_deg = math.degrees(target_rad) % 360

            angle_diff = abs(target_deg - current_absolute_angle)

            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            if angle_diff < (cheat_rotspeed * 0.8):
                norm = math.hypot(dx, dy)
                exact_dx = dx / norm
                exact_dy = dy / norm

                muzzle_offset = 90
                bx = player_x + exact_dx * muzzle_offset
                by = player_y + exact_dy * muzzle_offset

                bullets.append({'x': bx,'y': by,'dx': exact_dx,'dy': exact_dy,'speed': bullspeed,'life': 0})
                cheat_firetimer = 10
                break

def axe_hit():
    global axe_x, axe_y, enemy_positions, enemy_positions2, totalmeat, consc_count
    for enemy in enemy_positions:
        if enemy['consc']==0:
            ex = enemy['x']
            ey = enemy['y']
            dist_sq = (axe_x - ex) ** 2 + (axe_y - ey) ** 2
            effective_enemy_radius = enemy_rad * 0.9
            if dist_sq <= (effective_enemy_radius + 140) ** 2:
                enemy['meat']=max(0,enemy['meat']-1)
                totalmeat+=1
                if enemy['meat']<=0:
                    x,y=_random_enemy_pos(100)
                    enemy['x'] = x
                    enemy['y'] = y
                    enemy['trap'] =False
                    enemy['life'] = 2
                    enemy['consc'] = 1
                    enemy['meat'] = 2
                    enemy['count'] = 0
                    enemy['agro'] = False
                    enemy['trap'] = False
                    enemy['tame'] = False
                    enemy['ride'] = False
                    consc_count-=1

    for enemy in enemy_positions2:
        if enemy['consc']==0:
            ex = enemy['x']
            ey = enemy['y']
            dist_sq = (axe_x - ex) ** 2 + (axe_y - ey) ** 2
            effective_enemy_radius = enemy_rad * 0.9
            if dist_sq <= (effective_enemy_radius + 140) ** 2:
                enemy['meat']=max(0,enemy['meat']-1)
                totalmeat+=1
                if enemy['meat']<=0:
                    x,y=_random_enemy_pos(120)
                    angle = random.uniform(0, 2 * math.pi)
                    dx = math.cos(angle)
                    dy = math.sin(angle)
                    enemy['dx'] = dx
                    enemy['dy'] = dy
                    enemy['x'] = x
                    enemy['y'] = y
                    enemy['trap'] =False
                    enemy['life'] = 3
                    enemy['consc'] = 2
                    enemy['meat'] = 3
                    enemy['count'] = 0
                    enemy['agro'] = False
                    enemy['trap'] = False
                    enemy['tame'] = False
                    enemy['ride'] = False
                    consc_count-=1


def keyboardListener(key, x, y):
    global player_x, player_y, player_angle, gun_angle, water,trap1,kill,knock,axe, riding, riding1, riding2
    global life, score, miss, gameover, cheat, autocamgun, cheat_firetimer, consc_count, totalmeat, unconsc_count

    if key == b'r':
        # Reset game state
        life = 20
        score = 0
        miss = 0
        player_x = 0
        player_y = 0
        player_angle = -90
        gun_angle = 0
        bullets.clear()
        initialize_enemies()
        gameover = False
        cheat = False
        consc_count=0
        autocamgun = False
        cheat_firetimer = 0
        knock=False
        axe= True
        kill=False
        trap1={'trapset':False,'trapact':False,'trapx':0,'trapy':0}
        print("Game reset!")
        glutPostRedisplay()
        return

    # Toggle cheat mode
    if key == b'c':
        cheat = not cheat
        if cheat:
            knock=True
            axe= False
            kill=False
        else:
            gun_angle=0
        cheat_firetimer = 0
        print(f"Cheat mode {'ON' if cheat else 'OFF'}")
        glutPostRedisplay()
        return

    # Toggle auto-cam
    if key == b'v':
        autocamgun = not autocamgun
        print(
            f"Auto-Cam-with-gun {'ON' if autocamgun else 'OFF'} (applies only when cheat mode is active and in first-person)")
        glutPostRedisplay()
        return

    if gameover:
        return

    if key == b't':
        if trap1['trapset']:
            trap2['trapset']=True
        else:
            trap1['trapset']= True
            trap1['trapx']=player_x
            trap1['trapy']=player_y
        print("Trap set!")


    if key == b'k':
        if kill:
            knock=True
            kill= False
        elif knock:
            axe=True
            knock=False
        elif axe:
            kill= True
            axe= False

    if key == b'f':
        for enemy in enemy_positions:
            if enemy['consc']<=0:
                ex = enemy['x']
                ey = enemy['y']
                dist = math.hypot(ex - player_x, ey - player_y)
                if dist <= (enemy_rad * 0.8 + player_rad)+50:
                    if totalmeat>=2:
                        enemy['tame']= True
                        enemy['trap'] =False
                        enemy['life'] = 2
                        enemy['consc'] = 1
                        enemy['meat'] = 2
                        enemy['count'] = 0
                        enemy['agro'] = False
                        enemy['trap'] = False
                        enemy['ride'] = False
                        totalmeat-=2
                        consc_count-=1
                        unconsc_count-=1
                        print("Dino Tamed!")

                    else:
                        print("Not enough meat to tame dino.")

                else:
                    print("Too far to tame dino.")


        for enemy in enemy_positions2:
            if enemy['consc']<=0:
                ex = enemy['x']
                ey = enemy['y']
                dist = math.hypot(ex - player_x, ey - player_y)
                if dist <= (enemy_rad * 0.8 + player_rad)+50:
                    if totalmeat>=3:
                        enemy['tame']= True
                        enemy['trap'] =False
                        enemy['life'] = 3
                        enemy['consc'] = 2
                        enemy['meat'] = 3
                        enemy['count'] = 0
                        enemy['agro'] = False
                        enemy['ride'] = False
                        totalmeat-=3
                        consc_count-=1
                        unconsc_count-=1
                        print("Dino Tamed!")

                    else:
                        print("Not enough meat to tame dino.")

                else:
                    print("Too far to tame dino.")


    if key == b'm':
        if not riding:
            if not riding:
                for enemy in enemy_positions:
                    if enemy['tame']:
                        ex = enemy['x']
                        ey = enemy['y']
                        dist = math.hypot(ex - player_x, ey - player_y)
                        if dist <= (enemy_rad * 0.8 + player_rad)+50:
                            player_angle=-90
                            player_x= enemy['x']
                            player_y= enemy['y']
                            riding=True
                            riding1=True
                            enemy['ride']= True
                            print("Riding Dino!")
                            break
                        else:
                            print("Too far to ride dino.")

            if not riding:
                for enemy in enemy_positions2:
                    if enemy['tame']:
                        ex = enemy['x']
                        ey = enemy['y']
                        dist = math.hypot(ex - player_x, ey - player_y)
                        if dist <= (enemy_rad * 0.8 + player_rad)+50:
                            riding=True
                            riding2=True
                            player_angle=-90
                            player_x= enemy['x']
                            player_y= enemy['y']
                            enemy['ride']= True
                            print("Riding Dino!")
                            break
                        else:
                            print("Too far to ride dino.")

        else:
            riding = not riding
            riding1 = False
            riding2 = False
            if not riding:
                for enemy in enemy_positions:
                  enemy['ride']= False
                for enemy in enemy_positions2:
                  enemy['ride']= False
                print("Dismounted from Dino.")
    # Normalize angle
    player_angle %= 360
    angle_rad = math.radians(player_angle)

    # Movement
    if key == b'w':
        player_x -= player_speed * math.cos(angle_rad)
        player_y -= player_speed * math.sin(angle_rad)

    if key == b's':
        player_x += player_speed * math.cos(angle_rad)
        player_y += player_speed * math.sin(angle_rad)


    if key == b'a':
        player_angle += rotation_speed
    if key == b'd':
        player_angle -= rotation_speed


    #Waterdeath
    if not riding and player_x>grid_len+40 or player_x<-grid_len-40 or player_y>grid_len+50 or player_y<-grid_len-40:
        water= True
        gameover= not gameover

    if not riding and player_x>-1200 and player_x<20 and player_y>-830 and player_y<-630:
        water= True
        gameover= not gameover


    if not riding and player_x>20 and player_x<280 and player_y>-1070 and player_y<-630:
        water= True
        gameover= not gameover
    # Keep player inside bounds
    player_x = max(-grid_len - 60, min(grid_len + 60, player_x))
    player_y = max(-grid_len - 60, min(grid_len + 60, player_y))

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global cam_angle, cam_height
    if key == GLUT_KEY_UP:
        cam_height += 10
    if key == GLUT_KEY_DOWN and cam_height > 50:
        cam_height -= 10
    if key == GLUT_KEY_LEFT:
        cam_angle += 5
    if key == GLUT_KEY_RIGHT:
        cam_angle -= 5
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global first_person, gameover
    global axe_swinging,axe_x, axe_y
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not gameover:
            if not axe:
              spawn_bullet()
            else:
               axe_swinging = True
               axe_x=player_x
               axe_y=player_y
               axe_hit()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person
        print(
            f"Camera mode: {'First Person' if first_person else 'Third Person'}")
    glutPostRedisplay()

def idle():
    global frame_count
    if cheat and not gameover:
        autofirerotate()
    if not gameover:
        update_enemies()
        update_bullandcoll()



    global axe_swing_angle, axe_swinging

    if axe_swinging:
        axe_swing_angle -= axe_swing_speed

        if axe_swing_angle <= axe_max_swing:
            axe_swing_angle = axe_max_swing
            axe_swinging = False

    else:
        if axe_swing_angle < 0:
            axe_swing_angle += axe_swing_speed
            if axe_swing_angle >= 0:
                axe_swing_angle = 0

    frame_count += 1
    glutPostRedisplay()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        cam_z = 130
        if riding1:
            cam_z = 150
        elif riding2:
            cam_z = 210
        if cheat and autocamgun:
            ang = math.radians(player_angle + gun_angle)
        else:
            ang = math.radians(player_angle)

        # Forward direction
        forward_x = -math.cos(ang)
        forward_y = -math.sin(ang)

        # Camera offsets
        eye_offset_forward = 10
        eye_x = player_x + forward_x * eye_offset_forward
        eye_y = player_y + forward_y * eye_offset_forward

        # Look forward
        look_distance = 100
        look_x = eye_x + forward_x * look_distance
        look_y = eye_y + forward_y * look_distance

        gluLookAt(eye_x, eye_y, cam_z,look_x, look_y, cam_z,0, 0, 1)

    else:
        angle_rad = math.radians(cam_angle)
        camera_x = cam_dis * math.cos(angle_rad)
        camera_y = cam_dis * math.sin(angle_rad)
        camera_z = cam_height
        gluLookAt(camera_x, camera_y, camera_z,0, 0, 0,0, 0, 1)


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1600, 1500)

    setupCamera()
    draw_texts()
    draw_grids_and_walls()
    draw_enemies()
    draw_player()
    draw_bullets()
    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1600, 1000)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D OpenGL Intro")

    # Enable depth testing so the model renders correctly
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearDepth(1.0)

    initialize_enemies()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
