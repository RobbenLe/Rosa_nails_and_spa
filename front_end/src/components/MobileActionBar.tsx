interface MobileActionBarProps {
    phone: string;
    whatsapp: string;
    isChatEnabled: boolean;        // false when the chat kill switch is off: the Chat button disappears
    onOpenChat: () => void;
}

// Phones and tablets (below 1024px): keeps Chat, Call and WhatsApp one tap away while scrolling.
// Only WhatsApp is pink, because that is where an appointment is actually requested.
// Every button is at least 48px tall, above the 44px minimum for fingers.
const buttonBase =
    "flex min-h-12 items-center justify-center gap-2 rounded-full px-2 text-center font-body text-xs uppercase tracking-[0.1em]";
const quietButton = `${buttonBase} border border-ink/30 bg-cream text-ink`;
const pinkButton = `${buttonBase} bg-coral text-ink`;

function ChatIcon() {
    return (
        <svg aria-hidden width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.2A8 8 0 1 1 21 12z" />
        </svg>
    );
}

function PhoneIcon() {
    return (
        <svg aria-hidden width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z" />
        </svg>
    );
}

export default function MobileActionBar({ phone, whatsapp, isChatEnabled, onOpenChat }: MobileActionBarProps) {
    const telHref = `tel:${phone.replace(/\s+/g, "")}`;
    const waHref = `https://wa.me/${whatsapp.replace(/\D/g, "")}`;
    const columnClass = isChatEnabled ? "grid-cols-3" : "grid-cols-2";

    return (
        <div
            className={`fixed inset-x-0 bottom-0 z-40 grid ${columnClass} gap-2 border-t border-ink/10 bg-cream/95 px-3 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur lg:hidden`}
        >
            {isChatEnabled ? (
                <button type="button" onClick={onOpenChat} className={quietButton}>
                    <ChatIcon />
                    Chat
                </button>
            ) : null}

            <a href={telHref} className={quietButton}>
                <PhoneIcon />
                Call
            </a>

            <a href={waHref} target="_blank" rel="noopener noreferrer" className={pinkButton}>
                WhatsApp
            </a>
        </div>
    );
}
