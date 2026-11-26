"""The fixed sentences the bot says word for word (approved by the owner).

PROBLEM THIS FILE SOLVES
When a question is outside what the bot may answer, the model must not improvise.
The text below is shown exactly as written, in ONE language, never edited by the model.

Two kinds of WhatsApp button go with these texts (the website chooses the button label):
  "ask"  -> "Ask on WhatsApp" / "Vraag via WhatsApp"   (a question for Rosa)
  "book" -> "Book via WhatsApp" / "Boek via WhatsApp"  (an appointment request)
"""

BUTTON_ASK = "ask"
BUTTON_BOOK = "book"

# (b) Everything outside prices, services, opening hours, address, FAQ and booking:
# health, personal requests such as the choice of technician, strange questions, personal details, errors.
ASK_ROSA_REPLIES = {
    "en": 'Rosa can help you with that personally. Tap "Ask on WhatsApp" and send her a message, '
          "and she'll reply as soon as she can.",
    "nl": 'Daar helpt Rosa je graag persoonlijk mee. Tik op "Vraag via WhatsApp" en stuur haar een bericht, '
          "dan antwoordt ze zo snel mogelijk.",
}

# Used when the model's reply sounded like a time slot is free or booked.
SCHEDULE_REPLIES = {
    "en": 'Tap "Book via WhatsApp" and send the message. Rosa will check her schedule and reply to confirm.',
    "nl": 'Tik op "Boek via WhatsApp" en verstuur het bericht. Rosa kijkt in haar agenda en laat je weten of het lukt.',
}
