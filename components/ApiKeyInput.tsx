import React from 'react';

interface ApiKeyInputProps {
  apiKey: string;
  setApiKey: (key: string) => void;
}

const ApiKeyInput: React.FC<ApiKeyInputProps> = ({ apiKey, setApiKey }) => {
  return (
    <div className="space-y-3">
      <label htmlFor="api-key" className="block text-sm font-medium text-gray-300">
        Votre Clé API Gemini
      </label>
      <input
        type="password"
        id="api-key"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        className="block w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded-md shadow-sm placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-gray-200"
        placeholder="Entrez votre clé API ici"
      />
      <p className="text-xs text-gray-400 text-center">
        Votre clé est envoyée de manière sécurisée et n'est pas stockée. 
        <a 
          href="https://aistudio.google.com/app/apikey" 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-400 hover:underline ml-1"
        >
          Obtenez votre clé API sur Google AI Studio.
        </a>
      </p>
    </div>
  );
};

export default ApiKeyInput;
