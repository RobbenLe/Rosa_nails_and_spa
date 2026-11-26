import { ChatIcon, PhoneIcon } from "./icons";

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
