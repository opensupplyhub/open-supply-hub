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
    });
};
