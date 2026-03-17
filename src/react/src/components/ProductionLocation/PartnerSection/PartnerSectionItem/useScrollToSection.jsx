import { useRef, useEffect } from 'react';
import { clearScrollTargetSection } from '../../../../actions/sectionNavigation';
import { HEADER_HEIGHT } from '../../../../util/constants';

export const transitionDurationMs = 100;

export function useScrollToSection(scrollTargetId, groupUuid, dispatch) {
    const containerRef = useRef(null);

    useEffect(() => {
        if (scrollTargetId === groupUuid) {
            dispatch(clearScrollTargetSection());
            // Wait for the collapse to finish transitioning before scrolling.
            // Alternative would be complex logic to track the collapse state.
            setTimeout(() => {
                if (containerRef.current) {
                    const top =
                        containerRef.current.getBoundingClientRect().top +
                        window.scrollY -
                        HEADER_HEIGHT;
                    window.scrollTo({ top, behavior: 'smooth' });
                }
            }, transitionDurationMs);
        }
    }, [scrollTargetId, groupUuid, dispatch]);

    return containerRef;
}
