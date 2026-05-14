import React, { useEffect, useMemo, useState } from "react";
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
      return matchesName && matchesCategory && matchesMinPrice && matchesMaxPrice;
    });
  }, [allProducts, searchTerm, category, minPrice, maxPrice]);

  const handleProductSelect = (product: Product, checked: boolean) => {
    if (checked) {
      if (selectedProducts.length < MAX_SELECTED_PRODUCTS) {
        setSelectedProducts([...selectedProducts, product]);
      }
    } else {
      setSelectedProducts(selectedProducts.filter((p) => p.id !== product.id));
    }
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
              placeholder="Prix min"
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "120px" }}
            />

            <input
              type="number"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              placeholder="Prix max"
              style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", minWidth: "120px" }}
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
              <h2>Résultat de la comparaison</h2>
              <CompareTable products={selectedProducts} />
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
