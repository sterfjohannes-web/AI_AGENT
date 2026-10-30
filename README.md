# Rohstoff-Agent (Dashboard-App + Analyse-Agent)
1. Agent: `python3 agent/agent.py` -> schreibt app/report.json (Live-Kurse von Yahoo Finance; offline = DEMO-Daten).
2. Automatisch täglich: Ordner in ein GitHub-Repo, GitHub Actions (cron "0 6 * * 1-5") ruft agent.py auf und committet report.json; GitHub Pages / Netlify hostet app/.
3. Aufs Handy: URL im Handybrowser öffnen -> "Zum Home-Bildschirm" (iOS Safari) bzw. "App installieren" (Android Chrome).
Erweiterung: News-/LLM-Zusammenfassung, physische Preise (Spreads, Fracht), Risikolimits.
