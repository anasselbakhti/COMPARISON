import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

const Navbar: React.FC = () => (
  <nav className="navbar">
    <Link to="/">Accueil</Link> | <Link to="/products">Produits</Link> | <Link to="/compare">Comparer</Link>
  </nav>
);

export default Navbar;
