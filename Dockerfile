FROM python:3.7

ENV TZ 'Asia/Shanghai'
ENV PYTHONUNBUFFERED '0'

WORKDIR /app

COPY requirements.txt requirements.txt

RUN set -ex && pip install -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple

COPY . /app

EXPOSE 5500
EXPOSE 5510

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
CMD "pyco"