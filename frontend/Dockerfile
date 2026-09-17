FROM node:20-alpine

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./

ENV NEXT_TELEMETRY_DISABLED=1

EXPOSE 3000

ENV NODE_ENV=production

RUN npm run build

CMD ["npm", "start"]
