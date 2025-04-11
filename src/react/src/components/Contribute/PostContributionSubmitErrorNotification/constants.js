const ERROR_CONTENT_COPIES = {
    validation: {
        title: 'Data submission failed.',
        fieldErrorSubtitle:
            'Validation for the following fields failed during processing. Please double-check and try again:',
        nonFieldErrorSubtitle:
            'We encountered non-field specific errors, which may be related to multiple fields or the entire form. Please see them below:',
        supportInstructions:
            "If you can't resolve the issue by updating the field values, please contact the OS Hub team and provide the following data:",
    },
    highLevel: {
        title: 'Data submission failed.',
        subtitle:
            'Your request could not be processed due to an issue with the information provided. Please review your entries and try again. Please see the details below:',
        supportInstructions:
            "If you can't resolve the issue by updating the field values, please contact the OS Hub team and provide the following data:",
    },
    server: {
        title: 'Oops! Something went wrong.',
        body:
            'Something went wrong on our end while processing your request. Please try again, and we apologize for the inconvenience.',
        supportInstructions:
            'If the issue continues, feel free to contact our support team with the details below.',
    },
    uknown: {
        title: 'Oops! Something went wrong.',
        body:
            'An unknown error has occurred. Please check your internet connection and try again.',
        supportInstructions:
            'If the issue continues, feel free to contact our support team.',
    },
};

export default ERROR_CONTENT_COPIES;
