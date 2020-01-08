## climate-change

## Usage

1. Install necessary libraries if missing
   ```
    pip install dash
    pip install dash-daq
    pip install dash-bootstrap-components
    pip install pandas
    pip install gunicorn
   ```

## Running Locally

- Navigate to folder containing app.py
- Run:
  ```
  python app.py
  ```
- Visit `http:127.0.0.1:8050/` in your web browser.

## Heroku Deployment

**Note: Make sure project has a github repo before deployment**

- Download [Heroku cli](https://devcenter.heroku.com/articles/heroku-cli)
- Run:

  ```
  heroku create climate-change
  git add . # add all files to git
  git commit -m 'Initial app boilerplate'
  git push heroku master # deploy code to heroku
  heroku ps:scale web=1  # run the app with a 1 heroku "dyno"
  heroku open
  ```

- You should be able to view your app at https://spec-climate-change.herokuapp.com

## File Structure

- data folder should contain all data files. <br>
- assets folder should contain images, css, and js files.
