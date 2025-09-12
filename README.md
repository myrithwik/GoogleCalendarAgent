# 🧠 Agent Platform

An advanced **multi-agent orchestration system** built in Python, featuring a **General Agent**, a **Google Calendar Agent**, and a **Virtual Date Scheduling Agent**.  
This platform demonstrates how to design, route, and execute AI driven workflows by combining **LLM reasoning**, **tool use**, and **external API integrations**.

---

## 🚀 Key Features

- **Smart Routing with Pydantic**  
  Requests are first analyzed through a Pydantic model to classify intent and direct them to the correct agent (General, Calendar, or Date Scheduler).

- **Composable Agent Architecture**  
  Each agent specializes in its own domain (conversation, calendar, or scheduling) and can be extended with new capabilities.

- **Google Calendar Integration**  
  Supports listing calendars, listing events, creating events, and even generating new calendars automatically.

- **Automated Date Scheduling**  
  Finds overlapping availability between two calendars, selects the optimal 1 hour window, and generates personalized virtual date ideas.

- **LLM-Orchestrated Tool Use**  
  Separates responsibilities between:
  - **Extraction agents** that parse structured input from natural language.
  - **Action agents** that execute API calls.
  - **Response agents** that generate user friendly summaries.

---

## 🏗️ Architecture Overview

### Initial Router
- Uses a **Pydantic schema** to classify user intent.
- Routes requests to one of:
  - **General Agent**
  - **Calendar Agent**
  - **Date Scheduler Agent**

---

### General Agent
- Functions as a **general GPT5 assistant**.  
- Handles open ended conversation and reasoning tasks by leveraging chat history.

---

### Calendar Agent
- Specializes in **Google Calendar operations**:
  - **Make new calendar**
  - **List calendars**
  - **List events**
  - **Create new event**
- Workflow:
  1. Extract structured inputs from the user prompt.  
  2. Call the Google Calendar API with the extracted data.  
  3. Pass results through a response LLM for clean, human readable outputs.

---

### Date Scheduler Agent
- Orchestrates **end-to-end virtual date planning**.  
- Tool functions:
  - **Extract input specifications** (days, timeframes, date type).
  - **Find best time** by merging two users’ availability.
  - **Generate date ideas** (personalized, creative, and context aware).
  - **Create event** directly in Google Calendar with the chosen idea and time.
- Guided by a **system prompt** that enforces step by step reasoning and tool execution.

---

## ✨ Why This Project Stands Out

- **End-to-End AI Workflow**: From natural language to actionable results in external systems.  
- **Real World Impact**: Solves the modern challenge of coordination and decision making with LLM driven automation.  
- **Scalable Design**: New agents and tools can be plugged into the router without breaking existing functionality.  
