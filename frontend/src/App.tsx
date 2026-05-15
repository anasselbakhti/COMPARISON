import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Products from "./pages/Products";
import Compare from "./pages/Compare";
import CompareResult from "./pages/CompareResult";
import ProductDetail from "./pages/ProductDetail";
import "./App.css";

function App() {
  return (
    <>
      <Navbar />

      <div className="app-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/product/:id" element={<ProductDetail />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/compare/result" element={<CompareResult />} />
        </Routes>
      </div>
    </>
  );
}

export default App;