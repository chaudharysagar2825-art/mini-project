import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { casesApi } from '../api/cases';
import { Case } from '../types';

interface CaseContextType {
  cases: Case[];
  activeCase: Case | null;
  isLoading: boolean;
  error: string | null;
  setActiveCase: (caseItem: Case | null) => void;
  refreshCases: () => Promise<void>;
  createAutoCase: () => Promise<Case>;
}

const CaseContext = createContext<CaseContextType | undefined>(undefined);

export const CaseProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [cases, setCases] = useState<Case[]>([]);
  const [activeCase, setActiveCase] = useState<Case | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const isStaff = user && ['admin', 'caseworker', 'counsellor'].includes(user.role.toLowerCase());

  const refreshCases = useCallback(async () => {
    if (!isAuthenticated) {
      setCases([]);
      setActiveCase(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      let loadedCases: Case[] = [];
      if (isStaff) {
        loadedCases = await casesApi.listAllCases();
      } else {
        loadedCases = await casesApi.getMyCases();
      }
      setCases(loadedCases);

      // Preserve or set active case
      if (loadedCases.length > 0) {
        setActiveCase((prev) => {
          if (prev && loadedCases.some((c) => c.id === prev.id)) {
            return loadedCases.find((c) => c.id === prev.id) || loadedCases[0];
          }
          return loadedCases[0];
        });
      } else {
        setActiveCase(null);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load cases';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, isStaff]);

  useEffect(() => {
    refreshCases();
  }, [refreshCases]);

  const createAutoCase = async (): Promise<Case> => {
    setIsLoading(true);
    try {
      const newCase = await casesApi.generateCase();
      await refreshCases();
      setActiveCase(newCase);
      return newCase;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <CaseContext.Provider
      value={{
        cases,
        activeCase,
        isLoading,
        error,
        setActiveCase,
        refreshCases,
        createAutoCase,
      }}
    >
      {children}
    </CaseContext.Provider>
  );
};

export const useCase = () => {
  const context = useContext(CaseContext);
  if (!context) {
    throw new Error('useCase must be used within a CaseProvider');
  }
  return context;
};
