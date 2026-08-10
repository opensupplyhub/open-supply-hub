import {
    getFacilityProcessingSearchIndex,
    getFacilityProcessingNodeId,
} from '../../../data/facilityProcessingSearchIndex';

export const TAXONOMY_KINDS = Object.freeze({
    FACILITY_PROCESSING: 'facility_processing',
    ISIC4: 'isic4',
});

export const makeSelectOption = value =>
    Object.freeze({
        value,
        label: value,
    });

export function isFacilityProcessingNodeSelected(
    node,
    facilityType = [],
    processingType = [],
) {
    if (node.kind === 'facility_type') {
        return facilityType.some(option => option.value === node.label);
    }

    return processingType.some(option => option.value === node.label);
}

export function toggleFacilityProcessingNode(
    node,
    facilityType = [],
    processingType = [],
) {
    if (node.kind === 'facility_type') {
        const isSelected = isFacilityProcessingNodeSelected(
            node,
            facilityType,
            processingType,
        );

        if (isSelected) {
            return removeFacilityProcessingNodeById(
                node.id,
                facilityType,
                processingType,
            );
        }

        return Object.freeze({
            facilityType: [...facilityType, makeSelectOption(node.label)],
            processingType,
        });
    }

    const isSelected = isFacilityProcessingNodeSelected(
        node,
        facilityType,
        processingType,
    );

    if (isSelected) {
        return Object.freeze({
            facilityType,
            processingType: processingType.filter(
                option => option.value !== node.label,
            ),
        });
    }

    return Object.freeze({
        facilityType,
        processingType: [...processingType, makeSelectOption(node.label)],
    });
}

export function removeFacilityProcessingNodeById(
    nodeId,
    facilityType = [],
    processingType = [],
) {
    if (nodeId.startsWith('facility_type:')) {
        const facilityLabel = nodeId.slice('facility_type:'.length);
        const group = getFacilityProcessingSearchIndex().groups.find(
            entry => entry.facilityNode.facilityType === facilityLabel,
        );
        const processingLabels = new Set(
            (group?.processingNodes ?? []).map(node => node.label),
        );

        return Object.freeze({
            facilityType: facilityType.filter(
                option => option.value !== facilityLabel,
            ),
            processingType: processingType.filter(
                option => !processingLabels.has(option.value),
            ),
        });
    }

    if (nodeId.startsWith('processing_type:')) {
        const processingLabel = nodeId.split(':').slice(2).join(':');

        return Object.freeze({
            facilityType,
            processingType: processingType.filter(
                option => option.value !== processingLabel,
            ),
        });
    }

    return Object.freeze({ facilityType, processingType });
}

export function getFacilityProcessingNodeKey(node) {
    return getFacilityProcessingNodeId(node);
}

export function splitLabelForHighlight(label, highlightQuery) {
    if (!highlightQuery) {
        return [{ text: label, highlighted: false }];
    }

    const lowerLabel = label.toLowerCase();
    const lowerQuery = highlightQuery.toLowerCase();
    const matchIndex = lowerLabel.indexOf(lowerQuery);

    if (matchIndex < 0) {
        return [{ text: label, highlighted: false }];
    }

    return [
        { text: label.slice(0, matchIndex), highlighted: false },
        {
            text: label.slice(matchIndex, matchIndex + highlightQuery.length),
            highlighted: true,
        },
        {
            text: label.slice(matchIndex + highlightQuery.length),
            highlighted: false,
        },
    ].filter(part => part.text.length > 0);
}
