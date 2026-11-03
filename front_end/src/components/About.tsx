import { CATEGORIES } from "../data/services";

interface AboutProps {
    paragraphs: string[];
}

export default function About({ paragraphs }: AboutProps) {
    return (
        <section id="about" className="border-t border-ink/10 bg-butter px-6 py-20 md:py-28">
            <div className="mx-auto max-w-2xl text-center">
                <p className="font-body text-xs uppercase tracking-[0.35em] text-ink-soft">
                    About us
                </p>

                <h2 className="font-display italic mt-4 text-4xl md:text-5xl">
                    Our story
                </h2>

                {paragraphs.map((paragraph, index) => (
                    <p
                        key={index}
                        className="font-body mt-6 text-base leading-relaxed text-ink-soft md:text-lg"
                    >
                        {paragraph}
                    </p>
                ))}

                <p className="font-body mt-12 text-xs uppercase tracking-[0.25em] text-ink-soft">
                    What we do
                </p>

                <div className="mt-5 flex flex-wrap justify-center gap-3">
                    {CATEGORIES.map((category) => (
                        <span
                            key={category}
                            className="rounded-full border border-ink/15 px-5 py-2 font-body text-sm"
                        >
                            {category}
                        </span>
                    ))}
                </div>
            </div>
        </section>
    );
}