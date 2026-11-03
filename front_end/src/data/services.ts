import type { ServiceRow } from "../api";

export const CATEGORIES = [
    "Manicure & Pedicure",
    "Acrylic & Extensions",
    "BIAB & Gel",
    "Extras",
] as const;

export type Category = (typeof CATEGORIES)[number];

export interface PriceOption {
    label?: string; // omitted when there's just one plain price
    price: number;
}

export interface Service {
    id: string;
    name: string;
    category: Category;
    description: string;
    suitable: string;
    durationMinutes: number;
    durationMaxMinutes?: number; // set when options take different times, e.g. new set vs filling
    prices: PriceOption[];
}

/**
 * The database stores one row per option ("Natural – new set", "Natural – filling").
 * The price list shows them as one service with several prices, so group rows
 * that share a category and name.
 */
export function groupServiceRows(rows: ServiceRow[]): Service[] {
    const groups = new Map<string, Service>();

    for (const row of rows) {
        const key = `${row.category}|${row.name}`;
        const price: PriceOption = {
            label: row.variant || undefined,
            price: row.price_cents / 100,
        };
        const existing = groups.get(key);

        if (existing) {
            existing.prices.push(price);
            existing.durationMinutes = Math.min(existing.durationMinutes, row.duration_minutes);
            existing.durationMaxMinutes = Math.max(
                existing.durationMaxMinutes ?? row.duration_minutes,
                row.duration_minutes
            );
            continue;
        }

        groups.set(key, {
            id: String(row.id),
            name: row.name,
            category: row.category as Category,
            description: row.description,
            suitable: row.suitable,
            durationMinutes: row.duration_minutes,
            durationMaxMinutes: row.duration_minutes,
            prices: [price],
        });
    }

    return [...groups.values()];
}

// Shown until the live price list arrives from the server, and if the server
// can't be reached. The real prices are managed on the /admin page.
export const services: Service[] = [
    // ---------- Manicure & Pedicure ----------
    {
        id: "classic-manicure",
        name: "Classic Manicure",
        category: "Manicure & Pedicure",
        description: "Shaping, cuticle care and buff.",
        suitable: "Perfect for clients who want healthy, well-groomed nails with a natural, elegant finish.",
        durationMinutes: 40,
        prices: [{ price: 20 }],
    },
    {
        id: "gel-manicure",
        name: "Gel Manicure",
        category: "Manicure & Pedicure",
        description: "Gel colour applied to natural nails, cured for a hard, glossy finish.",
        suitable: "Perfect for clients who want a quick colour refresh with no extra length or structure.",
        durationMinutes: 60,
        prices: [{ price: 25 }],
    },
    {
        id: "classic-pedicure",
        name: "Classic Pedicure",
        category: "Manicure & Pedicure",
        description: "Soak, exfoliation, nail and cuticle care, finished with polish.",
        suitable: "Perfect for clients on their feet all day, or getting ready for soft feet.",
        durationMinutes: 40,
        prices: [{ price: 40 }],
    },
    {
        id: "gel-pedicure",
        name: "Gel Pedicure",
        category: "Manicure & Pedicure",
        description: "Full pedicure finished with gel colour for a lasting result.",
        suitable: "Perfect for holidays and events, when you need colour that lasts the whole trip.",
        durationMinutes: 60,
        prices: [{ price: 55 }],
    },

    // ---------- Acrylic & Extensions ----------
    {
        id: "Acrylic-natural",
        name: "Natural",
        category: "Acrylic & Extensions",
        description: "A clear acrylic overlay or extension, shaped and buffed to a natural finish.",
        suitable: "Perfect for clients who want strength and length that still looks like their own nails.",
        durationMinutes: 90,
        prices: [
            { label: "new set", price: 50 },
            { label: "filling", price: 40 },
        ],
    },
    {
        id: "Acrylic-natural-gel",
        name: "Natural with gel polish",
        category: "Acrylic & Extensions",
        description: "A natural acrylic set finished with gel colour of your choice.",
        suitable: "Perfect for clients who want the durability of acrylic with colour that lasts just as long.",
        durationMinutes: 105,
        prices: [
            { label: "new set", price: 60 },
            { label: "filling", price: 50 },
        ],
    },
    {
        id: "Acrylic-nude",
        name: "Nude",
        category: "Acrylic & Extensions",
        description: "A full set built in soft nude-toned acrylic, needing no polish on top.",
        suitable: "Perfect for clients who want a clean, understated look that suits any occasion.",
        durationMinutes: 90,
        prices: [
            { label: "new set", price: 50 },
            { label: "filling", price: 40 },
        ],
    },
    {
        id: "Acrylic-colour-powder",
        name: "Color powder",
        category: "Acrylic & Extensions",
        description: "A full set built in coloured acrylic powder, so the colour runs through the nail itself.",
        suitable: "Perfect for clients who want bold colour that never chips or grows out unevenly.",
        durationMinutes: 90,
        prices: [
            { label: "new set", price: 55 },
            { label: "filling", price: 45 },
        ],
    },
    {
        id: "Acrylic-baby-boom",
        name: "Baby boom",
        category: "Acrylic & Extensions",
        description: "A blended pink-to-white gradient built into the acrylic, with no hard line.",
        suitable: "Perfect for clients who want a softer, more modern take on the classic French.",
        durationMinutes: 105,
        prices: [
            { label: "new set", price: 65 },
            { label: "filling", price: 50 },
        ],
    },
    {
        id: "Acrylic-pink-white",
        name: "Pink & White",
        category: "Acrylic & Extensions",
        description: "The classic French: a pink nail bed with a crisp white tip, sculpted by hand.",
        suitable: "Perfect for clients who want a timeless, polished look that never dates.",
        durationMinutes: 105,
        prices: [
            { label: "new set", price: 65 },
            { label: "filling", price: 55 },
        ],
    },

    // ---------- BIAB & Gel ----------
    {
        id: "Biab",
        name: "BIAB (Builder Gel)",
        category: "BIAB & Gel",
        description: "A premium strengthening gel that protects the natural nail, promotes healthy growth, and leaves a smooth, durable finish.",
        suitable: "Perfect for clients who want beautiful, long-wear nails without added thickness.",
        durationMinutes: 75,
        prices: [
            { label: "Biab Colour", price: 50 },
            { label: "Biab Combination Gellak", price: 55}
        ],
    },
    {
        id: "gel-polish-removal",
        name: "Gel Polish Removal",
        category: "BIAB & Gel",
        description: "Gentle soak-off of existing gel polish, with the natural nail cleaned and buffed.",
        suitable: "Perfect for clients giving their nails a break, or coming in from another salon.",
        durationMinutes: 20,
        prices: [{ price: 10 }],
    },

    // ---------- Extras ----------
    {
        id: "nail-art",
        name: "Nail Art",
        category: "Extras",
        description: "Hand-painted detail, chrome, or stones. Priced per nail.",
        suitable: "Perfect for clients who want something personal, from a single accent nail to a full set.",
        durationMinutes: 10,
        prices: [{ label: "from", price: 5 }],
    },
    {
        id: "nail-repair",
        name: "Nail Repair",
        category: "Extras",
        description: "Repair of a single broken or lifted nail, reshaped to match the rest.",
        suitable: "Perfect when one nail goes wrong and you would rather not redo the whole set.",
        durationMinutes: 15,
        prices: [{ label: "from", price: 5 }],
    },
    {
        id: "removal",
        name: "Acrylic & Gel Removal",
        category: "Extras",
        description: "Safe soak-off of existing acrylic, gel or BIAB, leaving the natural nail clean and undamaged.",
        suitable: "Perfect for clients returning to natural nails, or starting fresh with a different style.",
        durationMinutes: 20,
        prices: [
            { label: "removal only", price: 15 },
            { label: "with new set", price: 10 },
        ],
    },
];