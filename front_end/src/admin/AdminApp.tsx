import { useCallback, useEffect, useState, type FormEvent } from "react";
import { adminApi, UnauthorizedError, type ServiceInput, type ServiceRow } from "../api";
import ServiceForm from "./ServiceForm";

// Remembered for this browser tab only, so closing the tab logs out.
const PASSWORD_KEY = "rosa-admin-password";

function loadPassword(): string {
    try {
        return sessionStorage.getItem(PASSWORD_KEY) ?? "";
    } catch {
        return "";
    }
}

function savePassword(password: string) {
    try {
        if (password) sessionStorage.setItem(PASSWORD_KEY, password);
        else sessionStorage.removeItem(PASSWORD_KEY);
    } catch {
        // Storage blocked: the admin just logs in again next visit.
    }
}

type Editing = { mode: "new" } | { mode: "edit"; service: ServiceRow } | null;

export default function AdminApp() {
    const [password, setPassword] = useState(loadPassword);
    const [categories, setCategories] = useState<string[]>([]);
    const [services, setServices] = useState<ServiceRow[] | null>(null);
    const [editing, setEditing] = useState<Editing>(null);
    const [notice, setNotice] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const logOut = useCallback(() => {
        savePassword("");
        setPassword("");
        setServices(null);
    }, []);

    const reload = useCallback(
        () =>
            adminApi
                .list(password)
                .then((data) => {
                    setCategories(data.categories);
                    setServices(data.services);
                    setError(null);
                })
                .catch((caught) => {
                    if (caught instanceof UnauthorizedError) logOut();
                    setError(caught instanceof Error ? caught.message : "Could not load services");
                }),
        [password, logOut]
    );

    useEffect(() => {
        if (!password) return;
        reload();
    }, [password, reload]);

    useEffect(() => {
        document.title = "Admin · Rosa Nails & Spa";
    }, []);

    if (!password) {
        return <Login error={error} onLogin={(value) => { savePassword(value); setError(null); setPassword(value); }} />;
    }

    async function save(input: ServiceInput) {
        if (editing?.mode === "edit") {
            await adminApi.update(password, editing.service.id, input);
            setNotice(`Saved “${input.name}”.`);
        } else {
            await adminApi.create(password, input);
            setNotice(`Added “${input.name}”.`);
        }
        setEditing(null);
        await reload();
    }

    async function remove(service: ServiceRow) {
        const label = service.variant ? `${service.name} – ${service.variant}` : service.name;
        if (!window.confirm(`Delete “${label}”? This cannot be undone.`)) return;

        try {
            const result = await adminApi.remove(password, service.id);
            setNotice(
                result?.hidden
                    ? `“${label}” has bookings, so it was hidden from the website instead of deleted.`
                    : `Deleted “${label}”.`
            );
            await reload();
        } catch (caught) {
            setError(caught instanceof Error ? caught.message : "Could not delete");
        }
    }

    const blank: ServiceInput = {
        name: "",
        variant: "",
        category: categories[0] ?? "",
        description: "",
        suitable: "",
        duration_minutes: 30,
        price_cents: 0,
        is_active: true,
        is_bookable: true,
    };

    return (
        <div className="min-h-screen bg-cream text-ink">
            <header className="sticky top-0 z-10 border-b border-ink/10 bg-cream/90 backdrop-blur">
                <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-6 py-4">
                    <p className="font-display italic text-xl">Rosa Nails &amp; Spa · Admin</p>
                    <div className="flex gap-5 font-body text-sm">
                        <a href="/#services" className="text-ink-soft underline-offset-4 hover:underline">
                            View website
                        </a>
                        <button type="button" onClick={logOut} className="text-ink-soft underline-offset-4 hover:underline">
                            Log out
                        </button>
                    </div>
                </div>
            </header>

            <main className="mx-auto max-w-5xl px-6 py-10">
                <div className="flex flex-wrap items-end justify-between gap-4">
                    <div>
                        <h1 className="font-display italic text-4xl">Services &amp; prices</h1>
                        <p className="font-body mt-2 text-sm text-ink-soft">
                            Changes show on the website straight away.
                        </p>
                    </div>
                    {editing ? null : (
                        <button
                            type="button"
                            onClick={() => { setNotice(null); setEditing({ mode: "new" }); }}
                            className="rounded-full bg-coral px-7 py-3 font-body text-sm uppercase tracking-[0.15em] transition hover:opacity-80"
                        >
                            + Add service
                        </button>
                    )}
                </div>

                {notice ? (
                    <p role="status" className="font-body mt-6 rounded-xl bg-butter px-4 py-3 text-sm">
                        {notice}
                    </p>
                ) : null}
                {error ? (
                    <p role="alert" className="font-body mt-6 text-sm text-coral-deep">
                        {error}
                    </p>
                ) : null}

                {editing ? (
                    <div className="mt-8">
                        <ServiceForm
                            // Remount when switching services so the form starts from the right values.
                            key={editing.mode === "edit" ? editing.service.id : "new"}
                            categories={categories}
                            existing={services ?? []}
                            initial={editing.mode === "edit" ? editing.service : blank}
                            isNew={editing.mode === "new"}
                            onSave={save}
                            onCancel={() => setEditing(null)}
                        />
                    </div>
                ) : null}

                {services === null ? (
                    <p className="font-body mt-10 text-ink-soft">Loading…</p>
                ) : (
                    categories.map((category) => {
                        const rows = services.filter((service) => service.category === category);

                        return (
                            <section key={category} className="mt-12">
                                <h2 className="font-body text-sm uppercase tracking-[0.25em] text-coral-deep">
                                    {category}
                                </h2>

                                {rows.length === 0 ? (
                                    <p className="font-body mt-3 text-sm text-ink-soft">No services yet.</p>
                                ) : (
                                    <ul className="mt-3 divide-y divide-ink/10 rounded-xl border border-ink/10 bg-cream">
                                        {rows.map((service) => (
                                            <li
                                                key={service.id}
                                                className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2 px-5 py-4"
                                            >
                                                <div className={service.is_active ? "" : "opacity-50"}>
                                                    <p className="font-display text-lg">
                                                        {service.name}
                                                        {service.variant ? (
                                                            <span className="font-body text-sm text-ink-soft"> · {service.variant}</span>
                                                        ) : null}
                                                    </p>
                                                    <p className="font-body text-sm text-ink-soft">
                                                        €{(service.price_cents / 100).toFixed(2)} · {service.duration_minutes} min
                                                        {service.is_active ? "" : " · hidden"}
                                                        {service.is_bookable ? "" : " · not bookable"}
                                                    </p>
                                                </div>

                                                <div className="flex gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            setNotice(null);
                                                            setEditing({ mode: "edit", service });
                                                            window.scrollTo({ top: 0, behavior: "smooth" });
                                                        }}
                                                        className="rounded-full border border-ink/20 px-4 py-1.5 font-body text-sm transition hover:border-ink/50"
                                                    >
                                                        Edit
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => remove(service)}
                                                        className="rounded-full border border-ink/20 px-4 py-1.5 font-body text-sm text-coral-deep transition hover:border-coral-deep"
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </section>
                        );
                    })
                )}
            </main>
        </div>
    );
}

function Login({ error, onLogin }: { error: string | null; onLogin: (password: string) => void }) {
    const [value, setValue] = useState("");

    function handleSubmit(event: FormEvent) {
        event.preventDefault();
        if (value) onLogin(value);
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-cream px-6 text-ink">
            <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-2xl bg-butter p-8">
                <p className="font-body text-xs uppercase tracking-[0.35em] text-ink-soft">Rosa Nails &amp; Spa</p>
                <h1 className="font-display italic mt-3 text-4xl">Admin</h1>

                <label className="mt-8 block font-body text-sm text-ink-soft">
                    Password
                    <input
                        type="password"
                        autoFocus
                        autoComplete="current-password"
                        value={value}
                        onChange={(event) => setValue(event.target.value)}
                        className="mt-1 w-full rounded-lg border border-ink/20 bg-cream px-3 py-2 text-base text-ink focus:border-ink focus:outline-none"
                    />
                </label>

                {error ? (
                    <p role="alert" className="font-body mt-3 text-sm text-coral-deep">
                        {error}
                    </p>
                ) : null}

                <button
                    type="submit"
                    className="mt-6 w-full rounded-full bg-coral py-3 font-body text-sm uppercase tracking-[0.15em] transition hover:opacity-80"
                >
                    Log in
                </button>
            </form>
        </div>
    );
}
