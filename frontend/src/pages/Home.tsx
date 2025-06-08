import { AnalysisForm } from "@/components/AnalysisForm";

export default function Home() {
  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold mb-6">Analyse ton article avec DataScope</h2>
      <AnalysisForm />
    </div>
  );
}
