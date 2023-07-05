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
- [x] Finish setting up GH Actions
- [ ] Create view to add games and link from dashboard view
- [ ] Write guessing game for in-person guessing (legacy)
   - [ ] `Submission` model
      - [ ] Add support for embedded videos from popular platforms (youtube)
      - [ ] Spotify
      - [ ] Non-video/word-of-the-day
   - [ ] Guessing game generator (ajax)
   - [ ] Link with fk `Submission` to `Round`
   - [ ] Reveal Submission view (ajax)
   - [ ] Record Winner view (ajax)
- [ ] Anonomous User Player Flow
- [ ] Authed User Player Flow
- [ ] Write Guessing Game for async play (allow authed users to submit guesses over a time period for a gaame). E.g. one song per day / week, users can log in and guess, winner announced when all guesses in or time elapses.
