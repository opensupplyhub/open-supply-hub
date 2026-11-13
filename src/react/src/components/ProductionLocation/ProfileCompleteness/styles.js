import COLOURS from '../../../util/COLOURS';
import claimDataContainerStyles from '../ClaimSection/ClaimDataContainer/styles';

/*
One flat blue for completeness at every level: never the green reserved for
claimed status, and never a red/amber/green scale, which would read as a
grade.
*/
const ACCENT = COLOURS.MATERIAL_BLUE;
const ACCENT_TINT = COLOURS.EXTRA_LIGHT_BLUE;
const TRACK = COLOURS.ACCENT_GREY;

const BAR_HEIGHTS = Object.freeze([7, 11, 15]);

export default theme => {
    const sectionStyles = claimDataContainerStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: sectionStyles.container,
        header: sectionStyles.header,
        headerOpen: sectionStyles.headerOpen,
        headerLeft: Object.freeze({
            ...sectionStyles.headerLeft,
            flexWrap: 'wrap',
        }),
        headerRight: sectionStyles.headerRight,
        title: sectionStyles.title,
        toggleLabel: sectionStyles.toggleLabel,
        chevron: sectionStyles.chevron,
        panel: Object.freeze({
            padding: '20px',
        }),
        sections: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: `${spacing * 2}px`,
        }),
        headerMeta: Object.freeze({
            fontSize: '0.875rem',
            color: theme.palette.text.secondary,
        }),
        adminChip: Object.freeze({
            fontSize: '0.75rem',
            fontWeight: 600,
            color: COLOURS.DARK_SLATE_GREY,
            backgroundColor: COLOURS.ACCENT_GREY,
            borderRadius: '4px',
            padding: '1px 7px',
            whiteSpace: 'nowrap',
        }),

        indicator: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: `${spacing}px`,
            marginTop: -spacing,
            marginBottom: spacing * 2,
            padding: 0,
            border: 'none',
            background: 'none',
            cursor: 'pointer',
            font: 'inherit',
            textAlign: 'left',
            '&:hover $indicatorLabel, &:focus $indicatorLabel': {
                color: theme.palette.text.primary,
                textDecoration: 'underline',
            },
        }),
        indicatorLabel: Object.freeze({
            fontSize: '0.875rem',
            fontWeight: 600,
            color: theme.palette.text.secondary,
        }),
        levelName: Object.freeze({
            fontSize: '0.75rem',
            fontWeight: 700,
            color: ACCENT,
            backgroundColor: ACCENT_TINT,
            borderRadius: '4px',
            padding: '1px 7px',
            whiteSpace: 'nowrap',
        }),
        bars: Object.freeze({
            display: 'inline-flex',
            alignItems: 'flex-end',
            gap: '2px',
            flex: 'none',
        }),
        bar: Object.freeze({
            display: 'block',
            width: '4px',
            borderRadius: '1px',
            backgroundColor: TRACK,
        }),
        barFilled: Object.freeze({
            backgroundColor: ACCENT,
        }),
        ...BAR_HEIGHTS.reduce(
            (acc, height, index) => ({
                ...acc,
                [`barHeight${index + 1}`]: Object.freeze({
                    height: `${height}px`,
                }),
            }),
            {},
        ),

        breakdown: Object.freeze({
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '10px 30px',
            margin: 0,
            padding: 0,
            listStyle: 'none',
        }),
        component: Object.freeze({
            display: 'grid',
            gridTemplateColumns: '1fr auto',
            gap: '2px 12px',
            alignItems: 'baseline',
            padding: '5px 0',
        }),
        componentName: Object.freeze({
            fontSize: '0.875rem',
            color: theme.palette.text.secondary,
        }),
        componentValue: Object.freeze({
            fontSize: '0.875rem',
            fontWeight: 600,
            fontVariantNumeric: 'tabular-nums',
        }),
        componentTrack: Object.freeze({
            gridColumn: '1 / -1',
            height: '6px',
            borderRadius: '3px',
            backgroundColor: TRACK,
            overflow: 'hidden',
        }),
        componentFill: Object.freeze({
            height: '100%',
            borderRadius: '3px',
            backgroundColor: ACCENT,
        }),
        totalLine: Object.freeze({
            display: 'flex',
            alignItems: 'baseline',
            flexWrap: 'wrap',
            gap: `${spacing}px ${spacing * 2}px`,
            marginTop: spacing * 2,
            paddingTop: spacing * 2,
            borderTop: `1px solid ${COLOURS.ACCENT_GREY}`,
        }),
        totalValue: Object.freeze({
            fontSize: '1.75rem',
            fontWeight: 700,
            fontVariantNumeric: 'tabular-nums',
        }),
        note: Object.freeze({
            fontSize: '0.875rem',
            color: theme.palette.text.secondary,
            margin: 0,
        }),

        classifier: Object.freeze({
            marginTop: spacing * 2,
            padding: `${spacing * 1.5}px ${spacing * 2}px`,
            backgroundColor: COLOURS.LIGHTEST_GREY,
            border: `1px solid ${COLOURS.ACCENT_GREY}`,
        }),
        classifierHeading: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: `${spacing}px`,
            margin: 0,
            fontSize: '1rem',
            fontWeight: 600,
        }),
        classifierTier: Object.freeze({
            fontSize: '0.875rem',
            fontWeight: 700,
            color: ACCENT,
            backgroundColor: ACCENT_TINT,
            borderRadius: '4px',
            padding: '1px 7px',
        }),
        classifierList: Object.freeze({
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: `${spacing}px ${spacing * 3}px`,
            margin: `${spacing}px 0`,
        }),
        classifierTerm: Object.freeze({
            fontSize: '0.75rem',
            color: theme.palette.text.secondary,
        }),
        classifierDefinition: Object.freeze({
            margin: 0,
            fontSize: '0.875rem',
            fontWeight: 600,
        }),

        steps: Object.freeze({
            margin: `${spacing}px 0 0`,
            padding: 0,
            listStyle: 'none',
        }),
        step: Object.freeze({
            padding: '11px 0',
            borderBottom: `1px solid ${COLOURS.ACCENT_GREY}`,
            '&:last-child': {
                borderBottom: 'none',
            },
        }),
        stepText: Object.freeze({
            fontSize: '1rem',
            fontWeight: 600,
        }),
        stepDetail: Object.freeze({
            fontSize: '0.875rem',
            color: theme.palette.text.secondary,
        }),
    });
};
