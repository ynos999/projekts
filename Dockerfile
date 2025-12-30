FROM python:3.13.3

ENV TZ=Europe/Riga
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DEBUG=False
ENV ENABLE_RECAPTCHA=True
ENV PRODUCTION=True

RUN apt-get update && apt-get -y install \
    nano

RUN pip install --upgrade pip

WORKDIR /usr/src/app

# 1. VISPIRMS izveidojam mapes
RUN mkdir -p /static /media

# 2. TAD izveidojam lietotāju (lai chown zinātu, kas ir "django")
RUN adduser --system --no-create-home --uid 9000 --group --disabled-password django

# 3. TAGAD piešķiram tiesības
RUN chown -R django:django /usr/src/app /static /media

# 4. Sagatavojam atkarības
COPY requirements.txt .
COPY entrypoint.sh .
RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh

# Pārslēdzamies uz lietotāju pirms koda kopēšanas
USER django

# 5. Nokopējam projektu (tagad tas piederēs django lietotājam)
COPY --chown=django:django . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]