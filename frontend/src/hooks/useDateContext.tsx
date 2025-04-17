import React, { createContext, useContext, useState, ReactNode } from 'react';
import { getCurrentDate, getDateBefore } from '../utils/dateUtils';

interface DateContextType {
  currentDate: string;
  setCurrentDate: (date: string) => void;
  dateRange: [string, string];
  setDateRange: (range: [string, string]) => void;
  timeRangeDays: number;
  setTimeRangeDays: (days: number) => void;
}

const DateContext = createContext<DateContextType | undefined>(undefined);

export const DateProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const today = getCurrentDate();
  const thirtyDaysAgo = getDateBefore(30);
  
  const [currentDate, setCurrentDate] = useState<string>(today);
  const [dateRange, setDateRange] = useState<[string, string]>([thirtyDaysAgo, today]);
  const [timeRangeDays, setTimeRangeDays] = useState<number>(30);

  return (
    <DateContext.Provider
      value={{
        currentDate,
        setCurrentDate,
        dateRange,
        setDateRange,
        timeRangeDays,
        setTimeRangeDays,
      }}
    >
      {children}
    </DateContext.Provider>
  );
};

export const useDateContext = (): DateContextType => {
  const context = useContext(DateContext);
  if (context === undefined) {
    throw new Error('useDateContext must be used within a DateProvider');
  }
  return context;
};

export default useDateContext; 