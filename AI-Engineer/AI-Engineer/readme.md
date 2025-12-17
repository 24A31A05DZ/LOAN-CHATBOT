# Agentic AI Personal Loan Chatbot

## Overview
A hackathon-ready prototype of an Agentic AI Personal Loan Chatbot for BFSI NBFC (Tata Capital-like use case). Built with a Master-Worker Agent architecture for intelligent loan processing.

## Tech Stack
- **Backend**: Python + FastAPI
- **Frontend**: HTML + CSS + JavaScript (vanilla)
- **AI Logic**: Rule-based + prompt-based agent simulation (no external LLM APIs)
- **PDF Generation**: reportlab
- **Storage**: JSON files (no database)

## Architecture

### Master Agent (Orchestrator)
- Handles entire conversation flow
- Decides which Worker Agent to invoke
- Maintains session state per user
- Starts and ends chat

### Worker Agents
1. **Sales Agent**: Collects loan amount and tenure, provides EMI estimates
2. **Verification Agent**: Fetches KYC from mock CRM JSON
3. **Underwriting Agent**: Credit decision logic with rules:
   - Credit score < 700: Reject
   - Loan <= pre-approved limit: Approve
   - Loan <= 2x pre-approved limit: Ask salary slip
   - EMI <= 50% salary: Approve
   - Else: Reject
4. **Sanction Generator**: Generates PDF sanction letter

## Project Structure
```
/
├── main.py                 # FastAPI application
├── agents/
│   ├── __init__.py
│   ├── master_agent.py     # Orchestrator
│   ├── sales_agent.py      # Loan details collection
│   ├── verification_agent.py # KYC verification
│   ├── underwriting_agent.py # Credit decision
│   └── sanction_generator.py # PDF generation
├── data/
│   ├── customers.json      # 10 dummy customers
│   └── offers.json         # Pre-approved offers
├── uploads/                # Salary slips & sanction letters
├── templates/
│   └── index.html          # Chat UI
└── static/
    └── style.css           # Styling
```

## API Endpoints
- `GET /` - Main chat interface
- `POST /chat` - Main conversation endpoint
- `POST /upload-salary` - Salary slip upload
- `GET /download/{filename}` - Download sanction letter
- `GET /health` - Health check

## Test Customers (Phone Numbers)
- 9876543210 - Rajesh Kumar (Credit: 750, Limit: 5L)
- 9876543211 - Priya Sharma (Credit: 680, Limit: 3L) - Will be rejected
- 9876543212 - Amit Patel (Credit: 820, Limit: 8L)
- 9876543213 - Sunita Reddy (Credit: 720, Limit: 4L)
- 9876543214 - Vikram Singh (Credit: 650, Limit: 2L) - Will be rejected
- 9876543215 - Neha Gupta (Credit: 780, Limit: 6L)
- 9876543216 - Rahul Verma (Credit: 710, Limit: 3.5L)
- 9876543217 - Anita Joshi (Credit: 690, Limit: 2.5L) - Will be rejected
- 9876543218 - Sanjay Mehta (Credit: 800, Limit: 7L)
- 9876543219 - Kavita Nair (Credit: 740, Limit: 4.5L)

## Running the Application
The application runs on port 5000 with the command:
```
python main.py
```

## Demo Flow
1. Type "Hi" to start
2. Enter loan amount (e.g., 300000)
3. Enter tenure (e.g., 24 months)
4. Confirm to proceed
5. Enter phone number (use test customer)
6. Confirm identity
7. Receive decision (approve/reject/need salary slip)
8. If approved, download sanction letter PDF
