# Conversational Kafka with Azure OpenAI – POC

#[Kafka Insight POC](assets/arch.png)

## 🚀 Overview
This repository contains a proof-of-concept that integrates **Apache Kafka** with **Azure OpenAI** to provide a **conversational interface** for Kafka operations.  
Instead of running CLI commands, users can type natural language prompts such as:

- "List topics"
- "Create a topic called test-topic with one-day retention"
- "What is the retention period of test-topic?"
- "What is ISR?"

The AI agent interprets the request, generates Kafka AdminClient code, executes it, and returns results in a **human-readable format**.

---

## 🏗 Architecture
- **Zookeeper & Kafka**: Messaging backbone (Confluent Docker images).
- **Backend (FastAPI)**: Handles user prompts, calls Azure OpenAI, executes Kafka code.
- **Azure OpenAI**: Translates natural language into Python Kafka operations.
- **Frontend (Nginx + HTML/JS)**: Lightweight conversational UI.

**Flow**:
```
User → Conversational UI → FastAPI Backend → Azure OpenAI → Kafka Cluster → Human-readable Results
```

---

## ⚡ Features
- Conversational Kafka topic management.
- Query topic configurations (e.g., retention.ms).
- Create new topics with defined retention.
- Explain Kafka concepts like ISR.
- Fully containerized setup for quick start.

---

## 📦 Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/AyodhyaDayananda/kafka-insight-poc.git
cd kafka-insight-poc
```

### 2. Environment Variables
Create a `.env` file in the `backend/` folder:

```ini
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment>
```

### 3. Start Kafka + Zookeeper
```bash
cd kafka-docker
docker-compose up -d
```

### 4. Run Backend
```bash
cd ../backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run Frontend
```bash
cd ../frontend
python -m http.server 8080
```

---

## 🎥 Demo
Example interaction:

```
You: create a topic call test-topic with one day retention
AI: Topic test-topic created successfully

You: what is the retention period
AI: Retention for test-topic: 1.00 days (24.00 hours)
```

---

## 📸 Screenshots
👉 Insert screenshots here:
- Docker services running
- Conversational UI
- Topic creation and retention response

---

## 📂 Repository Structure
```
kafka-insight-poc/
├── backend/        # FastAPI + Azure OpenAI integration
├── frontend/       # Conversational UI
├── kafka-docker/   # Kafka + Zookeeper Docker setup
└── README.md
```

---

## 🔗 GitHub Repository
[Kafka Insight POC](https://github.com/AyodhyaDayananda/kafka-insight-poc)

---

## 🏁 Strategic Outlook
This POC demonstrates the future of **AI-driven AIOps**:
- Human-readable infrastructure insights
- Lower barrier to platform operations
- AI as the interface for infrastructure

---

## 🧑‍💻 Author
**Ayodhya Dayananda**
