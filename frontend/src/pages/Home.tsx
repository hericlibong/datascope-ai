import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="w-full text-center space-y-6 mt-10">
      <h2 className="text-2xl font-bold">Analyse ton article avec DataScope</h2>
      <Link to="/login">
        <Button className="mt-4">Commencer une analyse</Button>
      </Link>
    </div>
  );
}
