#游戏对象的实现
import pygame, os
from Squish import config
from random import randrange

class SquishSprite(pygame.sprite.Sprite):
    """
    Squish中所有子图形的范型超类，构造函数负责载入图案，设置子图形的rect和area属性
    并且允许它在指定区域内进行移动，area有屏幕的大小和留白决定
    """
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image).convert()
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        shrink = -config.margin * 2
        self.area = screen.get_rect().inflate(shrink, shrink)

class Weight(SquishSprite):
    def __init__(self, speed):
        #落下的秤砣，使用SquishSprite构造函数设置秤砣图像
        SquishSprite.__init__(self, config.Weight_image)
        #秤砣下降的速度
        self.speed = speed
        #重置
        self.reset()

    def reset(self):
        #确定x的取值范围
        x = randrange(self.area.left, self.area.right)
        #设置秤砣底端的坐标范围
        self.rect.midbottom = x, 0

    def update(self):
        #根据它的速度将秤砣垂直移动一段距离，并且根据它是否触及屏幕底端
        #来设置landed属性
        self.rect.top += self.speed
        self.landed = self.rect.top >= self.area.bottom

class Banana(SquishSprite):
    def __init__(self):
        #设置香蕉图像，并且会停留在屏幕底端，水平位置由当前的鼠标位置决定
        SquishSprite.__init__(self, config.Banana_image)
        self.rect.bottom = self.area.bottom
        self.pad_top = config.Banana_pad_top
        self.pad_side = config.Banana_pad_side

    def update(self):
        #将香蕉中心点坐标设置为当前鼠标指针的横坐标，并且使用rect和clamp方法
        #确保香蕉停留在允许的范围内
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect = self.rect.clamp(self.area)

    def touches(self, other):
        #判断香蕉是否碰触到了其他的图形（比如秤砣）
        #设置一个不包括香蕉顶端和侧边的新矩形
        bounds = self.rect.inflate(-self.pad_side, -self.pad_top)
        #移动边界，使得这个矩形的底端和香蕉的底端重合
        bounds.bottom = self.rect.bottom
        #检查边界是否和其他对象的rect交叉
        return bounds.colliderect(other.rect)
