import { useFormik } from 'formik';
import { useEffect, useState, useCallback } from 'react';
import freeEmissionsEstimateValidationSchema from './utils.js';

// Custom hook to sync form field with Redux store.
export const useFormFieldSync = (formValue, storeValue, updateAction) => {
    useEffect(() => {
        if (formValue !== storeValue) {
            updateAction(formValue);
        }
    }, [formValue, storeValue, updateAction]);
};

export const useInfiniteYearScroll = () => {
    const CHUNK_SIZE = 25;
    const MIN_YEAR = 1000;
    const currentYear = new Date().getFullYear();

    const [years, setYears] = useState([]);
    const [hasMore, setHasMore] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [lastLoadedYear, setLastLoadedYear] = useState(currentYear);

    // Generate initial years chunk.
    useEffect(() => {
        const initialChunk = [];
        const endYear = Math.max(currentYear - CHUNK_SIZE + 1, MIN_YEAR);

        for (let year = currentYear; year >= endYear; year -= 1) {
            initialChunk.push({ value: year, label: year.toString() });
        }

        setYears(initialChunk);
        setLastLoadedYear(endYear);
        setHasMore(endYear > MIN_YEAR);
    }, [currentYear]);

    const loadMoreYears = useCallback(() => {
        if (isLoading || !hasMore) return;

        setIsLoading(true);

        // Calculate next chunk range.
        const startYear = lastLoadedYear - 1;
        const endYear = Math.max(startYear - CHUNK_SIZE + 1, MIN_YEAR);

        // Generate next chunk.
        const nextChunk = [];
        for (let year = startYear; year >= endYear; year -= 1) {
            nextChunk.push({ value: year, label: year.toString() });
        }

        // Add to existing years.
        setYears(prevYears => [...prevYears, ...nextChunk]);
        setLastLoadedYear(endYear);
        setHasMore(endYear > MIN_YEAR);
        setIsLoading(false);
    }, [lastLoadedYear, hasMore, isLoading]);

    return {
        years,
        hasMore,
        isLoading,
        loadMoreYears,
    };
};

export const useFreeEmissionsEstimateForm = initialValues =>
    useFormik({
        initialValues: {
            openingDate: '',
            closingDate: '',
            estimatedAnnualThroughput: '',
            energyCoal: '',
            energyNaturalGas: '',
            energyDiesel: '',
            energyKerosene: '',
            energyBiomass: '',
            energyCharcoal: '',
            energyAnimalWaste: '',
            energyElectricity: '',
            energyOther: '',
            energyCoalEnabled: false,
            energyNaturalGasEnabled: false,
            energyDieselEnabled: false,
            energyKeroseneEnabled: false,
            energyBiomassEnabled: false,
            energyCharcoalEnabled: false,
            energyAnimalWasteEnabled: false,
            energyElectricityEnabled: false,
            energyOtherEnabled: false,
            ...initialValues,
        },
        validationSchema: freeEmissionsEstimateValidationSchema,
        validateOnMount: true,
        initialTouched: Object.keys(initialValues).reduce((acc, key) => {
            acc[key] = true; // Mark all fields as touched.
            return acc;
        }, {}),
    });
