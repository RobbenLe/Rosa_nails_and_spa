import { useEffect, useRef, useState } from "react";
import type { Review, ReviewSummary } from "../api";

interface ReviewsProps {
    reviews: Review[];
    summary: ReviewSummary;
}

function Stars({ rating }: { rating: number }) {
    return (
        <span className="text-coral" aria-label={`${rating} out of 5 stars`}>
            {"\u2605".repeat(rating)}
            <span className="text-ink/15">{"\u2605".repeat(5 - rating)}</span>
        </span>
    );
}

export default function Reviews({ reviews, summary }: ReviewsProps) {
    const trackRef = useRef<HTMLUListElement>(null);
    const [canScroll, setCanScroll] = useState(false);

    useEffect(() => {
        const track = trackRef.current;
        if (!track) return;

        function update() {
            if (!track) return;
            setCanScroll(track.scrollWidth > track.clientWidth + 8);
        }

        update();
        window.addEventListener("resize", update);
        return () => window.removeEventListener("resize", update);
    }, [reviews.length]);

    if (reviews.length === 0) return null;

    function scrollByOneCard(direction: number) {
        const track = trackRef.current;
        if (!track) return;
        const first = track.firstElementChild as HTMLElement | null;
        const step = first ? first.offsetWidth + 16 : track.clientWidth;
        track.scrollBy({ left: step * direction, behavior: "smooth" });
    }

    return (
        <section id="reviews" className="border-t border-ink/10 bg-cream py-16 md:py-20">
            <div className="mx-auto max-w-5xl px-6 text-center">
                <p className="font-body text-xs uppercase tracking-[0.35em] text-coral-deep">
                    Reviews
                </p>

                <h2 className="font-display italic mt-4 text-4xl md:text-5xl">
                    What clients say
                </h2>

                <p className="font-body mt-6 text-lg">
                    <Stars rating={Math.round(summary.rating)} />
                    <span className="ml-3 font-medium">{summary.rating}</span>
                    <span className="text-ink-soft">
                        {" "}· {summary.total} Google reviews
                    </span>
                </p>
            </div>

            <div className="relative mt-10">
                <ul
                    ref={trackRef}
                    className={`no-scrollbar flex snap-x snap-proximity gap-4 overflow-x-auto px-6 pb-2 ${
                        canScroll ? "" : "justify-center"
                    }`}
                >
                    {reviews.map((review) => (
                        <li
                            key={review.id}
                            className="flex w-72 shrink-0 snap-start flex-col rounded-xl border border-ink/10 bg-butter p-6 md:w-80"
                        >
                            <Stars rating={review.rating} />

                            <p className="font-body mt-4 grow text-sm leading-relaxed">
                                {review.text}
                            </p>

                            <p className="font-body mt-5 text-sm font-medium">
                                {review.author}
                            </p>
                            <p className="font-body text-xs text-ink-soft">
                                {review.relativeTime}
                            </p>
                        </li>
                    ))}
                </ul>

                {canScroll ? (
                    <>
                        <button type="button" onClick={() => scrollByOneCard(-1)} aria-label="Previous reviews" className="absolute top-1/2 left-4 hidden h-11 w-11 -translate-y-1/2 rounded-full border border-ink/15 bg-cream/90 backdrop-blur transition hover:bg-butter md:block">
                            &#8249;
                        </button>

                        <button type="button" onClick={() => scrollByOneCard(1)} aria-label="Next reviews" className="absolute top-1/2 right-4 hidden h-11 w-11 -translate-y-1/2 rounded-full border border-ink/15 bg-cream/90 backdrop-blur transition hover:bg-butter md:block">
                            &#8250;
                        </button>
                    </>
                ) : null}
            </div>

            <p className="mt-6 text-center font-body text-xs text-ink-soft">
                <a href="https://search.google.com/local/reviews?placeid=ChIJkWLDq4XjxUcRmE8ZwH0Vpls" target="_blank" rel="noopener noreferrer" className="underline underline-offset-4 transition hover:text-ink">
                    Read all {summary.total} reviews on Google
                </a>
            </p>
        </section>
    );
}