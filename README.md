# 🍹 EVERS KÖK & BAR – Spin the Wheel Lottery

A simple, fun Streamlit app for spinning a wheel to win a free drink.
Built for friends and family visiting the bar/home — enter your name, age,
and phone number, spin the wheel, and see if you win!

## What it does

- One page with the app's purpose and a short set of rules
- Three input fields: **Name**, **Age**, **Phone number**
- A red & white spinning wheel styled for **EVERS KÖK & BAR**
- A pop-up after each spin announcing a **win** or a **loss**
- If you **lose**, you can spin again after a **5-minute cooldown**
- If you **win**, you can **download a JPEG certificate** for a free drink,
  redeemable at EVERS KÖK & BAR, Stenkilsvägen 23, Vätö

## Project structure

```
.
├── app.py            # Frontend / UI (Streamlit) — layout, wheel, popup
├── backend.py         # Logic — validation, cooldown, win/lose, certificate
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

`app.py` never contains business logic — it only calls functions from
`backend.py` and displays the results. This keeps the app easy to extend
later (e.g. swapping the storage layer or the odds) without touching the UI.

## How it works (rules)

- Win probability is **20%** by default (configurable in `backend.py` via
  `WIN_PROBABILITY`).
- Participants must be **18 or older** (configurable via `MIN_AGE`).
- Each phone number can spin once; after a **loss**, that phone number must
  wait **5 minutes** before spinning again. Wins have no cooldown.
- Attempts are stored locally in a file called `spins_data.json`, created
  automatically the first time someone spins. This is a lightweight
  "database" suitable for a home/small-bar setting — it is **not** meant for
  high-traffic or multi-user production use.

## Running it locally

1. Make sure you have Python 3.9+ installed.
2. Clone this repository and move into the folder:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
3. (Recommended) create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```
6. Streamlit will open the app in your browser (usually at
   `http://localhost:8501`).

## Deploying with GitHub + Streamlit Community Cloud

1. Push this project (all four files) to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   your GitHub account.
3. Click **"New app"**, select your repository, branch, and set the main
   file path to `app.py`.
4. Click **Deploy**. Streamlit will install `requirements.txt` automatically
   and give you a public URL you can share with friends and family.

## Notes & limitations (MVP scope)

- Data (`spins_data.json`) is stored on the server's local disk. On
  Streamlit Community Cloud, this file may be reset whenever the app
  restarts or redeploys — fine for casual home/bar use, but not a permanent
  record of winners.
- The 5-minute cooldown is tracked **per phone number**, not per browser, so
  it works even if someone refreshes the page or uses a different device.
- The wheel is drawn with SVG + CSS animation directly inside Streamlit —
  no external image files or JavaScript libraries required.
- The certificate is generated on the fly as a JPEG using Pillow, with the
  winner's name, the date, and the bar's details.

## Customizing

- **Change the odds:** edit `WIN_PROBABILITY` in `backend.py`.
- **Change the cooldown:** edit `COOLDOWN_SECONDS` in `backend.py`.
- **Change the bar name/address:** edit `BAR_NAME` and `BAR_ADDRESS` in
  `backend.py` (used both in the certificate and the footer).
- **Change the wheel colors/segments:** edit the `SEGMENTS` list at the top
  of `app.py`.
