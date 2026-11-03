import type { Salon } from "../data/salon";

interface FooterProps {
    salon: Salon;
}

export default function Footer({ salon }: FooterProps) {
    const telHref = `tel:${salon.phone.replace(/\s+/g, "")}`;

    return (
        // Extra bottom padding on phones so the fixed action bar never covers the footer.
        <footer className="border-t border-ink/10 bg-butter px-6 pt-14 pb-28 md:pb-14">
            <div className="mx-auto grid max-w-5xl gap-10 text-center md:grid-cols-3 md:text-left">
                <div>
                    <p className="font-display italic text-2xl">{salon.name}</p>
                    <p className="font-body mt-3 text-sm text-ink-soft">
                        Nail care by appointment in Amsterdam West.
                    </p>
                </div>

                <div className="font-body text-sm">
                    <p className="text-xs uppercase tracking-[0.25em] text-ink-soft">Visit</p>
                    <p className="mt-3">{salon.address}</p>
                    <p>{salon.city}</p>
                </div>

                <div className="font-body text-sm">
                    <p className="text-xs uppercase tracking-[0.25em] text-ink-soft">Book</p>
                    <a href={telHref} className="mt-3 block underline-offset-4 hover:underline">
                        {salon.phone}
                    </a>
                    <a href="#contact" className="text-ink-soft underline-offset-4 hover:underline">
                        Opening hours
                    </a>
                </div>
            </div>

            <p className="font-body mt-12 text-center text-xs uppercase tracking-[0.25em] text-ink-soft">
                © {new Date().getFullYear()} {salon.name}
            </p>
        </footer>
    );
}
