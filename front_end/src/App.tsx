import { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import About from "./components/About";
import Reviews from "./components/Reviews";
import Gallery from "./components/Gallery";
import Services from "./components/Services";
import Contact from "./components/Contact";
import SalonMap from "./components/SalonMap";

import { fetchReviews, type ReviewsResponse } from "./api";
import { salon } from "./data/salon";
import { services } from "./data/services";
import { gallery } from "./data/gallery";

function App() {
    const [reviewData, setReviewData] = useState<ReviewsResponse | null>(null);

    useEffect(() => {
        let cancelled = false;

        fetchReviews()
            .then((data) => {
                if (!cancelled) setReviewData(data);
            })
            .catch((error) => {
                console.error("Could not load reviews:", error);
            });

        return () => {
            cancelled = true;
        };
    }, []);

    return (
        <div id="top" className="min-h-screen bg-cream text-ink">
            <Navbar salonName={salon.name} phone={salon.phone} />

            <Hero
                salonName={salon.name}
                tagline={salon.tagline}
                phone={salon.phone}
            />

            <About paragraphs={salon.about} />

            <Reviews
                reviews={reviewData?.reviews ?? []}
                summary={reviewData?.summary ?? { rating: 0, total: 0 }}
            />

            <Gallery items={gallery} />

            <Services services={services} />

            <Contact salon={salon} />

            <SalonMap salon={salon} />

            <footer className="border-t border-ink/10 px-6 py-10 text-center">
                <p className="font-body text-xs uppercase tracking-[0.25em] text-ink-soft">
                    {salon.name} · Amsterdam
                </p>
            </footer>
        </div>
    );
}

export default App;