# ---- Build stage ----
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Serve stage ----
FROM nginx:alpine

# SPA routing config (fall back to index.html for client-side routes)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Angular 17 application builder outputs to dist/frontend/browser
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80
