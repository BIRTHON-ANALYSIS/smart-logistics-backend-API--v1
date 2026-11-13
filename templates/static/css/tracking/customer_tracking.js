(() => {
  const root = document.getElementById("shipment-tracking");
  if (!root) return;

  const trackingNumber = root.dataset.trackingNumber;
  const mapElement = document.getElementById("tracking-map");
  const statusElement = document.getElementById("tracking-status");

  if (!trackingNumber || !mapElement || !statusElement) {
    console.error("Tracking page is missing required elements.");
    return;
  }

  const map = L.map(mapElement).setView([9.082, 8.675], 6);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  let driverMarker = null;
  let socket = null;

  function showStatus(text) {
    statusElement.textContent = text;
  }

  function showLocation(location) {
    const latitude = Number(location.latitude);
    const longitude = Number(location.longitude);

    if (
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude) ||
      latitude < -90 ||
      latitude > 90 ||
      longitude < -180 ||
      longitude > 180
    ) {
      showStatus("Received an invalid location.");
      return;
    }

    const point = [latitude, longitude];

    if (!driverMarker) {
      driverMarker = L.marker(point).addTo(map);
      driverMarker.bindPopup("Driver's latest location");
    } else {
      driverMarker.setLatLng(point);
    }

    map.setView(point, 15);
    showStatus(`Last location update: ${location.recorded_at || "just now"}`);
  }

  function connect() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const url =
      `${protocol}//${window.location.host}/ws/shipments/` +
      `${encodeURIComponent(trackingNumber)}/`;

    socket = new WebSocket(url);

    socket.addEventListener("open", () => {
      showStatus("Connected. Waiting for tracking data…");
    });

    socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);

      if (message.type === "tracking_snapshot") {
        const shipment = message.shipment;

        showStatus(`Shipment status: ${shipment.status}`);

        if (shipment.current_location) {
          showLocation(shipment.current_location);
        } else {
          showStatus("Connected. Waiting for the driver's first location.");
        }
      }

      if (message.type === "location_updated") {
        showLocation(message.location);
      }

      if (message.type === "shipment_status_changed") {
        showStatus(`Shipment status: ${message.shipment.status}`);
      }

      if (message.type === "error") {
        showStatus(message.message);
      }
    });

    socket.addEventListener("close", () => {
      showStatus("Tracking connection closed.");
    });

    socket.addEventListener("error", () => {
      showStatus("Tracking connection error.");
    });
  }

  connect();

let reconnectTimer = null;
let reconnectDelay = 1000;
let manuallyClosed = false;

function connect() {
  if (manuallyClosed) return;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const url =
    `${protocol}//${window.location.host}/ws/shipments/` +
    `${encodeURIComponent(trackingNumber)}/`;

  socket = new WebSocket(url);

  socket.addEventListener("open", () => {
    reconnectDelay = 1000;
    showStatus("Connected. Waiting for tracking data…");
  });

  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);

    if (message.type === "tracking_snapshot") {
      const shipment = message.shipment;
      showStatus(`Shipment status: ${shipment.status}`);

      if (shipment.current_location) {
        showLocation(shipment.current_location);
      } else {
        showStatus("Connected. Waiting for the driver's first location.");
      }
    } else if (message.type === "location_updated") {
      showLocation(message.location);
    } else if (message.type === "shipment_status_changed") {
      showStatus(`Shipment status: ${message.shipment.status}`);
    } else if (message.type === "error") {
      showStatus(message.message);
    }
  });

  socket.addEventListener("close", () => {
    if (manuallyClosed) return;

    showStatus("Connection lost. Reconnecting…");
    clearTimeout(reconnectTimer);

    reconnectTimer = setTimeout(() => {
      connect();
      reconnectDelay = Math.min(reconnectDelay * 2, 30000);
    }, reconnectDelay);
  });

  socket.addEventListener("error", () => {
    showStatus("Tracking connection error.");
    socket.close();
  });
}

function stopTracking() {
  manuallyClosed = true;
  clearTimeout(reconnectTimer);

  if (socket && socket.readyState < WebSocket.CLOSING) {
    socket.close();
  }
}

window.addEventListener("pagehide", stopTracking);
connect();
})();