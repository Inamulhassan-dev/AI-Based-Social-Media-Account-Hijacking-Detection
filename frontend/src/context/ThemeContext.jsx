import { createContext, useContext } from "react";

const ThemeContext = createContext({ theme: "dark" });

export const ThemeProvider = ({ children }) => children;
export const useTheme = () => useContext(ThemeContext);
