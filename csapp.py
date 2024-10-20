import streamlit as st
import json
import requests
from typing import Dict, Any, Optional

# Constants
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
GEMINI_API_KEY = "AIzaSyBqkHfLgQj0Q7r8EMRDmwfAb8-KTIG-40s"  # Replace with your actual API key

# Data handling
def load_data(file_path: str = r'C:\Users\sivak\Downloads\Telegram Desktop\csbot\sampledata.json') -> Dict[str, Any]:
    with open(file_path) as f:
        return json.load(f)

# API interaction
def get_gemini_response(question: str, context: Optional[str] = None) -> str:
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": question
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers=headers)
        response.raise_for_status()
        # Extract and return the response content
        return response.json().get("result", {}).get("text", "Sorry, I couldn't understand that.")
    except requests.RequestException as e:
        return f"Error: Could not fetch response from Gemini API. {e}"

# Business logic
class CustomerSupportAssistant:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def get_order_info(self, order_id: str) -> str:
        order_info = self.data.get("orders", {}).get(order_id)
        if order_info:
            return (f"Order Status: {order_info['status']}, "
                    f"Tracking Number: {order_info['tracking_number']}, "
                    f"Expected Delivery: {order_info['expected_delivery']}.")
        return "Sorry, I couldn't find that order ID."

    def get_returns_policy(self) -> str:
        return self.data.get("returns_policy", "Sorry, I couldn't find the returns policy.")

    def get_product_info(self, product_id: str) -> str:
        product_info = self.data.get("products", {}).get(product_id)
        if product_info:
            return (f"Product: {product_info['name']}, "
                    f"Price: {product_info['price']}, "
                    f"Available: {'Yes' if product_info['available'] else 'No'}.")
        return "Sorry, I couldn't find that product."

    def process_query(self, query: str) -> str:
        query_lower = query.lower()
    
    # Check for order-related queries
        if "track" in query_lower or "order" in query_lower:
            order_id = query_lower.split()[-1]
            return self.get_order_info(order_id)
    
    # Check for return policy queries
        elif "return" in query_lower:
            return self.get_returns_policy()
    
    # Check for product-related queries
        elif "product" in query_lower or "price" in query_lower or "available" in query_lower:
        # Try to extract the product name from the query
            for product_id, product_info in self.data.get("products", {}).items():
                if product_info["name"].lower() in query_lower:
                    return self.get_product_info(product_id)
    
    # Fallback to using the Gemini API for more general queries
        else:
            return get_gemini_response(query, context=st.session_state.get('context', ''))



# Streamlit UI
class CustomerSupportUI:
    def __init__(self, assistant: CustomerSupportAssistant):
        self.assistant = assistant

    def run(self):
        st.title("Customer Support Assistant")
        st.write("Ask me anything about your order or our products!")

        if 'user' not in st.session_state:
            st.session_state.user = None

        if st.session_state.user is None:
            self.show_login()
        else:
            self.show_chat_interface()

    def show_login(self):
        username = st.text_input("Enter your username:")
        if st.button("Login"):
            if username:
                st.session_state.user = username
                st.success(f"Logged in as {username}")
            else:
                st.error("Please enter a username.")

    def show_chat_interface(self):
        if 'context' not in st.session_state:
            st.session_state.context = ""

        user_input = st.text_input("Your Question:", "")
        if st.button("Ask"):
            response = self.assistant.process_query(user_input)
            st.write(f"Assistant: {response}")
            self.update_context(user_input, response)

    def update_context(self, user_input: str, response: str):
        st.session_state.context += f"\nUser: {user_input}\nAssistant: {response}"

# Main execution
def main():
    data = load_data()
    assistant = CustomerSupportAssistant(data)
    ui = CustomerSupportUI(assistant)
    ui.run()

if __name__ == "__main__":
    main()
