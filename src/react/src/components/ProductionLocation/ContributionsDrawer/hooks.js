import { useEffect, useRef } from 'react';

/**
 * Optionally return focus to the trigger element when drawer closes.
 * @param {boolean} open - Whether the drawer is open
 * @param {React.RefObject} triggerRef - Ref of the element that opened the drawer
 */
export function useDrawerFocusReturn(open, triggerRef) {
    const previouslyOpen = useRef(false);

    useEffect(() => {
        if (previouslyOpen.current && !open && triggerRef?.current) {
            triggerRef.current.focus();
        }
        previouslyOpen.current = open;
    }, [open, triggerRef]);
}
