import { ISIC_REV4_TAXONOMY } from './isicRev4Taxonomy';

let isic4SearchIndex = null;

const matchesQuery = (text, lowerQuery) =>
    text.toLowerCase().includes(lowerQuery);

export const getIsic4NodeId = node => node.id;

export const getIsic4FilterValue = node => `${node.kind}:${node.code}`;

function buildIsic4SearchIndex(taxonomy) {
    const flatNodes = [];

    taxonomy.sections.forEach(section => {
        const sectionNode = Object.freeze({
            id: `section:${section.code}`,
            kind: 'section',
            code: section.code,
            label: section.label,
            displayLabel: section.displayLabel,
            depth: 0,
            parentId: null,
            countKey: `section:${section.code}`,
        });
        flatNodes.push(sectionNode);

        section.divisions.forEach(division => {
            const divisionNode = Object.freeze({
                id: `division:${division.code}`,
                kind: 'division',
                code: division.code,
                label: division.label,
                displayLabel: division.displayLabel,
                depth: 1,
                parentId: sectionNode.id,
                countKey: `division:${division.code}`,
            });
            flatNodes.push(divisionNode);

            division.groups.forEach(group => {
                const groupNode = Object.freeze({
                    id: `group:${group.code}`,
                    kind: 'group',
                    code: group.code,
                    label: group.label,
                    displayLabel: group.displayLabel,
                    depth: 2,
                    parentId: divisionNode.id,
                    countKey: `group:${group.code}`,
                });
                flatNodes.push(groupNode);

                group.classes.forEach(classNode => {
                    flatNodes.push(
                        Object.freeze({
                            id: `class:${classNode.code}`,
                            kind: 'class',
                            code: classNode.code,
                            label: classNode.label,
                            displayLabel: classNode.displayLabel,
                            depth: 3,
                            parentId: groupNode.id,
                            countKey: `class:${classNode.code}`,
                        }),
                    );
                });
            });
        });
    });

    return Object.freeze({ flatNodes });
}

export function getIsic4SearchIndex() {
    if (!isic4SearchIndex) {
        isic4SearchIndex = buildIsic4SearchIndex(ISIC_REV4_TAXONOMY);
    }
    return isic4SearchIndex;
}

function addDescendants(nodeId, allNodes, visibleIds) {
    visibleIds.add(nodeId);
    allNodes.forEach(node => {
        if (node.parentId === nodeId) {
            addDescendants(node.id, allNodes, visibleIds);
        }
    });
}

export function getIsic4VisibleRows(flatNodes, query = '') {
    const trimmedQuery = query.trim();
    const lowerQuery = trimmedQuery.toLowerCase();

    if (!lowerQuery) {
        const rows = flatNodes
            .filter(node => node.depth === 0)
            .map(node => ({
                node,
                depth: node.depth,
                isParent: true,
                highlightQuery: '',
            }));

        return Object.freeze({
            rows,
            hint: 'Type to search all ISIC levels, or select a section to browse',
        });
    }

    const nodeById = new Map(flatNodes.map(node => [node.id, node]));
    const visibleIds = new Set();

    const nodeMatches = node =>
        matchesQuery(node.label, lowerQuery) ||
        matchesQuery(node.code, lowerQuery) ||
        matchesQuery(node.displayLabel, lowerQuery);

    flatNodes.forEach(node => {
        if (!nodeMatches(node)) {
            return;
        }

        addDescendants(node.id, flatNodes, visibleIds);

        let { parentId } = node;
        while (parentId) {
            visibleIds.add(parentId);
            parentId = nodeById.get(parentId)?.parentId ?? null;
        }
    });

    const rows = flatNodes
        .filter(node => visibleIds.has(node.id))
        .map(node => ({
            node,
            depth: node.depth,
            isParent: node.kind !== 'class',
            highlightQuery: nodeMatches(node) ? trimmedQuery : '',
        }));

    const matchCount = rows.filter(row => row.highlightQuery).length;

    let hint = 'No matching ISIC categories';
    if (matchCount) {
        const categoryLabel = matchCount === 1 ? 'category' : 'categories';
        hint = `${matchCount} matching ISIC ${categoryLabel}`;
    }

    return Object.freeze({
        rows,
        hint,
    });
}
