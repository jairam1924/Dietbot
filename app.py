from tkinter import *
import pandas as pd
from difflib import get_close_matches
import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import pyttsx3

# Load the data from the Excel file
file_path = r'data/Bot_data.xlsx'  # Ensure the file is in the correct directory
diet_data = pd.read_excel(file_path)


# language_var = tk.StringVar()
# language_var.set('English') 

# Convert the data to a dictionary for easy lookup
diet_recommendations = {}
for index, row in diet_data.iterrows():
    condition = row['Health Condition'].strip().lower()
    recommended_food = row['Recommended FoodandDrink']
    alternatives = row['Alternatives']

    diet_recommendations[condition] = {
        "Recommended Food/Drink": [food.strip() for food in recommended_food.split(',')] if pd.notna(recommended_food) else [],
        "Benefits": row['Benefits'],
        "Alternatives": [alt.strip() for alt in alternatives.split('; ')] if pd.notna(alternatives) else []
    }

def find_closest_match(user_input, conditions):
    user_input = user_input.lower().strip()

    # Direct match first
    if user_input in conditions:
        return user_input

    # Check for closest matches based on the entire input
    closest = get_close_matches(user_input, conditions, n=1, cutoff=0.4)
    if closest:
        return closest[0]

    # Check each word in the input for closest matches
    user_input_words = user_input.split()
    matches = []
    for word in user_input_words:
        closest = get_close_matches(word, conditions, n=1, cutoff=0.4)
        if closest and closest[0] not in matches:
            matches.append(closest[0])

    # Return the most relevant match
    if matches:
        return matches[0]

    return None

def show_recommendation(input_entry, result_text):
    user_input = input_entry.get().strip().lower()
    conditions = list(diet_recommendations.keys())
    closest_match = find_closest_match(user_input, conditions)

    result_text.delete("1.0", tk.END)

    if closest_match:
        recommendation = diet_recommendations[closest_match]
        result_text.insert(tk.END, f"Recommended Food 🥙 and 🥛 Drinks to be consumed During {closest_match.capitalize()}:\n")
        for food in recommendation["Recommended Food/Drink"]:
            result_text.insert(tk.END, f"- {food}\n")
        result_text.insert(tk.END, f"\n Benefits  :\n\n- {recommendation['Benefits']}\n")
        result_text.insert(tk.END, "\n  Alternatives  :\n\n")
        for food in recommendation["Alternatives"]:
            result_text.insert(tk.END, f"- {food}\n")
    else:
        result_text.insert(tk.END, "Sorry, I don't have information on that health issue. Please try another one.")

    input_entry.delete(0, tk.END)

def speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Silence please")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Speak now please...")
        audio = recognizer.listen(source)

    try:
        # Recognize speech using Google Web Speech API
        user_input = recognizer.recognize_google(audio)
        user_input = user_input.lower()
        print(f"Did you say: {user_input}")

        # Update the entry widget with the recognized text
        input_entry.delete(0, tk.END)
        input_entry.insert(0, user_input)

        # Show recommendation based on the recognized speech
        show_recommendation(input_entry, result_text)

    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        result_text.insert(tk.END, "Sorry, could not understand the audio. Please try again.")
    except sr.RequestError:
        print("Sorry, there was an issue with the speech recognition service.")
        result_text.insert(tk.END, "Sorry, there was an issue with the speech recognition service. Please try again.")

def speak_aloud():
    engine = pyttsx3.init()
    text = result_text.get("1.0", tk.END).strip()
    if text:
        engine.say(text)
        engine.runAndWait()

def diet_bot():
    global input_entry, result_text

    root = tk.Tk()
    root.title("DietBot 🤖")

    # root.configure(bg='')
    # Create the main frame
    # canvas = tk.Canvas(root, bg='lightcoral')
    # canvas.pack(fill=tk.BOTH, expand=True)
    main_frame = tk.Canvas(root,bg='light green')
    main_frame.pack(fill=tk.BOTH, expand=True)

    mike_button_image = PhotoImage(file='icons/mike.png')
    sound_button_image = PhotoImage(file='icons/sound.png')

    # Create the title label
    title_label = ttk.Label(main_frame, text="Welcome to DietBot!", font=("Arial", 16, "bold"),background="light green")
    title_label.pack(pady=10)

    # Create the input entry and label
    input_label = ttk.Label(main_frame, text="Enter your health issue:",background="light green",font=("Arial",14,"italic"))
    input_label.pack(pady=5)

    place_holder = Frame(main_frame,bg='light green')
    place_holder.pack(pady=5)

    input_entry = ttk.Entry(place_holder, width=30)
    input_entry.grid(row=0, column=0, padx=5)

    mike_button = Button(place_holder, image=mike_button_image, borderwidth=4, command=speech)
    mike_button.grid(row=0, column=1, padx=5)

    # Bind the "Enter" key press event to the show_recommendation function
    def on_enter(event):
        show_recommendation(input_entry, result_text)

    input_entry.bind("<Return>", on_enter)

    place_holder2 = Frame(main_frame,bg='light green')
    place_holder2.pack(pady=5)

    sound_button = Button(place_holder2, image=sound_button_image, borderwidth=4, command=speak_aloud)
    sound_button.grid(row=0, column=1, padx=5)

    languages = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Hindi': 'hi',
    'telugu': 'te',
    'tamil': 'ta',
    'Chinese': 'zh-cn'}

    language_var = tk.StringVar()
    language_var.set('English') 
    languages = OptionMenu(place_holder2,language_var,*languages.keys())
    languages.grid(row=2, column=0, pady=10)  # Adjust the row, column, or padding as needed

    # Create the result text area
    result_text = tk.Text(place_holder2, height=20, width=50, wrap=tk.WORD)
    result_text.grid(row=0, column=0, padx=5)

    # Create the quit button
    quit_button = ttk.Button(main_frame, text="Quit", command=root.destroy)
    quit_button.pack(pady=10)

    root.mainloop()

# Run the chatbot
diet_bot()
