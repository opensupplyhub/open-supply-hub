import { getTypographyStyles } from '../../../util/typographyStyles';
import commonStyles from '../commonStyles';
import COLOURS from '../../../util/COLOURS';

export default theme => {
    const typography = getTypographyStyles(theme);
    return Object.freeze({
        container: Object.freeze({
            ...commonStyles(theme).container,
            padding: '20px',
        }),
        title: {
            marginBottom: theme.spacing.unit,
        },
        sectionTitleRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${theme.spacing.unit}px`,
            borderBottom: `1px solid ${theme.palette.divider}`,
            paddingBottom: theme.spacing.unit * 1.5,
            marginBottom: theme.spacing.unit * 2,
        }),
        sectionTitle: Object.freeze({
            ...typography.sectionTitle,
            marginTop: 0,
            marginBottom: 0,
            marginRight: 0,
        }),
        sectionTitleIcon: Object.freeze({
            color: theme.palette.text.secondary,
            flexShrink: 0,
        }),
        mapContainer: Object.freeze({
            width: 'auto',
            maxWidth: '100%',
            height: '320px',
            [theme.breakpoints.down('md')]: {
                height: '380px',
            },
        }),
        mapInner: Object.freeze({
            height: '100%',
            width: '100%',
        }),
        mapControlsRow: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'stretch',
            '& > * + *': {
                marginTop: theme.spacing.unit,
            },
        }),
        mapControlButton: Object.freeze({
            width: 34,
            height: 34,
            minWidth: 34,
            minHeight: 34,
            padding: 0,
            backgroundColor: theme.palette.background.paper,
            boxShadow: theme.shadows[2],
            color: theme.palette.text.secondary,
            '&:hover': {
                backgroundColor: theme.palette.grey[100],
            },
        }),
        googleMapsButton: Object.freeze({
            ...typography.bodyText,
            backgroundColor: theme.palette.background.paper,
            boxShadow: theme.shadows[2],
            color: theme.palette.text.secondary,
            textTransform: 'none',
            borderColor: theme.palette.grey[400],
            '&, & .MuiButton-label, & svg': {
                color: theme.palette.text.secondary,
            },
            '&:hover': {
                backgroundColor: theme.palette.grey[100],
                borderColor: theme.palette.grey[500],
                '&, & .MuiButton-label, & svg': {
                    color: theme.palette.text.secondary,
                },
            },
        }),
        googleMapsButtonIcon: Object.freeze({
            marginRight: theme.spacing.unit,
        }),
        mapDragHint: Object.freeze({
            display: 'inline-block',
            paddingTop: '0.25rem',
            paddingBottom: '0.35rem',
            paddingLeft: theme.spacing.unit,
            paddingRight: theme.spacing.unit,
            fontSize: '0.875rem',
            lineHeight: 1,
            color: COLOURS.WHITE,
            backgroundColor: '#00000080',
            cursor: 'grab',
        }),
    });
};
