import { useRef } from "react";
import type { GalleryItem } from "../data/gallery";

interface GalleryProps {
    items: GalleryItem[];
}

export default function Gallery({ items }: GalleryProps) {
    const trackRef = useRef<HTMLUListElement>(null);

    function scrollByOneCard(direction: number) {
        const track = trackRef.current;
        if (!track) return;

        const firstCard = track.firstElementChild as HTMLElement | null;
        const step = firstCard ? firstCard.offsetWidth + 16 : track.clientWidth;

        track.scrollBy({ left: step * direction, behavior: "smooth" });
    }

    return (
        <section id="gallery" className="border-t border-ink/10 bg-butter py-16 md:py-20">
            {/* Heading stays centred and constrained */}
            <div className="mx-auto max-w-5xl px-6">
                <p className="font-body text-center text-xs uppercase tracking-[0.35em] text-ink-soft">
                    Our work
                </p>

                <h2 className="font-display italic mt-4 text-center text-4xl md:text-5xl">
                    Recent sets
                </h2>
            </div>

            {/* Track runs the full width of the page */}
            <div className="relative mt-12">
                <ul
                    ref={trackRef}
                    className="no-scrollbar flex snap-x snap-mandatory gap-4 overflow-x-auto px-6 pb-2"
                >
                    {items.map((item) => (
                        <li
                            key={item.id}
                            className="w-64 shrink-0 snap-start overflow-hidden rounded-xl border border-ink/15 md:w-80 lg:w-96"
                        >
                            <img
                                src={item.src}
                                alt={item.alt}
                                loading="lazy"
                                className="aspect-square w-full object-cover"
                            />
                        </li>
                    ))}
                </ul>

                <button
                    type="button"
                    onClick={() => scrollByOneCard(-1)}
                    aria-label="Previous images"
                    className="absolute top-1/2 left-4 hidden h-11 w-11 -translate-y-1/2 rounded-full border border-ink/15 bg-cream/90 text-lg backdrop-blur transition hover:bg-butter md:block"
                >
                    &#8249;
                </button>

                <button
                    type="button"
                    onClick={() => scrollByOneCard(1)}
                    aria-label="Next images"
                    className="absolute top-1/2 right-4 hidden h-11 w-11 -translate-y-1/2 rounded-full border border-ink/15 bg-cream/90 text-lg backdrop-blur transition hover:bg-butter md:block"
                >
                    &#8250;
                </button>
            </div>
        </section>
    );
}