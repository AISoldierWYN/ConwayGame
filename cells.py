import pygame
import sys
import copy
import json
import tkinter as tk
from tkinter import filedialog

FPS = 20
DRAW_FPS = 60

# screen size
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BLOCK_SIZE = 10

COL_MAX_IDX = SCREEN_WIDTH // BLOCK_SIZE
ROW_MAX_IDX = SCREEN_HEIGHT // BLOCK_SIZE

# color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class ConwaysCells():
    cells_map = [[0] * (COL_MAX_IDX + 2) for _ in range(ROW_MAX_IDX + 2)]

    START_ROW_IDX = 1
    END_RAW_IDX = ROW_MAX_IDX
    START_COL_IDX = 1
    END_COL_IDX = COL_MAX_IDX

    def __init__(self, init_cell_list=None, load_files=None):
        if init_cell_list:
            for cell in init_cell_list:
                self.cells_map[cell[0]][cell[1]] = 1
        self.tmp_cells_map = copy.deepcopy(self.cells_map)
    
    def load_from_files(self, load_path):
        with open(load_path, 'r') as file:
            load_data = json.load(file)
            self.cells_map = load_data['cells_map']
            self.copyMap(self.cells_map, self.tmp_cells_map)
    
    def save_into_files(self, save_path):
        save_data = {
            'cells_map': self.cells_map
        }
        with open(save_path, 'w') as file:
            json.dump(save_data, file)
    
    def copyMap(self, src, dst):
        for i in range(len(src)):
            for j in range(len(src[i])):
                dst[i][j] = src[i][j]
    
    def calculate_index_by_mouse_pos(self, mouse_pos):
        # row = self.START_ROW_IDX + mouse_pos[1] // BLOCK_SIZE
        # col = self.START_COL_IDX + mouse_pos[0] // BLOCK_SIZE
        row = mouse_pos[1] // BLOCK_SIZE
        col = mouse_pos[0] // BLOCK_SIZE
        return [row, col]
    
    def set_cells_map_element_by_mouse_pos(self, screen, mouse_pos, mouse_pressed):
        left_mouse_pressed, right_mouse_pressed = mouse_pressed[0], mouse_pressed[2]
        position = self.calculate_index_by_mouse_pos(mouse_pos)
        if not left_mouse_pressed and not right_mouse_pressed:
            if self.cells_map[position[0]][position[1]] == 0:
                self.draw_one_cell(screen, position[1], position[0], RED)
            else:
                self.draw_one_cell(screen, position[1], position[0], WHITE)
        elif left_mouse_pressed:
            self.cells_map[position[0]][position[1]] = 1
        elif right_mouse_pressed:
            self.cells_map[position[0]][position[1]] = 0

    def update(self):
        row_pointer = self.START_ROW_IDX
        col_pointer = self.START_COL_IDX
        self.copyMap(self.cells_map, self.tmp_cells_map)
        for _ in range(ROW_MAX_IDX):
            for _1 in range(COL_MAX_IDX):
                self.update_certain_cell_in_tmp_map(row_pointer, col_pointer)
                col_pointer += 1
            row_pointer += 1
            col_pointer = self.START_COL_IDX
        self.copyMap(self.tmp_cells_map, self.cells_map)
    
    def update_certain_cell_in_tmp_map(self, row_pointer, col_pointer):
        if self.cells_map[row_pointer][col_pointer] == 0:
            # 出生规则：如果一个死细胞周围正好有3个活细胞，则该细胞变为活细胞（繁殖）。
            if self.check_birth(row_pointer, col_pointer):
                self.tmp_cells_map[row_pointer][col_pointer] = 1
        elif self.cells_map[row_pointer][col_pointer] == 1:
            if not self.check_alive(row_pointer, col_pointer):
                self.tmp_cells_map[row_pointer][col_pointer] = 0
    
    def calculate_around_alive_cells(self, row_pointer, col_pointer, self_is_alive=False):
        around_alive_cells = 0
        row = row_pointer - 1
        col = col_pointer - 1
        for _ in range(3):
            for _1 in range(3):
                if self.cells_map[row][col] == 1:
                    around_alive_cells += 1
                col += 1
            row += 1
            col = col_pointer - 1
        
        if self_is_alive:
            return around_alive_cells - 1
        else:
            return around_alive_cells

    def check_birth(self, row_pointer, col_pointer):
        around_alive_cells = self.calculate_around_alive_cells(row_pointer, col_pointer, False)
        return around_alive_cells == 3
        
    def check_alive(self, row_pointer, col_pointer):
        around_alive_cells = self.calculate_around_alive_cells(row_pointer, col_pointer, True)
        return around_alive_cells == 2 or around_alive_cells == 3
    
    def draw(self, screen):
        row_pointer = self.START_ROW_IDX
        col_pointer = self.START_COL_IDX
        for _ in range(ROW_MAX_IDX):
            for _1 in range(COL_MAX_IDX):
                if self.cells_map[row_pointer][col_pointer] == 1:
                    self.draw_one_cell(screen, col_pointer, row_pointer)
                col_pointer += 1
            row_pointer += 1
            col_pointer = self.START_COL_IDX
    
    def draw_one_cell(self, screen, left, top, color=BLACK):
        rect = pygame.Rect(left * BLOCK_SIZE, top * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, color, rect)

if __name__ == '__main__':
    print("""
        操作方式:
          鼠标左键按下，对应方块变黑，对应细胞为活细胞；
          鼠标右键按下，对应方块变白，对应位置如有细胞，变为死细胞，恢复为空白位置；
          s键：保存当前的状态；
          l键：加载存档；
          按下回车/Space，开始游戏
          注意：如果键盘响应不了，切换为纯英文输入法
          """)
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('元细胞')
    cells = ConwaysCells()

    user_init = True
    while user_init:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    user_init = False
                elif event.key == pygame.K_s:
                    root = tk.Tk()
                    root.withdraw()
                    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                        filetypes=[("存档", "*.txt")])
                    if file_path:
                        cells.save_into_files(file_path)
                    root.destroy()
                elif event.key == pygame.K_l:
                    root = tk.Tk()
                    root.withdraw()
                    file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                      filetypes=[("读档", "*.txt")])
                    if file_path:
                        cells.load_from_files(file_path)
                    root.destroy()
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        cells.draw(screen)
        cells.set_cells_map_element_by_mouse_pos(screen, mouse_pos, mouse_pressed)
        pygame.display.flip()
        clock.tick(DRAW_FPS)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(WHITE)
        cells.draw(screen)
        pygame.display.flip()
        cells.update()
        clock.tick(FPS)
