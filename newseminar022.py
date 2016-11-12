#!/usr/bin/env python

'''
Seminar v0.2 - an attempt to rewrite the Seminar game from scratch.

by Takis Tsiberis
http://takira.freehosting.net/
takira_gr@yahoo.com

Started coding at 1/20/2007 - mostly on weekends
Finished at 5/16/2007

Copyright (C) 2007 Panagiotis Tsiberis
This program is free software;
you can redistribute it and/or
modify it under the terms of the
GNU General Public License
as published by the
Free Software Foundation;
either version 2 of the License,
or (at your option) any later version.

This version works for both Linux and Windows.

Version 0.2.1:
The "pygame.mixer.music.pause()" and "pygame.mixer.music.unpause()"
functions do not "function" on windows so this is definitely a bug.

Version 0.2.1.1:
Fixed a minor mistake.

Version 0.2.2:
The code had some good bugs.
'''

#-------------------Imports-------------------
import pygame
from pygame.locals import *
from os import path
from sys import platform

#-------------------Constants-------------------
VERSION = '0.2.2'
SIZE = (800,600)
WHITE = (255,255,255)
BLACK = (0,0,0)
PASTEL_YELLOW = (255,255,155)
LIGHT_GREY = (220,220,220)
_FONT = 'VeraSe.ttf'
data_folder = 'newseminar_data'
PLATFORM = platform

#-------------------Global functions-------------------
def load_image(name, colorkey=None):
    fullname = path.join(data_folder, name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is -1:
        colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def display_some_text(text,size,p,b,centered=0):
    font = pygame.font.Font(path.join(data_folder,_FONT), size)
    t = font.render(text, 1, BLACK)
    tpos = t.get_rect()
    if centered:
        tpos.centerx = p[0]
        tpos.centery = p[1]
    else:
        tpos.left = p[0]
        tpos.top = p[1]
    b.blit(t, tpos)

def find_other_squares(j,k):
    _list = []
    if 0 <= j-3: _list.append((j-3,k))
    if 0 <= j-2 and k+2 <= 10: _list.append((j-2,k+2))
    if k+3 <= 10: _list.append((j,k+3))
    if j+2 <= 9 and k+2 <= 10: _list.append((j+2,k+2))
    if j+3 <= 9: _list.append((j+3,k))
    if j+2 <= 9 and 1 <= k-2: _list.append((j+2,k-2))
    if 1 <= k-3: _list.append((j,k-3))
    if 0 <= j-2 and 1 <= k-2: _list.append((j-2,k-2))
    return _list

#-------------------Classes-------------------
class simple_button(pygame.sprite.Sprite):
    def __init__(self,x,y,title,screen,background):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('button2.png')
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.status = 0
        # Draw some shadow lines
        background.lock()
        pygame.draw.line(background,BLACK,(x+1,y+self.rect.height),\
                         (x+self.rect.width-1,y+self.rect.height))
         #horizontal
        pygame.draw.line(background,BLACK,(x+self.rect.width,y+1),\
                         (x+self.rect.width,y+self.rect.height))
         #vertical
        background.unlock()
        # Display some text
        display_some_text(title,24,(60,20),self.image,1)
        background.blit(self.image,self.rect)
    def press(self):
        self.rect.inflate_ip(-2,-2)
        self.status = 1
    def unpress(self):
        self.rect.inflate_ip(2,2)
        self.status = 0
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)

class do_button(pygame.sprite.Sprite):
    def __init__(self,x,y,do,screen,background):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('button0.png')
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.top = y
        self.rect.left = x
        self.status = 0
        self.do = do
        self.is_on = 0
        self.screen = screen
        self.background = background
        self.update()
        background.blit(self.image,self.rect)
    def draw_some_shadow_lines(self,color):
        self.screen.lock()
        pygame.draw.line(self.background,color,(self.x+1,self.y+self.rect.height),\
                      (self.x+self.rect.width-1,self.y+self.rect.height)) #horizontal
        pygame.draw.line(self.background,color,(self.x+self.rect.width,self.y+1),\
                      (self.x+self.rect.width,self.y+self.rect.height)) #vertical
        self.screen.unlock()
    def draw_a_triangle(self,color):
        self.image.lock()
        if self.do:
            pygame.draw.polygon(self.image,color,((30,20),(15,30),(15,10)))
        else:
            pygame.draw.polygon(self.image,color,((10,20),(25,10),(25,30)))
        self.image.unlock()
    def press(self):
        self.rect.inflate_ip(-2,-2)
        self.status = 1
    def unpress(self):
        self.rect.inflate_ip(2,2)
        self.status = 0
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)
    def update(self):
        if self.is_on:
            self.image = load_image('button1.png')
            self.draw_some_shadow_lines(BLACK)
            self.draw_a_triangle(BLACK)
        elif not self.is_on:
            self.image = load_image('button0.png')
            self.draw_some_shadow_lines(WHITE)
            self.draw_a_triangle(LIGHT_GREY)

class do_button_holder:
    def __init__(self,screen,background):
        self.a = do_button(625,55,0,screen,background) # the undo button
        self.b = do_button(685,55,1,screen,background) # the redo button
    def update(self,number,total):
        if number == 0 and self.a.is_on:
            self.a.is_on = 0
            self.a.update()
        elif number > 0 and not self.a.is_on:
            self.a.is_on = 1
            self.a.update()
        if total == number and self.b.is_on:
            self.b.is_on = 0
            self.b.update()
        elif total > number and not self.b.is_on:
            self.b.is_on = 1
            self.b.update()

class radio_button(pygame.sprite.Sprite):
    def __init__(self,screen,text,topleft):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.image = pygame.Surface((45, 20)).convert()
        self.image.fill(WHITE)
        display_some_text(text, 15, (20,0), self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        if text == 'On':
            self.is_clicked = 1
        else:
            self.is_clicked = 0
        self.is_dirty = 1
        self.update()
    def draw_a_square(self,filled):
        self.image.lock()
        pygame.draw.rect(self.image, WHITE, (0,0,15,15))
        if filled:
            f = 0
        else:
            f = 2
        pygame.draw.rect(self.image, BLACK, (0,0,15,15), f)
        self.image.unlock()
    def update(self):
        if self.is_dirty:
            if self.is_clicked:
                self.draw_a_square(1)
            elif not self.is_clicked:
                self.draw_a_square(0)
            self.is_dirty = 0
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)

class radio_button_holder:
    def __init__(self,screen,background):
        self.screen = screen
        self.background = background
        musicfile = path.join(data_folder,'pcanon2.mid')
        pygame.mixer.music.load(musicfile)
        pygame.mixer.music.play(-1)
        self.draw_border()
        self.a = radio_button(screen,'On',[630,340])
        self.b = radio_button(screen,'Off',[680,340])
    def draw_border(self):
        self.screen.lock()
        pygame.draw.rect(self.background, BLACK, (615,310,120,70),1)
        pygame.draw.line(self.background, WHITE, (635,310),(715,310))
        self.screen.unlock()
        display_some_text('Music',24,[675,310],self.background,1)
    def update(self):
        if PLATFORM == 'win32':
            if self.a.is_clicked and self.a.is_dirty:
                self.b.is_clicked = 0
                self.b.is_dirty = 1
                pygame.mixer.music.play()
            elif self.b.is_clicked and self.b.is_dirty:
                self.a.is_clicked = 0
                self.a.is_dirty = 1
                pygame.mixer.music.stop()
        else:
            if self.a.is_clicked and self.a.is_dirty:
                self.b.is_clicked = 0
                self.b.is_dirty = 1
                pygame.mixer.music.unpause()
            elif self.b.is_clicked and self.b.is_dirty:
                self.a.is_clicked = 0
                self.a.is_dirty = 1
                pygame.mixer.music.pause()
        self.a.update()
        self.b.update()

class message_board(pygame.sprite.Sprite):
    def __init__(self,screen,background):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.background = background
        self.image = pygame.Surface((110,110)).convert()
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (620,140)
        self.draw_border()
        self.text1 = "Let's"
        self.text2 = "go !!!"
        display_some_text(self.text1,20,(55,45),self.image,1)
        display_some_text(self.text2,20,(55,65),self.image,1)
    def draw_border(self):
        self.screen.lock()
        pygame.draw.rect(self.background, BLACK, (610,130,130,130),1)
        pygame.draw.rect(self.background, BLACK, (615,135,120,120),1)
        self.screen.unlock()
    def update(self,a,b):
        if a == 0:
            if b < 100:
                self.text1 = 'Never'
                self.text2 = 'mind'
            elif b == 100:
                self.text1 = 'Bravo !!!'
                self.text2 = ''
        elif 0 < a < 100:
            self.text1 = 'Play !!!'
            self.text2 = ''
        elif a == 100:
            self.text1 = "Let's"
            self.text2 = "go !!!"
        self.image.fill(WHITE)
        display_some_text(self.text1,20,(55,45),self.image,1)
        display_some_text(self.text2,20,(55,65),self.image,1)

class grid:
    def __init__(self,screen,background):
        self.screen = screen
        self.background = background
        self.line_width = 3
        self.background.lock()
        for x in range(50,600,50):
            pygame.draw.line(background,BLACK,(x,50),(x,550),self.line_width)
            pygame.draw.line(background,BLACK,(50,x),(550,x),self.line_width)
        self.background.unlock()
    def digits(self,cell):
        if cell % 10 == 0:
            first_digit = (cell / 10) - 1
            second_digit = 10
        else:
            first_digit = cell / 10
            second_digit = cell % 10
        return first_digit, second_digit
    def cell(self,x,y):
        a = ((y / 50) * 10) - 10
        b = x / 50
        return a + b
    def _write(self,cell,number):
        self._clear(cell)
        first_digit, second_digit = self.digits(cell)
        write_location = 25 + second_digit * 50, 75 + first_digit * 50
        display_some_text(number,23,write_location,self.background,1)
    def _fill(self,cell,color=PASTEL_YELLOW):
        first_digit, second_digit = self.digits(cell)
        fill_rect = (1 + second_digit * 50 + (self.line_width/2),\
                     1 + 50 + (self.line_width/2) + first_digit * 50,\
                     50 - (self.line_width), 50 - (self.line_width))
        self.background.fill(color, fill_rect)
    def _clear(self,cell):
        self._fill(cell,WHITE)
    def is_focused(self,x,y):
        return (x in range(50+self.line_width,550-self.line_width+1)) and\
               (y in range(50+self.line_width,550-self.line_width+1))
    def update(self,a):
        for x in a[1:]:
            if x.is_dirty:
                if x.is_yellow:
                    self._fill(x._index)
                elif x.is_written:
                    self._write(x._index,str(x.number))
                elif (not x.is_yellow) or (not x.is_written):
                    self._clear(x._index)
                x.is_dirty = 0

class cell:
    def __init__(self,_index):
        self._index = _index
        self.number = 0
        self.is_written = 0
        self.is_yellow = 1
        self.is_dirty = 1

class cells:
    def __init__(self):
        self._list = [0]
        for x in range(1,101):
            self._list.append(cell(x))
    def update(self,flag,a,b,c):
        yellow_cells = 0
        if flag == 'start':
            for x in range(1,101):
                self._list[x].is_yellow = 1
                self._list[x].is_dirty = 1
            yellow_cells = 100
        else:
            for x in range(1,101):
                if self._list[x].is_yellow:
                    self._list[x].is_yellow = 0
                    self._list[x].is_dirty = 1
            if flag == 'play':
                pass
            elif flag == 'undo':
                pass
            elif flag == 'redo':
                pass
            for x in c:
                yellow_cell = x[0]*10 + x[1]
                if not self._list[yellow_cell].is_written:
                    self._list[yellow_cell].is_yellow = 1
                    self._list[yellow_cell].is_dirty = 1
                    yellow_cells = yellow_cells + 1
        return self._list, yellow_cells

class counter:
    def __init__(self):
        self.number = 0
        self.total = 0
    def update(self,a):
        self.number = self.number + a
        if self.total < self.number:
            self.total = self.number
        return [self.number,self.total]
        
class gameplay:
    def __init__(self,screen,background,_cells_,_counter_,_radio_button_holder_,_message_board_):
        self.screen = screen
        self.a = grid(screen,background)
        self.b = _cells_
        self.c = _counter_
        self.d1 = simple_button(615,505,'About',screen,background)
        self.d2 = simple_button(615,455,'Help',screen,background)
        self.d3 = simple_button(615,405,'New',screen,background)
        self.e = do_button_holder(screen,background)
        self.f = _radio_button_holder_
        self.g = _message_board_
        self.group = (self.d1,self.d2,self.d3,self.e.a,self.e.b,self.f.a,self.f.b,self.g)
        self.allsprites = pygame.sprite.RenderUpdates(self.group)
    def update(self,x,y):

        # some variables
        update_var = 0
        u5 = []

        # first update the counter
        if self.a.is_focused(x,y):
            if self.c.total > self.c.number:
                self.c.total = self.c.number
                for n in range(1,101):
                    m = self.b._list[n]
                    if m.number > self.c.number:
                        m.number = 0
                        m.is_written = 0
                        m.is_dirty = 1
            u2 = self.a.cell(x,y)
            if self.b._list[u2].is_yellow:
                self.c.update(1)
                update_var = 1
        elif self.e.a.is_focused(x,y) and self.e.a.is_on:
            self.c.update(-1)
            update_var = 2
        elif self.e.b.is_focused(x,y) and self.e.b.is_on:
            self.c.update(1)
            update_var = 3

        # next update the list
        if update_var == 1:
            y = self.b._list[u2]
            y.number = self.c.number
            y.is_written = 1
            y.is_dirty = 1
            u3 = self.a.digits(u2)
            u4 = find_other_squares(u3[0],u3[1])
            u5,u51 = self.b.update('play',self.c.number,u2,u4)
        elif update_var == 2:
            if self.c.number > 0:
                for x in range(1,101):
                    y = self.b._list[x]
                    if y.number == self.c.number:
                        u2 = y._index
                    elif y.number == self.c.number + 1:
                        y.is_written = 0
                        y.is_dirty = 1
                u3 = self.a.digits(u2)
                u4 = find_other_squares(u3[0],u3[1])
                u5,u51 = self.b.update('undo',0,0,u4)
            elif self.c.number == 0:
                for x in range(1,101):
                    y = self.b._list[x]
                    if y.number == 1:
                        y.is_written = 0
                        y.is_dirty = 1
                u5,u51 = self.b.update('start',0,0,0)
        elif update_var == 3:
            for x in range(1,101):
                y = self.b._list[x]
                if y.number == self.c.number:
                    y.is_written = 1
                    y.is_dirty = 1
                    u2 = y._index
            u3 = self.a.digits(u2)
            u4 = find_other_squares(u3[0],u3[1])
            u5,u51 = self.b.update('redo',self.c.number,u2,u4)

        # finally
        if u5:
            self.a.update(u5) # update the grid
            self.e.update(self.c.number,self.c.total) # update the do/undo buttons
            if update_var == 2:
                self.e.a.press()
            elif update_var == 3:
                self.e.b.press()
            self.g.update(u51,self.c.number) # update the message board

class game:
    def __init__(self,screen,background):
        _cells_ = cells()
        _counter_ = counter()
        _radio_button_holder_ = radio_button_holder(screen,background)
        _message_board_ = message_board(screen,background)
        run = 1
        while run:
            a = play(screen,background,_cells_,_counter_,_radio_button_holder_,_message_board_)
            if a == 0:
                run = 0
            elif a == 1:
                run1 = 1
                while run1:
                    b = about(screen,background,_cells_,_radio_button_holder_,_message_board_)
                    if b == 0:
                        run = 0
                        run1 = 0
                    elif b == 1:
                        run1 = 0
            elif a == 2:
                run2 = 1
                while run2:
                    c = _help(screen,background,_cells_,_radio_button_holder_,_message_board_)
                    if c == 0:
                        run = 0
                        run2 = 0
                    elif c == 1:
                        run2 = 0
            elif a == 3:
                _cells_.__init__()
                _counter_.__init__()
                _radio_button_holder_.draw_border()
                _message_board_.__init__(screen,background)
        pygame.quit()

#-------------------Game functions-------------------
def play(screen,background,_cells_,_counter_,_radio_button_holder_,_message_board_):

    a = gameplay(screen,background,_cells_,_counter_,_radio_button_holder_,_message_board_)

    # Draw the game on the screen for the first time
    a.a.update(a.b._list)
    a.e.update(a.c.number,a.c.total)
    screen.blit(background, (0, 0))
    a.allsprites.draw(screen)
    pygame.display.update()

    play_var = 0
    run = 1
    while run:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = 0
            else:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    x = event.pos[0]
                    y = event.pos[1]
                    if a.d1.is_focused(x,y):
                        a.d1.press()
                    elif a.d2.is_focused(x,y):
                        a.d2.press()
                    elif a.d3.is_focused(x,y):
                        a.d3.press()
                    elif a.f.a.is_focused(x,y) and not a.f.a.is_clicked:
                        a.f.a.is_clicked = 1
                        a.f.a.is_dirty = 1
                        a.f.update()
                    elif a.f.b.is_focused(x,y) and not a.f.b.is_clicked:
                        a.f.b.is_clicked = 1
                        a.f.b.is_dirty = 1
                        a.f.update()
                    else:
                        a.update(x,y)
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    if a.d1.status:
                        a.d1.unpress()
                        play_var = 1
                        run = 0
                    elif a.d2.status:
                        a.d2.unpress()
                        play_var = 2
                        run = 0
                    elif a.d3.status:
                        a.d3.unpress()
                        play_var = 3
                        run = 0
                    elif a.e.a.status:
                        a.e.a.unpress()
                    elif a.e.b.status:
                        a.e.b.unpress()
                screen.blit(background, (0, 0))
                a.allsprites.draw(screen)
                pygame.display.update()

    a.allsprites.remove(a.group)
    background.fill(WHITE)
    screen.blit(background, (0, 0))
    pygame.display.update()
    return play_var

def about(screen,background,_cells_,_radio_button_holder_,_message_board_):

    text_file = path.join(data_folder,'about.txt')
    in_file = open(text_file,"r")
    text = in_file.readlines()
    in_file.close()


    dist = 20
    y = dist
    for t in text:
        lt = len(t)-1
        display_some_text(t[:lt],dist,[400,y],background,1)
        y = y + dist

    sb = simple_button(340,550,'Back',screen,background)
    allsprites = pygame.sprite.RenderUpdates(sb)

    screen.blit(background, (0, 0))
    allsprites.draw(screen)
    pygame.display.update()

    run = 1
    play_var = 0
    while run:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = 0
            else:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if sb.is_focused(event.pos[0],event.pos[1]):
                        sb.press()
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    if sb.status:
                        sb.unpress()
                        play_var = 1
                        run = 0
                screen.blit(background, (0, 0))
                allsprites.draw(screen)
                pygame.display.update()

    allsprites.remove(sb)
    background.fill(WHITE)
    _radio_button_holder_.draw_border()
    _message_board_.draw_border()
    screen.blit(background, (0, 0))
    pygame.display.update()
    for x in _cells_._list[1:]:
        x.is_dirty = 1
    return play_var

def _help(screen,background,_cells_,_radio_button_holder_,_message_board_):

    text_file = path.join(data_folder,'help.txt')
    in_file = open(text_file,"r")
    text = in_file.readlines()
    in_file.close()

    y = 30
    for t in text:
        lt = len(t)-1
        display_some_text(t[:lt],20,[70,y],background)
        y = y + 20

    pics_list = [
                    ['grid1.png', [600, 30]],
                    ['grid2.png', [600, 300]]
                ]
    for z in pics_list:
        pic = load_image(z[0])
        picrect = pic.get_rect()
        picrect.centerx = (z[1][0])
        picrect.top = (z[1][1])
        background.blit(pic,picrect)

    sb = simple_button(185,530,'Back',screen,background)
    allsprites = pygame.sprite.RenderUpdates(sb)

    screen.blit(background, (0, 0))
    allsprites.draw(screen)
    pygame.display.update()

    run = 1
    play_var = 0
    while run:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = 0
            else:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if sb.is_focused(event.pos[0],event.pos[1]):
                        sb.press()
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    if sb.status:
                        sb.unpress()
                        play_var = 1
                        run = 0
                screen.blit(background, (0, 0))
                allsprites.draw(screen)
                pygame.display.update()

    allsprites.remove(sb)
    background.fill(WHITE)
    _radio_button_holder_.draw_border()
    _message_board_.draw_border()
    screen.blit(background, (0, 0))
    pygame.display.update()
    for x in _cells_._list[1:]:
        x.is_dirty = 1
    return play_var

def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('Seminar v' + VERSION)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(WHITE)

    screen.blit(background,(0,0))
    pygame.display.update()

    a = game(screen, background)

if __name__ == "__main__": main()
