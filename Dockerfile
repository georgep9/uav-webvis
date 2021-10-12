FROM continuumio/miniconda3 as flask-api
WORKDIR /app/server
COPY server/environment.yml ./
RUN conda env create -f environment.yml
RUN echo "source activate wvi" > ~/.bashrc
ENV PATH /opt/conda/envs/wvi/bin:$PATH
COPY server/ ./
CMD ["python3", "-u", "app.py"]
EXPOSE 5000

FROM node:lts-alpine as build-deps
WORKDIR /app/client
COPY client/package.json client/yarn.lock ./
RUN yarn install
COPY client/ ./
RUN yarn build

FROM nginx as nginx-server
COPY --from=build-deps /app/client/dist /app/client/dist
WORKDIR /app
COPY nginx.conf ./

CMD ["nginx", "-g", "daemon off;", "-c", "/app/nginx.conf"]
EXPOSE 80

