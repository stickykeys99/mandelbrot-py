# mandelbrot-py

python (3.10.8)  
pygame (2.1.2)  
numba (0.56.3)  
numpy (1.23.4)  

Palette from https://lospec.com/palette-list/slso8  
SLSO8 by Luis Miguel Maldonado

## Stuff

Tested at 1920 x 1020 resolution with 50 as default max number of iterations. Please note that this resolution is not dynamic, so you would have to manually edit this yourself for different screen sizes. (It's just a tuple, the rest of the work is done for you.)

Runs at 30 fps with these settings, scales down decently up to ~2fps minimum. All of this tested on this local machine.

Exploring the fractal via the controls below is frame-agnostic.

## Controls

z - zoom out, x - zoom in  
c - decrease focus, v - increase  
arrow keys to move

s to set back defaults (go back to default view)

Note that zooming increases/decreases focus by a fixed small value. You would not normally have to increase/decrease focus yourself as this is automatically scaled by proportion.

## Screenshots

![scrnshot.png](screenshots/scrnshot.png)

![scrnshot2.png](screenshots/scrnshot2.png)

![scrnshot3.png](screenshots/scrnshot3.png)

![scrnshot4.png](screenshots/scrnshot4.png)
