# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:26.5.0 AS build-stage

WORKDIR /app

RUN npm install --global npm@12.0.1

COPY package*.json /app/

RUN npm ci

COPY ./ /app/

# Docker Compose or a direct local build supplies this argument. Unset is valid
# for relative/local API configurations and avoids an undefined self-default.
ARG VITE_API_URL
# Non-secret display configuration. Authorization remains backend-owned.
ARG VITE_ENABLE_PUBLIC_SIGNUP=false
# Non-secret preview presentation bound; private delivery remains backend-owned.
ARG VITE_HTML_PREVIEW_MAX_BYTES=5242880

RUN npm run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1.31.3

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf

# Check Nginx from inside the container so Docker Compose can reject an image
# that started a process but cannot serve frontend requests.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail --silent --show-error http://127.0.0.1/health > /dev/null || exit 1
