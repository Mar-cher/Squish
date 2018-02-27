from pygame.locals import *
import sys, pygame
from random import randrange # 从指定范围内选一个数，三个参数，start，end，step

class Weight(pygame.sprite.Sprite):
    def __init__(self):
        #调用基类的初始化,省略对重复东西初始化的操作
        pygame.sprite.Sprite.__init__(self)
        #画sprite时需要使用到的图像和矩形
        self.image = Weight_image
        self.rect = self.image.get_rect()
        #重置
        self.reset()

    def reset(self):
        #将秤砣移动到屏幕顶端的随机位置
        self.rect.top = -self.rect.height
        self.rect.centerx = randrange(screen_size[0])

    def update(self):
        #更新秤砣，显示下一帧
        self.rect.top += 1
        if self.rect.top > screen_size[1]:
            self.reset()

pygame.init()
screen_size = 1920, 1080
pygame.display.set_mode(screen_size, FULLSCREEN)
pygame.mouse.set_visible(0)

Weight_image = pygame.image.load('weight.jpg')
Weight_image = Weight_image.convert()

sprites = pygame.sprite.RenderUpdates()
sprites.add(Weight())

screen = pygame.display.get_surface()
bg = (255, 255, 255)
screen.fill(bg)
pygame.display.flip()

def clear_callback(surf, rect):
    surf.fill(bg, rect)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
    sprites.clear(screen, clear_callback)
    sprites.update()
    updates = sprites.draw(screen)
    pygame.display.update(updates)
