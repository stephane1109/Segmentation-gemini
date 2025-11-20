# Segmentation de MP3 par IA avec Gemini

Cette application web permet d'effectuer une segmentation des locuteurs (diarisation) sur des fichiers MP3 directement dans le navigateur, en utilisant l'API puissante de Google Gemini (2.5 Flash, Pro ou 3.0).
La segmentation (ou « diarization » en anglais) vise à découper un enregistrement audio en segments et à identifier « qui parle quand ».
L’algorithme détecte les changements de locuteur et attribue un label à chaque voix (par exemple Locuteur 1, Locuteur 2, etc.). On obtient ainsi une transcription de la conversation structurée par intervenant, ce qui permet ensuite d’analyser le contenu par personne (qui pose quelles questions, qui répond, combien de temps chacun parle, etc.).

---
## Comment l'utiliser

1.  **Obtenez une clé API Gemini** depuis [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **Collez votre clé API** dans le champ prévu à cet effet.
3.  **Choisissez un modèle IA :**
    *   **Gemini 2.5 Flash :** Le choix le plus rapide et économique. Idéal pour les enregistrements clairs... mais pas très précis ! 
    *   **Gemini 2.5 Pro :** Offre une précision maximale.
4.  **Téléchargez un fichier MP3**.
5.  **Patientez** pendant que l'IA transcrit l'audio et identifie les différents locuteurs.
6.  **Consultez et exportez** le résultat directement depuis la page.
