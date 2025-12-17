"""
Verification Agent - Worker Agent
Fetches KYC data from mock CRM JSON
Validates customer identity
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "customers.json")
OFFERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "offers.json")


def load_customers() -> list:
    """Load customer data from JSON file"""
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def load_offers() -> list:
    """Load offers data from JSON file"""
    with open(OFFERS_PATH, "r") as f:
        return json.load(f)


from typing import Optional

def find_customer_by_phone(phone: str) -> Optional[dict]:
    """Find customer by phone number"""
    customers = load_customers()
    for customer in customers:
        if customer["phone"] == phone:
            return customer
    return None


def find_offer_by_customer_id(customer_id: str) -> Optional[dict]:
    """Find offer by customer ID"""
    offers = load_offers()
    for offer in offers:
        if offer["customer_id"] == customer_id:
            return offer
    return None


def process(session: dict, user_input: str) -> dict:
    """
    Verification Agent processes user input to verify identity
    Returns response with customer data if found
    """
    print(f"[VERIFICATION AGENT] Processing input: {user_input}")
    
    state = session.get("verification_state", "ask_phone")
    response = {}
    
    if state == "ask_phone":
        phone = user_input.strip().replace(" ", "").replace("-", "")
        if len(phone) == 10 and phone.isdigit():
            customer = find_customer_by_phone(phone)
            if customer:
                session["customer"] = customer
                session["customer_id"] = customer["id"]
                offer = find_offer_by_customer_id(customer["id"])
                if offer:
                    session["offer"] = offer
                    session["interest_rate"] = offer["interest_rate"]
                
                response["message"] = (
                    f"✅ Verification Successful!\n\n"
                    f"I found your profile in our system:\n"
                    f"👤 Name: {customer['name']}\n"
                    f"📍 City: {customer['city']}\n"
                    f"📞 Phone: {customer['phone']}\n\n"
                    f"Is this information correct? (Yes/No)"
                )
                response["next_state"] = "confirm_identity"
                session["verification_state"] = "confirm_identity"
                print(f"[VERIFICATION AGENT] Customer found: {customer['name']} (ID: {customer['id']})")
            else:
                response["message"] = (
                    "❌ Sorry, I couldn't find your profile in our system.\n"
                    "Please check your phone number or contact our branch for assistance.\n\n"
                    "Would you like to try again with a different number? (Yes/No)"
                )
                response["next_state"] = "not_found"
                session["verification_state"] = "not_found"
                print("[VERIFICATION AGENT] Customer not found in database")
        else:
            response["message"] = "Please enter a valid 10-digit phone number."
            response["next_state"] = "ask_phone"
    
    elif state == "confirm_identity":
        user_response = user_input.lower().strip()
        if user_response in ["yes", "y", "correct", "right", "ok"]:
            response["message"] = "Great! Your identity has been verified. Let me now check your eligibility..."
            response["next_state"] = "complete"
            response["proceed_to_underwriting"] = True
            session["verification_state"] = "complete"
            session["kyc_verified"] = True
            print("[VERIFICATION AGENT] Identity confirmed. Proceeding to underwriting.")
        elif user_response in ["no", "n", "wrong", "incorrect"]:
            response["message"] = "I apologize for the confusion. Please enter your registered phone number again."
            response["next_state"] = "ask_phone"
            session["verification_state"] = "ask_phone"
            session.pop("customer", None)
            print("[VERIFICATION AGENT] Identity not confirmed. Asking for phone again.")
        else:
            response["message"] = "Please respond with 'Yes' if the details are correct or 'No' if they're not."
            response["next_state"] = "confirm_identity"
    
    elif state == "not_found":
        user_response = user_input.lower().strip()
        if user_response in ["yes", "y"]:
            response["message"] = "Please enter your registered 10-digit phone number."
            response["next_state"] = "ask_phone"
            session["verification_state"] = "ask_phone"
        else:
            response["message"] = "Thank you for your interest. Please visit our nearest branch for assistance. Have a great day!"
            response["next_state"] = "ended"
            session["verification_state"] = "ended"
    
    return response


def get_initial_message() -> str:
    """Return the initial verification message"""
    return "To verify your identity, please enter your registered 10-digit phone number."
