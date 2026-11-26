"""The fixed sentences the bot says word for word (approved by the owner).

PROBLEM THIS FILE SOLVES
When a question is outside what the bot may answer, or a customer wants an appointment,
the model must not improvise. The texts below are shown exactly as written, in ONE language,
and the model never writes them (so a quote character in them can never break the model's answer format).

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

# (a) Appointment requests. The bot does not know Rosa's schedule, so it never says a time is free.
# Shown when the customer has given service, time and name, and also when the model's own reply
# sounded like a time slot is free or booked.
BOOKING_REPLIES = {
    "en": 'Rosa manages all appointments personally. Tap "Book via WhatsApp" and send her a message, '
          "and she'll check her schedule and find a time that suits you.",
    "nl": 'Rosa plant alle afspraken zelf in. Tik op "Boek via WhatsApp" en stuur haar een bericht, '
          "dan kijkt ze in haar agenda en zoekt ze een tijd die jou uitkomt.",
}
