import React from 'react';
import './App.css';
import ProductCard from './components/ProductCard';

function App() {
  // Sample product data based on your property catalog schema
  const products = [
    {
      id: 1,
      name: "Luxury Beachfront Condo",
      developer: "Example Developer",
      price: 2500000,
      description: "Beautiful beachfront property with stunning ocean views. Fully furnished with premium amenities.",
      imageUrl: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
      roomType: "1-Bedroom",
      roomNumber: "A101",
      block: "A",
      sqM: "45"
    },
    {
      id: 2,
      name: "Modern City Apartment",
      developer: "Example Developer",
      price: 3500000,
      description: "Spacious apartment in the heart of the city, with easy access to shopping, dining, and entertainment.",
      imageUrl: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
      roomType: "2-Bedroom",
      roomNumber: "B202",
      block: "B",
      sqM: "65"
    },
    {
      id: 3,
      name: "Mountain View Villa",
      developer: "Example Developer",
      price: 4200000,
      description: "Luxurious villa with panoramic mountain views, private garden, and infinity pool.",
      imageUrl: "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
      roomType: "3-Bedroom",
      roomNumber: "C303",
      block: "C",
      sqM: "120"
    }
  ];

  return (
    <div className="App">
      <header className="App-header">
        <h1>Property Catalog</h1>
        <p>Browse our exclusive selection of premium properties</p>
      </header>
      <main className="product-container">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </main>
    </div>
  );
}

export default App;
