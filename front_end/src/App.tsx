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
import ChatWidget from "./components/ChatWidget";
import Footer from "./components/Footer";

import { fetchChatEnabled, fetchReviews, fetchServices, type ReviewsResponse } from "./api";
import { salon } from "./data/salon";
import { groupServiceRows, services as fallbackServices } from "./data/services";
import { gallery } from "./data/gallery";
import { openStatus } from "./lib/hours";

// The two sets shown in the hero, picked by id so the gallery order can change freely.
const HERO_PHOTO_IDS = ["set-05", "set-08"];

function App() {
    const [reviewData, setReviewData] = useState<ReviewsResponse | null>(null);
    const [services, setServices] = useState(fallbackServices);
    const [isChatEnabled, setIsChatEnabled] = useState(false);
    const [isChatOpen, setIsChatOpen] = useState(false);

    useEffect(() => {
        let cancelled = false;

        fetchReviews()
            .then((data) => {
                if (!cancelled) setReviewData(data);
            })
            .catch((error) => {
                console.error("Could not load reviews:", error);
            });

        fetchServices()
            .then((rows) => {
                if (!cancelled) setServices(groupServiceRows(rows));
            })
            .catch((error) => {
                console.error("Could not load services, showing the built-in list:", error);
            });

        // Chat kill switch: the chat buttons only appear when the server says the chat is on.
        fetchChatEnabled().then((enabled) => {
            if (!cancelled) setIsChatEnabled(enabled);
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

            <MobileActionBar
                phone={salon.phone}
                whatsapp={salon.whatsapp}
                isChatEnabled={isChatEnabled}
                onOpenChat={() => setIsChatOpen(true)}
            />

            <ChatWidget
                whatsapp={salon.whatsapp}
                isEnabled={isChatEnabled}
                isOpen={isChatOpen}
                onOpen={() => setIsChatOpen(true)}
                onClose={() => setIsChatOpen(false)}
            />
        </div>
    );
}

export default App;
