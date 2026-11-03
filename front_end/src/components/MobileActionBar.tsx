interface MobileActionBarProps {
    phone: string;
    whatsapp: string;
}

// Phones only: keeps "call" and "WhatsApp" one tap away while scrolling.
export default function MobileActionBar({ phone, whatsapp }: MobileActionBarProps) {
    const telHref = `tel:${phone.replace(/\s+/g, "")}`;
    const waHref = `https://wa.me/${whatsapp.replace(/\D/g, "")}`;

    return (
        <div className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-2 gap-3 border-t border-ink/10 bg-cream/95 px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur md:hidden">
            <a
                href={telHref}
                className="rounded-full bg-coral py-3 text-center font-body text-sm uppercase tracking-[0.15em]"
            >
                Call to book
            </a>
            <a
                href={waHref}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-full border border-ink/20 py-3 text-center font-body text-sm uppercase tracking-[0.15em]"
            >
                WhatsApp
            </a>
        </div>
    );
}
