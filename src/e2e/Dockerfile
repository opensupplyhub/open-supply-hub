FROM mcr.microsoft.com/playwright:v1.48.1

COPY package.json package-lock.json playwright.config.ts ./
COPY ./tests ./tests
RUN npm ci

ENTRYPOINT [ "" ]