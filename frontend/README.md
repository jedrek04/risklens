# RiskLens frontend

React app with Vite. Plain JavaScript, plain CSS, no routing library and no state library.

## Run it

    cd frontend
    npm install
    npm run dev        # http://localhost:5173
    npm test           # logic tests, no browser needed
    npm run build      # production build in dist/

`npm run dev` talks to the Cloud Run backend. The dev server forwards `/api/...` to the cloud service and adds your
gcloud identity token, so log in once with `gcloud auth login`. No local backend is needed. To use another backend,
set `RISKLENS_API_URL` before starting. A deployed site needs `VITE_API_URL` (how the public site reaches the API is not decided yet).

The asset list comes from `src/data/tickers.json`. Regenerate it after changing the backend ticker list:

    python scripts/export_tickers.py

## How the code is organised

    src/
      main.jsx            starts React
      App.jsx             holds the shared state and shows step 1, 2 or 3
      config.js           limits: max assets, horizon, simulations, history
      pages/              one file per step (BuildPage, AnalysisPage, ReportPage)
      components/
        TopBar.jsx        the step buttons
        build/            everything on the Build screen, one component per file
        analysis/         the cards of the Analyse screen, one component per file (charts, calendar, sentiment cards)
      api.js              all calls to the backend, and the error messages
      hooks/useAnalysis.js  runs the three analyses side by side and keeps their state
      lib/                plain functions without React, all with tests
        portfolio.js      add, remove, fill, totals, the request for the API
        search.js         asset search and group counts
        groups.js         category and group names
        settings.js       checks the model settings
        calendar.js       places the unusual days on one time axis
        color.js          colour scales for the heatmap and the calendar
        sentiment.js      gauge angle, status texts, safe headline links
        riskShare.js      share of the portfolio risk per asset
        colors.js         the colour of each portfolio slot
      styles/global.css   colours, fonts, shared look
      data/tickers.json   generated, do not edit by hand

To change how something looks, edit the CSS next to its component. To change a rule (for example the
maximum number of assets), change `config.js` or the matching file in `lib/` and run `npm test`.
