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
   - [ ] Add Player management screen
- [ ] Add upload delete button
- [x] Write guessing game for in-person guessing (legacy)
   - [x] Guessing game generator
   - [x] Link with fk `Submission` to `Round`
   - [x] Reveal Submission view
   - [x] Record Winner view
- [ ] Add re-roll button
- [ ] add smarts to `Submission` model
   - [ ] Add support for embedded videos from popular platforms (youtube)
   - [ ] Spotify
   - [ ] Non-video/word-of-the-day
- [x] Authed User Player Flow
- [ ] Write Guessing Game for async play (allow authed users to submit guesses over a time period for a gaame). E.g. one song per day / week, users can log in and guess, winner announced when all guesses in or time elapses.
