import { useState } from "react";
import { CATEGORIES, type Category, type Service } from "../data/services";

interface ServicesProps {
    services: Service[];
}

export default function Services({ services }: ServicesProps) {
    const [activeCategory, setActiveCategory] = useState<Category>(CATEGORIES[0]);

    const visibleServices = services.filter(
        (service) => service.category === activeCategory
    );

    return (
        <section id="services" className="border-t border-ink/10 bg-cream px-6 py-16 md:py-20">
            <div className="mx-auto max-w-4xl">
                <p className="font-body text-center text-xs uppercase tracking-[0.35em] text-coral-deep">
                    Price list
                </p>

                <h2 className="font-display italic mt-4 text-center text-4xl md:text-5xl">
                    Services
                </h2>

                {/* Tab row */}
                <div className="mt-12 flex flex-wrap justify-center gap-x-8 gap-y-3">
                    {CATEGORIES.map((category) => {
                        const isActive = category === activeCategory;

                        return (
                            <button
                                key={category}
                                type="button"
                                onClick={() => setActiveCategory(category)}
                                className={`font-body border-b-2 pb-3 text-sm uppercase tracking-[0.15em] transition ${
                                    isActive
                                        ? "border-coral text-ink"
                                        : "border-transparent text-ink-soft hover:text-ink"
                                }`}
                            >
                                {category}
                            </button>
                        );
                    })}
                </div>

                {/* Only the selected category's services */}
                <ul className="mt-10 space-y-3">
                    {visibleServices.map((service) => (
                        <li
                            key={service.id}
                            className="rounded-xl border border-ink/10 bg-cream px-6 py-5 transition hover:border-coral/50"
                        >
                            <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
                                <h3 className="font-display text-xl">{service.name}</h3>

                                <div className="font-body flex gap-5 text-base font-medium text-coral-deep">
                                    {service.prices.map((option) => (
                                        <span key={option.label ?? "only"}>
                                            {option.label ? (
                                                <span className="text-ink-soft font-normal">
                                                    {option.label}{" "}
                                                </span>
                                            ) : null}
                                            &euro;{option.price}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <p className="font-body mt-2 max-w-xl text-sm text-ink">
                                {service.description}
                            </p>

                            <p className="font-body mt-1 max-w-xl text-sm italic text-ink-soft">
                                {service.suitable}
                            </p>

                            <p className="font-body mt-3 inline-block rounded-full bg-butter px-3 py-1 text-xs uppercase tracking-[0.15em] text-ink-soft">
                                {service.durationMinutes} min
                            </p>
                        </li>
                    ))}
                </ul>
            </div>
        </section>
    );
}