import taichi as ti, taichi.math as tm, numpy as np
import os, time, datetime

ti.init(arch=ti.gpu,default_fp=ti.f64)

# screen size
width, height = 1920,1020
pixels = ti.Vector.field(3,ti.uint8,shape=(width,height))
# palette
dir_path = os.path.dirname(os.path.realpath(__file__))
palette1_array = ti.tools.imread(dir_path+'/palettes/slso8-1x.png',3)
palette1 = ti.Vector.field(3, ti.uint8, (palette1_array.shape[0],palette1_array.shape[1]))
palette1.from_numpy(palette1_array)

palette2_array = ti.tools.imread(dir_path+'/palettes/apollo-1x.png',3)
palette2_array[-1,0] = [0,0,0]
palette2 = ti.Vector.field(3, ti.uint8, (palette2_array.shape[0],palette2_array.shape[1]))
palette2.from_numpy(palette2_array)

palettes = {'1':palette1,'2':palette2}

active_palette = palettes['1']
to_interpolate = 1

# base offset to transform the coordinates with 0,0 in the center
base_offset = np.array((width,height)) // 2

# default values
def init_values():
    global max_iter, max_iter_speed, max_iter_min, max_iter_max, def_zoom, zoom, zoom_speed, offset, base_num, offset_speed

    # max iterations
    max_iter = 50
    max_iter_speed = 0.2
    max_iter_min = 2
    max_iter_max = 1000

    # zoom
    def_zoom = 2.04 / height
    zoom = def_zoom
    zoom_speed = 0.99

    # offset speed is dependent on zoom, so will have to be recomputed as necessary
    offset = np.array([-0.6,0],dtype='float64')
    base_num = def_zoom * 4167
    offset_speed = base_num * zoom

    # max_iter_speed does not scale off of zoom_speed, so if ever it is changed/a button is introduced that changes it, it may be desired to scale it accordingly
    # offset_speed scales off of zoom

init_values()

# override values here
# for when you want to temporarily test a certain configuration
# zoom_speed = 0.9

@ti.kernel
def render(active_palette: ti.template(), palette_length :ti.uint8, to_interpolate: ti.uint8, max_iter: ti.uint16, offset: ti.types.ndarray(), zoom: ti.f64):
    # max_iter should be converted to python int before being passed here
    ti.loop_config(block_dim=1024)
    for x,y in pixels:
        c = tm.vec2((x - base_offset[0]) * zoom + offset[0], (y - base_offset[1]) * zoom + offset[1])
        z = tm.vec2(0.0, 0.0)
        num_iter = 0
        while num_iter < max_iter and tm.dot(z,z) < 4:
            z = tm.cmul(z,z) + c
            num_iter += 1
        v = 0.0
        col = ti.cast(tm.vec3(0,0,0), ti.uint8)
        if num_iter == max_iter: 
            col = active_palette[palette_length-1,0]
        else:
            v = (palette_length - 2) * num_iter / max_iter
            if to_interpolate == 0:
                col = active_palette[ti.cast(tm.round(v),ti.uint8),0]
            else:
                q,e = tm.floor(v),tm.ceil(v)
                col = ti.cast(tm.mix(active_palette[int(q),0],active_palette[int(e),0],v-int(v)),ti.uint8)
        pixels[x,y] = col

gui = ti.GUI('Mandelbrot Explorer', res=(width,height), fast_gui=True)

t0 = time.time_ns()
nano_to_mil = 1 / 1000000
dt = 33.33
base_fr = 30/1000
t_fact = dt * base_fr

pressed_zoom = []
pressed_h_pan = []
pressed_v_pan = [] 
pressed_mi = []

keytonum = {'z': -1, 'x': 1, ti.ui.LEFT: -1, ti.ui.RIGHT: 1, ti.ui.UP: 1, ti.ui.DOWN: -1, 'v': 1, 'c': -1}

keystolist = {('z','x'): pressed_zoom, (ti.ui.LEFT,ti.ui.RIGHT): pressed_h_pan, (ti.ui.UP,ti.ui.DOWN): pressed_v_pan, ('v','c'): pressed_mi}

# change curdir to screenshots folder
if not os.path.exists(f'{dir_path}/screenshots'): 
    os.makedirs(f'{dir_path}/screenshots')
os.chdir(f'{dir_path}/screenshots')

while gui.running:
    for event in gui.get_events():
        if event.type == ti.GUI.PRESS:
            if event.key == ti.ui.ESCAPE: gui.running = False
            if event.key == 'r': init_values()
            if event.key == 's': 
                name = str(datetime.datetime.now()).replace(':','-')
                ti.tools.imwrite(pixels, f'{name}.png')
            if event.key in palettes:
                active_palette = palettes[event.key]
            if event.key == 'e':
                to_interpolate = not to_interpolate
            for k,v in keystolist.items():
                if event.key in k and event.key not in v:
                    v.append(event.key)
                    break

        if event.type == ti.GUI.RELEASE:
            for v in keystolist.values():
                if event.key in v:
                    v.remove(event.key)
                    break
    
    if pressed_zoom:
        offset_speed = base_num * zoom
        dzoom = zoom_speed ** t_fact
        dmax_iter = max_iter_speed * t_fact
        zoom *= dzoom ** keytonum[pressed_zoom[-1]]

        if keytonum[pressed_zoom[-1]] == 1: 
            if max_iter < max_iter_max: max_iter += dmax_iter
        else:
            max_iter -= dmax_iter
    
    if pressed_mi:
        max_iter += 3 * t_fact * keytonum[pressed_mi[-1]]
    
    max_iter = max(max_iter,max_iter_min)

    if pressed_h_pan:
        offset[0] += offset_speed * t_fact * keytonum[pressed_h_pan[-1]]
    
    if pressed_v_pan:
        offset[1] += offset_speed * t_fact * keytonum[pressed_v_pan[-1]]
    
    render(active_palette, active_palette.shape[0], to_interpolate, int(max_iter),offset,zoom)
    gui.set_image(pixels)
    gui.show()

    t1 = time.time_ns()
    dt = (t1 - t0) * nano_to_mil
    t0 = t1
    t_fact = dt * base_fr

print(zoom)
print(offset)
print(max_iter)
