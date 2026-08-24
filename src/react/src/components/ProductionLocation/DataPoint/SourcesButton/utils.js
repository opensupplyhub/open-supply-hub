/*
`sourcesCount` is the total number of contributions the drawer will show for
the field, including the promoted one (OSDEV-3228). The label therefore states
the total rather than a "+N more" delta, so it matches the drawer contents and
reads correctly when a field has a single contribution.
*/
const getSourcesButtonLabel = sourcesCount => {
    const sourceWord = sourcesCount === 1 ? 'source' : 'sources';
    return `${sourcesCount} data ${sourceWord}`;
};

export default getSourcesButtonLabel;
