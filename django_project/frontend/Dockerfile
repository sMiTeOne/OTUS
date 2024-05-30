FROM nginx:alpine

RUN mkdir -p /var/www/main/static
ADD ./static /var/www/main/static
ADD ./nginx.conf /etc/nginx/conf.d/default.conf
