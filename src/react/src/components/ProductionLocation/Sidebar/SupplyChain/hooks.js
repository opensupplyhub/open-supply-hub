import { useState, useRef, useEffect, useMemo } from 'react';

import { splitContributorsIntoPublicAndNonPublic } from '../../../../util/util';
import { buildTypeCounts, aggregateByType, getTotalCount } from './utils';

export const useDerivedContributors = (contributors = []) =>
    useMemo(() => {
        const visibleContributors = contributors.filter(
            c => !!c.contributor_name || !!c.contributor_type,
        );
        const {
            publicContributors,
            nonPublicContributors,
        } = splitContributorsIntoPublicAndNonPublic(visibleContributors);
        const sortedPublicContributors = [...publicContributors].sort((a, b) =>
            (a.contributor_type || '').localeCompare(b.contributor_type || ''),
        );
        const aggregatedNonPublic = aggregateByType(nonPublicContributors);
        const merged = [...sortedPublicContributors, ...aggregatedNonPublic];
        return {
            visibleContributors,
            sortedPublicContributors,
            aggregatedNonPublic,
            typeCounts: buildTypeCounts(merged),
            totalCount: getTotalCount(merged),
        };
    }, [contributors]);

export const useDrawerOpen = () => {
    const [isOpen, setIsOpen] = useState(false);
    const triggerRef = useRef(null);
    const hasBeenOpenRef = useRef(false);

    useEffect(() => {
        if (isOpen) {
            hasBeenOpenRef.current = true;
        } else if (
            hasBeenOpenRef.current &&
            triggerRef.current &&
            typeof triggerRef.current.focus === 'function'
        ) {
            triggerRef.current.focus();
        }
    }, [isOpen]);

    return {
        isOpen,
        onOpen: () => setIsOpen(true),
        onClose: () => setIsOpen(false),
        triggerRef,
    };
};
