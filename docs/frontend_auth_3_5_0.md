## ✅ #3.5.0 – Création de la page d’inscription (signup)

### 🎯 Objectif
Permettre à un utilisateur de créer un compte via une interface frontend React connectée à l’API backend Django.  
Cette étape est préalable à toute authentification et utilisation des fonctionnalités sécurisées.

---

### 📁 Fichiers ajoutés

#### 1. `components/Auth/SignupForm.tsx`
- Formulaire React avec 3 champs : `username`, `email`, `password`
- États gérés : `loading`, `error`, `success`
- Appel à `register()` (API)
- Message de confirmation + redirection vers `/login`

#### 2. `pages/SignupPage.tsx`
- Rend le composant `SignupForm`
- Gère la redirection post-inscription via `useNavigate()`

#### 3. `api/auth.ts`
- Fonction `register({ username, email, password })`
- POST vers `/api/users/register/`
- Gestion d’erreurs et parsing JSON sécurisé

#### 4. `App.tsx`
- Ajout des routes `/signup` et `/login` (placeholder)
- Intégration dans le layout principal

#### 5. `pages/Home.tsx`
- Ajout d’un bouton **"Créer un compte"** pointant vers `/signup`

---

### 🔧 Backend utilisé
- **Route** : `POST /api/users/register/`
- **Vue Django** : `UserRegistrationAPIView`
- **Serializer** : `UserRegistrationSerializer`  
  - Champs requis : `username`, `email`, `password`
  - Validation Django intégrée (longueur, sécurité du mot de passe…)

---

### ✅ Résultat obtenu
- Création de compte fonctionnelle et testée
- Gestion propre des erreurs (champ manquant, mot de passe trop court…)
- Message de succès + redirection automatique vers `/login`
- Comptes visibles dans l’interface Django admin

---

### 🔜 Étape suivante
Passage à la sous-issue [#3.5.1 – Page Login avec appel API `/auth/token/`](#3.5.1).

## ✅ #3.5.1 – Page Login (connexion) et authentification

### 🎯 Objectif
Permettre à l’utilisateur de se connecter à l’application en saisissant son nom d’utilisateur et son mot de passe, et ainsi obtenir un token d’accès (JWT) lui permettant d’utiliser toutes les fonctionnalités protégées.

---

### 📁 Fichiers ajoutés / modifiés

#### 1. `components/Auth/LoginForm.tsx`
- Formulaire React avec 2 champs : `username`, `password`
- États gérés : `loading`, `error`
- Appel à la fonction `login()` (API)
- Affichage d’un message d’erreur en cas de mauvais identifiant ou mot de passe
- Redirection via la prop `onSuccess` (par défaut vers la page d’accueil `/`)

#### 2. `pages/LoginPage.tsx`
- Rend le composant `LoginForm`
- Gère la redirection post-authentification via `useNavigate()`

#### 3. `api/auth.ts`
- Fonction `login({ username, password })`
- POST vers `/api/token/`
- Récupération et stockage des tokens JWT (`accessToken`, `refreshToken`) ainsi que du `username`
- Gestion d’erreurs et parsing JSON sécurisé

#### 4. `App.tsx`
- Ajout de la route `/login`
- Routing cohérent avec le reste de l’application

#### 5. `pages/Home.tsx`
- Affichage du nom d’utilisateur si connecté (lecture depuis le localStorage)
- Ajout d’un bouton **"Déconnexion"** visible si connecté

---

### ✅ Résultat obtenu
- Connexion fonctionnelle, tokens correctement stockés
- Gestion des erreurs de connexion (mauvais identifiants, compte inexistant, etc.)
- Redirection fluide après login
- Affichage du nom d’utilisateur en page d’accueil si connecté
- Possibilité de déconnexion via le bouton “Déconnexion”

---

### 🔜 Étape suivante
Mise en place de la protection des routes via un composant `PrivateRoute` et gestion de la session sur toutes les pages sensibles.

---

## ✅ #3.5.2 – Stockage du token JWT et gestion de session

### 🎯 Objectif
Assurer la persistance de la session utilisateur en stockant les tokens JWT dans le navigateur, pour permettre à l’utilisateur de rester connecté tant que le token est valide, même après fermeture de l’onglet ou du navigateur.

---

### 📁 Fichiers modifiés

#### 1. `api/auth.ts`
- Stockage du `accessToken`, `refreshToken` et `username` dans le `localStorage`
- Fonctions utilitaires :  
  - `setTokens()` : stockage des tokens  
  - `clearTokens()` : suppression des tokens (logout/session expirée)  
  - `getAccessToken()`, `getUsername()` : lecture des infos de session
- Fonction `authFetch()` :  
  - Envoie le header `Authorization: Bearer <accessToken>` pour chaque requête protégée
  - Redirige automatiquement vers `/login` si le token est expiré

#### 2. `components/Auth/LogoutButton.tsx` (ou dans la Home)
- Appel à `clearTokens()` lors de la déconnexion
- Redirection immédiate vers `/login`

#### 3. `pages/Home.tsx`
- Vérification de la session via `getUsername()`
- Affichage conditionnel du bouton “Déconnexion” si connecté

---

### ⚙️ Choix technique

- **Les tokens sont stockés dans `localStorage`** afin de garantir la persistance de la session même après fermeture/réouverture du navigateur.
- **L’utilisateur reste connecté tant que le token d’accès est valide (30 min)**
- **La déconnexion volontaire ou l’expiration du token efface toutes les informations de session**
- **Aucune gestion automatique du refresh token à ce stade** :  
  - L’utilisateur doit se reconnecter après expiration du token d’accès.

---

### ✅ Résultat obtenu
- Expérience utilisateur continue (l’utilisateur ne perd pas la session à la fermeture du navigateur)
- Déconnexion propre et sécurisée
- Contrôle total sur la gestion de la session côté frontend

---

### 🔜 Étape suivante
Création du composant `PrivateRoute` pour protéger l’accès aux pages sensibles (analyse, historique…) et renforcer la sécurité de l’interface.


