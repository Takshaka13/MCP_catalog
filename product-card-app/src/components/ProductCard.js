import React from 'react';
import './ProductCard.css';

const ProductCard = ({ product }) => {
  return (
    <div className="product-card">
      <div className="product-image">
        <img src={product.imageUrl} alt={product.name} />
      </div>
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-developer">Developer: {product.developer}</p>
        <p className="product-price">${product.price.toFixed(2)}</p>
        <p className="product-description">{product.description}</p>
        <div className="product-details">
          <p>Room Type: {product.roomType}</p>
          <p>Room Number: {product.roomNumber}</p>
          <p>Block: {product.block}</p>
          <p>Area: {product.sqM} m²</p>
        </div>
        <div className="product-actions">
          <button className="add-to-cart">Add to Cart</button>
          <button className="view-details">View Details</button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard; 