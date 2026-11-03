const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface Review {
    id: string;
    author: string;
    rating: number;
    text: string;
    relativeTime: string;
}

export interface ReviewSummary {
    rating: number;
    total: number;
}

export interface ReviewsResponse {
    summary: ReviewSummary;
    reviews: Review[];
}

export async function fetchReviews(): Promise<ReviewsResponse> {
    const response = await fetch(`${API_BASE}/api/reviews`);

    if (!response.ok) {
        throw new Error(`Reviews request failed with ${response.status}`);
    }

    return response.json();
}

// ---------------------------------------------------------- services

/** One row in the database: a single bookable option with its own price. */
export interface ServiceRow {
    id: number;
    name: string;
    variant: string;
    category: string;
    description: string;
    suitable: string;
    duration_minutes: number;
    price_cents: number;
    is_active: boolean;
    is_bookable: boolean;
}

export type ServiceInput = Omit<ServiceRow, "id">;

export async function fetchServices(): Promise<ServiceRow[]> {
    const response = await fetch(`${API_BASE}/api/services`);

    if (!response.ok) {
        throw new Error(`Services request failed with ${response.status}`);
    }

    return response.json();
}

// ---------------------------------------------------------- admin

export class UnauthorizedError extends Error {}

/** Calls an admin endpoint with the password, and turns error replies into readable messages. */
async function adminRequest<T>(password: string, path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
        ...init,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${password}`,
        },
    });

    if (response.status === 401) throw new UnauthorizedError("Wrong password");

    if (!response.ok) {
        const body = await response.json().catch(() => null);
        const detail = Array.isArray(body?.detail)
            ? body.detail.map((item: { msg: string }) => item.msg).join(", ")
            : body?.detail;
        throw new Error(detail ?? `Request failed with ${response.status}`);
    }

    return response.status === 204 ? (undefined as T) : response.json();
}

export interface AdminServicesResponse {
    categories: string[];
    services: ServiceRow[];
}

export const adminApi = {
    list: (password: string) =>
        adminRequest<AdminServicesResponse>(password, "/api/admin/services"),

    create: (password: string, service: ServiceInput) =>
        adminRequest<ServiceRow>(password, "/api/admin/services", {
            method: "POST",
            body: JSON.stringify(service),
        }),

    update: (password: string, id: number, service: ServiceInput) =>
        adminRequest<ServiceRow>(password, `/api/admin/services/${id}`, {
            method: "PUT",
            body: JSON.stringify(service),
        }),

    remove: (password: string, id: number) =>
        adminRequest<{ hidden: boolean } | undefined>(password, `/api/admin/services/${id}`, {
            method: "DELETE",
        }),
};