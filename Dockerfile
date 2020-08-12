FROM python:3.8-slim
RUN pip3 install pyyaml
COPY deployment-mapper.py /deployment-mapper.py 
ENTRYPOINT ["python3", "/deployment-mapper.py"]
