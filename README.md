# ⚡ London Grid Watch

An experimental dashboard combining real-time electricity prices and carbon intensity data for London.

Live at: **[https://london-grid-dashboard.netlify.app/](https://london-grid-dashboard.netlify.app/)**

## About

This project experiments with integrating two APIs:
- **Octopus Energy API** — Real-time Agile electricity pricing
- **National Grid ESO Carbon Intensity API** — Current and forecasted carbon intensity for London

The dashboard displays current prices, carbon intensity, and visualizes both metrics over time to help identify the best times to use electricity based on cost and environmental impact.

## Tech Stack

- Frontend: Vanilla HTML/CSS/JavaScript with Chart.js
- Backend: Python serverless function (Netlify Functions)
- Deployment: Netlify