"use client";

import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import { useState } from "react";
import { useRouter } from "next/navigation";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix Leaflet's default marker icon not loading correctly under Next.js/webpack bundling
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const DEMO_REGION = { lat: 20.2, lon: 85.8, radiusDeg: 0.3, label: "Odisha Demo Region" };

function isInsideDemoRegion(lat: number, lon: number) {
  const dLat = lat - DEMO_REGION.lat;
  const dLon = lon - DEMO_REGION.lon;
  return Math.sqrt(dLat * dLat + dLon * dLon) < DEMO_REGION.radiusDeg;
}

function ClickHandler({ onClick }: { onClick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function MapView() {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);

  const handleMapClick = (lat: number, lon: number) => {
    if (isInsideDemoRegion(lat, lon)) {
      router.push("/process");
    } else {
      setMessage("No processed data for this area yet — try clicking near Odisha, India (the marker below).");
      setTimeout(() => setMessage(null), 4000);
    }
  };

  return (
    <div className="relative h-full w-full">
      <MapContainer
        center={[20.2, 85.8]}
        zoom={7}
        minZoom={3}
        maxZoom={16}
        maxBounds={[[-85, -180], [85, 180]]}
        maxBoundsViscosity={1.0}
        worldCopyJump={false}
        className="h-full w-full"
      >
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution="Tiles &copy; Esri"
          maxNativeZoom={16}
          noWrap={true}
        />
        <Marker position={[20.2, 85.8]}>
          <Popup>
            <b>{DEMO_REGION.label}</b>
            <br />
            Real Sentinel-2 &amp; Landsat data available here.
            <br />
            <button
              className="mt-2 rounded bg-blue-600 px-2 py-1 text-white"
              onClick={() => router.push("/process")}
            >
              Process this scene →
            </button>
          </Popup>
        </Marker>
        <ClickHandler onClick={handleMapClick} />
      </MapContainer>

      {message && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 rounded-lg bg-black/80 px-4 py-2 text-white shadow-lg">
          {message}
        </div>
      )}
    </div>
  );
}