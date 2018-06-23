FROM pykaldi/pykaldi:latest

LABEL maintainer "Sean2525 <madness48596@gmail.com>"

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "runtime.py" ] 
