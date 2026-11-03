# Rosa Nails & Spa

Website for **Rosa Nails & Spa**, a family-run nail salon in Amsterdam West.

- **Live website:** https://rosa-nails-and-spa.vercel.app
- **Admin page (edit services & prices):** https://rosa-nails-and-spa.vercel.app/admin

Customers see the salon's photos, price list, Google reviews, opening hours and
location, and can call or WhatsApp to book. The salon owner logs in to `/admin`
to add, edit or delete services and prices — changes show on the website
straight away.

---

## Contents

1. [How it fits together](#1-how-it-fits-together)
2. [Run it on your computer](#2-run-it-on-your-computer)
3. [How it runs online](#3-how-it-runs-online)
4. [Settings and secrets](#4-settings-and-secrets)
5. [What every file does](#5-what-every-file-does)
6. [Common tasks](#6-common-tasks)
7. [Known issues and to-dos](#7-known-issues-and-to-dos)

---

## 1. How it fits together

The project has two halves that talk to each other:

```
 Visitor's browser
        │
        ▼
 ┌─────────────────────────┐        /api/...        ┌──────────────────────────┐
 │  FRONT END (front_end/) │ ─────────────────────▶ │  BACK END (back_end/)    │
 │  React + TypeScript     │                        │  Python + FastAPI        │
 │  The pages you see      │ ◀───────────────────── │  Prices, admin, reviews  │
 └─────────────────────────┘        JSON data       └──────────┬───────────────┘
                                                              │
                                            ┌─────────────────┴─────────────────┐
                                            ▼                                   ▼
                                     Database                          Google Places API
                               (SQLite file locally,                   (live Google reviews)
                                Neon Postgres online)
```

| Part | Technology | What it does |
|---|---|---|
| **Front end** | React, TypeScript, Vite, Tailwind CSS | Everything visitors see, plus the `/admin` page |
| **Back end** | Python, FastAPI, SQLAlchemy | Stores services/prices, checks the admin password, fetches Google reviews |
| **Database** | SQLite (on your computer) / Neon Postgres (online) | Holds the services, prices and (later) bookings |
| **Hosting** | Vercel | Serves the website and runs the back end; redeploys on every push to GitHub |

If the back end can't be reached, the website still works: it shows a built-in
copy of the price list and hides the reviews section.

---

## 2. Run it on your computer

You need **Node.js** (for the front end) and **Python 3.12+** (for the back end).
Use two terminal windows — one for each half.

### Terminal 1 — back end (port 8000)

```bash
cd back_end
python -m venv .venv
```

Activate the virtual environment:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Windows (Git Bash): `source .venv/Scripts/activate`
- macOS / Linux: `source .venv/bin/activate`

Then:

```bash
pip install -r requirements.txt
copy .env.example .env        # macOS/Linux: cp .env.example .env
```

Open `back_end/.env` and fill in at least `ADMIN_PASSWORD` (see
[section 4](#4-settings-and-secrets)). Then start the server:

```bash
uvicorn main:app --reload
```

The first start creates `back_end/database.db` and fills it with the salon's
services. Check it works: http://localhost:8000/api/health → `{"status":"ok"}`.

### Terminal 2 — front end (port 5173)

```bash
cd front_end
npm install
npm run dev
```

Open:

- Website: http://localhost:5173
- Admin: http://localhost:5173/admin (log in with `ADMIN_PASSWORD` from `back_end/.env`)

> Your computer uses its **own** database file, so testing prices locally never
> changes the live website.

---

## 3. How it runs online

The site is hosted on **Vercel** as one project that serves both halves:

- The front end is built (`npm run build`) into plain files and served to visitors.
- Every request to `/api/...` is sent to [api/index.py](api/index.py), which starts
  the FastAPI back end.
- The database is **Neon Postgres**, connected through Vercel's Storage tab.
  (Vercel's servers are temporary, so a SQLite file would lose its data — that's
  why the online version uses Neon.)

**Updating the live site:** push to the `main` branch on GitHub. Vercel builds
and publishes it automatically in about a minute.

```bash
git add -A
git commit -m "Describe your change"
git push
```

Watch the build at https://vercel.com/smart-ai-assistant/rosa-nails-and-spa.

> **Plan note:** the project is on Vercel's free *Hobby* plan, which Vercel's
> terms limit to non-commercial use. A business site officially needs *Pro*
> ($20/month), or a move to a host that allows free business use (e.g. Netlify).

---

## 4. Settings and secrets

Secrets are **never** stored in Git. Locally they live in `back_end/.env`
(ignored by Git); online they live in Vercel → project → **Settings →
Environment Variables**. After changing one in Vercel, click **Redeploy**.

| Name | Needed for | Local (`back_end/.env`) | Online (Vercel) |
|---|---|---|---|
| `ADMIN_PASSWORD` | Logging in to `/admin`. If missing, admin is switched off. | ✅ you set it | ✅ you set it |
| `GOOGLE_PLACES_API_KEY` | Fetching Google reviews | optional | ✅ |
| `GOOGLE_PLACE_ID` | Which business's reviews to fetch | optional | ✅ |
| `DATABASE_URL` | Which database to use. Empty = local SQLite file. | leave empty | ✅ added by Neon automatically |
| `FRONTEND_ORIGINS` | Websites allowed to call the API from another address | default is fine | not needed (same address) |
| `VITE_API_BASE_URL` | (front end) Where the API lives. Default: `localhost:8000` in dev, same site online. | not needed | not needed |

The template with all names is [back_end/.env.example](back_end/.env.example).

---

## 5. What every file does

### Project root

| File | What it does |
|---|---|
| [README.md](README.md) | This guide. |
| [vercel.json](vercel.json) | Tells Vercel how to build the site: build the front end, send `/api/...` to the Python back end, and serve `/admin` from the same page. |
| [requirements.txt](requirements.txt) | The **real** list of Python packages for the back end. Lives here (not in `back_end/`) because Vercel only reads it from the project root. |
| [api/index.py](api/index.py) | The door Vercel uses to start the back end. It just loads `back_end/main.py`. You won't need to edit it. |
| [.gitignore](.gitignore) | Files Git must never upload: secrets (`.env`), database files (`*.db`), `node_modules`, Python caches. |
| [.claude/launch.json](.claude/launch.json) | Lets Claude Code start the front-end dev server in its preview browser. Not used by the website. |

### Back end — `back_end/`

| File | What it does |
|---|---|
| [main.py](back_end/main.py) | **Starting point of the API.** Creates the FastAPI app, sets which websites may call it (CORS), creates/updates database tables and fills an empty database on start-up, and defines `/api/health` and `/api/reviews` (Google reviews, cached for a day). |
| [services_api.py](back_end/services_api.py) | **The price list and admin endpoints.** `GET /api/services` (public price list) and the password-protected `GET/POST/PUT/DELETE /api/admin/services` used by the admin page. Also checks the admin password and validates what the form sends. |
| [models.py](back_end/models.py) | **The database tables**, described in Python: `Service` (name, option, category, price in cents, duration, description…), `Appointment`, `Technician` and `ClosedSlot` (the last three are for a future online-booking feature). |
| [database.py](back_end/database.py) | **Connects to the database.** Uses `DATABASE_URL` if set (Neon online), otherwise the local `database.db` file. `create_tables()` creates missing tables and adds new columns to existing ones. |
| [seed.py](back_end/seed.py) | **Starting data:** the salon's services, prices and descriptions, plus the technicians. Runs automatically on start-up but only fills an **empty** database — services deleted in the admin stay deleted. Can also be run by hand: `python seed.py`. |
| [config.py](back_end/config.py) | **Salon rules in one place:** time zone (Amsterdam), opening hours for booking, 15-minute booking grid, notice periods, and the list of service categories (must match the front end's list). |
| [core/availibility.py](back_end/core/availibility.py) | **Unfinished** start of online booking: works out which time slots a technician is free. Not used yet and contains typos that stop it from loading (see [section 7](#7-known-issues-and-to-dos)). |
| [requirements.txt](back_end/requirements.txt) | Points to the root `requirements.txt`, so `pip install -r requirements.txt` works from inside `back_end/`. |
| [.env.example](back_end/.env.example) | Template for `back_end/.env`, listing every setting with no values. Copy it to `.env` and fill it in. |
| `.env` *(not in Git)* | Your local secrets. |
| `database.db` *(not in Git)* | Your local SQLite database. Safe to delete — it is recreated and refilled on the next start. |

### Front end — `front_end/`

#### Setup files

| File | What it does |
|---|---|
| [package.json](front_end/package.json) | Lists the JavaScript packages (React, Vite, Tailwind…) and the commands `npm run dev`, `npm run build`, `npm run lint`. |
| `package-lock.json` | Exact package versions, so every install is identical. Managed by npm — don't edit. |
| [index.html](front_end/index.html) | The single HTML page the whole site is built into. Holds the browser-tab title, the description Google shows, the preview for links shared on WhatsApp/Facebook, and business details (address, hours) for Google in a special format (`application/ld+json`). |
| [vite.config.ts](front_end/vite.config.ts) | Settings for Vite, the tool that runs the dev server and builds the site (adds React and Tailwind). |
| `tsconfig*.json` | TypeScript settings. You won't need to edit these. |
| [eslint.config.js](front_end/eslint.config.js) | Code-quality rules checked by `npm run lint`. |
| `.gitignore` | Front-end files Git must ignore (build output, `node_modules`). |

#### `public/` — files served as-is

| File | What it does |
|---|---|
| [favicon.svg](front_end/public/favicon.svg) | The little yellow "R" icon in the browser tab. |
| `gallery/set-01.jpeg` … `set-09.jpeg` | Photos of nail sets shown in the gallery and the hero. |

#### `src/` — the website's code

| File | What it does |
|---|---|
| [main.tsx](front_end/src/main.tsx) | **Starting point.** Shows the admin page if the address is `/admin`, otherwise the website. |
| [App.tsx](front_end/src/App.tsx) | **The website page.** Puts all the sections in order and loads the reviews and price list from the back end. |
| [api.ts](front_end/src/api.ts) | **All communication with the back end:** fetching reviews and services, and the admin calls (list, add, edit, delete) with the password. |
| [index.css](front_end/src/index.css) | **Brand colours and fonts** (cream, butter yellow, coral, ink; Bodoni Moda + Jost) and a few global styles. Change a colour here and it changes everywhere. |
| [lib/hours.ts](front_end/src/lib/hours.ts) | Works out "Open now · until 18:00" / "Closed · opens tomorrow at 10:00" and which day is today — always in Amsterdam time. |

#### `src/components/` — the sections of the website (top to bottom)

| File | Section |
|---|---|
| [Navbar.tsx](front_end/src/components/Navbar.tsx) | Top menu bar with links and a "Call to book" button; becomes a ☰ menu on phones. |
| [Hero.tsx](front_end/src/components/Hero.tsx) | The big opening section: salon name, tagline, open/closed badge, buttons and two photos. |
| [About.tsx](front_end/src/components/About.tsx) | "Our story" text and the list of service categories. |
| [Reviews.tsx](front_end/src/components/Reviews.tsx) | Google star rating and review cards. Hidden if reviews can't be loaded. |
| [Gallery.tsx](front_end/src/components/Gallery.tsx) | Scrolling row of nail photos; tap one to open it large (lightbox). |
| [Services.tsx](front_end/src/components/Services.tsx) | The price list with category tabs. |
| [Contact.tsx](front_end/src/components/Contact.tsx) | Address, directions link, call/WhatsApp buttons and opening hours (today highlighted). |
| [SalonMap.tsx](front_end/src/components/SalonMap.tsx) | Embedded Google Map of the salon. |
| [Footer.tsx](front_end/src/components/Footer.tsx) | Bottom of the page: name, address, phone, copyright. |
| [MobileActionBar.tsx](front_end/src/components/MobileActionBar.tsx) | Phones only: "Call to book / WhatsApp" bar stuck to the bottom of the screen. |

#### `src/admin/` — the admin page

| File | What it does |
|---|---|
| [AdminApp.tsx](front_end/src/admin/AdminApp.tsx) | The whole `/admin` page: password login, list of services by category, Edit/Delete buttons, messages. Remembers the password only until the browser tab is closed. |
| [ServiceForm.tsx](front_end/src/admin/ServiceForm.tsx) | The add/edit form: category, name, option, price (€), duration, description, "Perfect for…", and the *show on website* / *bookable* switches. |

#### `src/data/` — fixed content

| File | What it does |
|---|---|
| [salon.ts](front_end/src/data/salon.ts) | **Salon details:** name, tagline, phone, WhatsApp, address, "Our story" text and opening hours. Edit this file to change any of them. |
| [services.ts](front_end/src/data/services.ts) | The list of **categories**, the code that groups database rows into services for the price list, and a **backup price list** shown if the back end is unreachable. (Real prices are managed in the admin.) |
| [gallery.ts](front_end/src/data/gallery.ts) | Which gallery photos to show, with a description of each (used by screen readers and Google). |
| [reviews.ts](front_end/src/data/reviews.ts) | Empty and unused — reviews come live from Google. Can be deleted. |

---

## 6. Common tasks

| I want to… | Do this |
|---|---|
| Change a **price**, add or remove a **service** | Use the admin page — no code needed. |
| Change **phone, address, tagline, "Our story"** | Edit [front_end/src/data/salon.ts](front_end/src/data/salon.ts). If you change the address or phone, also update the business details in [index.html](front_end/index.html). Then push. |
| Change **opening hours** | Update three places: `hours` in [salon.ts](front_end/src/data/salon.ts), `openingHoursSpecification` in [index.html](front_end/index.html), and `BUSINESS_HOURS` in [config.py](back_end/config.py). Then push. |
| Add or replace **gallery photos** | Put the photo in `front_end/public/gallery/` and add a line to [gallery.ts](front_end/src/data/gallery.ts) with a short description. To change the two hero photos, edit `HERO_PHOTO_IDS` in [App.tsx](front_end/src/App.tsx). |
| Add a **new service category** | Add it to `CATEGORIES` in [services.ts](front_end/src/data/services.ts) **and** `SERVICE_CATEGORIES` in [config.py](back_end/config.py) — the two lists must match. |
| Change **colours or fonts** | Edit the `@theme` block in [index.css](front_end/src/index.css). |
| Change the **admin password** | Locally: `back_end/.env`, then restart the back end. Online: Vercel → Settings → Environment Variables → edit `ADMIN_PASSWORD` → Redeploy. |
| Reset my **local** database | Stop the back end, delete `back_end/database.db`, start it again. |
| Check the code before pushing | In `front_end/`: `npm run lint` and `npm run build`. |
| See why the live site has an error | Vercel project → **Logs**. |

---

## 7. Known issues and to-dos

- **Hosting plan:** Vercel Hobby is for non-commercial use; a salon site
  officially needs Pro ($20/month) or a move to a host such as Netlify.
- **Custom domain:** the site uses `rosa-nails-and-spa.vercel.app`. Buying a
  domain (e.g. a `.nl`) is recommended before printing the link anywhere.
- **Street name:** the website says *Hofwickstraat 2*, Google says
  *Hofwijckstraat 2* — fix in [salon.ts](front_end/src/data/salon.ts) and
  [index.html](front_end/index.html).
- **Online booking is unfinished:** [core/availibility.py](back_end/core/availibility.py)
  has typos (`data` → `date`, `sqlachemy` → `sqlalchemy`, `display_name` →
  `display_order`) and isn't connected to the API yet.
- **Gallery photo `set-09.jpeg`** carries another account's watermark
  ("nail_mini") — replace it with one of the salon's own photos.
- **Duplicated data:** opening hours and categories are written in more than one
  file (see [section 6](#6-common-tasks)) — keep them in sync when changing them.
