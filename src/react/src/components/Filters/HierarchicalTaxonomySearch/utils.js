export const makeSelectOption = value =>
    Object.freeze({
        value,
        label: value,
    });

export function getIsic4ParentNodeId(node) {
    return node.parentId ?? null;
}

export function getAncestorNodeIds(node, getParentNodeId, nodeById) {
    const ancestorIds = [];
    let parentId = getParentNodeId(node);

    while (parentId) {
        ancestorIds.push(parentId);
        const parentNode = nodeById.get(parentId);
        parentId = parentNode ? getParentNodeId(parentNode) : null;
    }

    return ancestorIds;
}

export function getExpandedNodeIdsForRows(
    rows,
    getNodeKey,
    getParentNodeId,
    nodeById,
) {
    const expandedIds = new Set();

    rows.forEach(row => {
        if (row.isParent) {
            expandedIds.add(getNodeKey(row.node));
        }

        getAncestorNodeIds(row.node, getParentNodeId, nodeById).forEach(id =>
            expandedIds.add(id),
        );
    });

    return expandedIds;
}

export function filterRowsByExpandedState(
    rows,
    expandedNodeIds,
    getParentNodeId,
    nodeById,
    showAllRows,
) {
    if (showAllRows) {
        return rows;
    }

    return rows.filter(row => {
        if (row.depth === 0) {
            return true;
        }

        return getAncestorNodeIds(
            row.node,
            getParentNodeId,
            nodeById,
        ).every(id => expandedNodeIds.has(id));
    });
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
