"""
ai_engine.connectors.interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Définition d’un contrat minimal (« interface ») que tous les connecteurs
DataScope doivent respecter.

Pourquoi une *interface* ?
--------------------------
• Uniformiser l’appel depuis les couches supérieures (pipeline, API, UI).  
  Ex. :
      client: ConnectorInterface = DataGovClient()
      for suggestion in client.search("climate"):
          ... # agnostique de la source réelle

• Simplifier les tests : on peut remplacer n’importe quel connecteur réel
  par un *stub* qui renvoie des DatasetSuggestion factices.

• Faciliter l’ajout de nouveaux connecteurs : il suffit de proposer une classe
  qui implémente cette méthode `search` et l’écosystème DataScope l’accepte.

Choix techniques
----------------
• On utilise « typing.Protocol » (PEP 544).  
  → un objet est *implicitement* conforme dès qu’il possède
    les méthodes/attributs exigés ; inutile d’hériter explicitement.

• La méthode `search` renvoie un *Iterable* / *Iterator* de
  `DatasetSuggestion`.  
  Cela laisse chaque implémentation libre d’utiliser un `yield`,
  un wrapper sur un générateur, ou même une liste pré-chargée.

• On fixe un paramètre optionnel `page_size`
  pour maintenir la notion de pagination là où c’est pertinent (CKAN, etc.).

NB : Si un jour certains connecteurs doivent retourner un type différent
(USDataset brut, par ex.), on pourra introduire un second protocole ou
un paramètre générique. Pour l’instant, `DatasetSuggestion` est l’unité de
monnaie commune de tout le pipeline IA.
"""

from __future__ import annotations

from typing import Iterator, Protocol, Optional, List

from ai_engine.schemas import DatasetSuggestion


class ConnectorInterface(Protocol):
    """
    Contrat minimal de tout connecteur Datascope.

    Méthodes
    --------
    search(keyword, *, page_size=10, locations=None) -> Iterator[DatasetSuggestion]
        Recherche paginée de jeux de données pour un mot-clé.

        * `keyword`   : chaîne interrogée (déjà « nettoyée » ou libre).
        * `page_size` : taille de page souhaitée (implémentation-dépendant).
        * `locations` : liste optionnelle de lieux pour prioriser les résultats.
        * renvoie un itérateur (ou générateur) de `DatasetSuggestion`.

    Toute classe possédant **au moins** cette signature est considérée comme
    compatible. Pas d’héritage imposé ; c’est de l’« interface structurelle ».
    """

    # La syntaxe « ... » indique simplement que la méthode doit exister ;
    # chaque connecteur fournira sa propre implémentation concrète.
    def search(
        self,
        keyword: str,
        *,
        page_size: int = 10,
        locations: Optional[List[str]] = None,
    ) -> Iterator[DatasetSuggestion]: ...
