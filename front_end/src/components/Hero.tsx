import type { GalleryItem } from "../data/gallery";
import type { OpenStatus } from "../lib/hours";

interface HeroProps {
    salonName: string;
    tagline: string;
    phone: string;
    status: OpenStatus;
    photos: GalleryItem[];
}

// Styling shared by both buttons. Kept out of the markup so the
// structure stays readable and the two buttons can't drift apart.
const buttonBase =
    "rounded-full px-8 py-3 font-body text-sm uppercase tracking-[0.15em] transition";

export default function Hero({ salonName, tagline, phone, status, photos }: HeroProps) {
    const telHref = `tel:${phone.replace(/\s+/g, "")}`;
    const [main, side] = photos;

    return (
        <section className="relative overflow-hidden px-6 py-16 md:py-24">
            {/* Decorative colour washes — purely visual, hidden from screen readers */}
            <div
                aria-hidden
                className="pointer-events-none absolute -top-24 -right-20 h-72 w-72 rounded-full bg-coral/30 blur-3xl"
            />
            <div
                aria-hidden
                className="pointer-events-none absolute -bottom-32 -left-24 h-80 w-80 rounded-full bg-yellow/30 blur-3xl"
            />

            <div className="relative mx-auto grid max-w-6xl items-center gap-14 md:grid-cols-2">
                <div className="text-center md:text-left">
                    <p className="font-body inline-flex items-center gap-2 rounded-full border border-ink/10 bg-cream/80 px-4 py-1.5 text-xs uppercase tracking-[0.2em] text-ink-soft">
                        <span
                            aria-hidden
                            className={`h-2 w-2 rounded-full ${status.isOpen ? "bg-green-600" : "bg-ink/30"}`}
                        />
                        {status.label}
                    </p>

                    <h1 className="font-display italic mt-6 text-5xl leading-[1.05] md:text-7xl">
                        {salonName}
                    </h1>

                    <p className="font-body mx-auto mt-6 max-w-md text-base text-ink-soft md:mx-0 md:text-lg">
                        {tagline}
                    </p>

                    <div className="mt-10 flex flex-wrap justify-center gap-4 md:justify-start">
                        <a href={telHref} className={`${buttonBase} bg-coral hover:opacity-80`}>
                            Call to book
                        </a>

                        <a
                            href="#services"
                            className={`${buttonBase} border border-ink/20 hover:border-ink/50`}
                        >
                            View prices
                        </a>
                    </div>
                </div>

                {main ? (
                    <div className="relative mx-auto w-full max-w-sm md:max-w-none">
                        <img
                            src={main.src}
                            alt={main.alt}
                            className="aspect-[4/5] w-full rounded-[2rem] border border-ink/10 object-cover shadow-xl shadow-ink/10 md:w-4/5"
                        />
                        {side ? (
                            <img
                                src={side.src}
                                alt={side.alt}
                                className="absolute -bottom-6 -left-4 hidden aspect-square w-40 rounded-2xl border-4 border-cream object-cover shadow-lg md:right-0 md:left-auto md:block md:w-48"
                            />
                        ) : null}
                    </div>
                ) : null}
            </div>
        </section>
    );
}
