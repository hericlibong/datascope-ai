import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "@/pages/Home";
import About from "@/pages/About";
import { Layout } from "@/components/Layout";

export default function App() {
  return (
    <Router>
      <Layout>
        <nav className="mb-4 flex gap-6">
          <Link to="/" className="text-blue-800 font-semibold">Accueil</Link>
          <Link to="/about" className="text-blue-800 font-semibold">À propos</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Layout>
    </Router>
  );
}
