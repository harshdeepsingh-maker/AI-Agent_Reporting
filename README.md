#  Agent Swarm Collaboration — Daily Performance Reporting System

This repository implements a **multi-agent collaboration system** where specialized agents work together to generate a **daily company performance report**.  
The design mimics the *Agent Swarms* concept — autonomous, specialized agents that communicate, coordinate, and produce results without manual intervention.

##  Architecture Overview

```
agent-swarm-submission/
├── requirements.txt              # Python dependencies
├── data/                         # Mock data sources
│   ├── sales.json
│   └── marketing.json
├── src/agent_swarm/
│   ├── __main__.py               # Main entry point
│   ├── agents/                   # Specialized agents
│   │   ├── sales_agent.py
│   │   ├── marketing_agent.py
│   │   └── reporting_agent.py
│   ├── mock_api.py               # Simulated API layer
│   ├── eventbus.py               # Event-driven communication bus
│   ├── emailer.py                # Email sending logic
│   ├── email_utils.py            # SMTP helpers
│   ├── charts.py                 # Data visualization utilities
│   ├── models.py                 # Data models
│   ├── config.py / settings.py   # Configuration management
│   ├── template_env.py           # Jinja2 template environment
│   ├── logging_utils.py          # Structured logging
│   └── utils.py                  # General utilities
└── templates/
    ├── report_email.html          # HTML email template
    └── report_email.txt           # Plain-text email template
```

---

##  Key Features

- **Multi-Agent Architecture**  
  - Sales Agent fetches CRM data.  
  - Marketing Agent fetches campaign data.  
  - Reporting Agent orchestrates and synthesizes.  

- **Event-Driven Communication**  
  - Agents publish and subscribe to events using an `eventbus`.  
  - Reporting Agent waits for both Sales + Marketing results.  

- **Mock API Integration**  
  - `mock_api.py` simulates CRM + Marketing endpoints.  
  - `data/sales.json` and `data/marketing.json` serve as data sources.  

- **Report Generation**  
  - Data visualizations via `charts.py`.  
  - Report templating via `Jinja2` (`template_env.py`).  
  - Emails generated in both HTML and plain-text formats.  

- **Automated Scheduling**  
  - The system can be triggered by cron (Linux/macOS) or Task Scheduler (Windows).  
  - Default: **runs daily at 9 AM**.  

- **Resilient Error Handling**  
  - If one agent fails → report is still produced with missing data flagged.  
  - Logging captures errors with structured details.  

---

##  Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/harshdeepsingh-maker/AI-Agent_Reporting.git
cd AI-Agent_Reporting
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the system manually
```bash
python -m agent_swarm
```

### 4. Schedule automatic runs
Set up a cron job (Linux/macOS) or Task Scheduler (Windows).  
Example (Linux):
```bash
0 9 * * * /usr/bin/python3 /path/to/AI-Agent_Reporting/src/agent_swarm/__main__.py
```

---

##  Example Output

**Email Subject:**  
 Daily Performance Report — 2025-09-07  

**Email Body (HTML):**
- Sales Summary (last 24h)
- Marketing Campaign Performance
- Charts/Graphs
- Missing Data Notes (if errors occurred)

Reports are generated using Jinja2 templates (`report_email.html` / `.txt`).

---

##  Error Handling

- **Sales Agent failure** → Marketing data included, sales marked as *missing*.  
- **Marketing Agent failure** → Sales data included, marketing marked as *missing*.  
- **Both fail** → Report generated with a *no data available* warning.  

Errors are logged in structured JSON via `logging_utils.py`.

---



##  Author

Developed by **Harshdeep Singh**  

Run once: `python -m agent_swarm run-once`.
Mock API: `python -m agent_swarm mock-api`.
