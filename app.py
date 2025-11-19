import streamlit as st
import os
import tempfile
import json
from google import genai
from google.genai import types

# Configuration de la page
st.set_page_config(
    page_title="Segmentation de MP3 - Gemini 2.5 et 3",
    page_icon=None,
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
    .field-label {
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
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
    st.markdown(
        """
        <h1 style="text-align: center; color: #ff2d2d; margin-bottom: 0;">Segmentation de MP3</h1>
        <h2 style="text-align: center; color: #ff2d2d; margin-top: 0;">Modèles : Gemini 2.5 et 3</h2>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p style="text-align: center; margin: 0.5rem 0 0;">'
        '<a href="https://www.codeandcortex.fr" target="_blank" style="color: #61dafb; text-decoration: none;">www.codeandcortex.fr</a>'
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.4); margin: 1rem 0;'>", unsafe_allow_html=True)

    st.markdown(
        """
        Fournissez votre clé API, choisissez le modèle adapté à votre audio, puis téléchargez un MP3.
        Le modèle Gemini 2.5 Flash offre un quota gratuit généreux. Le modèle Gemini 3.0 peut offrir une meilleure précision.
        Pour les détails complets, <a href="https://ai.google.dev/gemini-api/docs/pricing?hl=fr" target="_blank">consultez la tarification officielle de l'API Gemini</a>.
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<h3 style="text-align: center; color: #ff2d2d;">Configuration</h3>', unsafe_allow_html=True)

    st.markdown('<div class="field-label">Votre Clé API Gemini</div>', unsafe_allow_html=True)

    api_key_input = st.text_input(
        "Votre Clé API Gemini",
        type="password",
        help="Obtenez votre clé sur Google AI Studio",
        placeholder="AIza...",
        label_visibility="collapsed"
    )

    api_key = api_key_input
    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Clé API détectée dans les secrets.")

    clean_key = clean_api_key(api_key)

    st.markdown(
        "<small>Votre clé est envoyée de manière sécurisée et n'est pas stockée. "
        "<a href='https://aistudio.google.com/app/api-keys' target='_blank'>Obtenez votre clé API sur Google AI Studio.</a></small>",
        unsafe_allow_html=True,
    )

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

    st.markdown('<h3 style="text-align: center; color: #ff2d2d;">Choix du Modèle IA</h3>', unsafe_allow_html=True)

    model_options = [
        {
            "value": "gemini-2.5-flash",
            "label": "Gemini 2.5 Flash",
            "description": "Le choix le plus rapide et économique. Parfait pour les enregistrements clairs.",
        },
        {
            "value": "gemini-2.5-pro",
            "label": "Gemini 2.5 Pro",
            "description": "Offre une précision accrue pour les audios complexes.",
        },
        {
            "value": "gemini-3.0-pro",
            "label": "Gemini 3.0",
            "description": "Modèle de nouvelle génération pour un raisonnement et une précision maximale.",
        },
    ]

    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = model_options[0]["value"]

    def _set_model(selected_value):
        st.session_state["selected_model"] = selected_value
        for option in model_options:
            st.session_state[f"model_option_{option['value']}"] = option["value"] == selected_value

    for option in model_options:
        checkbox_key = f"model_option_{option['value']}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = option["value"] == st.session_state["selected_model"]

        st.checkbox(
            f"{option['label']} — {option['description']}",
            key=checkbox_key,
            on_change=_set_model,
            args=(option["value"],)
        )

    model_choice = st.session_state.get("selected_model", model_options[0]["value"])

    use_star_format = st.checkbox(
        "Formater le nom du locuteur (ex: *Locuteur_A)",
        value=True,
        help="Ajoute un astérisque et remplace les espaces par des underscores."
    )

    st.markdown('<h3 style="text-align: center; color: #ff2d2d;">Importez votre fichier MP3</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Importer un fichier MP3",
        type=["mp3"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')

    launch_clicked = st.button("Lancer l'application", type="primary", use_container_width=True)

    if not clean_key:
        st.warning("Veuillez entrer votre clé API Gemini pour lancer une analyse.")
        return

    if launch_clicked:
        if uploaded_file is None:
            st.warning("Importez d'abord un fichier MP3 pour lancer l'analyse.")
            return

        with st.spinner("Analyse en cours avec Gemini... Cela peut prendre quelques instants."):
            try:
                uploaded_file.seek(0)

                result = process_audio(clean_key, uploaded_file, model_choice)

                st.success(f"Analyse terminée ! {len(result)} segments détectés.")

                output_text = ""

                for item in result:
                    raw_speaker = item.get('speaker', 'Inconnu')
                    timestamp = item.get('timestamp', '')
                    text = item.get('text', '')

                    display_speaker = raw_speaker
                    if use_star_format:
                        display_speaker = f"*{raw_speaker.replace(' ', '_')}"

                    output_text += f"[{timestamp}] {display_speaker}:\n{text}\n\n"

                    css_class = "default-speaker"
                    if "A" in raw_speaker: css_class = "speaker-A"
                    elif "B" in raw_speaker: css_class = "speaker-B"
                    elif "C" in raw_speaker: css_class = "speaker-C"

                    st.markdown(f"""
                    <div class=\"speaker-box {css_class}\">
                        <div style=\"font-weight: bold; margin-bottom: 0.2rem;\">{display_speaker} <span style=\"opacity: 0.6; font-size: 0.8em; font-weight: normal;\">[{timestamp}]</span></div>
                        <div>{text}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.download_button(
                    label="📥 Télécharger la transcription (.txt)",
                    data=output_text,
                    file_name=f"{uploaded_file.name}_diarisation.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error("❌ Une erreur est survenue lors de l'analyse.")

                st.code(str(e), language="text")

                error_text = str(e).lower()
                if "api key not valid" in error_text or "api_key_invalid" in error_text:
                    st.info(
                        "Google a rejeté la requête car la clé API n'est pas reconnue. "
                        "Assurez-vous d'utiliser une clé issue de Google AI Studio (préfixe `AIza`) "
                        "ou d'un compte de service Google AI (`gsk_`). Les jetons Hugging Face (`hf_…`) ne sont pas "
                        "acceptés directement par l'API Gemini."
                    )

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
