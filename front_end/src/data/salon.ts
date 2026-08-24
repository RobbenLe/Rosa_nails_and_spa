export interface OpeningHour{
    day: string;
    open: string | null;
    close: string | null;
}

export interface Salon {
    name: string;
    tagline: string;
    phone: string;
    address: string;
    whatsapp: string;
    city: string;
    about: string[];
    hours: OpeningHour[];
}

// PLACEHOLDER CONTENT — invented, realistic stand-in data.
// Swap this one file for the salon's real details later; nothing else changes.
export const salon: Salon = {
    name: 'Rosa Nails & Spa',
    tagline: 'Boutique nail care in the heart of Amsterdam — Manicures, Pedicure, Gel, Biab, Acrylic and Nail Art by appointment.',
    phone: '+31 6 33 42 67 98',
    whatsapp: '+31 6 33 42 67 98',
    address: 'Hofwickstraat 2',
    city: '1055 GE Amsterdam',
    about: [
        "Welcome to Rosa Nails & Spa, our cozy family‑run studio in Amsterdam West. Established in 2023, we’ve been growing ever since thanks to Rosa’s 10 years of experience and her passion for creating beautiful, healthy nails.",
        "We treat every client like a friend and family member, so feel free to stop by, relax, and get your nails done. You’re always welcome."
    ],
    hours: [
    { day: 'Monday',    open: '10:00', close: '18:00' },
    { day: 'Tuesday',   open: '10:00', close: '18:00' },
    { day: 'Wednesday', open: '10:00', close: '18:00' },
    { day: 'Thursday',  open: '10:00', close: '18:00' },
    { day: 'Friday',    open: '10:00', close: '18:00' },
    { day: 'Saturday',  open: '10:00', close: '18:00' },
    { day: 'Sunday',    open: null, close: null },
    ],
};