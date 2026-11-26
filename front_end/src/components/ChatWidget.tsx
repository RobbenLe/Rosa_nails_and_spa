import { useEffect, useRef, useState, type FormEvent } from "react";

import { ChatIcon } from "./icons";
import {
    ChatTooManyMessagesError,
    sendChat,
    type ChatBooking,
    type ChatMessage,
} from "../api";

// The chat window.
//   - Below 1024px (phones, tablets): full screen. It is opened from the bottom bar (MobileActionBar).
//   - 1024px and wider: a small panel in the bottom-right corner, opened from a floating button.
// App.tsx decides whether the chat is switched on (the kill switch) and whether it is open.
//
// Nothing is saved: the conversation only lives in this browser tab.

type Language = "en" | "nl";

const MAX_MESSAGE_CHARACTERS = 500;
const MAX_MESSAGES_SENT = 6;

const TEXT = {
    en: {
        open: "Rosa's Assistant",
        close: "Close chat",
        title: "Rosa's Assistant",
        subtitle: "Virtual assistant",
        privacy:
            "I'm a virtual assistant. Chats are not saved by us, but your messages are processed by an AI service (Anthropic). Please don't share health or sensitive details.",
        greeting: "Hi! Ask me about our services, prices and opening hours. I can also help you prepare a booking request.",
        placeholder: "Type your question...",
        send: "Send",
        typing: "Typing...",
        bookViaWhatsApp: "Book via WhatsApp",
        problem: "Something went wrong. Please ask Rosa directly on WhatsApp.",
        tooMany: "You have sent many messages. Please wait a few minutes or message Rosa on WhatsApp.",
        suggestions: ["What are your prices?", "When are you open?", "I'd like to book"],
    },
    nl: {
        open: "Rosa's Assistent",
        close: "Chat sluiten",
        title: "Rosa's Assistent",
        subtitle: "Virtuele assistent",
        privacy:
            "Ik ben een virtuele assistent. Wij slaan chats niet op, maar je berichten worden verwerkt door een AI-dienst (Anthropic). Deel geen gezondheids- of gevoelige gegevens.",
        greeting: "Hoi! Vraag me naar onze diensten, prijzen en openingstijden. Ik help je ook met een afspraakverzoek.",
        placeholder: "Typ je vraag...",
        send: "Verstuur",
        typing: "Aan het typen...",
        bookViaWhatsApp: "Boek via WhatsApp",
        problem: "Er ging iets mis. Vraag het Rosa direct via WhatsApp.",
        tooMany: "Je hebt veel berichten gestuurd. Wacht even of stuur Rosa een WhatsApp-bericht.",
        suggestions: ["Wat zijn de prijzen?", "Wanneer zijn jullie open?", "Ik wil een afspraak maken"],
    },
} as const;

interface ShownMessage {
    id: number;
    role: "user" | "assistant";
    content: string;
    showWhatsApp: boolean;
    booking: ChatBooking | null;
}

interface ChatWidgetProps {
    whatsapp: string;
    isEnabled: boolean;
    isOpen: boolean;
    onOpen: () => void;
    onClose: () => void;
}

// Matches Tailwind's `lg` breakpoint: below this width the chat is full screen.
const FULL_SCREEN_QUERY = "(max-width: 1023px)";

/** True while the screen is narrower than 1024px. Updates when the window is resized or rotated. */
function useIsFullScreenLayout(): boolean {
    const [isFullScreen, setIsFullScreen] = useState(() => window.matchMedia(FULL_SCREEN_QUERY).matches);

    useEffect(() => {
        const query = window.matchMedia(FULL_SCREEN_QUERY);
        const update = () => setIsFullScreen(query.matches);
        query.addEventListener("change", update);
        return () => query.removeEventListener("change", update);
    }, []);

    return isFullScreen;
}

interface VisibleArea {
    top: number;
    height: number;
}

/**
 * The part of the screen that is really visible. On phones the on-screen keyboard shrinks it,
 * so the chat follows it: the input stays above the keyboard and the newest message stays in view.
 * Returns null while not active, or when the browser does not support it (then CSS full height is used).
 */
function useVisibleArea(isActive: boolean): VisibleArea | null {
    const [area, setArea] = useState<VisibleArea | null>(null);

    useEffect(() => {
        const viewport = window.visualViewport;
        if (!isActive || !viewport) return;

        const update = () => setArea({ top: viewport.offsetTop, height: viewport.height });
        update();
        viewport.addEventListener("resize", update);
        viewport.addEventListener("scroll", update);
        return () => {
            viewport.removeEventListener("resize", update);
            viewport.removeEventListener("scroll", update);
        };
    }, [isActive]);

    return isActive ? area : null;
}

function guessLanguage(): Language {
    return navigator.language?.toLowerCase().startsWith("nl") ? "nl" : "en";
}

/** The ready-written WhatsApp message. Built here, so the number and text can never come from the AI. */
function buildWhatsAppLink(whatsappNumber: string, language: Language, booking: ChatBooking | null): string {
    let message: string;

    if (booking && language === "nl") {
        message = `Hoi Rosa, ik wil graag een afspraak maken voor ${booking.service} op ${booking.when}. Mijn naam is ${booking.name}.`;
    } else if (booking) {
        message = `Hi Rosa, I'd like to book ${booking.service} on ${booking.when}. My name is ${booking.name}.`;
    } else if (language === "nl") {
        message = "Hoi Rosa, ik wil graag een afspraak maken.";
    } else {
        message = "Hi Rosa, I'd like to make an appointment.";
    }

    return `https://wa.me/${whatsappNumber.replace(/\D/g, "")}?text=${encodeURIComponent(message)}`;
}

export default function ChatWidget({ whatsapp, isEnabled, isOpen, onOpen, onClose }: ChatWidgetProps) {
    const [language, setLanguage] = useState<Language>(guessLanguage);
    const [messages, setMessages] = useState<ShownMessage[]>([]);
    const [draft, setDraft] = useState("");
    const [isWaiting, setIsWaiting] = useState(false);
    const nextIdRef = useRef(1);
    const endOfMessagesRef = useRef<HTMLDivElement>(null);
    const text = TEXT[language];
    const isFullScreen = useIsFullScreenLayout();
    const visibleArea = useVisibleArea(isOpen && isFullScreen);

    // Keep the newest message in view, also when the keyboard opens or closes.
    useEffect(() => {
        endOfMessagesRef.current?.scrollIntoView({ block: "end" });
    }, [messages, isWaiting, isOpen, visibleArea?.height]);

    // Full screen: stop the page behind from scrolling.
    useEffect(() => {
        if (!isOpen || !isFullScreen) return;
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        return () => {
            document.body.style.overflow = previousOverflow;
        };
    }, [isOpen, isFullScreen]);

    // Escape closes the chat.
    useEffect(() => {
        if (!isOpen) return;
        const closeOnEscape = (event: KeyboardEvent) => {
            if (event.key === "Escape") onClose();
        };
        window.addEventListener("keydown", closeOnEscape);
        return () => window.removeEventListener("keydown", closeOnEscape);
    }, [isOpen, onClose]);

    if (!isEnabled) return null;

    function addMessage(partial: Omit<ShownMessage, "id">): ShownMessage[] {
        const message: ShownMessage = { ...partial, id: nextIdRef.current++ };
        const updated = [...messages, message];
        setMessages(updated);
        return updated;
    }

    async function sendMessage(customerText: string) {
        const trimmed = customerText.trim().slice(0, MAX_MESSAGE_CHARACTERS);
        if (!trimmed || isWaiting) return;

        setDraft("");
        const conversation = addMessage({ role: "user", content: trimmed, showWhatsApp: false, booking: null });
        setIsWaiting(true);

        const messagesForServer: ChatMessage[] = conversation
            .slice(-MAX_MESSAGES_SENT)
            .map((message) => ({ role: message.role, content: message.content }));

        try {
            const answer = await sendChat(messagesForServer);
            setMessages([
                ...conversation,
                {
                    id: nextIdRef.current++,
                    role: "assistant",
                    content: answer.reply,
                    showWhatsApp: answer.whatsapp,
                    booking: answer.booking,
                },
            ]);
        } catch (error) {
            const problemText = error instanceof ChatTooManyMessagesError ? text.tooMany : text.problem;
            setMessages([
                ...conversation,
                { id: nextIdRef.current++, role: "assistant", content: problemText, showWhatsApp: true, booking: null },
            ]);
        } finally {
            setIsWaiting(false);
        }
    }

    function handleSubmit(event: FormEvent) {
        event.preventDefault();
        sendMessage(draft);
    }

    return (
        <>
            {/* Wide screens only: small floating button, dark so it does not compete with the pink Call button. */}
            {!isOpen ? (
                <button
                    type="button"
                    onClick={onOpen}
                    aria-label={text.open}
                    className="fixed right-6 bottom-6 z-50 hidden min-h-12 items-center gap-2 rounded-full bg-ink px-5 font-body text-sm uppercase tracking-[0.1em] whitespace-nowrap text-cream shadow-lg transition hover:opacity-85 lg:flex"
                >
                    <ChatIcon />
                    {text.open}
                </button>
            ) : (
                <section
                    role="dialog"
                    aria-label={text.title}
                    // Phones and tablets: fills the visible screen. Wide screens: a panel in the corner.
                    style={isFullScreen && visibleArea ? { top: visibleArea.top, height: visibleArea.height } : undefined}
                    className="fixed inset-x-0 top-0 bottom-0 z-[60] flex flex-col overflow-hidden bg-cream lg:inset-x-auto lg:top-auto lg:right-6 lg:bottom-6 lg:h-[34rem] lg:max-h-[75vh] lg:w-96 lg:rounded-3xl lg:border lg:border-ink/10 lg:shadow-2xl"
                >
                    <header className="flex items-center justify-between gap-2 bg-butter pt-[max(0.5rem,env(safe-area-inset-top))] pr-3 pb-2 pl-5">
                        <div className="min-w-0">
                            <h2 className="font-display italic text-lg leading-tight whitespace-nowrap">{text.title}</h2>
                            <p className="font-body text-xs text-ink-soft">{text.subtitle}</p>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="flex rounded-full border border-ink/20">
                                {(["en", "nl"] as const).map((code) => (
                                    <button
                                        key={code}
                                        type="button"
                                        onClick={() => setLanguage(code)}
                                        aria-pressed={language === code}
                                        className={`min-h-11 min-w-11 rounded-full font-body text-xs uppercase ${
                                            language === code ? "bg-yellow" : "text-ink-soft"
                                        }`}
                                    >
                                        {code}
                                    </button>
                                ))}
                            </div>
                            <button
                                type="button"
                                onClick={onClose}
                                aria-label={text.close}
                                className="flex h-11 w-11 items-center justify-center rounded-full border border-ink/30 bg-cream text-xl"
                            >
                                {"\u2715"}
                            </button>
                        </div>
                    </header>

                    <p className="border-b border-ink/10 px-5 py-2 font-body text-xs text-ink-soft">{text.privacy}</p>

                    <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-5 py-4" aria-live="polite">
                        <p className="max-w-[85%] rounded-2xl bg-butter px-4 py-2 font-body text-sm">{text.greeting}</p>

                        {messages.length === 0 ? (
                            <div className="flex flex-wrap gap-2">
                                {text.suggestions.map((suggestion) => (
                                    <button
                                        key={suggestion}
                                        type="button"
                                        onClick={() => sendMessage(suggestion)}
                                        className="min-h-11 rounded-full border border-ink/20 px-4 font-body text-xs transition hover:border-ink/50"
                                    >
                                        {suggestion}
                                    </button>
                                ))}
                            </div>
                        ) : null}

                        {messages.map((message) => (
                            <div key={message.id} className={message.role === "user" ? "text-right" : ""}>
                                <p
                                    className={`inline-block max-w-[85%] whitespace-pre-line rounded-2xl px-4 py-2 text-left font-body text-sm ${
                                        message.role === "user" ? "bg-yellow" : "bg-butter"
                                    }`}
                                >
                                    {message.content}
                                </p>

                                {message.showWhatsApp ? (
                                    <a
                                        href={buildWhatsAppLink(whatsapp, language, message.booking)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        // Pink on phones (the chat covers the screen, so it is the only pink button). On wide screens the Navbar keeps the one pink button.
                                        className="mt-2 flex min-h-11 w-fit items-center rounded-full bg-coral px-5 font-body text-xs uppercase tracking-[0.15em] lg:bg-ink lg:text-cream"
                                    >
                                        {text.bookViaWhatsApp}
                                    </a>
                                ) : null}
                            </div>
                        ))}

                        {isWaiting ? <p className="font-body text-sm text-ink-soft">{text.typing}</p> : null}
                        <div ref={endOfMessagesRef} />
                    </div>

                    <form
                        onSubmit={handleSubmit}
                        className="flex gap-2 border-t border-ink/10 px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]"
                    >
                        <input
                            value={draft}
                            onChange={(event) => setDraft(event.target.value)}
                            maxLength={MAX_MESSAGE_CHARACTERS}
                            placeholder={text.placeholder}
                            aria-label={text.placeholder}
                            className="min-h-11 min-w-0 flex-1 rounded-full border border-ink/20 bg-white px-4 font-body text-base lg:text-sm"
                        />
                        <button
                            type="submit"
                            disabled={isWaiting || !draft.trim()}
                            className="min-h-11 rounded-full border border-ink/30 bg-cream px-4 font-body text-xs uppercase tracking-[0.15em] disabled:opacity-40"
                        >
                            {text.send}
                        </button>
                    </form>
                </section>
            )}
        </>
    );
}
