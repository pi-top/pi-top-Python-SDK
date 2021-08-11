from pitop import Pitop

pitop = Pitop()

pitop.speak.print_voices()

voices = pitop.speak.available_voices

for language, voices in voices.items():
    for voice in voices:
        pitop.speak.set_voice(language, voice)
        print(f"LANGUAGE: {language} | VOICE: {voice}", flush=True)
        pitop.speak("Hello")

while True:
    text = input("Enter text: ")
    pitop.speak(text)
