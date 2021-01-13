FROM python:3.8.5
COPY requirements.txt /src/requirements.txt
RUN pip install --upgrade pip
WORKDIR /src
RUN pip install -r /src/requirements.txt
COPY app.py /src
COPY api /src/api
COPY model /src/model
COPY database /src/database
COPY data_access /src/data_access
COPY swagger.yml /src
CMD python /src/app.py

