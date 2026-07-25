"use client";

import dynamic from "next/dynamic";

// Leaflet needs the browser's `window` object — dynamic import with ssr:false
// avoids Next.js trying to render it on the server, which would crash
const MapView = dynamic(() => import("../components/MapView"), { ssr: false });

export default function Home() {
  return (
    <main className="h-screen w-screen">
      <MapView />
    </main>
  );
}