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
