import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import CompareTable from "../components/CompareTable";
import type { Product } from "../types/product";

const MAX_SELECTED_PRODUCTS = 4;

const Compare: React.FC = () => {
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filtres
  const [searchTerm, setSearchTerm] = useState("");
  const [category, setCategory] = useState("all");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [minRam, setMinRam] = useState("");
  const [os, setOs] = useState("all");
  const [minYear, setMinYear] = useState("");
  const [maxYear, setMaxYear] = useState("");

  useEffect(() => {
    API.get("products/")
      .then((res) => {
        const products = res.data.results || res.data;
        setAllProducts(products);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Erreur API:", err);
        setError("Erreur lors du chargement des produits");
        setLoading(false);
      });
  }, []);

  const filteredProducts = useMemo(() => {
    return allProducts.filter((product) => {
      const matchesName = product.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = category === "all" || product.category === category;
      const matchesMinPrice = minPrice === "" || Number(product.price) >= parseFloat(minPrice);
      const matchesMaxPrice = maxPrice === "" || Number(product.price) <= parseFloat(maxPrice);
      
      // Filtres RAM
      const matchesMinRam = minRam === "" || (product.specs?.ram_gb || 0) >= parseInt(minRam);
      
      // Filtre OS
      const matchesOs = os === "all" || product.specs?.os?.toLowerCase().includes(os.toLowerCase());
      
      // Filtres Année de sortie (release_year ou year_release)
      const releaseYear = product.specs?.release_year || (product.specs as any)?.year_release;
      const matchesMinYear = minYear === "" || releaseYear >= parseInt(minYear);
      const matchesMaxYear = maxYear === "" || releaseYear <= parseInt(maxYear);
      
      return matchesName && matchesCategory && matchesMinPrice && matchesMaxPrice && 
             matchesMinRam && matchesOs && matchesMinYear && matchesMaxYear;
    });
  }, [allProducts, searchTerm, category, minPrice, maxPrice, minRam, os, minYear, maxYear]);

  const handleProductSelect = (product: Product, checked: boolean) => {
    if (checked) {
      if (selectedProducts.length < MAX_SELECTED_PRODUCTS) {
        setSelectedProducts([...selectedProducts, product]);
      }
    } else {
      setSelectedProducts(selectedProducts.filter((p) => p.id !== product.id));
    }
  };

  const navigate = useNavigate();

  const goToResultPage = () => {
    // Passe la sélection via l'état de navigation
    navigate("/compare/result", { state: { products: selectedProducts } });
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Comparer des produits</h1>

      {error && <p style={{ color: "red" }}>Erreur: {error}</p>}
      {loading && <p>Chargement des produits...</p>}

      {!loading && !error && (
        <div>
          <h2>Sélectionnez 2 à {MAX_SELECTED_PRODUCTS} produits ({selectedProducts.length}/{MAX_SELECTED_PRODUCTS})</h2>

          <div style={{ display: "flex", gap: "10px", marginBottom: "20px", flexWrap: "wrap" }}>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Recherche par nom"
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "220px" }}
            />

            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
            >
              <option value="all">Toutes les catégories</option>
              <option value="smartphone">Smartphone</option>
              <option value="laptop">Laptop</option>
            </select>

            <input
              type="number"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              placeholder="Prix min (MAD)"
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "120px" }}
            />

            <input
              type="number"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              placeholder="Prix max (MAD)"
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "120px" }}
            />

            <input
              type="number"
              value={minRam}
              onChange={(e) => setMinRam(e.target.value)}
              placeholder="RAM min (Go)"
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "120px" }}
            />

            <select
              value={os}
              onChange={(e) => setOs(e.target.value)}
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "140px" }}
            >
              <option value="all">Tous les OS</option>
              <option value="android">Android</option>
              <option value="ios">iOS</option>
              <option value="windows">Windows</option>
              <option value="macos">macOS</option>
              <option value="freertos">FreeDOS</option>
            </select>

            <input
              type="number"
              value={minYear}
              onChange={(e) => setMinYear(e.target.value)}
              placeholder="Année min"
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "100px" }}
            />

            <input
              type="number"
              value={maxYear}
              onChange={(e) => setMaxYear(e.target.value)}
              placeholder="Année max"
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "100px" }}
            />
          </div>

          {filteredProducts.length === 0 ? (
            <p>Aucun produit trouvé</p>
          ) : (
            <div style={{ marginBottom: "30px" }}>
              <p>{filteredProducts.length} produit(s) trouvé(s)</p>
              <ul style={{ padding: 0, listStyle: "none" }}>
                {filteredProducts.map((product) => {
                  const isSelected = selectedProducts.some((p) => p.id === product.id);
                  const isDisabled = !isSelected && selectedProducts.length >= MAX_SELECTED_PRODUCTS;

                  return (
                    <li
                      key={product.id}
                      style={{
                        padding: "10px 0",
                        borderBottom: "1px solid #eee",
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        opacity: isDisabled ? 0.6 : 1
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        disabled={isDisabled}
                        onChange={(e) => handleProductSelect(product, e.target.checked)}
                        style={{ margin: 0 }}
                      />
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600 }}>{product.name}</div>
                        <div style={{ fontSize: "13px", color: "#555" }}>
                          {product.brand} • {product.category} • {product.price} MAD
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          <div style={{ marginBottom: "15px", color: "#555" }}>
            Sélectionnez au moins 2 produits pour afficher le tableau comparatif.
          </div>

          {selectedProducts.length >= 2 ? (
            <div>
              <h2>Produits sélectionnés</h2>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
                {selectedProducts.map((p) => (
                  <div key={p.id} style={{ padding: '8px 10px', borderRadius: 6, background: '#eef2f7', border: '1px solid #d1d5db' }}>
                    {p.brand} — {p.name.substring(0, 40)}{p.name.length > 40 ? '…' : ''}
                  </div>
                ))}
              </div>
              <div>
                <button
                  onClick={goToResultPage}
                  style={{
                    padding: '10px 16px',
                    borderRadius: 8,
                    border: 'none',
                    backgroundColor: '#2b6cb0',
                    color: 'white',
                    cursor: 'pointer',
                  }}
                >
                  Voir la page résultat
                </button>
              </div>
            </div>
          ) : (
            <div style={{ padding: "15px", backgroundColor: "#fff3cd", borderRadius: "8px", border: "1px solid #ffeeba" }}>
              <p style={{ margin: 0 }}>
                Choisissez {2 - selectedProducts.length} produit(s) supplémentaire(s) pour comparer.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Compare;
