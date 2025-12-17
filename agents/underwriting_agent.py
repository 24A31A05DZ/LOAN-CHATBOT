"""
Underwriting Agent - Worker Agent
Fetches credit score from mock Credit Bureau JSON
Applies underwriting rules to decide loan approval
Rules:
- Credit score < 700 → Reject
- Loan ≤ pre-approved limit → Approve
- Loan ≤ 2× pre-approved limit → Ask salary slip
- EMI ≤ 50% salary → Approve
- Else → Reject
"""


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Calculate EMI using standard formula"""
    if annual_rate == 0:
        return principal / tenure_months
    monthly_rate = annual_rate / (12 * 100)
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    return round(emi, 2)


from typing import Optional

def process(session: dict, user_input: Optional[str] = None) -> dict:
    """
    Underwriting Agent processes loan application
    Returns decision based on credit rules
    """
    print("[UNDERWRITING AGENT] Starting credit assessment...")
    
    customer = session.get("customer", {})
    loan_amount = session.get("loan_amount", 0)
    loan_tenure = session.get("loan_tenure", 12)
    interest_rate = session.get("interest_rate", 10.5)
    
    credit_score = customer.get("credit_score", 0)
    preapproved_limit = customer.get("preapproved_limit", 0)
    salary = customer.get("salary", 0)
    
    emi = calculate_emi(loan_amount, interest_rate, loan_tenure)
    session["calculated_emi"] = emi
    
    print(f"[UNDERWRITING AGENT] Credit Score: {credit_score}")
    print(f"[UNDERWRITING AGENT] Pre-approved Limit: ₹{preapproved_limit:,.0f}")
    print(f"[UNDERWRITING AGENT] Requested Amount: ₹{loan_amount:,.0f}")
    print(f"[UNDERWRITING AGENT] Monthly Salary: ₹{salary:,.0f}")
    print(f"[UNDERWRITING AGENT] Calculated EMI: ₹{emi:,.0f}")
    
    response = {}
    
    if credit_score < 700:
        print(f"[UNDERWRITING AGENT] DECISION: REJECTED (Credit score {credit_score} < 700)")
        response["decision"] = "rejected"
        response["reason"] = "low_credit_score"
        response["message"] = (
            f"❌ Loan Application Status: NOT APPROVED\n\n"
            f"Unfortunately, we cannot approve your loan at this time.\n"
            f"Reason: Your credit score ({credit_score}) does not meet our minimum requirement of 700.\n\n"
            f"💡 Tips to improve your credit score:\n"
            f"• Pay all EMIs and credit card bills on time\n"
            f"• Keep credit utilization below 30%\n"
            f"• Avoid multiple loan applications\n\n"
            f"Please try again after improving your credit score. Thank you for considering us!"
        )
        response["next_state"] = "rejected"
        session["underwriting_state"] = "rejected"
        session["loan_status"] = "rejected"
    
    elif loan_amount <= preapproved_limit:
        print(f"[UNDERWRITING AGENT] DECISION: APPROVED (Loan ≤ pre-approved limit)")
        response["decision"] = "approved"
        response["reason"] = "within_preapproved_limit"
        response["message"] = (
            f"🎉 Congratulations! Your Loan is APPROVED!\n\n"
            f"📋 Loan Details:\n"
            f"• Loan Amount: ₹{loan_amount:,.0f}\n"
            f"• Tenure: {loan_tenure} months\n"
            f"• Interest Rate: {interest_rate}% p.a.\n"
            f"• Monthly EMI: ₹{emi:,.0f}\n\n"
            f"Your loan is within your pre-approved limit of ₹{preapproved_limit:,.0f}.\n"
            f"I'm generating your sanction letter now..."
        )
        response["next_state"] = "approved"
        response["proceed_to_sanction"] = True
        session["underwriting_state"] = "approved"
        session["loan_status"] = "approved"
        session["approved_amount"] = loan_amount
    
    elif loan_amount <= 2 * preapproved_limit:
        print(f"[UNDERWRITING AGENT] DECISION: NEEDS SALARY VERIFICATION (Loan ≤ 2× pre-approved limit)")
        response["decision"] = "needs_salary_proof"
        response["reason"] = "exceeds_preapproved_needs_verification"
        response["message"] = (
            f"📝 Additional Verification Required\n\n"
            f"Your requested loan amount (₹{loan_amount:,.0f}) exceeds your pre-approved limit "
            f"of ₹{preapproved_limit:,.0f}.\n\n"
            f"To proceed, I'll need to verify your income. Please upload your latest salary slip.\n\n"
            f"Click the 'Upload Salary Slip' button below to continue."
        )
        response["next_state"] = "awaiting_salary_slip"
        response["show_upload"] = True
        session["underwriting_state"] = "awaiting_salary_slip"
        session["loan_status"] = "pending_verification"
    
    else:
        print(f"[UNDERWRITING AGENT] DECISION: REJECTED (Loan > 2× pre-approved limit)")
        response["decision"] = "rejected"
        response["reason"] = "exceeds_maximum_limit"
        response["message"] = (
            f"❌ Loan Application Status: NOT APPROVED\n\n"
            f"Your requested loan amount (₹{loan_amount:,.0f}) exceeds the maximum eligible amount.\n"
            f"Maximum eligible: ₹{2 * preapproved_limit:,.0f} (2× your pre-approved limit)\n\n"
            f"Would you like to apply for a lower amount? Please start a new application with an amount "
            f"up to ₹{2 * preapproved_limit:,.0f}."
        )
        response["next_state"] = "rejected"
        session["underwriting_state"] = "rejected"
        session["loan_status"] = "rejected"
    
    return response


def process_salary_verification(session: dict, salary_uploaded: bool = False) -> dict:
    """
    Process salary slip verification
    Checks if EMI ≤ 50% of salary
    """
    print("[UNDERWRITING AGENT] Processing salary verification...")
    
    customer = session.get("customer", {})
    loan_amount = session.get("loan_amount", 0)
    loan_tenure = session.get("loan_tenure", 12)
    interest_rate = session.get("interest_rate", 10.5)
    salary = customer.get("salary", 0)
    
    emi = calculate_emi(loan_amount, interest_rate, loan_tenure)
    emi_to_salary_ratio = (emi / salary) * 100 if salary > 0 else 100
    
    print(f"[UNDERWRITING AGENT] Salary from slip: ₹{salary:,.0f}")
    print(f"[UNDERWRITING AGENT] EMI: ₹{emi:,.0f}")
    print(f"[UNDERWRITING AGENT] EMI to Salary Ratio: {emi_to_salary_ratio:.1f}%")
    
    response = {}
    
    if emi <= 0.5 * salary:
        print(f"[UNDERWRITING AGENT] DECISION: APPROVED (EMI ≤ 50% salary)")
        response["decision"] = "approved"
        response["reason"] = "salary_verified"
        response["message"] = (
            f"🎉 Congratulations! Your Loan is APPROVED!\n\n"
            f"📋 Loan Details:\n"
            f"• Loan Amount: ₹{loan_amount:,.0f}\n"
            f"• Tenure: {loan_tenure} months\n"
            f"• Interest Rate: {interest_rate}% p.a.\n"
            f"• Monthly EMI: ₹{emi:,.0f}\n\n"
            f"Your salary verification was successful.\n"
            f"EMI to Income Ratio: {emi_to_salary_ratio:.1f}% (within 50% limit)\n\n"
            f"I'm generating your sanction letter now..."
        )
        response["next_state"] = "approved"
        response["proceed_to_sanction"] = True
        session["underwriting_state"] = "approved"
        session["loan_status"] = "approved"
        session["approved_amount"] = loan_amount
    else:
        print(f"[UNDERWRITING AGENT] DECISION: REJECTED (EMI > 50% salary)")
        max_emi = 0.5 * salary
        max_loan = calculate_max_loan_for_emi(max_emi, interest_rate, loan_tenure)
        response["decision"] = "rejected"
        response["reason"] = "high_emi_ratio"
        response["message"] = (
            f"❌ Loan Application Status: NOT APPROVED\n\n"
            f"Your EMI (₹{emi:,.0f}) exceeds 50% of your monthly salary (₹{salary:,.0f}).\n"
            f"EMI to Income Ratio: {emi_to_salary_ratio:.1f}%\n\n"
            f"Maximum loan amount you can avail with your income: ₹{max_loan:,.0f}\n\n"
            f"Would you like to apply for a lower amount? Please start a new application."
        )
        response["next_state"] = "rejected"
        session["underwriting_state"] = "rejected"
        session["loan_status"] = "rejected"
    
    return response


def calculate_max_loan_for_emi(max_emi: float, annual_rate: float, tenure_months: int) -> float:
    """Calculate maximum loan amount for given EMI"""
    if annual_rate == 0:
        return max_emi * tenure_months
    monthly_rate = annual_rate / (12 * 100)
    principal = max_emi * (((1 + monthly_rate) ** tenure_months) - 1) / (monthly_rate * ((1 + monthly_rate) ** tenure_months))
    return round(principal, 0)
