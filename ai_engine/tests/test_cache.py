# from langchain_openai import ChatOpenAI
# from ai_engine.chains.extraction import run as extract_run

# def test_cache_hits(monkeypatch):
#     """
#     Teste que le cache SQLite empêche un second appel OpenAI
#     pour un prompt identique.
#     """

#     call_counter = {"n": 0}

#     def fake_invoke(self, *args, **kwargs):
#         call_counter["n"] += 1
#         from ai_engine.schemas import ExtractionResult
#         import json
#         obj = ExtractionResult(
#             language="fr",
#             persons=["Macron"], organizations=["ONU"],
#             locations=["Paris"], dates=["2025-01-01"], numbers=[]
#         )
#         return json.dumps(obj.model_dump())


#     # Patch global : tous les .invoke sur ChatOpenAI vont passer par fake_invoke
#     monkeypatch.setattr(ChatOpenAI, "invoke", fake_invoke)

#     article = "Emmanuel Macron a rencontré les représentants de l'ONU à Paris en 2025."

#     # Appel 1 : fake_invoke est appelé
#     extract_run(article)
#     assert call_counter["n"] == 1

#     # Appel 2 : le cache SQLite doit répondre, pas fake_invoke
#     extract_run(article)
#     assert call_counter["n"] == 1  # compteur inchangé → pas d’appel LLM
