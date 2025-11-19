mport streamlit as st
import os
import tempfile
import json
from google import genai
from google.genai import types

# Configuration de la page
st.set_page_config(
    page_title="Diarisation MP3 - Gemini",
    page_icon="🎙️",
    layout="centered"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .speaker-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #30363d;
    }
    .speaker-A { background-color: rgba(30, 58, 138, 0.3); border-color: #1e40af; }
    .speaker-B { background-color: rgba(88, 28, 135, 0.3); border-color: #7e22ce; }
    .speaker-C { background-color: rgba(20, 83, 45, 0.3); border-color: #15803d; }
    .default-speaker { background-color: rgba(55, 65, 81, 0.3); border-color: #4b5563; }
    </style>
""", unsafe_allow_html=True)

def process_audio(api_key, file_data, model_name):
    """Envoie l'audio à Gemini pour analyse."""
    # Nettoyage de sécurité supplémentaire
    clean_key = api_key.strip()
    client = genai.Client(api_key=clean_key)
    
    prompt = """
    Analysez le fichier audio fourni et effectuez une segmentation des locuteurs.
    Votre tâche est d'identifier chaque locuteur et de transcrire leur discours.
    La sortie doit être un tableau JSON valide. Chaque objet du tableau doit représenter un segment de parole et doit contenir les trois champs suivants :
    1. "speaker": Une chaîne de caractères identifiant le locuteur (par exemple, "Locuteur A", "Locuteur B").
    2. "timestamp": Une chaîne de caractères représentant l'heure de début du segment de parole au format "HH:MM:SS".
    3. "text": Une chaîne de caractères contenant le texte transcrit pour ce segment.
    """

    # Configuration du schéma de réponse JSON
    response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "speaker": {"type": "STRING"},
                "timestamp": {"type": "STRING"},
                "text": {"type": "STRING"},
            },
            "required": ["speaker", "timestamp", "text"],
        },
    }

    try:
        # Création d'un fichier temporaire pour l'audio car l'API attend des bytes ou un fichier
        # Note: Streamlit fournit un objet BytesIO, nous lisons les bytes directement
        audio_bytes = file_data.read()
        
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(data=audio_bytes, mime_type="audio/mpeg"),
                        types.Part(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema
            )
        )
        
        return json.loads(response.text)
    except Exception as e:
        # Gestion spécifique des erreurs courantes
        error_str = str(e)
        if "API key not valid" in error_str or "400" in error_str:
            raise ValueError("La clé API semble invalide (Erreur 400). Vérifiez qu'il n'y a pas d'espaces au début ou à la fin de votre clé.")
        if "429" in error_str:
            raise ValueError("Quota dépassé (Erreur 429). Veuillez patienter ou utiliser une autre clé.")
        raise e

def main():
    st.title("🎙️ Diarisation MP3 avec Gemini")
    st.markdown("Segmentation des locuteurs et transcription automatique.")

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.header("Configuration")
        
        # Gestion de la clé API
        api_key_input = st.text_input("Clé API Gemini", type="password", help="Obtenez votre clé sur Google AI Studio")
        
        # Vérification des secrets Streamlit si la clé n'est pas entrée manuellement
        api_key = api_key_input
        if not api_key and "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            st.success("Clé API détectée dans les secrets.")
        
        # IMPORTANT : Nettoyage de la clé (retrait des espaces invisibles)
        if api_key:
            api_key = api_key.strip()

        st.divider()
        
        model_choice = st.radio(
            "Modèle",
            ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.0-pro-preview"],
            index=0,
            help="Flash est plus rapide, Pro est plus précis."
        )
        
        # Mapping des noms conviviaux aux noms techniques
        model_map = {
            "gemini-2.5-flash": "gemini-2.5-flash",
            "gemini-2.5-pro": "gemini-2.5-pro", 
            "gemini-3.0-pro-preview": "gemini-3.0-pro-preview"
        }
        
        use_star_format = st.checkbox("Format *Locuteur_A", value=True, help="Ajoute un astérisque et remplace les espaces par des underscores.")

    # --- Main Content ---
    if not api_key:
        st.warning("Veuillez entrer votre clé API Gemini dans la barre latérale pour commencer.")
        return

    uploaded_file = st.file_uploader("Choisissez un fichier MP3", type=["mp3"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        
        if st.button("Lancer l'analyse", type="primary"):
            with st.spinner("Analyse en cours avec Gemini... Cela peut prendre quelques instants."):
                try:
                    # Reset file pointer just in case
                    uploaded_file.seek(0)
                    
                    # Traitement
                    result = process_audio(api_key, uploaded_file, model_map.get(model_choice, "gemini-2.5-flash"))
                    
                    st.success(f"Analyse terminée ! {len(result)} segments détectés.")
                    
                    # Affichage des résultats
                    output_text = ""
                    
                    for item in result:
                        raw_speaker = item.get('speaker', 'Inconnu')
                        timestamp = item.get('timestamp', '')
                        text = item.get('text', '')
                        
                        # Formatage du nom du locuteur
                        display_speaker = raw_speaker
                        if use_star_format:
                            display_speaker = f"*{raw_speaker.replace(' ', '_')}"
                        
                        # Construction du texte pour l'export
                        output_text += f"[{timestamp}] {display_speaker}:\n{text}\n\n"
                        
                        # Détermination de la classe CSS pour la couleur
                        css_class = "default-speaker"
                        if "A" in raw_speaker: css_class = "speaker-A"
                        elif "B" in raw_speaker: css_class = "speaker-B"
                        elif "C" in raw_speaker: css_class = "speaker-C"
                        
                        # Rendu visuel
                        st.markdown(f"""
                        <div class="speaker-box {css_class}">
                            <div style="font-weight: bold; margin-bottom: 0.2rem;">{display_speaker} <span style="opacity: 0.6; font-size: 0.8em; font-weight: normal;">[{timestamp}]</span></div>
                            <div>{text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Zone de téléchargement
                    st.download_button(
                        label="📥 Télécharger la transcription (.txt)",
                        data=output_text,
                        file_name=f"{uploaded_file.name}_diarisation.txt",
                        mime="text/plain"
                    )
                    
                except ValueError as ve:
                    st.error(f"❌ Erreur : {str(ve)}")
                except Exception as e:
                    st.error(f"❌ Une erreur inattendue est survenue : {str(e)}")

if __name__ == "__main__":
    main()
