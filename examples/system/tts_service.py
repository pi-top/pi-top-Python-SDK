from pitop.processing import tts

config = {
    "language": "us",
}

tts = tts.services.get(service_id="FESTIVAL", **config)

tts.say("This is the festival tts service")
