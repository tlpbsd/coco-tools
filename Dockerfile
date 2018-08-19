FROM jamieleecho/coco-dev:0.9

# Install coco-tools
RUN mkdir coco-tools
WORKDIR coco-tools
COPY vef2png ./vef2png
COPY setup.py .
RUN ./setup.py install
WORKDIR ..

