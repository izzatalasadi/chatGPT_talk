import time
import speech_recognition as sr
import pyttsx3
import openai
from playsound import playsound


# import selenium libs
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# Initialize language and TTS engine
language = "en-US"
engine = pyttsx3.init()

# Initialize OpenAI API
openai.api_key = ""


# Define functions
def chat(question):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            temperature=0.5,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.6,
            stop=["You:"]
        )
        return response.choices[0].text
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")


def play_tone():
    playsound("beep.mp3")


def voice_text(language):
    r = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            play_tone()
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language=language)
                break
            except sr.UnknownValueError:
                text_voice(
                    "I'm sorry, I couldn't understand what you said.", language)
            except sr.RequestError as e:
                text_voice(
                    f"Could not request results from Google Speech Recognition service in {language}; {e}", language)
    return text


def selenium_translate(text, language):

    s = Service(ChromeDriverManager().install())
    # Connecting with translate.google.com 
    url = 'https://translate.google.com/'

    # launch browser with selenium:=>
    # browser = webdriver.Chrome('path of chromedriver.exe file') if the chromedriver.exe is in different folder
    browser = webdriver.ChromeOptions()
    browser.add_argument('--headless')

    driver = webdriver.Chrome(service=s, options=browser)

    driver.get(url)
    driver.add_cookie({"name": "CONSENT", "value": "YES+NO.en+V9+BX+149"})

    # copy google Translator link here:=>
    driver.get("https://translate.google.co.in/?sl=auto&tl=" +
               language+"&text="+text+"&op=translate")

    driver.implicitly_wait(3)

    # just wait for some time for translating input text:=>
    # time.sleep(1)

    # Fill text area with the stored tweet feeds
    if driver.find_elements(By.TAG_NAME, 'button')[1]:
        driver.find_elements(By.TAG_NAME, 'button')[1].click()

    translated_text = driver.find_element(
        By.XPATH, "//span[@class='ryNqvb']").text
    driver.close()

    return translated_text


def text_voice(text, language):
    engine.setProperty('rate', 175)
    engine.setProperty('voice', language)

    voices = engine.getProperty('voices')
    for voice in voices:
        if language in voice.name:
            engine.setProperty('voice', voice.id)

    if "en" not in language:
        translated_text = selenium_translate(text, language)
        engine.say(translated_text)
    else:
        engine.say(text)
    # Use TTS engine to speak the translated text
    engine.runAndWait()

# Define main function


def change_language(language="en-EN"):
    # Start conversation loop
    while True:

        # Get the user's language choice
        language_choice = voice_text('en-US').lower()
        if 'english' in language_choice:
            language = 'en'
            text_voice("You have selected English.", language)
            break
        elif 'french' in language_choice:
            language = 'fr'
            text_voice("Vous avez sélectionné français.", language)
            break
        elif 'german' in language_choice:
            language = 'de'
            text_voice("Sie haben Deutsch ausgewählt.", language)
            break
        elif 'italian' in language_choice:
            language = 'it'
            text_voice("Hai selezionato l'italiano.", language)
            break

        elif 'Norwegian' in language_choice:
            language = 'no'
            text_voice("Hei, du har valgte norsk.", language)
            break

        elif 'portuguese' in language_choice:
            language = 'pt'
            text_voice("Você selecionou português.", language)
            break
        elif 'spanish' in language_choice:
            language = 'es'
            text_voice("Has seleccionado español.", language)
            break
        else:
            text_voice(
                "Sorry, I didn't understand your language selection. Please try again.", language)

    return language


def main():
   # Set default language to English
    language = 'en-EN'
    # Greet the user and prompt for language selection
    text_voice("Hello, Please select a language by saying its name.", language)
    text_voice(
        "Available languages are English, French, German, Italian, Portuguese, Norwegian and Spanish.", language)
    text_voice("Please speak after the beep.", language)

    language = change_language()

    text_voice("So, how can I assist you today?", language)
    text_voice("Please speak after the beep.", language)

    # Start conversation loop
    while True:
        user_input = voice_text(language).lower()
        # end conversation *need more languages*
        if "goodbye" in user_input or "bye" in user_input:
            text_voice("Goodbye! Have a great day.", language)
            break
        elif "change" and "language" in user_input:
            language = change_language()
        else:
            answer = chat(user_input)
            text_voice(answer, language)


# Run main function
if __name__ == '__main__':
    main()
