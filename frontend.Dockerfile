# Stage 1: Build Angular App
FROM node:20 AS build-stage
WORKDIR /app
# We use build context from the root, so copy from frontend/ folder
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
# Ensure we copy from the correct dist folder structure
# Angular 17+ uses dist/project-name/browser usually, but our angular.json
# specifies outputPath as dist/etrade-angular-ui.
COPY --from=build-stage /app/dist/etrade-angular-ui /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
