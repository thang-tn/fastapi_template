# {{ cookiecutter.project_name }}

## Setup and installation
### Local Development

#### Setting up dependencies
- Install pyenv and pyenv-virtualenv, use pyenv to manage python versions
    ```shell
    $ brew install pyenv
    $ brew install pyenv-virtualenv
    ```
- After installation, you'll still need to do Pyenv shell setup steps then add
    ```shell
    $ eval "$(pyenv init -)"
    $ eval "$(pyenv virtualenv-init -)"
    ```
    to your shell startup file, e.g. `~/.bash_profile`, `~/.zshrc`, or `~/.profile`.

- Install python 3.11
    ```shell
    $ pyenv install 3.11.7
    ```
- Setup virtualenv for the project
    ```shell
    $ pyenv virtualenv 3.11.4 venv
    ```
- Install dependencies for the project
    ```shell
    $ cd <your-project-directory>
    $ pyenv local venv
    $ pip install poetry
    $ poetry install
    ```

#### Setup app environment variables
- Copy `.env.example` to `.env`
    ```shell
    $ cp .env.example .env
    ```

- Start FastAPI server
    ```shell
    $ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

#### Setting up database
  - Update database environment variables in `.env` file
      ```yaml
      # Database
      DATABASE_URL=
      ```
  - Start postgres and create DB schema
  - Run migration to update to latest DB schema
    ```shell
     $ alembic upgrade head
    ```

#### Setting up Kafka

- Modify kafka setting environment variables in `.env` file
    ```yaml
    # Kafka sample
    KAFKA_BROKERS_TLS=
    KAFKA_GROUP_ID=
    KAFKA_SECURITY_PROTOCOL=
    ```
  ---
  **Hint**: Example of Kafka environment when using [kafka-docker](https://github.com/Thinkei/kafka-docker)  to start Kafka server
    ```yaml
    # Kafka sample
    KAFKA_HOST=127.0.0.1
    # KAFKA__GROUP_ID=
    KAFKA__BROKERS_TLS="127.0.0.1:9092"
    KAFKA__SECURITY_PROTOCOL="PLAINTEXT"
    ```
  ---
- Start Kafka consumer
    ```shell
    $ python -m app.consumer
    ```

#### Setting up Celery Worker
The project now uses Celery library to handle background tasks.
Using Celery with Redis as a broker and backend. For more information, see [the Celery README](https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#redis)
Make sure redis server is running before starting Celery worker.

- Modify Celery setting environment variables in `.env` file
    ```yaml
    # Celery
    CELERY_BROKER_URL=
    CELERY_RESULT_BACKEND=
    ```

  - **Hint**: Example of Celery environment when using [redis-docker](

- Start Celery worker
    ```shell
    $ celery -A app.worker worker -l info -Q smartmatch
    ```

### Via docker-compose
#### Start all services via docker-compose command
```shell
docker-compose up  # start the services
docker-compose up -d  # detached mode
docker-compose up --build --force-recreate -d # rebuild images and containers in detached mode
docker-compose down  # stop the services
```

### Testing
- Create a new databse for testing
- Update environment variable `TEST_DATABASE_URL` in your `.env` file
- Make sure you have installed testing dependencies
- Run tests using `pytest`



## Usages
### API docs
- http://localhost:8000/api/docs

### Healthcheck
- GET `/healthz`


## Python Coding Quality Guideline
In order to ensure the quality of the code, we take advantages of following libraries:
- [ruff](https://github.com/astral-sh/ruff): An extremely fast Python linter, written in Rust
- [mypy](https://github.com/python/mypy): Optional static typing for Python


### To run the libraries on a python file, execute below commands
```shell
mypy $file_name
ruff check $file_name
```

### Or you can run `pre-commit` to check all at once.

- To check if the python file is satisfied all the above libraries
```shell
pre-commit run --file $file_name
pre-commit run --all-files
```
