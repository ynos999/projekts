FROM nginx:1.22.0

ENV TZ=Europe/Riga
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# RUN rm /etc/nginx/conf.d/default.conf
# Izdzēšam VISU, kas ir conf.d mapē, lai tur nebūtu default.conf
RUN rm /etc/nginx/conf.d/*

# Kopējam tavu site.conf (pārliecinies par ceļu, ja tas ir tajā pašā mapē)
COPY site.conf /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
# COPY site.conf /etc/nginx/conf.d/site.conf

RUN apt-get update && apt-get -y install \
    nano