import type { OpeningHour } from "../data/salon";

// Opening hours are local to the salon, so "now" is always read in
// Amsterdam time — whatever timezone the visitor's device is in.
const SALON_TIMEZONE = "Europe/Amsterdam";

interface SalonNow {
    day: string;      // e.g. "Tuesday"
    minutes: number;  // minutes since midnight
}

function salonNow(date = new Date()): SalonNow {
    const parts = new Intl.DateTimeFormat("en-GB", {
        timeZone: SALON_TIMEZONE,
        weekday: "long",
        hour: "2-digit",
        minute: "2-digit",
        hourCycle: "h23",
    }).formatToParts(date);

    const get = (type: string) => parts.find((part) => part.type === type)?.value ?? "";

    return {
        day: get("weekday"),
        minutes: Number(get("hour")) * 60 + Number(get("minute")),
    };
}

function toMinutes(time: string): number {
    const [hours, minutes] = time.split(":").map(Number);
    return hours * 60 + minutes;
}

export function todayName(): string {
    return salonNow().day;
}

export interface OpenStatus {
    isOpen: boolean;
    label: string; // short human sentence, e.g. "Open now · until 18:00"
}

export function openStatus(hours: OpeningHour[]): OpenStatus {
    const now = salonNow();
    const todayIndex = hours.findIndex((hour) => hour.day === now.day);
    const today = hours[todayIndex];

    if (today?.open && today.close) {
        if (now.minutes < toMinutes(today.open)) {
            return { isOpen: false, label: `Closed · opens today at ${today.open}` };
        }
        if (now.minutes < toMinutes(today.close)) {
            return { isOpen: true, label: `Open now · until ${today.close}` };
        }
    }

    // Find the next day the salon opens.
    for (let offset = 1; offset <= hours.length; offset++) {
        const next = hours[(todayIndex + offset) % hours.length];
        if (next.open) {
            const when = offset === 1 ? "tomorrow" : next.day;
            return { isOpen: false, label: `Closed · opens ${when} at ${next.open}` };
        }
    }

    return { isOpen: false, label: "Closed" };
}
