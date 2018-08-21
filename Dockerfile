FROM jamieleecho/coco-dev:0.9

# Install coco-tools
RUN mkdir coco-tools
WORKDIR coco-tools
COPY coco ./coco
COPY setup.py .
RUN ./setup.py install
WORKDIR ..

