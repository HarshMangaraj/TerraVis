"use client";

import { MapContainer, TileLayer, ImageOverlay, useMapEvents } from "react-leaflet";
import { useState } from "react";
import { useRouter } from "next/navigation";
import "leaflet/dist/leaflet.css";

const OWM_API_KEY = "5ba57419e2277297fb5c9e8e66cd6763";

const PS2_BOUNDS: [[number, number], [number, number]] = [
  [19.797844728587815, 85.07855877196576],
  [20.79805182127461, 86.1387858835574],
];

// Landsat scene sits in roughly the same region — offset slightly so both are visible
const PS10_BOUNDS: [[number, number], [number, number]] = [
  [19.9, 86.3],
  [20.9, 87.3],
];

const MAP_CENTER: [number, number] = [20.3, 86.2];

function ClickHandler({ onClick }: { onClick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function isInside(lat: number, lon: number, bounds: [[number, number], [number, number]]) {
  const [[minLat, minLon], [maxLat, maxLon]] = bounds;
  return lat >= minLat && lat <= maxLat && lon >= minLon && lon <= maxLon;
}

export default function MapView() {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [hoveringPS2, setHoveringPS2] = useState(false);

  const handleMapClick = (lat: number, lon: number) => {
    if (isInside(lat, lon, PS2_BOUNDS)) {
      router.push("/process?task=ps2");
    } else if (isInside(lat, lon, PS10_BOUNDS)) {
      router.push("/process?task=ps10");
    } else {
      setMessage("Click a highlighted scene box to process it.");
      setTimeout(() => setMessage(null), 3000);
    }
  };

  return (
    <div className="relative h-full w-full bg-black">
      {/* Top title bar — padded to clear the zoom control */}
      <div className="absolute top-0 left-0 right-0 z-[1000] bg-gradient-to-b from-black/80 to-transparent px-6 py-4 pl-20 pointer-events-none">
        <h1 className="text-white text-xl font-bold tracking-tight">TerraVis</h1>
        <p className="text-white/70 text-sm">Satellite cloud removal & IR colorization, powered by GenAI</p>
      </div>

      <MapContainer
        center={MAP_CENTER}
        zoom={8}
        minZoom={3}
        maxZoom={16}
        maxBounds={[[-85, -180], [85, 180]]}
        maxBoundsViscosity={1.0}
        worldCopyJump={false}
        className="h-full w-full"
      >
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution="Basemap &copy; Esri | Sentinel-2 &amp; Landsat via Copernicus / Planetary Computer"
          maxNativeZoom={16}
          noWrap={true}
        />

        <TileLayer
          url={`https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=${OWM_API_KEY}`}
          attribution="Live clouds &copy; OpenWeatherMap"
          opacity={0.4}
          zIndex={500}
        />

        <ImageOverlay
          url="/scene_overlay.png"
          bounds={PS2_BOUNDS}
          opacity={hoveringPS2 ? 1 : 0.92}
          eventHandlers={{
            mouseover: () => setHoveringPS2(true),
            mouseout: () => setHoveringPS2(false),
            click: () => router.push("/process?task=ps2"),
          }}
        />

        <ClickHandler onClick={handleMapClick} />
      </MapContainer>

      {/* Legend panel, bottom-left */}
      <div className="absolute bottom-6 left-6 z-[1000] rounded-xl bg-black/85 backdrop-blur px-5 py-4 text-white shadow-2xl max-w-sm">
        <div className="flex items-center gap-2 mb-1">
          <span className="h-2 w-2 rounded-full bg-blue-400" />
          <span className="font-semibold text-sm">Sentinel-2 — Odisha, India</span>
        </div>
        <div className="text-xs text-white/60 pl-4">Captured Dec 7, 2024 · 62% cloud cover · Tile T45QUC</div>

        <div className="flex gap-2 mt-4">
          <button
            className="flex-1 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 transition"
            onClick={() => router.push("/process?task=ps2")}
          >
            Cloud Removal (PS2)
          </button>
          <button
            className="flex-1 rounded-lg bg-purple-600 px-3 py-2 text-sm font-medium text-white hover:bg-purple-700 transition"
            onClick={() => router.push("/process?task=ps10")}
          >
            IR Colorize (PS10)
          </button>
        </div>
      </div>

      {message && (
        <div className="absolute top-28 left-1/2 -translate-x-1/2 z-[1000] rounded-lg bg-black/85 px-4 py-2 text-white shadow-lg text-sm">
          {message}
        </div>
      )}
    </div>
  );
}