FROM node:alpine


# --no-cache: download package index on-the-fly, no need to cleanup afterwards
# --virtual: bundle packages, remove whole bundle at once, when done
RUN apk --no-cache --virtual build-dependencies add \
    python \
    git \
    make \
    g++ \
    openssl
RUN mkdir -p /app
COPY package.json /app/
RUN npm install
RUN openssl req -nodes -new -x509 -keyout /app/server.key -out /app/server.cert -subj "/C=US/ST=Texas/L=Austin/O=MF/OU=MF/CN=micahf.com"
WORKDIR /app
COPY . /app

EXPOSE 5555
CMD [ "node", "index.js" ]
