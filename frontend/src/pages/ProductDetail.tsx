import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../services/api";
import type { Product } from "../types/product";
import "../pages/ProductDetail.css";

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError("ID du produit manquant");
      setLoading(false);
      return;
    }

    API.get(`products/${id}/`)
      .then((res) => {
        setProduct(res.data);
        setLoading(false);

        // Si certaines specs sont manquantes, appeler l'endpoint de scraping à la demande
        (async function fetchDetailsIfNeeded(p: Product) {
          try {
            if (!p) return;
            const specs = p.specs || {};
            let needFetch = false;

            if (p.category === 'smartphone') {
              // si RAM, stockage, batterie ou caméra manquants
              if (!specs.ram_gb || !specs.storage_gb || !specs.battery_mah || !specs.camera_mp) {
                needFetch = true;
              }
            }

            if (p.category === 'laptop') {
              // si RAM, stockage, battery_wh ou poids manquants
              if (!specs.ram_gb || !specs.storage_gb || !specs.battery_wh || !specs.weight_kg) {
                needFetch = true;
              }
            }

            if (needFetch) {
              const endpoint = p.category === 'smartphone' ? `smartphones/${p.id}/fetch_details/` : `laptops/${p.id}/fetch_details/`;
              try {
                const r = await API.post(endpoint);
                // API returns the serialized product
                setProduct(r.data);
              } catch (err) {
                console.warn('Impossible de récupérer les détails du produit:', err);
              }
            }
          } catch (err) {
            console.warn('Erreur lors du check fetch details:', err);
          }
        })(res.data as Product);
      })
      .catch((err) => {
        console.error("Error fetching product:", err);
        setError("Erreur lors du chargement du produit");
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return <div style={{ padding: "20px", textAlign: "center" }}>Chargement...</div>;
  }

  if (error) {
    return <div style={{ padding: "20px", color: "red" }}>{error}</div>;
  }

  if (!product) {
    return <div style={{ padding: "20px" }}>Produit non trouvé</div>;
  }

  const specs = product.specs || {};

  return (
    <div className="product-detail-container">
      <button onClick={() => navigate(-1)} className="btn-back">
        ← Retour
      </button>

      <div className="product-detail-content">
        {/* Header Section */}
        <div className="product-header">
          <div className="product-title-section">
            <h1>{product.name}</h1>
            <p className="product-brand">{product.brand}</p>
            <p className="product-category">
              {product.category === "smartphone" ? "📱 Smartphone" : "💻 Laptop"}
            </p>
          </div>

          <div className="product-price-section">
            <div className="price-tag">{product.price} MAD</div>
            {product.avg_rating ? (
              <div className="rating">
                ⭐ {product.avg_rating.toFixed(1)}/5
              </div>
            ) : (
              <div className="rating">⭐ Aucun avis</div>
            )}
          </div>
        </div>

        {/* Source URL */}
        {product.source_url && (
          <div className="source-section">
            <a href={product.source_url} target="_blank" rel="noopener noreferrer" className="btn-source">
              🔗 Voir sur Jumia
            </a>
          </div>
        )}

        {/* Specs Section */}
        <div className="specs-grid">
          {/* Performance */}
          <section className="spec-section">
            <h2>⚙️ Performance</h2>
            <div className="spec-items">
              {specs.cpu && (
                <div className="spec-item">
                  <span className="spec-label">Processeur</span>
                  <span className="spec-value">{specs.cpu}</span>
                </div>
              )}
              {specs.ram_gb && (
                <div className="spec-item">
                  <span className="spec-label">RAM</span>
                  <span className="spec-value">{specs.ram_gb} Go</span>
                </div>
              )}
              {specs.gpu && (
                <div className="spec-item">
                  <span className="spec-label">GPU</span>
                  <span className="spec-value">{specs.gpu}</span>
                </div>
              )}
            </div>
          </section>

          {/* Storage & Display */}
          <section className="spec-section">
            <h2>💾 Stockage & Affichage</h2>
            <div className="spec-items">
              {specs.storage_gb && (
                <div className="spec-item">
                  <span className="spec-label">Stockage</span>
                  <span className="spec-value">{specs.storage_gb} Go</span>
                </div>
              )}
              {specs.screen_in && (
                <div className="spec-item">
                  <span className="spec-label">Écran</span>
                  <span className="spec-value">{specs.screen_in}"</span>
                </div>
              )}
            </div>
          </section>

          {/* Connectivity */}
          <section className="spec-section">
            <h2>🌐 Connectivité</h2>
            <div className="spec-items">
              {specs.os && (
                <div className="spec-item">
                  <span className="spec-label">Système d'exploitation</span>
                  <span className="spec-value">{specs.os}</span>
                </div>
              )}
              {specs.network && (
                <div className="spec-item">
                  <span className="spec-label">Réseau</span>
                  <span className="spec-value">{specs.network}</span>
                </div>
              )}
            </div>
          </section>

          {/* Battery & Size */}
          <section className="spec-section">
            <h2>🔋 Batterie & Dimensions</h2>
            <div className="spec-items">
              {specs.battery_mah && (
                <div className="spec-item">
                  <span className="spec-label">Batterie</span>
                  <span className="spec-value">{specs.battery_mah} mAh</span>
                </div>
              )}
              {specs.battery_wh && (
                <div className="spec-item">
                  <span className="spec-label">Batterie</span>
                  <span className="spec-value">{specs.battery_wh} Wh</span>
                </div>
              )}
              {specs.weight_kg && (
                <div className="spec-item">
                  <span className="spec-label">Poids</span>
                  <span className="spec-value">{specs.weight_kg} kg</span>
                </div>
              )}
            </div>
          </section>

          {/* Camera */}
          {specs.camera_mp && (
            <section className="spec-section">
              <h2>📷 Caméra</h2>
              <div className="spec-items">
                <div className="spec-item">
                  <span className="spec-label">Caméra arrière</span>
                  <span className="spec-value">{specs.camera_mp} MP</span>
                </div>
              </div>
            </section>
          )}

          {/* Year Release */}
          {specs.year_release && (
            <section className="spec-section">
              <h2>📅 Informations</h2>
              <div className="spec-items">
                <div className="spec-item">
                  <span className="spec-label">Année de sortie</span>
                  <span className="spec-value">{specs.year_release}</span>
                </div>
              </div>
            </section>
          )}
        </div>

        {/* Last Updated */}
        {product.updated_at && (
          <div className="metadata">
            <small>Mis à jour: {new Date(product.updated_at).toLocaleDateString("fr-FR")}</small>
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          <button onClick={() => navigate("/compare")} className="btn-compare">
            🔄 Comparer ce produit
          </button>
          <button onClick={() => navigate("/products")} className="btn-back-to-products">
            ← Retour au catalogue
          </button>
        </div>
      </div>
    </div>
  );
}
