import { getTypographyStyles } from '../../../util/typographyStyles';
import commonStyles from '../commonStyles';

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
        sectionTitle: Object.freeze({
            ...typography.sectionTitle,
            marginTop: 0,
            marginBottom: 0,
            marginRight: 0,
        }),
        mapContainer: Object.freeze({
            width: '100%',
            height: '200px',
            [theme.breakpoints.up('sm')]: {
                maxWidth: '100%',
                height: '320px',
            },
            [theme.breakpoints.up('md')]: {
                maxWidth: '1072px',
                height: '457px',
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
    });
};
