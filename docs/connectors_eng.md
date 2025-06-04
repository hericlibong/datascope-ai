
# Audit Connectors

| Critère                           | **USA – Data.gov**                                                                                       | **Canada – open.canada.ca**                                                     | **R-U – data.gov.uk**                                                                      |
| --------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Base URL (search)**             | `https://catalog.data.gov/api/3/action/package_search` ([open.gsa.gov][1])                               | `https://open.canada.ca/data/api/3/action/package_search` ([open.canada.ca][2]) | `https://data.gov.uk/api/3/action/package_search` ([Data.gov.uk][3])                       |
| **Auth. requise pour la lecture** | Aucune (clé facultative pour write)                                                                      | Aucune                                                                          | Aucune                                                                                     |
| **Pagination**                    | `rows` (nb) + `start` (offset)                                                                           | Idem CKAN : `rows` + `start`                                                    | Idem CKAN : `rows` + `start`                                                               |
| **Quota / rate-limit public**     | Non documenté (pas de limite claire pour CKAN ; prévoir < 1 req/s)                                       | Non documenté                                                                   | Non documenté                                                                              |
| **Format de réponse**             | JSON CKAN : `result.results` → list<dict>                                                                | Identique                                                                       | Identique                                                                                  |
| **Métadonnées clés dispo**        | `id`, `title`, `notes`, `organization.title`, `resources[].format`, `license_title`, `metadata_modified` | Même structure (bilingue en/fr selon dataset)                                   | Même structure                                                                             |
| **Langue dominante**              | 🇺🇸 EN                                                                                                  | 🇨🇦 EN + FR (mix)                                                              | 🇬🇧 EN                                                                                    |
| **Ex. requête**                   | `?q=climate+change&rows=5`                                                                               | `?q=eau+water&rows=5`                                                           | `?q=transport&rows=5`                                                                      |
| **Observations**                  | Très large catalogue (≈ 350 k datasets). Formats variés (`CSV`, `JSON`, `WMS`, …).                       | Certaines ressources pointent vers ArcGIS ; penser fallback MIME-type.          | Beaucoup de datasets historiques ; certains sans `resources[].format` → prévoir inférence. |

[1]: https://open.gsa.gov/api/datadotgov/?utm_source=chatgpt.com "Data.gov API - GSA Open Technology"
[2]: https://open.canada.ca/data/en/dataset/2d90548d-50ef-4802-91f8-c59c5cf68251/resource/36830ed0-cd83-4fea-b2ae-15890116c68e?utm_source=chatgpt.com "Open Government API - OpenAPI Specification"
[3]: https://guidance.data.gov.uk/get_data/api_documentation/?utm_source=chatgpt.com "API documentation - Data.gov.uk guidance"



Parfait, voici un bloc de documentation prêt à intégrer dans `docs/connectors_eng.md` (ou `connectors.md` si tu préfères centraliser) :

---

### 🇨🇦 CanadaGovClient – Bilingual Support

The Canadian open data platform ([open.canada.ca](https://open.canada.ca)) offers **full bilingual metadata** for most datasets.

#### 🔧 Current Implementation

* The `CanadaGovClient` is currently configured to return results in **English**.
* This is done by:

  * Fetching the `/en/dataset/…` endpoint
  * Extracting `title_translated['en']`, `description_translated['en']`, etc.

#### 🧪 Bilingual Support (Optional)

* The connector could dynamically switch to **French** output when `lang="fr"` is passed.
* This would require:

  * Replacing `/en/` with `/fr/` in dataset URLs
  * Using `title_translated['fr']`, etc.
* No change to the API structure — just optional field selection.

#### ✅ Benefit

This allows CanadaGovClient to **serve localized suggestions** depending on user preference or application language.

---

Souhaites-tu que je l’ajoute directement dans un fichier `docs/connectors_eng.md` existant ou que je t’aide à le créer si besoin ?
