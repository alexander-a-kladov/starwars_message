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
uniform float proect_x;
uniform float proect_y;
uniform int shadow_on;

in vec2 uvs;
out vec4 f_color;

void main() {
    vec2 uv = uvs;
    uv.y = sqrt(uvs.y-proect_y)/(sqrt(1-proect_y)+0.15);
    
    uv.x =  ((-proect_x+proect_x*uvs.y)+uvs.x)/(2.0*proect_x*uvs.y+(1.0-2.0*proect_x));

    vec3 color=vec3(0.0,0.0,0.0);
    if (uv.x>0.0 && uv.x<1.0 && uv.y>0.0 && uv.y<1.0) {
    	color = vec3(texture(tex, uv).r*1.2, texture(tex, uv).g*0.8, 0);
    	if (shadow_on == 1) {
    	   color=uv.y*color;
    	}
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
    
if __name__ == "__main__":
    t = 0
    text = ["Hello, World!","","",""]
    zoom = 1
    shadow = True
    music = False
    mute = True
    MAX_TICK = 50
    MIN_TICK = 10
    tick = 25
    MAX_PROECT_X = 100
    MIN_PROECT_X = 0
    proect_x = MAX_PROECT_X//2
    MAX_PROECT_Y = 100
    MIN_PROECT_Y = 0
    proect_y = 30
        
    if len(sys.argv)>1:
        message_name = sys.argv[1]
    else:
        message_name = "hello_world.txt"
    
    if len(sys.argv)>2:
        music_name = sys.argv[2]
    else:
        music_name = "song.mp3"
    
    message_f = open(message_name, "r")
    if message_f:
        text = []
        for line in message_f.readlines():
           text.append(line.strip())
    
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(music_name)
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)
        music = True
        mute = False
    except:
        pass
    pygame.display.set_caption(f'{message_name}')

    display.fill((0, 0, 0))
    yellow = (0, 100, 100)
    #pygame.draw.rect(display, yellow, pygame.Rect(0,0,SCR_SIZE[0],SCR_SIZE[1]))
    sprawl_index = 0
    crawl = 0
    keyup = True
    pygame.key.set_repeat(100)
    
    font = pygame.font.Font(None, 80)
    
    while True:
        if crawl%60==0 and zoom:
            text_surf = font.render(text[sprawl_index], 1, (255, 255, 0))
            display.blit(text_surf, (1,SCR_SIZE[1]-100))
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
                        if music:
                            pygame.mixer.music.pause()
                    else:
                        zoom = 1
                        if music:
                            pygame.mixer.music.unpause()
                elif event.key == pygame.K_s and keyup:
                    keyup = False
                    if shadow:
                        shadow = False
                    else:
                        shadow = True
                elif event.key == pygame.K_m and keyup:
                    keyup = False
                    if music:
                        if mute:
                            pygame.mixer.music.play(-1)
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
                elif event.key == pygame.K_LEFT:
                    if proect_x > MIN_PROECT_X:
                        proect_x -= 5
                elif event.key == pygame.K_RIGHT:
                    if proect_x < MAX_PROECT_X:
                        proect_x += 5
                elif event.key == pygame.K_x:
                    if proect_y > MIN_PROECT_Y:
                        proect_y -= 5
                elif event.key == pygame.K_z:
                    if proect_y < MAX_PROECT_Y:
                        proect_y += 5
            elif event.type == pygame.KEYUP:
                keyup = True
                    

        pygame.display.set_caption(f'{message_name} speed {tick/25.0:.1f} proect_x = {proect_x/100.0} proect_y = {proect_y/100.0} shadow = {shadow} pause = {not zoom} music = {not mute}')
        if zoom>0:
            crawl+=1
            back.blit(display.subsurface(0,1,SCR_SIZE[0],SCR_SIZE[1]-1), (0,0))
            display.blit(back, (0,0))
    	
        frame_tex = surf_to_texture(display)
        frame_tex.use(0)
        program['tex'] = 0
        program['proect_x'] = proect_x/100.0
        program['proect_y'] = proect_y/100.0
        program['shadow_on'] = int(shadow)
        render_object.render(mode=moderngl.TRIANGLE_STRIP)
    
        pygame.display.flip()
    
        frame_tex.release()
    
        clock.tick(tick)
    
