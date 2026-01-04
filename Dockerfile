FROM python:3.13.3

ENV TZ=Europe/Riga
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG=False
ENV ENABLE_RECAPTCHA=True
ENV PRODUCTION=True

RUN apt-get update && apt-get -y install nano && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /usr/src/app

# 1. Izveidojam mapes un lietotāju (kā root)
RUN mkdir -p /static /media && \
    adduser --system --no-create-home --uid 9000 --group --disabled-password django

# 2. Instalējam atkarības (kā root - ātrākai būvēšanai)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Nokopējam VISU projektu (ieskaitot entrypoint.sh un fixturas.json)
COPY . .

# 4. Svarīgākais solis: Piešķiram tiesības visam projekta saturam
# Šis jādara PIRMS pārslēgšanās uz USER django
RUN chown -R django:django /usr/src/app /static /media && \
    chmod +x /usr/src/app/entrypoint.sh

# 5. Tagad droši pārslēdzamies uz ierobežoto lietotāju
USER django

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]