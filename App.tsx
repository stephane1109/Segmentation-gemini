import React, { useState, useCallback, useMemo } from 'react';
import { DiarizationEntry } from './types';
import { processAudioFile } from './services/geminiService';
import FileUpload from './components/FileUpload';
import Loader from './components/Loader';
import DiarizationResult from './components/DiarizationResult';
import { ResetIcon } from './components/icons';
import ApiKeyInput from './components/ApiKeyInput';

const App: React.FC = () => {
  const [apiKey, setApiKey] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('gemini-2.5-flash');
  const [useStarFormat, setUseStarFormat] = useState<boolean>(true);
  const [file, setFile] = useState<File | null>(null);
  const [diarizationResult, setDiarizationResult] = useState<DiarizationEntry[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingMessage, setLoadingMessage] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const isApiKeySet = apiKey.trim() !== '';

  const handleFileSelect = useCallback(async (selectedFile: File) => {
    if (!isApiKeySet) {
      setError("Veuillez d'abord fournir une clé API Gemini.");
      return;
    }
    setFile(selectedFile);
    setIsLoading(true);
    setError(null);
    setDiarizationResult(null);
    setLoadingMessage('Analyse audio en cours... (cela peut prendre un moment)');

    try {
      const result = await processAudioFile(selectedFile, apiKey, selectedModel);
      
      const formattedResult = result.map(entry => ({
        ...entry,
        speaker: useStarFormat 
          ? `*${entry.speaker.replace(/ /g, '_')}` 
          : entry.speaker,
      }));

      setDiarizationResult(formattedResult);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  }, [apiKey, isApiKeySet, useStarFormat, selectedModel]);

  const speakerCount = useMemo(() => {
    if (!diarizationResult) return 0;
    const speakers = new Set(diarizationResult.map(entry => entry.speaker));
    return speakers.size;
  }, [diarizationResult]);

  const handleReset = () => {
    setFile(null);
    setDiarizationResult(null);
    setIsLoading(false);
    setError(null);
    setLoadingMessage('');
  };

  const renderContent = () => {
    if (isLoading) {
      return <Loader message={loadingMessage} />;
    }
    if (error) {
      return (
        <div className="text-center text-red-400 bg-red-900/50 p-4 rounded-lg">
          <p className="font-bold">Erreur</p>
          <p>{error}</p>
        </div>
      );
    }
    if (diarizationResult && file) {
      return <DiarizationResult result={diarizationResult} fileName={file.name} speakerCount={speakerCount} useStarFormat={useStarFormat} />;
    }
    // L'upload est désactivé si la clé n'est pas fournie
    return <FileUpload onFileSelect={handleFileSelect} isLoading={isLoading || !isApiKeySet} />;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-4xl text-center mb-8">
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
          Segmentation de MP3 par IA
        </h1>
        <p className="mt-4 text-lg text-gray-400">
          Fournissez votre clé API, choisissez le modèle adapté à votre audio, puis téléchargez un MP3.
        </p>
        <div className="mt-4 text-xs text-gray-500 max-w-xl mx-auto">
          Le modèle Gemini 2.5 Flash offre un quota gratuit généreux (jusqu'à 60 requêtes par minute). Le modèle Pro peut entraîner des frais. Pour les détails complets, consultez la 
          <a href="https://ai.google.dev/pricing" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline ml-1">
            tarification officielle de l'API Gemini.
          </a>
        </div>
      </div>
      
      {!diarizationResult && (
        <div className="w-full max-w-2xl mb-8 p-6 bg-gray-800/50 border border-gray-700 rounded-xl">
          <h2 className="text-xl font-bold mb-4 text-center">Configuration</h2>
          <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} />

          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Choix du Modèle IA
            </label>
            <fieldset className="space-y-3 rounded-md bg-gray-900 p-4 border border-gray-600">
              <legend className="sr-only">Choix du modèle IA</legend>
              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id="flash-model"
                    name="model-selection"
                    type="radio"
                    value="gemini-2.5-flash"
                    checked={selectedModel === 'gemini-2.5-flash'}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-500 bg-gray-700"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="flash-model" className="font-bold text-white cursor-pointer">
                    Gemini 2.5 Flash
                  </label>
                  <p className="text-gray-400">Le choix le plus rapide et économique. Parfait pour les enregistrements clairs. Recommandé pour la majorité des usages.</p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id="pro-model"
                    name="model-selection"
                    type="radio"
                    value="gemini-2.5-pro"
                    checked={selectedModel === 'gemini-2.5-pro'}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-500 bg-gray-700"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="pro-model" className="font-bold text-white cursor-pointer">
                    Gemini 2.5 Pro
                  </label>
                  <p className="text-gray-400">Offre une précision maximale pour les audios complexes (bruit, accents...). Le traitement est plus long.</p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id="gemini-3-model"
                    name="model-selection"
                    type="radio"
                    value="gemini-3-pro-preview"
                    checked={selectedModel === 'gemini-3-pro-preview'}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-500 bg-gray-700"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="gemini-3-model" className="font-bold text-white cursor-pointer">
                    Gemini 3.0 Pro (Preview)
                  </label>
                  <p className="text-gray-400">La dernière génération. Capacités de raisonnement supérieures pour les tâches très complexes.</p>
                </div>
              </div>
            </fieldset>
          </div>

          <div className="mt-6 flex items-center justify-center">
            <input
              type="checkbox"
              id="star-format"
              checked={useStarFormat}
              onChange={(e) => setUseStarFormat(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 bg-gray-700"
            />
            <label htmlFor="star-format" className="ml-2 block text-sm text-gray-300">
              Formater le nom du locuteur (ex: *Locuteur_A)
            </label>
          </div>
        </div>
      )}

      <main className="w-full max-w-4xl flex-grow flex items-center justify-center">
        {renderContent()}
      </main>

      {(diarizationResult || error) && !isLoading && (
        <footer className="mt-8">
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-6 py-2 bg-gray-700 text-white font-semibold rounded-lg hover:bg-gray-600 transition-colors duration-300"
          >
            <ResetIcon className="w-5 h-5" />
            Analyser un autre fichier
          </button>
        </footer>
      )}
    </div>
  );
};

export default App;