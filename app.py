from flask import Flask, render_template, request, jsonify
import json
import google.generativeai as genai
from fuzzywuzzy import process

app = Flask(__name__)

# Configure Google Gemini API Key
genai.configure(api_key="AIzaSyD2z3gmpyTx74yKh0z5YvkMTcoygUGf5r0")

# Load deals data
try:
    with open('data/deals.json', encoding='utf-8') as f:
        deals = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    deals = []

# Define category mappings
category_mappings = {
    "mobile": "Mobile Deals",
    "laptop": "Laptop Deals",
    "accessories": "Accessories Deals"
}

def analyze_query_with_gemini(user_input):
    """
    Uses Google's Gemini API to analyze user queries.
    Extracts product category or provides a conversational response.
    """
    prompt = f"""
    You are a smart shopping assistant. Answer user queries conversationally.
    If the query is about product deals (e.g., 'best mobile deals', 'laptop under 50000'),
    return ONLY the product category (mobile, laptop, accessories), Brand,Product,	Price,Discount,Rating,Store(flipkart, amazon,croma,Reliance Digital) and their urls to buy  json without extra text.
    
    If the query is a greeting (like 'hi' or 'hello'), respond with a friendly greeting and suggest available deals.
    
    User Query: "{user_input}"
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        if "429" in str(e):  # Handle quota exceeded error
            return "Sorry, I've hit my query limit for now. Try again later or ask something simple!"
        return "Sorry, I encountered an error processing your request. Try again later."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_deal', methods=['POST'])
def get_deal():
    user_input = request.json.get('message', '').strip().lower()
    
    if not user_input:
        return jsonify({"reply": "❌ Please enter a valid query."})
    
    ai_response = analyze_query_with_gemini(user_input)
    
    # Check for greetings
    if any(ai_response.lower().startswith(word) for word in ["hello", "hi", "hey"]):
        return jsonify({
            "reply": ai_response,
            "options": list(category_mappings.values())
        })
    ai_response = json.loads(ai_response.strip("```").strip("json"))
    # Match Gemini output with category mappings using fuzzy matching
    # match = process.extractOne(ai_response.lower(), category_mappings.keys(), score_cutoff=70)
    # if match is None:  # Handle case where no match is found
    #     return jsonify({"reply": "<p style='color: red; font-weight: bold;'>❌ I didn’t understand that. Try asking about mobile, laptop, or accessories deals!</p>"})
    
    # best_match, score = match
    # selected_category = category_mappings.get(best_match)
    
    # Find matching deals
    # matching_deals = [d for d in deals if selected_category and d["category"].lower() == best_match]
    
    if 1==1:
        response = f"<h3 class='text-xl font-bold text-red-600 mb-2'>🔥 Exclusive ! 🔥</h3>"
        response += "<table border='1' style='width:100%; border-collapse: collapse; text-align: center;'>"
        response += "<tr><th>Brand</th><th>Product</th><th>Price</th><th>Discount</th><th>Rating</th><th>Store</th></tr>"
        
        for d in ai_response:
            response += (
                f"<tr>"
                f"<td>{d.get('Brand', 'Unknown')}</td>"
                f"<td>{d.get('Product', 'N/A')}</td>"
                f"<td>₹{d.get('Price', 'N/A').strip("₹")}</td>"
                f"<td>{d.get('Discount', 'N/A')}</td>"
                f"<td>{d.get('Rating', 'N/A')} ⭐</td>"
                f"<td>{d.get('Store', 'Unavailable')}</td>"
                f"<td><a href='{d.get('url', '#')}' target='_blank'>Buy Now</a></td>"
                f"</tr>"
            )
        response += "</table>"
    else:
        response = "<p style='color: red; font-weight: bold;'>❌ No matching deals found. Try another query!</p>"
    
    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(debug=True)

