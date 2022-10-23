import numba, pygame, sys, os, numpy as np

pygame.init()
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

scr_size = (1920,1020)
scr = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
scr_size_array = np.array(scr_size)

canvas_array = pygame.surfarray.array3d(scr)

dir_path = os.path.dirname(os.path.realpath(__file__))
palette = pygame.image.load(dir_path+'/palette.png')
palette_array = pygame.surfarray.array3d(palette)
# palette_array = np.flip(palette_array,axis=0)

def init_values():
    global def_zoom, zoom, zoom_speed, base_offset, offset, base_num, offset_speed, max_iter, max_iter_speed, max_iter_min, max_iter_max, dirty
    # zoom rate = 1 / zoom
    # def is default
    def_zoom = 500
    zoom = def_zoom
    zoom_speed = 1.01
    # base offset to transform the coordinates with 0,0 in the center
    base_offset = scr_size_array // 2
    # offset to determine which point will be at the center of the screen
    # used as the focus point for zoom
    offset = np.array([-0.6,0],dtype='float64')
    # offset speed is dependent on the zoom_speed, so will have to be recomputed as necessary
    base_num = (def_zoom * 0.5) / 30
    offset_speed = base_num / zoom
    max_iter = 50
    max_iter_speed = 0.2
    max_iter_min = 2
    max_iter_max = 500
    dirty = 1

    # if ever a button to change zoom_speed is introduced, this must also change max_iter at the same proportion (note that the former is a factor and modified by a t_factor exponentially, and the latter is an addend and modified by a t_factor multiplicatively), however offset_speed is already based off of zoom_speed 

init_values()

dt = 33.33
base_fps = 30
t_fact = dt * (base_fps/1000)

@numba.njit(parallel=True)
def generate_fractal(canvas_array,max_iter,offset,zoom):
    for row in numba.prange(canvas_array.shape[0]):
        for col in range(canvas_array.shape[1]):
            c = (row - base_offset[0]) / zoom + offset[0] + 1j * ((col - base_offset[1]) / zoom + offset[1])
            num_iter = 0
            z = np.cdouble(0+0j)
            for i in range(max_iter-1):
                z = (z ** 2) + c
                if z.real ** 2 + z.imag ** 2 > 4:
                    break
                num_iter += 1
            v = int(palette_array.shape[0] * num_iter / max_iter)
            canvas_array[row,col] = palette_array[v,0]
    return canvas_array

# r_p = recently_pressed
r_p_zoom = 0
# 1 for zoom in
# 2 for zoom out

r_p_h_pan = 0
# 1 for right
# -1 for left

r_p_v_pan = 0
# 1 for down
# -1 for up
# flipped because pygame origin is at the topleft
# also, the coordinates were not flipped in the updating function as mandelbrot is symmetrical with the x-axis

is_running = True
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                r_p_zoom = 2
            if event.key == pygame.K_x:
                r_p_zoom = 1
            if event.key == pygame.K_LEFT:
                r_p_h_pan = -1
            if event.key == pygame.K_RIGHT:
                r_p_h_pan = 1
            if event.key == pygame.K_UP:
                r_p_v_pan = 1
            if event.key == pygame.K_DOWN:
                r_p_v_pan = -1
            if event.key == pygame.K_v:
                max_iter += 10
                dirty = 1
            if event.key == pygame.K_c:
                max_iter -= 10
                dirty = 1
            if event.key == pygame.K_s:
                init_values()
            
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_z and r_p_zoom == 2:
                r_p_zoom = 0
            if event.key == pygame.K_x and r_p_zoom == 1:
                r_p_zoom = 0
            if event.key == pygame.K_LEFT and r_p_h_pan == -1:
                r_p_h_pan = 0
            if event.key == pygame.K_RIGHT and r_p_h_pan == 1:
                r_p_h_pan = 0
            if event.key == pygame.K_UP and r_p_v_pan == 1:
                r_p_v_pan = 0
            if event.key == pygame.K_DOWN and r_p_v_pan == -1:
                r_p_v_pan = 0

    if r_p_zoom:
        dirty = 1
        offset_speed = (base_num / zoom)
        dzoom = zoom_speed ** t_fact
        dmax_iter = max_iter_speed * t_fact
        if r_p_zoom == 1:
            zoom *= dzoom
            max_iter += dmax_iter
        else:
            zoom /= dzoom
            max_iter -= dmax_iter
    
    max_iter = max(max_iter,max_iter_min)
    max_iter = min(max_iter,max_iter_max)
    
    if r_p_h_pan:
        dirty = 1
        if r_p_h_pan == 1:
            offset[0] += offset_speed * t_fact
        else:
            offset[0] -= offset_speed * t_fact
    
    if r_p_v_pan:
        dirty = 1
        if r_p_v_pan == 1:
            offset[1] -= offset_speed * t_fact
        else:
            offset[1] += offset_speed * t_fact

    if dirty:
        canvas_array = generate_fractal(canvas_array,int(max_iter),offset,zoom)
        pygame.surfarray.blit_array(scr,canvas_array)
        pygame.display.update()
    dirty = 1
    # ^ resetting dirty to 0 has been disabled to better monitor fps

    pygame.display.set_caption(f'FPS: {clock.get_fps():.2f} | zoom: {zoom:.2f} | max_iter: {int(max_iter)}')
    
    dt = clock.tick(150)
    t_fact = dt * (base_fps/1000)

pygame.quit()
sys.exit()
