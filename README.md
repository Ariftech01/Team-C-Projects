# Team C Projects

![Repository](https://img.shields.io/badge/Repository-Team%20C%20Projects-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![Projects](https://img.shields.io/badge/Projects-6-orange)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

**Team-C-Projects** is the central repository containing the project work developed by **Team C** as part of the **Infosys project development program**.

The repository contains six individual projects, with each team member maintaining their work inside a dedicated project directory.

The purpose of this repository is to provide a common, organized location for:

* Individual project development
* Milestone-based progress
* Source-code management
* Project documentation
* Testing and validation
* Demonstration and evaluation
* Team collaboration

Each project is independently structured according to its own requirements and technology stack.

---

## Team Members

| No. | Team Member               | Project                                                           |
| --: | ------------------------- | ----------------------------------------------------------------- |
|   1 | **ARIF AFZAL**            | Agentic AI for Safety Monitoring with Construction Risk Analytics |
|   2 | **DIKSHA RAUTELA**        | Construction Intelligence Hub                                     |
|   3 | **Kallam Swethana Reddy** | Construction Intelligence Hub                                     |
|   4 | **Kiran Rathod**          | Construction Intelligent Hub                                      |
|   5 | **Yogendra Medarametla**  | Agentic AI for Safety Monitoring with Construction Risk Analytics |
|   6 | **saipavan**              | Construction Intelligence Hub                                     |

---

# Projects

## 1. ARIF AFZAL

### Agentic AI for Safety Monitoring with Construction Risk Analytics

An enterprise-oriented construction management and intelligence platform designed to combine construction safety monitoring, risk intelligence, AI analysis, project management, operational monitoring, visualization, cost estimation, and reporting.

### Major Capabilities

* Dashboard
* Risk Intelligence
* AI Analysis
* 3D Building Visualizer
* Project Management
* Construction Operations
* Reports
* Settings
* Safety monitoring
* Risk analytics
* AI-assisted construction analysis
* Cost estimation
* Materials management
* Workforce monitoring
* Equipment monitoring
* Progress tracking

### Technology Highlights

* Python
* Streamlit
* Plotly
* Pandas
* NumPy
* SQLAlchemy
* SQLite / MySQL
* Ollama
* Machine-learning based analytics
* ReportLab
* OpenPyXL

The project is documented separately inside the corresponding member directory.

---

## 2. DIKSHA RAUTELA

### Construction Intelligence Hub

An AI-powered construction project-management application organized around a modular application architecture.

The project includes dedicated components for authentication, configuration, models, repositories, services, utilities, and user-interface functionality.

### Major Areas

* Dashboard
* Portfolio / Project Management
* Workspace
* AI Assistant
* AI Actions
* Analytics
* Settings
* Authentication
* Notifications

### Technology Highlights

* Python
* Streamlit
* Modular Python architecture
* Local JSON-based data storage
* Ollama / local AI
* Custom UI components

The application configuration identifies the project as **Construction Intelligence Hub** with the tagline **AI-Powered Construction Project Management**.

---

## 3. KALLAM SWETHANA REDDY

### Construction Intelligence Hub

A production-oriented AI-powered construction management platform built using Streamlit, SQLite, and Ollama.

### Major Features

* Multi-user authentication
* Per-user data isolation
* Project management
* Project CRUD operations
* Material estimation
* AI Assistant
* PDF and Excel report generation
* Interactive analytics
* Configurable project settings
* Dashboard
* Profile management

### Technology Highlights

* Python
* Streamlit
* SQLite
* Ollama
* Llama 3.2
* Plotly
* ReportLab
* OpenPyXL
* Pandas

The project includes dedicated Streamlit pages for Dashboard, Project Management, Material Estimator, AI Assistant, Reports, Analytics, Settings, About, and Profile.

---

## 4. KIRAN RATHOD

### Construction Intelligent Hub

A browser-based construction project-management application using a lightweight frontend architecture and local AI capabilities.

The application focuses on construction project monitoring and management while keeping data and AI functionality local.

### Major Features

* Project Management
* Team Management
* Budget Management
* Materials Management
* Risk Analysis
* Reports
* AI Insights
* AI Material Estimation
* Document Analysis
* Dashboard
* User Profile

### Technology Highlights

* HTML5
* CSS3
* JavaScript ES6+
* Ollama
* Llama 3.2
* Browser local storage / in-memory application data
* Python HTTP server for local execution

The project does not use React, npm, or a frontend build system.

---

## 5. YOGENDRA MEDARAMETLA

### Agentic AI for Safety Monitoring with Construction Risk Analytics

An enterprise-oriented construction intelligence platform developed as part of the **Infosys Springboard Virtual Internship 7.0**.

The project combines construction safety monitoring, predictive risk analytics, workforce management, financial estimation, materials management, AI assistance, and operational intelligence.

### Major Capabilities

* Real-time safety monitoring
* Safety checklist and incident tracking
* Composite AI risk analytics
* Risk forecasting
* Delay-risk what-if analysis
* Client requirement analysis
* Smart area planning
* BOQ generation
* Materials and inventory management
* Budget and cost variance analysis
* Workforce management
* Equipment and fleet management
* Local AI assistant
* PDF and Excel reporting

### Technology Highlights

* Python
* Streamlit
* Plotly
* Pandas
* NumPy
* SQLAlchemy
* MySQL / SQLite
* Ollama
* Gemma 3 1B
* Scikit-learn
* ReportLab
* OpenPyXL
* Passlib / Bcrypt

The project documentation identifies it as completed and evaluated within the Infosys Springboard Virtual Internship 7.0.

---

## 6. SAIPAVAN

### Construction Intelligence Hub

A Streamlit-based construction management application designed for site managers, engineers, and contractors.

The project combines project monitoring, material estimation, safety analysis, document analysis, and a locally hosted AI assistant.

### Major Features

* Dashboard
* Project Monitoring
* Document Analyzer
* Material Estimator
* Safety Analysis
* AI Assistant
* Project progress monitoring
* Material status monitoring
* Equipment information
* Workforce information
* Construction document analysis
* AI-based safety assessment

### Technology Highlights

* Python
* Streamlit
* Pandas
* NumPy
* Plotly
* Pillow
* Ollama
* Llama 3.2 1B
* Moondream
* PyPDF

The application is designed around local AI processing and does not require cloud AI APIs for its core AI functionality.

---

# Repository Structure

The repository follows a team-member-based organization.

```text
Team-C-Projects/
│
├── ARIF AFZAL/
│   └── Agentic Al for Safety Monitoring with Construction Risk Analytics/
│
├── DIKSHA RAUTELA/
│   ├── auth/
│   ├── config/
│   ├── models/
│   ├── repository/
│   ├── services/
│   ├── ui/
│   └── app.py
│
├── Kallam Swethana Reddy/
│   ├── assets/
│   ├── pages/
│   ├── app.py
│   ├── database.py
│   ├── material_estimator.py
│   ├── ollama_backend.py
│   └── ...
│
├── Kiran Rathod/
│   ├── ai/
│   ├── assets/
│   ├── data/
│   ├── js/
│   ├── styles/
│   ├── *.html
│   └── README.md
│
├── Yogendra Medarametla/
│   └── Agentic-Al-for-Safety-Monitoring-with-Construction-Risk-Analytics/
│       ├── ai_engine/
│       ├── auth/
│       ├── database/
│       ├── screens/
│       ├── tests/
│       └── app.py
│
├── saipavan/
│   ├── CIH.py
│   └── README.md
│
├── README.md
└── LICENSE
```

> Individual project structures may change as development continues. The root repository only defines the team-level organization.

---

# Development Approach

The Team C projects are developed independently within the common repository.

Each member is responsible for the development and documentation of their respective project.

The projects may differ in:

* Problem domain implementation
* Application architecture
* Technology stack
* AI model
* Data storage approach
* User interface
* Development stage
* Testing approach

The repository therefore does **not** require all projects to follow a single technical architecture.

---

# Common Development Themes

Although the projects have different implementations, several common themes appear across the repository:

* Construction project management
* Artificial intelligence
* Local AI / LLM integration
* Risk analysis
* Safety monitoring
* Material estimation
* Project monitoring
* Budget management
* Reporting
* Data visualization
* Operational intelligence

These common themes reflect the construction-management and AI-oriented direction of the team's project work.

---

# Milestone-Based Development

The projects are developed progressively according to the assigned project milestones.

The repository may contain projects at different milestone stages because individual members have different development scopes and progress levels.

The repository is intended to preserve this progression rather than artificially standardize the completion status of every project.

---

# Technology Diversity

The repository intentionally contains multiple technology approaches.

Examples include:

| Technology / Approach   | Used In                                    |
| ----------------------- | ------------------------------------------ |
| Python                  | Multiple projects                          |
| Streamlit               | Arif, Diksha, Swethana, Yogendra, Saipavan |
| HTML / CSS / JavaScript | Kiran                                      |
| SQLite                  | Multiple projects                          |
| MySQL                   | Yogendra                                   |
| Ollama                  | Multiple AI-enabled projects               |
| Llama models            | Multiple projects                          |
| Plotly                  | Multiple projects                          |
| ReportLab               | Selected projects                          |
| OpenPyXL                | Selected projects                          |
| SQLAlchemy              | Selected projects                          |
| Local browser data      | Kiran                                      |

This demonstrates the team's exploration of different approaches to solving construction-management and AI-related problems.

---

# Running Individual Projects

Each project has its own setup requirements.

Before running a project, navigate into the corresponding team member's directory and refer to its project-level documentation.

For example:

```bash
cd "ARIF AFZAL/Agentic Al for Safety Monitoring with Construction Risk Analytics"
```

or:

```bash
cd "Kiran Rathod"
```

or:

```bash
cd "saipavan"
```

Project-specific dependencies should be installed according to the `requirements.txt` or setup instructions provided within that project.

---

# Local AI

Several projects in this repository use locally hosted AI through **Ollama**.

Depending on the project, different local models and AI capabilities are used.

Examples include:

* Llama 3.2
* Llama 3.2 1B
* Gemma 3 1B
* Moondream

Because AI configuration differs between projects, refer to the individual project's documentation before starting its AI services.

---

# Security

Team members should never commit:

* Passwords
* API keys
* Authentication credentials
* Database credentials
* Private tokens
* `.env` files containing secrets
* Other sensitive configuration

Environment-specific configuration should be maintained locally and excluded from version control where appropriate.

---

# Contribution Guidelines

This is a team repository containing independently maintained projects.

When making changes:

1. Work primarily within your assigned project directory.
2. Do not modify another member's project without coordination.
3. Keep project-specific dependencies inside the appropriate project.
4. Maintain project documentation when introducing significant changes.
5. Test changes before committing.
6. Review staged changes before pushing.
7. Use meaningful commit messages.
8. Avoid committing sensitive information.
9. Coordinate changes to root-level files with the team.
10. Preserve the existing repository structure.

---

# Repository-Level Files

The root of the repository contains team-level documentation and configuration.

```text
README.md
LICENSE
```

Individual projects may contain their own README files, licenses, configuration files, documentation, and dependency definitions.

---

# Licensing

This repository contains multiple independently developed projects contributed by members of Team C.

The repository-level `LICENSE` provides the MIT License terms for material that the respective contributors are authorized to distribute under those terms.

Individual projects may contain:

* Their own license files
* Third-party libraries
* Third-party assets
* External dependencies
* Components subject to separate licenses

Third-party licenses and intellectual-property notices remain applicable where required.

For project-specific licensing information, refer to the documentation and license files within the respective project directory.

---

# Team

## Team C — Infosys Project

| Member                    | Project                                                           |
| ------------------------- | ----------------------------------------------------------------- |
| **Arif Afzal**            | Agentic AI for Safety Monitoring with Construction Risk Analytics |
| **Diksha Rautela**        | Construction Intelligence Hub                                     |
| **Kallam Swethana Reddy** | Construction Intelligence Hub                                     |
| **Kiran Rathod**          | Construction Intelligent Hub                                      |
| **Yogendra Medarametla**  | Agentic AI for Safety Monitoring with Construction Risk Analytics |
| **Saipavan**              | Construction Intelligence Hub                                     |

---

# Repository Information

**Repository:** `Team-C-Projects`

**Organization / Owner:** `Ariftech01`

**Primary Branch:** `main`

**Repository Type:** Public

**Team Size:** 6 Members

**Purpose:** Infosys project development, milestone progression, project evaluation, documentation, and demonstration.

---

## Disclaimer

This repository is maintained for project development, educational, internship, evaluation, and demonstration purposes.

Project implementations, sample data, AI models, dependencies, and third-party components may have their own limitations and licensing requirements.

Users should review the documentation and licensing information of each individual project and its dependencies before using, modifying, or redistributing the contents.

---

## Acknowledgment

We acknowledge the guidance and support provided through the Infosys project program and the mentors involved in the team's project development process.

---

**Team C — Infosys Project**

**Six Members • Six Individual Projects • One Team Repository**
