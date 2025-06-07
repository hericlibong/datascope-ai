import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

function App() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-blue-100">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Bienvenue sur DataScope</CardTitle>
          <CardDescription>
            Ceci est un exemple de carte Shadcn UI.<br />
            Tu peux la personnaliser à volonté.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>
            Ajoute ici n'importe quel contenu : texte, formulaire, infos, etc.<br />
            <strong>C'est le composant CardContent !</strong>
          </p>
        </CardContent>
        <CardFooter>
          <Button>Découvrir</Button>
        </CardFooter>
      </Card>
    </div>
  );
}

export default App;
