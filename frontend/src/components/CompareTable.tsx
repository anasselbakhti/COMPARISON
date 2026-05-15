import React from "react";
import type { Product } from "../types/product";

type Props = { products: Product[] };

export default function CompareTable({ products }: Props) {
  if (!products || products.length === 0) {
    return <div>Aucun produit à comparer.</div>;
  }

  const rows: { key: string; label: string; render: (p: Product) => React.ReactNode }[] = [
    { key: "name", label: "Nom", render: (p) => p.name },
    { key: "brand", label: "Marque", render: (p) => p.brand },
    { key: "category", label: "Catégorie", render: (p) => p.category },
    { key: "price", label: "Prix (MAD)", render: (p) => p.price },
    { key: "os", label: "OS", render: (p) => p.specs?.os || "—" },
    { key: "ram", label: "RAM (Go)", render: (p) => p.specs?.ram_gb ?? "—" },
    { key: "storage", label: "Stockage (Go)", render: (p) => p.specs?.storage_gb ?? "—" },
    { key: "cpu", label: "CPU", render: (p) => p.specs?.cpu || "—" },
    { key: "gpu", label: "GPU", render: (p) => p.specs?.gpu || "—" },
    { key: "release", label: "Année", render: (p) => p.specs?.release_year ?? p.specs?.year_release ?? "—" },
    { key: "rating", label: "Note moyenne", render: (p) => p.avg_rating ?? "—" },
  ];

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 600 }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #ddd" }}></th>
            {products.map((p) => (
              <th key={p.id} style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #ddd" }}>{p.name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.key}>
              <td style={{ padding: 8, fontWeight: 700, verticalAlign: "top", borderBottom: "1px solid #f0f0f0" }}>{row.label}</td>
              {products.map((p) => (
                <td key={p.id + row.key} style={{ padding: 8, verticalAlign: "top", borderBottom: "1px solid #f8f8f8" }}>{row.render(p)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
