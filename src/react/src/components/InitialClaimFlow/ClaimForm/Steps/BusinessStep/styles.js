import COLOURS from '../../../../../util/COLOURS';

const formLabel = Object.freeze({
    margin: '24px 0 8px 0',
    fontSize: '21px',
    fontWeight: 600,
});

const businessStepStyles = theme =>
    Object.freeze({
        formLabel: Object.freeze({
            ...formLabel,
        }),
        formLabelRoot: Object.freeze({
            ...formLabel,
            marginTop: 0,
        }),
        formFieldContainer: Object.freeze({
            position: 'relative',
            maxWidth: '528px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
        }),
        documentUploadContainer: Object.freeze({
            maxWidth: '1071px',
            marginTop: theme.spacing.unit * 2.5,
        }),
        disabledField: Object.freeze({
            cursor: 'default',
            boxSizing: 'border-box',
            padding: theme.spacing.unit * 2,
            fontWeight: 600,
            fontSize: '18px',
            borderRadius: '0',
        }),
        sectionDescription: Object.freeze({
            fontSize: '18px',
            marginBottom: '10px',
        }),
        linkField: Object.freeze({
            display: 'block',
            width: '100%',
            boxSizing: 'border-box',
            padding: theme.spacing.unit * 2,
            border: '1px solid rgba(0, 0, 0, 0.23)',
            borderRadius: '0',
            color: '#1976d2',
            textDecoration: 'none',
            fontWeight: 600,
            fontSize: '19px',
            '&:hover': {
                textDecoration: 'underline',
            },
        }),
        notchedOutlineStyles: Object.freeze({
            borderRadius: '0',
        }),
        errorWrapStyles: Object.freeze({
            margin: '8px 12px 0 0',
        }),
        helperText: Object.freeze({
            marginTop: theme.spacing.unit,
            marginLeft: 0,
        }),
        errorInput: Object.freeze({
            color: COLOURS.RED,
        }),
        importantNoteWrapper: Object.freeze({
            marginTop: theme.spacing.unit * 2.5,
        }),
    });

export default businessStepStyles;
