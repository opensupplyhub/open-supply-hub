export const makeSelectOption = value =>
    Object.freeze({
        value,
        label: value,
    });

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
