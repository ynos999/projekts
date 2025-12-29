FROM python:3.13.0

ENV TZ=Europe/Riga
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DEBUG=False
ENV ENABLE_RECAPTCHA=True
ENV PRODUCTION=True

# Atjauno pip versiju
RUN pip install --upgrade pip

# Uztaisam darba direktoriju
WORKDIR /usr/src/app

#Uztaisa linux lietotāju
RUN adduser --system --no-create-home --uid 9000 --group --disabled-password --disabled-login --gecos 'gunicorn django user' django

# Nokopet failus direktorija
COPY requirements requirements/


# Ieinstalet modulus no saraksta
RUN pip install -r requirements/production.txt

# Parkope
COPY . .


RUN apt-get update && apt-get -y install \
    nano