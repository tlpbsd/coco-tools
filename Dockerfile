FROM jamieleecho/coco-dev:0.9

# Convenience for Mac users
RUN ln -s /home /Users

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install coco-tools
RUN mkdir coco-tools
WORKDIR coco-tools
COPY coco ./coco
COPY setup.py .
RUN ./setup.py install
WORKDIR ..

