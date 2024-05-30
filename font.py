#!/usr/bin/python3
import sys
from array import array

import math as m
import pygame
import moderngl

pygame.init()

LETTER_SIZE=(110,120)
LETTER_BOX=(25,10,80,100)

screen = pygame.display.set_mode((1000, 800), pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface((1000, 800))
ctx = moderngl.create_context()

clock = pygame.time.Clock()

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0, # topleft
    1.0, 1.0, 1.0, 0.0,   # topright
    -1.0, -1.0, 0.0, 1.0,  # bottomleft
    1.0, -1.0, 1.0, 1.0  # bottomright
]))

vert_shader = '''
#version 430 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}
'''

frag_shader = '''
#version 430 core

uniform sampler2D tex;
//uniform float proect;

in vec2 uvs;
out vec4 f_color;

void main() {
    vec2 uv = uvs;
    uv.y = uvs.y;
    
    uv.x =  ((-0.5+0.5*uv.y)+uvs.x)/(uv.y);

    vec3 color=vec3(0.0,0.0,0.0);
    if (uv.x>=0.0 && uv.x<=1.0 && uv.y>=0.0 && uv.y<=1.0) {
    	color = vec3(texture(tex, uv).rg, 0)*pow(uvs.y,3);
    }
    f_color = vec4(color, 1.0);
}
'''

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

def getFontBox(index):
    row = index // 9
    col = index % 9
    x = col*LETTER_SIZE[0]+LETTER_BOX[0]
    y = row*LETTER_SIZE[1]+LETTER_BOX[1]
    return (x, y, LETTER_BOX[2], LETTER_BOX[3])

def getSymbol(symb):
    if symb>='A' and symb<='Z':
        index = ord(symb)-ord('A')
        return getFontBox(index)
    elif symb==',':
        return getFontBox(38)
    elif symb=='!':
        return getFontBox(44)
    return False
    
def drawTextLine(offset, line, fonts_img, t):
    c=0
    x,y = offset
    for symb in line.upper():
        font = getSymbol(symb)
        y = offset[1]#+20*m.cos((t-5*c)/10.0)
        if font:
            display.blit(fonts_img.subsurface(font), (x,y))
        x += LETTER_BOX[2]-40
        c+=1 
    
if __name__ == "__main__":
    t = 0
    speed = 0.0
    angle = 0.0
    zoom = 500
    zoom_speed = 0
    MAX_SPEED = 180.0
    MAX_ZOOM_SPEED = 25
    MAX_ZOOM = 1000
    MIN_ZOOM = -200
    
    if len(sys.argv)>1:
        image_name = sys.argv[1]
    else:
        image_name = "images/img.png"
        
    if len(sys.argv)>2:
        speed = float(sys.argv[2])
    else:
        speed = 0.0
        
    if speed < -180.0 or speed > 180.0:
        speed = 0.0
    
    pygame.display.set_caption(f'Zoom {round(1.0/zoom,3)} rotation speed {-speed} deg zoom_speed {-zoom_speed/100.0}')
    
    img = pygame.image.load(image_name)
    
    pygame.key.set_repeat(150)

    while True:
        display.fill((0, 0, 0))
        yellow = (0, 100, 100)
        pygame.draw.rect(display, yellow, pygame.Rect(0,0,1000,800))
        drawTextLine((250,zoom), "Hello, World!", img, t)
        drawTextLine((220,zoom+70), "of Good People", img, t)
    
        t += 1
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if speed < MAX_SPEED:
                        speed += 0.5
                elif event.key == pygame.K_RIGHT:
                    if speed > -MAX_SPEED:
                        speed -= 0.5
                elif event.key == pygame.K_DOWN:
                    if zoom_speed < MAX_ZOOM_SPEED:
                        zoom_speed += 1
                elif event.key == pygame.K_UP:
                    if zoom_speed > -MAX_ZOOM_SPEED:
                        zoom_speed -= 1
                elif event.key == pygame.K_SPACE:
                    speed = 0.0
                    zoom_speed = 0
            elif event.type == pygame.KEYUP:
                zoom_speed = 0
        pygame.display.set_caption(f'Zoom {zoom:.3f} rotation speed {-speed} deg zoom_speed {-zoom_speed/100.0}')
        angle += speed
    
        if zoom >= MIN_ZOOM and zoom <= MAX_ZOOM:
            zoom += zoom_speed
        if zoom < MIN_ZOOM:
            zoom_speed = 0
            zoom = MIN_ZOOM
        if zoom > MAX_ZOOM:
            zoom_speed = 0
            zoom = MAX_ZOOM
    
        frame_tex = surf_to_texture(display)
        frame_tex.use(0)
        program['tex'] = 0
        render_object.render(mode=moderngl.TRIANGLE_STRIP)
    
        pygame.display.flip()
    
        frame_tex.release()
    
        clock.tick(25)
    
