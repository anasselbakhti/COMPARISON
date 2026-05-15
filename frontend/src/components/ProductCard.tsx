import React from "react";
import type { Product } from "../types/product";
import "./ProductCard.css";

interface Props {
  product: Product;
}

const ProductCard: React.FC<Props> = ({ product }) => (
  <div className="product-card">
    <h2>{product.name}</h2>
    <p>Marque : {product.brand}</p>
    <p>Catégorie : {product.category}</p>
    {product.specs && (
      <div className="specs">
        {product.specs.ram_gb && <p>RAM : {product.specs.ram_gb}GB</p>}
        {product.specs.storage_gb && <p>Stockage : {product.specs.storage_gb}GB</p>}
        {product.specs.cpu && <p>CPU : {product.specs.cpu}</p>}
        {product.specs.gpu && <p>GPU : {product.specs.gpu}</p>}
        {product.specs.camera_mp && <p>Caméra : {product.specs.camera_mp}MP</p>}
        {product.specs.battery_mah && <p>Batterie : {product.specs.battery_mah}mAh</p>}
        {product.specs.battery_wh && <p>Batterie : {product.specs.battery_wh}Wh</p>}
      </div>
    )}
    <p className="price">
      <strong>Prix : {product.price} MAD</strong>
    </p>
    {product.avg_rating && product.avg_rating > 0 && (
      <p className="rating">⭐ {product.avg_rating}/5</p>
    )}
    {product.source_url && (
      <a href={product.source_url} target="_blank" rel="noopener noreferrer">Voir sur le site</a>
    )}
  </div>
);

export default ProductCard;
