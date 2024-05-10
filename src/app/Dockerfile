FROM node:14-slim

WORKDIR /usr/local/src
COPY ./src/app/package.json ./src/app/yarn.lock ./
RUN yarn install

COPY . .

EXPOSE 6543

CMD ["yarn", "run", "start"]