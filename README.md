# Daily Groove
A guessing game where players guess who submitted the randomly selected content. Inspired by http://app.groovebox.link.

# Local Development

- Install python 3.11 (or set pyenv to it)
- install Poetry & pre-commit: `pip install poetry pre-commmit`
- Clone the repo and cd to root directory
- activate venv: `poetry shell`
- install dependencies: `poetry install --with dev`
- install pre-commit hooks: `pre-commit install`
- migrate local sqlite db: `python manage.py migrate`
- run local server: `python manage.py runserver`

## Outstanding ToDos
[] Create view to add games and link from dashboard view
[] Write guessing game
   [] `Submission` model
   [] Guessing game generator (ajax)
   [] Link with fk `Submission` to `Round`
   [] Reveal Submission view (ajax)
   [] Record Winner view (ajax)
