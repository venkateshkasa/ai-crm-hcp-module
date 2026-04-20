# AI-First CRM HCP Module

## 🚀 Overview
This project is an AI-powered Customer Relationship Management (CRM) system designed for healthcare representatives to log interactions with Healthcare Professionals (HCPs).

The system allows users to log interactions using:
- Structured Form
- Conversational Chat (AI-powered)

---

## 🎯 Features

- 🧾 Form-based interaction logging  
- 💬 Chat-based interaction logging using AI  
- ✏️ Edit existing interactions  
- 📊 View interaction history  
- 🧠 AI-powered summarization  
- 🔮 Suggest next actions  

---

## 🧠 AI & Agent

This project uses:
- **LangGraph** for agent workflow and tool selection  
- **Groq LLM (gemma2-9b-it)** for natural language understanding  

The AI agent:
- Extracts doctor name, notes, and context  
- Decides which tool to use (log/edit/view)  
- Generates summaries and suggestions  

---

## 🧰 LangGraph Tools

1. **Log Interaction** – Save new interaction using AI  
2. **Edit Interaction** – Modify existing interaction  
3. **Get Interaction** – Retrieve interaction history  
4. **Summarize** – Generate short summary  
5. **Suggest Next Action** – Recommend follow-up steps  

---

## 🏗️ Tech Stack

### Frontend
- React
- Redux
- Axios

### Backend
- FastAPI (Python)
- LangGraph
- Groq API

### Database
- SQLite / PostgreSQL

---

## 🔄 System Flow

User Input (Form/Chat)  
→ FastAPI Backend  
→ LangGraph Agent  
→ Groq LLM  
→ Tool Execution  
→ Database Storage  

---

## ⚙️ Setup Instructions

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
