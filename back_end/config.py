#DEFIND THE SALON FIX RULES

from zoneinfo import ZoneInfo

# The salon's own timezone. All slot maths happens in UTC,
# but opening hours are expressed in local time.
SALON_TIMEZONE = ZoneInfo("Europe/Amsterdam")

#Booking Grid
SLOT_MINUTES = 15

# Opening hours in local time. Key is weekday: 0 = Monday ... 6 = Sunday.
# None means closed that day.
BUSINESS_HOURS = {
    0: ("10:00", "18:00"),
    1: ("10:00", "18:00"),
    2: ("10:00", "18:00"),
    3: ("10:00", "18:00"),
    4: ("10:00", "18:00"),
    5: ("10:00", "18:00"),
    6: None,
}

#Customer must book this far ahead
MIN_BOOKING_NOTICE_HOURS = 2

#Customer must cancle the appointment this far ahead
MIN_CANCLE_NOTICE_HOURS = 12

#Statuses that actually occupy a slot
ACTIVE_STATUSES = ("confirmed", "rescheduled")

#Price list categories, in the order the website shows them.
#Keep in sync with CATEGORIES in front_end/src/data/services.ts
SERVICE_CATEGORIES = (
    "Manicure & Pedicure",
    "Acrylic & Extensions",
    "BIAB & Gel",
    "Extras",
)
