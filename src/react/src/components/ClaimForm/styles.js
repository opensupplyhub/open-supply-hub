import COLOURS from '../../util/COLOURS';

const claimFormStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            width: '100%',
            minHeight: '100vh',
            backgroundColor: '#ffffff',
            paddingTop: theme.spacing.unit * 2,
            paddingBottom: theme.spacing.unit * 2,
            paddingLeft: theme.spacing.unit * 2,
            paddingRight: theme.spacing.unit * 2,
        }),
        innerContainer: Object.freeze({
            maxWidth: '896px',
            margin: '0 auto',
        }),
        paper: Object.freeze({
            padding: theme.spacing.unit * 3,
            marginTop: theme.spacing.unit * 2,
            marginBottom: theme.spacing.unit * 2,
            boxShadow:
                '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        }),
        title: Object.freeze({
            marginBottom: theme.spacing.unit,
            fontWeight: 700,
            color: COLOURS.NEAR_BLACK,
            fontSize: '1.5rem',
            textAlign: 'center',
        }),
        titleStyles: Object.freeze({
            fontSize: '36px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            gap: '5px',
            display: 'flex',
            alignItems: 'center',
        }),
        description: Object.freeze({
            marginBottom: theme.spacing.unit * 1.5,
            color: COLOURS.DARK_GREY,
            fontSize: '0.875rem',
            textAlign: 'center',
        }),
        progressContainer: Object.freeze({
            textAlign: 'center',
            maxWidth: '448px',
            margin: '0 auto',
            marginBottom: theme.spacing.unit * 2,
        }),
        progressBar: Object.freeze({
            marginBottom: theme.spacing.unit,
            height: 8,
            borderRadius: 4,
        }),
        progressText: Object.freeze({
            fontSize: '0.75rem',
            color: COLOURS.DARK_GREY,
            marginTop: theme.spacing.unit,
        }),
        stepContent: Object.freeze({
            marginTop: theme.spacing.unit * 3,
            marginBottom: theme.spacing.unit * 3,
        }),
        navigationButtons: Object.freeze({
            marginTop: theme.spacing.unit * 3,
        }),
        buttonBack: Object.freeze({
            textTransform: 'none',
            fontWeight: 600,
            paddingLeft: theme.spacing.unit * 3,
            paddingRight: theme.spacing.unit * 3,
        }),
        buttonNext: Object.freeze({
            textTransform: 'none',
            fontWeight: 600,
            paddingLeft: theme.spacing.unit * 3,
            paddingRight: theme.spacing.unit * 3,
            backgroundColor: '#FBBF24',
            color: '#000000',
            '&:hover': {
                backgroundColor: '#F59E0B',
            },
        }),
        buttonSuccess: Object.freeze({
            textTransform: 'none',
            fontWeight: 600,
            paddingLeft: theme.spacing.unit * 3,
            paddingRight: theme.spacing.unit * 3,
            backgroundColor: '#059669',
            color: '#ffffff',
            '&:hover': {
                backgroundColor: '#047857',
            },
        }),
        buttonSubmit: Object.freeze({
            textTransform: 'none',
            fontWeight: 600,
            paddingLeft: theme.spacing.unit * 3,
            paddingRight: theme.spacing.unit * 3,
            backgroundColor: '#059669',
            color: '#ffffff',
            '&:hover': {
                backgroundColor: '#047857',
            },
        }),
        sectionTitle: Object.freeze({
            fontSize: '1.25rem',
            fontWeight: 600,
            marginBottom: theme.spacing.unit * 2,
        }),
        sectionDescription: Object.freeze({
            fontSize: '0.875rem',
            color: COLOURS.DARK_GREY,
            marginBottom: theme.spacing.unit * 3,
        }),
        loadingContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '400px',
        }),
        errorContainer: Object.freeze({
            padding: theme.spacing.unit * 3,
            textAlign: 'center',
        }),
        errorText: Object.freeze({
            color: theme.palette.error.main,
            marginBottom: theme.spacing.unit * 2,
        }),
        errorButton: Object.freeze({
            marginTop: theme.spacing.unit * 2,
        }),
    });

const eligibilityStepStyles = theme =>
    Object.freeze({
        card: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            border: `1px solid ${COLOURS.GREY}`,
        }),
        content: Object.freeze({
            padding: theme.spacing.unit * 3,
        }),
        titleSection: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.unit,
            marginBottom: theme.spacing.unit * 3,
        }),
        titleIcon: Object.freeze({
            fontSize: '1.25rem',
        }),
        title: Object.freeze({
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
        }),
        accountInfoSection: Object.freeze({
            backgroundColor: '#f9fafb',
            border: '1px solid #e5e7eb',
            padding: theme.spacing.unit * 1.5,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        accountInfoBox: Object.freeze({
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            padding: theme.spacing.unit * 1.5,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        accountInfoRow: Object.freeze({
            fontSize: '14px',
            marginBottom: theme.spacing.unit,
            '&:last-child': {
                marginBottom: 0,
            },
        }),
        accountInfoLabel: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontWeight: theme.typography.fontWeightMedium,
        }),
        accountInfoValue: Object.freeze({
            color: '#111827',
            fontWeight: theme.typography.fontWeightMedium,
            marginLeft: theme.spacing.unit,
        }),
        sectionTitle: Object.freeze({
            fontSize: '16px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            color: '#111827',
            marginBottom: theme.spacing.unit * 2,
        }),
        selectWrapper: Object.freeze({
            marginBottom: 0,
        }),
        buttonContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: theme.spacing.unit * 3,
        }),
        backButton: Object.freeze({
            border: `1px solid ${COLOURS.GREY}`,
            backgroundColor: '#ffffff',
            padding: `${theme.spacing.unit}px ${theme.spacing.unit * 3}px`,
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightSemiBold,
            textTransform: 'uppercase',
            '&:hover': {
                backgroundColor: '#f9fafb',
            },
        }),
        continueButton: Object.freeze({
            backgroundColor: '#facc15',
            color: '#000000',
            padding: `${theme.spacing.unit}px ${theme.spacing.unit * 2}px`,
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightSemiBold,
            textTransform: 'none',
            '&:hover': {
                backgroundColor: '#eab308',
            },
            '&:disabled': {
                backgroundColor: '#facc15',
                opacity: 0.5,
            },
        }),
    });

export { claimFormStyles, eligibilityStepStyles };
