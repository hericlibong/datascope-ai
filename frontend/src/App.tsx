import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import Home from "@/pages/Home"
import About from "@/pages/About"
import AnalyzePage from "@/pages/AnalyzePage"
import { Layout } from "@/components/Layout"

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/analyze" element={<AnalyzePage />} />
        </Routes>
      </Layout>
    </Router>
  )
}
