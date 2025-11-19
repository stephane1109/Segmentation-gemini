import { GoogleGenAI, Type } from '@google/genai';
import { DiarizationEntry } from '../types';

// Fonction utilitaire pour convertir un fichier en chaîne base64
const fileToBase64 = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Le résultat est "data:audio/mpeg;base64,..."
      // Nous devons supprimer le préfixe pour obtenir uniquement les données base64
      const base64String = (reader.result as string).split(',')[1];
      resolve(base64String);
    };
    reader.onerror = (error) => reject(error);
  });

// Instruction détaillée pour l'IA
const SEGMENTATION_PROMPT = `
Analysez le fichier audio fourni et effectuez une segmentation des locuteurs.
Votre tâche est d'identifier chaque locuteur et de transcrire leur discours.
La sortie doit être un tableau JSON valide. Chaque objet du tableau doit représenter un segment de parole et doit contenir les trois champs suivants :
1. "speaker": Une chaîne de caractères identifiant le locuteur (par exemple, "Locuteur A", "Locuteur B").
2. "timestamp": Une chaîne de caractères représentant l'heure de début du segment de parole au format "HH:MM:SS".
3. "text": Une chaîne de caractères contenant le texte transcrit pour ce segment.

Exemple de format de sortie valide :
[
  {
    "speaker": "Locuteur A",
    "timestamp": "00:00:02",
    "text": "Bonjour, comment ça va aujourd'hui ?"
  },
  {
    "speaker": "Locuteur B",
    "timestamp": "00:00:05",
    "text": "Ça va bien, merci. Et vous ?"
  }
]

Maintenant, traitez le fichier audio.
`;

/**
 * Cette fonction envoie le fichier audio directement à l'API Gemini depuis le client.
 * @param file Le fichier MP3 à analyser.
 * @param apiKey La clé API Gemini fournie par l'utilisateur.
 * @param model Le modèle Gemini à utiliser ('gemini-2.5-flash' ou 'gemini-2.5-pro').
 * @returns Une promesse qui se résout avec le résultat de la diarisation.
 */
export async function processAudioFile(file: File, apiKey: string, model: string): Promise<DiarizationEntry[]> {
  try {
    const ai = new GoogleGenAI({ apiKey });

    // Convertir le fichier en base64
    const base64Audio = await fileToBase64(file);
    const audioPart = {
      inlineData: {
        data: base64Audio,
        mimeType: file.type || 'audio/mpeg',
      },
    };

    const textPart = {
      text: SEGMENTATION_PROMPT,
    };

    // Définir le schéma de la réponse attendue pour garantir un JSON correct
    const responseSchema = {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          speaker: { type: Type.STRING },
          timestamp: { type: Type.STRING },
          text: { type: Type.STRING },
        },
        required: ["speaker", "timestamp", "text"],
      },
    };

    // Appeler l'API Gemini
    const response = await ai.models.generateContent({
      model: model,
      contents: { parts: [audioPart, textPart] },
      config: {
        responseMimeType: "application/json",
        responseSchema: responseSchema,
      },
    });

    let jsonString = response.text.trim();
    // Correction : Nettoyer la réponse de l'IA avant de la parser.
    // Les modèles peuvent parfois envelopper le JSON dans des blocs de code markdown.
    if (jsonString.startsWith('```json')) {
        jsonString = jsonString.slice(7, -3).trim();
    }
    
    const result = JSON.parse(jsonString);

    return result as DiarizationEntry[];

  } catch (error) {
    console.error("Erreur lors de l'appel à l'API Gemini:", error);
    if (error instanceof Error) {
      if (error.message.includes('API key not valid')) {
        throw new Error("Clé API non valide. Veuillez vérifier votre clé et réessayer.");
      }
      if (error.message.includes('429')) {
        throw new Error("Trop de requêtes effectuées. Veuillez patienter un moment avant de réessayer.");
      }
      // Rendre le message d'erreur de parsing plus utile
      if (error.message.includes('JSON.parse')) {
        throw new Error(`Échec de l'analyse de la réponse de l'IA. Le format JSON reçu est invalide. Erreur : ${error.message}`);
      }
      throw new Error(`Échec du traitement du fichier via Gemini : ${error.message}`);
    }
    throw new Error("Une erreur inconnue est survenue lors du traitement du fichier avec Gemini.");
  }
}