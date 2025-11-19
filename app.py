import streamlit as st
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

def clean_api_key(key):
    """Nettoie la clé API de tout caractère indésirable."""
    if not key:
        return ""
    # Enlève les espaces, sauts de ligne, et guillemets accidentels
    return key.strip().replace('\n', '').replace('\r', '').replace('"', '').replace("'", "")

def process_audio(api_key, file_data, model_name):
    """Envoie l'audio à Gemini pour analyse."""
    # Nettoyage de sécurité
    clean_key = clean_api_key(api_key)
    
    # Initialisation du client
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
        # Lecture des bytes
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
        # En cas d'erreur, on laisse remonter l'exception pour l'afficher avec le debug info dans le main
        raise e

def main():
    st.title("🎙️ Diarisation MP3 avec Gemini")
    st.markdown("Segmentation des locuteurs et transcription automatique.")

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.header("Configuration")
        
        # Gestion de la clé API
        api_key_input = st.text_input("Clé API Gemini", type="password", help="Obtenez votre clé sur Google AI Studio")
        
        # Vérification des secrets Streamlit
        api_key = api_key_input
        if not api_key and "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            st.success("Clé API détectée dans les secrets.")
        
        # Nettoyage immédiat pour la validation
        clean_key = clean_api_key(api_key)

        # Validation visuelle pour l'utilisateur
        known_prefixes = {
            "AIza": "Google AI Studio",
            "gsk_": "Google AI Service Account",
            "hf_": "Hugging Face secret proxy",
        }

        if clean_key:
            if len(clean_key) < 30:
                st.warning("⚠️ La clé semble trop courte.")

            if not any(clean_key.startswith(prefix) for prefix in known_prefixes):
                st.info(
                    "ℹ️ Format de clé inattendu. Vérifiez qu'elle provient bien de Google AI Studio ou "
                    "d'une intégration approuvée."
                )
            else:
                detected = [name for prefix, name in known_prefixes.items() if clean_key.startswith(prefix)][0]
                st.caption(f"Clé détectée : {detected}.")

            if clean_key.startswith("hf_"):
                st.warning(
                    "Les clés Hugging Face (`hf_…`) ne peuvent pas être utilisées directement avec Gemini. "
                    "Récupérez une clé Google AI Studio (préfixe `AIza` ou `gsk_`)."
                )
        
        st.divider()
        
        model_choice = st.radio(
            "Modèle",
            ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.0-pro-preview"],
            index=0,
            help="Flash est plus rapide, Pro est plus précis."
        )
        
        # Mapping des noms
        model_map = {
            "gemini-2.5-flash": "gemini-2.5-flash",
            "gemini-2.5-pro": "gemini-2.5-pro", 
            "gemini-3.0-pro-preview": "gemini-3.0-pro-preview"
        }
        
        use_star_format = st.checkbox("Format *Locuteur_A", value=True, help="Ajoute un astérisque et remplace les espaces par des underscores.")

    # --- Main Content ---
    if not clean_key:
        st.warning("Veuillez entrer votre clé API Gemini dans la barre latérale pour commencer.")
        return

    uploaded_file = st.file_uploader("Choisissez un fichier MP3", type=["mp3"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        
        if st.button("Lancer l'analyse", type="primary"):
            with st.spinner("Analyse en cours avec Gemini... Cela peut prendre quelques instants."):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Traitement
                    result = process_audio(clean_key, uploaded_file, model_map.get(model_choice, "gemini-2.5-flash"))
                    
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
                    
                except Exception as e:
                    st.error("❌ Une erreur est survenue lors de l'analyse.")

                    # Affichage technique de l'erreur
                    st.code(str(e), language="text")

                    error_text = str(e).lower()
                    if "api key not valid" in error_text or "api_key_invalid" in error_text:
                        st.info(
                            "Google a rejeté la requête car la clé API n'est pas reconnue. "
                            "Assurez-vous d'utiliser une clé issue de Google AI Studio (préfixe `AIza`) "
                            "ou d'un compte de service Google AI (`gsk_`). Les jetons Hugging Face (`hf_…`) ne sont pas "
                            "acceptés directement par l'API Gemini."
                        )

                    # Section de débogage pour la clé API
                    with st.expander("ℹ️ Informations de débogage (Clé API)"):
                        mask_len = len(clean_key)
                        if mask_len > 8:
                            masked_key = f"{clean_key[:4]}...{clean_key[-4:]}"
                        else:
                            masked_key = "Trop courte pour afficher"
                        
                        st.write(f"**Longueur de la clé reçue :** {mask_len}")
                        st.write(f"**Aperçu de la clé utilisée :** `{masked_key}`")
                        st.write("**Vérification :** Assurez-vous que cet aperçu correspond au début et à la fin de votre clé réelle.")
                        st.write("Si vous voyez des guillemets ou des espaces inattendus, corrigez votre fichier de secrets ou votre entrée.")

if __name__ == "__main__":
    main()
