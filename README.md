# 3t-bot 🏋️‍♀️💪🧘

A bot which helps me sign up for powerpit and pilates reformer classes at 3T. I just want to get fit man.

## 🤖  With Github Actions

To get the bot running with Github Actions, you will need to fork this repo and add the following secrets to your repo:

- `GYM_USERNAME` - Your 3T email
- `GYM_PASSWORD` - Your 3T password
- `EMAIL_USER` - Your Gmail email
- `EMAIL_APP_PWD` - Your Gmail app password

In the `.github/workflows` folder, you will find a `run_bot.yml` file. This file contains the cron job which will run the bot every Sunday at 08:00. You can change this to your preferred time.

## 📦 Local set-up

First, this repo uses `poetry` for handling the python dependencies, so make sure this is downloaded. When this is done, run `poetry install` and the python environment should be up and running

Now run `playwright install` in order to install playwright fully.

### 🔑 Environment Variables

The environment variables which has been defined can be seen in `.env.example`. Copy `.env.example` to `.env` and fill in your details:

```bash
GYM_USERNAME=your_3t_email@example.com
GYM_PASSWORD=your_3t_password

EMAIL_USER=your_email@gmail.com
EMAIL_APP_PWD=your_app_password # NOT YOUR REGULAR EMAIL PASSWORD, MUST BE CREATED
```

📢 **Important: How to Get an `EMAIL_APP_PWD`**

- The bot only supports Gmail for sending email notifications.
- This only works if 2-Step Verification is enabled on your account!
- To generate the `EMAIL_APP_PWD`, [go here](https://myaccount.google.com/apppasswords)

### 🚀 Running the Bot

We want to run the bot with a cron job, so it can be run at a specific time, in our case Sunday's at 08:00 in the morning.

```bash
crontab -e
```

This will open the crontab file, it will prompt you to choose an editor, choose your preferred editor.

```bash
0 8 * * 0 cd /path/to/this/repo && source .venv/bin/activate && python src/main.py >> logs/cron.log 2>&1
```

- The `0 8 * * 0` is the time and day the bot will run. This is in the format `minute hour day month day_of_week`.
- The `cd /path/to/this/repo` is the path to the repo.
- `source .venv/bin/activate` is the path to the python environment. It can be found running `which python` after running `poetry install`
- `python src/main.py` is the command to run the bot.
- `>> logs/cron.log 2>&1` is the output of the bot, which will be logged in `logs/cron.log`.

Example:

```bash
0 8 * * 0 cd /home/taheera.ahmed/code/3t-bot && source .venv/bin/activate && python src/main.py >> logs/cron.log 2>&1
```

To check if the cron job has been added, run `crontab -l`.
