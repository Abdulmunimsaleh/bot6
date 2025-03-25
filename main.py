from fastapi import FastAPI, Query
import google.generativeai as genai
from playwright.sync_api import sync_playwright
import json

# Set your Gemini API key
genai.configure(api_key="AIzaSyCpugWq859UTT5vaOe01EuONzFweYT2uUY")

app = FastAPI()

# Function to scrape the website and extract content
def scrape_website(url="https://tripzoori-gittest1.fly.dev/"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # Wait for the page to load completely
        page.wait_for_selector("body")
        
        # Extract all visible text from the page
        page_content = page.inner_text("body")
        
        # Store scraped data in a JSON file
        with open("website_data.json", "w", encoding="utf-8") as f:
            json.dump({"content": page_content}, f, indent=4)
        
        browser.close()
        return page_content

# Function to load scraped data
def load_data():
    try:
        with open("website_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("content", "")
    except FileNotFoundError:
        return scrape_website()

# Function to ask questions using Gemini
def ask_question(question: str):
    data = load_data()
    
    prompt = f"""
    You are an AI assistant that answers questions based on the website content.
    Website Data: {data}
    Question: {question}
    Answer:
    """
    
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    
    return response.text.strip()

@app.get("/ask")
def get_answer(question: str = Query(..., title="Question", description="Ask a question about the website")):
    answer = ask_question(question)
    return {"question": question, "answer": answer}

