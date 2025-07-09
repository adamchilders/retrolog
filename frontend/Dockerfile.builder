# frontend/Dockerfile.builder

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./

# This Dockerfile is only for building the React app, not serving it.
# The build output will be mounted to a volume for the appserver to use.
