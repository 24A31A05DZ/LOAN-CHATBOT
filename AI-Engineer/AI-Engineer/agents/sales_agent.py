"""
Sales Agent - Worker Agent
Collects loan amount and tenure from user
Provides EMI estimates to persuade user
"""

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Calculate EMI using standard formula"""
    if annual_rate == 0:
        return principal / tenure_months
    monthly_rate = annual_rate / (12 * 100)
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    return round(emi, 2)


def process(session: dict, user_input: str) -> dict:
    """
    Sales Agent processes user input to collect loan details
    Returns response with next state information
    """
    print(f"[SALES AGENT] Processing input: {user_input}")
    
    state = session.get("sales_state", "ask_amount")
    response = {}
    
    if state == "ask_amount":
        try:
            amount = float(user_input.replace(",", "").replace("₹", "").strip())
            if amount < 10000:
                response["message"] = "The minimum loan amount is ₹10,000. Please enter a valid amount."
                response["next_state"] = "ask_amount"
            elif amount > 5000000:
                response["message"] = "The maximum loan amount is ₹50,00,000. Please enter a valid amount."
                response["next_state"] = "ask_amount"
            else:
                session["loan_amount"] = amount
                response["message"] = f"Great! You've requested a loan of ₹{amount:,.0f}. Now, please tell me your preferred loan tenure in months (12 to 72 months)."
                response["next_state"] = "ask_tenure"
                session["sales_state"] = "ask_tenure"
                print(f"[SALES AGENT] Loan amount captured: ₹{amount:,.0f}")
        except ValueError:
            response["message"] = "I couldn't understand that amount. Please enter a valid number (e.g., 300000 or 3,00,000)."
            response["next_state"] = "ask_amount"
    
    elif state == "ask_tenure":
        try:
            tenure = int(user_input.strip())
            if tenure < 12:
                response["message"] = "Minimum tenure is 12 months. Please enter a valid tenure."
                response["next_state"] = "ask_tenure"
            elif tenure > 72:
                response["message"] = "Maximum tenure is 72 months. Please enter a valid tenure."
                response["next_state"] = "ask_tenure"
            else:
                session["loan_tenure"] = tenure
                loan_amount = session.get("loan_amount", 0)
                interest_rate = session.get("interest_rate", 10.5)
                emi = calculate_emi(loan_amount, interest_rate, tenure)
                session["estimated_emi"] = emi
                
                response["message"] = (
                    f"Excellent choice! Here's your loan summary:\n\n"
                    f"📋 Loan Amount: ₹{loan_amount:,.0f}\n"
                    f"📅 Tenure: {tenure} months\n"
                    f"💰 Interest Rate: {interest_rate}% p.a.\n"
                    f"💵 Estimated EMI: ₹{emi:,.0f}/month\n\n"
                    f"This looks like a great deal! Shall I proceed with the verification? (Yes/No)"
                )
                response["next_state"] = "confirm"
                session["sales_state"] = "confirm"
                print(f"[SALES AGENT] Tenure captured: {tenure} months, EMI: ₹{emi:,.0f}")
        except ValueError:
            response["message"] = "Please enter a valid number of months (e.g., 24 or 36)."
            response["next_state"] = "ask_tenure"
    
    elif state == "confirm":
        user_response = user_input.lower().strip()
        if user_response in ["yes", "y", "proceed", "ok", "sure", "yeah"]:
            response["message"] = "Perfect! Let me verify your details from our records..."
            response["next_state"] = "complete"
            response["proceed_to_verification"] = True
            session["sales_state"] = "complete"
            print("[SALES AGENT] User confirmed. Proceeding to verification.")
        elif user_response in ["no", "n", "cancel", "stop"]:
            response["message"] = "No problem! If you change your mind, feel free to start again. Have a great day!"
            response["next_state"] = "cancelled"
            session["sales_state"] = "cancelled"
            print("[SALES AGENT] User cancelled the application.")
        else:
            response["message"] = "Please respond with 'Yes' to proceed or 'No' to cancel."
            response["next_state"] = "confirm"
    
    return response


def get_initial_message() -> str:
    """Return the initial sales pitch message"""
    return (
        "Welcome to our Personal Loan service! 🏦\n\n"
        "I'm here to help you get the best loan offer tailored to your needs.\n\n"
        "To get started, please tell me how much loan amount you're looking for? (₹10,000 - ₹50,00,000)"
    )
