import React from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface ResultCardProps {
  children?: React.ReactNode;
  className?: string;
  title?: string;
  language?: "en" | "fr";
  isLoading?: boolean;
  isEmpty?: boolean;
  error?: string;
  icon?: React.ReactNode;
}

export function ResultCard({ 
  children, 
  className, 
  title, 
  language = "en",
  isLoading = false,
  isEmpty = false,
  error,
  icon 
}: ResultCardProps) {
  const t = (en: string, fr: string) => language === "fr" ? fr : en;

  if (error) {
    return (
      <Card className={cn("rounded-2xl border-red-500/20 bg-red-500/5 backdrop-blur-sm", className)}>
        <CardContent className="p-6">
          <div className="text-center text-red-400">
            <p className="font-medium">{t("Error", "Erreur")}</p>
            <p className="text-sm text-red-300 mt-1">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className={cn("rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm", className)}>
        <CardHeader className="pb-4">
          {title && (
            <div className="flex items-center gap-2">
              {icon && <div className="text-slate-400">{icon}</div>}
              <Skeleton className="h-6 w-48" />
            </div>
          )}
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </CardContent>
      </Card>
    );
  }

  if (isEmpty) {
    return (
      <Card className={cn("rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm", className)}>
        <CardHeader className="pb-4">
          {title && (
            <div className="flex items-center gap-2">
              {icon && <div className="text-slate-400">{icon}</div>}
              <h3 className="text-lg font-semibold text-white">{title}</h3>
            </div>
          )}
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-slate-400">
            <p>{t("No data available", "Aucune donnée disponible")}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm", className)}>
      {title && (
        <CardHeader className="pb-4">
          <div className="flex items-center gap-2">
            {icon && <div className="text-slate-400">{icon}</div>}
            <h3 className="text-lg font-semibold text-white">{title}</h3>
          </div>
        </CardHeader>
      )}
      <CardContent className={title ? "" : "p-6"}>
        {children}
      </CardContent>
    </Card>
  );
}