# RiskGuard – AI-Based Transaction Risk Detection (MVP)

RiskGuard is a **behavior-based transaction risk prioritization system**
that detects anomalous financial activity using machine learning and
human-in-the-loop verification.

> This is not a fraud-proof system.
> It is a risk triage and decision-support layer.

## Features
- Cold-start handling using global baselines
- Behavioral anomaly detection (Isolation Forest)
- Spending velocity analysis
- Soft risk controls (no hard blocking)
- Human verification with cooldown
- Explainable risk reasons
- Modular backend + interactive frontend simulator

## Tech Stack
- Python (Flask, Pandas, Scikit-learn)
- JavaScript, HTML, CSS
- Isolation Forest (unsupervised ML)

## Architecture
- Frontend simulates mobile banking UX
- Backend scores transactions in real-time
- Risk logic applies persistence & thresholds
- User confirmation treated as weak signal

## Limitations
- Behavioral systems can be evaded by gradual mimicry
- Thresholds require recalibration
- Not compliance-certified (demo MVP)
