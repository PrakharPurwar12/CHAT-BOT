from flask import Flask, render_template, request, jsonify
import json
import google.generativeai as genai
import os


app = Flask(__name__)

# Configure Google Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


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
    return the json list where easch elements contains ONLY the "product_category" of type (mobile, laptop, accessories), "brand" of type string,
    "product" of type string, "price" of type string, "discount" of type string,"rating" of type string,
    "store" of type string (flipkart, amazon,croma,Reliance Digital) if more than one store then add new entry in list and their "urls" of type string to buy in json format without any extra text.

    If the query is a greeting (like 'hi' or 'hello' or 'thank you'), respond with a friendly greeting and suggest available deals.

    User Query: "{user_input}"
    """
    print(prompt)
    try:
        model = genai.GenerativeModel("gemini-3-flash-preview")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        if "429" in str(e):  # Handle quota exceeded error
            return "Sorry, I've hit my query limit for now. Try again later or ask something simple!"
        return "Sorry, I encountered an error processing your request. Try again later."


@app.route('/')
def home():
    return render_template('index.html')

def get_urls(data):
    url = data.get('urls', '')  # Changed from 'url' to 'urls' to match JSON response
    brand = data.get('brand', '')
    product = data.get('product', '')
    price = str(data.get('price', '')).strip("₹").replace(",", "")
    if "flipkart" in url.lower():
        url = "https://www.flipkart.com/search?q="+brand+"+"+product.replace(" ", "+") + "&p%5B%5D=facets.price_range.from%3D"+str(int(price)-10)+"&p%5B%5D=facets.price_range.to%3DMax"
        print(url)
    elif "amazon" in url.lower():
        url = "https://www.amazon.in/s?k="+brand+"+"+product.replace(" ", "+") + "&low-price="+price
        print(url)
    elif "reliancedigital" in url.lower():
        url = "https://www.reliancedigital.in/products?q=" +brand+"+"+product.replace(" ", "+") + "&min_price_effective=%5B" +str(int(price)-10) + ",INR%20TO%20"+str(int(price)+5000) +",INR%5D"
        print(url)
    elif "croma" in url.lower():
        url = "https://www.croma.com/searchB?q=" +brand+"%20"+product.replace(" ", "%20") + "%3Arelevance&text="+ brand+"%20"+product.replace(" ", "%20")
        print(url)
    return url
@app.route('/get_deal', methods=['POST'])
def get_deal():
    user_input = request.json.get('message', '').strip().lower()
    if not user_input:
        return jsonify({"reply": "❌ Please enter a valid query."})

    ai_response = analyze_query_with_gemini(user_input)
    try:
        ai_response = json.loads(ai_response.strip("```").strip("json"))
    except:
        ai_response = {"greeting": ai_response}
    # Check for greetings
    if type(ai_response) == dict:
        if any(ai_response.get("greeting", "not found").lower().startswith(word) for word in
               ["hello", "hi", "hey", "thank you", "you're welcome!"]):
            return jsonify({
                "reply": ai_response.get("greeting", "hello"),
                "options": list(category_mappings.values())
            })
    print(ai_response)

    if 1 == 1:
        response = f"<h3 class='text-xl font-bold text-red-600 mb-2'>🔥 Exclusive ! 🔥</h3>"
        response += "<table border='1' style='width:100%; border-collapse: collapse; text-align: center;'>"
        response += "<tr><th>Brand</th><th>Product</th><th>Price</th><th>Discount</th><th>Rating</th><th>Store</th></tr>"

        for d in ai_response:
            if not type(d) == dict:
                d = dict()

            response += (
                f"<tr>"
                f"<td>{d.get('brand', 'Unknown')}</td>"
                f"<td>{d.get('product', 'N/A')}</td>"
                f"<td>₹{str(d.get('price', 0)).strip('₹')}</td>"
                f"<td>{d.get('discount', 'N/A')}</td>"
                f"<td>{d.get('rating', 'N/A')} ⭐</td>"
                f"<td>{d.get('store', 'Unavailable')}</td>"
                f"<td><a href='{get_urls(d)}' target='_blank'>Buy Now</a></td>"
                f"</tr>"
            )
        response += "</table>"
    else:
        response = "<p style='color: red; font-weight: bold;'>❌ No matching deals found. Try another query!</p>"

    return jsonify({"reply": response})
            
    response += "</table>"
    # else:
    #     response = "<p style='color: red; font-weight: bold;'>❌ No matching deals found. Try another query!</p>"

    return jsonify({"reply": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    #get_deal()