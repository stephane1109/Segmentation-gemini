import React, { useRef } from 'react';
import { MusicIcon } from './icons';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, isLoading }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    if (isLoading) return;
    const file = event.dataTransfer.files?.[0];
    if (file && file.type === 'audio/mpeg') {
      onFileSelect(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleClick = () => {
    if (isLoading) return;
    fileInputRef.current?.click();
  };

  const disabledClasses = "opacity-50 cursor-not-allowed";
  const enabledClasses = "hover:border-blue-500 hover:bg-gray-800/50 cursor-pointer";

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`w-full h-64 border-2 border-dashed border-gray-600 rounded-xl flex flex-col items-center justify-center text-gray-400 transition-all duration-300 ${isLoading ? disabledClasses : enabledClasses}`}
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".mp3"
          className="hidden"
          disabled={isLoading}
        />
        <MusicIcon className="w-16 h-16 mb-4 text-gray-500" />
        <p className="text-lg font-semibold">
            {isLoading ? "Veuillez fournir une clé API" : "Déposez votre fichier MP3 ici"}
        </p>
        <p>ou</p>
        <p className={`font-bold ${isLoading ? "" : "text-blue-400"}`}>
            {isLoading ? "" : "Cliquez pour parcourir"}
        </p>
      </div>
    </div>
  );
};

export default FileUpload;
