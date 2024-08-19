#
# gizmos.py - Реализует разные полезные визуальные инструменты для редактора.
#


# Импортируем:
import numpy as np
from OpenGL import GL as gl


# Класс сетки:
class Grid:
    def __init__(self, camera) -> None:
        self.camera          = camera  # 2D камера.
        self.grid_size       = 1024    # Размер сетки.
        self.grids           = 4       # Столько сеток создать. Размер ячеек сетки: 1 / 10 / 100 метров.
        self.grid_list       = []      # Список сеток.
        self.is_enabled      = True    # Включена ли сетка.
        self.all_alpha       = 1.0     # Общая альфа цветов.
        self.is_enabled_axis = True    # Включены ли линии осей.
        self.alpha_axis      = 1.0     # Альфа цветов линий осей.

        # Создание сетки:
        self.vertices = np.array([])
        for x in range(-self.grid_size//2, (self.grid_size//2)+1):
            self.vertices = np.append(self.vertices, [x * self.camera.meter, -self.grid_size//2 * self.camera.meter, 0])
            self.vertices = np.append(self.vertices, [x * self.camera.meter, +self.grid_size//2 * self.camera.meter, 0])
        for y in range(-self.grid_size//2, (self.grid_size//2)+1):
            self.vertices = np.append(self.vertices, [-self.grid_size//2 * self.camera.meter, y * self.camera.meter, 0])
            self.vertices = np.append(self.vertices, [+self.grid_size//2 * self.camera.meter, y * self.camera.meter, 0])

    # Создать сетку:
    def create(self) -> "Grid":
        # Создание буфера вершин сетки для более быстрой отрисовки:
        for index in range(self.grids):
            vertex_buffer = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_STATIC_DRAW)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            self.grid_list.append([vertex_buffer, 1.0])
        return self

    # Отрисовать сетку:
    def render(self, delta_time: float, bg_color: list) -> None:
        is_enabled, self.delta_time = False, delta_time
        if gl.glIsEnabled(gl.GL_LINE_SMOOTH): gl.glDisable(gl.GL_LINE_SMOOTH) ; is_enabled = True
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        # Включена ли сетка:
        if self.is_enabled: self.all_alpha += 0.175 * delta_time*60
        else:               self.all_alpha -= 0.175 * delta_time*60
        self.all_alpha = 0 if self.all_alpha < 0 else self.all_alpha
        self.all_alpha = 1 if self.all_alpha > 1 else self.all_alpha

        # Включены ли линии осей:
        if self.is_enabled_axis: self.alpha_axis += 0.175 * delta_time*60
        else:                    self.alpha_axis -= 0.175 * delta_time*60
        self.alpha_axis = 0 if self.alpha_axis < 0 else self.alpha_axis
        self.alpha_axis = 1 if self.alpha_axis > 1 else self.alpha_axis

        # Проходимся по сеткам:
        for index, grid in enumerate(self.grid_list):
            size = 10**index

            # Показать или скрыть сетку если камера далеко:
            # if self.camera.zoom > 24*size/(index+1): grid[1] = 0 if grid[1] < 0 else grid[1]-.1*(delta_time*60)
            # else: grid[1] = 1 if grid[1] > 1 else grid[1] + 0.1 * (delta_time * 60)

            # Меняем альфа-канал сеткам в зависимости от их размера и зума камеры:
            grid[1] = size * 1/self.camera.zoom * self.all_alpha
            grid[1] = 0 if grid[1] < 0 else grid[1]
            grid[1] = 1 if grid[1] > 1 else grid[1]

            # Если alpha = 0, не продолжаем итерацию:
            if grid[1] <= 0.025: continue
            # Иначе если зум камеры меньше чем коэффициент и итерация больше 1:
            elif self.camera.zoom < size/len(self.grid_list)/2 and index > 0: continue

            # Цвет сетки:
            color = (
                (128 - (bg_color[0]*255)) % 128 / 255 if bg_color[0]*255 > 128 else (bg_color[0]*255) / 255 + 0.15,
                (128 - (bg_color[1]*255)) % 128 / 255 if bg_color[1]*255 > 128 else (bg_color[1]*255) / 255 + 0.15,
                (128 - (bg_color[2]*255)) % 128 / 255 if bg_color[2]*255 > 128 else (bg_color[2]*255) / 255 + 0.15
            )
            # color = (
            #     (128 - bg_color[0]) % 128 / 255 if bg_color[0] > 128 else bg_color[0] / 255 + 0.15*(index+1),
            #     (128 - bg_color[1]) % 128 / 255 if bg_color[1] > 128 else bg_color[1] / 255 + 0.15*(index+1),
            #     (128 - bg_color[2]) % 128 / 255 if bg_color[2] > 128 else bg_color[2] / 255 + 0.15*(index+1)
            # )

            # Отрисовываем сетку:
            gl.glLineWidth(1)
            # gl.glLineWidth(max(1, index*1.5))
            gl.glPushMatrix()
            gl.glTranslated(
                round(self.camera.position.x / self.camera.meter / size) * self.camera.meter * size,
                round(self.camera.position.y / self.camera.meter / size) * self.camera.meter * size, 0)
            gl.glScaled(size, size, 1.0)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, grid[0])
            gl.glVertexPointer(3, gl.GL_DOUBLE, 0, None)
            gl.glColor4f(*color, grid[1])
            gl.glDrawArrays(gl.GL_LINES, 0, len(self.vertices)//3)
            gl.glPopMatrix()

        if not gl.glIsEnabled(gl.GL_LINE_SMOOTH) and is_enabled: gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        outline_of_lines = (3 + 3) + 1  # В скобочках кол-во пикселей с двух сторон.

        # Отрисовка осей (X и Y):
        cpx = self.camera.position.x-((self.camera.width*self.camera.zoom)/2)*self.camera.meter
        cpy = self.camera.position.y-((self.camera.height*self.camera.zoom)/2)*self.camera.meter
        x_line = [(cpx, 0), (cpx+self.camera.width*self.camera.zoom*self.camera.meter, 0)]
        y_line = [(0, cpy), (0, cpy+self.camera.height*self.camera.zoom*self.camera.meter)]
        gl.glEnable(gl.GL_LINE_SMOOTH)

        # Линии:
        offset = (outline_of_lines*self.camera.meter/100) * self.camera.zoom
        gl.glLineWidth(1)
        gl.glBegin(gl.GL_LINES)
        gl.glColor4f(1.0, 0.1, 0.1, self.alpha_axis)
        gl.glVertex2d(*x_line[0])
        gl.glVertex2d(-offset, 0)
        gl.glVertex2d(+offset, 0)
        gl.glVertex2d(*x_line[1])
        gl.glColor4f(0.1, 1.0, 0.1, self.alpha_axis)
        gl.glVertex2d(*y_line[0])
        gl.glVertex2d(0, -offset)
        gl.glVertex2d(0, +offset)
        gl.glVertex2d(*y_line[1])
        gl.glEnd()
        gl.glDisable(gl.GL_LINE_SMOOTH)

        # Отрисовка точки в центре мировых координат:
        point_size = outline_of_lines * 1.5

        # Точка:
        gl.glPointSize(point_size*.45)
        gl.glBegin(gl.GL_POINTS)
        gl.glColor4f(1, 1, 1, self.alpha_axis)
        gl.glVertex2d(0, 0)
        gl.glEnd()

    # Удаляет буфер вершин (надо для освобождения памяти при закрытии программы):
    def destroy(self) -> None:
        vertex_buffers = [grid[0] for grid in self.grid_list]
        self.grid_list.clear()
        gl.glDeleteBuffers(len(vertex_buffers), vertex_buffers)
