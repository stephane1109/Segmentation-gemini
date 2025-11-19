# Segmentation de MP3 par IA avec Gemini

Cette application web permet d'effectuer une segmentation des locuteurs (diarisation) sur des fichiers MP3 directement dans le navigateur, en utilisant l'API puissante de Google Gemini (2.5 Flash, Pro ou 3.0).

## Architecture

L'application repose sur une architecture moderne :
*   **Frontend :** React + Vite + TypeScript (Interface utilisateur).
*   **Backend :** FastAPI (Python) sert l'application statique et permet la compatibilité avec les environnements de déploiement cloud comme Hugging Face Spaces.
*   **IA :** Google Gemini API (via `@google/genai`).

---

## 🚀 Déploiement sur Hugging Face Spaces

Il existe deux façons principales de déployer cette application sur Hugging Face.

### Méthode 1 : Space Docker (Recommandée) 🏆

C'est la méthode la plus simple et la plus automatisée. Hugging Face va gérer la construction du site (build React) et le lancement du serveur (Python) en une seule étape grâce au fichier `Dockerfile` inclus.

1.  Allez sur [Hugging Face Spaces](https://huggingface.co/spaces) et cliquez sur **Create new Space**.
2.  Entrez un nom pour votre Space.
3.  Choisissez **Docker** comme SDK.
4.  Cliquez sur **Create Space**.
5.  Copiez tous les fichiers de ce projet dans le dépôt de votre Space (via Git ou l'interface web).

**Comment ça marche ?**
Le `Dockerfile` contient deux étapes :
1.  Il télécharge Node.js, installe les dépendances et compile le React (`npm run build`).
2.  Il prépare un environnement Python, installe FastAPI, récupère le site compilé et le lance.

### Méthode 2 : Build Local + Space Python (Alternative)

Utilisez cette méthode si vous souhaitez construire l'application sur votre propre machine et n'envoyer que le résultat final.

1.  **Sur votre machine**, compilez le projet :
    ```bash
    npm install
    npm run build
    ```
    Cela va créer un dossier `dist/` contenant votre site web optimisé.

2.  **Sur Hugging Face** :
    *   Créez un Space Docker (ou Python standard si configuré).
    *   N'envoyez QUE les fichiers suivants :
        *   Le dossier `dist/` (complet).
        *   `app.py`
        *   `requirements.txt`
        *   `Dockerfile` (Optionnel si vous configurez l'environnement manuellement, mais recommandé).

---

## 🛠️ Installation et Développement Local

Pour exécuter l'application sur votre machine :

1.  **Installer les dépendances :**
    ```bash
    npm install
    ```

2.  **Lancer le serveur de développement :**
    ```bash
    npm run dev
    ```
    Ouvrez `http://localhost:3000` dans votre navigateur.

Note : En local, vous n'avez pas besoin de lancer le serveur Python (`app.py`), le serveur de développement Vite suffit.

## Sécurité et API Key

Cette application fonctionne sur le principe "Bring Your Own Key". La clé API Google Gemini est saisie par l'utilisateur dans le navigateur et n'est **jamais stockée** sur le serveur. Elle transite directement du navigateur vers les serveurs de Google.
