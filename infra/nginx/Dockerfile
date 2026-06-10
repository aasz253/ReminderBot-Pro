FROM nginx:1.25-alpine

RUN apk add --no-cache certbot py3-pip 2>/dev/null; \
    pip3 install --break-system-packages certbot-nginx 2>/dev/null || true

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /var/www/certbot /var/log/nginx

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
