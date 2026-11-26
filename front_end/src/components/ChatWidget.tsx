import { useEffect, useRef, useState, type FormEvent } from "react";

import {
    ChatTooManyMessagesError,
    fetchChatEnabled,
    sendChat,
    type ChatBooking,
    type ChatMessage,
} from "../api";

// The chat window. It is hidden unless the server says the chatbot is switched on
// (the kill switch), so turning the chatbot off on the server removes it from the website.
//
// Nothing is saved: the conversation only lives in this browser tab.

type Language = "en" | "nl";

const MAX_MESSAGE_CHARACTERS = 500;
const MAX_MESSAGES_SENT = 6;

const TEXT = {
    en: {
        open: "Chat with us",
        close: "Close chat",
        title: "Ask Rosa's assistant",
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
        open: "Chat met ons",
        close: "Chat sluiten",
        title: "Vraag het aan Rosa's assistent",
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

export default function ChatWidget({ whatsapp }: ChatWidgetProps) {
    const [isEnabled, setIsEnabled] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [language, setLanguage] = useState<Language>(guessLanguage);
    const [messages, setMessages] = useState<ShownMessage[]>([]);
    const [draft, setDraft] = useState("");
    const [isWaiting, setIsWaiting] = useState(false);
    const nextIdRef = useRef(1);
    const endOfMessagesRef = useRef<HTMLDivElement>(null);
    const text = TEXT[language];

    useEffect(() => {
        let cancelled = false;
        fetchChatEnabled().then((enabled) => {
            if (!cancelled) setIsEnabled(enabled);
        });
        return () => {
            cancelled = true;
        };
    }, []);

    useEffect(() => {
        endOfMessagesRef.current?.scrollIntoView({ block: "end" });
    }, [messages, isWaiting, isOpen]);

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
            {!isOpen ? (
                <button
                    type="button"
                    onClick={() => setIsOpen(true)}
                    className="fixed right-4 bottom-24 z-50 rounded-full bg-coral px-6 py-3 font-body text-sm uppercase tracking-[0.15em] shadow-lg transition hover:opacity-80 md:bottom-6"
                >
                    {text.open}
                </button>
            ) : (
                <section
                    role="dialog"
                    aria-label={text.title}
                    className="fixed inset-x-3 bottom-24 z-50 flex max-h-[75vh] flex-col overflow-hidden rounded-3xl border border-ink/10 bg-cream shadow-2xl md:inset-x-auto md:right-6 md:bottom-6 md:w-96"
                >
                    <header className="flex items-center justify-between gap-2 bg-butter px-5 py-3">
                        <h2 className="font-display italic text-lg">{text.title}</h2>
                        <div className="flex items-center gap-2">
                            {(["en", "nl"] as const).map((code) => (
                                <button
                                    key={code}
                                    type="button"
                                    onClick={() => setLanguage(code)}
                                    aria-pressed={language === code}
                                    className={`rounded-full px-2 py-0.5 font-body text-xs uppercase ${
                                        language === code ? "bg-yellow" : "text-ink-soft"
                                    }`}
                                >
                                    {code}
                                </button>
                            ))}
                            <button
                                type="button"
                                onClick={() => setIsOpen(false)}
                                aria-label={text.close}
                                className="font-body text-lg"
                            >
                                {"✕"}
                            </button>
                        </div>
                    </header>

                    <p className="border-b border-ink/10 px-5 py-2 font-body text-xs text-ink-soft">{text.privacy}</p>

                    <div className="flex-1 space-y-3 overflow-y-auto px-5 py-4" aria-live="polite">
                        <p className="max-w-[85%] rounded-2xl bg-butter px-4 py-2 font-body text-sm">{text.greeting}</p>

                        {messages.length === 0 ? (
                            <div className="flex flex-wrap gap-2">
                                {text.suggestions.map((suggestion) => (
                                    <button
                                        key={suggestion}
                                        type="button"
                                        onClick={() => sendMessage(suggestion)}
                                        className="rounded-full border border-ink/20 px-3 py-1 font-body text-xs transition hover:border-ink/50"
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
                                        message.role === "user" ? "bg-coral" : "bg-butter"
                                    }`}
                                >
                                    {message.content}
                                </p>

                                {message.showWhatsApp ? (
                                    <a
                                        href={buildWhatsAppLink(whatsapp, language, message.booking)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="mt-2 block w-fit rounded-full bg-yellow px-4 py-2 font-body text-xs uppercase tracking-[0.15em]"
                                    >
                                        {text.bookViaWhatsApp}
                                    </a>
                                ) : null}
                            </div>
                        ))}

                        {isWaiting ? <p className="font-body text-sm text-ink-soft">{text.typing}</p> : null}
                        <div ref={endOfMessagesRef} />
                    </div>

                    <form onSubmit={handleSubmit} className="flex gap-2 border-t border-ink/10 px-4 py-3">
                        <input
                            value={draft}
                            onChange={(event) => setDraft(event.target.value)}
                            maxLength={MAX_MESSAGE_CHARACTERS}
                            placeholder={text.placeholder}
                            aria-label={text.placeholder}
                            className="min-w-0 flex-1 rounded-full border border-ink/20 bg-white px-4 py-2 font-body text-sm"
                        />
                        <button
                            type="submit"
                            disabled={isWaiting || !draft.trim()}
                            className="rounded-full bg-coral px-4 py-2 font-body text-xs uppercase tracking-[0.15em] disabled:opacity-40"
                        >
                            {text.send}
                        </button>
                    </form>
                </section>
            )}
        </>
    );
}
