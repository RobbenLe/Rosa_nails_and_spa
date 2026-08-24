import { useState } from "react";

const NAV_LINKS = [
    { href: "#about", label: "About" },
    { href: "#gallery", label: "Gallery" },
    { href: "#services", label: "Services" },
    { href: "#contact", label: "Contact" },
];

interface NavbarProps {
    salonName: string;
    phone: string;
}

export default function Navbar({ salonName, phone }: NavbarProps) {
    const [isOpen, setIsOpen] = useState(false);
    const telHref = `tel:${phone.replace(/\s+/g, "")}`;

    return (
        <header className="sticky top-0 z-50 border-b border-ink/10 bg-cream/85 backdrop-blur">
           <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
                <a href="#top" className="font-display italic text-xl md:text-2xl">
                    {salonName}
                </a>

                <ul className="hidden gap-10 md:flex">
                    {NAV_LINKS.map((link) => (
                        <li key={link.href}>

                               <a href={link.href} className="font-body text-sm uppercase tracking-[0.18em] text-ink-soft transition hover:text-ink">
                                {link.label}
                            </a>
                        </li>
                    ))}
                </ul>


                    <a href={telHref} className="hidden rounded-full bg-coral px-6 py-2.5 font-body text-sm uppercase tracking-[0.15em] transition hover:opacity-80 md:block">
                    Call to book
                </a>

                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    aria-expanded={isOpen}
                    aria-label="Toggle navigation menu"
                    className="font-body text-xl md:hidden"
                >
                    {isOpen ? "\u2715" : "\u2630"}
                </button>
            </nav>

            {isOpen ? (
                <ul className="border-t border-ink/10 bg-cream px-6 py-4 md:hidden">
                    {NAV_LINKS.map((link) => (
                        <li key={link.href}>

                               <a href={link.href}
                                onClick={() => setIsOpen(false)}
                                className="block py-3 font-body text-sm uppercase tracking-[0.18em] text-ink-soft"
                            >
                                {link.label}
                            </a>
                        </li>
                    ))}
                    <li>

                            <a href={telHref}
                            className="mt-2 block rounded-full bg-coral px-5 py-3 text-center font-body text-xs uppercase tracking-[0.15em]"
                        >
                            Call to book
                        </a>
                    </li>
                </ul>
            ) : null}
        </header>
    );
}