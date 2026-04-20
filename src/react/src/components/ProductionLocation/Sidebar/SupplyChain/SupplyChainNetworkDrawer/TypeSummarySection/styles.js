import COLOURS from '../../../../../../util/COLOURS';

export default () =>
    Object.freeze({
        typeSummary: Object.freeze({
            flexWrap: 'wrap',
            gap: '8px',
            marginBottom: '16px',
        }),
        typeChip: Object.freeze({
            display: 'inline-block',
            fontSize: '0.9rem',
            color: COLOURS.NEAR_BLACK,
            backgroundColor: COLOURS.LIGHT_GREY,
            padding: '2px 10px',
        }),
    });
