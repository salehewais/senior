# Production storefront. The Vite dev server is not this image.
# VITE_API_BASE_URL is the public gateway origin the browser calls.
FROM node:22-alpine AS build

WORKDIR /src

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html vite.config.ts tsconfig.json tsconfig.app.json tsconfig.node.json ./
COPY src ./src

ARG VITE_API_BASE_URL=http://127.0.0.1:8080
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /src/dist /usr/share/nginx/html

RUN apk add --no-cache wget \
    && mkdir -p /tmp/nginx_client_temp /tmp/nginx_proxy_temp /tmp/nginx_fastcgi_temp /tmp/nginx_uwsgi_temp /tmp/nginx_scgi_temp \
    && chown -R nginx:nginx /usr/share/nginx/html /tmp/nginx_client_temp /tmp/nginx_proxy_temp /tmp/nginx_fastcgi_temp /tmp/nginx_uwsgi_temp /tmp/nginx_scgi_temp

USER nginx
EXPOSE 8080

# nginx is PID 1. The official entrypoint script is not used, so it cannot swallow SIGTERM.
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
