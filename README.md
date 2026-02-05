# Hardware Control
```main.py``` is the script that starts the user interface for hardware control. It uses [https://nicegui.io/](https://nicegui.io/), and the different device drivers can be found in the ```hardware``` folder.

# Analysis and Figures
```figures.py``` is the script that generates the figures. The data can be downloaded at [zenodo](https://doi.org/10.5281/zenodo.18433941).

We provide two datasets for the maps, the one used throughout the manuscript is in lines 17, 18. The second dataset was acquired on another day (sanity check) and can be visualized by removing the comments in lines 21-24.

# Environment
It was during this project that I discovered [PIXI](https://pixi.prefix.dev/latest/), and while I used it for the [simulations repository](https://github.com/Omnistic/residual_ellipticity_in_pshg_simulations), I do not have it in this repository (and I deeply regret it).

The main packages used are:
- ```numpy```
- ```plotly```
- ```nicegui```
- ```scipy```
- ```pyvisa```
- ```nidaqmx```

And this is my environment:
```
# Name                    Version                   Build  Channel
aiofiles                  23.2.1                   pypi_0    pypi
aiohttp                   3.9.5                    pypi_0    pypi
aiosignal                 1.3.1                    pypi_0    pypi
annotated-types           0.6.0                    pypi_0    pypi
anyio                     4.3.0                    pypi_0    pypi
async-timeout             4.0.3                    pypi_0    pypi
attrs                     23.2.0                   pypi_0    pypi
bidict                    0.23.1                   pypi_0    pypi
bottle                    0.12.25                  pypi_0    pypi
bzip2                     1.0.8                h2bbff1b_5
ca-certificates           2024.3.11            haa95532_0
certifi                   2024.2.2                 pypi_0    pypi
cffi                      1.16.0                   pypi_0    pypi
choreographer             1.2.0                    pypi_0    pypi
click                     8.1.7                    pypi_0    pypi
clr-loader                0.2.6                    pypi_0    pypi
colorama                  0.4.6                    pypi_0    pypi
contourpy                 1.2.1                    pypi_0    pypi
cycler                    0.12.1                   pypi_0    pypi
deprecation               2.1.0                    pypi_0    pypi
docutils                  0.19                     pypi_0    pypi
exceptiongroup            1.2.0                    pypi_0    pypi
fastapi                   0.109.2                  pypi_0    pypi
fonttools                 4.51.0                   pypi_0    pypi
frozenlist                1.4.1                    pypi_0    pypi
h11                       0.14.0                   pypi_0    pypi
hightime                  0.2.2                    pypi_0    pypi
httpcore                  1.0.5                    pypi_0    pypi
httptools                 0.6.1                    pypi_0    pypi
httpx                     0.27.0                   pypi_0    pypi
idna                      3.7                      pypi_0    pypi
ifaddr                    0.2.0                    pypi_0    pypi
iniconfig                 2.3.0                    pypi_0    pypi
itsdangerous              2.2.0                    pypi_0    pypi
jinja2                    3.1.3                    pypi_0    pypi
kaleido                   1.1.0                    pypi_0    pypi
kiwisolver                1.4.5                    pypi_0    pypi
libffi                    3.4.4                hd77b12b_0
logistro                  2.0.1                    pypi_0    pypi
markdown2                 2.4.13                   pypi_0    pypi
markupsafe                2.1.5                    pypi_0    pypi
matplotlib                3.8.4                    pypi_0    pypi
multidict                 6.0.5                    pypi_0    pypi
narwhals                  2.10.1                   pypi_0    pypi
nicegui                   1.4.22                   pypi_0    pypi
nidaqmx                   0.9.0                    pypi_0    pypi
numpy                     1.26.4                   pypi_0    pypi
openssl                   3.0.13               h2bbff1b_0
orjson                    3.11.4                   pypi_0    pypi
packaging                 24.0                     pypi_0    pypi
pandas                    2.2.3                    pypi_0    pypi
patsy                     1.0.1                    pypi_0    pypi
pillow                    10.3.0                   pypi_0    pypi
pip                       23.3.1          py310haa95532_0
plotly                    6.3.1                    pypi_0    pypi
plotly-express            0.4.1                    pypi_0    pypi
pluggy                    1.6.0                    pypi_0    pypi
proxy-tools               0.1.0                    pypi_0    pypi
pscript                   0.7.7                    pypi_0    pypi
pycparser                 2.22                     pypi_0    pypi
pydantic                  2.7.0                    pypi_0    pypi
pydantic-core             2.18.1                   pypi_0    pypi
pygments                  2.17.2                   pypi_0    pypi
pyparsing                 3.1.2                    pypi_0    pypi
pyserial                  3.5                      pypi_0    pypi
pytest                    8.4.2                    pypi_0    pypi
pytest-timeout            2.4.0                    pypi_0    pypi
python                    3.10.14              he1021f5_0
python-dateutil           2.9.0.post0              pypi_0    pypi
python-dotenv             1.0.1                    pypi_0    pypi
python-engineio           4.9.0                    pypi_0    pypi
python-multipart          0.0.9                    pypi_0    pypi
python-socketio           5.11.2                   pypi_0    pypi
pythonnet                 3.0.3                    pypi_0    pypi
pytz                      2025.1                   pypi_0    pypi
pyvisa                    1.14.1                   pypi_0    pypi
pywebview                 5.1                      pypi_0    pypi
pyyaml                    6.0.1                    pypi_0    pypi
scipy                     1.13.0                   pypi_0    pypi
setuptools                68.2.2          py310haa95532_0
simple-websocket          1.0.0                    pypi_0    pypi
simplejson                3.20.2                   pypi_0    pypi
six                       1.16.0                   pypi_0    pypi
sniffio                   1.3.1                    pypi_0    pypi
sqlite                    3.41.2               h2bbff1b_0
starlette                 0.36.3                   pypi_0    pypi
statsmodels               0.14.4                   pypi_0    pypi
tenacity                  8.2.3                    pypi_0    pypi
tk                        8.6.12               h2bbff1b_0
tomli                     2.3.0                    pypi_0    pypi
typing-extensions         4.11.0                   pypi_0    pypi
tzdata                    2025.1                   pypi_0    pypi
uvicorn                   0.29.0                   pypi_0    pypi
vbuild                    0.8.2                    pypi_0    pypi
vc                        14.2                 h21ff451_1
vs2015_runtime            14.27.29016          h5e58377_2
watchfiles                0.21.0                   pypi_0    pypi
websockets                12.0                     pypi_0    pypi
wheel                     0.41.2          py310haa95532_0
wsproto                   1.2.0                    pypi_0    pypi
xz                        5.4.6                h8cc25b3_0
yarl                      1.9.4                    pypi_0    pypi
zlib                      1.2.13               h8cc25b3_0
```
