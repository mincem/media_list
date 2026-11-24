# media_list
Manager for media lists

## Installation

* Using Python 3.11
* Run `pip install -r requirements.txt`

## Usage

* Run `python manage.py runserver 8000`

## Development

* Run `pip install -r requirements-dev.txt` to also install the development tools (pylint, uv)

### Dependencies

`requirements.in` and `requirements-dev.in` list the packages we depend on directly. `requirements.txt` and `requirements-dev.txt` are generated from them with every package pinned, so don't edit those by hand.

After changing a `.in` file, or to upgrade everything to the newest allowed versions, regenerate both lock files (in this order):

```bash
uv pip compile requirements.in --universal --python-version 3.11 --upgrade -o requirements.txt
uv pip compile requirements-dev.in --universal --python-version 3.11 --upgrade -o requirements-dev.txt
```

Leave out `--upgrade` to keep the current versions and only apply the changes from the `.in` files.

### Linter

```bash
pylint --load-plugins pylint_django --django-settings-module=config.settings.production src/media_list
```

* Pylint can also be configured in PyCharm with a plugin.
