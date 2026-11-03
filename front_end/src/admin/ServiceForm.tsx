import { useState, type FormEvent } from "react";
import type { ServiceInput, ServiceRow } from "../api";

interface ServiceFormProps {
    categories: string[];
    existing: ServiceRow[];          // used to suggest names, so options group together
    initial: ServiceInput;
    isNew: boolean;
    onSave: (service: ServiceInput) => Promise<void>;
    onCancel: () => void;
}

const inputClass =
    "mt-1 w-full rounded-lg border border-ink/20 bg-cream px-3 py-2 font-body text-base focus:border-ink focus:outline-none";
const labelClass = "block font-body text-sm text-ink-soft";

export default function ServiceForm({ categories, existing, initial, isNew, onSave, onCancel }: ServiceFormProps) {
    const [form, setForm] = useState(initial);
    // Price is typed in euros; kept as text so "12." or "" don't fight the user while typing.
    const [priceText, setPriceText] = useState(isNew ? "" : String(initial.price_cents / 100));
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    function update<K extends keyof ServiceInput>(key: K, value: ServiceInput[K]) {
        setForm((current) => ({ ...current, [key]: value }));
    }

    const nameSuggestions = [
        ...new Set(existing.filter((row) => row.category === form.category).map((row) => row.name)),
    ];

    async function handleSubmit(event: FormEvent) {
        event.preventDefault();
        const euros = Number(priceText.replace(",", "."));
        if (priceText.trim() === "" || Number.isNaN(euros) || euros < 0) {
            setError("Enter a price in euros, e.g. 45 or 12.50");
            return;
        }

        setSaving(true);
        setError(null);
        try {
            await onSave({ ...form, price_cents: Math.round(euros * 100) });
        } catch (caught) {
            setError(caught instanceof Error ? caught.message : "Could not save");
            setSaving(false);
        }
    }

    return (
        <form onSubmit={handleSubmit} className="rounded-2xl border border-ink/10 bg-butter p-6 md:p-8">
            <h2 className="font-display italic text-3xl">{isNew ? "Add a service" : "Edit service"}</h2>

            <div className="mt-6 grid gap-5 md:grid-cols-2">
                <label className={labelClass}>
                    Category
                    <select
                        value={form.category}
                        onChange={(event) => update("category", event.target.value)}
                        className={inputClass}
                    >
                        {categories.map((category) => (
                            <option key={category}>{category}</option>
                        ))}
                    </select>
                </label>

                <label className={labelClass}>
                    Name
                    <input
                        required
                        list="service-names"
                        value={form.name}
                        onChange={(event) => update("name", event.target.value)}
                        placeholder="e.g. Gel Manicure"
                        className={inputClass}
                    />
                    <datalist id="service-names">
                        {nameSuggestions.map((name) => (
                            <option key={name} value={name} />
                        ))}
                    </datalist>
                </label>

                <label className={labelClass}>
                    Option <span className="text-xs">(optional)</span>
                    <input
                        value={form.variant}
                        onChange={(event) => update("variant", event.target.value)}
                        placeholder="e.g. new set, filling, from"
                        className={inputClass}
                    />
                    <span className="mt-1 block text-xs">
                        Same name + different option = one service with several prices.
                    </span>
                </label>

                <div className="grid grid-cols-2 gap-4">
                    <label className={labelClass}>
                        Price (€)
                        <input
                            required
                            inputMode="decimal"
                            value={priceText}
                            onChange={(event) => setPriceText(event.target.value)}
                            placeholder="45"
                            className={inputClass}
                        />
                    </label>

                    <label className={labelClass}>
                        Duration (min)
                        <input
                            required
                            type="number"
                            min={1}
                            max={600}
                            value={form.duration_minutes}
                            onChange={(event) => update("duration_minutes", Number(event.target.value))}
                            className={inputClass}
                        />
                    </label>
                </div>

                <label className={`${labelClass} md:col-span-2`}>
                    Description
                    <textarea
                        rows={2}
                        value={form.description}
                        onChange={(event) => update("description", event.target.value)}
                        className={inputClass}
                    />
                </label>

                <label className={`${labelClass} md:col-span-2`}>
                    Perfect for…
                    <textarea
                        rows={2}
                        value={form.suitable}
                        onChange={(event) => update("suitable", event.target.value)}
                        placeholder="Perfect for clients who…"
                        className={inputClass}
                    />
                </label>

                <label className="flex items-center gap-3 font-body text-sm">
                    <input
                        type="checkbox"
                        checked={form.is_active}
                        onChange={(event) => update("is_active", event.target.checked)}
                        className="h-5 w-5 accent-ink"
                    />
                    Show on the website
                </label>

                <label className="flex items-center gap-3 font-body text-sm">
                    <input
                        type="checkbox"
                        checked={form.is_bookable}
                        onChange={(event) => update("is_bookable", event.target.checked)}
                        className="h-5 w-5 accent-ink"
                    />
                    Can be booked on its own
                </label>
            </div>

            {error ? (
                <p role="alert" className="font-body mt-5 text-sm text-coral-deep">
                    {error}
                </p>
            ) : null}

            <div className="mt-8 flex flex-wrap gap-3">
                <button
                    type="submit"
                    disabled={saving}
                    className="rounded-full bg-coral px-7 py-3 font-body text-sm uppercase tracking-[0.15em] transition hover:opacity-80 disabled:opacity-50"
                >
                    {saving ? "Saving…" : isNew ? "Add service" : "Save changes"}
                </button>
                <button
                    type="button"
                    onClick={onCancel}
                    className="rounded-full border border-ink/20 px-7 py-3 font-body text-sm uppercase tracking-[0.15em] transition hover:border-ink/50"
                >
                    Cancel
                </button>
            </div>
        </form>
    );
}
