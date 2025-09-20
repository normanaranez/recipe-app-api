# recipe-app-api


To install new libraries using pip in docker, run:
```sh
docker compose run --rm app sh -c "<python command or django command here>"
```

To generate a new `requirements.txt` in the root folder, run:
```sh
docker compose run --rm -v $(pwd)/requirements.txt:/requirements.txt app sh -c "pip freeze > /requirements.txt"
```