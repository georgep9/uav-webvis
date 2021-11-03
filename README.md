# UAVPayload-Visualization

[Uni project] - RESTful web interface for visualizing air quality and image processing data.

TODO: Refactor front-end API calls into seperate files.

Feel free to post some data to <http://wvi.geopat.io> (I've blocked saving image detections to prevent unexpected S3 costs so don't expect your history to show on reload).

![architecture](/assets/images/architecture.png)
![screenshot](/assets/images/screenshot.png)

## Installation

Requires [Docker Compose](https://docs.docker.com/compose/install/), [yarn](https://classic.yarnpkg.com/lang/en/docs/install/#windows-stable), and [Anaconda](https://www.anaconda.com/products/individual).

### Client

```bash
cd client
yarn install
```

### Server

```bash
cd server
conda env create -f environment.yml
```

## Usage

AWS credentials must be configured to connect with DynamoDB (see `utils/create_ddb_table.py` to create a table).

### Docker Compose

Start:
```
docker-compose up -d
```
Stop:
```
docker-compose down
```

### Development

Before anything, make sure there's a running redis server with hostname `wvi-redis`.
If the Flask server is having trouble connecting to that hostname, change the redis `host` parameter in `server/app.py` to `"localhost"`
and ensure redis is running locally.

Use seperate terminals (I recommend tmux) for client and server.

#### Client

To connect with a local API server, set the `VUE_APP_API_HOST` environment variable to `http://localhost:5000` either in `.env` or with `export VUE_APP_API_HOST=http://localhost:5000`.

```bash
cd client
yarn serve
```

#### Server

```bash
cd server
conda activate wvi
python app.py
```
