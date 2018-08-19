# coco-tools
TRS-80 Color Computer Tools

- vef2png - convert OS-9 VEF images to PNG


## Installation
You can create a coco-dev Docker image via:
```
./build-docker-image
```

You can run tools in that Docker image via a command like:
```
./coco-dev vef2png vef2png/samples/simpson.vef simpsons.png
```

Alternatively, you can install vef2png directly to your system via
the following:
```
./setup.py install
```

