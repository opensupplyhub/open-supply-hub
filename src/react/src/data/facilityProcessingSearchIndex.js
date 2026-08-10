import { FACILITY_PROCESSING_TAXONOMY } from './facilityProcessingTaxonomy';

let facilityProcessingSearchIndex = null;

const matchesQuery = (text, lowerQuery) =>
    text.toLowerCase().includes(lowerQuery);

export const getFacilityProcessingNodeId = node => node.id;

function buildFacilityProcessingSearchIndex(taxonomy) {
    const groups = taxonomy.map(entry => {
        const facilityNode = Object.freeze({
            id: `facility_type:${entry.facilityType}`,
            kind: 'facility_type',
            label: entry.facilityType,
            displayLabel: entry.facilityType,
            facilityType: entry.facilityType,
            depth: 0,
            countKey: entry.facilityType,
        });

        const processingNodes = entry.processingTypes.map(processingType =>
            Object.freeze({
                id: `processing_type:${entry.facilityType}:${processingType.label}`,
                kind: 'processing_type',
                label: processingType.label,
                displayLabel: processingType.label,
                facilityType: entry.facilityType,
                depth: 1,
                countKey: processingType.label,
            }),
        );

        return Object.freeze({
            facilityNode,
            processingNodes,
        });
    });

    return Object.freeze({ groups });
}

export function getFacilityProcessingSearchIndex() {
    if (!facilityProcessingSearchIndex) {
        facilityProcessingSearchIndex = buildFacilityProcessingSearchIndex(
            FACILITY_PROCESSING_TAXONOMY,
        );
    }
    return facilityProcessingSearchIndex;
}

export function getFacilityProcessingVisibleRows(groups, query = '') {
    const trimmedQuery = query.trim();
    const lowerQuery = trimmedQuery.toLowerCase();
    const rows = [];
    let groupCount = 0;
    let hitCount = 0;

    groups.forEach(({ facilityNode, processingNodes }) => {
        const facilityMatches =
            !lowerQuery || matchesQuery(facilityNode.label, lowerQuery);
        const matchingProcessingNodes = lowerQuery
            ? processingNodes.filter(node =>
                  matchesQuery(node.label, lowerQuery),
              )
            : processingNodes;

        if (!facilityMatches && matchingProcessingNodes.length === 0) {
            return;
        }

        groupCount += 1;
        hitCount +=
            (facilityMatches ? 1 : 0) + matchingProcessingNodes.length;

        const processingNodesToShow = facilityMatches
            ? processingNodes
            : matchingProcessingNodes;

        rows.push({
            node: facilityNode,
            depth: 0,
            isParent: true,
            highlightQuery: facilityMatches ? trimmedQuery : '',
        });

        processingNodesToShow.forEach(processingNode => {
            const processingMatches =
                !lowerQuery ||
                matchesQuery(processingNode.label, lowerQuery);

            rows.push({
                node: processingNode,
                depth: 1,
                isParent: false,
                highlightQuery: processingMatches ? trimmedQuery : '',
            });
        });
    });

    const hint = trimmedQuery
        ? `${hitCount} matches across ${groupCount} facility ${
              groupCount === 1 ? 'type' : 'types'
          }`
        : 'Browse all facility types, or type to search both levels at once';

    return Object.freeze({ rows, hint });
}
