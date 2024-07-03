import React, { useContext, useState, useEffect, createContext, ReactNode } from "react";

interface DataContextType {
  emotesNameToUrlMap: Record<string, string>;
}

export const DataContext = createContext<DataContextType>({
  emotesNameToUrlMap: {}
});

interface Emote {
  id: string;
  name: string;
}

interface ApiResponse7tv {
  emotes: Emote[]
}

export const DataProvider = ({ children }:{ children: ReactNode }) => {
  const [emotesNameToUrlMap, setEmotesNameToUrlMap] = useState({});

  useEffect(() => {
    (async() => {
      const response = await fetch('https://7tv.io/v3/emote-sets/64cf3c4bfb2d2df1bc66116c');
      if (!response.ok) {
        throw new Error ('use7tvEmotes: data fetch failed');
      }
      const data7tv:ApiResponse7tv = await response.json();
      const emotesNameToUrlMap:Record<string, string> = {};
      data7tv.emotes.forEach(emote => {
        const emoteSrc = `https://cdn.7tv.app/emote/${emote.id}/4x.webp`;
        emotesNameToUrlMap[emote.name] = emoteSrc;
        (new Image()).src = emoteSrc; // preload the images for performance
      });
      setEmotesNameToUrlMap(emotesNameToUrlMap);
    })();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <DataContext.Provider value={{
      emotesNameToUrlMap
    }}>
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error("Context must be used within a Provider");
  }
  return context;
};
