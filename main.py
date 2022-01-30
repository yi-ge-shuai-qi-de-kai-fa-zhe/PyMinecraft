# coding=utf-8
# Always believe,always hope.

#感谢您的遇见！
#本项目（PyMinecraft）GitHub地址：
#https://github.com/chinese-wzq/PyMinecraft
#本项目（PyMinecraft）Gitee地址：
#https://gitee.com/this_is_the_best_name/PyMinecraft
#如果你发现有无良程序员大量盗用本程序代码并且未加声明的
#欢迎你与他对线，并且将他的作品地址发给我（让我康康啊♂）
#以下为程序声明以及一些介绍，如果有不符合规范的欢迎提出拉取请求，我不懂开源协议，太多了QAQ

#本程序使用字体：JetBrains Mono，字体不同可能会出现程序内的注释排版紊乱！

#本程序部分行较长。为什么？因为觉得这样很爽（莫名）

################################################
#                本作品为兴趣使然                 #
#             我并没有收过任何人的钱财              #
#             也没有与任何人有契约关系              #
#     本作品与MOJANG工作室（BUGJUMP）没有任何关系    #
#     我从来没有查看过Minecraft的源码（反正看不懂）   #
#      本作品仅供学习、娱乐，商用请注明项目地址        #
#        欢迎提交拉取请求，这是对我最大的支持         #
#    我也只是一个小小的初二生，很多数学计算略为粗糙     #
#            因此希望您帮助改进我的算法             #
################################################
#            本游戏是开源的，所有人可编辑           #
#           因此，我才能尽量保证代码的安全性         #
#          本游戏从设计之初就采用了超多函数设置       #
#          这使得游戏的大部分函数具有参考价值        #
#             如果本游戏的某些函数帮到了您          #
#        欢迎您在项目地址上点一个免费的Star（星）     #
#             你的星会成为我Coding的动力           #
################################################

#################感谢与你相遇！###################

#导入OpenGL相关库
import numpy
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
#导入字体显示相关库(即将废弃)
from OpenGL.WGL import *
import win32ui
#导入三角函数相关库
import math
#导入窗口相关库
import win32con,win32gui
#导入区块读取相关库
import json,os,copy
#导入方块贴图生成库
from PIL import Image
from PIL import ImageDraw
#导入字体点阵获取相关库
from freetype import *

#允许用户自定义的变量,已将大部分变量做好注释

mouse_move_speed=0.01 #鼠标移动距离
player_move_speed=0.1
look_length=15  #渲染距离,只支持不小于1的奇数
highest_y=100  #世界最高Y坐标
lowest_y=0   #世界最低Y坐标，目前如果更改将会报错！
player_x=0    #这几个不必细说，都懂都懂
player_y=-1
player_z=-1
font="C:/WINDOWS/Fonts/msyh.ttc"    #显示文字时使用的字体,需完整路径
window_height=400    #窗口的长和宽
window_width=400
set_chat_list_show_time=50      #聊天框显示多久，2/3时间不变，1/3时间淡化消失
saves_folder_dir=".\\saves\\"   #指定了存储所有存档的文件夹的位置
save_folder_dir=".\\saves\\example\\"   #指定了存储单个存档的文件夹的位置
load_all_save=False   #在启动时就加载所有的区块，并且不会执行卸载和加载的程序，可以减少程序卡顿，但在存档过大时需谨慎开启

#用户不应该动的变量
save_folder_files_list=os.listdir(save_folder_dir)
player_see_x=0
player_see_y=0
lock_muose=False
debug=False
map=[]
block_texture=[]
debug_text=[['XYZ:',0.0,',',0.0,',',0.0],
            ['EYE:',0,',',0],]
block_size=11   #必须为单数
buffer_block_size=15   #也必须为单数
temp1=block_size/2#区块加载的缓存变量
temp2=(buffer_block_size-1)/2
temp7=(block_size-1)/-2
keyboard={}
for i in [b'\x1b',b'`',b'w',b's',b'a',b'd',b" "]:keyboard[i]=False
mouse={0:1,2:1}
input_text=False
input_buffer=""
chat_list=[]
chat_list_show_time=0
guide_buttons=[]
def create_block_texture(block_type:int):#没错，方块材质直接现画！
    block=Image.new("RGB",(100,100),"white")
    draw=ImageDraw.Draw(block)
    if block_type==1:draw.line([5,5,5,95,95,95,95,5,5,5],(0,255,0),10)
    pixels=block.load()
    all_pixels=[]
    for x in range(100):
        for y in range(100):all_pixels+=list(pixels[x,y])
    return bytes(all_pixels)
block_texture.append(create_block_texture(1))
def float2int(i):return int(str(i).split(".")[0])
def write_list(wait_write_list:list,write:str,point:list,fill:any=0,fill_callback=None):#代码再不重写就TM要爆炸了
    really_point=wait_write_list
    for i in range(len(point)):
        while point[i]>len(really_point)-1:
            if fill_callback is None:really_point.append(copy.copy(fill))
            else:really_point.append(fill_callback(i,point))
        if i==len(point)-1:
            really_point[point[i]]=write
            return wait_write_list
        really_point=really_point[point[i]]
#如果设置为加载全部区块，则进行一些操作
if load_all_save:
    for i in save_folder_files_list:
        a,b=i.split(",")
        a=int(a)
        b=int(b)
        with open(save_folder_dir+str(a)+','+str(b)) as f: map=write_list(map,json.load(f),[a>=0,a+int(a<0),b>=0,b+int(b<0)],fill=[])
def read_block(x:int,y:int,z:int):#此模块包装了读取方块的代码,未来可能也会把世界生成的代码放里边！
    #以下为基本原理：
    #1.先计算输入坐标位于的区块位置
    #2.读取区块文件，并将区块放入map进行缓存
    #                               ↑
    #将区块放入缓存中，并卸载超出缓存区域的区块，关于map的区块索引结构结构：（存在负数，每层需要两层，一层正一层负）
    #                                                         第一层：区块的X
    #                                                         第二层：区块的Z
    #                                                         此索引方法虽然会出现许多空的项，但是比全部载入对内存的消耗少得多了
    #3.从区块里读取指定位置方块,索引方法：（不存在负数情况），随后返回指定位置方块
    #                              第一层：Y
    #                              第二层：X
    #                              第二层：Z
    global map
    #第一步
    i=1
    ii=1
    if x<0:i=-1
    if z<0:ii=-1
    block_X=float2int((x+temp1*i)/block_size)
    block_Z=float2int((z+temp1*ii)/block_size)
    #第二步，这里决定先卸载再载入
    temp3=block_X>=0
    temp4=block_X+int(block_X<0)
    temp5=block_Z>=0
    temp6=block_Z+int(block_Z<0)
    if not load_all_save:
        for i in range(len(map)):
            for ii in range(len(map[i])):
                for iii in range(len(map[i][ii])):
                    for iiii in range(len(map[i][ii][iii])):
                        if i>0:a=ii
                        else:a=ii*-1-1
                        if iii>0:aa=iiii
                        else:aa=iiii*-1-1
                        if not block_X-temp2<=a<=block_X+temp2 or not block_Z-temp2<=aa<=block_Z+temp2:
                            with open(save_folder_dir+str(a)+","+str(aa),"w") as f:json.dump(map[i][ii][iii][iiii],f)#这里有bug哈
                            map[i][ii][iii][iiii]=0
        try:
            if not map[temp3][temp4][temp5][temp6]:raise IndexError
        except IndexError:
            if str(block_X)+','+str(block_Z) in save_folder_files_list:
                with open(save_folder_dir+str(block_X)+','+str(block_Z)) as a:map=write_list(map,json.load(a),[temp3,temp4,temp5,temp6],[])
            else:
                return 0
    #第三步
    #    v4----- v5
    #   /|      /|
    #  v0------v1|
    #  | |↗    | |
    #  | v7----|-v6
    #  |/      |/
    #  v3------v2→
    #目标就是先求出区块中心，随后求出V3这个点的位置，最后换算坐标进入区块坐标系
    center_block_x=(block_X-0.5)*block_size
    center_block_z=(block_Z-0.5)*block_size
    try:return map[temp3][temp4][temp5][temp6][y][float2int(x-center_block_x)][float2int(z-center_block_z)]
    except IndexError:return 0
def write_block_fill_callback(a,b):
    if a==len(b)-1:return 0
    else:return []
def write_block(x:int,y:int,z:int,write:int):
    global map
    #第一步
    i=1
    ii=1
    if x<0:i=-1
    if z<0:ii=-1
    block_X=float2int((x+temp1*i)/block_size)
    block_Z=float2int((z+temp1*ii)/block_size)
    temp3=block_X>=0
    temp4=block_X+int(block_X<0)
    temp5=block_Z>=0
    temp6=block_Z+int(block_Z<0)
    center_block_x=(block_X-0.5)*block_size
    center_block_z=(block_Z-0.5)*block_size
    map=write_list(map,write,[temp3,temp4,temp5,temp6,y,float2int(x-center_block_x),float2int(z-center_block_z)],fill_callback=write_block_fill_callback)
draw=False
block_VAO=0
block_VBO_buffer_len=0
texture_VBO=0
def print_blocks(sx:int,sy:int,sz:int):#这里将来会选择性显示方块，不会全部显示一遍，多伤显卡QAQ
    #特别鸣谢：Stack Overflow用户Rabbid76
    #没有他回答了我两个问题，我这一辈子都做不出来
    #问题链接：
    #https://stackoverflow.com/questions/70476151/opengl-vbo-can-run-without-error-but-no-graphics
    #https://stackoverflow.com/questions/70610206/opengl-vbo-vao-ebo-can-run-without-error-but-no-graphics
    #https://stackoverflow.com/questions/70844191/pyopengl-run-with-no-texture
    #虽然他别没有叫我贴上这个注释，不过我想，做人要学会感恩😀
    global draw,block_VAO,block_VBO_buffer_len,texture_VBO
    if not draw:
        block_point_buffer=[]
        block_color_buffer=[]
        texture_coord=[]
        for y in range(lowest_y,highest_y+1):
            for x in range(sx-int((look_length-1)/2),sx+int((look_length-1)/2)+1):
                for z in range(sz-int((look_length-1)/2),sz+int((look_length-1)/2)+1):
                    by_wzq=read_block(x,y,z)
                    if not by_wzq==0:
                        #图盗的
                        #    v4----- v5
                        #   /|      /|
                        #  v0------v1|
                        #  | |     | |
                        #  | v7----|-v6
                        #  |/      |/
                        #  v3------v2
                        block_point_buffer+=[x-0.5,y+0.5,z-0.5,  #V0
                                             x+0.5,y+0.5,z-0.5,  #V1
                                             x+0.5,y+0.5,z+0.5,  #V5
                                             x-0.5,y+0.5,z+0.5,  #V4

                                             x-0.5,y-0.5,z-0.5,  #V3
                                             x+0.5,y-0.5,z-0.5,  #V2
                                             x+0.5,y-0.5,z+0.5,  #V6
                                             x-0.5,y-0.5,z+0.5,  #V7

                                             x+0.5,y-0.5,z-0.5,  #V2
                                             x+0.5,y-0.5,z+0.5,  #V6
                                             x+0.5,y+0.5,z+0.5,  #V5
                                             x+0.5,y+0.5,z-0.5,  #V1

                                             x-0.5,y-0.5,z-0.5,  #V3
                                             x-0.5,y-0.5,z+0.5,  #V7
                                             x-0.5,y+0.5,z+0.5,  #V4
                                             x-0.5,y+0.5,z-0.5,  #V0

                                             x-0.5,y-0.5,z-0.5,  #V3
                                             x+0.5,y-0.5,z-0.5,  #V2
                                             x+0.5,y+0.5,z-0.5,  #V1
                                             x-0.5,y+0.5,z-0.5,  #V0

                                             x-0.5,y-0.5,z+0.5,  #V7
                                             x+0.5,y-0.5,z+0.5,  #V6
                                             x+0.5,y+0.5,z+0.5,  #V5
                                             x-0.5,y+0.5,z+0.5,] #V4
                        block_color_buffer+=(0.0,0.0,0.0)*6
                        texture_coord+=[1.0,1.0,
                                        0.0,1.0,
                                        0.0,0.0,
                                        1.0,0.0]*6
        #创建顶点VBO
        block_VBO=glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,block_VBO)
        a=numpy.array(block_point_buffer,dtype='float32')
        glBufferData(GL_ARRAY_BUFFER,sys.getsizeof(a),a,GL_STATIC_DRAW)
        block_VBO_buffer_len=int(len(a)/3)
        #创建纹理VBO
        texture_VBO=glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,texture_VBO)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,100,100,0,GL_RGB,GL_UNSIGNED_BYTE,block_texture[0])
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D,0)
        #创建纹理指针
        texture_EBO=glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,texture_EBO)
        a=numpy.array(texture_coord,dtype='float32')
        glBufferData(GL_ARRAY_BUFFER,sys.getsizeof(a),a,GL_STATIC_DRAW)
        #绑定VAO
        block_VAO=glGenVertexArrays(1)
        glBindVertexArray(block_VAO)
        #绑定顶点VBO
        glBindBuffer(GL_ARRAY_BUFFER,block_VBO)
        glVertexPointer(3,GL_FLOAT,0,None)
        glEnableClientState(GL_VERTEX_ARRAY)
        #绑定纹理VBO
        glBindBuffer(GL_ARRAY_BUFFER,texture_EBO)
        glTexCoordPointer(2,GL_FLOAT,0,None)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        #解绑
        glBindVertexArray(0)
        draw=True
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D,texture_VBO)
    glBindVertexArray(block_VAO)
    glColor3ub(255,255,255)
    glDrawArrays(GL_QUADS,0,block_VBO_buffer_len)
    glBindVertexArray(0)
class GetCharacterImage:
    def __init__(self,buffer=False):
        self.__bitmap=None
        self.bitmap=None
        self.size_buffer=None
        self.rows=None
        self.face=Face(font)
        self.load=False
        self.buffer=buffer
        if self.buffer:self.characters_buffer={}
    def get_size(self):
        if self.load:
            if self.buffer:return self.size_buffer
            return self.rows,self.__bitmap.width
        else:raise Exception("在创建字符前获取大小")
    def character2types(self,character,size,color,all_row,except_character=(",","，","。",".")):
        """
        :param character: 仅支持单个字符
        :param size: 大小
        :param color: 颜色
        :param all_row: 自动补齐高度，使文字在图像中间
        :param except_character: 不补行的字符元组
        :return: 可以被opengl读取的格式
        """

        if self.buffer and character+str(size) in self.characters_buffer:
            self.size_buffer=self.characters_buffer[character+"_size"]
            return self.characters_buffer[character+str(size)]
        self.face.set_char_size(size*64)
        self.face.load_char(character)
        self.__bitmap=self.face.glyph.bitmap
        bitmap_buffer=self.__bitmap.buffer
        self.load=True
        bitmap__temp=[]
        self.bitmap=[]
        temp=(self.__bitmap.rows,self.__bitmap.width)
        #补行
        if len(bitmap_buffer)<all_row*temp[1] and character not in except_character:
            self.rows=all_row
            #按照指定长度切割列表
            for i in range(temp[0]):bitmap__temp.append(list(bitmap_buffer[i*temp[1]:(i+1)*temp[1]]))
            on_rows=float2int((all_row-len(bitmap__temp))/2)
            under_rows=all_row-len(bitmap__temp)-on_rows
            for _ in range(on_rows):bitmap__temp.insert(0,list([0]*temp[1]))
            for _ in range(under_rows): bitmap__temp.append(list([0]*temp[1]))
            #合并列表
            debug=len(bitmap__temp)
            for _ in range(len(bitmap__temp)-1):
                bitmap__temp[0]+=bitmap__temp[1]
                bitmap__temp.pop(1)
            bitmap__temp=bitmap__temp[0]
        else:
            bitmap__temp=bitmap_buffer
            self.rows=self.__bitmap.rows
        for i in bitmap__temp:self.bitmap+=list(color)+[i]
        if self.buffer:
            self.characters_buffer[character+str(size)]=bytes(self.bitmap)
            self.characters_buffer[character+"_size"]=[self.rows,self.__bitmap.width]
            self.size_buffer=self.characters_buffer[character+"_size"]
            return self.characters_buffer[character+str(size)]
        return bytes(self.bitmap)
character_getter=GetCharacterImage()
class PrintText:
    def __init__(self):
        self.texture_buffer={}
    def print_freetype_2d(self,text:list,x=0,y=0,z=0,m=1,color=(0,0,0),size=24,spacing=2,all_row=20,buffer=True):#采用freetype+texture，更方便自定义，字体更好看！
        global character_getter
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        for i in text:
            qaq=0
            dx=x
            if i=="": i=" "
            for ii in "".join([str(x) for x in i]):#需要进行特殊处理
                if ii==" ":
                    a=(all_row,float2int(9/24*size))
                    if a[0]>qaq: qaq=a[0]
                    dx+=a[1]+spacing
                    continue
                if buffer and ii+str(size)+str(color)+str(all_row) in self.texture_buffer:
                    a=self.texture_buffer[ii+str(size)+str(color)+str(all_row)+"_size"]
                    glBindTexture(GL_TEXTURE_2D,self.texture_buffer[ii+str(size)+str(color)+str(all_row)])
                else:
                    texture=glGenTextures(1)
                    glBindTexture(GL_TEXTURE_2D,texture)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
                    aa=character_getter.character2types(ii,size=size,color=color,all_row=all_row)
                    a=character_getter.get_size()
                    glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,a[1],a[0],0,GL_RGBA,GL_UNSIGNED_BYTE,aa)
                    glGenerateMipmap(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D,0)
                    if buffer:
                        self.texture_buffer[ii+str(size)+str(color)+str(all_row)]=texture
                        self.texture_buffer[ii+str(size)+str(color)+str(all_row)+"_size"]=a
                    glBindTexture(GL_TEXTURE_2D,texture)
                if a[0]>qaq: qaq=a[0]
                glBegin(GL_QUADS)
                glTexCoord2f(1,1)
                glVertex3f(dx+a[1],y,z)
                glTexCoord2f(0,1)
                glVertex3f(dx,y,z)
                glTexCoord2f(0,0)
                glVertex3f(dx,y+a[0],z)
                glTexCoord2f(1,0)
                glVertex3f(dx+a[1],y+a[0],z)
                glEnd()
                dx+=a[1]+spacing
            y+=qaq*m
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
text_printer=PrintText()
def debug_3d():
    if debug:
        #显示一个世界原点的坐标系
        glLineWidth(1)
        glBegin(GL_LINES)
        glColor3ub(0,0,255)
        glVertex3f(0,0,0)
        glVertex3f(1,0,0)
        glColor3ub(0,255,0)
        glVertex3f(0,0,0)
        glVertex3f(0,1,0)
        glColor3ub(255,0,0)
        glVertex3f(0,0,0)
        glVertex3f(0,0,1)
        glEnd()
        #显示坐标系文字（方便与MC原版进行矫正）
        hDC=wglGetCurrentDC()
        #设定文字的字体、颜色和背景
        win32gui.SelectObject(hDC,win32ui.CreateFont({"height":0,"width":0,"name":font}).GetSafeHandle())
        win32gui.SetBkMode(hDC,win32con.TRANSPARENT)
        glColor3ub(0,0,0)
        a=glGenLists(1)
        glRasterPos3f(1,0,0)
        wglUseFontBitmapsW(hDC,ord('x'),1,a)
        glCallList(a)
        glRasterPos3f(0,1,0)
        wglUseFontBitmapsW(hDC,ord('y'),1,a)
        glCallList(a)
        glRasterPos3f(0,0,1)
        wglUseFontBitmapsW(hDC,ord('z'),1,a)
        glCallList(a)
        win32gui.DeleteObject(hDC)
def debug_2d():
    global debug_text
    if debug:
        #更新调试信息
        a=debug_text[0]
        a[1]=round(player_x,2)
        a[3]=round(player_y,2)
        a[5]=round(player_z,2)
        debug_text[0]=a
        a=debug_text[1]
        a[1]=round(player_see_x,2)
        a[3]=round(player_see_y,2)
        debug_text[1]=a
        #调用文字显示函数显示debug内容，并顺便打印文字出来
        text_printer.print_freetype_2d(debug_text,y=780,m=-1)
def view_orientations(px,py,callback=None):
    #我还没有学过三角函数，因此如果输入负数也能正常使用，以下代码可以更加简洁。请帮忙改一改哈😀
    if callback is not None:
        px,py=callback(px,py)
    if px>=0:
        if px>90:
            x=math.cos(px-90)
            z=math.sin(px-90)*-1
        else:
            x=math.sin(px)
            z=math.cos(px)
    else:
        if px<-90:
            x=math.cos((px+90)*-1)*-1
            z=math.sin((px+90)*-1)*-1
        else:
            x=math.sin(px*-1)*-1
            z=math.cos(px*-1)
    if py>=0:
        y=math.sin(py)
    else:
        y=math.sin(py*-1)*-1
    return x,y,z
def world_main_loop():
    global input_text,chat_list_show_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-0.3,0.3,-0.3,0.3,0.1,8)
    #笔记：
    #glFrustum(left,right,bottom,top,zNear,zFar)
    #这个函数的参数只定义近裁剪平面的左下角点和右上角点的三维空间坐标，即(left，bottom，-near)和(right，top，-near)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #计算视角望向的位置
    x,y,z=view_orientations(player_see_x,player_see_y)
    gluLookAt(
        player_x,player_y+1,player_z,
        player_x+x,player_y+y+1,player_z+z,
        0,1,0
    )
    #渲染方块
    print_blocks(int(player_x),int(player_y),int(player_z))
    #显示选中的方块
    #    v4----- v5
    #   /|      /|
    #  v0------v1|
    #  | |     | |
    #  | v7----|-v6
    #  |/      |/
    #  v3------v2
    i=mouse_hit_test()[0]
    if i!=[1]:
        x,y,z=i
        a=[x-0.5,y+0.5,z-0.5,  #V0
           x+0.5,y+0.5,z-0.5,  #V1
           x+0.5,y-0.5,z-0.5,  #V2
           x-0.5,y-0.5,z-0.5,  #V3
           x-0.5,y+0.5,z+0.5,  #V4
           x+0.5,y+0.5,z+0.5,  #V5
           x+0.5,y-0.5,z+0.5,  #V6
           x-0.5,y-0.5,z+0.5,] #V7
        b=[0,3,1,2,5,6,4,7,0,1,4,5,7,6,3,2,0,4,1,5,2,6,3,7]
        glLineWidth(5)
        glBegin(GL_LINES)
        glColor3ub(232,232,232)
        for i in range(int(len(b)/2)):
            glVertex3f(a[b[i*2]*3],a[b[i*2]*3+1],a[b[i*2]*3+2])
            glVertex3f(a[b[i*2+1]*3],a[b[i*2+1]*3+1],a[b[i*2+1]*3+2])
        glEnd()
    debug_3d()
    #进入2D状态
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,window_height*2,0,window_width*2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #显示指针
    glLineWidth(2)
    glBegin(GL_LINES)
    glColor3ub(232,232,232)
    glVertex2f(400,425)
    glVertex2f(400,375)
    glVertex2f(425,400)
    glVertex2f(375,400)
    glEnd()
    #调试模式
    debug_2d()
    #显示指令栏
    if chat_list_show_time!=0 and not input_text:
        chat_list_show_time-=1
        if set_chat_list_show_time/3*1<chat_list_show_time:text_printer.print_freetype_2d([input_buffer]+chat_list)
        else:
            a=int(255/(set_chat_list_show_time/3*1)*(set_chat_list_show_time/3*1-(set_chat_list_show_time/3*1)+chat_list_show_time))
            glColor4ub(255,255,255,a)
            text_printer.print_freetype_2d([input_buffer]+chat_list)
    if input_text:text_printer.print_freetype_2d([input_buffer]+chat_list)
    #交换缓存，显示画面
    glutSwapBuffers()
def walk_left(a,b):return a+1.57,b#1.57是实测出来的数据~
def spectator_mode(button):
    global player_x,player_y,player_z
    if button in [b'w',b's']:
        x,y,z=view_orientations(player_see_x,player_see_y)
        if button==b's':
            x*=-1
            y*=-1
            z*=-1
    else:
        x,y,z=view_orientations(player_see_x,player_see_y,walk_left)
        if button==b'd':
            x*=-1
            z*=-1
        y=0
    player_x+=x*player_move_speed
    player_y+=y*player_move_speed
    player_z+=z*player_move_speed
    glutPostRedisplay()
def run_command(command):#名义上叫做运行指令，实际上负责了聊天框输入事件处理的全部
    global chat_list,chat_list_show_time,draw
    if command[0]=="/":
        #对输入进行拆分
        command_split=command[1:].split(' ')
        if command_split[0]=="fill":
            write_block(int(command_split[1]),int(command_split[2]),int(command_split[3]),int(command_split[4]))
            draw=False
        if command_split[0]=="tp":
            global player_x,player_y,player_z
            player_x=float(command_split[1])
            player_y=float(command_split[2])
            player_z=float(command_split[3])
    chat_list=[input_buffer]+chat_list
    chat_list_show_time=set_chat_list_show_time
def lock_or_unlock_mouse(a):
    global lock_muose
    if a:
        lock_muose=False
        glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
    else:
        glutWarpPointer(window_height,window_width)
        lock_muose=True
        glutSetCursor(GLUT_CURSOR_NONE)
        glutPostRedisplay()
def mouse_hit_test():
    #感谢开源项目https://github.com/fogleman/Minecraft提供的函数思路！
    m=8#精度
    x,y,z=player_x,player_y+1,player_z
    x_vector,y_vector,z_vector=view_orientations(player_see_x,player_see_y)
    free_block=0
    for _ in range(int(60*m)):
        free_block=float2int(x),float2int(y),float2int(z)
        x,y,z=x+x_vector/m,y+y_vector/m,z+z_vector/m
        if y<lowest_y-0.5:return [1],[1]
        if read_block(float2int(x),float2int(y),float2int(z))!=0:
            return (float2int(x),float2int(y),float2int(z)),free_block
    return [1],[1]
def world_mouseclick(button,state,x,y):
    global mouse,draw
    if not mouse[2]:
        i=mouse_hit_test()[1]
        if i!=[1]:
            write_block(i[0],i[1],i[2],1)
            draw=False
    if not mouse[0]:
        i=mouse_hit_test()[0]
        if i!=[1]:
            write_block(i[0],i[1],i[2],0)
            draw=False
    mouse[button]=state
def keyboarddown(button,x,y):
    global keyboard,input_text,input_buffer,debug,lock_muose,player_y
    if input_text:
        if button==b'\r':
            input_text=False
            run_command(input_buffer)
            input_buffer=""
            lock_or_unlock_mouse(False)
        elif button==b'\x1b':
            input_text=False
            input_buffer=""
            lock_or_unlock_mouse(False)
        elif button==b'\x08':input_buffer=input_buffer[:-1]
        else:input_buffer+=button.decode()
        glutPostRedisplay()
    else:
        if not keyboard[b'\x1b'] and button==b'\x1b':lock_or_unlock_mouse(lock_muose)#锁定或非锁定状态
        elif not keyboard[b'`'] and button==b'`':#调试模式
            if debug:debug=False
            else:debug=True
            glutPostRedisplay()
        elif button==b'/':
            input_text=True
            lock_or_unlock_mouse(True)
            input_buffer="/"
            glutPostRedisplay()
            return 0
        elif button==b't':
            input_text=True
            lock_or_unlock_mouse(True)
            glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
            glutPostRedisplay()
            return 0
        keyboard[button]=True
def keyboardup(button,x,y):
    global keyboard
    keyboard[button]=False
def world_mousemove(x,y):
    global player_see_x,player_see_y
    if lock_muose and window_height!=x and window_width!=y:
        player_see_x=(window_height-x)*mouse_move_speed+player_see_x
        player_see_y=(window_width-y)*mouse_move_speed+player_see_y
        #这里增加了数值限制，防止过头，因为是实测的数据，可能有不准，见谅~
        if player_see_y>2:player_see_y=2
        if player_see_y<-2:player_see_y=-2
        if player_see_x>3:player_see_x-=6
        if player_see_x<-3: player_see_x+=6
        glutWarpPointer(window_height,window_width)
        glutPostRedisplay()
def backgroud():
    global keyboard,player_y
    #键盘
    for i in [b'w',b's',b'a',b'd']:
        if keyboard[i]:spectator_mode(i)
    if keyboard[b' ']:
        player_y+=0.1
        glutPostRedisplay()
    #聊天框淡化事件，必须要激活
    if chat_list_show_time!=0 and not input_text:glutPostRedisplay()
def guide_button_event_init():
    global guide_buttons
    guide_buttons=[]
def guide_main_loop():
    glClear(GL_COLOR_BUFFER_BIT)
    # glColor3f(1.0,0.0,0.0)
    # glRectf(-0.5,-0.5,0.5,0.5)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,window_height*2,0,window_width*2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    PrintText.print_text_list_freetype(["PyMinecraft+-"],x=0,y=400,size=96)
    glutSwapBuffers()
def guide_init():#处理情况：游戏退出到主界面，其他界面退出到主界面
    glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
    glutIdleFunc(nothing)
    glutPassiveMotionFunc(nothing)
    glutMouseFunc(nothing)
    glMatrixMode(GL_MODELVIEW)
    glLoadMatrixd(init_info[0])
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixd(init_info[1])
    glutDisplayFunc(guide_main_loop)
def go_to_world():
    glViewport(0,0,window_height*2,window_width*2)
    glutSetCursor(GLUT_CURSOR_NONE)
    glutDisplayFunc(world_main_loop)
    glutIdleFunc(backgroud)
    glutPassiveMotionFunc(world_mousemove)
    glutMouseFunc(world_mouseclick)
def nothing(*args):pass
def init():
    #进行glut的最基础初始化
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_DEPTH|GLUT_RGBA)
    glutCreateWindow("PyMinecraft ByWzq".encode('GBK',errors="replace"))
    #使用户无法更改窗口大小
    hwnd=win32gui.GetForegroundWindow()
    A=win32gui.GetWindowLong(hwnd,win32con.GWL_STYLE)
    A^=win32con.WS_THICKFRAME
    win32gui.SetWindowLong(hwnd,win32con.GWL_STYLE,A)
    #完成其余的初始化
    glutReshapeWindow(window_height*2,window_width*2)
    glClearColor(0.0,174.0,238.0,238.0)
init()
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)
glutKeyboardFunc(keyboarddown)
glutKeyboardUpFunc(keyboardup)
init_info=(glGetDoublev(GL_MODELVIEW_MATRIX),glGetDoublev(GL_PROJECTION_MATRIX))
#guide_init()
go_to_world()
glutMainLoop()#正式开始运行
