from flask import Flask, render_template,request
import json
import openai
import os
from datetime import datetime
import pandas as pd

# app = Flask(__name__)

# @app.route("/test")
# def test():
#     return render_template("index.html", title="Hello")

# @app.route("/")
# def hello_world():
    
from flask import Flask, render_template, jsonify
import json
import openai
from datetime import datetime
import requests

app = Flask(__name__)

# Initialize OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_KEY")

# File path of the JSON file
file_path = 'products_combined.json'  # Update this path as needed

# Function to load categories and products from a JSON file
def load_categories(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON file: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

# Function to get all products from categories
def get_all_products(categories_data):
    products = []
    for category in categories_data.get("Categories", []):
        products.extend(category.get("data", []))
    return products

# Function to find related products based on the sub-category and other attributes
def find_related_products(products, cart_products):
    related_products = []
    for cart_product in cart_products:
        matching_products = [
            product for product in products
            if (product["name"] != cart_product["name"] and
                product["sub_category"] == cart_product["sub_category"] and
                product.get("gender") == cart_product.get("gender", product.get("gender")))
        ]
        related_products.extend(matching_products)
    return related_products

# Function to create prompts for OpenAI
def create_prompts(friend_name, friend_birthday, cart_products):
    prompts = []
    for product in cart_products:
        prompt = (
            f"Suggest similar and complementary products for my friend {friend_name} whose birthday is on {friend_birthday}. "
            f"She has added the following item to her cart: {product}. "
            "Please recommend similar products and complementary items, ensuring to include products "
            "that match the sub-category and other attributes like gender if applicable. "
            "Provide the names, links, and all relevant details in JSON format."
        )
        prompts.append(prompt)
    return prompts

# Function to check if the friend's birthday is approaching
def is_birthday_approaching(birthday_str, days_threshold=30):
    try:
        birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
        today = datetime.now()
        days_until_birthday = (birthday - today).days
        return 0 <= days_until_birthday <= days_threshold
    except ValueError:
        print(f"Invalid birthday format: {birthday_str}. Expected format: YYYY-MM-DD")
        return False

# Function to find product details by name
def get_product_details(products, product_names):
    product_details = {
        product["name"]: {
            "category": product.get("Category"),
            "sub_category": product.get("sub_category"),
            "image": product.get("image"),
            "link": product.get("link"),
            "ratings": product.get("ratings"),
            "discount_price": product.get("discount_price"),
            "actual_price": product.get("actual_price")
        }
        for product in products if product["name"] in product_names
    }
    return product_details

# Function to parse recommendations from the OpenAI response
def parse_recommendations(response_text):
    try:
        # Attempt to parse JSON response
        recommendations = json.loads(response_text)
        return recommendations
    except json.JSONDecodeError:
        print("Failed to parse recommendations as JSON.")
        return []

@app.route("/test")
def test():
    return render_template("index.html", title="Hello")

# @app.route("/")
# def hello_world():
#     categories_data = load_categories(file_path)

#     if categories_data:
#         # Sample data for the friend
#         friend_data = {
#             "name": "Alice",
#             "phone_number": "+1234567890",
#             "birthday": "2024-09-05",
#             "cart": [
#                 "Bangalore Refinery 999 Purity Silver Bar 1 Kg",
#                 "Fashion Frill Men's Jewellery 3D Cuboid Vertical Bar/Stick Stainless Steel Black Silver Locket Pendant Necklace Chain For ...",
#                 "Premium Leather Wallet for Men",
#                 "Fastrack Reflex Play|1.3” AMOLED Display Smart Watch with AOD|Premium Metallic Body|Animated Watchfaces|in-Built Games|BP...",
#                 "Fossil Gen 5E Smartwatch with AMOLED Screen, Wear OS by Google, Built-in Speaker for Phone Calls, Google Assistant, SpO2, ..."
#             ]
#         }

#         if is_birthday_approaching(friend_data["birthday"]):
#             # Get all products from the categories data
#             products = get_all_products(categories_data)

#             # Filter products in the cart that exist in the JSON data
#             cart_products = [product for product in products if product["name"] in friend_data["cart"]]

#             if not cart_products:
#                 return "No matching products from the cart found in the JSON data."
#             else:
#                 # Create prompts for each product in the cart
#                 prompts = create_prompts(friend_data["name"], friend_data["birthday"], cart_products)

#                 recommendations = []
#                 for prompt in prompts:
#                     try:
#                         # Generate recommendations using GPT-3.5-turbo
#                         response = openai.ChatCompletion.create(
#                             model="gpt-3.5-turbo",
#                             messages=[
#                                 {"role": "system", "content": "You are a helpful assistant."},
#                                 {"role": "user", "content": prompt}
#                             ],
#                             max_tokens=1000  # Increased token limit for detailed responses
#                         )

#                         # Append the response
#                         recommendations.append(response.choices[0].message['content'].strip())

#                     except openai.error.InvalidRequestError as e:
#                         print(f"Invalid Request Error: {e}")
#                     except openai.error.OpenAIError as e:
#                         print(f"OpenAI Error: {e}")

#                 # Combine the recommendations into a full output
#                 full_recommendations = "\n\n".join(recommendations)
#                 print("Full Recommendations:\n", full_recommendations)

#                 # Parse recommendations as JSON
#                 recommended_products = parse_recommendations(full_recommendations)

#                 if recommended_products:
#                     # Extract recommended product names from the parsed recommendations
#                     recommended_product_names = [
#                         product["name"] for product in recommended_products
#                     ]

#                     # Get detailed information for the recommended products
#                     recommended_product_details = get_product_details(products, recommended_product_names)

#                     # Prepare and print the output in JSON format including prices
#                     output = {
#                         "Recommended_Products": [
#                             {
#                                 "name": details["name"],
#                                 "category": details.get("category"),
#                                 "sub_category": details.get("sub_category"),
#                                 "image": details.get("image"),
#                                 "link": details.get("link"),
#                                 "ratings": details.get("ratings"),
#                                 "discount_price": details.get("discount_price"),
#                                 "actual_price": details.get("actual_price")
#                             }
#                             for details in recommended_product_details.values()
#                         ]
#                     }
#                     return jsonify(output)  # Return recommendations as JSON response
#                 else:
#                     return "No valid recommendations found."
#         else:
#             return "Friend's birthday is not approaching soon."
#     else:
#         return "Failed to load categories data."


# def load_and_process_contacts():
#     with open('contact.json', 'r') as file:
#         data = json.load(file)

#     # Convert JSON data to DataFrame
#     df = pd.DataFrame(data)

#     # Create a lookup dictionary for contact to date of birth
#     dob_lookup = df.set_index('contact')['dateofbirth'].to_dict()

#     # Function to map friend's contact to their date of birth
#     def map_friends_to_dob(friends):
#         for friend in friends:
#             friend['dateofbirth'] = dob_lookup.get(friend['contact'], None)
#         return friends

#     # Apply the function to the 'friendslist' column
#     df['friends_with_dob'] = df['friendslist'].apply(map_friends_to_dob)

#     # Display the resulting DataFrame as JSON
#     result = df[['contact','name', 'dateofbirth','friends_with_dob']]

#     print(result)
#     result.to_csv('contacts_with_friends_dob.csv', index=False)
#     return result

# def load_and_process_contacts():
#     with open('contact.json', 'r') as file:
#         data = json.load(file)

#     # Convert JSON data to DataFrame
#     df = pd.DataFrame(data)

#     # Create a lookup dictionary for contact to date of birth
#     dob_lookup = df.set_index('contact')['dateofbirth'].to_dict()

#     # Function to map friend's contact to their date of birth
#     def map_friends_to_dob(friends):
#         for friend in friends:
#             friend['dateofbirth'] = dob_lookup.get(friend['contact'], None)
#         return friends

#     # Apply the function to the 'friendslist' column
#     df['friends_with_dob'] = df['friendslist'].apply(map_friends_to_dob)

#     # Function to check if a birthday is within the next 5 days
#     def is_birthday_soon(dob):
#         if dob:
#             birthday_this_year = datetime.strptime(dob, '%d-%m-%Y').replace(year=datetime.now().year)
#             today = datetime.now()
#             days_difference = (birthday_this_year - today).days
#             return 0 <= days_difference <= 5
#         return False

#     # Function to check if any friend in the list has a birthday soon
#     def check_friends_birthday(friends):
#         return [friend for friend in friends if is_birthday_soon(friend['dateofbirth'])]

#     # Apply the function to create a new column
#     df['birthday_soon_friends'] = df['friends_with_dob'].apply(check_friends_birthday)

#     # Display the resulting DataFrame as JSON
#     result = df[['contact', 'name', 'dateofbirth', 'friends_with_dob', 'birthday_soon_friends']]
    
#     print(result)
#     # result.to_csv('contacts_with_birthday_soon_friends.csv', index=False)
#     return result

def load_and_process_contacts():
    # Load contact data
    with open('contact.json', 'r') as file:
        contact_data = json.load(file)

    # Convert JSON data to DataFrame
    df = pd.DataFrame(contact_data)

    # Create a lookup dictionary for contact to date of birth
    dob_lookup = df.set_index('contact')['dateofbirth'].to_dict()

    # Function to map friend's contact to their date of birth
    def map_friends_to_dob(friends):
        for friend in friends:
            friend['dateofbirth'] = dob_lookup.get(friend['contact'], None)
        return friends

    # Apply the function to the 'friendslist' column
    df['friends_with_dob'] = df['friendslist'].apply(map_friends_to_dob)

    # Function to check if a birthday is within the next 5 days
    def is_birthday_soon(dob):
        if dob:
            birthday_this_year = datetime.strptime(dob, '%d-%m-%Y').replace(year=datetime.now().year)
            today = datetime.now()
            days_difference = (birthday_this_year - today).days
            return 0 <= days_difference <= 5
        return False

    # Function to check if any friend in the list has a birthday soon
    def check_friends_birthday(friends):
        return [friend for friend in friends if is_birthday_soon(friend['dateofbirth'])]

    # Apply the function to create a new column
    df['birthday_soon_friends'] = df['friends_with_dob'].apply(check_friends_birthday)

    # Load user cart data
    with open('usercart.json', 'r') as file:
        user_cart_data = json.load(file)

    # Create a dictionary for easy lookup of cart items by phone number
    user_cart_lookup = {item['phone']: item['cart'] for item in user_cart_data}

    # Function to map cart data to friends with upcoming birthdays
    def map_cart_to_birthday_friends(friends):
        for friend in friends:
            if friend['dateofbirth']:
                phone = friend['contact']
                # Get cart items for the friend's phone number
                cart_items = user_cart_lookup.get(phone, [])
                friend['cart_items'] = cart_items
        return friends

    # Apply the function to create a new column with cart data
    df['friends_with_cart'] = df['birthday_soon_friends'].apply(map_cart_to_birthday_friends)

    # Display the resulting DataFrame as JSON
    result = df[['contact', 'name', 'dateofbirth', 'friends_with_dob', 'birthday_soon_friends', 'friends_with_cart']]

    print(result)
    result.to_csv('contacts_with_friends_cart.csv', index=False)
    return result
@app.route("/", methods=['POST'])
def hello_world():
    categories_data = load_categories(file_path)

    if categories_data:
        # data = request.get_json()

        contacts_df = load_and_process_contacts() 
        print(contacts_df)
        # Sample data for the friend
        # for friend in contacts_df['birthday_soon_friends']:
        #     if friend[0]['contact'] == friend_data['contact']:
        #         friend_data['name'] = friend['name']
        #         friend_data['birthday'] = friend['dateofbirth']
                
        #         # Extract cart items
        #         cart_items = friend['cart_items']
        #         updated_cart = []
                
        #         for item in cart_items:
        #             for product in item['data']:
        #                 updated_cart.append(product['name'])
                
        #         friend_data['cart'] = updated_cart

        # # Print the updated friend_data
        #     print(friend_data)
        
        friend_data = {
            "name": "Alice",
            "phone_number": "+1234567890",
            "birthday": "2024-09-05",
            "cart": [
                "Bangalore Refinery 999 Purity Silver Bar 1 Kg",
                "Fashion Frill Men's Jewellery 3D Cuboid Vertical Bar/Stick Stainless Steel Black Silver Locket Pendant Necklace Chain For ...",
                "Premium Leather Wallet for Men",
                "Fastrack Reflex Play|1.3” AMOLED Display Smart Watch with AOD|Premium Metallic Body|Animated Watchfaces|in-Built Games|BP...",
                "Fossil Gen 5E Smartwatch with AMOLED Screen, Wear OS by Google, Built-in Speaker for Phone Calls, Google Assistant, SpO2, ..."
            ]
        }

        if is_birthday_approaching(friend_data["birthday"]):
            # Get all products from the categories data
            products = get_all_products(categories_data)

            # Filter products in the cart that exist in the JSON data
            cart_products = [product for product in products if product["name"] in friend_data["cart"]]

            if not cart_products:
                return "No matching products from the cart found in the JSON data."
            else:
                # Create prompts for each product in the cart
                prompts = create_prompts(friend_data["name"], friend_data["birthday"], cart_products)

                recommendations = []
                for prompt in prompts:
                    try:
                        # Generate recommendations using GPT-3.5-turbo
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=1000  # Increased token limit for detailed responses
                        )

                        # Append the full response content as a JSON object
                        rec_content = response.choices[0].message['content'].strip()
                        rec_json = json.loads(rec_content)
                        recommendations.append(rec_json)

                    except json.JSONDecodeError:
                        print("Failed to parse recommendation as JSON.")
                    except openai.error.InvalidRequestError as e:
                        print(f"Invalid Request Error: {e}")
                    except openai.error.OpenAIError as e:
                        print(f"OpenAI Error: {e}")

                # Combine the recommendations into a full output
                full_recommendations = {
                    "similar_products": [],
                    "complementary_items": []
                }

                for rec in recommendations:
                    if 'similar_products' in rec:
                        full_recommendations["similar_products"].extend(rec['similar_products'])
                    if 'complementary_items' in rec:
                        full_recommendations["complementary_items"].extend(rec['complementary_items'])
                
                return jsonify({"Full_Recommendations": full_recommendations})  # Return full recommendations as JSON response
        else:
            return "Friend's birthday is not approaching soon."
    else:
        return "Failed to load categories data."
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

