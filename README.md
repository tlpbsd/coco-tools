# coco-tools
TRS-80 Color Computer Tools

- cm3toppm - convert RS-DOS CM3 images to PPM
- mgetoppm - convert RS-DOS MGE images to PPM
- veftopng - convert OS-9 VEF images to PNG


## Installation
You can create a coco-dev Docker image via:
```
./build-docker-image
```

You can run tools in that Docker image via a command like:
```
./coco-dev veftopng coco/samples/simpson.vef simpsons.png
```

Alternatively, you can install veftopng directly to your system via
the following:
```
./setup.py install
```

