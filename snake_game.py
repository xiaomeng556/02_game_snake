import pygame
import random
import os
import sys

# ==========================================
# 游戏常量配置 (Game Constants)
# ==========================================
WINDOW_WIDTH = 800      # 游戏窗口宽度
WINDOW_HEIGHT = 600     # 游戏窗口高度
GRID_SIZE = 20          # 网格大小 (蛇身和食物的尺寸)
FPS = 6                 # 游戏运行帧率 (控制蛇的移动速度)

# ==========================================
# 颜色定义 (Colors) - (R, G, B)
# ==========================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)       # 食物颜色
GREEN = (0, 255, 0)     # 蛇身颜色
DARK_GREEN = (0, 200, 0) # 蛇头颜色
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)  # 提示文字颜色

# ==========================================
# 方向向量 (Direction Vectors)
# ==========================================
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    """
    蛇类：负责管理蛇的身体位置、移动、增长及碰撞逻辑。
    """
    def __init__(self):
        self.reset()

    def reset(self):
        """重置蛇的状态（初始长度、位置、方向）"""
        self.length = 3
        # positions[0] 是蛇头，后面的元素是身体
        self.positions = [((WINDOW_WIDTH // 2), (WINDOW_HEIGHT // 2))]
        # 初始身体段落 (水平排列)
        for i in range(1, self.length):
            self.positions.append((self.positions[0][0] - i * GRID_SIZE, self.positions[0][1]))
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0

    def get_head_position(self):
        """获取蛇头的当前坐标"""
        return self.positions[0]

    def update(self):
        """
        更新蛇的位置。
        返回: True 如果移动成功，False 如果发生碰撞（游戏结束）。
        """
        self.direction = self.next_direction
        cur = self.get_head_position()
        x, y = self.direction
        # 计算新蛇头的位置
        new = (((cur[0] + (x * GRID_SIZE))), (cur[1] + (y * GRID_SIZE)))

        # 1. 自身碰撞检测: 如果新蛇头撞到了现有的身体段
        if len(self.positions) > 2 and new in self.positions[2:]:
            return False
        
        # 2. 边界碰撞检测: 检查蛇头是否超出屏幕边界
        if new[0] < 0 or new[0] >= WINDOW_WIDTH or new[1] < 0 or new[1] >= WINDOW_HEIGHT:
            return False

        # 将新蛇头插入到位置列表最前端
        self.positions.insert(0, new)
        
        # 如果当前身体长度超过了应有长度，则移除尾部 (实现移动效果)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def grow(self):
        """吃到食物后增长长度并加分"""
        self.length += 1
        self.score += 10

    def draw(self, surface):
        """在屏幕上绘制蛇"""
        for i, p in enumerate(self.positions):
            # 蛇头和蛇身使用不同深浅的绿色区分
            color = DARK_GREEN if i == 0 else GREEN
            r = pygame.Rect((p[0], p[1]), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, r)
            # 绘制黑色边框，增强立体感
            pygame.draw.rect(surface, BLACK, r, 1)

    def handle_keys(self, event):
        """
        处理键盘方向键事件，改变蛇的移动方向。
        增加逻辑防止蛇直接掉头（例如向上移动时禁止直接按向下）。
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != DOWN:
                self.next_direction = UP
            elif event.key == pygame.K_DOWN and self.direction != UP:
                self.next_direction = DOWN
            elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                self.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                self.next_direction = RIGHT

class Food:
    """
    食物类：负责随机生成食物并管理其绘制。
    """
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position([])

    def randomize_position(self, snake_positions):
        """
        在网格内随机生成食物位置。
        确保食物不会出现在蛇的身体位置上。
        """
        while True:
            x = random.randint(0, (WINDOW_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
            y = random.randint(0, (WINDOW_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
            self.position = (x, y)
            if self.position not in snake_positions:
                break

    def draw(self, surface):
        """在屏幕上绘制食物"""
        r = pygame.Rect((self.position[0], self.position[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, BLACK, r, 1)

class Game:
    """
    游戏管理类：主控中心，负责初始化、循环控制、音效加载及 HUD 渲染。
    """
    def get_font(self, size):
        """
        根据系统环境获取中文字体。
        按顺序尝试加载 SimHei, 微软雅黑, Arial, 或默认字体。
        """
        font_names = ["SimHei", "Microsoft YaHei", "Arial", "Courier New"]
        for name in font_names:
            try:
                font = pygame.font.SysFont(name, size)
                if font: return font
            except:
                continue
        return pygame.font.SysFont(None, size)

    def __init__(self):
        # 初始化 Pygame 相关组件
        pygame.init()
        pygame.mixer.init() # 初始化混音器用于播放音效
        
        # 窗口设置
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('贪吃蛇小游戏')
        
        # 时钟对象，用于控制游戏帧率
        self.clock = pygame.time.Clock()
        
        # 字体加载
        self.font = self.get_font(24)
        self.large_font = self.get_font(48)
        
        # 实例化蛇和食物
        self.snake = Snake()
        self.food = Food()
        self.food.randomize_position(self.snake.positions)
        
        # 加载历史最高分
        self.high_score = self.load_high_score()
        self.game_over = False # 游戏结束标志位
        self.paused = False    # 暂停标志位
        
        # 加载音效文件 (若文件不存在，对应的变量将为 None，代码会安全跳过播放)
        # 您需要将相应的 wav/mp3 文件放在项目根目录下
        self.eat_sound = self.load_sound('eat.wav')           # 吃食物音效
        self.game_over_sound = self.load_sound('game_over.wav') # 游戏结束音效
        
        # 加载背景音乐
        self.load_background_music('background.mp3')

    def load_sound(self, filename):
        """安全加载音效文件"""
        try:
            if os.path.exists(filename):
                return pygame.mixer.Sound(filename)
        except Exception as e:
            print(f"Warning: Could not load sound {filename}: {e}")
        return None

    def load_background_music(self, filename):
        """安全加载并播放背景音乐"""
        try:
            if os.path.exists(filename):
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play(-1) # -1 表示无限循环播放
                pygame.mixer.music.set_volume(0.5) # 设置音量为 50%
        except Exception as e:
            print(f"Warning: Could not load background music {filename}: {e}")

    def load_high_score(self):
        """从文件读取最高分记录"""
        try:
            if os.path.exists('high_score.txt'):
                with open('high_score.txt', 'r') as f:
                    return int(f.read())
        except:
            pass
        return 0

    def save_high_score(self):
        """保存新的最高分到文件"""
        if self.snake.score > self.high_score:
            self.high_score = self.snake.score
            with open('high_score.txt', 'w') as f:
                f.write(str(self.high_score))

    def draw_text(self, text, font, color, x, y, center=False):
        """
        通用文本渲染函数。
        text: 文字内容, font: 字体对象, color: 颜色, x/y: 坐标, center: 是否居中。
        """
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(img, rect)

    def reset_game(self):
        """重新开始游戏时重置状态"""
        self.snake.reset()
        self.food.randomize_position(self.snake.positions)
        self.game_over = False
        self.paused = False

    def run(self):
        """
        游戏主循环。
        """
        while True:
            # 1. 事件监听 (Input Handling)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_high_score()
                    pygame.quit()
                    sys.exit()
                
                if not self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p: # P 键暂停/继续
                            self.paused = not self.paused
                        else:
                            self.snake.handle_keys(event)
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: # R 键重新开始
                            self.reset_game()

            # 2. 逻辑更新 (Update Logic)
            if not self.game_over and not self.paused:
                # 更新蛇的位置，如果返回 False 则说明撞墙或撞到自己
                if not self.snake.update():
                    self.game_over = True
                    if self.game_over_sound:
                        self.game_over_sound.play()
                    self.save_high_score()
                
                # 吃食物检测: 如果蛇头坐标与食物坐标重合
                if self.snake.get_head_position() == self.food.position:
                    self.snake.grow()
                    self.food.randomize_position(self.snake.positions)
                    if self.eat_sound:
                        self.eat_sound.play()

            # 3. 画面渲染 (Rendering)
            self.screen.fill(BLACK) # 背景填充黑色
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # 绘制 HUD 信息 (得分显示)
            self.draw_text(f"当前得分: {self.snake.score}", self.font, WHITE, 10, 10)
            self.draw_text(f"最高分: {self.high_score}", self.font, WHITE, 10, 40)
            
            # 绘制暂停提示
            if self.paused:
                self.draw_text("游戏暂停 - 按 P 继续", self.large_font, YELLOW, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, center=True)
            
            # 绘制游戏结束提示
            if self.game_over:
                self.draw_text("游戏结束!", self.large_font, RED, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40, center=True)
                self.draw_text(f"最终得分: {self.snake.score}", self.font, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10, center=True)
                self.draw_text("按 R 重新开始", self.font, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50, center=True)

            # 更新屏幕显示
            pygame.display.update()
            
            # 控制帧率 (12 FPS)
            self.clock.tick(FPS)

if __name__ == '__main__':
    # 运行游戏
    game = Game()
    game.run()
