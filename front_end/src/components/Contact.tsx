import type { Salon } from "../data/salon";
import { todayName } from "../lib/hours";

interface ContactProps {
    salon: Salon;
}

export default function Contact({ salon }: ContactProps) {
    const telHref = `tel:${salon.phone.replace(/\s+/g, "")}`;
    const waHref = `https://wa.me/${salon.whatsapp.replace(/\D/g, "")}`;
    const directionsHref = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(
        `${salon.name}, ${salon.address}, ${salon.city}`
    )}`;
    const today = todayName();

    return (
        <section id="contact" className="bg-cream px-6 py-16 md:py-20">
            <div className="mx-auto max-w-5xl rounded-3xl bg-butter px-6 py-16 md:px-12 md:py-20">
                <p className="font-body text-center text-xs uppercase tracking-[0.35em] text-ink-soft">
                    Find us
                </p>

                <h2 className="font-display italic mt-4 text-center text-4xl md:text-5xl">
                    Visit the salon
                </h2>

                <div className="mt-14 grid gap-14 md:grid-cols-2">
                    {/* Left: address and contact */}
                    <div>
                        <h3 className="font-body text-sm uppercase tracking-[0.25em] text-coral-deep">
                            Address
                        </h3>

                        <p className="font-body mt-4 text-lg">{salon.address}</p>
                        <p className="font-body text-lg">{salon.city}</p>

                        <a
                            href={directionsHref}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-body mt-2 inline-block text-sm text-ink-soft underline underline-offset-4 transition hover:text-ink"
                        >
                            Get directions
                        </a>

                        <div className="mt-8 flex flex-wrap gap-4">
                            <a
                                href={telHref}
                                className="rounded-full bg-coral px-7 py-3 font-body text-sm uppercase tracking-[0.15em] transition hover:opacity-80"
                            >
                                Call {salon.phone}
                            </a>

                            <a
                                href={waHref}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="rounded-full border border-ink/20 px-7 py-3 font-body text-sm uppercase tracking-[0.15em] transition hover:border-ink/50"
                            >
                                WhatsApp
                            </a>
                        </div>
                    </div>

                    {/* Right: opening hours, with today highlighted */}
                    <div>
                        <h3 className="font-body text-sm uppercase tracking-[0.25em] text-coral-deep">
                            Opening hours
                        </h3>

                        <dl className="mt-4">
                            {salon.hours.map((hour) => {
                                const isToday = hour.day === today;

                                return (
                                    <div
                                        key={hour.day}
                                        className={`flex justify-between border-b border-ink/10 py-2 ${
                                            isToday ? "font-medium" : ""
                                        }`}
                                    >
                                        <dt className="font-body text-sm">
                                            {hour.day}
                                            {isToday ? (
                                                <span className="ml-2 rounded-full bg-yellow px-2 py-0.5 text-[0.65rem] uppercase tracking-[0.15em]">
                                                    Today
                                                </span>
                                            ) : null}
                                        </dt>
                                        <dd
                                            className={`font-body text-sm ${
                                                hour.open ? "text-ink" : "text-ink-soft"
                                            }`}
                                        >
                                            {hour.open ? `${hour.open} – ${hour.close}` : "Closed"}
                                        </dd>
                                    </div>
                                );
                            })}
                        </dl>
                    </div>
                </div>
            </div>
        </section>
    );
}
