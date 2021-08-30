# coding=utf-8
# 不会吧不会吧还有人不知道UTF-8??????
#导入OpenGL相关库
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
#导入字体显示相关库
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import random
#允许用户自定义的变量
move_speed=0.01 #鼠标移动距离
look_length=9  #渲染距离,只支持不小于1的奇数
highest_y=100
lowest_y=0
player_x=0
player_y=0
player_z=-1
font="msyh.ttc"

#用户不应该动的变量
player_see_x=0#为了以后的更新做好准备
player_see_y=0
lock_muose=False
mouse_should_move_pos=(0,0)
mouse_fix_No1=5
debug=True
map=[[],[[[],[[[],[1]]]]]]
block_color=[(50,205,50)]
def generate_text_image(text:str,color:str,size:int):
    global font,debug
    Wzq_NB=ImageFont.truetype(font,size)
    size=Wzq_NB.getsize(text)
    wzq=Image.new("RGBA",size)
    picture=ImageDraw.Draw(wzq)
    picture.text((0,0),text,font=Wzq_NB,fill=color)
    a=np.ravel(wzq)
    c=np.split(a,[size[0]*4],axis=0)
    A=list(np.concatenate(c))
    if debug:
        c.reverse()
        print("e")
    rgba=list(np.concatenate(c))
    return bytes(rgba),Wzq_NB.getsize(text)
def debug_main():
    global debug
    #if debug:
    global player_see_x,player_see_y
    mua=generate_text_image("E:"+str(int(player_see_x))+";"+str(int(player_see_y)),"gray",50)
    glDrawPixels(mua[1][0],mua[1][1],GL_RGBA,GL_UNSIGNED_BYTE,mua[0])
def find_block(x:int,y:int,z:int):
    global map
    try:
        return map[x>=0][abs(x)][y>=0][abs(y)][z>=0][abs(z)]
    except:
        return 0
def print_blocks(sx:int,sy:int,sz:int):
    global look_length,highest_y,lowest_y,block_color
    by_13905069=(sx-int((look_length-1)/2),sx+int((look_length-1)/2)+1)
    for x in range(by_13905069[0],by_13905069[1]):
        for y in range(lowest_y,highest_y+1):
            for z in range(by_13905069[0],by_13905069[1]):
                by_wzq=find_block(x,y,z)
                if not by_wzq==0:
                    #这里先粗略写一下
                    #    v4----- v5
                    #   /|      /|
                    #  v0------v1|
                    #  | |     | |
                    #  | v7----|-v6
                    #  |/      |/
                    #  v3------v2
                    #盗图大师
                    color=block_color[by_wzq-1]
                    glBegin(GL_QUAD_STRIP)
                    glColor3ub(color[0],color[1],color[2])
                    glVertex3f(x-0.5,y+0.5,z-0.5)#V0
                    glVertex3f(x+0.5,y+0.5,z-0.5)#V1
                    glVertex3f(x-0.5,y-0.5,z-0.5)#V3
                    glVertex3f(x+0.5,y-0.5,z-0.5)#V2
                    glVertex3f(x+0.5,y-0.5,z+0.5)#V6
                    glVertex3f(x-0.5,y-0.5,z+0.5)#V7
                    # glVertex3f(x-0.5,y+0.5,z-0.5)#V0
                    # glVertex3f(x+0.5,y+0.5,z-0.5)#V1
                    # glVertex3f(x+0.5,y+0.5,z+0.5)#V5
                    # glVertex3f(x-0.5,y+0.5,z+0.5)#V4

                    # glVertex3f(x-0.5,y-0.5,z-0.5)#V3
                    # glVertex3f(x+0.5,y-0.5,z-0.5)#V3
                    glEnd()
def draw():
    global player_see_x,player_see_y,player_x,player_y,player_z
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(0.3,-0.3,0.3,-0.3,0.1,1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        player_x,player_y+1,player_z,
        player_see_x,player_see_y,0,
        0,1,0
    )
    #渲染方块
    print_blocks(player_x,player_y,player_z)
    #渲染结束
    #调试模式
    debug_main()
    glutSwapBuffers()
def keyboardchange(button,x,y):#实现暂停、视角的前进与后退等功能
    if button==b'\x1b':#是否开启鼠标控制
        global lock_muose,mouse_fix_No1,mouse_should_move_pos
        if lock_muose:
            lock_muose=False
            glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
        else:
            glutWarpPointer(mouse_should_move_pos[0],mouse_should_move_pos[1])
            lock_muose=True
            mouse_fix_No1=1
            glutSetCursor(GLUT_CURSOR_NONE)
            glutPostRedisplay()
    elif button==b'`':#调试模式
        global debug
        if debug:debug=False
        else:debug=True
    else:
        print(button)
def change(x,y):
    global mouse_should_move_pos
    mouse_should_move_pos=(400,400)
    glutPostRedisplay()#没了它，拉动窗口图形就会变形
def mousemove(x,y):
    global lock_muose,mouse_fix_No1
    if lock_muose and mouse_fix_No1==5:
        global move_speed,mouse_should_move_pos,player_see_x,player_see_y
        #这里重写了一下，为了以后的更新做准备
        player_see_x=(x-mouse_should_move_pos[0])*move_speed+player_see_x
        player_see_y=(y-mouse_should_move_pos[1])*move_speed+player_see_y
        glutWarpPointer(mouse_should_move_pos[0],mouse_should_move_pos[1])
        mouse_fix_No1=1
        glutPostRedisplay()
        return 0
    mouse_fix_No1+=1
def draw_main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutCreateWindow("Minecraft 重置版 ByWzq".encode('GBK',errors="replace"))
    glutSetCursor(GLUT_CURSOR_NONE)
    glutReshapeWindow(800,800)
    glViewport(0,0,800,800)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glutDisplayFunc(draw)
    glutReshapeFunc(change)#在每次拉动窗口的时候重新渲染
    glutKeyboardFunc(keyboardchange)
    glutPassiveMotionFunc(mousemove)
    glutMainLoop()
draw_main()
#generate_text_image(".","blue",100)