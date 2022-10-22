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

# zoom rate = 1 / zoom
# def is default
def_zoom = 500
zoom = def_zoom
zoom_speed = 1.5
# base offset to transform the coordinates with 0,0 in the center
# vertical flipping not included here, and is done in the proceeding function
base_offset = scr_size_array // 2
base_offset[0] += 300
# the below offset should be applied before zoom
offset = np.array([0,0],dtype='float64')
# offset speed is dependent on the zoom_speed, so will have to be recomputed as necessary
base_num = def_zoom * 0.5
offset_speed = base_num / zoom
max_iter = 50
max_iter_speed = 5
dirty = 1

# unfortunately i can't get the parallelization to work, it's the same fps with it or without
@numba.njit(parallel=True)
def generate_fractal(canvas_array,palette_array,max_iter,base_offset,offset,zoom):
    # the max_iter being accessed here is not the same as the state of the global, it is converted to integer before putting in
    for row in numba.prange(canvas_array.shape[0]):
        for col in range(canvas_array.shape[1]):
            coord = np.array([row,canvas_array.shape[1]-col],dtype='float64')
            coord -= base_offset
            coord += offset
            coord = offset - ((offset - coord) / zoom)
            c = np.cdouble(coord[0] + coord[1] * 1j)
            num_iter = 0
            z = np.cdouble(0+0j)
            for i in range(max_iter):
                z = (z ** 2) + c
                if np.abs(z) > 2:
                    break
                num_iter += 1
            if num_iter >= max_iter:
                num_iter = max_iter-1
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
# 1 for up
# -1 for down

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
                # zoom rate = 1 / zoom
                # def is default
                def_zoom = 500
                zoom = def_zoom
                zoom_speed = 1.5
                # base offset to transform the coordinates with 0,0 in the center
                # vertical flipping not included here, and is done in the proceeding function
                base_offset = scr_size_array // 2
                base_offset[0] += 300
                # the below offset should be applied before zoom
                offset = np.array([0,0],dtype='float64')
                # offset speed is dependent on the zoom_speed, so will have to be recomputed as necessary
                base_num = def_zoom * 0.5
                offset_speed = base_num / zoom
                max_iter = 50
                max_iter_speed = 5
                dirty = 1
            
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
        if r_p_zoom == 1:
            zoom *= zoom_speed
            max_iter += max_iter_speed
        else:
            zoom /= zoom_speed
            max_iter -= max_iter_speed
    
    if max_iter < 1:
        max_iter = 1
    
    if r_p_h_pan:
        dirty = 1
        if r_p_h_pan == 1:
            offset[0] += offset_speed
        else:
            offset[0] -= offset_speed
    
    if r_p_v_pan:
        dirty = 1
        if r_p_v_pan == 1:
            offset[1] += offset_speed
        else:
            offset[1] -= offset_speed

    if dirty:
        canvas_array = generate_fractal(canvas_array,palette_array,int(max_iter),base_offset,offset,zoom)
        pygame.surfarray.blit_array(scr,canvas_array)
        pygame.display.update()
    dirty = 0

    pygame.display.set_caption('FPS :' + str(int(clock.get_fps())))
    dt = clock.tick(300)

pygame.quit()
sys.exit()
