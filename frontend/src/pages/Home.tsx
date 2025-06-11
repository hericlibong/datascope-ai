import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"

export default function Home() {
  return (
    <div className="w-full text-center space-y-6 mt-10">
      <h2 className="text-2xl font-bold">Analyse ton article avec DataScope</h2>

      {/* Bouton vers l’analyse */}
      <Link to="/analyze">
        <Button className="mt-4">Commencer une analyse</Button>
      </Link>

      {/* Lien texte vers la page "À propos" */}
      <div className="mt-6">
        <Link to="/about" className="text-sm text-blue-600 hover:underline">
          En savoir plus sur DataScope →
        </Link>
      </div>
    </div>
  )
}
