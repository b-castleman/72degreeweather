# Get base image
FROM python:3.9

# Add source file (and destination)
ADD . .

RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt

CMD ["python","./runme.py"]

