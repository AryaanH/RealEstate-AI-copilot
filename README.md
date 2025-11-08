# AURA — Real-Estate AI Copilot  
**Data-grounded market intelligence for the Australian property sector**  
Built with **Azure AI Foundry, FastAPI, and modern web architecture.**

---

## Overview  

**AURA (AI Urban Real-Estate Analyst)** is a domain-grounded AI copilot that analyses curated Australian housing reports to generate structured insights on:  
- Housing affordability trends across states  
- Suburb-level growth performance  
- Rental yields & investor hotspots  
- First-home buyer affordability  

It connects directly to an **Azure AI Foundry Agent** enriched with **vector-indexed PDF datasets** (RAG pipeline).  
AURA reads real housing data — not the open web — and responds using structured, concise analysis that feels like a financial report, not a chatbot.

---

## Key Capabilities  

| Feature | Description |
|----------|-------------|
| **RAG Vector Store Integration** | Uses Azure AI Foundry to ground answers in 15+ uploaded government housing PDFs. |
| **Conversational Insights** | Answers policy, affordability, and growth questions through natural chat. |
| **Modern Web UI** | Full-screen, gold-and-red theme built in HTML + CSS + JS (FastAPI-served). |
| **Azure-Integrated Backend** | Powered by FastAPI, connected via Azure SDKs (`azure-ai-projects`, `azure-identity`). |
| **Markdown-formatted Responses** | Clean, professional answers styled like investor reports using the `marked` JS library. |
| **Deployable on Azure App Service** | Containerized using Docker for scalable, production-ready deployment. |

---

## Tech Stack  

**AI Layer:**  
- Azure AI Foundry (Agents + Vector Indexes + Cognitive Search)  
- GPT-4o-mini deployment (custom knowledge grounding)  

**Backend:**  
- FastAPI (Python)  
- Azure SDKs (`azure-ai-projects`, `azure-identity`)  
- `uvicorn` web server  
- `.env` config for secure keys  

**Frontend:**  
- HTML + CSS + Vanilla JS  
- Markdown parsing via [`marked`](https://www.npmjs.com/package/marked)  
- Responsive, dark gold-red UI  

**Infrastructure:**  
- Dockerized container  
- Deployable via Azure App Service  
- CI/CD via GitHub integration  

---

## System Architecture  
User → Web UI (HTML/CSS/JS)  
↓  
FastAPI Backend (Python)  
↓  
Azure AI Foundry Agent  
↓  
Vector Index (PDF Knowledge)  
↓  
GPT-4o-mini → Structured AURA Reply  

---

## Sample Interaction  

**User:** Compare VIC vs NSW housing trends using only the uploaded reports.  
**AURA:**  
> ### VIC vs NSW Housing Trends  
> - **Victoria (VIC):** Melbourne’s median housing values rose 8.1% annually over 25 years, outperforming other states.  
> - **New South Wales (NSW):** Sydney shows steady but cyclical growth, with stronger policy emphasis on affordability initiatives.  
> **Recommendation:** Investors seeking capital growth may prefer VIC; for policy stability and affordability, NSW remains favorable.  

---

## ⚙️ Local Setup  

1️⃣ Clone the Repository 
```bash
git clone https://github.com/AryaanH/RealEstate-AI-Copilot.git
cd RealEstate-AI-Copilot

2️⃣ Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the app
uvicorn src.server:app --reload --port 8000

Open http://localhost:8000 in your browser to access the UI.

Author
Aryaan Hashim

🎓 B.Eng. Software Engineering, Monash University
☁️ Cloud & AI Engineer | Azure + AWS + Applied AI
📍 Melbourne, Australia
LinkedIn: linkedin.com/in/aryaan-hashim
GitHub: github.com/AryaanH

Built to demonstrate applied Azure AI engineering — bridging data, design, and deployment.