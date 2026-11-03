import { useRef, useState } from "react";
import type { GalleryItem } from "../data/gallery";

interface GalleryProps {
    items: GalleryItem[];
}

export default function Gallery({ items }: GalleryProps) {
    const trackRef = useRef<HTMLUListElement>(null);
    const dialogRef = useRef<HTMLDialogElement>(null);
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    function scrollByOneCard(direction: number) {
        const track = trackRef.current;
        if (!track) return;

        const firstCard = track.firstElementChild as HTMLElement | null;
        const step = firstCard ? firstCard.offsetWidth + 16 : track.clientWidth;

        track.scrollBy({ left: step * direction, behavior: "smooth" });
    }

    function openPhoto(index: number) {
        setOpenIndex(index);
        dialogRef.current?.showModal();
    }

    function showSibling(direction: number) {
        setOpenIndex((index) =>
            index === null ? null : (index + direction + items.length) % items.length
        );
    }

    const openItem = openIndex === null ? null : items[openIndex];

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
                    {items.map((item, index) => (
                        <li
                            key={item.id}
                            className="w-64 shrink-0 snap-start overflow-hidden rounded-xl border border-ink/15 md:w-80 lg:w-96"
                        >
                            <button
                                type="button"
                                onClick={() => openPhoto(index)}
                                aria-label={`View larger: ${item.alt}`}
                                className="block w-full cursor-zoom-in"
                            >
                                <img
                                    src={item.src}
                                    alt={item.alt}
                                    loading="lazy"
                                    className="aspect-square w-full object-cover transition duration-500 hover:scale-105"
                                />
                            </button>
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

            {/* Lightbox — the native <dialog> handles Esc, focus trapping and the backdrop */}
            <dialog
                ref={dialogRef}
                onClose={() => setOpenIndex(null)}
                onClick={(event) => {
                    // A click on the backdrop lands on the dialog itself, not its contents.
                    if (event.target === event.currentTarget) dialogRef.current?.close();
                }}
                onKeyDown={(event) => {
                    if (event.key === "ArrowLeft") showSibling(-1);
                    if (event.key === "ArrowRight") showSibling(1);
                }}
                className="m-auto max-h-[90vh] max-w-[min(90vw,48rem)] overflow-visible bg-transparent p-0 backdrop:bg-ink/80 backdrop:backdrop-blur-sm"
            >
                {openItem ? (
                    <figure className="relative">
                        <img
                            src={openItem.src}
                            alt={openItem.alt}
                            className="max-h-[80vh] w-auto rounded-2xl object-contain"
                        />
                        <figcaption className="font-body mt-3 text-center text-sm text-cream">
                            {openItem.alt}
                        </figcaption>

                        <button
                            type="button"
                            onClick={() => dialogRef.current?.close()}
                            aria-label="Close"
                            className="absolute top-3 right-3 h-10 w-10 rounded-full bg-cream/90 text-lg"
                        >
                            &#10005;
                        </button>
                        <button
                            type="button"
                            onClick={() => showSibling(-1)}
                            aria-label="Previous photo"
                            className="absolute top-1/2 left-3 h-10 w-10 -translate-y-1/2 rounded-full bg-cream/90 text-lg"
                        >
                            &#8249;
                        </button>
                        <button
                            type="button"
                            onClick={() => showSibling(1)}
                            aria-label="Next photo"
                            className="absolute top-1/2 right-3 h-10 w-10 -translate-y-1/2 rounded-full bg-cream/90 text-lg"
                        >
                            &#8250;
                        </button>
                    </figure>
                ) : null}
            </dialog>
        </section>
    );
}
