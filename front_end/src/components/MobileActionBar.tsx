import { ChatIcon, PhoneIcon } from "./icons";

interface MobileActionBarProps {
    phone: string;
    whatsapp: string;
    isChatEnabled: boolean;        // false when the chat kill switch is off: the Chat button disappears
    onOpenChat: () => void;
}

// Phones and tablets (below 1024px): keeps Assistant (the chat), Call and WhatsApp one tap away while scrolling.
// Only WhatsApp is pink, because that is where an appointment is actually requested.
// Every button is at least 48px tall, above the 44px minimum for fingers.
const buttonBase =
    "flex min-h-12 items-center justify-center gap-1.5 rounded-full px-2 text-center font-body text-xs uppercase tracking-[0.06em] whitespace-nowrap";
const quietButton = `${buttonBase} border border-ink/30 bg-cream text-ink`;
const pinkButton = `${buttonBase} bg-coral text-ink`;

export default function MobileActionBar({ phone, whatsapp, isChatEnabled, onOpenChat }: MobileActionBarProps) {
    const telHref = `tel:${phone.replace(/\s+/g, "")}`;
    const waHref = `https://wa.me/${whatsapp.replace(/\D/g, "")}`;
    // The Assistant label is the longest, so its column is wider; this keeps every label on one line at 360px.
    const columnClass = isChatEnabled ? "grid-cols-[1.5fr_1fr_1.3fr]" : "grid-cols-2";
    const assistantLabel = navigator.language?.toLowerCase().startsWith("nl") ? "Assistent" : "Assistant";

    return (
        <div
            className={`fixed inset-x-0 bottom-0 z-40 grid ${columnClass} gap-2 border-t border-ink/10 bg-cream/95 px-3 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur lg:hidden`}
        >
            {isChatEnabled ? (
                <button type="button" onClick={onOpenChat} className={quietButton}>
                    <ChatIcon />
                    {assistantLabel}
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
