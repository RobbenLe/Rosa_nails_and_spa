import { ChatIcon, PhoneIcon } from "./icons";

interface MobileActionBarProps {
    phone: string;
    whatsapp: string;
    isChatEnabled: boolean | null; // null = not known yet (room is kept); false = kill switch off: the button disappears
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
    // While we do not know yet (null) the Assistant slot is kept, so the bar does not jump when the answer arrives.
    const showAssistantSlot = isChatEnabled !== false;
    const columnClass = showAssistantSlot ? "grid-cols-[1.5fr_1fr_1.3fr]" : "grid-cols-2";
    const assistantLabel = navigator.language?.toLowerCase().startsWith("nl") ? "Assistent" : "Assistant";

    return (
        <div
            className={`fixed inset-x-0 bottom-0 z-40 grid ${columnClass} gap-2 border-t border-ink/10 bg-cream/95 px-3 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur lg:hidden`}
        >
            {isChatEnabled === true ? (
                <button type="button" onClick={onOpenChat} className={quietButton}>
                    <ChatIcon />
                    {assistantLabel}
                </button>
            ) : null}

            {isChatEnabled === null ? (
                // Invisible stand-in with the same size: nobody can see or tap it.
                <span aria-hidden className={`${quietButton} invisible`}>
                    <ChatIcon />
                    {assistantLabel}
                </span>
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
