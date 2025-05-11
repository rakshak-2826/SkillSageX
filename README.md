# SkillSageX

**SkillSageX** is an AI-powered career development companion designed to help students and job-seekers evaluate their readiness, simulate interviews, visualize skill gaps, and receive tailored career and project suggestions.

---

## 🔍 Overview

SkillSageX is part of the HustleNest platform, built to bridge the gap between resumes and real-world job roles. It provides:

- Intelligent resume parsing
- Adaptive interview simulations
- Role-fit scoring and recommendations
- 3D skill graph visualizations
- Personalized learning roadmaps and project ideas
- Final career readiness reports

---

## 🧩 Tech Stack

| Layer       | Technology                                 |
|------------|---------------------------------------------|
| Frontend   | React, Next.js, Three.js, Tailwind CSS      |
| Backend    | Spring Boot (Java)                          |
| AI Engine  | Python (invoked from Java)                  |
| Database   | MySQL                                       |

---

## ✨ Features

- 📝 Resume upload and parsing
- 🤖 AI-powered interview chatbot
- 🧠 Technical & personality evaluation
- 🎯 Role fit scoring and career suggestions
- 🌐 3D skill graph with learning roadmap
- 🛠️ Personalized project ideas
- 📊 Final report summarizing user's career profile

---

## 📁 Project Structure

```
SkillSageX/
├── backend/                # Spring Boot application
├── frontend/               # Next.js + React frontend
├── ai-engine/              # Python scripts (CLI modules)
├── database/               # MySQL schema and seed data
└── README.md
```

---

## 🔄 System Workflow

1. User uploads resume via UI
2. Spring Boot backend stores file and invokes Python scripts using `ProcessBuilder`
3. Python modules (e.g. `resume_parser.py`, `chatbot_engine.py`) process data and return JSON
4. Java backend stores results in MySQL
5. Frontend fetches and displays results via REST APIs

---

## ⚙️ Installation & Setup

> **Prerequisites:** Node.js, Java 17+, Python 3.8+, MySQL

### 1. Clone the repository
```bash
git clone https://github.com/your-username/SkillSageX.git
cd SkillSageX
```

### 2. Set up the database
- Create a MySQL database: `skillsagex`
- Run schema script in `/database/schema.sql`
- Configure DB credentials in `/backend/src/main/resources/application.properties`

### 3. Start the backend
```bash
cd backend
./mvnw spring-boot:run
```

### 4. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Configure Python engine (optional virtual env recommended)
```bash
cd ai-engine
pip install -r requirements.txt
```

---

## 📌 Python Modules (CLI-based)

Each Python script reads from JSON input and writes to stdout (JSON):

- `resume_parser.py`
- `chatbot_engine.py`
- `answer_scorer.py`
- `personality_analyzer.py`
- `role_suggester.py`
- `skill_graph.py`
- `project_generator.py`
- `summary_builder.py`

Example call from Java:
```java
new ProcessBuilder("python3", "resume_parser.py", "input.json")
```

---

## 📊 Database Tables

- `users`  
- `resumes`  
- `chat_logs`  
- `evaluation_scores`  
- `suggested_roles`  
- `skill_graphs`  
- `projects`  
- `summaries`  

Each user session is fully tracked and persists across modules.

---

## 🧠 Key Outcomes for Users

- Full resume analysis and skill extraction  
- Role-aware, AI-driven interview simulation  
- Scoring across technical, personality, and fit metrics  
- Alternate career paths with fit percentages  
- Interactive skill graphs and personalized roadmaps  
- Tailored project ideas for skill improvement  
- Comprehensive final summary report

---

## 📬 Contributing

We welcome contributions! Please open issues or submit pull requests to enhance functionality, fix bugs, or improve documentation.

---

## 📄 License

[MIT](LICENSE)

---

## 🙋‍♀️ Questions?

Feel free to reach out via GitHub Issues or Discussions for support or ideas.
