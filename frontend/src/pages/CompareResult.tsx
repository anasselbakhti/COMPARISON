import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import type { Product } from "../types/product";
import CompareTable from "../components/CompareTable";
import API from "../services/api";

export default function CompareResult() {
  const location = useLocation();
  const navigate = useNavigate();
  const products: Product[] = (location.state && (location.state as any).products) || [];
  const [aiComment, setAiComment] = useState<string | null>(null);
  const [loadingAi, setLoadingAi] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const fetchAiComment = async () => {
    setAiError(null);
    setAiComment(null);
    setLoadingAi(true);
    try {
      const res = await API.post("ai/compare/", { products });
      setAiComment(res.data.comment || "");
    } catch (e: any) {
      console.error(e);
      setAiError(e?.response?.data?.error || e.message || String(e));
    } finally {
      setLoadingAi(false);
    }
  };
  

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <h1 style={{ margin: 0 }}>Résultat de la comparaison</h1>
        <div>
          <button
            onClick={() => navigate(-1)}
            style={{ marginRight: 8, padding: '8px 12px', borderRadius: 6 }}
          >
            ← Retour
          </button>
          <button
            onClick={fetchAiComment}
            disabled={loadingAi}
            style={{ padding: '8px 12px', borderRadius: 6, background: '#2563eb', color: '#fff', border: 'none', cursor: 'pointer' }}
          >
            {loadingAi ? 'Génération IA...' : 'Obtenir un avis IA'}
          </button>
        </div>
      </div>

      {aiError && <div style={{ marginTop: 12, color: "#b91c1c" }}>{aiError}</div>}
      {aiComment && (
        <div style={{ marginTop: 12, padding: 16, background: '#fff', border: '1px solid #e6edf8', borderRadius: 8 }}>
          <h3 style={{ margin: '0 0 8px 0' }}>Avis de l'IA</h3>
          <p style={{ margin: 0, lineHeight: 1.6, color: '#1f2937' }}>{aiComment}</p>
        </div>
      )}

      {products.length === 0 ? (
        <div>
          <p>Aucun produit reçu pour la comparaison. Retournez à la page de comparaison et sélectionnez au moins 2 produits.</p>
        </div>
      ) : (
        <div>
          <CompareTable products={products} />
        </div>
      )}
    </div>
  );
}
