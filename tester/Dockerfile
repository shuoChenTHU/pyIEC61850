FROM python:3.10-alpine

# Install libstdc++ as a runtime dependency.
RUN apk add --no-cache libstdc++

WORKDIR /work
COPY . /work
# Uncomment the following line if you need to install Python packages:
# RUN pip install -r requirements.txt
ENV PYTHONPATH=/work
RUN chmod +x /work/_iec61850.so
CMD ["python", "/work/demovirtualcls.py"]