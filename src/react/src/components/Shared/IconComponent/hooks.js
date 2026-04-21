import { useState, useRef, useCallback, useEffect } from 'react';

import LEAVE_TRIGGER_DELAY_MS from './constants';

const useInteractiveTooltip = () => {
    const [open, setOpen] = useState(false);
    const closeTimerRef = useRef(null);

    const clearCloseTimer = useCallback(() => {
        if (closeTimerRef.current) {
            clearTimeout(closeTimerRef.current);
            closeTimerRef.current = null;
        }
    }, []);

    const handleTriggerEnter = useCallback(() => {
        clearCloseTimer();
        setOpen(true);
    }, [clearCloseTimer]);

    const handleTriggerLeave = useCallback(() => {
        clearCloseTimer();
        closeTimerRef.current = setTimeout(
            () => setOpen(false),
            LEAVE_TRIGGER_DELAY_MS,
        );
    }, [clearCloseTimer]);

    const handlePopperEnter = useCallback(() => {
        clearCloseTimer();
        setOpen(true);
    }, [clearCloseTimer]);

    const handlePopperLeave = useCallback(() => setOpen(false), []);

    useEffect(() => () => clearCloseTimer(), [clearCloseTimer]);

    return {
        open,
        setOpen,
        clearCloseTimer,
        handleTriggerEnter,
        handleTriggerLeave,
        handlePopperEnter,
        handlePopperLeave,
    };
};

export default useInteractiveTooltip;
