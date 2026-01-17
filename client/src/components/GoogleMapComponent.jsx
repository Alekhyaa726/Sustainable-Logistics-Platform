import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix for default Leaflet marker icons not showing up in React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const GoogleMapComponent = ({ routeData }) => {
  // --- MODIFIED: Default to Bengaluru Warehouse Coordinates ---
  const warehouseCoordinates = [12.9716, 77.5946]; 

  const [routePath, setRoutePath] = useState([warehouseCoordinates]);
  const [orders, setOrders] = useState([]); 

  useEffect(() => {
    if (routeData?.full_route) {
      // Backend sends tuples (lat, lon), which JSON converts to arrays [lat, lon].
      // Leaflet loves arrays, so we use them directly.
      setRoutePath(routeData.full_route);
    }

    if (routeData?.assigned_orders?.length) {
      fetchOrders(routeData.assigned_orders);
    }
    
    if (!routeData) {
      setOrders([]);
      setRoutePath([warehouseCoordinates]);
    }
  }, [routeData]);

  const fetchOrders = async (orderIds) => {
    try {
      const fetchedOrders = await Promise.all(
        orderIds.map(async (id) => {
          // --- MODIFIED: Added slash just in case, though usually optional for IDs ---
          const response = await fetch(`http://127.0.0.1:8000/orders/${id}`);
          return response.json();
        })
      );
      setOrders(fetchedOrders);
    } catch (error) {
      console.error("Error fetching orders:", error);
    }
  };

  return (
    <div>
      {/* --- MODIFIED: Replaced GoogleMap with MapContainer (OpenStreetMap) --- */}
      <MapContainer 
        center={warehouseCoordinates} 
        zoom={13} 
        style={{ width: "100%", height: "70vh" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Route Path (Blue Line) */}
        <Polyline
          positions={routePath}
          pathOptions={{ color: "blue", weight: 4, opacity: 0.8 }}
        />

        {/* Warehouse Marker */}
        <Marker position={warehouseCoordinates}>
          <Popup>
            <div style={{ textAlign: "center" }}>
              <h3 style={{ margin: "0", fontWeight: "bold" }}>Warehouse</h3>
              <p>Bengaluru Hub</p>
            </div>
          </Popup>
        </Marker>

        {/* Orders Markers */}
        {orders.map((order) => {
          const coords = order.delivery_coordinates.split(",").map(Number);
          if (isNaN(coords[0]) || isNaN(coords[1])) return null;

          return (
            <Marker key={order.id} position={coords}>
              <Popup>
                <div style={{ width: "200px" }}>
                  <h3 style={{ margin: "0 0 5px 0", color: "#e67e22" }}>Order: {order.name}</h3>
                  <p style={{ margin: "2px 0" }}><strong>Priority:</strong> {order.priority}</p>
                  <p style={{ margin: "2px 0" }}><strong>Weight:</strong> {order.weight} kg</p>
                  <p style={{ margin: "2px 0" }}><strong>Status:</strong> {order.status}</p>
                  <p style={{ margin: "2px 0" }}><strong>Distance:</strong> {order.delivery_distance} km</p>
                  <p style={{ margin: "2px 0" }}><strong>ETA:</strong> {order.estimate_delivery_time}</p>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Orders List Panel */}
      <div className="p-6 bg-gray-800 rounded-lg shadow-md mt-6">
        <h1 className="text-3xl font-bold text-orange-400 mb-4">Assigned Orders</h1>
        {orders.length === 0 ? (
          <p className="text-gray-300">No orders assigned or routing pending...</p>
        ) : (
          <ul className="space-y-4">
            {orders.map((order) => (
              <li key={order.id} className="bg-gray-700 p-4 rounded-lg shadow-md border-l-4 border-orange-500">
                <div className="flex justify-between items-start">
                    <div>
                        <p className="text-lg font-medium text-white">
                        {order.name}
                        </p>
                        <p className="text-sm text-gray-300">
                        Priority: <span className="text-white">{order.priority}</span>
                        </p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-gray-300">
                        {order.estimate_delivery_time}
                        </p>
                        <p className="text-xs text-gray-400">
                        {order.delivery_distance} km
                        </p>
                    </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default GoogleMapComponent;