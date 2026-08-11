import {
    getIsic4FilterValue,
    getIsic4NodeId,
} from '../../../data/isic4SearchIndex';

export const makeIsic4SelectOption = node =>
    Object.freeze({
        value: getIsic4FilterValue(node),
        label: node.displayLabel,
    });

export function isIsic4NodeSelected(node, isic4 = []) {
    return isic4.some(option => option.value === getIsic4FilterValue(node));
}

export function toggleIsic4Node(node, isic4 = []) {
    const filterValue = getIsic4FilterValue(node);
    const isSelected = isic4.some(option => option.value === filterValue);

    if (isSelected) {
        return isic4.filter(option => option.value !== filterValue);
    }

    return [...isic4, makeIsic4SelectOption(node)];
}

export function getIsic4NodeKey(node) {
    return getIsic4NodeId(node);
}
