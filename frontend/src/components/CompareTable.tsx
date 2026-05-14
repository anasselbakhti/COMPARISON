import type { Product } from "../types/product";

interface CompareTableProps {
  products?: Product[];
}

function CompareTable({ products = [] }: CompareTableProps) {
  if (products.length === 0) {
    return <p>Aucun produit sélectionné pour la comparaison</p>;
  }

  const getSpecValue = (product: Product, specKey: string) => {
    if (!product.specs) return "N/A";

    switch (specKey) {
      case "ram": return product.specs.ram_gb ?? null;
      case "storage": return product.specs.storage_gb ?? null;
      case "cpu": return product.specs.cpu || null;
      case "gpu": return product.specs.gpu || null;
      case "battery": return product.specs.battery_mah ?? product.specs.battery_wh ?? null;
      case "screen": return product.specs.screen_in ?? null;
      case "os": return product.specs.os || null;
      case "camera": return product.specs.camera_mp ?? null;
      case "network": return product.specs.network || null;
      case "weight": return product.specs.weight_kg ?? null;
      default: return null;
    }
  };

  const renderSpecValue = (product: Product, specKey: string) => {
    const value = getSpecValue(product, specKey);
    if (value === null || value === undefined || value === "") return "N/A";
    switch (specKey) {
      case "ram":
      case "storage":
        return `${value} GB`;
      case "battery":
        return typeof value === "number" && value > 1000 ? `${value} mAh` : `${value} Wh`;
      case "screen":
        return `${value}"`;
      case "camera":
        return `${value} MP`;
      case "weight":
        return `${value} kg`;
      default:
        return `${value}`;
    }
  };

  const numericValue = (product: Product, specKey: string) => {
    const value = getSpecValue(product, specKey);
    if (value === null || value === undefined || value === "") return null;
    if (typeof value === "number") return value;
    if (typeof value === "string") {
      const parsed = parseFloat(value.replace(/[^0-9.]/g, ""));
      return Number.isNaN(parsed) ? null : parsed;
    }
    return null;
  };

  const bestValues: Record<string, number | null> = {
    price: null,
    ram: null,
    storage: null,
    battery: null,
    screen: null,
    weight: null,
  };

  products.forEach((product) => {
    const price = Number(product.price);
    if (!Number.isNaN(price)) {
      bestValues.price = bestValues.price === null ? price : Math.min(bestValues.price, price);
    }

    ["ram", "storage", "battery", "screen"].forEach((key) => {
      const value = numericValue(product, key);
      if (value !== null) {
        bestValues[key] = bestValues[key] === null ? value : Math.max(bestValues[key] as number, value);
      }
    });

    const weightValue = numericValue(product, "weight");
    if (weightValue !== null) {
      bestValues.weight = bestValues.weight === null ? weightValue : Math.min(bestValues.weight, weightValue);
    }
  });

  const isBestValue = (product: Product, specKey: string) => {
    const value = numericValue(product, specKey);
    if (value === null) return false;
    const best = bestValues[specKey];
    return best !== null && value === best;
  };

  const sections = [
    {
      title: "Performance",
      rows: [
        { key: "cpu", label: "Processeur" },
        { key: "ram", label: "RAM" },
        { key: "gpu", label: "Carte Graphique" }
      ]
    },
    {
      title: "Affichage",
      rows: [
        { key: "screen", label: "Écran" },
        { key: "weight", label: "Poids" }
      ]
    },
    {
      title: "Connectivité",
      rows: [
        { key: "network", label: "Réseau" },
        { key: "os", label: "Système" }
      ]
    },
    {
      title: "Autonomie",
      rows: [
        { key: "battery", label: "Batterie" }
      ]
    }
  ];

  const priceRow = {
    key: "price",
    label: "Prix (MAD)"
  };

  const ratingRow = {
    key: "rating",
    label: "Note moyenne"
  };

  const hasRating = products.some((product) => product.avg_rating && product.avg_rating > 0);

  return (
    <div style={{ overflowX: "auto", marginTop: "20px" }}>
      <table style={{
        width: "100%",
        borderCollapse: "collapse",
        border: "1px solid #ddd",
        fontSize: "14px"
      }}>
        <thead>
          <tr style={{ backgroundColor: "#f8f9fa" }}>
            <th style={{ padding: "12px", border: "1px solid #ddd", textAlign: "left", minWidth: "200px" }}>
              Caractéristique
            </th>
            {products.map((product, index) => (
              <th key={product.id} style={{
                padding: "12px",
                border: "1px solid #ddd",
                textAlign: "center",
                minWidth: "150px",
                backgroundColor: index % 2 === 0 ? "#e9ecef" : "#f8f9fa"
              }}>
                <div style={{ fontWeight: "bold", marginBottom: "5px" }}>
                  {product.brand}
                </div>
                <div style={{ fontSize: "12px", color: "#666" }}>
                  {product.name.length > 30 ? product.name.substring(0, 30) + "..." : product.name}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style={{ padding: "12px", border: "1px solid #ddd", fontWeight: "bold", backgroundColor: "#fff3cd" }}>
              {priceRow.label}
            </td>
            {products.map((product, index) => {
              const highlight = isBestValue(product, priceRow.key);
              return (
                <td key={product.id} style={{
                  padding: "12px",
                  border: "1px solid #ddd",
                  textAlign: "center",
                  fontWeight: "bold",
                  backgroundColor: highlight ? "#d4edda" : index % 2 === 0 ? "#f8f9fa" : "#ffffff"
                }}>
                  {product.price}
                </td>
              );
            })}
          </tr>

          {hasRating && (
            <tr>
              <td style={{ padding: "12px", border: "1px solid #ddd", fontWeight: "bold", backgroundColor: "#fff3cd" }}>
                {ratingRow.label}
              </td>
              {products.map((product, index) => (
                <td key={product.id} style={{
                  padding: "12px",
                  border: "1px solid #ddd",
                  textAlign: "center",
                  backgroundColor: index % 2 === 0 ? "#f8f9fa" : "#ffffff"
                }}>
                  {product.avg_rating && product.avg_rating > 0 ? `⭐ ${product.avg_rating}/5` : "N/A"}
                </td>
              ))}
            </tr>
          )}

          {sections.map((section) => (
            <>
              <tr>
                <td colSpan={products.length + 1} style={{
                  padding: "12px",
                  border: "1px solid #ddd",
                  backgroundColor: "#e9f7ff",
                  fontWeight: "bold",
                  color: "#155724"
                }}>
                  {section.title}
                </td>
              </tr>
              {section.rows.map((row) => (
                <tr key={row.key}>
                  <td style={{ padding: "12px", border: "1px solid #ddd", fontWeight: "bold" }}>
                    {row.label}
                  </td>
                  {products.map((product, index) => {
                    const highlight = isBestValue(product, row.key);
                    return (
                      <td key={product.id} style={{
                        padding: "12px",
                        border: "1px solid #ddd",
                        textAlign: "center",
                        backgroundColor: highlight ? "#d4edda" : index % 2 === 0 ? "#f8f9fa" : "#ffffff",
                        fontWeight: highlight ? "700" : "400"
                      }}>
                        {renderSpecValue(product, row.key)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </>
          ))}

          <tr>
            <td style={{ padding: "12px", border: "1px solid #ddd", fontWeight: "bold", backgroundColor: "#fff3cd" }}>
              Lien
            </td>
            {products.map((product, index) => (
              <td key={product.id} style={{
                padding: "12px",
                border: "1px solid #ddd",
                textAlign: "center",
                backgroundColor: index % 2 === 0 ? "#f8f9fa" : "#ffffff"
              }}>
                {product.source_url ? (
                  <a
                    href={product.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "#007bff", textDecoration: "none" }}
                  >
                    Voir le produit
                  </a>
                ) : (
                  "N/A"
                )}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default CompareTable;