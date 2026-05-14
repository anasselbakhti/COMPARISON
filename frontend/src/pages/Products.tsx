import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import type { Product } from "../types/product";

export default function Products() {
  const navigate = useNavigate();
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [category, setCategory] = useState("all");
  const [brand, setBrand] = useState("all");
  const [ramMin, setRamMin] = useState("");
  const [ramMax, setRamMax] = useState("");
  const [os, setOs] = useState("all");
  const [yearMin, setYearMin] = useState("");
  const [yearMax, setYearMax] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    API.get("products/")
      .then((res) => {
        const products = res.data.results || res.data;
        setAllProducts(products);
        setLoading(false);
      })
      .catch((err) => {
        console.error("API Error:", err);
        setError("Erreur lors du chargement des produits");
        setLoading(false);
      });
  }, []);

  const uniqueBrands = useMemo(() => {
    return Array.from(new Set(allProducts.map((p) => p.brand))).sort();
  }, [allProducts]);

  const uniqueOS = useMemo(() => {
    return Array.from(new Set(allProducts.map((p) => p.specs?.os).filter((o) => o))).sort();
  }, [allProducts]);

  const filteredProducts = useMemo(() => {
    return allProducts.filter((product) => {
      const matchesName = product.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = category === "all" || product.category === category;
      const matchesBrand = brand === "all" || product.brand === brand;
      const matchesOS = os === "all" || product.specs?.os === os;
      const matchesPriceMin = priceMin === "" || Number(product.price) >= parseFloat(priceMin);
      const matchesPriceMax = priceMax === "" || Number(product.price) <= parseFloat(priceMax);
      const matchesRamMin = ramMin === "" || (product.specs?.ram_gb ?? 0) >= parseInt(ramMin);
      const matchesRamMax = ramMax === "" || (product.specs?.ram_gb ?? 0) <= parseInt(ramMax);
      const matchesYearMin = yearMin === "" || (product.specs?.year_release ?? 2024) >= parseInt(yearMin);
      const matchesYearMax = yearMax === "" || (product.specs?.year_release ?? 2024) <= parseInt(yearMax);

      return (
        matchesName &&
        matchesCategory &&
        matchesBrand &&
        matchesOS &&
        matchesPriceMin &&
        matchesPriceMax &&
        matchesRamMin &&
        matchesRamMax &&
        matchesYearMin &&
        matchesYearMax
      );
    });
  }, [allProducts, searchTerm, category, brand, os, priceMin, priceMax, ramMin, ramMax, yearMin, yearMax]);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Produits</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "10px", marginBottom: "20px" }}>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Recherche par nom"
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
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

        <select
          value={brand}
          onChange={(e) => setBrand(e.target.value)}
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        >
          <option value="all">Toutes les marques</option>
          {uniqueBrands.map((b) => (
            <option key={b} value={b}>
              {b}
            </option>
          ))}
        </select>

        <select
          value={os}
          onChange={(e) => setOs(e.target.value)}
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        >
          <option value="all">Tous les OS</option>
          {uniqueOS.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>

        <input
          type="number"
          value={ramMin}
          onChange={(e) => setRamMin(e.target.value)}
          placeholder="RAM min (Go)"
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        />

        <input
          type="number"
          value={ramMax}
          onChange={(e) => setRamMax(e.target.value)}
          placeholder="RAM max (Go)"
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        />

        <input
          type="number"
          value={priceMin}
          onChange={(e) => setPriceMin(e.target.value)}
          placeholder="Prix min"
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        />

        <input
          type="number"
          value={priceMax}
          onChange={(e) => setPriceMax(e.target.value)}
          placeholder="Prix max"
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        />

        <input
          type="number"
          value={yearMin}
          onChange={(e) => setYearMin(e.target.value)}
          placeholder="Année min"
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        />

        <input
          type="number"
          value={yearMax}
          onChange={(e) => setYearMax(e.target.value)}
          placeholder="Année max"
          style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        />
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {loading ? (
        <p>Chargement...</p>
      ) : (
        <div>
          <p style={{ fontWeight: 600 }}>{filteredProducts.length} produit(s) trouvé(s)</p>
          <ul style={{ padding: 0, listStyle: "none" }}>
            {filteredProducts.map((product) => (
              <li
                key={product.id}
                onClick={() => navigate(`/product/${product.id}`)}
                style={{
                  padding: "12px",
                  borderBottom: "1px solid #eee",
                  display: "grid",
                  gridTemplateColumns: "1fr auto",
                  gap: "20px",
                  alignItems: "center",
                  backgroundColor: "#f9f9f9",
                  marginBottom: "8px",
                  borderRadius: "5px",
                  cursor: "pointer",
                  transition: "all 0.3s",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "#e8f4f8";
                  e.currentTarget.style.transform = "translateX(4px)";
                  e.currentTarget.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.1)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = "#f9f9f9";
                  e.currentTarget.style.transform = "translateX(0)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                <div>
                  <div style={{ fontWeight: 600 }}>{product.name}</div>
                  <div style={{ fontSize: "13px", color: "#555" }}>
                    {product.brand} • {product.category} {product.specs?.os && `• ${product.specs.os}`}
                  </div>
                </div>
                <div style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                  <div style={{ fontWeight: 600, color: "#28a745" }}>{product.price} MAD</div>
                  {product.specs?.ram_gb && <div style={{ fontSize: "12px", color: "#666" }}>{product.specs.ram_gb} Go RAM</div>}
                </div>
              </li>
            ))}
          </ul>
          {filteredProducts.length === 0 && <p>Aucun produit ne correspond aux filtres.</p>}
        </div>
      )}
    </div>
  );
}