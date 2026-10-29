# Alfa lease km tracker

A phone app (installable web app) that shows how many km you are ahead or behind your lease allowance.
A daily GitHub job reads the odometer from your Alfa Connect account and saves it to `docs/readings.json`.

## Setup

1. Create a GitHub account and a new repository (for example `alfa-lease`).
2. Upload everything in this folder to it, keeping the folder structure (`docs/`, `scripts/`, `.github/`).
3. In the repository go to Settings > Secrets and variables > Actions > New repository secret. Add:
   - `UCONNECT_EMAIL`: your Alfa Connect login e-mail
   - `UCONNECT_PASSWORD`: your Alfa Connect password
4. Open the Actions tab, choose "Log odometer", press "Run workflow". Open the finished run and read the log.
   You should see a line like `Vehicle: Alfa Romeo Tonale, odometer=41234 km` and `Saved 41234 km for ...`.
5. Go to Settings > Pages. Under "Build and deployment" choose "Deploy from a branch", branch `main`, folder `/docs`, then Save.
6. After a minute your app is live at `https://YOUR-USERNAME.github.io/REPO-NAME/`.
7. Open that address on your phone:
   - iPhone (Safari): Share > Add to Home Screen
   - Android (Chrome): menu > Install app / Add to Home screen
8. In the app, open "Lease setup" and enter lease start date, length, total km and the odometer at delivery.

## Troubleshooting

- Login fails: check the e-mail and password by logging in to the Alfa Connect app. If you live outside Europe, change
  `UCONNECT_BRAND` in `.github/workflows/log-odometer.yml` to `ALFA_ROMEO_US_CANADA` or `ALFA_ROMEO_ASIA`.
- Odometer missing: the car has not reported it yet. Start the car, wait a few minutes, run the workflow again.
- The app does not show new readings: open `docs/config.json` and set `dataUrl` to
  `https://raw.githubusercontent.com/YOUR-USERNAME/REPO-NAME/main/docs/readings.json`.
- Daily runs stop: GitHub can pause scheduled jobs in quiet repositories. Re-enable it in the Actions tab.

## Privacy

On a free GitHub account the repository must be public for Pages to work, so your odometer readings are public.
Your password is stored as an encrypted secret and is not visible in the repository.
This uses an unofficial interface that the community reverse-engineered from the Alfa Connect app, so it can break if Stellantis changes things.
