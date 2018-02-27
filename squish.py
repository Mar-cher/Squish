#包括主Game类和一些游戏状态类
import os, sys, pygame
##导入一些常用的函数和常量
from pygame.locals import *
#导入对应的模块
from Squish import objects
from Squish import config

class State:
    #表示何时程序退出
    def handle(self, event):
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()

    def firstDisplay(self, screen):
        #使用背景色填充屏幕
        screen.fill(config.Background_color)
        #pygame.display.update()是将数据画到前面显示，每次看到的都是在原基础上改变的过程
        #而pygame.display.flip()是交替显示的意思，每次看到的都是完整的图案。
        pygame.display.flip()

    def display(self):
        #用于在显示过一次状态之后再次显示，默认的行为是什么都不做
        pass

class Level(State):
    #游戏等级，用于计算已经落下了多少的秤砣，移动子图形以及其他的和游戏逻辑相关的任务
    def __init__(self, number = 1):
        self.number = number
        #本关还要落下多少秤砣
        self.remaining = config.Weight_per_level
        #将速度设置为config里面的速度
        speed = config.Drop_speed
        #为每个大于一的等级都增加一个Speed_increase对应的值
        speed += (self.number - 1) * config.Speed_increase
        #创建秤砣和香蕉
        self.weight = objects.Weight(speed)
        self.banana = objects.Banana()
        both = self.weight, self.banana
        self.sprites = pygame.sprite.RenderUpdates(both)

    def update(self, game):
        #更新游戏状态
        self.sprites.update()
        #香蕉和秤砣接触的情况
        if self.banana.touches(self.weight):
            game.nextState = GameOver()
        #秤砣落下之后的情况
        elif self.weight.landed:
            #重置位置
            self.weight.reset()
            #剩下的秤砣数减一
            self.remaining -= 1
            #当所有秤砣已用完时，过关
            if self.remaining == 0:
                game.nextState = LevelCleared(self.number)

    def display(self, screen):
        #用背景色填充屏幕
        screen.fill(config.Background_color)
        #对self.sprites.draw提供的需要更新的矩形列表进行更新
        updates = self.sprites.draw(screen)
        pygame.display.update(updates)

#暂停游戏的状态，只要键盘上的按键被按下或者鼠标被点击都可以结束这个状态
#下面这个类是后面几个类的基类
class Paused(State):
    #用一个bool变量来表示用户是否结束暂停
    finished = 0
    #如果需要图片的话，将这个变量设置为文件名
    image = None
    #引号里面可以设置成提示性文本（看个人喜好）
    text = 'Pause'

    def handle(self, event):
        #通过对State进行委托(运用State的方法)以及对按键和鼠标点击作为反应来处理事件
        #如果键盘按键被按下时或者鼠标被点击时，将bool变量self.finished设定为真
        State.handle(self, event)
        if event.type in [MOUSEBUTTONDOWN, KEYDOWN]:
            self.finished = 1

    def update(self, game):
        #如果self.finished为真，则告诉游戏切换到下一个由self.nextState()表示的状态
        if self.finished:
            game.nextState = self.nextState()

    def firstDisplay(self, screen):
        #背景色填充
        screen.fill(config.Background_color)
        #设置字体以及字体的大小
        font = pygame.font.Font(None, config.font_size)
        #文本
        lines = self.text.strip().splitlines()
        #文本的高
        height = len(lines) * font.get_linesize()
        center, top = screen.get_rect().center
        top -= height // 2
        if self.image:
            image = pygame.image.load(self.image).convert()
            r = image.get_rect()
            top += r.height // 2
            r.midbottom = center.top - 20
            screen.blit(image, r)
        #bool型变量，用来表示文本中的字体是否抗锯齿
        antialias = 1
        #黑色的元组表示,里面的数字范围均是0~255
        black = (0, 0, 0)
        for line in lines:
            #字体render后面的参数一共有4个，分别是文本，是否抗锯齿（bool型的变量），字体的颜色，背景的颜色（可不写，即默认值）
            text = font.render(line.strip(), antialias, black)
            r = text.get_rect()
            r.midtop = center, top
            #将text移动到r处，其中r为text的左上角
            screen.blit(text, r)
            top += font.get_linesize()
        #显示画面
        pygame.display.flip()

#暂停状态(Paused)的子类，显示有关的游戏信息，在Level状态后显示信息
class Info(Paused):
    nextState = Level
    text = '''
    In this game you are a banana,
    trying to survive a course in
    self-defense against fruit, where
    the participants will "defend" 
    themselves against you with a 
    16 ton weight.
    '''

#暂停状态(Paused)的子类，显示图片和欢迎信息的暂停状态，在info状态后显示
class StartUp(Paused):
    nextState = Info
    image = config.Splash_image
    text = '''
    Welcome to Squish,
    the game of Fruit Self-Denfense.
    '''

#暂停状态(Paused)的子类，提示用户等级提升的状态，在next level后显示
class LevelCleared(Paused):
    def __init__(self, number):
        self.number = number
        self.text = '''
        Level %i cleared
        Click to start next level
        '''%self.number

    def nextState(self):
        return Level(self.number + 1)

#暂停状态(Paused)的子类，提示用户输掉游戏的状态，在first level后显示
class GameOver(Paused):
    nextState = Level
    text = '''
    Game Over,
    click to Restart, Esc to Quit.
    '''

#负责主事件循环的游戏对象，任务包括在不同的状态间切换
class Game:
    def __init__(self, *args):
        #获取图像和游戏放置的目录
        path = os.path.abspath(args[0])
        dir = os.path.split(path[0])
        #移动上面的目录（这样图片便可以在稍后打开）
        os.chdir(dir)
        #无状态方式启动
        self.state = None
        #在第一个时间循环迭代中移动到StartUp
        self.nextState = StartUp()

    #这个方法旨在动态设置变量，进行一些重要的初始化工作，并且进入主事件循环
    def run(self):
        #初始化pygame
        pygame.init()
        #设置一个bool型的变量，用其来记住是否为全屏模式
        flag = 0
        if config.full_screen:
            flag = FULLSCREEN
        screen_size = config.Screen_size
        #访问显示器，设置屏幕的大小，模式
        screen = pygame.display.set_mode(screen_size, flag)
        #设置屏幕的名称
        pygame.display.set_caption('Fruit Self Denfense')
        #隐藏或者展示鼠标指针
        pygame.mouse.set_visible(False)
        #主循环
        while True:
            if self.state != self.nextState:
                self.state = self.nextState
                self.state.firstDisplay(screen)
            for event in pygame.event.get():
                self.state.handle(event)
            self.state.update(self)
            self.state.display(screen)

if __name__ == "__main__":
    game = Game(*sys.argv)
    game.run()

