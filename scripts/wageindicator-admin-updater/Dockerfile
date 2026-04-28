FROM mcr.microsoft.com/playwright:v1.59.1-jammy

WORKDIR /app

COPY package.json package.json
RUN npm install

COPY . .

CMD ["npm", "run", "update"]
