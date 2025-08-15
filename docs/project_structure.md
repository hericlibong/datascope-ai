# Carte et dépendances du projet Datascope_AI

## Vue arborescente simplifiée
Voici l’arborescence des fichiers et leurs principaux imports :

datascope_backend/
├── settings.py
│   ├── decouple
│   ├── pathlib
│   └── django
├── urls.py
│   ├── django.urls
│   ├── django.contrib
│   ├── api.urls
│   ├── analysis.urls
│   └── users.urls
├── asgi.py, wsgi.py
│   └── django.core

ai_engine/
├── __init__.py
│   ├── decouple
│   ├── langchain_community.cache
│   └── langchain.globals
├── apps.py, admin.py, models.py
│   └── django
├── pipeline.py
│   ├── ai_engine.utils
│   ├── ai_engine.chains
│   ├── ai_engine.formatter
│   ├── ai_engine.schemas
│   ├── ai_engine.scoring
│   ├── ai_engine.memory
│   └── ai_engine.connectors.*
├── formatter.py, scoring.py, schemas.py, utils.py
│   ├── ai_engine.schemas
│   ├── ai_engine.utils
│   └── pydantic, tiktoken, typing
├── connectors/
│   ├── requests, pydantic, tenacity
│   ├── ai_engine.schemas
│   └── ai_engine.connectors.*
├── memory/, chains/
│   └── ai_engine.*

analysis/
├── models.py, admin.py, apps.py
│   └── django
├── serializers.py
│   ├── rest_framework
│   └── analysis.models
├── views.py
│   ├── rest_framework
│   ├── analysis.models, serializers
│   ├── users.serializers, users.models
│   └── ai_engine.pipeline
├── urls.py
│   ├── django.urls
│   └── analysis.views

api/
├── models.py, admin.py, apps.py
│   └── django
├── views.py
│   └── django.shortcuts
├── urls.py
│   ├── django.urls
│   ├── rest_framework.routers
│   ├── analysis.views
│   └── users.views
│   └── rest_framework_simplejwt.views

users/
├── models.py, admin.py, apps.py
│   └── django
├── serializers.py
│   ├── rest_framework
│   └── users.models
├── views.py
│   ├── rest_framework
│   ├── users.serializers, users.models
│   └── django
├── urls.py
│   └── django.urls

---


## Graphe des dépendances
Diagramme généré en Mermaid (compatible GitHub et VS Code avec l’extension "Markdown Preview Mermaid Support") :


```mermaid
graph TD
    subgraph datascope_backend
        settings.py -->|imports| decouple
        settings.py -->|imports| pathlib
        settings.py -->|imports| django
        urls.py -->|imports| django.urls
        urls.py -->|imports| django.contrib
        urls.py -->|includes| api.urls
        urls.py -->|includes| analysis.urls
        urls.py -->|includes| users.urls
        asgi.py -->|imports| django.core
        wsgi.py -->|imports| django.core
    end

    subgraph ai_engine
        __init__.py -->|imports| decouple
        __init__.py -->|imports| langchain_community.cache
        __init__.py -->|imports| langchain.globals
        apps.py -->|imports| django
        admin.py -->|imports| django
        models.py -->|imports| django
        pipeline.py -->|imports| ai_engine.utils
        pipeline.py -->|imports| ai_engine.chains
        pipeline.py -->|imports| ai_engine.formatter
        pipeline.py -->|imports| ai_engine.schemas
        pipeline.py -->|imports| ai_engine.scoring
        pipeline.py -->|imports| ai_engine.memory
        pipeline.py -->|imports| ai_engine.connectors
        formatter.py -->|imports| ai_engine.schemas
        formatter.py -->|imports| pydantic
        formatter.py -->|imports| typing
        scoring.py -->|imports| ai_engine.schemas
        scoring.py -->|imports| ai_engine.utils
        schemas.py -->|imports| pydantic
        schemas.py -->|imports| typing
        utils.py -->|imports| tiktoken
        connectors -->|imports| requests
        connectors -->|imports| pydantic
        connectors -->|imports| tenacity
        connectors -->|imports| ai_engine.schemas
        connectors -->|imports| ai_engine.connectors
        memory -->|imports| ai_engine
        chains -->|imports| ai_engine
    end

    subgraph analysis
        models.py -->|imports| django
        admin.py -->|imports| django
        apps.py -->|imports| django
        serializers.py -->|imports| rest_framework
        serializers.py -->|imports| analysis.models
        views.py -->|imports| rest_framework
        views.py -->|imports| analysis.models
        views.py -->|imports| analysis.serializers
        views.py -->|imports| users.serializers
        views.py -->|imports| users.models
        views.py -->|imports| ai_engine.pipeline
        urls.py -->|imports| django.urls
        urls.py -->|imports| analysis.views
    end

    subgraph api
        models.py -->|imports| django
        admin.py -->|imports| django
        apps.py -->|imports| django
        views.py -->|imports| django.shortcuts
        urls.py -->|imports| django.urls
        urls.py -->|imports| rest_framework.routers
        urls.py -->|imports| analysis.views
        urls.py -->|imports| users.views
        urls.py -->|imports| rest_framework_simplejwt.views
    end

    subgraph users
        models.py -->|imports| django
        admin.py -->|imports| django
        apps.py -->|imports| django
        serializers.py -->|imports| rest_framework
        serializers.py -->|imports| users.models
        views.py -->|imports| rest_framework
        views.py -->|imports| users.serializers
        views.py -->|imports| users.models
        urls.py -->|imports| django.urls
    end

    %% Cross-app dependencies
    analysis.views.py --> ai_engine.pipeline.py
    analysis.views.py --> users.serializers.py
    analysis.views.py --> users.models.py
    api.urls.py --> analysis.views.py
    api.urls.py --> users.views.py

```
