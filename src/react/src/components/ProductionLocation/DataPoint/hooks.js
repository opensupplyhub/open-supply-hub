import { useState, useCallback } from 'react';

/**
 * Hook to control drawer open state and return focus to trigger on close.
 * @returns {{ drawerOpen: boolean, openDrawer: function, closeDrawer: function }}
 */
export function useDataPointDrawer() {
    const [drawerOpen, setDrawerOpen] = useState(false);

    const openDrawer = useCallback(() => {
        setDrawerOpen(true);
    }, []);

    const closeDrawer = useCallback(() => {
        setDrawerOpen(false);
    }, []);

    return { drawerOpen, openDrawer, closeDrawer };
}
