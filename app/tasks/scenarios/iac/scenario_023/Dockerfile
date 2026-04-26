FROM node:latest

ENV NPM_TOKEN=npm_EXAMPLE_FAKE_TOKEN_HERE
ENV MONGODB_URI=mongodb://admin:RootPass2023@db:27017/prod

ADD https://github.com/example/scripts/raw/main/setup.sh /setup.sh
RUN bash /setup.sh

COPY package.json package-lock.json ./
RUN npm install --unsafe-perm --allow-root

COPY . /app
WORKDIR /app

EXPOSE 3000
EXPOSE 9229

CMD ["node", "--inspect=0.0.0.0:9229", "server.js"]
