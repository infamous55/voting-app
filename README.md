# Voting App

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)

A RESTful microservice for voting with real time updates.

## Overview

The project is implemented with [Python](https://www.python.org/) and [FastAPI](https://fastapi.tiangolo.com/) for the API, with [PostgreSQL](https://www.postgresql.org/) serving as the database. The environment relies on [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).

The `docker-compose.yml` file also includes two additional services: `prometheus` and `grafana`, used for monitoring.

## Running locally

To run the project, first clone the repository and navigate to the `voting-app` directory.

```sh
git clone https://github.com/infamous55/voting-app.git && cd voting-app
```

Start the development server using the following command:

```sh
docker-compose up
```

The documentation, provided in OpenAPI format, can be found at `http://localhost:8000/docs/`.

![Screenshot of the documentation](./assets/screenshot.png)

[Prometheus](https://prometheus.io/) is available at `http://localhost:9090/`, and [Grafana](https://grafana.com) at `http://localhost:3000/`.

## To Do:

- [ ] Add production environment for deployment
- [ ] Add unit tests
- [ ] Add tracing with [OpenTelemetry](https://opentelemetry.io/)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

Distributed under the MIT License. See `LICENSE` for more information.
