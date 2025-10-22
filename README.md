# 🧠 TourWise Backend – AI-Powered Multi-Agent Travel Planner

The **TourWise Backend** is a FastAPI-based system that powers an AI-driven travel planning assistant.
It generates personalized itineraries, estimates costs, suggests attractions, and automates itinerary delivery using **LangGraph**, **RAG**, and **n8n** integrations.

---

## 🚀 Key Features

* 🤖 **LangGraph Multi-Agent System**
  Modular AI agents (Guide, Budget, Language, Coordinator) coordinate to generate complete itineraries.

* 🔍 **Retrieval-Augmented Generation (RAG)**
  Uses **Pinecone** + **SentenceTransformers** for semantic search and context retrieval.

* 💬 **Natural Language Planning**
  Processes free-form user queries like *"Plan a 3-day trip to Ethiopia"* and converts them into structured travel plans.

* 💸 **Budget Optimization**
  Automatically suggests savings options and calculates total estimated costs.

* ✉️ **Email Workflow Automation**
  Integrates with **n8n** to format and deliver itineraries to users via email.

* 🧭 **Fallback Search System**
  If vector results are insufficient, it performs Google-based retrieval as backup.

---

## 🏗️ Architecture Overview

**Core Components:**

| Component                | Description                                                        |
| ------------------------ | ------------------------------------------------------------------ |
| **FastAPI**              | RESTful API layer for itinerary generation and automation triggers |
| **LangGraph**            | Multi-agent orchestration framework                                |
| **Groq LLM**             | Handles structured reasoning and JSON-based response generation    |
| **Pinecone**             | Vector database for semantic document retrieval                    |
| **SentenceTransformers** | Embedding generation for RAG                                       |
| **n8n Webhook**          | Email delivery automation after itinerary creation                 |

**Agent Workflow:**

1. **Guide Agent** → Retrieves attractions and builds initial itinerary.
2. **Budget Agent** → Adjusts plan according to user’s budget and travel style.
3. **Language Agent** → Adds local language annotations and cultural advice.
4. **Coordinator** → Combines agent results and returns the final structured plan.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/SBAK729/TourWise.git
cd TourWise
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set Up Environment Variables

Create a `.env` file in the `/backend` directory:

```env
PINECONE_API_KEY=your_pinecone_api_key
GROQ_API_KEY=your_groq_api_key
```

### 4️⃣ Run the API

```bash
uvicorn app.main:app --reload
```

Your backend will run at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📡 API Endpoints

### **POST** `/auth/generate-itinerary`

Generates a full itinerary from a user query.

#### Request Example:

```json
{
  "user_input": "plan a 3-day trip to Addis Ababa"
}
```

#### Response Example:

```json
{
  "itinerary": [
    {
      "day": "Day 1",
      "activities": [
        {
          "time": "09:00–10:30",
          "title": "National Museum of Ethiopia",
          "description": "Explore Ethiopia's history and see 'Lucy'.",
          "notes": "Entry fee: $10"
        }
      ]
    }
  ],
  "estimated_total_cost_usd": 1500
}
```

---

## 🧩 n8n Workflow Integration

After the itinerary is generated, a webhook call can trigger an **n8n workflow** to:

* Format the itinerary into an HTML email.
* Send via SMTP or Gmail node.
* Log delivery success/failure back to the backend.

Webhook Example (FastAPI):

```python
import requests

def trigger_n8n_workflow(user_email, itinerary_data):
    n8n_webhook_url = "https://sinbikila.app.n8n.cloud/webhook/send-itinerary-email"
    payload = {"email": user_email, "itinerary": itinerary_data}
    requests.post(n8n_webhook_url, json=payload)
```


## 🐳 Docker Setup

To containerize and deploy on Render or locally:

**Dockerfile**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


## 🧠 Future Improvements

* 🗺️ Integrate Google Maps API for route visualization
* 🧾 Add hotel and flight booking modules
* 🔄 Improve itinerary ranking using real-time review data
* 🧳 Introduce personal travel assistant chatbot

