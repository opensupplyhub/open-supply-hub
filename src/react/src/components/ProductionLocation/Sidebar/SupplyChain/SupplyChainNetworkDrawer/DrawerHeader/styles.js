import COLOURS from '../../../../../../util/COLOURS';

export default () =>
    Object.freeze({
        header: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            marginBottom: '12px',
        }),
        headerLeft: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '8px',
        }),
        titleIcon: Object.freeze({
            fontSize: '1.5rem',
            color: COLOURS.PURPLE,
        }),
        title: Object.freeze({
            fontWeight: 700,
            fontSize: '1.4rem',
            lineHeight: 1.3,
            color: COLOURS.NEAR_BLACK,
            marginLeft: '10px',
        }),
        closeButton: Object.freeze({
            margin: '-8px',
            color: COLOURS.DARK_GREY,
            '&:hover': Object.freeze({
                backgroundColor: COLOURS.HOVER_GREY,
                color: COLOURS.PURPLE,
            }),
        }),
    });
