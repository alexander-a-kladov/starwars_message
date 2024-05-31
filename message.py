#!/usr/bin/python3
import sys
from array import array

import math as m
import pygame
import moderngl

pygame.init()

LETTER_SIZE=(110,120)
LETTER_BOX=(25,10,80,100)

SCR_SIZE=(1400,800)

screen = pygame.display.set_mode(SCR_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface(SCR_SIZE)
back = pygame.Surface(SCR_SIZE)
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
    uv.y = pow(uvs.y*3.0,0.5)-0.9;
    
    uv.x =  ((-0.5+0.5*uvs.y)+uvs.x)/(uvs.y);

    vec3 color=vec3(0.0,0.0,0.0);
    if (uv.x>0.0 && uv.x<1.0 && uv.y>0.0 && uv.y<1.0) {
    	color = vec3(texture(tex, uv).rg, 0)*pow(uvs.y,1);
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
    symb_dict={'.':37, ',':38, ';':39, ':':40, '$':41, '#':42, '\'':43, '!':44,'"':45,
               '/':46, '?':47, '%':48, '&':49, '(':50, ')':51, '@':52 }
    if symb>='A' and symb<='Z':
        index = ord(symb)-ord('A')
        return getFontBox(index)
    if symb>='0' and symb<='9':
        index = ord(symb)-ord('0')+27
        return getFontBox(index)
    if symb in symb_dict:
        return getFontBox(symb_dict[symb])
    return False
    
def drawTextLine(offset, line, fonts_img, t):
    c=0
    x,y = offset
    for symb in line.upper():
        font = getSymbol(symb)
        y = offset[1]
        if font:
            display.blit(fonts_img.subsurface(font), (x,y))
        x += LETTER_BOX[2]-42
        c+=1 
    
if __name__ == "__main__":
    t = 0
    text = "Hello, World!"
    zoom = 10
    MAX_TICK = 100
    MIN_TICK = 25
    tick = MIN_TICK
 
    
    if len(sys.argv)>2:
        image_name = sys.argv[2]
    else:
        image_name = "images/img.png"
        
    if len(sys.argv)>1:
        message_name = sys.argv[1]
    else:
        message_name = "message.txt"
        
    pygame.mixer.init()
    pygame.mixer.music.load("song.mp3")
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play()
    pygame.display.set_caption(f'{message_name}')
    mute = False
    
    img = pygame.image.load(image_name)
    message_f = open(message_name, "r")
    if message_f:
        text = []
        for line in message_f.readlines():
           text.append(line.strip())

    display.fill((0, 0, 0))
    yellow = (0, 100, 100)
    #pygame.draw.rect(display, yellow, pygame.Rect(0,0,SCR_SIZE[0],SCR_SIZE[1]))
    sprawl_index = 0
    crawl = 0
    keyup = True
    pygame.key.set_repeat(100)
    while True:
        if crawl%80==0 and zoom:
            drawTextLine((1,SCR_SIZE[1]-100), text[sprawl_index], img, t)
            sprawl_index+=1

        if sprawl_index >= len(text):
            sprawl_index = 0
        t += 1
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and keyup:
                    keyup = False
                    if zoom > 0:
                        zoom = 0
                        pygame.mixer.music.pause()
                    else:
                        zoom = 1
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_m and keyup:
                    keyup = False
                    if mute:
                        pygame.mixer.music.play()
                        mute = False
                    else:
                        pygame.mixer.music.stop()
                        mute = True
                elif event.key == pygame.K_UP:
                    if tick < MAX_TICK:
                        tick+=1
                elif event.key == pygame.K_DOWN:
                    if tick > MIN_TICK:
                        tick-=1
            elif event.type == pygame.KEYUP:
                keyup = True
                    

        if zoom>0:
            crawl+=1
            back.blit(display.subsurface(0,1,SCR_SIZE[0],SCR_SIZE[1]-1), (0,0))
            display.blit(back, (0,0))
    	
        frame_tex = surf_to_texture(display)
        frame_tex.use(0)
        program['tex'] = 0
        render_object.render(mode=moderngl.TRIANGLE_STRIP)
    
        pygame.display.flip()
    
        frame_tex.release()
    
        clock.tick(tick)
    