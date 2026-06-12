FROM mcr.microsoft.com/playwright:v1.60.0

COPY package.json package-lock.json playwright.config.ts ./
COPY ./tests ./tests
RUN npm ci --ignore-scripts

ENTRYPOINT [ "npx", "playwright", "test" ]