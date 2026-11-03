import { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import About from "./components/About";
import Reviews from "./components/Reviews";
import Gallery from "./components/Gallery";
import Services from "./components/Services";
import Contact from "./components/Contact";
import SalonMap from "./components/SalonMap";
import MobileActionBar from "./components/MobileActionBar";
import Footer from "./components/Footer";

import { fetchReviews, type ReviewsResponse } from "./api";
import { salon } from "./data/salon";
import { services } from "./data/services";
import { gallery } from "./data/gallery";
import { openStatus } from "./lib/hours";

// The two sets shown in the hero, picked by id so the gallery order can change freely.
const HERO_PHOTO_IDS = ["set-05", "set-08"];

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

    const heroPhotos = gallery.filter((item) => HERO_PHOTO_IDS.includes(item.id));

    return (
        <div id="top" className="min-h-screen bg-cream text-ink">
            <Navbar salonName={salon.name} phone={salon.phone} />

            <main>
                <Hero
                    salonName={salon.name}
                    tagline={salon.tagline}
                    phone={salon.phone}
                    status={openStatus(salon.hours)}
                    photos={heroPhotos}
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
            </main>

            <Footer salon={salon} />

            <MobileActionBar phone={salon.phone} whatsapp={salon.whatsapp} />
        </div>
    );
}

export default App;
