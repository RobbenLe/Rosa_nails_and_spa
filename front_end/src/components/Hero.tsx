interface HeroProps {
    salonName: string;
    tagline: string;
    phone: string;
}

// Styling shared by both buttons. Kept out of the markup so the
// structure stays readable and the two buttons can't drift apart.
const buttonBase =
    "rounded-full px-8 py-3 font-body text-sm uppercase tracking-[0.15em] transition";

export default function Hero({ salonName, tagline, phone }: HeroProps) {
    const telHref = `tel:${phone.replace(/\s+/g, "")}`;

    return (
        <section className="relative overflow-hidden px-6 py-24 md:py-32">
            {/* Decorative colour washes — purely visual, hidden from screen readers */}
            <div
                aria-hidden
                className="pointer-events-none absolute -top-24 -right-20 h-72 w-72 rounded-full bg-rose/40 blur-3xl"
            />
            <div
                aria-hidden
                className="pointer-events-none absolute -bottom-32 -left-24 h-80 w-80 rounded-full bg-yellow/30 blur-3xl"
            />

            <div className="relative mx-auto max-w-3xl text-center">
                <p className="font-body text-xs uppercase tracking-[0.35em] text-ink/60">
                    Amsterdam
                </p>

                <h1 className="font-display italic mt-6 text-5xl leading-[1.05] md:text-7xl">
                    {salonName}
                </h1>

                <p className="font-body mx-auto mt-6 max-w-md text-base text-ink/70 md:text-lg">
                    {tagline}
                </p>

                <div className="mt-10 flex flex-wrap justify-center gap-4">

                        <a href={telHref}
                        className={`${buttonBase} bg-coral hover:opacity-80`}
                    >
                        Call to book
                    </a>


                        <a href="#services"
                        className={`${buttonBase} border border-ink/20 hover:border-ink/50`}
                    >
                        View services
                    </a>
                </div>
            </div>
        </section>
    );
}