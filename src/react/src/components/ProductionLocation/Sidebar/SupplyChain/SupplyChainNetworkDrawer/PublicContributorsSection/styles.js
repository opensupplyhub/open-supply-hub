import COLOURS from '../../../../../../util/COLOURS';

export default () =>
    Object.freeze({
        contributorList: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            marginBottom: '16px',
        }),
        contributorEntry: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREY,
            padding: '16px',
            '&:hover': Object.freeze({
                backgroundColor: COLOURS.HOVER_GREY,
            }),
        }),
        contributorName: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '1.25rem',
            fontWeight: 600,
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            marginBottom: '2px',
            overflowWrap: 'break-word',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        contributorNameIcon: Object.freeze({
            fontSize: '0.875rem',
            color: 'inherit',
            marginTop: '5px',
        }),
        contributorType: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            marginBottom: '6px',
        }),
        listEntry: Object.freeze({
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            padding: '8px 12px',
            marginBottom: '8px',
            backgroundColor: COLOURS.WHITE,
            width: '80%',
            justifySelf: 'flex-end',
        }),
        listEntryLabel: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            marginBottom: '2px',
        }),
        listIcon: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            flexShrink: 0,
            marginTop: '2px',
        }),
        listName: Object.freeze({
            fontSize: '1.15rem',
            color: COLOURS.NEAR_BLACK,
            fontWeight: 500,
        }),
    });
