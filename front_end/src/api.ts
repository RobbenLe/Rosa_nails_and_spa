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