import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("Listing available voices:")
for index, voice in enumerate(voices):
    print(f"ID: {index}")
    print(f"Name: {voice.name}")
    print(f"Languages: {voice.languages}")
    print(f"Gender: {voice.gender}")
    print("-" * 20)
    
    # Optional: Test each voice (this might be annoying if there are many)
    # engine.setProperty('voice', voice.id)
    # engine.say(f"Hi, I am {voice.name}. Do you like my voice?")
    # engine.runAndWait()
