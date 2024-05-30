FROM nginx:alpine

RUN mkdir -p /var/www/hasker/static
ADD ./static /var/www/hasker/static
ADD ./nginx.conf /etc/nginx/conf.d/default.conf
