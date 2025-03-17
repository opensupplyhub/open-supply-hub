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
            'Your request could not be processed. It seems there was an issue with the information you provided. Please check your input and try again:',
        supportInstructions:
            "If you can't resolve the issue by updating the field values, please contact the OS Hub team and provide the following data:",
    },
    server: {
        title: 'Oops! Something went wrong.',
        body:
            'Something went wrong on our end while processing your request. Our team has been notified and will work on resolving the issue. Please try again later, and we apologize for the inconvenience.',
        supportInstructions:
            'If the issue continues, feel free to contact our support team with the details below.',
    },
    uknown: {
        title: 'Oops! Something went wrong.',
        body:
            'Something went wrong, but we couldn’t identify the exact cause. This might be related to your network connection or an unexpected problem on our end. Please check your internet connection and try again. If the issue persists, feel free to contact support for assistance.',
        supportInstructions:
            'If the issue continues, feel free to contact our support team with the details below.',
    },
};

export default ERROR_CONTENT_COPIES;
