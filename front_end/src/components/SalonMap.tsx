import type { Salon } from "../data/salon";

interface SalonMapProps {
    salon: Salon;
}

export default function SalonMap({ salon }: SalonMapProps) {
    const query = encodeURIComponent(
        `${salon.name}, ${salon.address}, ${salon.city}`
    );

    return (
        <section aria-label="Salon location" className="h-[380px] w-full md:h-[460px]">
            <iframe
                title={`Map showing the location of ${salon.name}`}
                src={`https://maps.google.com/maps?q=${query}&z=15&output=embed`}
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                className="h-full w-full border-0"
            />
        </section>
    );
}