import React from "react";
import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme } from "../contexts/ThemeContext";

export const ThemeSwitcher: React.FC = () => {
  const { theme, setTheme } = useTheme();

  const themes = [
    { value: "light" as const, icon: Sun, label: "Light" },
    { value: "dark" as const, icon: Moon, label: "Dark" },
    { value: "system" as const, icon: Monitor, label: "System" },
  ];

  return (
    <div className="flex items-center gap-1 bg-gray-900/50 dark:bg-gray-900/50 light:bg-gray-100/80 border border-gray-800 dark:border-gray-800 light:border-gray-300 rounded-lg p-1">
      {themes.map(({ value, icon: Icon, label }) => (
        <button
          key={value}
          onClick={() => setTheme(value)}
          className={`
            relative flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-mono font-bold uppercase tracking-wider transition-all
            ${theme === value 
              ? "bg-amber-500 text-black shadow-[0_0_12px_rgba(245,158,11,0.4)]" 
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50 dark:hover:bg-gray-800/50 light:hover:bg-gray-200/50"
            }
          `}
          title={`${label} mode`}
        >
          <Icon className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">{label}</span>
        </button>
      ))}
    </div>
  );
};
