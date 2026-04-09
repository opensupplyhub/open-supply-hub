import { useState, useCallback } from 'react';

const useDrawerState = (initialFieldKey = null) => {
    const [openFieldKey, setOpenFieldKey] = useState(initialFieldKey);
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const openDrawer = useCallback(key => {
        setOpenFieldKey(key);
        setIsDrawerOpen(true);
    }, []);
    const closeDrawer = useCallback(() => setIsDrawerOpen(false), []);
    return [openFieldKey, isDrawerOpen, openDrawer, closeDrawer];
};

export default useDrawerState;
