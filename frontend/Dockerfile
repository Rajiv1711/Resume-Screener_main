# syntax=docker/dockerfile:1

# Production build for React frontend served by nginx
FROM node:20-alpine AS build
WORKDIR /app

ENV CI=true NODE_ENV=production

# Install deps with caching
COPY package*.json ./
RUN if [ -f package-lock.json ]; then \
      echo "Using npm ci" && npm ci; \
    else \
      echo "Using npm install" && npm install; \
    fi

# Copy source and build
COPY . .

# Build-time API base URL (must start with REACT_APP_ for CRA)
ARG REACT_APP_API_BASE_URL=http://backend:8000/api
ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}
RUN npm run build

# --- Runtime: Nginx ---
FROM nginx:alpine AS runtime

# Install curl for healthcheck
RUN apk add --no-cache curl

# Harden nginx and enable SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static files
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://127.0.0.1:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
