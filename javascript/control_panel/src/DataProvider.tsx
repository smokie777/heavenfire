import { useContext, useState, useEffect, createContext, ReactNode } from "react";

interface DataContextType {
  data: {
    emotesNameToUrlMap: Record<string, string>;
  };
}

const DataContext = createContext<DataContextType>({ data: { emotesNameToUrlMap: {} }});

interface Emote {
  id: string;
  name: string;
}

interface ApiResponse7tv {
  emotes: Emote[]
}

export const DataProvider = ({ children }:{ children: ReactNode }) => {
  const [data, setData] = useState({ emotesNameToUrlMap: {} });

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
      setData({ ...data, emotesNameToUrlMap });
    })();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <DataContext.Provider value={{ data }}>
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
