export interface DatasetSuggestion {
    title: string;
    description?: string|null;
    source_name: string;
    source_url: string;
    formats: string[];
    organization?: string|null;
    license?: string|null;
    last_modified?: string|null;
    richness?: number;
    found_by: "CONNECTOR" | "LLM";
  }
  
  export interface LLMSourceSuggestion {
    title: string;
    description: string;
    link: string;
    source: string;
  }
  
  export interface VizSuggestion {
    title: string;
    chart_type: string;
    x: string;
    y: string;
    note?: string|null;
  }
  
  export interface AngleResources {
    index:        number;
    title:        string;
    description:  string;
    keywords:     string[];
    datasets:     DatasetSuggestion[];
    sources:      LLMSourceSuggestion[];
    visualizations: VizSuggestion[];
  }
  