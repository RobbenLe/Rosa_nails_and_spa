import type { Salon } from "../data/salon";

interface ContactProps {
    salon: Salon;
}

export default function Contact({ salon }: ContactProps) {
    const telHref = `tel:${salon.phone.replace(/\s+/g, "")}`;
    const waHref = `https://wa.me/${salon.whatsapp.replace(/\D/g, "")}`;

    return (
        <section id="contact" className="bg-yellow-soft px-6 py-17 md:py-10">
            <div className="mx-auto max-w-5xl rounded-3xl bg-butter px-6 py-16 md:px-12 md:py-20">
                <p className="font-body text-center text-xs uppercase tracking-[0.35em] text-ink/60">
                    Find us
                </p>

                <h2 className="font-display italic mt-4 text-center text-4xl md:text-5xl">
                    Visit the salon
                </h2>

                <div className="mt-14 grid gap-14 md:grid-cols-2">
                    {/* Left: address and contact */}
                    <div>
                        <h3 className="font-body text-sm uppercase tracking-[0.25em] text-coral">
                            Address
                        </h3>

                        <p className="font-body mt-4 text-lg">{salon.address}</p>
                        <p className="font-body text-lg">{salon.city}</p>

                        <div className="mt-8 flex flex-wrap gap-4">

                                <a href={telHref}
                                className="rounded-full bg-coral px-7 py-3 font-body text-sm uppercase tracking-[0.15em] transition hover:opacity-80"
                            >
                                Call {salon.phone}
                            </a>


                                <a href={waHref}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="rounded-full border border-ink/20 px-7 py-3 font-body text-sm uppercase tracking-[0.15em] transition hover:border-ink/50"
                            >
                                WhatsApp
                            </a>
                        </div>
                    </div>

                    {/* Right: opening hours */}
                    <div>
                        <h3 className="font-body text-sm uppercase tracking-[0.25em] text-coral">
                            Opening hours
                        </h3>

                        <dl className="mt-4">
                            {salon.hours.map((hour) => (
                                <div
                                    key={hour.day}
                                    className="flex justify-between border-b border-ink/10 py-2"
                                >
                                    <dt className="font-body text-sm">{hour.day}</dt>
                                    <dd
                                        className={`font-body text-sm ${
                                            hour.open ? "text-ink/80" : "text-ink/55"
                                        }`}
                                    >
                                        {hour.open ? `${hour.open} – ${hour.close}` : "Closed"}
                                    </dd>
                                </div>
                            ))}
                        </dl>
                    </div>
                </div>
            </div>
        </section>
    );
}