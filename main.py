import pygame
import math

# Inicializa Pygame
pygame.init()

# Configurações da tela 2D
width, height = 1600, 900
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Trabalho 2 - Computação Gráfica')
clock = pygame.time.Clock()

# Configurações da tela 3D
screen3D = None

# Configurações do grid
cell_size = 20
grid_color = (0, 0, 0)

# Variáveis para a posição da câmera
camera_x = 0
camera_y = 0
camera_z = 0

# Variáveis para a rotação do objeto
rotation_x = 0
rotation_y = 0

# Variável para verificar se o botão do mouse está pressionado para rotação
mouse_pressed_for_rotation = False

# Fator de sensibilidade para a rotação
sensitivity_factor = 0.1  # Quanto menor o valor, menor a sensibilidade

# Variável para controlar a escala (zoom)
scale_factor = 1.0  # Valor inicial da escala

# Número de slices para revolucionar o perfil 2D
num_slices = 30

# Classe para representar o polígono
class Polygon:
    def __init__(self):
        self.points = []
        self.closed = False

    def add_point(self, point):
        if not self.closed:
            self.points.append(point)

    def close(self):
        if len(self.points) >= 2:
            self.points.append(self.points[0])  # Link the last point with the first one
            self.closed = True

    def draw(self):
        # Desenha os pontos do polígono
        for point in self.points:
            pygame.draw.circle(screen, (0, 0, 0), point, 3)

        # Desenha as arestas do polígono
        if len(self.points) >= 2:
            pygame.draw.lines(screen, (0, 0, 0), False, self.points, 2)

# Cria uma instância do polígono
polygon = Polygon()

# Função para atualizar a escala com base nas entradas do teclado
def update_scale(event, scale_factor):
    global num_slices  # Você pode precisar ajustar o número de slices para manter a aparência correta
    if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
        scale_factor *= 1.1  # Aumenta a escala em 10%
    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
        scale_factor /= 1.1  # Diminui a escala em 10%
    return scale_factor

# Função para atualizar a rotação do objeto com base no movimento do mouse
def update_rotation_on_mouse_motion(rotation_x, rotation_y, dx, dy, sensitivity_factor):
    rotation_x += dx * sensitivity_factor  # Movimento horizontal do mouse afeta a rotação em torno do eixo X
    rotation_y += dy * sensitivity_factor  # Movimento vertical do mouse afeta a rotação em torno do eixo Y
    return rotation_x, rotation_y

def update_camera(event, camera_x, camera_y, camera_z):
    if event.key == pygame.K_LEFT:
        camera_x -= 10
    elif event.key == pygame.K_RIGHT:
        camera_x += 10
    elif event.key == pygame.K_UP:
        camera_y -= 10
    elif event.key == pygame.K_DOWN:
        camera_y += 10
    elif event.key == pygame.K_a:  # Tecla 'A' para mover para frente (diminuir Z)
        camera_z -= 10
    elif event.key == pygame.K_d:  # Tecla 'D' para mover para trás (aumentar Z)
        camera_z += 10
    return camera_x, camera_y, camera_z

# Função para desenhar o grid
def draw_grid():
    for x in range(0, width, cell_size):
        pygame.draw.line(screen, grid_color, (x, 0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, grid_color, (0, y), (width, y))

# Função para revolucionar o perfil 2D e criar o wireframe 3D
def revolve_profile(profile, slices, angle_offset, rotation_x, rotation_y, scale_factor=1.0):
    revolved_points = []
    revolved_points_scaled = []
    cos_rx = math.cos(math.radians(rotation_x))
    sin_rx = math.sin(math.radians(rotation_x))
    cos_ry = math.cos(math.radians(rotation_y))
    sin_ry = math.sin(math.radians(rotation_y))
    
    for slice in range(slices):
        angle = math.radians(slice * (360 / slices) + angle_offset)
        for x, y in profile:
            # Calcula as coordenadas 3D rotacionadas
            rotated_x = x * math.cos(angle)
            rotated_z = x * math.sin(angle)
            
            # Aplica a rotação em torno do eixo Y
            yz = y * cos_ry - rotated_z * sin_ry
            zz = y * sin_ry + rotated_z * cos_ry
            
            # Aplica a rotação em torno do eixo X
            xy = rotated_x * cos_rx - yz * sin_rx
            yz = rotated_x * sin_rx + yz * cos_rx
            
            revolved_points.append((xy, yz, zz))

        for point in revolved_points:
            scaled_x = point[0] * scale_factor
            scaled_y = point[1] * scale_factor
            scaled_z = point[2] * scale_factor
            revolved_points_scaled.append((scaled_x, scaled_y, scaled_z))

    return revolved_points_scaled

# Função para desenhar o wireframe 3D
def draw_wireframe(points, slices, camera_x, camera_y, camera_z):
    for i in range(len(points)):
        # Ajusta os pontos para a profundidade da câmera
        z_adjusted_x = (points[i][0] - camera_z) + width // 2 - camera_x
        z_adjusted_y = (points[i][1] - camera_z) + height // 2 - camera_y
        next_z_adjusted_x = (points[(i + 1) % len(points)][0] - camera_z) + width // 2 - camera_x
        next_z_adjusted_y = (points[(i + 1) % len(points)][1] - camera_z) + height // 2 - camera_y
        pygame.draw.line(screen3D, (0, 0, 0), 
                         (z_adjusted_x, z_adjusted_y),
                         (next_z_adjusted_x, next_z_adjusted_y), 1)
    # Desenha as linhas verticais
    for i in range(slices):
        for j in range(len(polygon.points)):
            start_index = i * len(polygon.points) + j
            end_index = (start_index + len(polygon.points)) % len(points)
            # Ajusta os pontos para a profundidade da câmera
            start_z_adjusted_x = (points[start_index][0] - camera_z) + width // 2 - camera_x
            start_z_adjusted_y = (points[start_index][1] - camera_z) + height // 2 - camera_y
            end_z_adjusted_x = (points[end_index][0] - camera_z) + width // 2 - camera_x
            end_z_adjusted_y = (points[end_index][1] - camera_z) + height // 2 - camera_y
            pygame.draw.line(screen3D, (0, 0, 0), 
                             (start_z_adjusted_x, start_z_adjusted_y),
                             (end_z_adjusted_x, end_z_adjusted_y), 1)

# Main loop
running = True
angle_offset = 0  # Ângulo de rotação do wireframe 3D
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not polygon.closed:  # Only allow adding points if the polygon is not closed
                polygon.add_point(event.pos)
            mouse_pressed_for_rotation = True
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed_for_rotation = False
        if event.type == pygame.MOUSEMOTION:
            if mouse_pressed_for_rotation:
                rotation_x, rotation_y = update_rotation_on_mouse_motion(rotation_x, rotation_y, event.rel[0], event.rel[1], sensitivity_factor)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                polygon.close()
                if polygon.closed:
                    screen3D = pygame.display.set_mode((width, height))
                    pygame.display.set_caption('Trabalho 2 - Computação Gráfica - Wireframe 3D')
            camera_x, camera_y, camera_z = update_camera(event, camera_x, camera_y, camera_z)
            scale_factor = update_scale(event, scale_factor)

    screen.fill((255, 255, 255))

    # Desenha o perfil
    polygon.draw()

    # Desenha o grid
    draw_grid()

    # Se o polígono estiver fechado, revoluciona e desenha o wireframe 3D
    if polygon.closed and screen3D is not None:
        revolved_points = revolve_profile(polygon.points, num_slices, angle_offset, rotation_x, rotation_y, scale_factor)
        screen3D.fill((255, 255, 255))
        draw_wireframe(revolved_points, num_slices, camera_x, camera_y, camera_z)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()