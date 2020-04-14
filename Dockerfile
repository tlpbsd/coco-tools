FROM jamieleecho/coco-dev:0.19

# Convenience for Mac users
RUN ln -s /home /Users

# Install requirements
COPY requirements.txt .
RUN \
  python2 /usr/bin/pip2 install -r requirements.txt && \
  pip3 install -r requirements.txt

# Install coco-tools
RUN mkdir coco-tools-build
WORKDIR coco-tools-build
COPY setup.py .
COPY coco ./coco
RUN \
  python2 setup.py install && \
  python3 setup.py install
WORKDIR ..

