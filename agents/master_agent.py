"""
Master Agent - Orchestrator
Handles entire conversation flow
Decides which Worker Agent to invoke
Maintains session state per user
Starts and ends chat
"""

from agents import sales_agent, verification_agent, underwriting_agent, sanction_generator


def get_initial_state() -> dict:
    """Return initial session state"""
    return {
        "current_agent": "greeting",
        "conversation_stage": "start",
        "sales_state": "ask_amount",
        "verification_state": "ask_phone",
        "underwriting_state": "pending",
        "loan_status": None,
        "kyc_verified": False
    }


def process_message(session: dict, user_input: str) -> dict:
    """
    Master Agent orchestrates the conversation
    Routes to appropriate worker agent based on current state
    """
    print("\n" + "="*60)
    print("[MASTER AGENT] Processing message...")
    print(f"[MASTER AGENT] Current stage: {session.get('conversation_stage', 'unknown')}")
    print(f"[MASTER AGENT] Current agent: {session.get('current_agent', 'unknown')}")
    print(f"[MASTER AGENT] User input: {user_input}")
    print("="*60)
    
    response = {
        "message": "",
        "show_upload": False,
        "show_download": False,
        "download_file": None,
        "session_ended": False
    }
    
    current_agent = session.get("current_agent", "greeting")
    
    if current_agent == "greeting":
        print("[MASTER AGENT] Invoking SALES AGENT for initial greeting")
        session["current_agent"] = "sales"
        session["conversation_stage"] = "collecting_loan_details"
        response["message"] = sales_agent.get_initial_message()
        return response
    
    elif current_agent == "sales":
        print("[MASTER AGENT] Invoking SALES AGENT")
        sales_response = sales_agent.process(session, user_input)
        response["message"] = sales_response.get("message", "")
        
        if sales_response.get("proceed_to_verification"):
            session["current_agent"] = "verification"
            session["conversation_stage"] = "verification"
            verification_msg = verification_agent.get_initial_message()
            response["message"] += "\n\n" + verification_msg
            print("[MASTER AGENT] Transitioning to VERIFICATION AGENT")
        
        elif sales_response.get("next_state") == "cancelled":
            session["current_agent"] = "ended"
            response["session_ended"] = True
            print("[MASTER AGENT] Session ended by user")
        
        return response
    
    elif current_agent == "verification":
        print("[MASTER AGENT] Invoking VERIFICATION AGENT")
        verification_response = verification_agent.process(session, user_input)
        response["message"] = verification_response.get("message", "")
        
        if verification_response.get("proceed_to_underwriting"):
            session["current_agent"] = "underwriting"
            session["conversation_stage"] = "underwriting"
            underwriting_response = underwriting_agent.process(session)
            response["message"] += "\n\n" + underwriting_response.get("message", "")
            response["show_upload"] = underwriting_response.get("show_upload", False)
            print("[MASTER AGENT] Transitioning to UNDERWRITING AGENT")
            
            if underwriting_response.get("proceed_to_sanction"):
                session["current_agent"] = "sanction"
                session["conversation_stage"] = "generating_sanction"
                sanction_response = sanction_generator.generate_sanction_letter(session)
                response["message"] += "\n\n" + sanction_response.get("message", "")
                response["show_download"] = sanction_response.get("show_download", False)
                response["download_file"] = sanction_response.get("filename")
                session["current_agent"] = "completed"
                print("[MASTER AGENT] Loan APPROVED. Sanction letter generated.")
            
            elif underwriting_response.get("decision") == "rejected":
                session["current_agent"] = "ended"
                response["session_ended"] = True
                print("[MASTER AGENT] Loan REJECTED. Session ended.")
        
        elif verification_response.get("next_state") == "ended":
            session["current_agent"] = "ended"
            response["session_ended"] = True
            print("[MASTER AGENT] Verification failed. Session ended.")
        
        return response
    
    elif current_agent == "underwriting":
        if session.get("underwriting_state") == "awaiting_salary_slip":
            response["message"] = "Please upload your salary slip using the button below to continue."
            response["show_upload"] = True
        else:
            response["message"] = "Your application is being processed. Please wait..."
        return response
    
    elif current_agent == "completed":
        response["message"] = (
            "Your loan application has been completed! 🎉\n\n"
            "If you need any further assistance or want to apply for another loan, "
            "please start a new conversation.\n\n"
            "Thank you for choosing Capital Finance Ltd!"
        )
        response["show_download"] = True
        response["download_file"] = session.get("sanction_letter_filename")
        return response
    
    elif current_agent == "ended":
        response["message"] = "This conversation has ended. Please start a new chat for a fresh application."
        response["session_ended"] = True
        return response
    
    response["message"] = "I'm sorry, something went wrong. Please start a new conversation."
    return response


def process_salary_upload(session: dict) -> dict:
    """
    Process after salary slip is uploaded
    Invokes underwriting agent for salary verification
    """
    print("\n" + "="*60)
    print("[MASTER AGENT] Processing salary slip upload...")
    print("="*60)
    
    response = {
        "message": "",
        "show_upload": False,
        "show_download": False,
        "download_file": None,
        "session_ended": False
    }
    
    print("[MASTER AGENT] Invoking UNDERWRITING AGENT for salary verification")
    underwriting_response = underwriting_agent.process_salary_verification(session, salary_uploaded=True)
    response["message"] = underwriting_response.get("message", "")
    
    if underwriting_response.get("proceed_to_sanction"):
        session["current_agent"] = "sanction"
        session["conversation_stage"] = "generating_sanction"
        print("[MASTER AGENT] Invoking SANCTION GENERATOR")
        sanction_response = sanction_generator.generate_sanction_letter(session)
        response["message"] += "\n\n" + sanction_response.get("message", "")
        response["show_download"] = sanction_response.get("show_download", False)
        response["download_file"] = sanction_response.get("filename")
        session["current_agent"] = "completed"
        print("[MASTER AGENT] Loan APPROVED after salary verification. Sanction letter generated.")
    
    elif underwriting_response.get("decision") == "rejected":
        session["current_agent"] = "ended"
        response["session_ended"] = True
        print("[MASTER AGENT] Loan REJECTED after salary verification. Session ended.")
    
    return response
