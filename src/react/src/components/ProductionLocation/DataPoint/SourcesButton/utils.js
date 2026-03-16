const getSourcesButtonLabel = sourcesCount => {
    const sourceWord = sourcesCount === 1 ? 'source' : 'sources';
    return `+${sourcesCount} data ${sourceWord}`;
};

export default getSourcesButtonLabel;
