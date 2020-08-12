FROM python:3.8-alpine
COPY deployment-mapper.py /deployment-mapper.py 
ENTRYPOINT ["python3", "/deployment-mapper.py"]
