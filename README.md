# coco-tools
TRS-80 Color Computer Tools

- cm3toppm - convert RS-DOS CM3 images to PPM
- hrstoppm - convert RS-DOS HRS images to PPM
- maxtoppm - convert RS-DOS MAX images to PPM
- mgetoppm - convert RS-DOS MGE images to PPM
- pixtopgm - convert RS-DOS PIX images to PGM
- rattoppm - convert RS-DOS RAT images to PPM
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

Alternatively, you can install coco-tools directly to your system via
the following:
```
./setup.py install
```

## Running Tests
Tests are run against the Docker enviornment via:
```
./run-tests
```

You can also run a smaller subset of tests via a command like:
```
./run-tests tests.coco.test_util
```
