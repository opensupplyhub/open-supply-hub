import { useState, useCallback } from 'react';

const useDrawerState = (initialFieldKey = null) => {
    const [openFieldKey, setOpenFieldKey] = useState(initialFieldKey);
    const openDrawer = useCallback(key => setOpenFieldKey(key), []);
    const closeDrawer = useCallback(() => setOpenFieldKey(null), []);
    return [openFieldKey, openDrawer, closeDrawer];
};

export default useDrawerState;
